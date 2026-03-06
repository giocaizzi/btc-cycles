"""test configuration"""

import datetime

import pandas as pd
import pytest

MOCK_PREDICTION = (
    datetime.datetime(2028, 4, 5, tzinfo=datetime.timezone.utc),
    1050000,
)


@pytest.fixture
def test_prices():
    """Bitcoin test prices from CSV."""
    df = pd.read_csv("tests/test_prices.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df
