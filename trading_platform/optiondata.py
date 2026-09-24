import json
import os
import re
from datetime import datetime, timezone
import websocket
from .core import OptionTrade

OCC_RE = re.compile(r"^(.+?)(\d{6})([CP])(\d{8})$")


class OptionDataRaw:
    """Optional OptionData.io RAW trade stream.

    RAW emits one service record per received print, but the provider explicitly
    does not guarantee a complete/lossless OPRA session. Access is trial/paid,
    not permanently free.
    """

    def __init__(self, token=None):
        self.token = token or os.getenv("OPTIONDATA_API_KEY")
        if not self.token:
            raise ValueError("OPTIONDATA_API_KEY is required")
        self.url = os.getenv("OPTIONDATA_WS_URL", "wss://ws.optiondata.io")

    @staticmethod
    def _contract(symbol):
        m = OCC_RE.match(symbol.upper())
        if not m:
            return None, None, None, None
        root, ymd, right, strike = m.groups()
        return root, datetime.strptime(ymd, "%y%m%d").date().isoformat(), right, int(strike) / 1000

    def stream(self, symbols=None):
        ws = websocket.create_connection(self.url, timeout=20)
        try:
            payload = {"token": self.token, "aggregation_mode": "RAW"}
            if symbols:
                payload["symbols"] = ",".join(symbols)
            ws.send(json.dumps(payload))
            while True:
                raw = ws.recv()
                if raw is None:
                    break
                rows = json.loads(raw)
                if isinstance(rows, dict):
                    rows = [rows]
                for row in rows:
                    symbol = str(row.get("symbol") or row.get("S") or "").upper()
                    underlying, expiry, right, strike = self._contract(symbol)
                    if not underlying:
                        continue
                    ts_raw = row.get("timestamp") or row.get("ts") or row.get("t")
                    if ts_raw is None:
                        continue
                    if isinstance(ts_raw, (int, float)):
                        ts = datetime.fromtimestamp(
                            ts_raw / 1000 if ts_raw > 10_000_000_000 else ts_raw,
                            tz=timezone.utc,
                        )
                    else:
                        ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                    yield OptionTrade(
                        ts=ts,
                        ticker=underlying,
                        expiry=expiry,
                        strike=strike,
                        right=right,
                        price=row.get("price") or row.get("p"),
                        bid=row.get("bid") or row.get("bp"),
                        ask=row.get("ask") or row.get("ap"),
                        size=row.get("size") or row.get("s") or row.get("quantity"),
                        exchange=row.get("exchange") or row.get("x"),
                        trade_id=str(row.get("id") or row.get("trade_id") or ""),
                        source="optiondata_raw",
                        raw={**row, "_data_status": "raw_service_records_not_completeness_guaranteed"},
                    )
        finally:
            ws.close()
