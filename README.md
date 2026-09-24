# trading-platform

Research-only options tape ingestion and analysis platform.

## Data-source reality

There is no verified permanently-free source that provides the complete, raw, real-time U.S. options OPRA tape. OPRA is the consolidated options market-data processor; current OPRA redistribution is governed by licensing and vendor/subscriber arrangements.

The project therefore distinguishes full/raw, indicative/derived, delayed, and trial sources instead of presenting them as equivalent.

| Source | Cost status | Integration | Full raw OPRA? |
|---|---|---|---|
| Alpaca Basic | Free | WebSocket indicative trades/quotes for explicit contracts | No; derivative feed, trades delayed 15m |
| Tradier Sandbox | Free account access | Delayed option quote snapshots | No; delayed snapshots, not raw tape |
| ThetaData Free | Free | EOD options history | No; EOD only |
| OptionData.io | Trial, then paid | RAW service-record trade stream | No completeness guarantee |
| Unusual Whales | Paid | Provider-normalized real-time flow | No; not a raw OPRA feed |
| OPRA | Licensed | Through entitled vendors | Yes; consolidated last-sale/quote information |

## Alpaca free path

Set OPTIONS_FLOW_PROVIDER=alpaca and use explicit OCC option symbols in ALPACA_OPTION_SYMBOLS. The adapter now caches the most recent quote for each subscribed contract and attaches it to subsequent trade observations, so quote-side classification can work when the feed supplies both events.

The source is deliberately marked as alpaca_indicative with data status indicative_derivative_delayed_15m.

## OptionData RAW path

Set OPTIONS_FLOW_PROVIDER=optiondata and OPTIONDATA_API_KEY. The adapter requests RAW mode rather than aggregated mode. RAW means one service record per received print, but the provider explicitly says it is not an OPRA-native audit feed and does not guarantee a complete/lossless session. Its access is trial/paid rather than permanently free.

## Tradier delayed supplement

The Tradier adapter can retrieve delayed sandbox option snapshots. It is intentionally not part of the live raw-tape path because Tradier documents sandbox options as 15-minute delayed and does not offer delayed paper streaming.

## Unusual Whales

Keep the richer Unusual Whales provider by setting OPTIONS_FLOW_PROVIDER=unusual_whales and UW_API_KEY.

## Normalized research features

- option trade timestamp and contract
- premium = price x contracts x 100
- NBBO-relative quote location when bid/ask are available
- contract size versus open interest
- near-expiration observations
- provider-supplied sweep flags when present
- repeated activity on the same contract
- historical forward-return, maximum-favorable and maximum-adverse movement
- explicit source/data-status metadata so delayed or derived observations are never silently mixed with other feeds

The platform does not claim to reproduce any private proprietary alert algorithm.

## Tests

    pip install -r requirements.txt
    python -m pytest -q

## Scope

This is a non-executing research system. It has no broker integration, order placement, position management, or automated execution.