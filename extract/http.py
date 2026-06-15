"""Shared HTTP layer: a polite, rate-limited, retrying JSON client.

All API collectors build on `ApiClient` so retry/backoff and throttling
behaviour is consistent across Congress.gov, openFEC, and Senate LDA.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple thread-safe minimum-interval throttle.

    `min_interval` is the minimum number of seconds between requests,
    derived from an API's stated per-hour / per-minute limit.
    """

    def __init__(self, min_interval: float) -> None:
        self._min_interval = max(0.0, min_interval)
        self._lock = threading.Lock()
        self._last_call = 0.0

    def wait(self) -> None:
        with self._lock:
            elapsed = time.monotonic() - self._last_call
            sleep_for = self._min_interval - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._last_call = time.monotonic()


# Exceptions that are worth retrying (transient network / server issues).
_RETRYABLE = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


class RetryableStatusError(requests.exceptions.RequestException):
    """Raised for 429/5xx so tenacity will retry the call."""


class ApiClient:
    """A configured requests session with throttling + retry.

    Parameters
    ----------
    base_url:
        Root URL the collector appends paths to.
    requests_per_hour:
        Used to compute the polite minimum interval between calls.
    default_params:
        Params merged into every request (e.g. an API key).
    timeout:
        Per-request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str,
        requests_per_hour: float = 1000.0,
        default_params: dict[str, Any] | None = None,
        timeout: float = 30.0,
        user_agent: str = "influence-network-capstone/0.1 (educational research)",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_params = dict(default_params or {})
        self.timeout = timeout
        self._limiter = RateLimiter(3600.0 / requests_per_hour if requests_per_hour else 0.0)
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})

    @retry(
        retry=retry_if_exception_type(_RETRYABLE + (RetryableStatusError,)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET a path and return parsed JSON, retrying transient failures."""
        self._limiter.wait()
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        merged = {**self.default_params, **(params or {})}

        resp = self._session.get(url, params=merged, timeout=self.timeout)

        if resp.status_code == 429 or resp.status_code >= 500:
            # Honour Retry-After when the server provides it.
            retry_after = resp.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
            logger.warning("Retryable HTTP %s for %s", resp.status_code, url)
            raise RetryableStatusError(f"HTTP {resp.status_code} for {url}")

        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
