"""base module for btc_cycles.core.sources"""

import datetime as dt
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

# bitcoin start date is 2009-01-01 (or 2009-01-03)?
# in any case, as for issue26, the start date returned
# by historical price services might also change
# cryptocompare now from 2010-07-17
# TODO: dynamic start date (?)
START = dt.datetime(2010, 7, 17)


class Source(ABC):
    """Source class

    Abstract class to get historical OHLC data.

    Attributes:
        api_key (Optional[str]): API key for the source
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    def get_data(
        self, coin: str, fiat: str, start: str | dt.datetime, end: str | dt.datetime
    ) -> pd.DataFrame:
        """Get historical OHLC data

        Args:
            coin (str): coin symbol
            fiat (str): currency symbol

        Returns:
            DataFrame: historical OHLC data
        """
        ...
