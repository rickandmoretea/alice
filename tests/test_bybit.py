from src.bybit import BybitClient


def test_bybit_get_price():
    client = BybitClient()
    price = client.get_price("BTCUSDT")
    assert price > 0, "Price should be greater than 0"


def test_bybit_place_order():
    client = BybitClient()
    response = client.place_order("buy", 0.001, "BTCUSDT")
    assert (
        response.get("retCode") == 0
    ), f"Unexpected retCode in Bybit response: {response}"
    assert "result" in response, "Response missing 'result'"
    print("Bybit order placed successfully:", response)
