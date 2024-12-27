import pytest

from src.bybit import BybitClient


@pytest.mark.parametrize("symbol", ["BTCUSDT"])
def test_bybit_get_price(symbol):
    client = BybitClient()
    price = client.get_price(symbol)
    assert price > 0, "Price should be greater than 0"

@pytest.mark.skip(reason="Skipping order placement test in CI") #remove this line to run the test
def test_bybit_place_order():
    client = BybitClient()
    response = client.place_order("Buy", "10", "BTCUSDT")
    assert response.get("retCode") == 0, f"Unexpected retCode in Bybit response: {response}"
    print("Bybit order placed successfully:", response)