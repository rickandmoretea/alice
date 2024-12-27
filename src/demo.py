from src.aggregator import AggregatorClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def place_order_best_price():
    client = AggregatorClient()

    # Fetch the best price
    try:
        best_info = client.get_best_price(symbol="BTCUSDT", side="buy")
        best_exchange = best_info["exchange"]
        best_price = best_info["price"]
        logger.info(f"Best price is {best_price} on {best_exchange.__class__.__name__}")

        # Place order note: if `buy` quantity should be USDT to spend, if `sell` quantity should be BTC to sell
        response = client.place_order("buy", "15", "BTCUSDT")
        logger.info(f"Order placed: {response}")
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        return


if __name__ == "__main__":
    place_order_best_price()
