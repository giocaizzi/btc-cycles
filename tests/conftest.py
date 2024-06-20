"""test configuration"""

import pandas as pd
import pytest

# ---- Test data ----


@pytest.fixture
def test_prices():
    """read csv test_prices.csv"""
    df = pd.read_csv("tests/test_prices.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df
