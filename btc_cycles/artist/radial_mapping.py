"""Radial mapping utilities for dual-axis polar charts."""

import numpy as np
import pandas as pd

# chart constant (must match static.py / interactive.py)
PRICE_UPPER_BOUND = 1_000_000


def map_to_btc_radial(
    coin_close: pd.Series,
    btc_close_min: float,
) -> pd.Series:
    """Map alt-coin prices into BTC's log-radial range.

    Linearly maps the coin's log-price range onto BTC's log-price range
    so both series share the same visual radial space on the polar chart.

    Args:
        coin_close: Alt-coin close prices.
        btc_close_min: Minimum BTC close price in the display range.

    Returns:
        Mapped prices that can be plotted on BTC's radial axis.
    """
    btc_log_min = np.log10(btc_close_min)
    btc_log_max = np.log10(PRICE_UPPER_BOUND)

    coin_log = np.log10(coin_close)
    coin_log_min = coin_log.min()
    coin_log_max = coin_log.max()

    # avoid division by zero if all prices are the same
    coin_log_range = coin_log_max - coin_log_min
    if coin_log_range == 0:
        mid = (btc_log_min + btc_log_max) / 2
        return pd.Series(np.full(len(coin_close), 10**mid), index=coin_close.index)

    normalized = (coin_log - coin_log_min) / coin_log_range
    mapped_log = btc_log_min + normalized * (btc_log_max - btc_log_min)
    return pd.Series(10**mapped_log, index=coin_close.index)


def coin_tick_labels(
    btc_grid_intervals: list[float],
    coin_close: pd.Series,
    btc_close_min: float,
) -> list[str]:
    """Compute alt-coin price labels at BTC grid positions.

    For each BTC grid line, computes what the corresponding alt-coin price
    would be, giving the user a readable second radial axis.

    Args:
        btc_grid_intervals: BTC price grid values (e.g. [100, 1000, ...]).
        coin_close: Alt-coin close prices (original, unmapped).
        btc_close_min: Minimum BTC close price in the display range.

    Returns:
        Formatted price strings for each grid position.
    """
    btc_log_min = np.log10(btc_close_min)
    btc_log_max = np.log10(PRICE_UPPER_BOUND)

    coin_log_min = np.log10(coin_close.min())
    coin_log_max = np.log10(coin_close.max())
    coin_log_range = coin_log_max - coin_log_min

    labels = []
    for interval in btc_grid_intervals:
        btc_log = np.log10(interval)
        # reverse the mapping: BTC radial position -> coin price
        if coin_log_range == 0:
            coin_price = coin_close.iloc[0]
        else:
            normalized = (btc_log - btc_log_min) / (btc_log_max - btc_log_min)
            coin_log_val = coin_log_min + normalized * coin_log_range
            coin_price = 10**coin_log_val

        labels.append(_format_price(coin_price))
    return labels


def _format_price(price: float) -> str:
    """Format a price for tick labels."""
    if price >= 1_000_000:
        return f"{price / 1_000_000:.1f}M"
    elif price >= 1_000:
        return f"{price / 1_000:.1f}k"
    elif price >= 1:
        return f"{price:.1f}"
    elif price >= 0.01:
        return f"{price:.3f}"
    else:
        return f"{price:.4g}"
