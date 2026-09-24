from trading_platform.optiondata import OptionDataRaw


def test_optiondata_occ_contract():
    assert OptionDataRaw._contract("AAPL240315C00172500") == (
        "AAPL", "2024-03-15", "C", 172.5
    )
