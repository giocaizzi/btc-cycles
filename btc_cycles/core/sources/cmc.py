"""CoinmarketCap API wrapper."""

import pandas as pd
import requests

from btc_cycles.core.sources.base import Source

BASE_URL = "https://pro-api.coinmarketcap.com/v2"
ENDPOINT = "/cryptocurrency/ohlcv/historical"


class CoinMarketCap(Source):
    """CoinMarketCap v2 API Source"""

    def get_data(self, symbol: str, start: str, end: str) -> dict:
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
        return pd.DataFrame(response.json())
