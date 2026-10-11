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


@pytest.fixture
def mock_coin(test_prices):
    """Mock Coin object with test prices aligned to BTC cycles."""
    coin = type("Coin", (), {})()
    # reuse BTC test prices with scaled-down close values to simulate an alt-coin
    coin_prices = test_prices.copy()
    coin_prices["Close"] = coin_prices["Close"] / 500
    # compute ATH and distance for the scaled coin prices
    coin_prices["ATH"] = coin_prices["Close"].cummax()
    coin_prices["distance_ath_perc"] = (
        coin_prices["Close"] - coin_prices["ATH"]
    ) / coin_prices["ATH"]
    coin.prices = coin_prices
    coin.symbol = "SOL"
    coin.color = "#FF8C00"
    return coin
