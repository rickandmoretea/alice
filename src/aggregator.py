from typing import Dict, Any
from binance import BinanceClient
from bybit import BybitClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AggregatorClient:
    def __init__(self, exchanges=None):
        """
        exchanges: List of instantiated exchange clients
        """
        self.exchanges = exchanges or [BinanceClient(), BybitClient()]

    def get_best_price(self, symbol="BTCUSDT", side="buy") -> Dict[str, Any]:
        """
        Get the best price for a given symbol and side (buy/sell)
        """
        if side.lower() not in ["buy", "sell"]:
            raise ValueError("Side should be either 'buy' or 'sell'")

        best_exchange = None
        best_price = None

        for exchange in self.exchanges:
            try:
                price = exchange.get_price(symbol)
                logger.info(f"Price from {exchange.__class__.__name__}: {price}")
                # When it's 'buy' the best price is the lowest price
                if best_price is None or (side.lower() == "buy" and price < best_price):
                    best_price = price
                    best_exchange = exchange
                elif side.lower() == "sell" and price > best_price:
                    best_price = price
                    best_exchange = exchange
            except Exception as e:
                logger.error(
                    f"Error getting price from {exchange.__class__.__name__}: {e}"
                )
        if not best_exchange or best_price is None:
            raise ValueError("No suitable exchange found or price is unavailable")

        return {
            "exchange": best_exchange,
            "price": best_price,
        }

    def place_order(self, side, quantity, symbol="BTCUSDT"):
        """
        Automatically picks the best exchange to
        place the order based on the best quote.
        """
        best_info = self.get_best_price(symbol, side)
        best_exchange = best_info["exchange"]
        best_price = best_info["price"]

        if not best_exchange or best_price is None:
            raise ValueError("Unable to find the best exchange or price is None")

        logger.info(
            f"Placing order on {best_exchange.__class__.__name__} "
            f"for {quantity} {symbol} at {best_price}"
        )

        return best_exchange.place_order(side, quantity, symbol)
