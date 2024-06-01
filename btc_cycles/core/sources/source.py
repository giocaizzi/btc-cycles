"""Source class"""

import datetime as dt
import pandas as pd

import cryptocompare
from cryptocmd import CmcScraper

START = dt.datetime(2009, 1, 1)


class Source:

    def __init__(self, source: str, api_key: str | None = None):
        self.source = source
        self.api_key = api_key

    def get_data(self, coin: str, fiat: str) -> pd.DataFrame:
        """Get historical OHLC data

        entrypoint to child classes method

        Args:
            coin (str): coin symbol
            fiat (str): currency symbol

        Returns:
            DataFrame: historical OHLC data

        Raises:
            ValueError: source not available
        """
        if self.source == "cryptocompare":
            cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
            data = cryptocompare.get_historical_price_day_from(
                coin=coin, currency=fiat, fromTs=START
            )
            data = pd.DataFrame(data)
            data["time"] = pd.to_datetime(data["time"], unit="s")
            data.rename({"time": "Date", "close": "Close"}, axis=1, inplace=True)
            return data[["Date", "Close"]]

        elif self.source == "coinmarketcap-free":
            scraper = CmcScraper(coin, fiat=fiat)
            scraper.get_data()
            return scraper.get_dataframe()[["Date", "Close"]]

        elif self.source == "coinmarketcap":
            raise NotImplementedError("CoinMarketCap API v2 not implemented")

        else:
            raise ValueError(f"source '{self.source}' not available")
