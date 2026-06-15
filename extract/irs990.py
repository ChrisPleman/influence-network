"""IRS Form 990 e-file XML parser.

The IRS publishes 990 returns as XML (one file per return) in annual bulk
downloads. Schemas vary by year, and elements live in the
``http://www.irs.gov/efile`` namespace. To stay robust across schema versions
this parser matches on element *local-name* rather than fixed namespaced paths.

Extracted into SQLite: organization header (EIN, name, revenue, expenses,
mission), grants paid (Schedule I), and officers/directors/key employees.

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

    if return_data is not None:
        form = _child(return_data, "IRS990")
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
            # Political activity signal: Schedule C presence / 501(c)(4) flag.
            pol = _text(form, "PoliticalCampaignActyInd") or _text(form, "PoliticalActivitiesInd")
            org["political_activity_flag"] = 1 if (pol and pol.lower() in {"1", "true", "x"}) else 0

            people.extend(_parse_officers(form, org["ein"], org["tax_year"]))

        grants.extend(_parse_grants(return_data, org["ein"], org["tax_year"]))

    return {"org": org, "grants": grants, "people": people}


def _parse_officers(form: etree._Element, ein: str | None,
                    tax_year: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Officers/Directors/Trustees/Key Employees group element name varies.
    for grp_tag in ("Form990PartVIISectionAGrp", "OfficerDirectorTrusteeKeyEmpl"):
        for grp in _findall(form, grp_tag):
            person = (
                _text(grp, "PersonNm")
                or _text(grp, "PersonName")
                or _text(grp, "NamePerson")
            )
            title = _text(grp, "TitleTxt") or _text(grp, "Title")
            comp = _float(
                _text(grp, "ReportableCompFromOrgAmt")
                or _text(grp, "CompensationAmt")
            )
            if person:
                rows.append({
                    "ein": ein,
                    "person_name": person,
                    "title": title,
                    "compensation": comp,
                    "tax_year": tax_year,
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
            count += 1
            if count % 500 == 0:
                logger.info("Ingested %d 990 files...", count)
    logger.info("Ingested %d 990 files from %s", count, directory)
    return count


def iter_parsed(directory: str | Path, pattern: str = "*.xml") -> Iterable[dict[str, Any]]:
    """Yield parsed dicts without writing — useful for inspection/tests."""
    for fp in sorted(Path(directory).glob(pattern)):
        yield parse_990_file(fp)
