"""coin module"""

import pandas as pd

from .prices import _find_ath, _find_cycle_progress, merge_halvings
from .sources import Source

DEFAULT_COLORS: dict[str, str] = {
    "SOL": "#FF8C00",
    "ETH": "#627eea",
    "ADA": "#0033ad",
    "DOT": "#e6007a",
    "BNB": "#f0b90b",
    "AVAX": "#e84142",
}
FALLBACK_COLOR = "grey"


class Coin:
    """Generic cryptocurrency aligned to BTC halving cycles.

    Fetches price data for any coin and aligns it to BTC halving cycles
    by computing cycle progress relative to BTC halvings.

    Args:
        symbol: Coin ticker (e.g. "SOL", "ETH").
        halvings: BTC halving DataFrame (from Bitcoin.halvings).
        source: Data source name. Defaults to "cryptocompare".
        currency: Fiat currency. Defaults to "USD".
        api_key: API key for the data source.
        color: Override display color. Defaults to palette lookup.

    Attributes:
        symbol: Coin ticker.
        prices: DataFrame with Date, Close, and cycle_progress columns.
        color: Display color string.
    """

    def __init__(
        self,
        symbol: str,
        halvings: pd.DataFrame,
        source: str = "cryptocompare",
        currency: str = "USD",
        api_key: str | None = None,
        color: str | None = None,
    ):
        self.symbol = symbol.upper()
        self.color = color or DEFAULT_COLORS.get(self.symbol, FALLBACK_COLOR)

        data = Source(source, api_key).get_data(self.symbol, currency)
        data = merge_halvings(data, halvings)
        data = _find_ath(data)
        self.prices = _find_cycle_progress(data)
