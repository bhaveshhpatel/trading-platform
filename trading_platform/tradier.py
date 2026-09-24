import os
import requests
from datetime import datetime, timezone


class TradierDelayed:
    """Tradier sandbox delayed option snapshots.

    This is a free-account research supplement, not a full raw tape. Tradier
    documents sandbox options data as delayed by 15 minutes and does not offer
    delayed paper streaming.
    """

    def __init__(self, token=None):
        self.token = token or os.getenv("TRADIER_SANDBOX_TOKEN")
        if not self.token:
            raise ValueError("TRADIER_SANDBOX_TOKEN is required")
        self.base = os.getenv("TRADIER_BASE_URL", "https://sandbox.tradier.com/v1")

    def snapshot(self, symbols):
        r = requests.get(
            f"{self.base}/markets/quotes",
            params={"symbols": ",".join(symbols), "greeks": "false"},
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
            timeout=20,
        )
        r.raise_for_status()
        rows = r.json().get("quotes", {}).get("quote", [])
        if isinstance(rows, dict):
            rows = [rows]
        now = datetime.now(timezone.utc).isoformat()
        for q in rows:
            yield {
                "observed_at": now,
                "symbol": q.get("symbol"),
                "bid": q.get("bid"),
                "ask": q.get("ask"),
                "last": q.get("last"),
                "volume": q.get("volume"),
                "open_interest": q.get("open_interest"),
                "source": "tradier_sandbox",
                "data_status": "15m_delayed_snapshot_not_raw_tape",
            }
