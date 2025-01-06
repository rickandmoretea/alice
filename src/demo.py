from src.aggregator import AggregatorClient
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.setLevel("DEBUG")


def place_order_best_price(symbol="BTCUSDT", side="buy", quantity="0.5"):
    client = AggregatorClient()

    # Fetch the best price
    try:
        best_info = client.get_best_price(symbol=symbol, side=side)
        best_exchange = best_info["exchange"]
        best_price = best_info["price"]
        logger.info(f"[BEST PRICE] {symbol} -> {best_price} on {best_exchange.__class__.__name__}")
        # Place order note: if `buy` quantity should be USDT to spend,
        # if `sell` quantity should be BTC to sell
        response = client.place_order(side, quantity, symbol)
        logger.info(f"[ORDER SUCCESS] {response}")
    except Exception as e:
        logger.error(f"[ORDER FAILURE] {e}, {response}")
        return


def buy_sold_BTCUSDT():
    # quantity should be USDT to spend when side is `buy`
    # quantity should be BTC to sell when side is `sell`

    # Buying 500 USDT worth of BTC on Best Exchange
    place_order_best_price(symbol="BTCUSDT", side="buy", quantity="100")


if __name__ == "__main__":
    buy_sold_BTCUSDT()
