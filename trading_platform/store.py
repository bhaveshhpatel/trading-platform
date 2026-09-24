import json,sqlite3
from pathlib import Path

class Store:
    def __init__(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path)
        self.db.executescript("CREATE TABLE IF NOT EXISTS option_trades (trade_id TEXT PRIMARY KEY, ts TEXT, ticker TEXT, expiry TEXT, strike REAL, right TEXT, price REAL, bid REAL, ask REAL, size INTEGER, oi INTEGER, volume INTEGER, underlying REAL, iv REAL, delta REAL, gamma REAL, exchange TEXT, source TEXT, raw_json TEXT); CREATE TABLE IF NOT EXISTS research_events (id INTEGER PRIMARY KEY, ts TEXT, event_type TEXT, ticker TEXT, payload_json TEXT)")
    def add(self,t):
        tid=t.trade_id or (t.source+":"+t.ts.isoformat()+":"+t.ticker+":"+str(t.strike)+":"+str(t.size))
        self.db.execute("INSERT OR IGNORE INTO option_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tid,t.ts.isoformat(),t.ticker,t.expiry,t.strike,t.right,t.price,t.bid,t.ask,t.size,t.oi,t.volume,t.underlying,t.iv,t.delta,t.gamma,t.exchange,t.source,json.dumps(t.raw or {}))); self.db.commit()
    def add_many(self,items):
        for t in items:self.add(t)
    def add_event(self,e):
        self.db.execute("INSERT INTO research_events(ts,event_type,ticker,payload_json) VALUES(?,?,?,?)",(e["start"],e["type"],e["ticker"],json.dumps(e))); self.db.commit()
