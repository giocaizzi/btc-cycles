"""Source class"""

import datetime as dt
import warnings

import cryptocompare
import pandas as pd
from cryptocmd import CmcScraper

# earliest date available from cryptocompare
START = dt.datetime(2010, 7, 17)


class DataSourceError(Exception):
    """Raised when a data source fails to return data."""


class Source:
    """Fetches historical OHLC price data from a named source.

    Args:
        source: Data source name (e.g. "cryptocompare").
        api_key: API key for the data source.
    """

    def __init__(self, source: str, api_key: str | None = None):
        self.source = source
        self.api_key = api_key

    def get_data(self, coin: str, fiat: str) -> pd.DataFrame:
        """Get historical OHLC data.

        Args:
            coin: Coin symbol (e.g. "BTC").
            fiat: Currency symbol (e.g. "USD").

        Returns:
            Historical OHLC data with Date and Close columns.

        Raises:
            DataSourceError: If the source fails.
            ValueError: If the source is not available.
        """
        fetchers = {
            "cryptocompare": self._fetch_cryptocompare,
            "coinmarketcap-free": self._fetch_coinmarketcap_free,
            "coinmarketcap": self._fetch_coinmarketcap,
        }

        fetcher = fetchers.get(self.source)
        if fetcher is None:
            raise ValueError(f"source '{self.source}' not available")

        return fetcher(coin, fiat)

    def _fetch_cryptocompare(self, coin: str, fiat: str) -> pd.DataFrame:
        try:
            cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
            data = cryptocompare.get_historical_price_day_from(
                coin=coin, currency=fiat, fromTs=START
            )
            data = pd.DataFrame(data)
            data["time"] = pd.to_datetime(data["time"], unit="s")
            data.rename({"time": "Date", "close": "Close"}, axis=1, inplace=True)
            return data[["Date", "Close"]]
        except Exception as e:
            raise DataSourceError(
                f"Error getting data from 'cryptocompare': {e}"
            ) from e

    def _fetch_coinmarketcap_free(self, coin: str, fiat: str) -> pd.DataFrame:
        warnings.warn(
            "The 'coinmarketcap-free' source is broken,"
            " and if a fix is not found,"
            " it will be removed in the future.",
            stacklevel=3,
        )
        try:
            scraper = CmcScraper(coin, fiat=fiat)
            scraper.get_data()
            return scraper.get_dataframe()[["Date", "Close"]]
        except Exception as e:
            raise DataSourceError(
                f"Error getting data from 'coinmarketcap-free': {e}"
            ) from e

    def _fetch_coinmarketcap(self, coin: str, fiat: str) -> pd.DataFrame:
        raise NotImplementedError("CoinMarketCap API v2 not implemented")
