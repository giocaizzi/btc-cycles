"""static artist module"""

from __future__ import annotations

import copy
import datetime
from importlib.metadata import version
from typing import TYPE_CHECKING, Union

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

from .utils import ColorBar, ProgressLabels

if TYPE_CHECKING:
    from ..bitcoin import Bitcoin


class StaticArtist:
    """static artist

    Using `matpotlib` to plot statically.

    Args:
        bitcoin (Bitcoin): bitcoin object
        colorbar (ColorBar): color bar object
        theme (dict): a dictionary with the theme colors

    Attributes:
        bitcoin (Bitcoin): bitcoin object
        colorbar (ColorBar): color bar object
        theme (dict): a dictionary with the theme colors
    """

    def __init__(self, bitcoin: Bitcoin, theme: dict = "light"):
        self.bitcoin = copy.copy(bitcoin)
        self.colorbar = ColorBar(self.bitcoin)
        self.theme = theme

        # move to a colorbar method
        self._set_colors()

    def _set_colors(self):
        """set colors

        Create a new column in the DataFrame with the color
        """
        # TODO: this is a colorbar method
        self.bitcoin.prices["color"] = self.bitcoin.prices["distance_ath_perc"].apply(
            lambda x: mcolors.to_hex(self.colorbar.cmap(self.colorbar.norm(x)))
        )

    def plot(self, from_date: Union[str, datetime.datetime]):
        """plot

        Args:
            from_date (Union[str, datetime.datetime]): start date
        """
        # Create a polar subplot with extra space on the right
        self.f, self.axes = plt.subplots(
            1, 1, subplot_kw=dict(polar=True), figsize=(10, 10)
        )
        # Set background color
        self.f.set_facecolor(self.theme["background"])
        self.axes.set_facecolor(self.theme["background"])

        # Plot data
        self.add_data(from_date=from_date)

        # now point
        self.add_now()

        # halving
        self.add_halving()

        # # Plot ATHs
        self.add_aths()

        # plot cycle lows
        self.add_bottoms()

        # cycle low probability band
        self.add_low_probability_band()

        # format graph
        self.format_chart()

        # legend
        self.add_legend()

        # colorbar
        self.add_colorbar()

        # image creation date and copyright
        self.add_watermark()

        # return figure
        return self.f

    def add_watermark(self) -> None:
        """add watermark to plot"""
        try:
            # python ^3.10
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
            color="darkgrey",
        )

    def add_data(self, from_date: Union[str, datetime.datetime]) -> None:
        """add data to plot

        This method filters the data inplace.

        Args:
            from_date (Union[str, datetime.datetime]): start date
        """
        if from_date is not None:
            # filter data
            self.bitcoin.prices = self.bitcoin.prices[
                self.bitcoin.prices.Date >= from_date
            ]

        # plot data
        self.axes.scatter(
            self.bitcoin.prices["cycle_progress"] * 2 * np.pi,
            self.bitcoin.prices["Close"].to_numpy(),
            s=3,
            # markersize=1,
            c=self.bitcoin.prices["color"],
            zorder=9,
        )

    def format_chart(self) -> None:
        """format axes"""
        # Set y-axis to logarithmic scale
        self.axes.set_rscale("log")

        # Set direction (1 for clockwise, -1 for counterclockwise)
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
            1000000,
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
            if v >= self.bitcoin.prices.Close.min()
        )

        # set gridline color
        self.axes.grid(color=self.theme["grid"])

        # Set r gridlines
        self.axes.set_rgrids(
            grid_intervals[start_index:],
            labels=labels[start_index:],
        )

        # Set xticks and labels
        self.axes.set_xticks(
            np.linspace(0, 2 * np.pi, 4, endpoint=False),
        )
        self.axes.set_xticklabels(
            ProgressLabels(self.bitcoin).labels,
            fontsize=8,
        )

        # r label
        self.axes.set_rlabel_position(0)

        # y label
        self.axes.set_ylabel("Price\n(USD)", rotation=0, labelpad=15)
        self.axes.yaxis.set_label_coords(0.5, 1.03)

        # ticks params
        self.axes.tick_params(
            axis="both", which="major", pad=30, colors=self.theme["text"]
        )

        # edge color
        [spine.set_edgecolor("lightgrey") for spine in self.axes.spines.values()]

    def add_bottoms(self) -> None:
        """add cycle low points to plot"""
        lows = self.bitcoin.prices[self.bitcoin.prices["is_cycle_low"]]
        self.axes.scatter(
            lows["cycle_progress"] * 2 * np.pi,
            lows["Close"],
            marker="v",
            c=self.theme["low_marker"],
            s=40,
            zorder=10,
        )

    def add_low_probability_band(self, n_bins: int = 100) -> None:
        """Add a shaded radial band showing cycle low probability density.

        Uses KDE on historical cycle low progress values to estimate
        where in the cycle the bottom is most likely to occur.
        Draws thin radial strips with alpha proportional to the density.

        Args:
            n_bins (int): number of angular bins for the shading.
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

        # evaluate density on a grid
        grid = np.linspace(0, 1, n_bins + 1)
        centers = (grid[:-1] + grid[1:]) / 2
        density = kde(centers)

        # normalize density to [0, 1] for alpha mapping
        density_norm = density / density.max()

        # radial extent: full price range
        r_min = self.bitcoin.prices["Close"].min()
        r_max = 1_000_000

        # draw each strip
        color = mcolors.to_rgb(self.theme["low_marker"])
        max_alpha = 0.15
        bin_width = (grid[1] - grid[0]) * 2 * np.pi

        for i, (center, d) in enumerate(zip(centers, density_norm)):
            if d < 0.10:
                continue
            theta = center * 2 * np.pi
            self.axes.bar(
                theta,
                r_max - r_min,
                width=bin_width,
                bottom=r_min,
                color=color,
                alpha=d * max_alpha,
                zorder=1,
                edgecolor="none",
            )

    def add_aths(self) -> None:
        """add all time highs to plot"""
        aths = self.bitcoin.prices[self.bitcoin.prices["distance_ath_perc"] == 0]
        self.axes.scatter(
            aths["cycle_progress"] * 2 * np.pi,
            aths["Close"],
            marker="x",
            c=self.theme["ath_marker"],
            s=20,
            zorder=10,
        )

    def add_halving(self) -> None:
        """add halving to plot"""
        self.axes.vlines(
            0,
            self.bitcoin.prices["Close"].min(),
            1000000,
            color=self.theme["halving_line"],
            linewidth=3,
            zorder=0,
        )

    def add_now(self) -> None:
        self.axes.scatter(
            self.bitcoin.prices["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            self.bitcoin.prices["Close"].to_numpy()[-1],
            marker="D",
            c=self.bitcoin.prices["color"].to_numpy()[-1],
            s=50,
            zorder=8,
        )
        # now line
        self.axes.vlines(
            self.bitcoin.prices["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            self.bitcoin.prices["Close"].min(),
            self.bitcoin.prices["Close"].to_numpy()[-1],
            color=self.theme["now_line"],
            linestyle="--",
            zorder=8,
        )

    def add_legend(self) -> None:
        """add legend and title to plot using proxy artists."""
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch

        proxies = [
            Line2D([], [], marker="o", color="grey", markersize=3, linestyle="None"),
            Line2D(
                [],
                [],
                marker="D",
                color=self.bitcoin.prices["color"].to_numpy()[-1],
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
            Patch(facecolor=self.theme["low_marker"], alpha=0.15),
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
        """add colorbar to plot"""
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
