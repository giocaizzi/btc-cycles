"""bitcoin module"""

from typing import Optional
from ...core.base import BaseCoin


class Bitcoin(BaseCoin):
    """Bitcoin class"""

    def __init__(
        self,
        source: str = "cryptocompare",
        fiat: str = "USD",
        api_key: Optional[str] = None
    ):
        """initialize Bitcoin class

        Args:
            source (str, optional): source to get historical OHLC data. Defaults to "cryptocompare".
            fiat (str, optional): currency symbol. Defaults to "USD".
            api_key (str, optional): API key for the source. Defaults to None.
        """
        # get processed price data
        super().from_source("BTC", source, fiat, api_key)
