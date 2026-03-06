"""test prices module — behaviour tests for price metric functions"""

import pandas as pd
import pytest

from btc_cycles.core.prices import _find_ath, _find_cycle_lows, _find_cycle_progress


@pytest.fixture
def two_cycle_prices():
    """Two completed cycles + one ongoing, with a clear ATH and drawdown."""
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2013-01-01",
                    "2013-12-01",
                    "2014-06-01",
                    "2017-01-01",
                    "2017-12-01",
                    "2018-12-01",
                    "2021-01-01",
                ]
            ),
            "Close": [100, 1000, 200, 900, 20000, 3000, 30000],
            "cycle_id": [1, 1, 1, 2, 2, 2, 3],
            "Halving": pd.to_datetime(
                [
                    "2012-11-28",
                    "2012-11-28",
                    "2012-11-28",
                    "2016-07-09",
                    "2016-07-09",
                    "2016-07-09",
                    "2020-05-11",
                ]
            ),
            "cycle_length": [1319, 1319, 1319, 1402, 1402, 1402, 1440],
        }
    )


class TestFindATH:
    def test_ath_never_decreases(self, two_cycle_prices):
        result = _find_ath(two_cycle_prices)
        assert result["ATH"].is_monotonic_increasing

    def test_distance_is_zero_at_ath(self, two_cycle_prices):
        result = _find_ath(two_cycle_prices)
        at_ath = result[result["Close"] == result["ATH"]]
        assert (at_ath["distance_ath_perc"] == 0.0).all()

    def test_distance_is_negative_below_ath(self, two_cycle_prices):
        result = _find_ath(two_cycle_prices)
        below_ath = result[result["Close"] < result["ATH"]]
        assert (below_ath["distance_ath_perc"] < 0).all()

    def test_single_row(self):
        """A single data point is its own ATH with zero distance."""
        df = pd.DataFrame({"Close": [100]})
        result = _find_ath(df)
        assert result.loc[0, "ATH"] == 100
        assert result.loc[0, "distance_ath_perc"] == 0.0


class TestFindCycleLows:
    def test_lows_only_in_completed_cycles(self, two_cycle_prices):
        df = _find_ath(two_cycle_prices)
        result = _find_cycle_lows(df)
        lows = result[result["is_cycle_low"]]
        last_cycle = result["cycle_id"].max()
        assert (lows["cycle_id"] < last_cycle).all()

    def test_at_least_one_low_per_completed_cycle(self, two_cycle_prices):
        df = _find_ath(two_cycle_prices)
        result = _find_cycle_lows(df)
        lows = result[result["is_cycle_low"]]
        completed_cycles = set(range(1, result["cycle_id"].max()))
        assert completed_cycles == set(lows["cycle_id"])

    def test_low_is_at_deepest_drawdown(self, two_cycle_prices):
        df = _find_ath(two_cycle_prices)
        result = _find_cycle_lows(df)
        completed = result[result["cycle_id"] < result["cycle_id"].max()]
        for _, group in completed.groupby("cycle_id"):
            cycle_lows = group[group["is_cycle_low"]]
            deepest = group["distance_ath_perc"].min()
            assert deepest in cycle_lows["distance_ath_perc"].values

    def test_single_cycle_produces_no_lows(self):
        """Only one cycle (ongoing) means no completed cycles → no lows."""
        df = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2021-01-01", "2021-06-01"]),
                "Close": [30000, 20000],
                "cycle_id": [1, 1],
                "distance_ath_perc": [0.0, -0.33],
            }
        )
        result = _find_cycle_lows(df)
        assert not result["is_cycle_low"].any()


class TestFindCycleProgress:
    def test_progress_at_halving_is_zero(self):
        df = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2020-05-11"]),
                "Halving": pd.to_datetime(["2020-05-11"]),
                "cycle_length": [1440],
            }
        )
        result = _find_cycle_progress(df)
        assert result.loc[0, "cycle_progress"] == 0.0

    def test_progress_increases_with_time(self, two_cycle_prices):
        result = _find_cycle_progress(two_cycle_prices)
        for _, group in result.groupby("cycle_id"):
            assert group["cycle_progress"].is_monotonic_increasing

    def test_halfway_through_cycle(self):
        """720 days into a 1440-day cycle should be 0.5 progress."""
        df = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2022-05-01"]),
                "Halving": pd.to_datetime(["2020-05-11"]),
                "cycle_length": [1440],
            }
        )
        result = _find_cycle_progress(df)
        expected = (pd.Timestamp("2022-05-01") - pd.Timestamp("2020-05-11")).days / 1440
        assert abs(result.loc[0, "cycle_progress"] - expected) < 0.001
