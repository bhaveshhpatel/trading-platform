"""Free-source capability registry.

This module deliberately does NOT claim a free current-day options trade tape exists.

As of 2026-09-24:
- Alpaca Basic options data is an indicative/derived feed and is not an
  authoritative trade tape.
- Strasmore's free tier does not expose its tick-level options_trades table;
  that table is paid.
- Massive's free Options Basic tier is EOD/aggregates and does not expose
  option trades.
- Cboe publishes free samples and some free summaries, but its transaction
  detail is a paid data product.

Therefore the production alert engine must never silently fall back to an
indicative or aggregate feed and label it as raw options flow.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderCapability:
    name: str
    authoritative_trades: bool
    current_session: bool
    delayed: bool
    free: bool
    notes: str


FREE_CAPABILITIES = {
    "alpaca_indicative": ProviderCapability(
        name="Alpaca Indicative",
        authoritative_trades=False,
        current_session=True,
        delayed=True,
        free=True,
        notes="Derived/indicative options feed; do not use for authoritative flow-side classification.",
    ),
    "strasmore_free": ProviderCapability(
        name="Strasmore Free",
        authoritative_trades=False,
        current_session=False,
        delayed=True,
        free=True,
        notes="Free tier has T+1 options aggregates; tick-level options_trades is paid.",
    ),
    "massive_basic": ProviderCapability(
        name="Massive Options Basic",
        authoritative_trades=False,
        current_session=False,
        delayed=True,
        free=True,
        notes="Free tier provides EOD/reference/minute aggregates; individual option trades require a paid tier.",
    ),
}


def authoritative_free_current_day_trade_feed_available() -> bool:
    """Return the verified capability, rather than guessing."""
    return False
