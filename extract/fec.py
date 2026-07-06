"""openFEC (FEC) API collector.

Pulls committees (e.g. Super PACs) and their disbursements into SQLite.

Docs: https://api.open.fec.gov/developers/

Usage:
    from extract.fec import FecCollector
    fec = FecCollector()
    fec.collect_committees(committee_type="O")        # O = Super PAC
    fec.collect_disbursements(cycle=2024, limit=500)
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from .config import settings
from .db import connect, init_db, upsert
from .http import ApiClient

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open.fec.gov/v1"
# A registered key gives 1,000/hr (7,200/hr on request). DEMO_KEY is far lower.
REQUESTS_PER_HOUR = 900


class FecCollector:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or settings.fec_api_key or "DEMO_KEY"
        self.client = ApiClient(
            BASE_URL,
            requests_per_hour=REQUESTS_PER_HOUR,
            default_params={"api_key": key},
        )

    def _paginate(self, path: str, params: dict[str, Any] | None = None,
                  limit: int | None = None) -> Iterator[dict[str, Any]]:
        """Yield results across openFEC's page-based pagination."""
        page = 1
        per_page = 100
        yielded = 0
        while True:
            page_params = {"per_page": per_page, "page": page, **(params or {})}
            data = self.client.get(path, page_params)
            results = data.get("results", []) or []
            if not results:
                break
            for item in results:
                yield item
                yielded += 1
                if limit and yielded >= limit:
                    return
            pagination = data.get("pagination", {}) or {}
            pages = pagination.get("pages", page)
            if page >= pages:
                break
            page += 1

    def collect_committees(self, committee_type: str | None = None,
                           limit: int | None = None) -> int:
        """Collect committees, optionally filtered by FEC committee_type.

        committee_type "O" = Super PAC (independent-expenditure-only).
        """
        init_db()
        params: dict[str, Any] = {}
        if committee_type:
            params["committee_type"] = committee_type
        count = 0
        with connect() as conn:
            for c in self._paginate("committees", params, limit=limit):
                upsert(conn, "committees", {
                    "committee_id": c.get("committee_id"),
                    "name": c.get("name"),
                    "committee_type": c.get("committee_type"),
                    "designation": c.get("designation"),
                    "party": c.get("party"),
                    "raw_json": c,
                })
                count += 1
        logger.info("Collected %d committees", count)
        return count

    def collect_disbursements(self, cycle: int, committee_id: str | None = None,
                              limit: int | None = None) -> int:
        """Collect Schedule B disbursements for a two-year cycle."""
        init_db()
        params: dict[str, Any] = {"two_year_transaction_period": cycle, "sort": "-disbursement_date"}
        if committee_id:
            params["committee_id"] = committee_id
        count = 0
        with connect() as conn:
            for d in self._paginate("schedules/schedule_b", params, limit=limit):
                upsert(conn, "fec_disbursements", {
                    "sub_id": d.get("sub_id"),
                    "committee_id": d.get("committee_id"),
                    "recipient_name": d.get("recipient_name"),
                    "disbursement_amount": d.get("disbursement_amount"),
                    "disbursement_date": d.get("disbursement_date"),
                    "disbursement_description": d.get("disbursement_description"),
                    "raw_json": d,
                })
                count += 1
                if count % 100 == 0:
                    logger.info("Collected %d disbursements...", count)
        logger.info("Collected %d disbursements (cycle %d)", count, cycle)
        return count

    def close(self) -> None:
        self.client.close()
