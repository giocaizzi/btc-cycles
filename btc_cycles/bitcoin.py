"""bitcoin module"""

from .prices import Prices
from .halvings import get_halving_data
from .artists import Artist


# TODO: for now its assuming that the
#  cycle length is the same as previous


class Bitcoin:
    """Bitcoin

    Attributes:
        prices (DataFrame): bitcoin prices
    """

    def __init__(self):
        # get price data
        self.prices = Prices().data
        # predicted halving date

    def plot(self, kind="static", **kwargs):
        """plot

        Args:
            kind (str, optional): plot kind. Defaults to "static".
            \\*\\*kwargs: additional keyword arguments to plotting method
        """
        Artist(kind, self).plot(**kwargs)
