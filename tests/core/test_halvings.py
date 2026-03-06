"""test halvings module — behaviour tests"""

import datetime

import pandas as pd
import pytest

from btc_cycles.core.halvings import Halvings, HalvingAPIError, get_halving_data
from tests.conftest import MOCK_PREDICTION


class TestHalvings:
    def test_loads_known_halvings(self):
        halvings = Halvings(prediction=MOCK_PREDICTION)
        genesis = halvings.data[halvings.data["block"] == 0]
        assert not genesis.empty
        assert genesis.iloc[0]["Date"].year == 2009

    def test_sets_predicted_date_for_next_halving(self):
        halvings = Halvings(prediction=MOCK_PREDICTION)
        row = halvings.data[halvings.data["block"] == 1050000]
        assert not row.empty
        assert row.iloc[0]["Date"] == MOCK_PREDICTION[0]

    def test_has_cycle_metadata(self):
        halvings = Halvings(prediction=MOCK_PREDICTION)
        assert "cycle_length" in halvings.data.columns
        assert "cycle_id" in halvings.data.columns
        assert halvings.data["cycle_id"].iloc[0] == 1

    def test_known_halving_count(self):
        """At least 5 historical halvings should be present (genesis + 4 actual)."""
        halvings = Halvings(prediction=MOCK_PREDICTION)
        known = halvings.data[halvings.data["Date"].notna()]
        assert len(known) >= 5

    def test_unmatched_block_leaves_data_unchanged(self):
        """Prediction for a non-existent block doesn't corrupt data."""
        bogus_prediction = (
            datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc),
            9999999,
        )
        halvings = Halvings(prediction=bogus_prediction)
        # no row should have the bogus date
        assert not (halvings.data["Date"] == bogus_prediction[0]).any()


class TestGetHalvingData:
    def test_returns_future_date_and_block(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "target": {
                "predicted_timestamp": 1838300000,
                "block_number": "1050000",
            }
        }
        mocker.patch(
            "btc_cycles.core.halvings.requests.get",
            return_value=mock_response,
        )
        date, block = get_halving_data()
        assert isinstance(date, datetime.datetime)
        assert date.tzinfo is not None
        assert block == 1050000

    def test_raises_on_network_failure(self, mocker):
        import requests

        mocker.patch(
            "btc_cycles.core.halvings.requests.get",
            side_effect=requests.ConnectionError("down"),
        )
        with pytest.raises(HalvingAPIError):
            get_halving_data()

    def test_raises_on_malformed_response(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {}
        mocker.patch(
            "btc_cycles.core.halvings.requests.get",
            return_value=mock_response,
        )
        with pytest.raises(HalvingAPIError):
            get_halving_data()
