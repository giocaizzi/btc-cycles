"""CoinmarketCap API wrapper."""

import pandas as pd
import requests
import datetime as dt

from btc_cycles.core.sources.base import Source, START

BASE_URL = "https://pro-api.coinmarketcap.com/v2"
ENDPOINT = "/cryptocurrency/ohlcv/historical"


class CoinMarketCap(Source):
    """CoinMarketCap v2 API Source"""

    def get_data(self, coin: str, fiat:str) -> dict:
        """Get historical OHLC data from CoinMarketCap

        Args:
            coin (str): coin symbol
            fiat (str): currency symbol

        Returns:
            dict: historical OHLC data
        """
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }
        params = {
            "symbol": coin,
            "time_start": self.start.strftime("%Y-%m-%d"),
            "time_end": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        }
        url = f"{BASE_URL}{ENDPOINT}"
        response = requests.get(url, headers=headers, params=params)
        return pd.DataFrame(response.json())
