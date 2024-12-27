import time
from typing import Dict, Any, final
import hmac
import hashlib
import requests
import json
from urllib.parse import urlencode, quote

from src.utils.error_handler import APIError
from src.utils.logger import get_logger

logger = get_logger(__name__)

@final
class APIClient:
    __slots__ = (
        "base_url",
        "api_key",
        "secret_key",
        "use_signature",
        "exchange",
    )

    def __init__(
        self,
        base_url: str,
        api_key: str,
        secret_key: str,
        use_signature: bool = False,
        exchange: str = "binance",
    ):
        self.base_url = base_url
        self.api_key = api_key or ""
        self.secret_key = secret_key or ""
        self.use_signature = use_signature
        self.exchange = exchange.lower()

    def get(
            self, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if params is None:
            params = {}

        headers = self._get_headers()
        if self.use_signature:
            if self.exchange == "binance":
                # For Binance GET, we will append timestamp + signature
                params["timestamp"] = int(time.time() * 1000)
                query_string = self._build_query_string(params)
                signature = self._generate_signature(query_string)
                params["signature"] = signature
            elif self.exchange == "bybit":
                pass
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=headers,
            params=urlencode(params),
        )
        return self._handle_response(response)
    def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        if data is None:
            data = {}

        headers = self._get_headers()

        logger.info(
            f"[POST INIT] endpoint={endpoint}, exchange={self.exchange}, "
            f"use_signature={self.use_signature}, data_before_sign={data}, headers={headers}"
        )

        if self.use_signature:
            if self.exchange == "binance":
                # BINANCE: form-encoded body + signature appended to the data
                if "timestamp" not in data:
                    data["timestamp"] = int(time.time() * 1000)

                query_string = self._build_query_string(data)
                signature = self._generate_signature(query_string)
                data["signature"] = signature

                headers["Content-Type"] = "application/x-www-form-urlencoded"
                logger.info(
                    f"[BINANCE SIGNED] query_string={query_string}, signature={signature}"
                )

                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    data=self._build_query_string(data),
                )

            elif self.exchange == "bybit":
                # BYBIT actually requires payload as JSON string and signature over the string
                recv_window = "5000"
                timestamp = str(int(time.time() * 1000))

                # Convert to JSON string
                payload_str = json.dumps(data, separators=(",", ":"))
                param_str = timestamp + self.api_key + recv_window + payload_str

                # Generate signature
                signature = hmac.new(
                    self.secret_key.encode("utf-8"),
                    param_str.encode("utf-8"),
                    hashlib.sha256
                ).hexdigest()

                headers.update({
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "Content-Type": "application/json"
                })

                logger.info(
                    f"[BYBIT SIGNED] param_str={param_str}, signature={signature}, payload={payload_str}"
                )

                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    data=payload_str
                )
            else:
                response = requests.post(
                    f"{self.base_url}{endpoint}", headers=headers, json=data
                )
        else:
            # Unsigned requests
            headers["Content-Type"] = "application/json"
            response = requests.post(
                f"{self.base_url}{endpoint}", headers=headers, json=data
            )

        # After response
        logger.info(
            f"[POST RESPONSE] endpoint={endpoint}, status={response.status_code}, "
            f"body={response.text[:500]}..."  # limit body length for readability
        )

        return self._handle_response(response)

    def _get_headers(self):
        if self.exchange == "binance":
            return {"X-MBX-APIKEY": self.api_key}
        elif self.exchange == "bybit":
            return {}
        else:
            raise ValueError(f"Unsupported exchange: {self.exchange}")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                raise APIError(
                    "Invalid JSON response", status_code=response.status_code
                )
        else:
            raise APIError(
                f"API Error: {response.status_code} {response.text}",
                status_code=response.status_code,
            )

    def _build_query_string(self, params: Dict[str, Any]) -> str:
        return "&".join(
            f"{key}={quote(str(params[key]))}" for key in sorted(params.keys())
        )

    def _generate_signature(self, query_string) -> str:
        return hmac.new(
            self.secret_key.encode(), query_string.encode(), hashlib.sha256
        ).hexdigest()
