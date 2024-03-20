"""artist module"""

from ..bitcoin import Bitcoin
from .static_artist import StaticArtist


class Artist:
    """Artist for plotting"""

    def __init__(self, kind: str = "static", bitcoin: Bitcoin = None):
        """_summary_

        Args:
            kind (str, optional): _description_. Defaults to "static".
            bitcoin (Bitcoin, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        self.artist = None
        if kind == "static":
            self._kind = kind
            self.artist = StaticArtist(bitcoin)
        elif kind == "dynamic":
            # TODO: implement dynamic artist (plotly)
            raise NotImplementedError
        else:
            raise ValueError("kind must be 'static' or 'dynamic'")

    @property
    def kind(self) -> str:
        return self._kind

    def plot(self):
        """wrapper for plot method of artist"""
        self.artist.plot()
