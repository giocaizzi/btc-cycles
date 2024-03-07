"""static artist module"""

from ..bitcoin import Bitcoin


class StaticArtist:
    """static artist

    Using `matpotlib` to plot statically.
    """

    def __init__(self, bitcoin: Bitcoin):
        self.bitcoin = bitcoin

    def plot(self):
        """plot static"""
        pass
