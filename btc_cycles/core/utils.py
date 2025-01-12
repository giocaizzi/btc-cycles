import os
import pandas as pd
from typing import Optional

from btc_cycles.core.sources import SOURCES, CoinMarketCap, CryptoCompare


def ath(dataframe: pd.DataFrame) -> pd.DataFrame:
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


def cycle_progress(dataframe: pd.DataFrame) -> pd.DataFrame:
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


def _fmt_df(data: pd.DataFrame, halvings: pd.DataFrame) -> None:
    """Format DataFrame"""
    # make Date UTC aware
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize("UTC")
    # add column to merged df so to keep track of halving dates
    halvings = halvings.copy()
    halvings["Halving"] = halvings["Date"]
    data = data.merge(
        halvings,
        how="outer",  # keep all halving dates
        on="Date",
    )
    # # fill NaNs due to merge only on subset of columns
    data[["block", "cycle_length", "cycle_id", "Halving", "reward"]] = (
        data[["block", "cycle_length", "cycle_id", "Halving", "reward"]]
        .infer_objects()
        .ffill()
    )
    # remove Halvings outside of prices datarange
    data = data[data["Close"].notna()]
    # sort by date (ATH calculation requires ascending order)
    data = data.sort_values("Date").reset_index(drop=True)

    # set metrics
    # find ATH
    data = ath(data)
    # find cycle progress
    data = cycle_progress(data)


def get_coin_from_source(
    coin: str, fiat: str, source: SOURCES, api_key: Optional[str] = None
) -> pd.DataFrame:
    """get historical OHLC data

    Gets historical OHLC data using desired `source`.

        Sets the following metrics on the OHLC dataframe:
        - ATH
        - distance from ATH in percentage
        - cycle progress

    Args:
        coin (str): coin symbol
        fiat (str): currency symbol
        source (str): source to get historical OHLC data
        halvings (DataFrame): BTC halving data

    Returns:
        DataFrame: historical OHLC data
    """
    # get price data
    if source == "coinmarketcap":
        data = CoinMarketCap(api_key=api_key).get_data(coin, fiat)
    elif source == "coinmarketcap-free":
        raise NotImplementedError("Source 'coinmarketcap-free' is not implemented.")
    elif source == "cryptocompare":
        data = CryptoCompare(api_key=api_key).get_data(coin, fiat)
    else:
        raise ValueError(f"Source '{source}' is not valid.")
    return data
