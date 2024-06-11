"""test artist module"""

import matplotlib

from btc_cycles import Bitcoin

# Mock the Prices object in the Bitcoin class
# loading the data from the test_prices.csv file


def test_Bitcoin_plot(mocker, test_prices):
    """test artist"""
    # Mock the return value of Prices().data
    mock_prices = mocker.patch("btc_cycles.core.prices.Prices", autospec=True)
    mock_prices.return_value.data.return_value = test_prices

    # Initialize Bitcoin object
    bitcoin = Bitcoin()

    # Call the plot method
    figure = bitcoin.plot()

    # Assert that the returned object is a matplotlib Figure
    assert isinstance(figure, matplotlib.figure.Figure)

    # Assert that Prices was called with the correct arguments
    mock_prices.assert_called_once_with(
        currency="USD", source="coinmarketcap-free", api_key=None
    )
