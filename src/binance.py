import os
from src.utils.api_client import APIClient
from src.utils.error_handler import APIError
from dotenv import load_dotenv
load_dotenv()
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BinanceClient:
    def __init__(self):
        self.base_url = "https://testnet.binance.vision/api"

        self.public_client = APIClient(
            base_url=self.base_url,
            api_key="",
            secret_key="",
            use_signature=False,
            exchange="binance",
        )

        self.signed_client = APIClient(
            base_url=self.base_url,
            api_key=os.getenv("BINANCE_TESTNET_API_KEY"),
            secret_key=os.getenv("BINANCE_TESTNET_SECRET_KEY"),
            use_signature=True,
            exchange="binance",
        )

    def get_price(self, symbol="BTCUSDT"):
        endpoint = "/v3/ticker/price"  # As of 28 Dec, 2024
        params = {"symbol": symbol}
        response = self.public_client.get(endpoint, params=params)
        logger.info(f"[GET] {endpoint}, params={params}, response={response}")
        return float(response["price"])

    def place_order(self, side, quantity, symbol="BTCUSDT"):
        endpoint = "/v3/order"
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity,
        }

        response = self.signed_client.post(endpoint, data=data)

        if "code" in response and response["code"] != 200:
            raise APIError(f"Binance error: {response}")
        logger.info(f"Placing Binance order: side={side}, qty={quantity}, symbol={symbol}")
        return response
