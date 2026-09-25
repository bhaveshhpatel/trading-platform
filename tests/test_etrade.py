from app.providers.etrade import ETradeClient, ETradeCredentials


def test_etrade_surface_is_read_only():
    methods = {name for name in dir(ETradeClient) if not name.startswith("_")}
    assert {"quote", "option_chain", "option_expirations"} <= methods
    assert not any("order" in name.lower() for name in methods)


def test_oauth_header_contains_required_fields():
    client = ETradeClient(
        ETradeCredentials("consumer", "secret", "token", "token-secret")
    )
    header = client._authorization_header(
        "GET", "https://api.etrade.com/v1/market/quote/AAPL", {}
    )
    assert header.startswith("OAuth ")
    assert "oauth_consumer_key=" in header
    assert "oauth_token=" in header
    assert "oauth_signature_method=" in header
    assert "oauth_signature=" in header
