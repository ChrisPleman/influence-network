"""Senate LDA (Lobbying Disclosure Act) API collector.

Pulls lobbying filings and their lobbying-activity descriptions (the free-text
issue summaries that are the NLP target) into SQLite.

Docs: https://lda.senate.gov/api/redoc/v1/

Usage:
    from extract.lda import LdaCollector
    LdaCollector().collect_filings(filing_year=2024, limit=200)
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from .config import settings
from .db import connect, init_db, insert_many, upsert
from .http import ApiClient

logger = logging.getLogger(__name__)

BASE_URL = "https://lda.senate.gov/api/v1"
# Anonymous ~15/min; with key ~120/min. Stay polite at ~600/hr default.
REQUESTS_PER_HOUR = 600


class LdaCollector:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or settings.lda_api_key
        default_params: dict[str, Any] = {}
        client = ApiClient(BASE_URL, requests_per_hour=REQUESTS_PER_HOUR,
                           default_params=default_params)
        # LDA uses a token auth header when a key is supplied.
        if key:
            client._session.headers["Authorization"] = f"Token {key}"
        self.client = client

    def _paginate(self, path: str, params: dict[str, Any] | None = None,
                  limit: int | None = None) -> Iterator[dict[str, Any]]:
        """Yield results across LDA's DRF-style next-URL pagination."""
        page_params = {"page": 1, "page_size": 25, **(params or {})}
        url: str | None = path
        yielded = 0
        first = True
        while url:
            data = self.client.get(url, page_params if first else None)
            first = False
            for item in data.get("results", []) or []:
                yield item
                yielded += 1
                if limit and yielded >= limit:
                    return
            url = data.get("next")  # absolute URL or None

    def collect_filings(self, filing_year: int, limit: int | None = None) -> int:
        """Collect filings for a year plus their lobbying activities."""
        init_db()
        count = 0
        with connect() as conn:
            for f in self._paginate(
                "filings/", {"filing_year": filing_year}, limit=limit
            ):
                uuid = f.get("filing_uuid")
                client = f.get("client") or {}
                registrant = f.get("registrant") or {}
                upsert(conn, "lda_filings", {
                    "filing_uuid": uuid,
                    "client_name": client.get("name"),
                    "registrant_name": registrant.get("name"),
                    "filing_year": f.get("filing_year"),
                    "filing_period": f.get("filing_period"),
                    "income": f.get("income"),
                    "expenses": f.get("expenses"),
                    "raw_json": f,
                })
                activities = (
                    {
                        "filing_uuid": uuid,
                        "general_issue_code": a.get("general_issue_code"),
                        "description": a.get("description"),
                        "raw_json": a,
                    }
                    for a in (f.get("lobbying_activities") or [])
                )
                insert_many(conn, "lda_lobbying_activities", activities)
                count += 1
                if count % 50 == 0:
                    logger.info("Collected %d LDA filings...", count)
        logger.info("Collected %d LDA filings (year %d)", count, filing_year)
        return count

    def close(self) -> None:
        self.client.close()
