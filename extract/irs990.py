"""IRS Form 990 e-file XML parser.

The IRS publishes 990 returns as XML (one file per return) in annual bulk
downloads. Schemas vary by year, and elements live in the
``http://www.irs.gov/efile`` namespace. To stay robust across schema versions
this parser matches on element *local-name* rather than fixed namespaced paths.

Extracted into SQLite: organization header (EIN, name, revenue, expenses,
mission), grants paid (Schedule I), officers/directors/key employees, and
lobbying expenditures (Schedule C).

See irs990_schema_notes.md for known schema quirks and open questions
encountered while mapping fields across tax years.

Usage:
    from extract.irs990 import parse_990_file, ingest_990_directory
    ingest_990_directory("data/irs990_xml/")        # all *.xml in a folder
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable

from lxml import etree

from .db import connect, init_db, insert_many, upsert

logger = logging.getLogger(__name__)


def _child(node: etree._Element | None, tag: str) -> etree._Element | None:
    """First child element matching `tag` by local-name (namespace-agnostic)."""
    if node is None:
        return None
    found = node.xpath(f"./*[local-name()='{tag}']")
    return found[0] if found else None


def _text(node: etree._Element | None, *tags: str) -> str | None:
    """Follow a chain of local-name children and return stripped text."""
    cur = node
    for tag in tags:
        cur = _child(cur, tag)
        if cur is None:
            return None
    if cur is None or cur.text is None:
        return None
    return cur.text.strip()


def _float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def _bool_as_float(value: str | None) -> float | None:
    if value is None:
        return None
    if value.lower() in ('1', 'x', 'true'):
        return 1
    return 0


def _findall(node: etree._Element, tag: str) -> list[etree._Element]:
    return node.xpath(f"./*[local-name()='{tag}']")


def parse_990_file(path: str | Path) -> dict[str, Any]:
    """Parse one 990 XML return into a structured dict.

    Returns a dict with keys: org, grants, people. Designed to tolerate
    missing sections (not every return files Schedule I).
    """
    tree = etree.parse(str(path))
    root = tree.getroot()

    return_header = _child(root, "ReturnHeader")
    return_data = _child(root, "ReturnData")

    ein = _text(return_header, "Filer", "EIN") if return_header is not None else None
    tax_year = _text(return_header, "TaxYr") or _text(return_header, "TaxYear")

    name = None
    if return_header is not None:
        filer = _child(return_header, "Filer")
        if filer is not None:
            # BusinessName/BusinessNameLine1Txt (newer) or .../BusinessNameLine1 (older)
            name = (
                _text(filer, "BusinessName", "BusinessNameLine1Txt")
                or _text(filer, "BusinessName", "BusinessNameLine1")
            )

    org: dict[str, Any] = {
        "ein": ein,
        "name": name,
        "tax_year": int(tax_year) if tax_year and tax_year.isdigit() else None,
        "total_revenue": None,
        "total_expenses": None,
        "political_activity_flag": None,
        "mission": None,
        "raw_json": None,
    }
    grants: list[dict[str, Any]] = []
    people: list[dict[str, Any]] = []
    contractors: list[dict[str, Any]] = []

    if return_data is not None:
        form = _child(return_data, "IRS990") or _child(return_data, "IRS990EZ")
        if form is not None:
            org["total_revenue"] = _float(
                _text(form, "CYTotalRevenueAmt") or _text(form, "TotalRevenueCurrentYear")
            )
            org["total_expenses"] = _float(
                _text(form, "CYTotalExpensesAmt") or _text(form, "TotalExpensesCurrentYear")
            )
            org["mission"] = (
                _text(form, "MissionDesc")
                or _text(form, "ActivityOrMissionDesc")
                or _text(form, "MissionStatement")
            )
            people.extend(_parse_officers(form, org["ein"], org["tax_year"]))
            contractors.extend(_parse_contractors(form, org["ein"], org["tax_year"]))

        grants.extend(_parse_grants(return_data, org["ein"], org["tax_year"]))
        lobbying = _parse_schedule_c(return_data, org["ein"], org["tax_year"])
        try:
            related_orgs, related_org_transactions = _parse_schedule_r(return_data, org["ein"],
                                                                       org["tax_year"])
        except TypeError:
            related_orgs = related_org_transactions = None

        # Political activity signal: an explicit Part IV flag on the core
        # form, OR the presence of reported lobbying expenditures on
        # Schedule C (whichever Part applies to the filer's exemption type).
        pol = _text(form, "PoliticalCampaignActyInd") or _text(form, "PoliticalActivitiesInd")
        pol_flag = bool(pol and pol.lower() in {"1", "true", "x"})
        lobbying_spend = 0.0
        if lobbying:
            lobbying, _527_orgs = lobbying
            lobbying_spend = sum(
                lobbying.get(key) or 0.0
                for key in ("total_lobbying_expend_amt", "total_lobbying_expenditures_amt")
            )
        else:
            _527_orgs = None
        org["political_activity_flag"] = 1 if (pol_flag or lobbying_spend > 0) else 0
    else:
        lobbying = None
        _527_orgs = None
        related_orgs = None
        related_org_transactions = None

    filer_data = {
        "org": org,
        "grants": grants,
        "people": people,
        "lobbying": lobbying,
        "section_527_orgs": _527_orgs,
        "contractors": contractors,
        "related_orgs": related_orgs,
        "related_org_transactions": related_org_transactions
    }

    return filer_data


def _parse_officers(form: etree._Element, ein: str | None,
                    tax_year: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Officers/Directors/Trustees/Key Employees group element name varies.
    grp_tags = (
        "Form990PartVIISectionAGrp",
        "OfficerDirectorTrusteeKeyEmpl",
        "OfficerDirectorTrusteeEmplGrp"
    )
    for grp_tag in grp_tags:
        for grp in _findall(form, grp_tag):
            person = (
                _text(grp, "PersonNm")
                or _text(grp, "PersonName")
                or _text(grp, "NamePerson")
            )
            title = _text(grp, "TitleTxt") or _text(grp, "Title")
            # Position
            is_indiv_trustee_or_director = _bool_as_float(
                _text(grp, "IndividualTrusteeOrDirectorInd")
            )
            is_institutional_trustee = _bool_as_float(
                _text(grp, "InstitutionalTrusteeInd")
            )
            is_officer = _bool_as_float(_text(grp, "OfficerInd"))
            is_key_employee = _bool_as_float(_text(grp, "KeyEmployeeInd"))
            is_highest_compensated_employee = _bool_as_float(
                _text(grp, "HighestCompensatedEmployeeInd")
            )
            is_former_employee = _bool_as_float(
                _text(grp, "FormerEmployeeId")
            )
            # Weekly hours
            avg_weekly_hours_org = _float(
                _text(grp, "AverageHoursPerWeekRt")
                or _text(grp, "AverageHrsPerWkDevotedToPosRt")
            )
            avg_weekly_hours_related_org = _float(_text(grp, "AverageHoursPerWeekRltdOrgRt"))
            # Compensation
            comp = _float(
                _text(grp, "ReportableCompFromOrgAmt")
                or _text(grp, "CompensationAmt")
            )
            comp_related_org = _float(_text(grp, "ReportableCompFromRltdOrgAmt"))
            comp_other = _float(
                _text(grp, "OtherCompensationAmt")
                or _text(grp, "ExpenseAccountOtherAllwncAmt")
            )
            if person:
                rows.append({
                    "ein": ein,
                    "tax_year": tax_year,
                    "person_name": person,
                    "title": title,
                    "is_indiv_trustee_or_director": is_indiv_trustee_or_director,
                    "is_institutional_trustee": is_institutional_trustee,
                    "is_officer": is_officer,
                    "is_key_employee": is_key_employee,
                    "is_highest_compensated_employee": is_highest_compensated_employee,
                    "is_former_employee": is_former_employee,
                    "avg_weekly_hours_worked_org": avg_weekly_hours_org,
                    "avg_weekly_hours_worked_related_org": avg_weekly_hours_related_org,
                    "compensation_from_org": comp,
                    "compensation_from_related_org": comp_related_org,
                    "compensation_other": comp_other
                })
    return rows


def _parse_grants(return_data: etree._Element, ein: str | None,
                  tax_year: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sched_i = _child(return_data, "IRS990ScheduleI")
    if sched_i is None:
        return rows
    for grp in _findall(sched_i, "RecipientTable"):
        grantee_ein = _text(grp, "RecipientEIN") or _text(grp, "EINOfRecipient")
        grantee_name = (
            _text(grp, "RecipientBusinessName", "BusinessNameLine1Txt")
            or _text(grp, "RecipientNameBusiness", "BusinessNameLine1")
            or _text(grp, "RecipientPersonNm")
        )
        amount = _float(_text(grp, "CashGrantAmt") or _text(grp, "AmountOfCashGrant"))
        rows.append({
            "grantor_ein": ein,
            "grantee_ein": grantee_ein,
            "grantee_name": grantee_name,
            "amount": amount,
            "tax_year": tax_year,
        })
    return rows


def _parse_contractors(form: etree._Element, ein: str | None,
                    tax_year: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    contractor_groups = _findall(form, "ContractorCompensationGrp")
    if contractor_groups is None:
        return rows
    # Accounting for potential variation in element tags
    for contractor_group in contractor_groups:
        contractor = (
            _text(contractor_group, "ContractorName", "PersonNm")
            or _text(contractor_group, "ContractorName", "BusinessNameLine1Txt")
        )
        address = _text(contractor_group, "ContractorAddress", "AddressLine1Txt")
        state_code = _text(contractor_group, "ContractorAddress", "StateAbbreviationCd")
        city = _text(contractor_group, "ContractorAddress", "CityNm")
        zip_code = _text(contractor_group, "ContractorAddress", "ZIPCd")
        comp = _float(
            _text(contractor_group, "CompensationAmt")
        )
        services_desc = _text(contractor_group, "ServicesDesc")
        if contractor:
            rows.append({
                "ein": ein,
                "contractor_name": contractor,
                "address": address,
                "state": state_code,
                "city": city,
                "zip_code": zip_code,
                "compensation": comp,
                "tax_year": tax_year,
                "services_description": services_desc
            })
    return rows


# Part II-B checklist: which lobbying activities the filer engaged in.
# (element local-name, human-readable label)
_SCHEDULE_C_ACTIVITY_FLAGS = (
    ("VolunteersInd", "volunteers"),
    ("PaidStaffOrManagementInd", "paid_staff_or_management"),
    ("MediaAdvertisementsInd", "media_advertisements"),
    ("MailingsMembersInd", "mailings_to_members"),
    ("PublicationsOrBroadcastInd", "publications_or_broadcast"),
    ("GrantsOtherOrganizationsInd", "grants_to_other_organizations"),
    ("DirectContactLegislatorsInd", "direct_contact_with_legislators"),
    ("RalliesDemonstrationsInd", "rallies_or_demonstrations"),
    ("OtherActivitiesInd", "other_activities"),
)


def _parse_schedule_c(return_data: etree._Element, ein: str | None,
                      tax_year: int | None
                      ) -> tuple[dict[str, Any], list[dict[str, Any]] | None] | None:
    """Extract lobbying-expenditure data (Schedule C) for one return.

    Schedule C has three mutually-exclusive lobbying sections depending on
    the filer's exemption type and 501(h) election:
      - Part I-A: political organizations / 527(f) exempt-function spending.
      - Part II-A: 501(c)(3) orgs that elected the 501(h) expenditure test.
      - Part II-B: 501(c)(3) orgs that did NOT elect 501(h) (activity-based
        test); reports an activity checklist plus dollar amounts.
      - Part III-B: 501(c)(4)/(5)/(6) orgs; reports nondeductible lobbying
        and political dues allocations.
    Returns None if the filer did not attach Schedule C at all.
    """
    sched_c = _child(return_data, "IRS990ScheduleC")
    if sched_c is None:
        return None

    row: dict[str, Any] = {
        "ein": ein,
        "tax_year": tax_year,
        # Part I-A
        "total_exempt_function_expend_amt": _float(_text(sched_c, "TotalExemptFunctionExpendAmt")),
        # Part II-A (501(h) electors)
        "total_lobbying_expend_amt": _float(
            _text(sched_c, "TotalLobbyingExpendGrp", "FilingOrganizationsTotalAmt")
        ),
        "total_exempt_purpose_expend_amt": _float(
            _text(sched_c, "TotalExemptPurposeExpendGrp", "FilingOrganizationsTotalAmt")
        ),
        "lobbying_nontaxable_amt": _float(
            _text(sched_c, "LobbyingNontaxableAmountGrp", "FilingOrganizationsTotalAmt")
        ),
        "grassroots_nontaxable_amt": _float(
            _text(sched_c, "GrassrootsNontaxableGrp", "FilingOrganizationsTotalAmt")
        ),
        "lobbying_ceiling_amt": _float(_text(sched_c, "LobbyingCeilingAmt")),
        "grassroots_ceiling_amt": _float(_text(sched_c, "GrassrootsCeilingAmt")),
        # Part II-B (non-electing 501(c)(3))
        "total_lobbying_expenditures_amt": _float(_text(sched_c, "TotalLobbyingExpendituresAmt")),
        "direct_contact_legislators_amt": _float(_text(sched_c, "DirectContactLegislatorsAmt")),
        "other_lobbying_activities_amt": _float(_text(sched_c, "OtherActivitiesAmt")),
        # Part III-B (501(c)(4)/(5)/(6))
        "nondeductible_lobbying_pltcl_amt": _float(
            _text(sched_c, "NonDeductibleLbbyngPltclTotAmt")
        ),
        "taxable_amt": _float(_text(sched_c, "TaxableAmt")),
        "raw_json": None,
    }

    activity_types = [
        label for tag, label in _SCHEDULE_C_ACTIVITY_FLAGS
        if (_text(sched_c, tag) or "").lower() in {"1", "true", "x"}
    ]
    row["lobbying_activity_types"] = activity_types or None

    section_527_org_groups = _findall(sched_c, "Section527PoliticalOrgGrp")
    if section_527_org_groups is None:
        return row, None

    section_527_orgs: list[dict[str, Any]] = []
    for section_527_org_group in section_527_org_groups:
        _527_ein = _text(section_527_org_group, "EIN")
        _527_name = _text(section_527_org_group,
                          "OrganizationBusinessName", "BusinessNameLine1Text")
        _527_address = _text(section_527_org_group, "USAddress", "AddressLine1Text")
        _527_city = _text(section_527_org_group, "USAddress", "CityNm")
        _527_state_code = _text(section_527_org_group, "USAddress", "StateAbbreviationCd")
        _527_zip_code = _text(section_527_org_group, "USAddress", "ZIPCd")
        _527_paid_internal_funds = _float(_text(section_527_org_group, "PaidInternalFundsAmt"))
        _527_contributions_transferred = _float(
            _text(section_527_org_group, "ContributionsRcvdDlvrAmt")
        )
        section_527_orgs.append(
            {
                "filer_ein": ein,
                "tax_year": tax_year,
                "ein": _527_ein,
                "name": _527_name,
                "address": _527_address,
                "city": _527_city,
                "state_code": _527_state_code,
                "zip_code": _527_zip_code,
                "paid_internal_funds": _527_paid_internal_funds,
                "contributions_transferred": _527_contributions_transferred
            }
        )

    return row, section_527_orgs

def _parse_schedule_r(
    return_data: etree._Element, ein: str | None,
    tax_year: int | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | None:
    """Extract related org data (Schedule R) for one return.

    Schedule R has 7 sections depending on the type of
    organizations the filer is related to:
      - Part I: Identification of Disregarded Entities.
      - Part II: Identification of Related Tax-Exempt Organizations.
      - Part II: Identification of Related Organizations Taxable as a Partnership.
      - Part IV: Identification of Related Organizations Taxable as a Corporation or Trust.
      - Part V: (ONLY Q2 PARSED) Transactions With Related Organizations.
      - Part VI: (NOT PARSED) Unrelated Organizations Taxable as a Partnership.
      - Part VII: (NOT PARSED) Supplemental information.
    Returns None if the filer did not attach Schedule R at all.
    """
    sched_r = _child(return_data, "IRS990ScheduleR")
    if sched_r is None:
        return None

    sched_r_part_i = _findall(sched_r, 'IdDisregardedEntitiesGrp')
    related_orgs: list[dict[str, Any]] = []
    if sched_r_part_i is not None:
        for grp in sched_r_part_i:
            related_org_ein = _text(grp, "EIN")
            related_org_name = _text(grp, "DisregardedEntityName", "BusinessNameLine1Txt")
            related_org_primary_activities = _text(grp, "PrimaryActivitiesTxt")
            related_org_control_ent = _text(grp, "DirectControllingEntityName",
                                                          "BusinessNameLine1Txt")
            # Addres lines
            related_org_address = _text(grp, "USAddress", "AddressLine1Txt")
            related_org_state_code = _text(grp, "USAddress", "StateAbbreviationCd")
            related_org_city = _text(grp, "USAddress", "CityNm")
            related_org_zip_code = _text(grp, "USAddress", "ZIPCd")
            related_orgs.append({
                "filer_ein": ein,
                "tax_year": tax_year,
                "ein": related_org_ein,
                "name": related_org_name,
                "entity_type": "Disregarded",
                "primary_activities": related_org_primary_activities,
                "direct_controlling_entity": related_org_control_ent if \
                    related_org_control_ent not in ("N/A", "NA") else None,
                "address": related_org_address,
                "state_code": related_org_state_code,
                "city": related_org_city,
                "zip_code": related_org_zip_code
            })

    sched_r_part_ii = _findall(sched_r, 'IdRelatedTaxExemptOrgGrp')
    if sched_r_part_ii is not None:
        for grp in sched_r_part_ii:
            related_org_ein = _text(grp, "EIN")
            related_org_name = _text(grp, "DisregardedEntityName", "BusinessNameLine1Txt")
            related_org_entity_type = _text(grp, "ExemptCodeSectionTxt")
            related_org_primary_activities = _text(grp, "PrimaryActivitiesTxt")
            related_org_control_ent = _text(grp, "DirectControllingEntityName",
                                                          "BusinessNameLine1Txt")
            # Addres lines
            related_org_address = _text(grp, "USAddress", "AddressLine1Txt")
            related_org_state_code = _text(grp, "USAddress", "StateAbbreviationCd")
            related_org_city = _text(grp, "USAddress", "CityNm")
            related_org_zip_code = _text(grp, "USAddress", "ZIPCd")
            related_orgs.append({
                "filer_ein": ein,
                "tax_year": tax_year,
                "ein": related_org_ein,
                "name": related_org_name,
                "entity_type": related_org_entity_type,
                "primary_activities": related_org_primary_activities,
                "direct_controlling_entity": related_org_control_ent if \
                    related_org_control_ent not in ("N/A", "NA") else None,
                "address": related_org_address,
                "state_code": related_org_state_code,
                "city": related_org_city,
                "zip_code": related_org_zip_code
            })

    sched_r_part_iii = _findall(sched_r, 'IdRelatedOrgTxblPartnershipGrp')
    if sched_r_part_iii is not None:
        for grp in sched_r_part_iii:
            related_org_ein = _text(grp, "EIN")
            related_org_name = _text(grp, "RelatedOrganizationName", "BusinessNameLine1Txt")
            related_org_primary_activities = _text(grp, "PrimaryActivitiesTxt")
            related_org_control_ent = _text(grp, "DirectControllingEntityName",
                                                          "BusinessNameLine1Txt")
            # Addres lines
            related_org_address = _text(grp, "USAddress", "AddressLine1Txt")
            related_org_state_code = _text(grp, "USAddress", "StateAbbreviationCd")
            related_org_city = _text(grp, "USAddress", "CityNm")
            related_org_zip_code = _text(grp, "USAddress", "ZIPCd")
            related_orgs.append({
                "filer_ein": ein,
                "tax_year": tax_year,
                "ein": related_org_ein,
                "name": related_org_name,
                "entity_type": "Taxable Partnership",
                "primary_activities": related_org_primary_activities,
                "direct_controlling_entity": related_org_control_ent if \
                    related_org_control_ent not in ("N/A", "NA") else None,
                "address": related_org_address,
                "state_code": related_org_state_code,
                "city": related_org_city,
                "zip_code": related_org_zip_code
            })

    sched_r_part_iv = _findall(sched_r, 'IdRelatedOrgTxblCorpTrGrp')
    if sched_r_part_iv is not None:
        for grp in sched_r_part_iv:
            related_org_ein = _text(grp, "EIN")
            related_org_name = _text(grp, "RelatedOrganizationName", "BusinessNameLine1Txt")
            related_org_entity_type = _text(grp, "EntityTypeTxt")
            related_org_primary_activities = _text(grp, "PrimaryActivitiesTxt")
            related_org_control_ent = _text(grp, "DirectControllingEntityName",
                                                          "BusinessNameLine1Txt")
            # Addres lines
            related_org_address = _text(grp, "USAddress", "AddressLine1Txt")
            related_org_state_code = _text(grp, "USAddress", "StateAbbreviationCd")
            related_org_city = _text(grp, "USAddress", "CityNm")
            related_org_zip_code = _text(grp, "USAddress", "ZIPCd")
            related_orgs.append({
                "filer_ein": ein,
                "tax_year": tax_year,
                "ein": related_org_ein,
                "name": related_org_name,
                "entity_type": related_org_entity_type,
                "primary_activities": related_org_primary_activities,
                "direct_controlling_entity": related_org_control_ent if \
                    related_org_control_ent not in ("N/A", "NA") else None,
                "address": related_org_address,
                "state_code": related_org_state_code,
                "city": related_org_city,
                "zip_code": related_org_zip_code
            })

    sched_r_transactions = _findall(sched_r, 'TransactionsRelatedOrgGrp')
    transactions: list[dict[str, Any]] = []
    if sched_r_transactions is not None:
        for grp in sched_r_transactions:
            related_org_name = _text(grp, "OtherOrganizationName", "BusinessNameLine1Txt")
            related_org_transaction_type = _text(grp, "TransactionTypeTxt")
            related_org_transaction_amount = _float(_text(grp, "InvolvedAmt"))
            related_org_amount_determination_method = _text(grp, "MethodOfAmountDeterminationTxt")
            transactions.append({
                "filer_ein": ein,
                "tax_year": tax_year,
                "related_org_name": related_org_name,
                "type": related_org_transaction_type,
                "amount": related_org_transaction_amount,
                "amount_determination_method": related_org_amount_determination_method
            })

    return related_orgs, transactions

def ingest_990_file(path: str | Path) -> None:
    """Parse and write a single 990 XML file to SQLite."""
    init_db()
    parsed = parse_990_file(path)
    org = parsed["org"]
    if not org.get("ein"):
        logger.warning("Skipping %s: no EIN found", path)
        return
    with connect() as conn:
        upsert(conn, "orgs", org)
        insert_many(conn, "org_grants", parsed["grants"])
        insert_many(conn, "org_people", parsed["people"])
        insert_many(conn, "org_contractors", parsed["contractors"])
        if parsed["lobbying"]:
            upsert(conn, "org_lobbying", parsed["lobbying"])
            upsert(conn, "section_527_org", parsed["section_527_org"])
        if parsed["related_orgs"]:
            upsert(conn, "related_org", parsed["related_orgs"])
        if parsed["related_org_transactions"]:
            upsert(conn, "related_org_transaction", parsed["related_org_transactions"])


def ingest_990_directory(directory: str | Path, pattern: str = "*.xml") -> int:
    """Parse every matching XML file in a directory. Returns files ingested."""
    init_db()
    files = sorted(Path(directory).glob(pattern))
    count = 0
    with connect() as conn:
        for fp in files:
            try:
                parsed = parse_990_file(fp)
            except etree.XMLSyntaxError as exc:
                logger.warning("Bad XML %s: %s", fp, exc)
                continue
            org = parsed["org"]
            if not org.get("ein"):
                continue
            upsert(conn, "orgs", org)
            insert_many(conn, "org_grants", parsed["grants"])
            insert_many(conn, "org_people", parsed["people"])
            insert_many(conn, "org_contractors", parsed["contractors"])
            if parsed["lobbying"]:
                upsert(conn, "org_lobbying", parsed["lobbying"])
                upsert(conn, "section_527_org", parsed["section_527_orgs"])
            if parsed["related_orgs"]:
                upsert(conn, "related_org", parsed["related_orgs"])
            if parsed["related_org_transactions"]:
                upsert(conn, "related_org_transaction", parsed["related_org_transactions"])
            count += 1
            if count % 500 == 0:
                logger.info("Ingested %d 990 files...", count)
    logger.info("Ingested %d 990 files from %s", count, directory)
    return count


def iter_parsed(directory: str | Path, pattern: str = "*.xml") -> Iterable[dict[str, Any]]:
    """Yield parsed dicts without writing — useful for inspection/tests."""
    for fp in sorted(Path(directory).glob(pattern)):
        yield parse_990_file(fp)
