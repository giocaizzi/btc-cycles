"""test radial mapping utilities"""

import numpy as np
import pandas as pd
import pytest

from btc_cycles.artist.radial_mapping import (
    PRICE_UPPER_BOUND,
    _format_price,
    coin_tick_labels,
    map_to_btc_radial,
)


class TestMapToBtcRadial:
    def test_maps_to_btc_range(self):
        coin_close = pd.Series([10.0, 100.0, 1000.0])
        btc_close_min = 1000.0
        mapped = map_to_btc_radial(coin_close, btc_close_min)

        # lowest coin price maps to btc_close_min
        assert np.isclose(mapped.iloc[0], btc_close_min, rtol=1e-6)
        # highest coin price maps to PRICE_UPPER_BOUND
        assert np.isclose(mapped.iloc[-1], PRICE_UPPER_BOUND, rtol=1e-6)

    def test_preserves_order(self):
        coin_close = pd.Series([5.0, 50.0, 500.0])
        mapped = map_to_btc_radial(coin_close, 100.0)
        assert (mapped.diff().iloc[1:] > 0).all()

    def test_preserves_index(self):
        coin_close = pd.Series([10.0, 20.0], index=[5, 10])
        mapped = map_to_btc_radial(coin_close, 100.0)
        assert list(mapped.index) == [5, 10]

    def test_constant_prices(self):
        coin_close = pd.Series([42.0, 42.0, 42.0])
        mapped = map_to_btc_radial(coin_close, 100.0)
        # all should map to same midpoint value
        assert mapped.nunique() == 1


class TestCoinTickLabels:
    def test_returns_correct_count(self):
        grid = [100, 1000, 10000, 100000]
        coin_close = pd.Series([1.0, 10.0, 100.0])
        labels = coin_tick_labels(grid, coin_close, btc_close_min=100.0)
        assert len(labels) == 4

    def test_labels_are_strings(self):
        grid = [1000, 10000]
        coin_close = pd.Series([50.0, 200.0])
        labels = coin_tick_labels(grid, coin_close, btc_close_min=1000.0)
        assert all(isinstance(l, str) for l in labels)


class TestFormatPrice:
    def test_millions(self):
        assert _format_price(2_500_000) == "2.5M"

    def test_thousands(self):
        assert _format_price(1_500) == "1.5k"

    def test_units(self):
        assert _format_price(42.3) == "42.3"

    def test_cents(self):
        assert _format_price(0.05) == "0.050"

    def test_tiny(self):
        result = _format_price(0.001)
        assert "0.001" in result
