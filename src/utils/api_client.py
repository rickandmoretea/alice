import time
from typing import Dict, Any, final
import hmac
import hashlib
from urllib.parse import urlencode, quote

import requests

from src.utils.error_handler import APIError


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

    def post(
        self, endpoint: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if data is None:
            data = {}

        headers = self._get_headers()

        if self.use_signature:
            if self.exchange == "binance":
                # BINANCE: form-encoded body + signature appended to the data
                # 1) We must include "timestamp"
                if "timestamp" not in data:
                    data["timestamp"] = int(time.time() * 1000)
                # 2) Build query string and sign it
                query_string = self._build_query_string(data)
                signature = self._generate_signature(query_string)
                data["signature"] = signature

                # 3) We do a form-encoded POST
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    data=self._build_query_string(data),  # data= as a string
                )

            elif self.exchange == "bybit":
                # BYBIT: JSON body + signature as a field in JSON
                if "timestamp" not in data:
                    data["timestamp"] = int(time.time() * 1000)
                query_string = self._build_query_string(data)
                signature = self._generate_signature(query_string)
                data["signature"] = signature

                headers["Content-Type"] = "application/json"
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=data,  # JSON body
                )
            else:
                # Default fallback
                response = requests.post(
                    f"{self.base_url}{endpoint}", headers=headers, json=data
                )
        else:
            # Un-signed requests
            if self.exchange == "binance":
                # Possibly form-encoded or JSON, but typically public endpoints can handle either.
                # We'll do form-encoded as a safe default for Binance.
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    data=self._build_query_string(data),
                )
            elif self.exchange == "bybit":
                # Bybit typically wants JSON, even for public endpoints (if they exist).
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    f"{self.base_url}{endpoint}", headers=headers, json=data
                )
            else:
                # Fallback
                response = requests.post(
                    f"{self.base_url}{endpoint}", headers=headers, json=data
                )

        return self._handle_response(response)

    def _get_headers(self):
        if self.exchange == "binance":
            headers = {"X-MBX-APIKEY": self.api_key}
        else:  # Assume Bybit
            headers = {
                "X-BAPI-API-KEY": self.api_key,
            }
        return headers

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
