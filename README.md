# trading-platform

Research-only options tape ingestion and analysis platform.

## Configurable options-flow providers

The runtime provider is selected with `OPTIONS_FLOW_PROVIDER`.

### Free path: Alpaca indicative options stream

Set:

```bash
export OPTIONS_FLOW_PROVIDER=alpaca
export ALPACA_API_KEY_ID="..."
export ALPACA_API_SECRET_KEY="..."
export ALPACA_OPTIONS_FEED=indicative
python -m trading_platform.cli live
```

Alpaca's current Basic market-data plan is $0 and provides an **indicative options feed** over WebSocket. Alpaca's documentation explicitly distinguishes this from its paid OPRA feed: the indicative feed is a derivative of OPRA rather than the full consolidated OPRA tape. Therefore this is a genuinely free real-time streaming path, but it must not be treated as equivalent to a full OPRA tape. The adapter uses Alpaca's documented MsgPack options WebSocket format and normalizes option trade messages.

You can restrict the subscription to contracts with:

```bash
export ALPACA_OPTION_SYMBOLS="AAPL240315C00172500,SPY240315P00450000"
```

If omitted, the adapter uses the configured default subscription value; if your Alpaca account/API version rejects a wildcard, set explicit contract symbols.

### Unusual Whales path

Keep the richer Unusual Whales provider by switching:

```bash
export OPTIONS_FLOW_PROVIDER=unusual_whales
export UW_API_KEY="..."
python -m trading_platform.cli live
```

Unusual Whales currently documents real-time options flow and a WebSocket option-trade stream, but its real-time API is a paid service. The free website tier is delayed.

## Normalized research features

- option trade timestamp and contract
- premium = price x contracts x 100
- NBBO-relative quote location when bid/ask are available
- contract size versus open interest
- near-expiration observations
- provider-supplied sweep flags when present
- repeated activity on the same contract
- historical forward-return, maximum-favorable and maximum-adverse movement

The platform deliberately keeps provider payloads and uses transparent, measurable features. It does not claim to recreate any private proprietary algorithm.

## Wall St. Je$us / Steamroom mapping

Public Steamroom material describes tools including Wiseguy Alerts, Net Sweeper Flow, GEX-Ray and a Wall St. Je$us feed. The complete proprietary detection logic is not publicly disclosed. This project therefore implements observable tape characteristics rather than claiming to reproduce private logic.

## Historical import

```bash
python -m trading_platform.cli import-jsonl sample.jsonl
```

## Tests

```bash
pip install -r requirements.txt
python -m pytest -q
```

## Scope

This is a non-executing research system. It has no broker integration, order placement, position management, or automated execution.
