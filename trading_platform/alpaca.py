import os, re, msgpack, websocket
from datetime import datetime
from .core import OptionTrade

OCC_RE = re.compile(r"^(.+?)(\d{6})([CP])(\d{8})$")


class AlpacaIndicative:
    """Alpaca options WebSocket adapter.

    feed=indicative is the free derivative feed. feed=opra requires entitlement.
    The adapter never labels indicative data as full OPRA.
    """

    def __init__(self, key=None, secret=None, feed=None):
        self.key = key or os.getenv("ALPACA_API_KEY_ID")
        self.secret = secret or os.getenv("ALPACA_API_SECRET_KEY")
        self.feed = feed or os.getenv("ALPACA_OPTIONS_FEED", "indicative")
        if not self.key or not self.secret:
            raise ValueError("ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY are required")
        if self.feed not in {"indicative", "opra"}:
            raise ValueError("ALPACA_OPTIONS_FEED must be indicative or opra")
        self.url = f"wss://stream.data.alpaca.markets/v1beta1/{self.feed}"

    @staticmethod
    def _contract(symbol):
        m = OCC_RE.match(symbol)
        if not m:
            return None, None, None, None
        root, ymd, right, strike = m.groups()
        expiry = datetime.strptime(ymd, "%y%m%d").date().isoformat()
        return root, expiry, right, int(strike) / 1000

    @staticmethod
    def _symbols(symbols=None):
        if symbols:
            return [s.strip().upper() for s in symbols if s.strip()]
        raw = os.getenv("ALPACA_OPTION_SYMBOLS", "")
        if raw.strip():
            return [s.strip().upper() for s in raw.split(",") if s.strip()]
        raise ValueError(
            "ALPACA_OPTION_SYMBOLS must contain explicit OCC option symbols; "
            "a wildcard is intentionally not used."
        )

    def stream(self, symbols=None, include_quotes=True):
        symbols = self._symbols(symbols)
        ws = websocket.create_connection(self.url, timeout=20)
        last_quote = {}
        try:
            ws.send(msgpack.packb(
                {"action": "auth", "key": self.key, "secret": self.secret},
                use_bin_type=True,
            ))
            auth = msgpack.unpackb(ws.recv(), raw=False)
            auth_rows = auth if isinstance(auth, list) else [auth]
            if not any(r.get("T") == "success" and r.get("msg") == "authenticated" for r in auth_rows):
                raise RuntimeError(f"Alpaca authentication failed: {auth}")

            sub = {"action": "subscribe", "trades": symbols}
            if include_quotes:
                sub["quotes"] = symbols
            ws.send(msgpack.packb(sub, use_bin_type=True))

            while True:
                payload = ws.recv()
                if payload is None:
                    break
                messages = msgpack.unpackb(payload, raw=False)
                if isinstance(messages, dict):
                    messages = [messages]
                for row in messages:
                    if not isinstance(row, dict):
                        continue
                    typ = row.get("T")
                    symbol = str(row.get("S") or "").upper()
                    if typ not in {"t", "q"} or not symbol:
                        continue
                    underlying, expiry, right, strike = self._contract(symbol)
                    if not underlying:
                        continue
                    if typ == "q":
                        last_quote[symbol] = (row.get("bp"), row.get("ap"))
                        continue

                    ts = datetime.fromisoformat(str(row["t"]).replace("Z", "+00:00"))
                    bid, ask = last_quote.get(symbol, (None, None))
                    yield OptionTrade(
                        ts=ts,
                        ticker=underlying,
                        expiry=expiry,
                        strike=strike,
                        right=right,
                        price=row.get("p"),
                        bid=bid,
                        ask=ask,
                        size=row.get("s"),
                        exchange=row.get("x"),
                        trade_id=str(row.get("i", "")),
                        source=f"alpaca_{self.feed}",
                        raw={
                            **row,
                            "_data_status": (
                                "indicative_derivative_delayed_15m"
                                if self.feed == "indicative" else "opra"
                            ),
                            "_source_feed": self.feed,
                        },
                    )
        finally:
            ws.close()
