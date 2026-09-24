# trading-platform

Research-only options-flow ingestion and analysis platform.

## Data-source verification

No mock, synthetic, paper-market, or sandbox source is used as a live options-flow source.

Important limitation: no permanently-free source was verified that supplies the complete raw OPRA options tape, even with a 15-minute delay.

| Source | Genuine market data? | Delay | Raw/full OPRA? | Free? | Role |
|---|---|---|---|---|---|
| Alpaca Basic Indicative | Yes, market-derived from OPRA | Trades 15m | No; indicative derivatives | Yes | Free baseline |
| OptionData.io RAW | Yes, real provider trade stream | Provider real-time | Not independently guaranteed complete OPRA | Trial/paid | Raw-record research |
| Unusual Whales | Yes, provider market-data feed | Real-time | No; normalized provider feed | No | Premium flow source |
| Tradier Sandbox | Yes, genuine delayed market data | 15m | No | Yes | Removed from live flow path |
| ThetaData Free | Yes, historical EOD | 1 day | No | Yes | Not a live flow source |
| Databento OPRA | Yes, licensed OPRA | Live / delayed historical | Yes | No; temporary new-user credits | Full-tape option |

## Alpaca

Alpaca Basic is retained because its options stream is a genuine market-data service. However, Alpaca explicitly describes the free Indicative Pricing Feed as a derivative of OPRA: quotes are not actual OPRA quotes and trades are derivatives delayed by 15 minutes.

The adapter therefore records the feed as indicative and does not call it raw tape.

## OptionData RAW

OptionData documents a real-time options trade WebSocket with RAW mode. RAW preserves individual option trade records instead of applying the provider's simultaneous-trade aggregation. This is useful for flow research, but the platform does not claim that the service is a complete OPRA audit feed.

## Why Tradier was removed

Tradier sandbox data is genuine delayed market data constructed from the same consolidated feed, so it is not mock data. However, Tradier does not provide delayed paper streaming, and the sandbox is a snapshot/paper environment. It therefore does not belong in the live options-flow ingestion layer.

## Why ThetaData Free is not integrated

The free ThetaData tier provides historical EOD U.S. stock/options data. Its delayed intraday and trade-stream capabilities require paid tiers, so it does not solve the free live/delayed raw-flow requirement.

## Full OPRA

Databento's OPRA.PILLAR dataset is a genuine consolidated U.S. equity-options dataset covering last sales and national BBO across U.S. options venues. It is licensed/paid; temporary new-user credits do not make it a permanently-free source.

## Configuration

Free baseline:

    OPTIONS_FLOW_PROVIDER=alpaca
    ALPACA_OPTIONS_FEED=indicative
    ALPACA_API_KEY_ID=...
    ALPACA_API_SECRET_KEY=...
    ALPACA_OPTION_SYMBOLS=...

Raw-record provider:

    OPTIONS_FLOW_PROVIDER=optiondata
    OPTIONDATA_API_KEY=...

Premium provider:

    OPTIONS_FLOW_PROVIDER=unusual_whales
    UW_API_KEY=...

## Data-integrity rules

Every normalized observation retains provider and data-status metadata. Delayed/indicative observations must not be silently mixed with raw OPRA observations in research or backtests.

The platform is research-only and non-executing.