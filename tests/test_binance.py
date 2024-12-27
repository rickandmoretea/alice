import pytest

from src.binance import BinanceClient


@pytest.mark.integration
def test_binance_get_price():
    client = BinanceClient()
    price = client.get_price("BTCUSDT")
    assert price > 0, "Price should be greater than 0"


@pytest.mark.integration
def test_binance_place_order():
    client = BinanceClient()
    response = client.place_order("BUY", 0.01, "BTCUSDT")
    assert "orderId" in response, "Order ID should be present in response"
