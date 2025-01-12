""""""
from typing import Optional
from btc_cycles.core.base import BaseCoin


class Ethereum(BaseCoin):

    def __init__(
        self,
        source: str = "cryptocompare",
        fiat: str = "USD",
        api_key: Optional[str] = None,
    ):
        """initialize Ethereum class

        Args:
            source (str, optional): source to get historical OHLC data. Defaults to "cryptocompare".
            fiat (str, optional): currency symbol. Defaults to "USD".
            api_key (str, optional): API key for the source. Defaults to None.
        """
        # get processed price data
        super().from_source("ETH", source, fiat, api_key)
