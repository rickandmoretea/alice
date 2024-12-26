import urllib
from typing import Dict, Any, final
import hmac
import hashlib
from urllib.parse import urlencode

import requests

from src.utils.error_handler import APIError

@final
class APIClient:
    __slots__ = ('base_url', 'api_key', 'secret_key', 'use_signature')

    def __init__(self, base_url: str, api_key: str, secret_key: str, use_signature: bool = False):
        """
        :param base_url: Base URL for the exchange
        :param api_key: API key for the exchange
        :param secret_key: API secret key for the exchange
        :param use_signature: If let to True, the client will sign the requests automatically
        """
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.use_signature = use_signature

    def get(self, endpoint, params=None) -> Dict[str, Any]:
        """
        Send a GET request to the endpoint with the given parameters.
        :param endpoint:  API endpoint
        :param params:  Query parameters
        :return: JSON response
        """
        if params is None:
            params = {}
        headers = self._get_headers()
        if self.use_signature:
            query_string = self._build_query_string(params)
            signature = self._generate_signature(query_string)
            params["signature"] = signature

        response = requests.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
        return self._handle_response(response)

    def post(self, endpoint, data=None) -> Dict[str, Any]:
        if data is None:
            data = {}
        headers = self._get_headers()
        if self.use_signature:
            query_string = self._build_query_string(data)
            signature = self._generate_signature(query_string)
            data["signature"] = signature

            query_string_with_sig = self._build_query_string(data)
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=query_string_with_sig,
            )
        else:
            query_string = self._build_query_string(data)
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=query_string
            )
        return self._handle_response(response)

    def _get_headers(self):
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _handle_response(response) -> Dict[str, Any]:
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                raise APIError("Invalid JSON response", status_code=response.status_code)
        else:
            raise APIError(
                f"API Error: {response.status_code} {response.text}",
                status_code=response.status_code
            )

    @staticmethod
    def _build_query_string(params) -> str:
        """Convert dict to query string then sort it by key (s.t the signature will be consistent)
        """
        return "&".join(f"{key}={urllib.parse.quote(str(params[key]))}" for key in sorted(params.keys()))

    def _generate_signature(self, query_string) -> str:
        """Generate HMAC SHA256 signature for the query string"""
        return hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()


