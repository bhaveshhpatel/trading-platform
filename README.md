# Trading Platform — Research Edition

A research-only market-data platform for studying unusual options activity and testing transparent event-detection hypotheses.

This repository intentionally does **not** place orders, recommend trades, rank securities, or emit buy/sell signals. It records market events, derives descriptive features, and measures historical outcomes without look-ahead bias.

The architecture uses publicly described concepts such as options-flow feeds, sweep detection, premium/Delta/GEX-style features, and public WallStJesus/Steamroom descriptions. Private/proprietary algorithms are not claimed to be reproduced.

## Features

- SQLite event store
- Unusual Whales REST adapter
- Normalized option-trade schema
- Descriptive sweep/flow feature extraction
- Repeat-activity clustering
- Forward-return and excursion backtesting
- JSONL import for offline datasets
- Research-event output
- GitHub Actions CI
- No order execution and no broker integration

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m trading_platform --help
```

Set `UNUSUAL_WHALES_API_KEY` only when using the provider adapter. Provider access and data licensing are separate from this repository.

