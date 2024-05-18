"""bitcoin module"""

from __future__ import annotations

from .prices import Prices
from .halvings import get_halving_data, Halvings
from ..artist import Artist


# TODO: for now its assuming that the
#  cycle length is the same as previous


class Bitcoin:
    """Bitcoin

    Bitcoin class stores bitcoin prices and halvings data.

    Available data sources:
    - coinmarketcap-free
    - cryptocompare (requires API key)

    Plot bitcoin prices and halvings data.

    Args:
        source (str, optional): data source. Defaults to "coinmarketcap-free".
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

    def plot(self, kind="static", **kwargs) -> matplotlib.figure.Figure:
        """plot

        Args:
            kind (str, optional): plot kind. Defaults to "static".
            \\*\\*kwargs: additional keyword arguments to plotting method

        Returns:
            matplotlib.figure.Figure: figure object
        """
        return Artist(kind, self).plot(**kwargs)
