import os, re, msgpack, websocket
from datetime import datetime, timezone
from .core import OptionTrade

OCC_RE=re.compile(r"^(.+?)(\d{6})([CP])(\d{8})$")

class AlpacaIndicative:
    """Free Alpaca Basic options stream adapter.

    Alpaca documents the Basic plan's options feed as an indicative feed.
    It is real-time over WebSocket, but is not the full OPRA tape.
    """
    def __init__(self,key=None,secret=None,feed=None):
        self.key=key or os.getenv("ALPACA_API_KEY_ID")
        self.secret=secret or os.getenv("ALPACA_API_SECRET_KEY")
        self.feed=feed or os.getenv("ALPACA_OPTIONS_FEED","indicative")
        if not self.key or not self.secret: raise ValueError("ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY are required")
        if self.feed not in {"indicative","opra"}: raise ValueError("ALPACA_OPTIONS_FEED must be indicative or opra")
        self.url=f"wss://stream.data.alpaca.markets/v1beta1/{self.feed}"

    @staticmethod
    def _contract(symbol):
        m=OCC_RE.match(symbol)
        if not m: return None, None, None, None
        root,ymd,right,strike=m.groups()
        expiry=datetime.strptime(ymd,"%y%m%d").date().isoformat()
        return root,expiry,right,int(strike)/1000

    def stream(self, symbols=("*",)):
        ws=websocket.create_connection(self.url,timeout=20)
        try:
            ws.send(msgpack.packb({"action":"auth","key":self.key,"secret":self.secret},use_bin_type=True))
            auth=msgpack.unpackb(ws.recv(),raw=False)
            if auth.get("T")!="success": raise RuntimeError(f"Alpaca authentication failed: {auth}")
            sub={"action":"subscribe","trades":list(symbols),"quotes":list(symbols)}
            ws.send(msgpack.packb(sub,use_bin_type=True))
            while True:
                payload=ws.recv()
                if payload is None: break
                messages=msgpack.unpackb(payload,raw=False)
                if isinstance(messages,dict): messages=[messages]
                for row in messages:
                    if not isinstance(row,dict): continue
                    typ=row.get("T")
                    if typ not in {"t","q"}: continue
                    symbol=row.get("S") or ""
                    underlying,expiry,right,strike=self._contract(symbol)
                    if not underlying: continue
                    if typ=="t":
                        ts=datetime.fromisoformat(str(row["t"]).replace("Z","+00:00"))
                        yield OptionTrade(ts=ts,ticker=underlying,expiry=expiry,strike=strike,right=right,price=row.get("p"),bid=None,ask=None,size=row.get("s"),exchange=row.get("x"),trade_id=str(row.get("i","")),source="alpaca_indicative",raw=row)
                    else:
                        # Quote events are retained as observations; they are not option trades.
                        continue
        finally:
            ws.close()
