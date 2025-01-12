"""prices module"""

from typing import Optional, Literal, Union
import pandas as pd
import datetime as dt
from matplotlib.figure import Figure

from .utils import _fmt_df, get_coin_from_source
from ..coins.bitcoin.halvings import Halvings, get_halving_data
from .sources import SOURCES
from ..artist import Artist

FIAT = Literal["USD", "EUR"]


class BaseCoin:
    """BaseCoin class

    BaseCoin is a base class for all coins.

    Attributes:
        coin (str): coin symbol
        fiat (str): currency symbol
        data (DataFrame): historical OHLC data
        halvings (DataFrame): BTC halving data
    """

    coin: str = None
    fiat: str = None
    source: SOURCES = None
    data: pd.DataFrame = None
    halvings: pd.DataFrame = Halvings().data

    def __init__(
        self,
        coin: str,
        source: SOURCES,
        fiat: Optional[FIAT] = "USD",
        data: Optional[pd.DataFrame] = None,
    ):
        """initialize BaseCoin class

        Args:
            coin (str): coin symbol.
            source (str): source to get historical OHLC data.
            fiat (str, optional): currency symbol. Defaults to "USD".
            data (DataFrame, optional): historical OHLC data. Defaults to None.
        """
        # set attributes
        self.coin = coin
        self.fiat = fiat
        self.source = source
        self.data = data

        # predicted next halving date and block
        self.predicted_halving_date, self.predicted_halving_block = get_halving_data()

    @classmethod
    def from_source(
        cls,
        coin: str,
        source: SOURCES,
        fiat: Optional[FIAT] = "USD",
        api_key: Optional[str] = None,
    ) -> "BaseCoin":
        """initialize BaseCoin class from source data

        Args:
            coin (str): coin symbol.
            source (str): source to get historical OHLC data.
            fiat (str, optional): currency symbol. Defaults to "USD".
            api_key (str, optional): API key for the source. Defaults to None.

        Returns:
            BaseCoin: instance of BaseCoin class
        """
        # get historical OHLC data
        data = get_coin_from_source(coin, fiat, source, api_key)
        # format dataframe
        data = _fmt_df(data, cls.halvings)
        # create instance
        return cls(coin=coin, fiat=fiat, source=source, data=data)

    def plot(
        self,
        kind: str = "static",
        from_date: Union[str, dt.datetime] = None,
        theme: Union[Literal["light", "dark"], dict] = "light",
        **plotting_kwargs,
    ) -> Figure:
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
