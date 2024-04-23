"""test artist utils"""

import pandas as pd

from btc_cycles import Bitcoin
from btc_cycles.artist.utils import ColorBar, ProgressLabels

TEST = Bitcoin()


def test_colorbar():
    """test color bar"""
    colorbar = ColorBar(TEST)
    assert colorbar.cmap is not None
    assert colorbar.norm is not None


def test_progress_labels():
    """test progress labels"""
    progress_labels = ProgressLabels(TEST)
    # test labels
    assert progress_labels.labels is not None
    assert isinstance(progress_labels.labels, pd.Series)
    # test predicted halving string
    assert progress_labels.predicted_halving_str is not None
    assert isinstance(progress_labels.predicted_halving_str, str)
