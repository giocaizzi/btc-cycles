"""bitcoin module"""

from .halvings import Halvings, get_halving_data
from .scraper import Scraper

# from .artists.artist import Artist

import pandas as pd
import datetime


class Bitcoin:
    """Bitcoin

    Attributes:
        history (DataFrame): halving history
        prices (DataFrame): historical OHLC data
    """

    def __init__(self):
        self._set_history()
        self._set_prices()
        self._set_metrics()

    def _set_history(self) -> None:
        """set history DataFrame"""
        self.history = Halvings().data

    def _set_prices(self) -> None:
        """set prices DataFrame"""
        # get data
        self.prices = Scraper().get_data()[["Date", "Close"]]
        # make Date UTC aware
        self.prices["Date"] = pd.to_datetime(self.prices["Date"]).dt.tz_localize("UTC")
        # add column to merged df so to keep track of halving dates
        history = self.history.copy()
        history["Halving"] = history["Date"]
        self.prices = self.prices.merge(
            history,
            how="outer",  # keep all halving dates
            on="Date",
        )
        # # fill NaNs due to merge only on subset of columns
        self.prices[["block", "cycle_length", "cycle_id", "Halving", "reward"]] = (
            self.prices[
                ["block", "cycle_length", "cycle_id", "Halving", "reward"]
            ].ffill()
        )
        # remove Halvings outside of prices datarange
        self.prices = self.prices[self.prices["Close"].notna()]
        # sort by date (ATH calculation requires ascending order)
        self.prices = self.prices.sort_values("Date").reset_index(drop=True)

    def _set_metrics(self) -> None:
        """set metrics to prices DataFrame"""
        # find ATH
        self.prices = _find_ath(self.prices)
        # find cycle progress
        self.prices = _find_cycle_progress(self.prices)

    # def plot(self, kind="static", **kwargs):
    #     """plot

    #     Args:
    #         kind (str, optional): plot kind. Defaults to "static".
    #         \\*\\*kwargs: additional keyword arguments to plotting method
    #     """
    #     Artist(kind, self).plot(**kwargs)


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
