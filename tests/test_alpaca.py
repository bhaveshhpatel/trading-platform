from trading_platform.alpaca import AlpacaIndicative

def test_occ_contract():
    assert AlpacaIndicative._contract("AAPL240315C00172500")==("AAPL","2024-03-15","C",172.5)
