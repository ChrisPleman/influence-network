"""Congress.gov API v3 collector.

Pulls bills (with actions, sponsors, cosponsors, and text-version URLs) for a
given Congress and bill type, into the SQLite tables defined in db.py.

Docs: https://api.congress.gov/  |  https://github.com/LibraryOfCongress/api.congress.gov

Usage:
    from extract.congress import CongressCollector
    CongressCollector().collect_bills(congress=118, bill_type="hr", limit=50)
"""
from __future__ import annotations

import logging
from typing import Any, Iterator

from .config import settings
from .db import connect, init_db, insert_many, upsert
from .http import ApiClient

logger = logging.getLogger(__name__)

BASE_URL = "https://api.congress.gov/v3"
# Congress.gov allows 5,000 requests/hour with a key.
REQUESTS_PER_HOUR = 4500


class CongressCollector:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or settings.require("congress_api_key")
        self.client = ApiClient(
            BASE_URL,
            requests_per_hour=REQUESTS_PER_HOUR,
            default_params={"api_key": key, "format": "json"},
        )

    # --- low-level pagination ------------------------------------------------
    def _paginate(self, path: str, item_key: str, params: dict[str, Any] | None = None,
                  limit: int | None = None) -> Iterator[dict[str, Any]]:
        """Yield items across paginated Congress.gov responses.

        `item_key` is the top-level list field (e.g. "bills", "actions").
        """
        offset = 0
        page_size = 250  # API max
        yielded = 0
        while True:
            page_params = {"offset": offset, "limit": page_size, **(params or {})}
            data = self.client.get(path, page_params)
            items = data.get(item_key, []) or []
            if not items:
                break
            for item in items:
                yield item
                yielded += 1
                if limit and yielded >= limit:
                    return
            if len(items) < page_size:
                break
            offset += page_size

    # --- public collectors ---------------------------------------------------
    def collect_bills(self, congress: int, bill_type: str, limit: int | None = None) -> int:
        """Collect bills + their actions/sponsors/text versions.

        Returns the number of bills written.
        """
        init_db()
        bill_type = bill_type.lower()
        count = 0
        with connect() as conn:
            for stub in self._paginate(
                f"bill/{congress}/{bill_type}", "bills", limit=limit
            ):
                number = stub.get("number")
                if number is None:
                    continue
                bill_id = f"{congress}-{bill_type}-{number}"
                detail = self._fetch_bill_detail(congress, bill_type, number)
                upsert(conn, "bills", self._bill_row(bill_id, congress, bill_type, number, detail))

                self._collect_actions(conn, bill_id, congress, bill_type, number)
                self._collect_sponsors(conn, bill_id, congress, bill_type, number, detail)
                self._collect_text_versions(conn, bill_id, congress, bill_type, number)
                count += 1
                if count % 25 == 0:
                    logger.info("Collected %d bills (%s)...", count, bill_id)
        logger.info("Done: %d bills for congress %d %s", count, congress, bill_type)
        return count

    # --- helpers -------------------------------------------------------------
    def _fetch_bill_detail(self, congress: int, bill_type: str, number: int) -> dict[str, Any]:
        data = self.client.get(f"bill/{congress}/{bill_type}/{number}")
        return data.get("bill", {}) or {}

    @staticmethod
    def _bill_row(bill_id: str, congress: int, bill_type: str, number: int,
                  detail: dict[str, Any]) -> dict[str, Any]:
        latest = detail.get("latestAction") or {}
        policy = detail.get("policyArea") or {}
        return {
            "bill_id": bill_id,
            "congress": congress,
            "bill_type": bill_type,
            "bill_number": number,
            "title": detail.get("title"),
            "introduced_date": detail.get("introducedDate"),
            "latest_action": latest.get("text"),
            "policy_area": policy.get("name"),
            "raw_json": detail,
        }

    def _collect_actions(self, conn, bill_id, congress, bill_type, number) -> None:
        rows = (
            {
                "bill_id": bill_id,
                "action_date": a.get("actionDate"),
                "action_code": a.get("actionCode"),
                "action_text": a.get("text"),
                "raw_json": a,
            }
            for a in self._paginate(
                f"bill/{congress}/{bill_type}/{number}/actions", "actions"
            )
        )
        insert_many(conn, "bill_actions", rows)

    def _collect_sponsors(self, conn, bill_id, congress, bill_type, number, detail) -> None:
        # Primary sponsor(s) live on the detail payload.
        for sp in detail.get("sponsors", []) or []:
            upsert(conn, "bill_sponsors", {
                "bill_id": bill_id,
                "bioguide_id": sp.get("bioguideId"),
                "full_name": sp.get("fullName"),
                "party": sp.get("party"),
                "state": sp.get("state"),
                "is_original_cosponsor": 0,
                "raw_json": sp,
            })
        # Cosponsors come from a sub-endpoint.
        for cs in self._paginate(
            f"bill/{congress}/{bill_type}/{number}/cosponsors", "cosponsors"
        ):
            upsert(conn, "bill_sponsors", {
                "bill_id": bill_id,
                "bioguide_id": cs.get("bioguideId"),
                "full_name": cs.get("fullName"),
                "party": cs.get("party"),
                "state": cs.get("state"),
                "is_original_cosponsor": 1,
                "raw_json": cs,
            })

    def _collect_text_versions(self, conn, bill_id, congress, bill_type, number) -> None:
        for tv in self._paginate(
            f"bill/{congress}/{bill_type}/{number}/text", "textVersions"
        ):
            for fmt in tv.get("formats", []) or []:
                upsert(conn, "bill_text_versions", {
                    "bill_id": bill_id,
                    "version_code": tv.get("type"),
                    "version_date": tv.get("date"),
                    "format_type": fmt.get("type"),
                    "url": fmt.get("url"),
                })

    def close(self) -> None:
        self.client.close()
