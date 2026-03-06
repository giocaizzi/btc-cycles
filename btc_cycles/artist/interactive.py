"""interactive artist module"""

import copy
import datetime
from importlib.metadata import version
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

from .utils import ColorBar, ProgressLabels

if TYPE_CHECKING:
    from ..core.bitcoin import Bitcoin

# chart constants (shared with static)
PRICE_UPPER_BOUND = 1_000_000
KDE_MAX_ALPHA = 0.15
KDE_DENSITY_THRESHOLD = 0.10


class InteractiveArtist:
    """Interactive polar chart artist using Plotly.

    Args:
        bitcoin: Bitcoin object with price and halving data.
        theme: Theme color dictionary.
    """

    def __init__(self, bitcoin: "Bitcoin", theme: dict[str, str]):
        self.bitcoin = copy.deepcopy(bitcoin)
        self.colorbar = ColorBar(self.bitcoin)
        self.theme = theme

        self._set_colors()

    def _set_colors(self) -> None:
        """Create a color column based on distance from ATH."""
        self.bitcoin.prices["color"] = self.bitcoin.prices["distance_ath_perc"].apply(
            lambda x: mcolors.to_hex(self.colorbar.cmap(self.colorbar.norm(x)))
        )

    def plot(
        self,
        from_date: str | datetime.datetime | None,
    ) -> go.Figure:
        """Render the interactive polar chart.

        Args:
            from_date: Start date for filtering displayed data.

        Returns:
            The Plotly figure.
        """
        if from_date is not None:
            self.display_data = self.bitcoin.prices[
                self.bitcoin.prices.Date >= from_date
            ]
        else:
            self.display_data = self.bitcoin.prices

        self.fig = go.Figure()

        self._add_low_probability_band()
        self._add_data()
        self._add_halving()
        self._add_now()
        self._add_aths()
        self._add_bottoms()
        self._add_legend()
        self._format_chart()

        return self.fig

    def _add_data(self) -> None:
        """Add scatter data trace."""
        theta_deg = self.display_data["cycle_progress"] * 360

        hover_text = [
            f"Date: {row.Date.strftime('%Y-%m-%d')}<br>"
            f"Price: ${row.Close:,.2f}<br>"
            f"Cycle: {int(row.cycle_id)}<br>"
            f"Progress: {row.cycle_progress:.1%}<br>"
            f"ATH distance: {row.distance_ath_perc:.1%}"
            for _, row in self.display_data.iterrows()
        ]

        self.fig.add_trace(
            go.Scatterpolar(
                r=self.display_data["Close"],
                theta=theta_deg,
                mode="markers",
                marker=dict(
                    size=3,
                    color=self.display_data["color"].tolist(),
                ),
                text=hover_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

    def _add_now(self) -> None:
        """Add current price marker and radial line."""
        last = self.display_data.iloc[-1]
        theta_now = last["cycle_progress"] * 360

        # radial line from min to current price
        r_min = self.display_data["Close"].min()
        self.fig.add_trace(
            go.Scatterpolar(
                r=[r_min, last["Close"]],
                theta=[theta_now, theta_now],
                mode="lines",
                line=dict(
                    color=self.theme["now_line"],
                    dash="dash",
                    width=1,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # diamond marker
        self.fig.add_trace(
            go.Scatterpolar(
                r=[last["Close"]],
                theta=[theta_now],
                mode="markers",
                marker=dict(
                    size=10,
                    color=last["color"],
                    symbol="diamond",
                ),
                text=[
                    f"Today<br>"
                    f"Date: {last['Date'].strftime('%Y-%m-%d')}<br>"
                    f"Price: ${last['Close']:,.2f}"
                ],
                hoverinfo="text",
                showlegend=False,
            )
        )

    def _add_halving(self) -> None:
        """Add halving day radial line."""
        r_min = self.display_data["Close"].min()
        self.fig.add_trace(
            go.Scatterpolar(
                r=[r_min, PRICE_UPPER_BOUND],
                theta=[0, 0],
                mode="lines",
                line=dict(
                    color=self.theme["halving_line"],
                    width=3,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    def _add_aths(self) -> None:
        """Add all-time high markers."""
        aths = self.display_data[self.display_data["distance_ath_perc"] == 0]
        if aths.empty:
            return

        hover_text = [
            f"ATH<br>Date: {row.Date.strftime('%Y-%m-%d')}<br>Price: ${row.Close:,.2f}"
            for _, row in aths.iterrows()
        ]

        self.fig.add_trace(
            go.Scatterpolar(
                r=aths["Close"],
                theta=aths["cycle_progress"] * 360,
                mode="markers",
                marker=dict(
                    size=6,
                    color=self.theme["ath_marker"],
                    symbol="x",
                ),
                text=hover_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

    def _add_bottoms(self) -> None:
        """Add cycle low markers."""
        lows = self.display_data[self.display_data["is_cycle_low"]]
        if lows.empty:
            return

        hover_text = [
            f"Cycle Low<br>Date: {row.Date.strftime('%Y-%m-%d')}<br>"
            f"Price: ${row.Close:,.2f}<br>"
            f"ATH distance: {row.distance_ath_perc:.1%}"
            for _, row in lows.iterrows()
        ]

        self.fig.add_trace(
            go.Scatterpolar(
                r=lows["Close"],
                theta=lows["cycle_progress"] * 360,
                mode="markers",
                marker=dict(
                    size=8,
                    color=self.theme["low_marker"],
                    symbol="triangle-down",
                ),
                text=hover_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

    def _add_low_probability_band(self, n_bins: int = 100) -> None:
        """Add shaded radial band showing cycle low probability density."""
        lows = self.bitcoin.prices[self.bitcoin.prices["is_cycle_low"]]
        if len(lows) < 2:
            return

        progress_values = lows["cycle_progress"].values

        # exclude outliers using IQR
        q1, q3 = np.percentile(progress_values, [25, 75])
        iqr = q3 - q1
        mask = (progress_values >= q1 - 1.5 * iqr) & (progress_values <= q3 + 1.5 * iqr)
        filtered = progress_values[mask]
        if len(filtered) < 2:
            return

        kde = gaussian_kde(filtered)

        grid = np.linspace(0, 1, n_bins + 1)
        centers = (grid[:-1] + grid[1:]) / 2
        density = kde(centers)
        density_norm = density / density.max()

        r_min = self.display_data["Close"].min()
        r_max = PRICE_UPPER_BOUND

        color_rgb = mcolors.to_rgb(self.theme["low_marker"])
        r_int, g_int, b_int = [int(c * 255) for c in color_rgb]
        bin_width_deg = (grid[1] - grid[0]) * 360

        for center, d in zip(centers, density_norm):
            if d < KDE_DENSITY_THRESHOLD:
                continue
            theta_center = center * 360
            alpha = d * KDE_MAX_ALPHA

            theta_left = theta_center - bin_width_deg / 2
            theta_right = theta_center + bin_width_deg / 2
            self.fig.add_trace(
                go.Scatterpolar(
                    r=[r_min, r_max, r_max, r_min, r_min],
                    theta=[
                        theta_left,
                        theta_left,
                        theta_right,
                        theta_right,
                        theta_left,
                    ],
                    mode="lines",
                    fill="toself",
                    fillcolor=f"rgba({r_int},{g_int},{b_int},{alpha})",
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    def _add_legend(self) -> None:
        """Add proxy legend traces matching the static chart's legend order."""
        last = self.display_data.iloc[-1]
        color_rgb = mcolors.to_rgb(self.theme["low_marker"])
        r_int, g_int, b_int = [int(c * 255) for c in color_rgb]

        # same order as static: BTC/USD, Today Close, Today, Halving,
        # ATH, Cycle low, Cycle low probability
        proxy_traces = [
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="markers",
                marker=dict(size=5, color="grey"),
                name="BTC/USD",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="markers",
                marker=dict(size=8, color=last["color"], symbol="diamond"),
                name="Today BTC/USD Close",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="lines",
                line=dict(color=self.theme["now_line"], dash="dash"),
                name="Today",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="lines",
                line=dict(color=self.theme["halving_line"], width=3),
                name="Halving day",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="markers",
                marker=dict(size=7, color=self.theme["ath_marker"], symbol="x"),
                name="All time high (ATH)",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="markers",
                marker=dict(
                    size=7, color=self.theme["low_marker"], symbol="triangle-down"
                ),
                name="Cycle low",
            ),
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="lines",
                fill="toself",
                fillcolor=f"rgba({r_int},{g_int},{b_int},{KDE_MAX_ALPHA})",
                line=dict(width=0),
                name="Cycle low probability",
            ),
        ]
        for trace in proxy_traces:
            self.fig.add_trace(trace)

    def _build_angular_labels(self) -> list[str]:
        """Build angular axis date labels from ProgressLabels, converting to HTML."""
        import re

        pl = ProgressLabels(self.bitcoin)
        labels = []
        for progress in [0.00, 0.25, 0.50, 0.75]:
            raw = pl.labels.loc[progress]
            # convert matplotlib LaTeX bold to HTML bold
            converted = re.sub(
                r"\$\\bf\{([^}]+)\}\$",
                r"<b>\1</b>",
                raw,
            )
            converted = converted.replace("\n", "<br>")
            labels.append(converted)
        return labels

    def _format_chart(self) -> None:
        """Format layout, axes, and styling."""
        bg = self.theme["background"]
        text_color = self.theme["text"]

        # build tick labels for the r-axis (log scale)
        grid_intervals = [
            0.001,
            0.01,
            0.1,
            1,
            10,
            100,
            1000,
            10000,
            100000,
            PRICE_UPPER_BOUND,
        ]
        labels = [
            "0.001",
            "0.01",
            "0.1",
            "1",
            "10",
            "100",
            "1k",
            "10k",
            "100k",
            "1M",
        ]

        start_index = next(
            i
            for i, v in enumerate(grid_intervals)
            if v >= self.display_data.Close.min()
        )

        # build watermark text
        try:
            date = datetime.datetime.now(datetime.UTC)
        except AttributeError:
            date = datetime.datetime.utcnow()
        date_text = date.strftime("%Y-%m-%d %H:%M UTC")
        watermark = f"{date_text} | btc-cycles : {version('btc-cycles')}"

        # distance-from-ATH colorbar via invisible trace
        cmap = plt.get_cmap("cool")
        plotly_colorscale = [
            [i / 255, mcolors.to_hex(cmap(i / 255))] for i in range(256)
        ]

        self.fig.add_trace(
            go.Scatterpolar(
                r=[None],
                theta=[None],
                mode="markers",
                marker=dict(
                    size=0,
                    color=[0],
                    colorscale=plotly_colorscale,
                    cmin=self.bitcoin.prices["distance_ath_perc"].min(),
                    cmax=0,
                    colorbar=dict(
                        title=dict(text="Distance from ATH"),
                        tickvals=[0, -0.2, -0.4, -0.6, -0.8, -1.0],
                        ticktext=["ATH", "-20%", "-40%", "-60%", "-80%", "-100%"],
                        len=0.25,
                        x=0.95,
                        y=0.92,
                        yanchor="top",
                    ),
                    showscale=True,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        self.fig.update_layout(
            polar=dict(
                bgcolor=bg,
                domain=dict(x=[0.1, 0.9], y=[0.05, 0.95]),
                radialaxis=dict(
                    type="log",
                    range=[
                        np.log10(self.display_data["Close"].min()),
                        np.log10(PRICE_UPPER_BOUND),
                    ],
                    tickvals=grid_intervals[start_index:],
                    ticktext=labels[start_index:],
                    gridcolor=self.theme["grid"],
                    color=text_color,
                    angle=90,
                    tickangle=90,
                ),
                angularaxis=dict(
                    direction="clockwise",
                    rotation=90,
                    tickvals=[0, 90, 180, 270],
                    ticktext=self._build_angular_labels(),
                    gridcolor=self.theme["grid"],
                    color=text_color,
                ),
            ),
            paper_bgcolor=bg,
            plot_bgcolor=bg,
            font=dict(color=text_color),
            title=dict(
                text="BTCUSD price halving cycles",
                font=dict(size=16, color=text_color),
                x=0.5,
            ),
            legend=dict(
                x=0.0,
                y=1.0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_color),
            ),
            margin=dict(l=100, r=80, t=60, b=60),
            annotations=[
                dict(
                    text=watermark,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.02,
                    showarrow=False,
                    font=dict(size=10, color=self.theme["watermark"]),
                )
            ],
            width=1000,
            height=1000,
        )
