import json, os, requests, websocket
from datetime import datetime, timezone
from .core import parse_trade

class UnusualWhales:
    def __init__(self, api_key=None, rest_url="https://api.unusualwhales.com/api/option-trades/flow-alerts", ws_url="wss://api.unusualwhales.com/socket"):
        self.api_key=api_key or os.getenv("UW_API_KEY")
        self.rest_url=rest_url; self.ws_url=ws_url
        if not self.api_key: raise ValueError("UW_API_KEY is required")
    def headers(self): return {"Authorization":"Bearer " + self.api_key,"Accept":"application/json"}
    def fetch(self, params=None):
        r=requests.get(self.rest_url,headers=self.headers(),params=params or {},timeout=20); r.raise_for_status(); p=r.json()
        rows=p if isinstance(p,list) else p.get("data",p.get("results",p.get("flow",[])))
        return [parse_trade(x,"unusual_whales") for x in rows if isinstance(x,dict)]
    def stream(self):
        configured=os.getenv("UW_WS_SUBSCRIPTION_JSON")
        msg=json.loads(configured) if configured else {"subscribe":"option_trades"}
        ws=websocket.create_connection(self.ws_url,header=["Authorization: Bearer " + self.api_key],timeout=20)
        try:
            ws.send(json.dumps(msg))
            while True:
                payload=ws.recv()
                if payload is None: break
                data=json.loads(payload)
                rows=data if isinstance(data,list) else data.get("data",data.get("trades",data.get("events",[data])))
                if isinstance(rows,dict): rows=[rows]
                for row in rows:
                    if isinstance(row,dict):
                        try: yield parse_trade(row,"unusual_whales")
                        except (TypeError,ValueError): pass
        finally: ws.close()
