import pandas as pd
import pytest


import datetime
from unittest import mock

from btc_cycles.coins.bitcoin.halvings import update_predicted_halving_date

@pytest.mark.skip
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