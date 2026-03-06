"""static artist module"""

import copy
import datetime
from importlib.metadata import version
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

from .utils import ColorBar, ProgressLabels

if TYPE_CHECKING:
    from ..core.bitcoin import Bitcoin

# chart constants
PRICE_UPPER_BOUND = 1_000_000
KDE_MAX_ALPHA = 0.15
KDE_DENSITY_THRESHOLD = 0.10


class StaticArtist:
    """Static polar chart artist using matplotlib.

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
    ) -> plt.Figure:
        """Render the polar chart.

        Args:
            from_date: Start date for filtering displayed data.

        Returns:
            The matplotlib figure.
        """
        self.f, self.axes = plt.subplots(
            1, 1, subplot_kw=dict(polar=True), figsize=(10, 10)
        )
        self.f.set_facecolor(self.theme["background"])
        self.axes.set_facecolor(self.theme["background"])

        self.add_data(from_date=from_date)
        self.add_now()
        self.add_halving()
        self.add_aths()
        self.add_bottoms()
        self.add_low_probability_band()
        self.format_chart()
        self.add_legend()
        self.add_colorbar()
        self.add_watermark()

        return self.f

    def add_watermark(self) -> None:
        """Add creation date and copyright watermark."""
        try:
            date = datetime.datetime.now(datetime.UTC)
        except AttributeError:
            date = datetime.datetime.utcnow()
        date_text = date.strftime("%Y-%m-%d %H:%M UTC")
        self.axes.annotate(
            (f"{date_text}\n© giocaizzi/btc-cycles : {version('btc-cycles')}"),
            xy=(0.5, 0.33),
            xycoords="axes fraction",
            textcoords="axes fraction",
            fontsize=8,
            ha="center",
            va="center",
            color=self.theme["watermark"],
        )

    def add_data(self, from_date: str | datetime.datetime | None) -> None:
        """Plot scatter data, filtering by from_date for display only.

        Args:
            from_date: Start date for filtering.
        """
        if from_date is not None:
            self.display_data = self.bitcoin.prices[
                self.bitcoin.prices.Date >= from_date
            ]
        else:
            self.display_data = self.bitcoin.prices

        self.axes.scatter(
            self.display_data["cycle_progress"] * 2 * np.pi,
            self.display_data["Close"].to_numpy(),
            s=3,
            c=self.display_data["color"],
            zorder=9,
        )

    def format_chart(self) -> None:
        """Format axes, gridlines, and tick labels."""
        self.axes.set_rscale("log")
        self.axes.set_theta_direction(-1)
        self.axes.set_theta_offset(np.pi / 2.0)

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

        self.axes.grid(color=self.theme["grid"])
        self.axes.set_rgrids(
            grid_intervals[start_index:],
            labels=labels[start_index:],
        )

        self.axes.set_xticks(
            np.linspace(0, 2 * np.pi, 4, endpoint=False),
        )
        self.axes.set_xticklabels(
            ProgressLabels(self.bitcoin).labels,
            fontsize=8,
        )

        self.axes.set_rlabel_position(0)

        self.axes.tick_params(
            axis="both", which="major", pad=35, colors=self.theme["text"]
        )

        for spine in self.axes.spines.values():
            spine.set_edgecolor("lightgrey")

    def add_bottoms(self) -> None:
        """Add cycle low markers to plot."""
        lows = self.display_data[self.display_data["is_cycle_low"]]
        self.axes.scatter(
            lows["cycle_progress"] * 2 * np.pi,
            lows["Close"],
            marker="v",
            c=self.theme["low_marker"],
            s=40,
            zorder=10,
        )

    def add_low_probability_band(self, n_bins: int = 100) -> None:
        """Add shaded radial band showing cycle low probability density.

        Uses KDE on historical cycle low progress values to estimate
        where in the cycle the bottom is most likely to occur.

        Args:
            n_bins: Number of angular bins for the shading.
        """
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

        color = mcolors.to_rgb(self.theme["low_marker"])
        bin_width = (grid[1] - grid[0]) * 2 * np.pi

        for center, d in zip(centers, density_norm):
            if d < KDE_DENSITY_THRESHOLD:
                continue
            theta = center * 2 * np.pi
            self.axes.bar(
                theta,
                r_max - r_min,
                width=bin_width,
                bottom=r_min,
                color=color,
                alpha=d * KDE_MAX_ALPHA,
                zorder=1,
                edgecolor="none",
            )

    def add_aths(self) -> None:
        """Add all-time high markers to plot."""
        aths = self.display_data[self.display_data["distance_ath_perc"] == 0]
        self.axes.scatter(
            aths["cycle_progress"] * 2 * np.pi,
            aths["Close"],
            marker="x",
            c=self.theme["ath_marker"],
            s=20,
            zorder=10,
        )

    def add_halving(self) -> None:
        """Add halving day vertical line."""
        self.axes.vlines(
            0,
            self.display_data["Close"].min(),
            PRICE_UPPER_BOUND,
            color=self.theme["halving_line"],
            linewidth=3,
            zorder=0,
        )

    def add_now(self) -> None:
        """Add current price marker and vertical line."""
        self.axes.scatter(
            self.display_data["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            self.display_data["Close"].to_numpy()[-1],
            marker="D",
            c=self.display_data["color"].to_numpy()[-1],
            s=50,
            zorder=8,
        )
        self.axes.vlines(
            self.display_data["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            self.display_data["Close"].min(),
            self.display_data["Close"].to_numpy()[-1],
            color=self.theme["now_line"],
            linestyle="--",
            zorder=8,
        )

    def add_legend(self) -> None:
        """Add legend and title using proxy artists."""
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch

        proxies = [
            Line2D([], [], marker="o", color="grey", markersize=3, linestyle="None"),
            Line2D(
                [],
                [],
                marker="D",
                color=self.display_data["color"].to_numpy()[-1],
                markersize=7,
                linestyle="None",
            ),
            Line2D([], [], color=self.theme["now_line"], linestyle="--"),
            Line2D([], [], color=self.theme["halving_line"], linewidth=3),
            Line2D(
                [],
                [],
                marker="x",
                color=self.theme["ath_marker"],
                markersize=7,
                linestyle="None",
            ),
            Line2D(
                [],
                [],
                marker="v",
                color=self.theme["low_marker"],
                markersize=7,
                linestyle="None",
            ),
            Patch(facecolor=self.theme["low_marker"], alpha=KDE_MAX_ALPHA),
        ]
        labels = [
            "BTC/USD",
            "Today BTC/USD Close",
            "Today",
            "Halving day",
            "All time high (ATH)",
            "Cycle low",
            "Cycle low probability",
        ]

        legend = self.f.legend(
            proxies,
            labels,
            loc="upper left",
            bbox_to_anchor=(0.01, 0.97),
            fontsize=10,
            title="$\\bf{BTCUSD\\ price\\ halving\\ cycles}$",
            title_fontsize="13",
            frameon=False,
        )
        for text in legend.get_texts():
            text.set_color(self.theme["text"])
        legend.get_title().set_color(self.theme["text"])

    def add_colorbar(self) -> None:
        """Add distance-from-ATH colorbar."""
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes

        sm = plt.cm.ScalarMappable(cmap=self.colorbar.cmap, norm=self.colorbar.norm)
        inset_ax = inset_axes(
            self.axes,
            width="2.5%",
            height="25%",
            bbox_to_anchor=(0, 0, 0.95, 1.05),
            bbox_transform=self.axes.transAxes,
            borderpad=0,
        )
        cbar = self.f.colorbar(
            sm,
            cax=inset_ax,
            orientation="vertical",
            ticks=[0, -0.2, -0.4, -0.6, -0.8, -1],
        )
        cbar.ax.set_yticklabels(
            ["ATH", "-20%", "-40%", "-60%", "-80%", "-100%"],
            color=self.theme["text"],
        )
        inset_ax.set_title(
            "Distance from ATH",
            fontdict={"fontweight": "bold", "color": self.theme["text"]},
            pad=10,
        )
