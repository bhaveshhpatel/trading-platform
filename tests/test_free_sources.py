from app.providers.free_sources import (
    authoritative_free_current_day_trade_feed_available,
    FREE_CAPABILITIES,
)


def test_no_free_authoritative_current_day_options_trade_feed_is_claimed():
    assert authoritative_free_current_day_trade_feed_available() is False


def test_alpaca_indicative_is_not_authoritative():
    p = FREE_CAPABILITIES["alpaca_indicative"]
    assert p.free is True
    assert p.current_session is True
    assert p.authoritative_trades is False


def test_free_aggregates_are_not_promoted_to_trade_tape():
    for name in ("strasmore_free", "massive_basic"):
        assert FREE_CAPABILITIES[name].authoritative_trades is False
