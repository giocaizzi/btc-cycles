"""artist module"""

from __future__ import annotations
from typing import Union, Literal

from .static import StaticArtist


class Artist:
    """Artist for plotting"""

    def __init__(self, kind: str = "static", bitcoin: Bitcoin = None, theme: Union[Literal["light", "dark"], dict] = "light"):
        """Artist

        Artist for plotting, either static or dynamic.
        Static artist uses `matplotlib` and dynamic artist uses `plotly`.

        Args:
            kind (str, optional): _description_. Defaults to "static".
            bitcoin (Bitcoin, optional): _description_. Defaults to None.
            theme (Union[Literal["light", "dark"], dict], optional): _description_. Defaults to "light".

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        self.artist = None
        if kind == "static":
            self._kind = kind
            self.artist = StaticArtist(bitcoin,theme=theme)
        elif kind == "dynamic":
            # TODO: implement dynamic artist (plotly)
            raise NotImplementedError
        else:
            raise ValueError("kind must be 'static' or 'dynamic'")

    @property
    def kind(self) -> str:
        return self._kind

    def plot(self, **kwargs):
        """wrapper for plot method of artist

        Args:
            \\*\\*kwargs: keyword arguments to plotting method
        """
        return self.artist.plot(**kwargs)
