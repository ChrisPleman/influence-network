"""Extraction package for the Dark Money Influence Network capstone.

Submodules:
    config   - environment/config loading
    http     - shared rate-limited, retrying HTTP session
    db       - SQLite schema + insert helpers
    congress - Congress.gov API v3 collector
    fec      - openFEC API collector
    lda      - Senate LDA API collector
    irs990   - IRS Form 990 XML parser
"""

__all__ = ["config", "http", "db"]
