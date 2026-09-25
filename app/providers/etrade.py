"""Read-only E*TRADE market-data adapter.

This adapter intentionally exposes only market quotes and option chains.
It does not expose order endpoints and does not treat option-chain snapshots
as an authoritative transaction tape.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from typing import Any


@dataclass(frozen=True)
class ETradeCredentials:
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str


class ETradeClient:
    """Minimal read-only E*TRADE market-data client using OAuth 1.0a."""

    def __init__(self, credentials: ETradeCredentials, *, sandbox: bool = False, timeout: int = 20):
        self.credentials = credentials
        self.timeout = timeout
        self.base_url = "https://apisb.etrade.com/v1" if sandbox else "https://api.etrade.com/v1"

    @staticmethod
    def _oauth_encode(value: str) -> str:
        return quote(str(value), safe="-._~")

    def _authorization_header(self, method: str, url: str, params: dict[str, Any] | None = None) -> str:
        params = params or {}
        oauth = {
            "oauth_consumer_key": self.credentials.consumer_key,
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.credentials.access_token,
            "oauth_version": "1.0",
        }

        parsed = urlsplit(url)
        signing_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        signing_pairs += [(str(k), str(v)) for k, v in params.items() if v is not None]
        signing_pairs += list(oauth.items())
        signing_pairs.sort(key=lambda p: (self._oauth_encode(p[0]), self._oauth_encode(p[1])))

        normalized = "&".join(
            f"{self._oauth_encode(k)}={self._oauth_encode(v)}" for k, v in signing_pairs
        )
        base_uri = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        base_string = "&".join([
            method.upper(),
            self._oauth_encode(base_uri),
            self._oauth_encode(normalized),
        ])
        signing_key = (
            f"{self._oauth_encode(self.credentials.consumer_secret)}"
            f"&{self._oauth_encode(self.credentials.access_token_secret)}"
        )
        digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        oauth["oauth_signature"] = base64.b64encode(digest).decode()

        return "OAuth " + ", ".join(
            f'{self._oauth_encode(k)}="{self._oauth_encode(v)}"' for k, v in oauth.items()
        )

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}.json"
        clean = {k: v for k, v in params.items() if v is not None}
        request = Request(
            f"{url}?{urlencode(clean)}",
            headers={
                "Authorization": self._authorization_header("GET", url, clean),
                "Accept": "application/json",
                "Connection": "close",
            },
            method="GET",
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def quote(self, symbols: str | list[str]) -> dict[str, Any]:
        """Return quote data for one or more symbols."""
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        return self._get(f"market/quote/{symbols}", {})

    def option_expirations(self, symbol: str) -> dict[str, Any]:
        """Return available option expiration dates."""
        return self._get("market/optionexpiredate", {"symbol": symbol, "expiryType": "ALL"})

    def option_chain(
        self,
        symbol: str,
        *,
        expiry_year: int | None = None,
        expiry_month: int | None = None,
        expiry_day: int | None = None,
        strike_price_near: float | None = None,
        no_of_strikes: int | None = None,
        include_weekly: bool | None = True,
        skip_adjusted: bool | None = True,
        option_category: str | None = "STANDARD",
        chain_type: str | None = "CALLPUT",
        price_type: str | None = "ATNM",
    ) -> dict[str, Any]:
        """Return option-chain snapshots with bid/ask, volume, OI and Greeks when available."""
        params = {
            "symbol": symbol,
            "expiryYear": expiry_year,
            "expiryMonth": expiry_month,
            "expiryDay": expiry_day,
            "strikePriceNear": strike_price_near,
            "noOfStrikes": no_of_strikes,
            "includeWeekly": str(include_weekly).lower() if include_weekly is not None else None,
            "skipAdjusted": str(skip_adjusted).lower() if skip_adjusted is not None else None,
            "optionCategory": option_category,
            "chainType": chain_type,
            "priceType": price_type,
        }
        return self._get("market/optionchains", params)
