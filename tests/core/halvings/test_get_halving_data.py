from btc_cycles.coins.bitcoin.halvings import get_halving_data


import datetime
from unittest import mock

# --------------------
# Halving API response testing
# --------------------
# This test is expected to fail if the API response is not up to date.
# So, like in 2024, when the future halving date is not u


@mock.patch("btc_cycles.core.halvings.requests.get")
def test_get_halving_data_mocked(mock_get):
    """Test get_halving_data"""
    # Mock response data
    mock_response = {
        "target": {
            "predicted_timestamp": 1700000000,
            "block_number": 700000
        }
    }
    mock_get.return_value.json.return_value = mock_response

    # Call the function
    date, block = get_halving_data()

    # Expected results
    expected_date = datetime.datetime.fromtimestamp(1700000000).replace(tzinfo=datetime.timezone.utc)
    expected_block = 700000

    # Assert the results
    assert isinstance(date, datetime.datetime)
    assert date == expected_date

    assert isinstance(block, int)
    assert block == expected_block


def test_get_halving_data_api_response_uptodate_date_is_future():
    """Test get_halving_data date is in the future"""
    # Call the function
    date, block = get_halving_data()
    # assert that the date is in the future
    assert date > datetime.datetime.now(datetime.timezone.utc)


def test_get_halving_data_api_response_uptodate_block_is_future():
    """Test get_halving_data block is in the future"""
    pass