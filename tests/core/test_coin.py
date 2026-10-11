"""test coin module"""

import pandas as pd
import pytest

from btc_cycles.core.coin import FALLBACK_COLOR, Coin


@pytest.fixture
def mock_halvings():
    """BTC halving DataFrame for testing."""
    return pd.DataFrame(
        {
            "block": [630000, 840000],
            "Date": pd.to_datetime(["2020-05-11", "2024-04-20"]).tz_localize("UTC"),
            "reward": [6.25, 3.125],
            "cycle_length": [1440.0, 1446.0],
            "cycle_id": [4, 5],
        }
    )


@pytest.fixture
def mock_coin_prices():
    """Raw price data mimicking Source.get_data() output for an alt-coin."""
    dates = pd.date_range("2020-06-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "Date": dates,
            "Close": [10 + i * 0.5 for i in range(100)],
        }
    )


@pytest.fixture
def coin(mocker, mock_halvings, mock_coin_prices):
    """Coin with mocked data source."""
    mocker.patch(
        "btc_cycles.core.coin.Source.get_data",
        return_value=mock_coin_prices,
    )
    return Coin("SOL", halvings=mock_halvings)


class TestCoinInit:
    def test_has_prices_with_cycle_progress(self, coin):
        assert isinstance(coin.prices, pd.DataFrame)
        assert "cycle_progress" in coin.prices.columns

    def test_has_close_column(self, coin):
        assert "Close" in coin.prices.columns

    def test_symbol_is_uppercase(self, mocker, mock_halvings, mock_coin_prices):
        mocker.patch(
            "btc_cycles.core.coin.Source.get_data",
            return_value=mock_coin_prices,
        )
        coin = Coin("sol", halvings=mock_halvings)
        assert coin.symbol == "SOL"

    def test_uses_btc_halvings_for_cycle_progress(self, coin):
        assert coin.prices["cycle_progress"].notna().all()
        assert (coin.prices["cycle_progress"] >= 0).all()

    def test_prices_sorted_by_date(self, coin):
        dates = coin.prices["Date"].values
        assert (dates[:-1] <= dates[1:]).all()


class TestCoinColor:
    def test_has_ath_columns(self, coin):
        assert "ATH" in coin.prices.columns
        assert "distance_ath_perc" in coin.prices.columns

    def test_default_color_for_sol(self, coin):
        assert coin.color == "#FF8C00"

    def test_custom_color(self, mocker, mock_halvings, mock_coin_prices):
        mocker.patch(
            "btc_cycles.core.coin.Source.get_data",
            return_value=mock_coin_prices,
        )
        coin = Coin("SOL", halvings=mock_halvings, color="cyan")
        assert coin.color == "cyan"

    def test_unknown_symbol_gets_fallback(self, mocker, mock_halvings, mock_coin_prices):
        mocker.patch(
            "btc_cycles.core.coin.Source.get_data",
            return_value=mock_coin_prices,
        )
        coin = Coin("UNKNOWN", halvings=mock_halvings)
        assert coin.color == FALLBACK_COLOR
