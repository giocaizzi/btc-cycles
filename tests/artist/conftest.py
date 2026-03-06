"""artist test configuration"""

import datetime

import pandas as pd
import pytest


@pytest.fixture
def mock_bitcoin(mocker, test_prices):
    """Mock Bitcoin object with test prices and halving data."""
    bitcoin = mocker.MagicMock()
    bitcoin.prices = test_prices
    bitcoin.halvings = pd.DataFrame(
        {
            "block": [630000, 840000],
            "Date": pd.to_datetime(["2020-05-11", "2024-04-20"]).tz_localize(
                "UTC"
            ),
            "cycle_length": [1440.0, 1446.0],
            "cycle_id": [4, 5],
        }
    )
    bitcoin.predicted_halving_date = datetime.datetime(
        2028, 4, 5, tzinfo=datetime.timezone.utc
    )
    bitcoin.predicted_halving_block = 1050000
    return bitcoin
