"""CoinmarketCap API wrapper."""

import requests

BASE_URL = "https://pro-api.coinmarketcap.com/v2"
ENDPOINT = "/cryptocurrency/ohlcv/historical"


class CoinMarketCap:
    """CoinMarketCap v2 API wrapper"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_historical_data(self, symbol: str, start: str, end: str) -> dict:
        """Get historical OHLC data from CoinMarketCap

        Args:
            symbol (str): cryptocurrency symbol
            start (str): start date in format "YYYY-MM-DD"
            end (str): end date in format "YYYY-MM-DD"

        Returns:
            dict: historical OHLC data
        """
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }
        params = {
            "symbol": symbol,
            "time_start": start,
            "time_end": end,
        }
        url = f"{BASE_URL}{ENDPOINT}"
        response = requests.get(url, headers=headers, params=params)
        return response.json()
