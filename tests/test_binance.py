import pytest

from src.binance import BinanceClient


@pytest.mark.parametrize("symbol", ["BTCUSDT"])
def test_binance_get_price(symbol):
    client = BinanceClient()
    price = client.get_price(symbol)
    assert price > 0, "Price should be greater than 0"

@pytest.mark.skip(reason="Skipping order placement test in CI") #remove this line to run the test
def test_binance_place_order():
    client = BinanceClient()
    response = client.place_order("BUY", 100, "BTCUSDT")
    assert "orderId" in response, "Order ID should be present in response"
