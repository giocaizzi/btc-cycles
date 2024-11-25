"""test halvings"""

import pandas as pd

from btc_cycles.core.halvings import Halvings
import datetime
import requests
from unittest import mock
from btc_cycles.core.halvings import get_halving_data


# --------------------
# Halvings class testing
# --------------------

@mock.patch("btc_cycles.core.halvings.get_halving_data")
def test_halvings_init(mock_get_halving_data):
    """Test Halvings class initialization"""
    # Mock get_halving_data response
    mock_get_halving_data.return_value = (datetime.datetime(2024, 5, 1, tzinfo=datetime.timezone.utc), 700000)

    # Create Halvings instance
    halvings = Halvings()

    # Assert data is a DataFrame
    assert isinstance(halvings.data, pd.DataFrame)

    # Assert columns
    assert list(halvings.data.columns) == ["block", "reward", "Date",	"cycle_length", "cycle_id"]

    # Assert cycle_length and cycle_id are correct
    assert halvings.data["cycle_length"].dtype == "float64"
    assert halvings.data["cycle_id"].dtype == "int64"

@mock.patch("btc_cycles.core.halvings.get_halving_data")
def test_update_predicted_halving_date(mock_get_halving_data):
    """Test update_predicted_halving_date function"""
    # Mock get_halving_data response
    mock_get_halving_data.return_value = (datetime.datetime(2024, 5, 1, tzinfo=datetime.timezone.utc), 700000)

    # Create sample data
    data = pd.DataFrame({
        "block": [699999, 700000, 700001],
        "Date": [datetime.datetime(2020, 5, 1), datetime.datetime(2024, 5, 1), datetime.datetime(2028, 5, 1)]
    })

    # Update predicted halving date
    updated_data = update_predicted_halving_date(data)

    # Assert the date is updated
    assert updated_data.loc[updated_data["block"] == 700000, "Date"].values[0] == datetime.datetime(2024, 5, 1, tzinfo=datetime.timezone.utc)


# --------------------
# get_halving_data testing
# --------------------

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

# --------------------
# Halving API response testing
# --------------------
# This test is expected to fail if the API response is not up to date.
# So, like in 2024, when the future halving date is not u
def test_get_halving_data_api_response_uptodate_date_is_future():
    """Test get_halving_data date is in the future"""
    # Call the function
    date, block = get_halving_data()
    # assert that the date is in the future
    assert date > datetime.datetime.now(datetime.timezone.utc)

def test_get_halving_data_api_response_uptodate_block_is_future():
    """Test get_halving_data block is in the future"""
    pass
    """test halvings"""