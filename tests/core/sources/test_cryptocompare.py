from unittest import mock

import pandas as pd
import pytest

from btc_cycles.core.sources.cryptocompare import CryptoCompare


@pytest.fixture
def cryptocompare_instance():
    return CryptoCompare(api_key="test_api_key")


@mock.patch(
    "btc_cycles.core.sources.cryptocompare.cryptocompare.get_historical_price_day_from"
)
def test_get_data(mock_get_historical_price_day_from, cryptocompare_instance):
    """Assert that the get_data method returns a DataFrame with the expected data

    Given the mock_data that represents the data returned by the API
    - test proper data transformation
    - test that the method returns the expected DataFrame
    """
    # Mock cryptocompare API response data
    # time and close columns
    mock_data = [
        {"time": 1609459200, "close": 29000},
        {"time": 1609545600, "close": 29500},
    ]
    mock_get_historical_price_day_from.return_value = mock_data

    # Get data
    result = cryptocompare_instance.get_data(coin="BTC", fiat="USD")

    # Expected data
    # DataFrames with `Date` and `Close` columns
    expected_data = pd.DataFrame(
        {
            "Date": pd.to_datetime([1609459200, 1609545600], unit="s"),
            "Close": [29000, 29500],
        }
    )

    # Assert
    pd.testing.assert_frame_equal(result, expected_data)


@mock.patch(
    "btc_cycles.core.sources.cryptocompare.cryptocompare.get_historical_price_day_from"
)
def test_get_data_exception(mock_get_historical_price_day_from, cryptocompare_instance):
    """Assert that the get_data method raises a ValueError when an exception is raised"""
    mock_get_historical_price_day_from.side_effect = Exception("API error")

    with pytest.raises(
        ValueError, match="Error getting data from 'cryptocompare' source: API error"
    ):
        cryptocompare_instance.get_data(coin="BTC", fiat="USD")
