"""prices module"""

import pandas as pd
from cryptocmd import CmcScraper

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
        dataframe["Close"] / dataframe["ATH"]
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
    """Prices"""

    def __init__(self):
        self.coin = "BTC"
        # get price data
        self.data = self._get_data()
        # get halving data
        self.halvings = Halvings().data
        # format DataFrame
        self._fmt_df()
        # set metrics
        self._set_metrics()

    def _get_data(self) -> pd.DataFrame:
        """Get historical OHLC data

        Returns:
            DataFrame: OHLC data
        """
        scraper = CmcScraper(self.coin)
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
