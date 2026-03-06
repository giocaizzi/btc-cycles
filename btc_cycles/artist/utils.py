"""common utils for artists"""

import datetime as dt
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

if TYPE_CHECKING:
    from ..core.bitcoin import Bitcoin


class ColorBar:
    """Color bar for distance-from-ATH color mapping.

    Args:
        bitcoin: Bitcoin object with price data.

    Attributes:
        norm: Matplotlib normalizer.
        cmap: Matplotlib colormap.
    """

    def __init__(self, bitcoin: "Bitcoin"):
        self._set_cmap(bitcoin)

    def _set_cmap(self, bitcoin: "Bitcoin") -> None:
        """Set colormap and normalization from price data."""
        self.norm = mcolors.Normalize(
            vmin=bitcoin.prices["distance_ath_perc"].min(),
            vmax=bitcoin.prices["distance_ath_perc"].max(),
        )
        self.cmap = plt.get_cmap("cool")


class ProgressLabels:
    """Progress labels for the polar chart x-axis ticks.

    Args:
        bitcoin: Bitcoin object with price and halving data.

    Attributes:
        labels: Formatted date labels for [0, 0.25, 0.50, 0.75] progress.
    """

    def __init__(self, bitcoin: "Bitcoin"):
        self._create_labels(bitcoin)

    def _create_labels(self, bitcoin: "Bitcoin") -> None:
        """Create labels for [0, 0.25, 0.50, 0.75] percent of cycle progress."""
        self.labels: list[pd.DataFrame] = []
        self._get_moments(bitcoin)

    def _get_moments(self, bitcoin: "Bitcoin") -> None:
        """Get moments for each progress value."""
        for progress in [0.00, 0.25, 0.50, 0.75]:
            self.labels.append(
                bitcoin.prices[
                    abs((bitcoin.prices["cycle_progress"] - progress)) < 0.0005
                ]
                .groupby("cycle_id")
                .first()
                .reset_index()
            )
        self.labels = pd.concat(self.labels)

        self.labels["cycle_progress"] = self.labels["cycle_progress"].apply(
            lambda x: round(x, 2)
        )
        self.labels = self.labels.groupby("cycle_progress")["Date"].apply(
            lambda x: "".join(
                f"{label}\n" for label in x.dt.strftime("%d-%m-%Y").to_list()
            )
        )

        self._add_predicted(bitcoin)

    def _add_predicted(self, bitcoin: "Bitcoin") -> None:
        """Adds predicted halving date to labels."""
        expected_length = bitcoin.halvings["cycle_length"].dropna().iloc[-1]
        predicted_dates = [bitcoin.predicted_halving_date] + [
            bitcoin.halvings["Date"].dropna().iloc[-2] + dt.timedelta(days=x)
            for x in [x * expected_length for x in [0.25, 0.5, 0.75]]
        ]
        for i, date in enumerate(predicted_dates):
            predicted_string = r"$\bf{{{}}}$".format(date.strftime("%d-%m-%Y"))
            self.labels.iloc[i] = self.labels.iloc[i] + predicted_string
