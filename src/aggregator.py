from typing import Dict, Any
from binance import BinanceClient
from bybit import BybitClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AggregatorClient:
    def __init__(self, exchanges=None):
        self.exchanges = exchanges or [BinanceClient(), BybitClient()]
        self.best_info = None  # Cache the best price info

    def get_best_price(self, symbol="BTCUSDT", side="buy") -> Dict[str, Any]:
        """
        Get the best price for a given symbol and side (buy/sell).
        """
        if side.lower() not in ["buy", "sell"]:
            raise ValueError("Side should be either 'buy' or 'sell'")

        best_exchange = None
        best_price = None
        log_details = []

        for exchange in self.exchanges:
            try:
                price = exchange.get_price(symbol)
                log_details.append(f"{exchange.__class__.__name__}: {price}")
                # Determine the best price
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

        # Cache the best info to avoid redundant calls
        self.best_info = {
            "exchange": best_exchange,
            "price": best_price,
        }

        # High-level log
        logger.info(f"[BEST PRICE] {symbol} {side.upper()} -> {best_price} from {best_exchange.__class__.__name__}")

        # Debug log
        logger.debug(f"[PRICE DETAILS] {log_details}")

        return self.best_info

    def place_order(self, side, quantity, symbol="BTCUSDT"):
        """
        Place the order using the best price information.
        """
        # Reuse cached best_info to avoid redundant price fetches
        if not self.best_info:
            self.best_info = self.get_best_price(symbol, side)

        best_exchange = self.best_info["exchange"]
        best_price = self.best_info["price"]

        if not best_exchange or best_price is None:
            raise ValueError("Unable to find the best exchange or price is None")

        logger.info(
            f"Placing order on {best_exchange.__class__.__name__} "
            f"for {quantity} {symbol} at {best_price}"
        )

        return best_exchange.place_order(side, quantity, symbol)
