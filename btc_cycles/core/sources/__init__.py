"""sources module"""

from typing import Literal

from .cmc import CoinMarketCap
from .cryptocompare import CryptoCompare

SOURCES = Literal["coinmarketcap","coinmarketcap-free","cryptocompare"]

__all__ = ["CryptoCompare", "CoinMarketCap"]
