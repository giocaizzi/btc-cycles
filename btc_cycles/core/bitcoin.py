"""bitcoin module"""

import datetime
from typing import TYPE_CHECKING, Literal, Union

from ..artist import Artist
from .halvings import Halvings, get_halving_data
from .prices import Prices

if TYPE_CHECKING:
    import matplotlib.figure
    import plotly.graph_objects as go

    from .coin import Coin


class Bitcoin:
    """Bitcoin price data and halving cycle analysis.

    Fetches price data from the selected source, merges with halving
    cycle data, and computes metrics (ATH, cycle progress, cycle lows).

    Args:
        source: Data source. Defaults to "cryptocompare".
        currency: Currency. Defaults to "USD".
        api_key: API key for the data source.

    Attributes:
        prices: Bitcoin prices with cycle metrics.
        halvings: Bitcoin halving dates and cycle info.
        predicted_halving_date: Predicted next halving date.
        predicted_halving_block: Predicted next halving block number.
    """

    def __init__(
        self,
        source: str = "cryptocompare",
        currency: str = "USD",
        api_key: str | None = None,
    ):
        # single API call for halving prediction
        prediction = get_halving_data()
        self.predicted_halving_date, self.predicted_halving_block = prediction

        # single Halvings instantiation, reused for prices
        halvings = Halvings(prediction=prediction)
        self.halvings = halvings.data

        # get processed price data
        self.prices = Prices(
            currency=currency,
            source=source,
            api_key=api_key,
            halvings=halvings.data,
        ).data

    def plot(
        self,
        kind: Literal["static", "interactive"] = "static",
        from_date: str | datetime.datetime | None = None,
        theme: Literal["light", "dark"] | dict[str, str] = "light",
        overlay: "Coin | None" = None,
    ) -> Union["matplotlib.figure.Figure", "go.Figure"]:
        """Plot bitcoin prices against halving cycles.

        Args:
            kind: Plot kind ("static" or "interactive"). Defaults to "static".
            from_date: Start date for display filtering.
            theme: Theme for the plot. Defaults to "light". If a dictionary
                is passed, only the keys to override need to be provided.
                Valid keys: background, text, grid, now_line, halving_line,
                ath_marker, low_marker, watermark.
            overlay: Optional alt-coin to overlay on the chart.

        Returns:
            A matplotlib Figure (static) or Plotly Figure (interactive).
        """
        return Artist(bitcoin=self, kind=kind, theme=theme, overlay=overlay).plot(
            from_date=from_date
        )
