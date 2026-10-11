"""test overlay rendering in both static and interactive artists"""

import matplotlib.figure
import plotly.graph_objects as go

from btc_cycles.artist.artist import Artist


class TestStaticOverlay:
    def test_returns_figure_with_overlay(self, mock_bitcoin, mock_coin):
        artist = Artist(
            mock_bitcoin, kind="static", theme="light", overlay=mock_coin
        )
        fig = artist.plot(from_date="2020-05-11")
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_without_overlay_unchanged(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="static", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_overlay_adds_legend_entry(self, mock_bitcoin, mock_coin):
        artist = Artist(
            mock_bitcoin, kind="static", theme="light", overlay=mock_coin
        )
        fig = artist.plot(from_date="2020-05-11")
        legend_texts = [t.get_text() for t in fig.legends[0].get_texts()]
        assert "SOL/USD" in legend_texts


class TestInteractiveOverlay:
    def test_returns_figure_with_overlay(self, mock_bitcoin, mock_coin):
        artist = Artist(
            mock_bitcoin, kind="interactive", theme="light", overlay=mock_coin
        )
        fig = artist.plot(from_date="2020-05-11")
        assert isinstance(fig, go.Figure)

    def test_overlay_adds_extra_traces(self, mock_bitcoin, mock_coin):
        artist_no_overlay = Artist(
            mock_bitcoin, kind="interactive", theme="light"
        )
        fig_no = artist_no_overlay.plot(from_date="2020-05-11")

        artist_with_overlay = Artist(
            mock_bitcoin, kind="interactive", theme="light", overlay=mock_coin
        )
        fig_yes = artist_with_overlay.plot(from_date="2020-05-11")

        assert len(fig_yes.data) > len(fig_no.data)

    def test_overlay_legend_includes_coin_name(self, mock_bitcoin, mock_coin):
        artist = Artist(
            mock_bitcoin, kind="interactive", theme="light", overlay=mock_coin
        )
        fig = artist.plot(from_date="2020-05-11")
        legend_names = [t.name for t in fig.data if t.name]
        assert any("SOL/USD" in name for name in legend_names)

    def test_without_overlay_unchanged(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        assert isinstance(fig, go.Figure)
