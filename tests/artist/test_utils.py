"""test artist utils — behaviour tests"""

import pandas as pd

from btc_cycles.artist.utils import ColorBar, ProgressLabels


class TestColorBar:
    def test_normalizes_full_range(self, mock_bitcoin):
        """Norm maps min distance → 0 and max distance → 1."""
        colorbar = ColorBar(mock_bitcoin)
        assert colorbar.norm(mock_bitcoin.prices["distance_ath_perc"].min()) == 0.0
        assert colorbar.norm(mock_bitcoin.prices["distance_ath_perc"].max()) == 1.0

    def test_colormap_returns_rgba(self, mock_bitcoin):
        colorbar = ColorBar(mock_bitcoin)
        rgba = colorbar.cmap(0.5)
        assert len(rgba) == 4


class TestProgressLabels:
    def test_produces_four_labels(self, mock_bitcoin):
        """One label per progress tick: 0%, 25%, 50%, 75%."""
        labels = ProgressLabels(mock_bitcoin).labels
        assert isinstance(labels, pd.Series)
        assert len(labels) == 4

    def test_labels_contain_formatted_dates(self, mock_bitcoin):
        """Each label should contain at least one date in dd-mm-yyyy format."""
        import re

        date_pattern = re.compile(r"\d{2}-\d{2}-\d{4}")
        labels = ProgressLabels(mock_bitcoin).labels
        for label in labels:
            assert date_pattern.search(label), f"No date found in label: {label!r}"
