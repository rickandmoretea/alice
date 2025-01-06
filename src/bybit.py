import os

from src.utils.api_client import APIClient
from src.utils.error_handler import APIError
from dotenv import load_dotenv
from src.utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()


class BybitClient:
    def __init__(self, testnet=True):
        testnet = os.getenv("TESTNET", "true").lower() == "true"
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"

        self.public_client = APIClient(
            base_url=self.base_url,
            api_key=os.getenv("BYBIT_TESTNET_API_KEY"),
            secret_key=os.getenv("BYBIT_TESTNET_SECRET_KEY"),
            use_signature=False,
            exchange="bybit",
        )

        self.signed_client = APIClient(
            base_url=self.base_url,
            api_key=os.getenv("BYBIT_TESTNET_API_KEY"),
            secret_key=os.getenv("BYBIT_TESTNET_SECRET_KEY"),
            use_signature=True,
            exchange="bybit",
        )

    def get_price(self, symbol="BTCUSDT"):
        endpoint = "/v5/market/tickers"
        params = {"category": "spot", "symbol": symbol}
        response = self.public_client.get(endpoint, params=params)
        if response.get("retCode") != 0:
            raise APIError(f"Bybit public API error: {response}")

        data_lst = response["result"].get("list", [])  # get the price
        if not data_lst:
            raise APIError(f"No ticker data returned. Full response: {response}")

        last_price_str = data_lst[0].get("lastPrice")
        # High-level log
        logger.info(f"[BYBIT PRICE] {symbol} -> {last_price_str}")
        # Detailed log (DEBUG level)
        logger.debug(f"[GET] {endpoint}, params={params}, response={response}")

        return float(last_price_str)

    def place_order(self, side, quantity, symbol="BTCUSDT"):
        endpoint = "/v5/order/create"
        data = {
            "category": "spot",
            "symbol": symbol,
            "side": "Buy" if side.lower() == "buy" else "Sell",
            "orderType": "Market",
            "qty": str(quantity),
        }

        response = self.signed_client.post(endpoint, data=data)

        if response.get("retCode") != 0:
            raise APIError(f"Bybit private API error: {response}")

        # High-level log
        logger.info(f"[BYBIT ORDER] {side.upper()} {quantity} {symbol}")
        # Detailed log (DEBUG level)
        logger.debug(
            f"[POST] {endpoint}, data={data}, response={response}"
        )
        return response


