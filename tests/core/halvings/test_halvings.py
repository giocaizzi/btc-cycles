"""test halvings"""

import pandas as pd

from btc_cycles.coins.bitcoin.halvings import Halvings
import datetime
from unittest import mock

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

