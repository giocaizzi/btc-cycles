"""test halvings"""

import pandas as pd

from btc_cycles.halvings import Halvings


def test_Halving():
    """test Halving"""
    halvings = Halvings()
    # data is a DataFrame
    assert isinstance(halvings.data, pd.DataFrame)
