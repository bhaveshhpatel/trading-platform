from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
from typing import Any, Iterable

@dataclass(slots=True)
class OptionTrade:
    ts: datetime
    ticker: str
    expiry: str | None
    strike: float | None
    right: str | None
    price: float | None
    bid: float | None
    ask: float | None
    size: int | None
    oi: int | None = None
    volume: int | None = None
    underlying: float | None = None
    iv: float | None = None
    delta: float | None = None
    gamma: float | None = None
    exchange: str | None = None
    trade_id: str | None = None
    source: str = "unknown"
    raw: dict[str, Any] | None = None

    @property
    def premium(self):
        return float(self.price or 0) * int(self.size or 0) * 100.0

    @property
    def quote_side(self):
        if self.price is None: return "unknown"
        if self.ask is not None and self.price >= self.ask: return "ask"
        if self.bid is not None and self.price <= self.bid: return "bid"
        if self.bid is not None and self.ask is not None and self.bid <= self.price <= self.ask: return "mid"
        return "unknown"

    @property
    def dte(self):
        if not self.expiry: return None
        try: return (datetime.fromisoformat(self.expiry).date() - self.ts.date()).days
        except ValueError: return None

def tags(t: OptionTrade, premium_min=25000, size_min=150):
    out=set()
    if t.premium >= premium_min: out.add("large_premium")
    if (t.size or 0) >= size_min: out.add("large_size")
    if t.quote_side in ("ask","bid"): out.add("quote_" + t.quote_side)
    if t.oi and t.size and t.size > t.oi: out.add("size_gt_open_interest")
    if t.dte is not None and t.dte <= 7: out.add("near_expiry")
    raw=t.raw or {}
    if raw.get("is_sweep") is True or raw.get("sweep") is True: out.add("provider_sweep")
    return out

def repeated_activity(trades: Iterable[OptionTrade], window_seconds=180, min_trades=3):
    groups=defaultdict(list)
    for t in sorted(trades,key=lambda x:x.ts):
        key=(t.ticker,t.expiry,t.strike,t.right)
        bucket=groups[key]
        if not bucket or (t.ts-bucket[-1].ts).total_seconds() <= window_seconds: bucket.append(t)
        else: groups[key]=[t]
    events=[]
    for key,b in groups.items():
        if len(b)>=min_trades:
            events.append({"type":"repeat_activity","ticker":b[0].ticker,"expiry":b[0].expiry,"strike":b[0].strike,"right":b[0].right,"start":b[0].ts.isoformat(),"end":b[-1].ts.isoformat(),"trade_count":len(b),"total_premium":round(sum(x.premium for x in b),2),"quote_sides":sorted({x.quote_side for x in b}),"research_only":True})
    return events

def summarize(trades):
    rows=list(trades); counts=Counter()
    for t in rows: counts.update(tags(t))
    return {"research_only":True,"trade_count":len(rows),"tickers":sorted({t.ticker for t in rows}),"total_premium":round(sum(t.premium for t in rows),2),"tag_counts":dict(counts),"repeat_events":repeated_activity(rows)}

def parse_trade(row, source="jsonl"):
    rawts=row.get("ts",row.get("timestamp"))
    if isinstance(rawts,(int,float)): ts=datetime.fromtimestamp(rawts,tz=timezone.utc)
    else: ts=datetime.fromisoformat(str(rawts).replace("Z","+00:00"))
    return OptionTrade(ts=ts,ticker=str(row.get("ticker",row.get("symbol",""))).upper(),expiry=row.get("expiry",row.get("expiration")),strike=row.get("strike",row.get("strike_price")),right=row.get("right",row.get("option_type")),price=row.get("price",row.get("spot",row.get("execution_price"))),bid=row.get("bid"),ask=row.get("ask"),size=row.get("size",row.get("contracts")),oi=row.get("oi",row.get("open_interest")),volume=row.get("volume"),underlying=row.get("underlying",row.get("underlying_price",row.get("stock_price"))),iv=row.get("iv"),delta=row.get("delta"),gamma=row.get("gamma"),exchange=row.get("exchange"),trade_id=row.get("trade_id",row.get("id")),source=source,raw=row)

def forward_study(event_trades, underlying_points, horizons=(300,1800,3600)):
    prices=sorted(underlying_points,key=lambda x:x[0]); out=[]
    for t in event_trades:
        if t.underlying is None: continue
        for h in horizons:
            future=[p for ts,p in prices if t.ts <= ts <= t.ts+timedelta(seconds=h)]
            if not future or t.underlying == 0: continue
            ch=[(float(p)/float(t.underlying)-1)*100 for p in future]
            out.append({"ticker":t.ticker,"event_time":t.ts.isoformat(),"horizon_seconds":h,"return_pct":round(ch[-1],6),"max_favorable_pct":round(max(ch),6),"max_adverse_pct":round(min(ch),6)})
    return out
