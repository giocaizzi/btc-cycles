"""test interactive artist"""

import plotly.graph_objects as go

from btc_cycles.artist.artist import Artist


class TestInteractiveArtist:
    def test_returns_plotly_figure(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        assert isinstance(fig, go.Figure)

    def test_has_data_traces(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        # should have at least: data scatter, halving line, now line, now marker
        assert len(fig.data) >= 4

    def test_log_radial_axis(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        assert fig.layout.polar.radialaxis.type == "log"

    def test_dark_theme_background(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="dark")
        fig = artist.plot(from_date="2020-05-11")
        assert fig.layout.paper_bgcolor == "black"

    def test_from_date_none(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date=None)
        assert isinstance(fig, go.Figure)

    def test_to_html(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        fig = artist.plot(from_date="2020-05-11")
        html = fig.to_html()
        assert "<div" in html
        assert "plotly" in html.lower() or "Plotly" in html
