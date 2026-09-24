import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlencode
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
        params = {
            "token": self.token,
            "aggregation_mode": "RAW",
        }
        if symbols:
            params["symbols"] = ",".join(symbols)
        ws_url = f"{self.url}?{urlencode(params)}"
        ws = websocket.create_connection(ws_url, timeout=20)
        try:
            while True:
                raw = ws.recv()
                if raw is None:
                    break
                row = json.loads(raw)
                if not isinstance(row, dict):
                    continue
                if row.get("status"):
                    if row.get("status") == "ERROR":
                        raise RuntimeError(row.get("msg", "OptionData error"))
                    continue

                option_symbol = str(row.get("option_symbol") or "").upper()
                underlying, expiry, right, strike = self._contract(option_symbol)
                if not underlying:
                    # Keep a defensive fallback for any alternate payload.
                    underlying = str(row.get("symbol") or "").upper()
                    expiry = row.get("expiration_date")
                    right = "C" if str(row.get("put_call", "")).upper() == "CALL" else "P"
                    strike = row.get("strike")
                if not underlying or not expiry:
                    continue

                ts_raw = row.get("updated_timestamp")
                if ts_raw is not None:
                    ts = datetime.fromtimestamp(float(ts_raw) / 1000, tz=timezone.utc)
                else:
                    ts = datetime.fromisoformat(
                        str(row.get("time")).replace(" ", "T")
                    ).replace(tzinfo=timezone.utc)

                yield OptionTrade(
                    ts=ts,
                    ticker=underlying,
                    expiry=expiry,
                    strike=float(strike) if strike is not None else None,
                    right=right,
                    price=row.get("price"),
                    bid=row.get("bid"),
                    ask=row.get("ask"),
                    size=row.get("size"),
                    oi=row.get("oi"),
                    underlying=row.get("underlying_price"),
                    iv=row.get("iv"),
                    delta=row.get("delta"),
                    gamma=row.get("gamma"),
                    trade_id=str(row.get("id") or ""),
                    source="optiondata_raw",
                    raw={
                        **row,
                        "_data_status": "raw_service_records_not_completeness_guaranteed",
                    },
                )
        finally:
            ws.close()
