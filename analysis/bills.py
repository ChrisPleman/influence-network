"""Extract bill references from free text and link lobbying activities to bills.

LDA lobbying-activity descriptions frequently name specific bills, e.g.
    "HR 824 - Telehealth Benefit Expansion... HR 1843/S1001..."
This module pulls those bill IDs out with a regex (high precision, no model
needed) and produces a join key that matches Congress.gov's bill_id format.

Bill ID format used here: "{type}{number}", e.g. "hr824", "s1001".
Congress is NOT in the LDA text, so the link is on (type, number) and you
disambiguate by filing_year / congress when joining to the bills table.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Bill/resolution type prefixes Congress uses.
# Order matters: match longer prefixes (hjres) before shorter (h).
_BILL_TYPES = [
    "hjres", "sjres", "hconres", "sconres", "hres", "sres", "hr", "s",
]

# Matches: HR 1234, H.R. 1234, H R 1234, S.1001, S 1001, H.J.Res. 5, etc.
# Group 1 = type letters (with optional dots/spaces), Group 2 = number.
_PATTERN = re.compile(
    r"\b("
    r"H\.?\s?J\.?\s?Res\.?|S\.?\s?J\.?\s?Res\.?|"
    r"H\.?\s?Con\.?\s?Res\.?|S\.?\s?Con\.?\s?Res\.?|"
    r"H\.?\s?Res\.?|S\.?\s?Res\.?|"
    r"H\.?\s?R\.?|S"
    r")\.?\s?(\d{1,5})\b",
    re.IGNORECASE,
)


def _normalize_type(raw: str) -> str:
    """Collapse 'H.R.' / 'H R' / 'HJRes' to canonical lowercase type."""
    compact = re.sub(r"[.\s]", "", raw).lower()  # 'h.r.' -> 'hr', 'h j res' -> 'hjres'
    # Map a couple of aliases just in case.
    return compact


@dataclass(frozen=True)
class BillRef:
    """A bill reference found in text. `bill_type`+`number` join to Congress."""
    bill_type: str   # e.g. "hr", "s", "hjres"
    number: int

    @property
    def key(self) -> str:
        return f"{self.bill_type}{self.number}"


def extract_bill_refs(text: str | None) -> list[BillRef]:
    """Return unique bill references found in a piece of text.

    >>> [r.key for r in extract_bill_refs("HR 824 and S1001, plus H.J.Res. 5")]
    ['hr824', 's1001', 'hjres5']
    """
    if not text:
        return []
    found: dict[str, BillRef] = {}
    for m in _PATTERN.finditer(text):
        btype = _normalize_type(m.group(1))
        if btype not in _BILL_TYPES:
            continue
        number = int(m.group(2))
        ref = BillRef(btype, number)
        found[ref.key] = ref  # dedupe by key
    return list(found.values())


# --- DB-backed linking --------------------------------------------------------

def build_lobbying_bill_links(db_path=None) -> int:
    """Scan lda_lobbying_activities, extract bill refs, store links in a table.

    Creates table `lobbying_bill_links(filing_uuid, bill_type, bill_number,
    bill_key)` and fills it. Returns the number of links written.
    """
    # Imported here so the regex functions above stay dependency-free.
    from extract.db import connect

    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lobbying_bill_links (
                filing_uuid TEXT,
                bill_type   TEXT,
                bill_number INTEGER,
                bill_key    TEXT,
                UNIQUE(filing_uuid, bill_key)
            )
            """
        )
        rows = conn.execute(
            "SELECT filing_uuid, description FROM lda_lobbying_activities"
        ).fetchall()

        count = 0
        for row in rows:
            for ref in extract_bill_refs(row["description"]):
                conn.execute(
                    "INSERT OR IGNORE INTO lobbying_bill_links "
                    "(filing_uuid, bill_type, bill_number, bill_key) VALUES (?, ?, ?, ?)",
                    (row["filing_uuid"], ref.bill_type, ref.number, ref.key),
                )
                count += 1
    return count
