# trading-platform

Research-only options tape ingestion and analysis platform.

## Real-time tape source

The integrated provider is the official Unusual Whales API. Its current documentation describes real-time options flow covering options trades across U.S. exchanges and documents a WebSocket endpoint for live option-trade streaming. The provider currently lists real-time API access as paid; its free website tier is delayed, so this repository does not pretend that a free feed is real-time.

Configure `UW_API_KEY` at runtime. Do not commit credentials.

```bash
export UW_API_KEY="..."
python -m trading_platform.cli live
```

The WebSocket subscription message defaults to:

```json
{"subscribe":"option_trades"}
```

If the provider account documentation specifies a different subscription payload, set `UW_WS_SUBSCRIPTION_JSON` instead.

## What the platform measures

- raw option-trade observations
- premium = price x contracts x 100
- NBBO-relative quote location
- contract size versus open interest
- near-expiration observations
- provider-supplied sweep flags when present
- repeated activity on the same contract inside a configurable time window
- forward-return, maximum-favorable and maximum-adverse movement for historical research
- SQLite persistence of normalized data plus original provider payloads

The feature layer is intentionally transparent and configurable. It does not claim to reproduce any private proprietary algorithm.

## Wall St. Je$us / Steamroom research mapping

Public Steamroom material describes products including Wiseguy Alerts, Net Sweeper Flow, GEX-Ray and a Wall St. Je$us feed. The public material does not disclose the complete proprietary detection logic. This project therefore maps only observable characteristics that can be measured from tape data rather than asserting that it has recreated their private system.

Examples of research tags include:

- large premium
- large size
- ask/bid quote location
- size greater than open interest
- near expiration
- provider sweep flag
- repeated same-contract activity

These are descriptive research observations, not trading recommendations.

## Historical import

JSONL input:

```json
{"ts":"2026-01-02T14:30:00Z","ticker":"ABC","expiry":"2026-01-16","strike":100,"right":"call","price":2.50,"bid":2.45,"ask":2.50,"size":200,"oi":1000,"volume":3000}
```

Run:

```bash
python -m trading_platform.cli import-jsonl sample.jsonl
```

## Tests

```bash
pip install -r requirements.txt
python -m pytest -q
```

## Scope

This repository is a non-executing research system. It has no broker integration, order placement, position management, or automated execution.
