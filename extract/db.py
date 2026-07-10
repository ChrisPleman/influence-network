"""SQLite storage layer: schema definition + idempotent upsert helpers.

The schema is intentionally normalized but lightweight — one DB file that
all collectors write to. Raw API payloads are also stored as JSON so you can
re-parse later without re-pulling from rate-limited APIs.
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
    ein        TEXT,
    person_name TEXT,
    title      TEXT,
    compensation REAL,
    tax_year   INTEGER
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
    tax_year   INTEGER
    services_description      TEXT,
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
    ein                          TEXT NOT NULL
    name                         TEXT NOT NULL.
    address                      TEXT NOT NULL,
    city                         TEXT NOT NULL,
    state_code                   TEXT NOT NULL,
    zip_code                     TEXT NOT NULL,
    paid_internal_funds          REAL NULL,
    contributions_transferred    REAL NULL,
    PRIMARY KEY (filer_ein, tax_year, ein)
    
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
    primary_activities           TEXT NOT NULL,
    direct_controlling_entity    TEXT NULL,
    address                      TEXT NOT NULL,
    state_code                   TEXT NOT NULL,
    city                         TEXT NOT NULL,
    zip_code                     TEXT NOT NULL,
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

INSERT INTO transaction_type (type_code, type_desc) 
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
    name                         TEXT NOT NULL,
    type                         TEXT NOT NULL REFERENCES transaction_type(type_code),
    primary_activities           TEXT NOT NULL,
    direct_controlling_entity    TEXT NULL,
    address                      TEXT NOT NULL,
    state_code                   TEXT NOT NULL,
    city                         TEXT NOT NULL,
    zip_code                     TEXT NOT NULL,
    PRIMARY KEY (filer_ein, tax_year, ein)
);
CREATE INDEX IF NOT EXISTS idx_related_org_transaction_filer_ein ON related_org_transaction(filer_ein);
CREATE INDEX IF NOT EXISTS idx_related_org_ein ON related_org(ein);
CREATE INDEX IF NOT EXISTS idx_related_org_name ON related_org(name);
"""


@contextmanager
def connect(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with sane defaults, committing on success."""
    path = Path(db_path) if db_path else settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
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


def _coerce(value: Any) -> Any:
    """Make a Python value safe for sqlite binding (dict/list -> JSON)."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def upsert(conn: sqlite3.Connection, table: str, row: dict[str, Any]) -> None:
    """Insert-or-replace a single row keyed on the table's primary key."""
    cols = list(row.keys())
    placeholders = ", ".join("?" for _ in cols)
    col_list = ", ".join(cols)
    values = [_coerce(row[c]) for c in cols]
    conn.execute(
        f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})",
        values,
    )


def insert_many(conn: sqlite3.Connection, table: str, rows: Iterable[dict[str, Any]]) -> int:
    """Insert-or-replace many rows; returns the count written."""
    count = 0
    for row in rows:
        upsert(conn, table, row)
        count += 1
    return count
