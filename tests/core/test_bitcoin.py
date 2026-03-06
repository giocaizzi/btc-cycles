"""test bitcoin module — behaviour tests"""

import datetime

import matplotlib.figure
import pandas as pd
import pytest

from btc_cycles.core.bitcoin import Bitcoin
from tests.conftest import MOCK_PREDICTION


@pytest.fixture
def bitcoin(mocker, test_prices) -> Bitcoin:
    """Bitcoin with mocked external dependencies (API + data source)."""
    mocker.patch(
        "btc_cycles.core.bitcoin.get_halving_data",
        return_value=MOCK_PREDICTION,
    )
    mock_prices = mocker.MagicMock()
    mock_prices.data = test_prices
    mocker.patch("btc_cycles.core.bitcoin.Prices", return_value=mock_prices)
    return Bitcoin()


class TestBitcoinInit:
    def test_has_price_data(self, bitcoin):
        assert isinstance(bitcoin.prices, pd.DataFrame)
        assert "Close" in bitcoin.prices.columns

    def test_has_halving_data(self, bitcoin):
        assert isinstance(bitcoin.halvings, pd.DataFrame)

    def test_has_predicted_halving(self, bitcoin):
        assert isinstance(bitcoin.predicted_halving_date, datetime.datetime)
        assert isinstance(bitcoin.predicted_halving_block, int)
        assert bitcoin.predicted_halving_block == 1050000

    def test_default_source_is_cryptocompare(self, mocker, test_prices):
        mocker.patch(
            "btc_cycles.core.bitcoin.get_halving_data",
            return_value=MOCK_PREDICTION,
        )
        mock_prices_cls = mocker.patch("btc_cycles.core.bitcoin.Prices")
        mock_prices_cls.return_value.data = test_prices
        Bitcoin()
        call_kwargs = mock_prices_cls.call_args
        assert call_kwargs.kwargs["source"] == "cryptocompare"


class TestBitcoinPlot:
    def test_returns_matplotlib_figure(self, bitcoin):
        fig = bitcoin.plot()
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_accepts_from_date(self, bitcoin):
        fig = bitcoin.plot(from_date="2023-01-01")
        assert isinstance(fig, matplotlib.figure.Figure)
