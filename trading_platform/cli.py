import os
import argparse
import json
from .core import parse_trade, tags, summarize
from .uw import UnusualWhales
from .alpaca import AlpacaIndicative
from .optiondata import OptionDataRaw
from .store import Store


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("import-jsonl")
    a.add_argument("path")
    a.add_argument("--db", default="data/research.sqlite")
    l = s.add_parser("live")
    l.add_argument("--db", default="data/research.sqlite")
    l.add_argument("--symbols", default=os.getenv("OPTIONDATA_SYMBOLS", ""))

    args = p.parse_args()
    db = getattr(args, "db", "data/research.sqlite")
    store = Store(db)

    if args.cmd == "import-jsonl":
        trades = []
        with open(args.path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    trades.append(parse_trade(json.loads(line)))
        store.add_many(trades)
        result = summarize(trades)
        for e in result["repeat_events"]:
            store.add_event(e)
            print(json.dumps(e))
        print(json.dumps({k: v for k, v in result.items() if k != "repeat_events"}, indent=2))
        return

    provider = os.getenv("OPTIONS_FLOW_PROVIDER", "alpaca").lower()
    symbols = [x.strip() for x in args.symbols.split(",") if x.strip()]

    if provider == "alpaca":
        stream = AlpacaIndicative().stream()
    elif provider == "optiondata":
        stream = OptionDataRaw().stream(symbols=symbols or None)
    elif provider == "unusual_whales":
        stream = UnusualWhales().stream()
    else:
        raise ValueError(
            "OPTIONS_FLOW_PROVIDER must be alpaca, optiondata, or unusual_whales"
        )

    for t in stream:
        store.add(t)
        tt = sorted(tags(t))
        print(
            json.dumps(
                {
                    "research_only": True,
                    "event": "tape_observation",
                    "ticker": t.ticker,
                    "ts": t.ts.isoformat(),
                    "source": t.source,
                    "data_status": (t.raw or {}).get("_data_status", "provider_normalized"),
                    "premium": t.premium,
                    "quote_side": t.quote_side,
                    "tags": tt,
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
