"""bitcoin module"""

from .halving import get_halving_data
from .scraper import Scraper

import pandas as pd
import datetime

HALVINGS = [
    (datetime.datetime(2012, 11, 28), 210000),
    (datetime.datetime(2016, 7, 9), 420000),
    (datetime.datetime(2020, 5, 11), 630000),
]


class Bitcoin:
    """Bitcoin

    Attributes:
        founded (datetime): founded date (2009-01-03)
        history (DataFrame): halving history
        prices (DataFrame): historical OHLC data
    """

    def __init__(self):
        self.founded = datetime.datetime(2009, 1, 3)
        self._set_history()
        self._set_prices()
        self._set_metrics()

    def _set_history(self) -> None:
        """set history DataFrame"""
        self.history = pd.DataFrame(
            [(self.founded, 0)] + HALVINGS + [(get_halving_data())],
            columns=["Date", "block"],
        )
        # cycle length
        self.history["cycle_length"] = (self.history["Date"].diff().dt.days).shift(-1)
        # cycle id
        self.history["cycle"] = self.history.index + 1

    def _set_prices(self) -> None:
        """set prices DataFrame"""
        # get data
        self.prices = Scraper().get_data()[["Date", "Close"]]
        # add column to merged df so to keep track of halving dates
        history = self.history.copy()
        history["Halving"] = history["Date"]
        self.prices = self.prices.merge(
            history,
            how="outer",  # keep all halving dates
            on="Date",
        )
        # fill NaNs due to merge
        self.prices[["Block", "cycle_length", "cycle", "Halving"]] = self.prices[
            ["Block", "cycle_length", "cycle", "Halving"]
        ].fillna(method="ffill")
        # remove Halvings outside of prices datarange
        self.prices = self.prices[self.prices["Close"].notna()]
        # sort by date (ATH calculation requires ascending order)
        self.prices = self.prices.sort_values("Date")

    def _set_metrics(self) -> None:
        """set metrics to prices DataFrame"""
        # find ATH
        self.prices = _find_ath(self.prices)
        # find cycle progress
        self.prices = _find_cycle_progress(self.prices)


def _find_ath(dataframe: pd.DataFrame) -> pd.DataFrame:
    """find all-time high

    Args:
        dataframe (DataFrame): historical OHLC data with
            "Close" column

    Returns:
        DataFrame: historical OHLC data with
            "ATH" and "distance_ath_perc" columns
    """
    dataframe["ATH"] = dataframe["Close"].cummax()
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
