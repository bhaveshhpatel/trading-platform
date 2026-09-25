# trading-platform

Research-only, non-executing options-flow ingestion and analysis platform.

## E*TRADE integration

E*TRADE is now integrated as a read-only market-data context provider.

The documented E*TRADE Developer Platform provides market quotes and option
chains. Option-chain responses include bid/ask, bid/ask size, last price,
volume, open interest, timestamps, strike/type and Greeks when available.

The Developer Platform itself is free for developers, but production access
requires an E*TRADE API key and the applicable API/market-data agreements.

### What E*TRADE does not solve

E*TRADE's Power E*TRADE Pro UI has a real-time options Trade Tape. That UI
shows option, quantity, trade price, IV, underlying-at-trade, market-at-trade
and whether the print was at/between bid/ask.

The documented Developer API does NOT expose that Trade Tape as a raw
programmatic OPRA transaction stream. We therefore do not label E*TRADE
option-chain observations as individual trade prints.

That distinction is critical for this project because trade-side signals
require actual transaction events.

## How E*TRADE improves the platform

The new app/providers/etrade.py adapter can provide:

1. Underlying and option quote validation.
2. Option-chain snapshots.
3. Bid/ask spread and liquidity measurements.
4. Volume and open-interest context.
5. IV/Greek context when returned.
6. Expiration discovery.
7. Timestamped quote/chain snapshots for research.

The adapter deliberately contains no order-preview, order-placement, cancel,
or account-trading methods.

## Current free-data conclusion

There is still no verified completely free, programmatically accessible,
current-session authoritative options transaction feed in this architecture.

| Source | Trade prints | Current session | Free | Role |
|---|---:|---:|---:|---|
| E*TRADE Market API | No documented raw tape | Yes | Developer API is free; agreements required | Quote/chain context |
| Alpaca Basic Indicative | Derived/indicative | Yes, delayed | Yes | Non-authoritative research |
| Strasmore Free | Tick-level trades paid | No | Yes | Aggregate research |
| Massive Options Basic | Individual trades paid | No | Yes | Aggregate research |
| Licensed OPRA trade vendor | Yes | Depends on product | No | Authoritative trade input |

The alert engine therefore remains authoritative-only for claims that
require actual prints, including trade-side classification, sweeps, repeated
prints and print-level premium.

## Configuration

Set these GitHub Actions secrets/variables when E*TRADE API credentials are
available:

ETRADE_CONSUMER_KEY
ETRADE_CONSUMER_SECRET
ETRADE_ACCESS_TOKEN
ETRADE_ACCESS_TOKEN_SECRET
ETRADE_SANDBOX=false

Never commit these values to the repository.

E*TRADE uses OAuth 1.0a. Its documented lifecycle says access tokens can become
inactive after two hours without API requests and normally expire at midnight
US Eastern time, so token lifecycle management should remain separate from
the market-data adapter.

## Architecture

    MARKET DATA
         |
    +----+--------------------+
    |                         |
    | authoritative            | context feeds
    | transaction feed         | E*TRADE quotes/chains
    |                         | free aggregate sources
    +-------------+-----------+
                  |
           normalized data
                  |
           flow analytics
             /         \
          alerts     dashboard

GitHub Actions can run collection/analytics jobs and Vercel can host the
dashboard, but neither changes the licensing or fidelity of the underlying
market data.

This project remains research-only and non-executing.
