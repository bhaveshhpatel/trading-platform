"""Market-data capability registry.

The registry distinguishes authoritative transaction data from quote/chain
data so the alert engine cannot silently treat a quote snapshot as a trade.

A free current-session authoritative options trade tape remains unverified.
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
    "etrade_market_api": ProviderCapability(
        name="E*TRADE Market API",
        authoritative_trades=False,
        current_session=True,
        delayed=False,
        free=True,
        notes=(
            "Documented API provides quotes and option chains including bid/ask, "
            "sizes, volume, open interest, timestamps and Greeks. It does not "
            "document a raw options Trade Tape endpoint. Production access "
            "requires E*TRADE API and market-data agreements."
        ),
    ),
}


def authoritative_free_current_day_trade_feed_available() -> bool:
    """Return the verified capability, rather than guessing."""
    return False
