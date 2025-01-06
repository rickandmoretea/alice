import time
from typing import Dict, Any, final
import hmac
import hashlib
import requests
import json
from urllib.parse import quote

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

    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle GET requests.
        For signed requests, include necessary headers and parameters.
        """
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
                self._add_bybit_signature(params)

        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=headers,
            params=params,
        )
        return self._handle_response(response)

    def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle POST requests.
        For signed requests, include necessary headers and parameters.
        """
        if data is None:
            data = {}

        headers = self._get_headers()

        logger.info(
            f"[POST INIT] endpoint={endpoint}, exchange={self.exchange}, "
            f"use_signature={self.use_signature}, data_before_sign={data}, headers={headers}"
        )

        if self.use_signature:
            if self.exchange == "binance":
                data["timestamp"] = int(time.time() * 1000)
                query_string = self._build_query_string(data)
                signature = self._generate_signature(query_string)
                data["signature"] = signature
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    data=self._build_query_string(data),
                )
            elif self.exchange == "bybit":
                response = self._handle_bybit_post(endpoint, data, headers)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.post(
                f"{self.base_url}{endpoint}", headers=headers, json=data
            )
        # Handle both raw response and parsed dictionary for logging
        if isinstance(response, requests.Response):
            logger.info(
                f"[POST RESPONSE] endpoint={endpoint}, status={response.status_code}, body={response.text[:500]}..."
            )
            return self._handle_response(response)
        else:
            logger.info(f"[POST RESPONSE] endpoint={endpoint}, parsed_response={response}")
            return response

    def _get_headers(self):
        """
        Return headers for the request, depending on the exchange.
        """
        if self.exchange == "binance":
            return {"X-MBX-APIKEY": self.api_key}
        elif self.exchange == "bybit":
            return {}
        else:
            raise ValueError(f"Unsupported exchange: {self.exchange}")

    def _add_bybit_signature(self, params: Dict[str, Any]):
        """
        Add Bybit signature and required fields for signed GET requests.
        """
        recv_window = "5000"
        timestamp = str(int(time.time() * 1000))
        params.update(
            {
                "apiKey": self.api_key,
                "apiTimestamp": timestamp,
                "apiRecvWindow": recv_window,
            }
        )
        param_str = "&".join([f"{key}={params[key]}" for key in sorted(params)])
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["apiSignature"] = signature

    def _handle_bybit_post(self, endpoint: str, data: Dict[str, Any], headers: Dict[str, Any]):
        recv_window = "5000"
        timestamp = str(int(time.time() * 1000))
        payload_str = json.dumps(data, separators=(",", ":"))
        param_str = timestamp + self.api_key + recv_window + payload_str
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers.update(
            {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
                "X-BAPI-RECV-WINDOW": recv_window,
                "Content-Type": "application/json",
            }
        )

        logger.info(
            f"[BYBIT POST] Endpoint: {endpoint}, Payload: {data}, Headers: {headers}"
        )

        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=headers,
            data=payload_str,
        )
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Process the HTTP response.
        """
        # Log raw response
        logger.info(
            f"RAW RESPONSE -> Status: {response.status_code}, "
            f"Content: {response.text}"
        )

        try:
            response_data = response.json()  # Parse JSON response
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")

        # Check for HTTP errors
        if 200 <= response.status_code < 300:
            return response_data
        else:
            raise APIError(f"HTTP Error: {response.status_code} {response_data}")

    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """
        Build a query string from parameters.
        """
        return "&".join(
            f"{key}={quote(str(params[key]))}" for key in sorted(params.keys())
        )

    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC SHA256 signature for Binance.
        """
        return hmac.new(
            self.secret_key.encode(), query_string.encode(), hashlib.sha256
        ).hexdigest()
