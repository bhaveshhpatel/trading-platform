import argparse,json
from .core import parse_trade,tags,summarize
from .uw import UnusualWhales
from .store import Store

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("import-jsonl"); a.add_argument("path"); a.add_argument("--db",default="data/research.sqlite")
    s.add_parser("live").add_argument("--db",default="data/research.sqlite")
    args=p.parse_args(); db=getattr(args,"db","data/research.sqlite"); store=Store(db)
    if args.cmd=="import-jsonl":
        trades=[]
        for line in open(args.path,encoding="utf-8"):
            if line.strip(): trades.append(parse_trade(json.loads(line)))
        store.add_many(trades); result=summarize(trades)
        for e in result["repeat_events"]: store.add_event(e); print(json.dumps(e))
        print(json.dumps({k:v for k,v in result.items() if k!="repeat_events"},indent=2))
    else:
        for t in UnusualWhales().stream():
            store.add(t); tt=sorted(tags(t))
            if tt: print(json.dumps({"research_only":True,"event":"tape_observation","ticker":t.ticker,"ts":t.ts.isoformat(),"premium":t.premium,"quote_side":t.quote_side,"tags":tt}),flush=True)

if __name__=="__main__": main()
