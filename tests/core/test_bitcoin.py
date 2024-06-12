"""test artist module"""

import matplotlib
import pytest
import datetime
import pandas as pd
import matplotlib.figure
from btc_cycles.core.bitcoin import Bitcoin


@pytest.fixture
def bitcoin_instance(mocker, test_prices) -> Bitcoin:
    # Create a mock for Prices class
    mock_prices = mocker.MagicMock()
    # Set the data attribute of the mock to be a DataFrame
    mock_prices.data = test_prices
    # Patch the Prices class to return the mock when instantiated
    mocker.patch("btc_cycles.core.bitcoin.Prices", return_value=mock_prices)
    return Bitcoin()


def test_Bitcoin_init(bitcoin_instance: Bitcoin, mocker):
    # # Assert that Prices was called with the correct arguments
    # Prices.assert_called_once_with(
    #     currency="USD", source="coinmarketcap-free", api_key=None
    # )
    # Assert that the prices attribute is set correctly
    assert isinstance(bitcoin_instance.prices, pd.DataFrame)
    # Assert that the halvings attribute is set correctly
    assert isinstance(bitcoin_instance.halvings, pd.DataFrame)
    # Assert that the predicted_halving_date attribute is set correctly
    assert isinstance(bitcoin_instance.predicted_halving_date, datetime.datetime)
    # Assert that the predicted_halving_block attribute is set correctly
    assert isinstance(bitcoin_instance.predicted_halving_block, int)


def test_Bitcoin_plot(bitcoin_instance: Bitcoin, mocker):
    # Call the plot method
    figure = bitcoin_instance.plot()
    # Assert that the returned object is a matplotlib Figure
    assert isinstance(figure, matplotlib.figure.Figure)
