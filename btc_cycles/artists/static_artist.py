"""static artist module"""

from __future__ import annotations


class StaticArtist:
    """static artist

    Using `matpotlib` to plot statically.

    Args:
        bitcoin (Bitcoin): bitcoin object
    """

    def __init__(self, bitcoin: Bitcoin):
        self.bitcoin = bitcoin

    def plot(self):
        """plot"""
        pass
