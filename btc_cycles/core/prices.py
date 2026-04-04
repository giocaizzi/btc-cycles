"""prices module"""

import pandas as pd

from .sources import Source


def _find_ath(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Find all-time high and distance from ATH.

    Args:
        dataframe: Historical OHLC data with "Close" column.

    Returns:
        Data with "ATH" and "distance_ath_perc" columns added.
    """
    dataframe["ATH"] = dataframe["Close"].cummax()
    dataframe["distance_ath_perc"] = (
        dataframe["Close"] - dataframe["ATH"]
    ) / dataframe["ATH"]
    return dataframe


def _find_cycle_lows(
    dataframe: pd.DataFrame, min_separation_days: int = 90
) -> pd.DataFrame:
    """Find significant drawdown lows in each completed cycle.

    For each completed cycle, finds the deepest drawdown from ATH,
    then checks for a second significant low separated by at least
    `min_separation_days` from the first.

    Excludes the last (ongoing) cycle since the true bottom is unknown.

    Args:
        dataframe: Historical OHLC data with
            "distance_ath_perc", "cycle_id", and "Date" columns.
        min_separation_days: Minimum days between two lows
            to consider them distinct.

    Returns:
        Data with "is_cycle_low" column added.
    """
    dataframe["is_cycle_low"] = False
    last_cycle = dataframe["cycle_id"].max()

    for _, cycle_df in dataframe[dataframe["cycle_id"] < last_cycle].groupby(
        "cycle_id"
    ):
        # first low: deepest drawdown
        first_low_idx = cycle_df["distance_ath_perc"].idxmin()
        dataframe.loc[first_low_idx, "is_cycle_low"] = True

        # second low: deepest drawdown at least min_separation_days away
        first_low_date = dataframe.loc[first_low_idx, "Date"]
        distant = cycle_df[
            (cycle_df["Date"] - first_low_date).dt.days.abs() >= min_separation_days
        ]
        if not distant.empty:
            second_low_idx = distant["distance_ath_perc"].idxmin()
            dataframe.loc[second_low_idx, "is_cycle_low"] = True

    return dataframe


def _find_cycle_progress(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Find cycle progress as fraction of cycle length.

    Args:
        dataframe: Historical OHLC data with
            "cycle" and "cycle_length" columns.

    Returns:
        Data with "cycle_progress" column added.
    """
    dataframe["cycle_progress"] = (
        (dataframe["Date"] - dataframe["Halving"]).dt.days
    ) / dataframe["cycle_length"]
    return dataframe


def merge_halvings(data: pd.DataFrame, halvings: pd.DataFrame) -> pd.DataFrame:
    """Merge price data with halvings and forward-fill cycle metadata.

    Args:
        data: Price data with "Date" and "Close" columns.
        halvings: Halving data with "Date", "block", "reward",
            "cycle_length", and "cycle_id" columns.

    Returns:
        Merged DataFrame sorted by date with forward-filled cycle metadata.
    """
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize("UTC")

    halvings = halvings.copy()
    halvings["Halving"] = halvings["Date"]
    data = data.merge(
        halvings,
        how="outer",
        on="Date",
    )
    data[["block", "cycle_length", "cycle_id", "Halving", "reward"]] = (
        data[["block", "cycle_length", "cycle_id", "Halving", "reward"]]
        .infer_objects()
        .ffill()
    )
    # remove halvings outside of price data range
    data = data[data["Close"].notna()]
    # sort by date (ATH calculation requires ascending order)
    data = data.sort_values("Date").reset_index(drop=True)
    return data


class Prices:
    """Get historical OHLC data and set metrics.

    Fetches price data from the source, merges with halvings,
    and computes ATH, cycle lows, and cycle progress.

    Args:
        currency: Currency symbol (e.g. "USD").
        source: Data source name.
        api_key: API key for the source.
        halvings: Pre-built halving data to avoid redundant API calls.

    Attributes:
        data: Processed historical OHLC data with metrics.
    """

    coin: str = "BTC"

    def __init__(
        self,
        currency: str,
        source: str,
        api_key: str | None,
        halvings: pd.DataFrame,
    ):
        self.data = Source(source, api_key).get_data(self.coin, currency)
        self.halvings = halvings
        self._fmt_df()
        self._set_metrics()

    def _fmt_df(self) -> None:
        """Format DataFrame by merging with halvings and forward-filling."""
        self.data = merge_halvings(self.data, self.halvings)

    def _set_metrics(self) -> None:
        """Set ATH, cycle lows, and cycle progress metrics."""
        self.data = _find_ath(self.data)
        self.data = _find_cycle_lows(self.data)
        self.data = _find_cycle_progress(self.data)
