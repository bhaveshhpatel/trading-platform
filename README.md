# trading-platform

Research-only, non-executing options-flow ingestion and analysis platform.

## Free-data investigation — important conclusion

I investigated whether there is a **completely free, programmatically accessible, current-session options trade feed containing genuine reported prints** that we can safely use as the authoritative input for flow alerts.

**I could not verify one. The code therefore does not pretend that one exists.**

This distinction matters because the project needs trade-level facts for characteristics such as repeated prints, trade size/premium, and bid/ask-side classification.

### What was verified

| Source | Genuine reported option trades | Current-session | Free | Result |
|---|---:|---:|---:|---|
| Alpaca Basic Indicative | No — derived/indicative | Yes, delayed | Yes | **Not authoritative** |
| Strasmore Free | No — tick-level `options_trades` is paid | No; T+1 options | Yes | **Not sufficient** |
| Massive Options Basic | No — EOD/minute aggregates; trades paid | No | Yes | **Not sufficient** |
| Cboe free samples/summaries | No bulk free transaction-level feed | No | Samples/summaries | **Not sufficient** |
| OPRA licensed vendors | Yes | Yes or delayed | No | **Authoritative option** |

Alpaca's official documentation says its Basic options source is the Indicative Pricing Feed and that its trades are derivatives delayed by 15 minutes; quotes are also modified/indicative. Therefore the platform explicitly refuses to treat Alpaca Indicative as an authoritative flow tape. citeturn0search1turn0search3

Strasmore's current API documentation is particularly useful for verifying the boundary: its warehouse contains `options_trades` with tick-level OPRA trades, but that table is marked **paid tier**. Its free tier is one year of history and does not include tick-level trades/quotes. citeturn3search0turn3search2

Massive's current pricing similarly puts individual options trades behind paid tiers; the free Options Basic plan provides EOD/reference/minute aggregates instead. citeturn1search11

Cboe's own Option Trades product contains trade price, size, execution exchange and NBBO at trade time, but it is a subscription product; its free material consists of samples/summaries rather than a free live transaction feed. citeturn1search13turn1search0

### Why the project now has an authoritative-only guard

The signal engine should never convert an aggregate or indicative observation into a claim such as:

- "bought at the ask"
- "sold at the bid"
- "aggressive buyer"
- "sweep"
- "repeat institutional print"

unless the underlying data actually supports that conclusion.

The new `app/providers/free_sources.py` capability registry and tests make this explicit.

## Current architecture

The platform now treats data sources as separate capability classes:

```
                   DATA PROVIDERS
                         |
        +----------------+----------------+
        |                                 |
 authoritative                      non-authoritative
 trade feed                         research feeds
        |                                 |
        v                                 v
   FLOW ENGINE                     UI / experiments
        |
        v
     ALERTS
```

The free path can still be used for **historical/aggregate research**, but it is not allowed to masquerade as a raw trade tape.

## Cost implication

GitHub Actions can provide free compute for scheduled collection, and Vercel can host the dashboard, but neither changes the licensing or fidelity of the underlying market data.

GitHub can store and process data that we legitimately receive. It cannot turn a derived feed into an OPRA print.

Therefore I would **not deploy a supposedly "free raw-tape alerting" system yet**. That would give false confidence.

The correct zero-cost state is:

1. Keep the repository and GitHub Actions infrastructure.
2. Keep the non-authoritative free providers isolated.
3. Accumulate only data whose provenance is explicitly labeled.
4. Run the backtest engine on authoritative historical data when available.
5. Enable authoritative live alerts when an appropriately licensed trade feed is configured.

This is intentionally research-only and non-executing.
