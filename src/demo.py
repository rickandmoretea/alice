from src.aggregator import AggregatorClient
from src.binance import BinanceClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def place_order_best_price(symbol="BTCUSDT", side="buy", quantity="0.5"):
    client = AggregatorClient()

    # Fetch the best price
    try:
        best_info = client.get_best_price(symbol=symbol, side=side)
        best_exchange = best_info["exchange"]
        best_price = best_info["price"]
        logger.info(f"Best price is {best_price} on {best_exchange.__class__.__name__}")

        # Place order note: if `buy` quantity should be USDT to spend,
        # if `sell` quantity should be BTC to sell
        response = client.place_order(side, quantity, symbol)
        logger.info(f"Order placed: {response}")
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        return


def get_balance():
    client = BinanceClient()
    balance = client.get_balance()
    logger.info(f"Balance: {balance}")
    return balance


if __name__ == "__main__":
    place_order_best_price()
