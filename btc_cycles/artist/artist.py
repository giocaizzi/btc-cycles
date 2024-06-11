"""artist module"""

from __future__ import annotations
import warnings
from typing import Union, Literal

from .static import StaticArtist

THEMES = {
    "light": {
        "background": "white",
        "text": "black",
        "grid": "darkgrey",
        "now_line": "darkgrey",
        "halving_line": "lightgreen",
        "ath_marker": "black",
    },
    "dark": {
        "background": "black",
        "text": "white",
        "grid": "lightgrey",
        "now_line": "lightgrey",
        "halving_line": "lightgreen",
        "ath_marker": "white",
    },
}


class Artist:
    """Artist for plotting"""

    def __init__(
        self,
        bitcoin: Bitcoin,
        kind: Literal["static", "dynamic"],
        theme: Union[Literal["light", "dark"], dict],
    ):
        """Artist

        Artist for plotting, either static or dynamic.
        Static artist uses `matplotlib` and dynamic artist uses `plotly`.

        Arguments:
            bitcoin (Bitcoin): bitcoin object.
            kind (Literal["static", "dynamic"], optional): type of artist.
                Defaults to "static".
            theme (Union[Literal["light", "dark"], dict], optional): theme colors.
                Defaults to "light".


        Attributes:
            artist (StaticArtist): artist for plotting
            theme (dict): theme colors

        Raises:
            NotImplementedError: _description_
            ValueError: _description_
        """
        self.artist = None
        self.theme = None

        # unwrap theme
        self.__unwrap_theme(theme)

        # set artist
        if kind == "static":
            self._kind = kind
            self.artist = StaticArtist(bitcoin, theme=self.theme)
        elif kind == "dynamic":
            # TODO: implement dynamic artist (plotly)
            raise NotImplementedError
        else:
            raise ValueError("kind must be 'static' or 'dynamic'")

    def __unwrap_theme(
        self,
        theme: Union[Literal["light", "dark"], dict],
    ) -> None:
        """unwrap theme

        Args:
            theme (Union[Literal["light", "dark"], dict], optional): theme colors.
        """
        if isinstance(theme, str) and theme in THEMES:
            self.theme = THEMES[theme]
        # if dict, check if it has the right keys
        elif isinstance(theme, dict):
            # if theme is a dictionary with the same keys as the default themes
            # then use it
            if set(theme.keys()) == set(THEMES["light"].keys()):
                self.theme = theme
            else:
                # else use the light theme and update the keys
                for key in theme.keys():
                    self.theme = THEMES["light"]
                    if key not in THEMES["light"]:
                        # warning message
                        warnings.warn(f"Theme key '{key}' not recognized. Ignoring it.")
                    else:
                        self.theme[key] = theme[key]
        else:
            raise ValueError(
                "theme must be 'light', 'dark' or a dictionary with the theme colors"
            )

    @property
    def kind(self) -> str:
        return self._kind

    def plot(self, **kwargs):
        """wrapper for plot method of artist

        Args:
            \\*\\*kwargs: keyword arguments to plotting method
        """
        return self.artist.plot(**kwargs)
