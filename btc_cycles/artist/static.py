"""static artist module"""

from __future__ import annotations

import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from .utils import ColorBar, ProgressLabels


class StaticArtist:
    """static artist

    Using `matpotlib` to plot statically.

    Args:
        bitcoin (Bitcoin): bitcoin object
        colorbar (ColorBar): color bar object
    """

    def __init__(self, bitcoin: Bitcoin):
        self.bitcoin = bitcoin.copy()
        self.colorbar = ColorBar(self.bitcoin)

    def _set_colors(self):
        """set colors

        Create a new column in the DataFrame with the color
        """
        self.bitcoin.prices["color"] = self.bitcoin.prices["distance_ath_perc"].apply(
            lambda x: mcolors.to_hex(self.colorbar.cmap(self.colorbar.norm(x)))
        )

    def plot(self):
        """plot"""
        pass
