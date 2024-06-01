"""bitcoin module"""

from __future__ import annotations
from typing import Union, Literal
import datetime

from .prices import Prices
from .halvings import get_halving_data, Halvings
from ..artist import Artist


# TODO: for now its assuming that the
#  cycle length is the same as previous


class Bitcoin:
    """Bitcoin

    Bitcoin class stores bitcoin prices and halvings data.
    All sources require an API key.

    Available data sources:
    - coinmarketcap
    - cryptocompare
    - coinmarketcap-free (**legacy broken source**)

    Plot bitcoin prices and halvings data.

    Args:
        source (str, optional): data source. Defaults to "cryptocompare".
        currency (str, optional): currency. Defaults to "USD".
        api_key (str, optional): API key. Defaults to None.

    Attributes:
        prices (DataFrame): bitcoin prices
        halvings (DataFrame): bitcoin halvings
        predicted_halving_date (datetime): predicted halving date
        predicted_halving_block (int): predicted halving block
    """

    def __init__(
        self,
        source: str = "coinmarketcap-free",
        currency: str = "USD",
        api_key: str = None,
    ):
        # get processed price data
        self.prices = Prices(currency=currency, source=source, api_key=api_key).data
        # save halving data
        self.halvings = Halvings().data
        # predicted next halving date and block
        self.predicted_halving_date, self.predicted_halving_block = get_halving_data()

    def plot(
        self,
        kind: str = "static",
        from_date: Union[str, datetime.datetime] = None,
        theme: Union[Literal["light", "dark"], dict] = "light",
        **plotting_kwargs,
    ) -> matplotlib.figure.Figure:
        """plot

        Args:
            kind (str, optional): plot kind. Defaults to "static".
            from_date (Union[str, datetime.datetime], optional): start date.
                Defaults to None, which fetches all data.
            \\*\\*plotting_kwargs: additional keyword arguments to Artist's
                plotting method.
            theme (Union[Literal["light", "dark"],dict], optional): theme
                for the plot. Defaults to "light". If a dictionary is passed,
                it should contain one of following keys. It's not required to
                pass all of them, only the ones you want to change from the
                default `light` theme:
                - background: background color
                - text: text color
                - grid: grid color
                - now_line: now line color
                - halving_line: halving line color
                - ath_marker: all-time high marker color

        Returns:
            matplotlib.figure.Figure: figure object
        """
        # update plotting kwargs
        plotting_kwargs.update({"from_date": from_date})
        # plot
        return Artist(bitcoin=self, kind=kind, theme=theme).plot(**plotting_kwargs)
