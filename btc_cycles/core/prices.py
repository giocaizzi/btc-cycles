"""prices module"""

import pandas as pd
import datetime as dt
from cryptocmd import CmcScraper
import cryptocompare

from .halvings import Halvings


def _find_ath(dataframe: pd.DataFrame) -> pd.DataFrame:
    """find all-time high

    Args:
        dataframe (DataFrame): historical OHLC data with
            "Close" column

    Returns:
        DataFrame: historical OHLC data with
            "ATH" and "distance_ath_perc" columns
    """
    # find ATH
    dataframe["ATH"] = dataframe["Close"].cummax()
    # find distance from ATH in percentage
    dataframe["distance_ath_perc"] = (
        dataframe["Close"] - dataframe["ATH"]
    ) / dataframe["ATH"]
    return dataframe


def _find_cycle_progress(dataframe: pd.DataFrame) -> pd.DataFrame:
    """find cycle progress

    Args:
        dataframe (DataFrame): historical OHLC data with
            "cycle" and "cycle_length" columns

    Returns:
        DataFrame: historical OHLC data with
            "cycle_progress" column
    """
    dataframe["cycle_progress"] = (
        (dataframe["Date"] - dataframe["Halving"]).dt.days
    ) / dataframe["cycle_length"]
    return dataframe


class Prices:
    """Get historical OHLC data and set metrics

    Prices class to get historical OHLC data and halving data,
    and process it.

    Gets historical OHLC data using desired `source`.

    The source `coinmarketcap-free`, gets data from
    CoinMarketCap, without authentication and using the `cryptocmd` package,
    a wrapper to the API. Without authentication, the data returns a limited
    number of data points.

    The source `cryptocompare` uses the `cryptocompare` package to get data.
    Requires an API key.

    Sets the following metrics on the OHLC dataframe:
    - ATH
    - distance from ATH in percentage
    - cycle progress

    Args:
        source (str): source to get historical OHLC data
        api_key (str): API key for source

    Attributes:
        source(str): source to get historical OHLC data
        coin (str): coin symbol
        data (DataFrame): historical OHLC data
        halvings (DataFrame): halving data
    """

    def __init__(self, currency: str, source: str, api_key: str):
        self.source = source
        self.coin = "BTC"
        self.fiat = currency
        # get price data
        self.data = self._get_data(api_key=api_key)
        # get halving data
        self.halvings = Halvings().data
        # format DataFrame
        self._fmt_df()
        # set metrics
        self._set_metrics()

    def _get_data(self, api_key: str) -> pd.DataFrame:
        """Get historical OHLC data

        Returns:
            DataFrame: OHLC data
        """
        if self.source == "cryptocompare":
            cryptocompare.cryptocompare._set_api_key_parameter(api_key)
            data = cryptocompare.get_historical_price_day_from(
                coin=self.coin, currency=self.fiat, fromTs=dt.datetime(2009, 1, 1)
            )
            data = pd.DataFrame(data)
            data["time"] = pd.to_datetime(data["time"], unit="s")
            data.rename({"time": "Date", "close": "Close"}, axis=1, inplace=True)
            return data[["Date", "Close"]]

        else:
            scraper = CmcScraper(self.coin, fiat=self.fiat)
            scraper.get_data()
            return scraper.get_dataframe()[["Date", "Close"]]

    def _fmt_df(self) -> None:
        """Format DataFrame"""
        # make Date UTC aware
        self.data["Date"] = pd.to_datetime(self.data["Date"]).dt.tz_localize("UTC")
        # add column to merged df so to keep track of halving dates
        halvings = self.halvings.copy()
        halvings["Halving"] = halvings["Date"]
        self.data = self.data.merge(
            halvings,
            how="outer",  # keep all halving dates
            on="Date",
        )
        # # fill NaNs due to merge only on subset of columns
        self.data[["block", "cycle_length", "cycle_id", "Halving", "reward"]] = (
            self.data[["block", "cycle_length", "cycle_id", "Halving", "reward"]]
            .infer_objects()
            .ffill()
        )
        # remove Halvings outside of prices datarange
        self.data = self.data[self.data["Close"].notna()]
        # sort by date (ATH calculation requires ascending order)
        self.data = self.data.sort_values("Date").reset_index(drop=True)

    def _set_metrics(self) -> None:
        """set metrics to prices DataFrame"""
        # find ATH
        self.data = _find_ath(self.data)
        # find cycle progress
        self.data = _find_cycle_progress(self.data)
