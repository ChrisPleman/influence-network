"""SQLite storage layer: schema and upsert helpers.

One DB file that all collectors write to. Raw API payloads are stored as JSON
so you can re-parse without re-pulling from rate-limited APIs.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

from .config import settings

# --- Schema -----------------------------------------------------------------
# Tables are grouped by source. `raw_json` columns preserve the full payload
# for re-parsing; structured columns hold the fields we join on.

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ===================== Congress.gov =====================
CREATE TABLE IF NOT EXISTS bills (
    bill_id        TEXT PRIMARY KEY,      -- e.g. "118-hr-1234"
    congress       INTEGER NOT NULL,
    bill_type      TEXT NOT NULL,         -- hr, s, hjres, ...
    bill_number    INTEGER NOT NULL,
    title          TEXT,
    introduced_date TEXT,
    latest_action  TEXT,
    policy_area    TEXT,
    raw_json       TEXT,
    fetched_at     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bill_actions (
    bill_id     TEXT NOT NULL REFERENCES bills(bill_id),
    action_date TEXT,
    action_code TEXT,
    action_text TEXT,
    raw_json    TEXT
);
CREATE INDEX IF NOT EXISTS idx_actions_bill ON bill_actions(bill_id);

CREATE TABLE IF NOT EXISTS bill_sponsors (
    bill_id    TEXT NOT NULL REFERENCES bills(bill_id),
    bioguide_id TEXT,
    full_name  TEXT,
    party      TEXT,
    state      TEXT,
    is_original_cosponsor INTEGER,  -- 0 = sponsor, 1 = cosponsor
    raw_json   TEXT
);
CREATE INDEX IF NOT EXISTS idx_sponsors_bill ON bill_sponsors(bill_id);

CREATE TABLE IF NOT EXISTS bill_text_versions (
    bill_id      TEXT NOT NULL REFERENCES bills(bill_id),
    version_code TEXT,                 -- e.g. "Introduced in House"
    version_date TEXT,
    format_type  TEXT,                 -- "Formatted Text", "XML", ...
    url          TEXT,
    PRIMARY KEY (bill_id, version_code, format_type)
);

CREATE TABLE IF NOT EXISTS members (
    bioguide_id TEXT PRIMARY KEY,
    full_name   TEXT,
    party       TEXT,
    state       TEXT,
    chamber     TEXT,
    raw_json    TEXT
);

-- ===================== FEC (openFEC) =====================
CREATE TABLE IF NOT EXISTS committees (
    committee_id   TEXT PRIMARY KEY,
    name           TEXT,
    committee_type TEXT,
    designation    TEXT,
    party          TEXT,
    raw_json       TEXT
);

CREATE TABLE IF NOT EXISTS fec_disbursements (
    sub_id          TEXT PRIMARY KEY,    -- FEC unique transaction id
    committee_id    TEXT,
    recipient_name  TEXT,
    disbursement_amount REAL,
    disbursement_date   TEXT,
    disbursement_description TEXT,
    raw_json        TEXT
);
CREATE INDEX IF NOT EXISTS idx_disb_committee ON fec_disbursements(committee_id);

-- ===================== Senate LDA =====================
CREATE TABLE IF NOT EXISTS lda_filings (
    filing_uuid    TEXT PRIMARY KEY,
    client_name    TEXT,
    registrant_name TEXT,
    filing_year    INTEGER,
    filing_period  TEXT,
    income         REAL,
    expenses       REAL,
    raw_json       TEXT
);
CREATE INDEX IF NOT EXISTS idx_lda_client ON lda_filings(client_name);

CREATE TABLE IF NOT EXISTS lda_lobbying_activities (
    filing_uuid   TEXT NOT NULL REFERENCES lda_filings(filing_uuid),
    general_issue_code TEXT,
    description   TEXT,             -- free-text issue description (NLP target)
    raw_json      TEXT
);
CREATE INDEX IF NOT EXISTS idx_lda_act_filing ON lda_lobbying_activities(filing_uuid);

-- ===================== IRS Form 990 =====================
CREATE TABLE IF NOT EXISTS orgs (
    ein         TEXT PRIMARY KEY,
    name        TEXT,
    tax_year    INTEGER,
    form_type   TEXT,
    exempt_organization_type TEXT,
    total_revenue REAL,
    total_expenses REAL,
    political_activity_flag INTEGER,
    mission     TEXT,
    raw_json    TEXT
);

CREATE TABLE IF NOT EXISTS org_grants (
    grantor_ein TEXT,
    grantee_ein TEXT,
    grantee_name TEXT,
    amount      REAL,
    tax_year    INTEGER
);
CREATE INDEX IF NOT EXISTS idx_grants_grantor ON org_grants(grantor_ein);
CREATE INDEX IF NOT EXISTS idx_grants_grantee ON org_grants(grantee_ein);

CREATE TABLE IF NOT EXISTS org_people (
    ein                                  TEXT NOT NULL REFERENCES orgs(ein),
    tax_year                             INTEGER NOT NULL,
    person_name                          TEXT NOT NULL,
    title                                TEXT NOT NULL,
    is_indiv_trustee_or_director         REAL NULL,
    is_institutional_trustee             REAL NULL,
    is_officer                           REAL NULL,
    is_key_employee                      REAL NULL,
    is_highest_compensated_employee      REAL NULL,
    is_former_employee                   REAL NULL,
    avg_weekly_hours_worked_org          REAL NULL,
    avg_weekly_hours_worked_related_org  REAL NULL,
    compensation_from_org                REAL NULL,
    compensation_from_related_org        REAL NULL,
    compensation_other                   REAL NULL,
    PRIMARY KEY (ein, tax_year, person_name)
);
CREATE INDEX IF NOT EXISTS idx_people_ein ON org_people(ein);
CREATE INDEX IF NOT EXISTS idx_people_name ON org_people(person_name);

CREATE TABLE IF NOT EXISTS org_contractors (
    ein        TEXT,
    contractor_name TEXT,
    address      TEXT,
    state      TEXT,
    city      TEXT,
    zip_code      TEXT,
    compensation REAL,
    tax_year   INTEGER,
    services_description TEXT
);
CREATE INDEX IF NOT EXISTS idx_contractor_ein ON org_contractors(ein);
CREATE INDEX IF NOT EXISTS idx_contractor_name ON org_contractors(contractor_name);

-- Schedule C: lobbying expenditures. One row per filing; not every org files
-- Schedule C, and which Part (II-A, II-B, III) is populated depends on the
-- filer's exemption type (501(h)-electing 501(c)(3), non-electing 501(c)(3),
-- or 501(c)(4)/(5)/(6)).
CREATE TABLE IF NOT EXISTS org_lobbying (
    ein                               TEXT PRIMARY KEY,
    tax_year                          INTEGER,
    total_exempt_function_expend_amt  REAL,  -- Part I-A (political orgs / 527)
    total_lobbying_expend_amt         REAL,  -- Part II-A line 1e (501(h) electors)
    total_exempt_purpose_expend_amt   REAL,  -- Part II-A line 1f
    lobbying_nontaxable_amt           REAL,  -- Part II-A line 1g
    grassroots_nontaxable_amt         REAL,  -- Part II-A line 1h
    lobbying_ceiling_amt              REAL,  -- Part II-A line 3 (4-yr avg base)
    grassroots_ceiling_amt            REAL,  -- Part II-A line 8 (4-yr avg base)
    total_lobbying_expenditures_amt   REAL,  -- Part II-B total (non-electing 501(c)(3))
    direct_contact_legislators_amt    REAL,  -- Part II-B line 1f
    other_lobbying_activities_amt     REAL,  -- Part II-B line 1j
    lobbying_activity_types           TEXT,  -- JSON list of checked Part II-B activities
    nondeductible_lobbying_pltcl_amt  REAL,  -- Part III-B (501(c)(4)/(5)/(6) dues nondeduct.)
    taxable_amt                       REAL,  -- Part III-B line 5 excise-tax base
    raw_json                          TEXT
);
CREATE INDEX IF NOT EXISTS idx_lobbying_ein ON org_lobbying(ein);

-- Some tax-exempt orgs contribute their internal funds, or transfer their
-- contributions to Super PACs (Section 527 Org). This information is captured here
CREATE TABLE IF NOT EXISTS section_527_org (
    filer_ein                    TEXT NOT NULL REFERENCES orgs(ein),
    tax_year                     INTEGER NOT NULL,
    ein                          TEXT,
    name                         TEXT NOT NULL,
    address                      TEXT,
    city                         TEXT,
    state_code                   TEXT,
    zip_code                     TEXT,
    paid_internal_funds          REAL NULL,
    contributions_transferred    REAL NULL,
    PRIMARY KEY (filer_ein, tax_year, name)
    
);
CREATE INDEX IF NOT EXISTS idx_section_527_org_filer_ein ON section_527_org(filer_ein);
CREATE INDEX IF NOT EXISTS idx_section_527_org_ein ON section_527_org(ein);
CREATE INDEX IF NOT EXISTS idx_section_527_org_name ON section_527_org(name);

-- Schedule R: related organization and transactions between them. Several rows
-- per filing; not every org files a Schedule R, and which Part (I-VII) is populated
-- depends on the type of organization the filer is related to, the types of
-- transactions between them, and any supplemental information that is relevant
-- to provide to the IRS.
CREATE TABLE IF NOT EXISTS related_org (
    filer_ein                    TEXT NOT NULL REFERENCES orgs(ein),
    tax_year                     INTEGER NOT NULL,
    ein                          TEXT NOT NULL,
    name                         TEXT NOT NULL,
    entity_type                  TEXT NOT NULL,
    primary_activities           TEXT,
    direct_controlling_entity    TEXT NULL,
    address                      TEXT,
    state_code                   TEXT,
    city                         TEXT,
    zip_code                     TEXT,
    PRIMARY KEY (filer_ein, tax_year, ein)
);
CREATE INDEX IF NOT EXISTS idx_related_org_filer_ein ON related_org(filer_ein);
CREATE INDEX IF NOT EXISTS idx_related_org_ein ON related_org(ein);
CREATE INDEX IF NOT EXISTS idx_related_org_name ON related_org(name);
CREATE INDEX IF NOT EXISTS idx_related_entity_type ON related_org(entity_type);

CREATE TABLE IF NOT EXISTS transaction_type (
    type_code TEXT PRIMARY KEY NOT NULL,
    type_desc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ids_transaction_type_code ON transaction_type(type_code);

INSERT OR IGNORE INTO transaction_type (type_code, type_desc)
VALUES 
    ('A', 'Receipt of (i) interest, (ii) annuities, (iii) royalties, or (iv) rent from a controlled entity.'),
    ('B', 'Gift, grant, or capital contribution to related organization(s).'),
    ('C', 'Gift, grant, or capital contribution from related organization(s).'),
    ('D', 'Loans or loan guarantees to or for related organization(s).'),
    ('E', 'Loans or loan guarantees by related organization(s.'),
    ('F', 'Dividends from related organization(s).'),
    ('G', 'Sale of assets to related organization(s)'),
    ('H', 'Purchase of assets from related organization(s).'),
    ('I', 'Exchange of assets with related organization(s).'),
    ('J', 'Lease of facilities, equipment, or other assets to related organization(s).'),
    ('K', 'Lease of facilities, equipment, or other assets from related organization(s).'),
    ('L', 'Performance of services or membership or fundraising solicitations for related organization(s.'),
    ('M', 'Performance of services or membership or fundraising solicitations by related organization(s).'),
    ('N', 'Sharing of facilities, equipment, mailing lists, or other assets with related organization(s).'),
    ('O', 'Sharing of paid employees with related organization(s).'),
    ('P', 'Reimbursement paid to related organization(s) for expenses.'),
    ('Q', 'Reimbursement paid by related organization(s) for expenses.'),
    ('R', 'Other transfer of cash or property to related organization(s).'),
    ('S', 'Other transfer of cash or property from related organization(s).');

CREATE TABLE IF NOT EXISTS related_org_transaction (
    filer_ein                    TEXT NOT NULL REFERENCES orgs(ein),
    tax_year                     INTEGER NOT NULL,
    related_org_name             TEXT NOT NULL,
    type                         TEXT NOT NULL REFERENCES transaction_type(type_code),
    amount                       REAL,
    amount_determination_method  TEXT,
    PRIMARY KEY (filer_ein, tax_year, related_org_name, type)
);
CREATE INDEX IF NOT EXISTS idx_related_org_transaction_filer_ein ON related_org_transaction(filer_ein);
"""

# IRS v2 is additive. The original IRS tables above are retained for existing
# notebooks, but are not suitable for annual history because their primary keys
# are EIN-centric. These tables make the individual IRS source object/filing the
# canonical record and scope every schedule row to that filing.
IRS990_V2_SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    ein             TEXT PRIMARY KEY,
    current_name    TEXT,
    normalized_name TEXT,
    first_seen_at   TEXT DEFAULT (datetime('now')),
    last_seen_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_organizations_normalized_name
    ON organizations(normalized_name);

CREATE TABLE IF NOT EXISTS irs990_source_objects (
    source_object_id TEXT PRIMARY KEY,
    file_name        TEXT NOT NULL,
    file_path        TEXT,
    content_sha256   TEXT NOT NULL,
    byte_size        INTEGER NOT NULL,
    parser_version   TEXT NOT NULL,
    ingest_status    TEXT NOT NULL,
    attempt_count    INTEGER NOT NULL DEFAULT 0,
    last_error       TEXT,
    first_attempt_at TEXT DEFAULT (datetime('now')),
    last_attempt_at  TEXT DEFAULT (datetime('now')),
    completed_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_irs990_source_status
    ON irs990_source_objects(ingest_status, parser_version);

CREATE TABLE IF NOT EXISTS irs990_filings (
    filing_id                INTEGER PRIMARY KEY,
    source_object_id         TEXT NOT NULL UNIQUE REFERENCES irs990_source_objects(source_object_id),
    ein                      TEXT NOT NULL REFERENCES organizations(ein),
    tax_year                 INTEGER,
    tax_period_end_date      TEXT,
    return_timestamp         TEXT,
    form_type                TEXT,
    filer_name               TEXT,
    exempt_organization_type TEXT,
    total_revenue            REAL,
    total_expenses           REAL,
    political_activity_flag  INTEGER,
    mission                  TEXT,
    parsed_at                TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_irs990_filings_ein_year ON irs990_filings(ein, tax_year);
CREATE INDEX IF NOT EXISTS idx_irs990_filings_form_year ON irs990_filings(form_type, tax_year);

CREATE TABLE IF NOT EXISTS irs990_filing_grants (
    filing_id    INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no      INTEGER NOT NULL,
    grantee_ein  TEXT,
    grantee_name TEXT,
    amount       REAL,
    PRIMARY KEY (filing_id, line_no)
);
CREATE INDEX IF NOT EXISTS idx_irs990_grants_grantee ON irs990_filing_grants(grantee_ein);

CREATE TABLE IF NOT EXISTS irs990_filing_people (
    filing_id INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no INTEGER NOT NULL,
    person_name TEXT, title TEXT,
    is_indiv_trustee_or_director REAL, is_institutional_trustee REAL,
    is_officer REAL, is_key_employee REAL, is_highest_compensated_employee REAL,
    is_former_employee REAL, avg_weekly_hours_worked_org REAL,
    avg_weekly_hours_worked_related_org REAL, compensation_from_org REAL,
    compensation_from_related_org REAL, compensation_other REAL,
    PRIMARY KEY (filing_id, line_no)
);

CREATE TABLE IF NOT EXISTS irs990_filing_contractors (
    filing_id INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no INTEGER NOT NULL,
    contractor_name TEXT, address TEXT, state TEXT, city TEXT, zip_code TEXT,
    compensation REAL, services_description TEXT,
    PRIMARY KEY (filing_id, line_no)
);

CREATE TABLE IF NOT EXISTS irs990_filing_lobbying (
    filing_id INTEGER PRIMARY KEY REFERENCES irs990_filings(filing_id),
    total_exempt_function_expend_amt REAL, total_lobbying_expend_amt REAL,
    total_exempt_purpose_expend_amt REAL, lobbying_nontaxable_amt REAL,
    grassroots_nontaxable_amt REAL, lobbying_ceiling_amt REAL,
    grassroots_ceiling_amt REAL, total_lobbying_expenditures_amt REAL,
    direct_contact_legislators_amt REAL, other_lobbying_activities_amt REAL,
    lobbying_activity_types TEXT, nondeductible_lobbying_pltcl_amt REAL,
    taxable_amt REAL
);

CREATE TABLE IF NOT EXISTS irs990_filing_527_orgs (
    filing_id INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no INTEGER NOT NULL, ein TEXT, name TEXT, address TEXT, city TEXT,
    state_code TEXT, zip_code TEXT, paid_internal_funds REAL,
    contributions_transferred REAL,
    PRIMARY KEY (filing_id, line_no)
);

CREATE TABLE IF NOT EXISTS irs990_filing_related_orgs (
    filing_id INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no INTEGER NOT NULL, ein TEXT, name TEXT, entity_type TEXT,
    primary_activities TEXT, direct_controlling_entity TEXT, address TEXT,
    state_code TEXT, city TEXT, zip_code TEXT,
    PRIMARY KEY (filing_id, line_no)
);
CREATE INDEX IF NOT EXISTS idx_irs990_related_org_ein ON irs990_filing_related_orgs(ein);

CREATE TABLE IF NOT EXISTS irs990_filing_related_org_transactions (
    filing_id INTEGER NOT NULL REFERENCES irs990_filings(filing_id),
    line_no INTEGER NOT NULL, related_org_name TEXT, type TEXT, amount REAL,
    amount_determination_method TEXT,
    PRIMARY KEY (filing_id, line_no)
);

-- Cross-source name matching is stored as evidence and review decisions; a
-- candidate score alone never makes two entities equivalent.
CREATE TABLE IF NOT EXISTS entity_observations (
    observation_id INTEGER PRIMARY KEY,
    source_system TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    subject_role TEXT NOT NULL,
    native_identifier TEXT,
    observed_name TEXT,
    normalized_name TEXT,
    irs_filing_id INTEGER REFERENCES irs990_filings(filing_id),
    observed_at TEXT,
    UNIQUE(source_system, source_record_id, subject_role)
);
CREATE INDEX IF NOT EXISTS idx_entity_observations_normalized_name
    ON entity_observations(normalized_name);

CREATE TABLE IF NOT EXISTS entity_match_candidates (
    candidate_id INTEGER PRIMARY KEY,
    left_observation_id INTEGER NOT NULL REFERENCES entity_observations(observation_id),
    right_observation_id INTEGER NOT NULL REFERENCES entity_observations(observation_id),
    matcher_name TEXT NOT NULL,
    score REAL NOT NULL,
    evidence_json TEXT,
    is_current INTEGER NOT NULL DEFAULT 1,
    invalidated_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    CHECK(left_observation_id < right_observation_id),
    UNIQUE(left_observation_id, right_observation_id, matcher_name)
);

CREATE TABLE IF NOT EXISTS entity_match_decisions (
    decision_id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES entity_match_candidates(candidate_id),
    decision TEXT NOT NULL CHECK(decision IN ('accepted', 'rejected', 'needs_review')),
    reviewer TEXT,
    rationale TEXT,
    decided_at TEXT DEFAULT (datetime('now'))
);
"""


@contextmanager
def connect(db_path: Path | None = None, timeout: float = 30.0) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with sane defaults, committing on success.

    timeout controls how long to wait for a write lock before raising. Default 30s
    is sufficient for concurrent ingestion where other writers may briefly hold the lock.
    """
    path = Path(db_path) if db_path else settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path | None = None) -> None:
    """Create all tables if they do not yet exist."""
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.executescript(IRS990_V2_SCHEMA)
        existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(orgs)")}
        for column, definition in (
            ("form_type", "TEXT"),
            ("exempt_organization_type", "TEXT"),
        ):
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE orgs ADD COLUMN {column} {definition}")
        candidate_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(entity_match_candidates)")
        }
        for column, definition in (
            ("is_current", "INTEGER NOT NULL DEFAULT 1"),
            ("invalidated_at", "TEXT"),
        ):
            if column not in candidate_columns:
                conn.execute(f"ALTER TABLE entity_match_candidates ADD COLUMN {column} {definition}")


def _coerce(value: Any) -> Any:
    """Make a Python value safe for sqlite binding (dict/list -> JSON)."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def upsert(conn: sqlite3.Connection, table: str, row: dict[str, Any]) -> None:
    """Insert or update a row without deleting referenced parent records."""
    cols = list(row.keys())
    placeholders = ", ".join("?" for _ in cols)
    col_list = ", ".join(cols)
    values = [_coerce(row[c]) for c in cols]
    updates = ", ".join(f"{column} = excluded.{column}" for column in cols)
    conn.execute(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT DO UPDATE SET {updates}",
        values,
    )


def insert_many(conn: sqlite3.Connection, table: str, rows: Iterable[dict[str, Any]]) -> int:
    """Insert-or-replace many rows; returns the count written."""
    count = 0
    for row in rows:
        upsert(conn, table, row)
        count += 1
    return count
