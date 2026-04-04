"""artist module"""

import datetime
import warnings
from typing import TYPE_CHECKING, Literal, Union

from .interactive import InteractiveArtist
from .static import StaticArtist

if TYPE_CHECKING:
    import matplotlib.figure
    import plotly.graph_objects as go

    from ..core.bitcoin import Bitcoin
    from ..core.coin import Coin

THEMES: dict[str, dict[str, str]] = {
    "light": {
        "background": "white",
        "text": "black",
        "grid": "darkgrey",
        "now_line": "darkgrey",
        "halving_line": "lightgreen",
        "ath_marker": "black",
        "low_marker": "red",
        "watermark": "darkgrey",
    },
    "dark": {
        "background": "black",
        "text": "white",
        "grid": "lightgrey",
        "now_line": "lightgrey",
        "halving_line": "lightgreen",
        "ath_marker": "white",
        "low_marker": "red",
        "watermark": "lightgrey",
    },
}


class Artist:
    """Artist for plotting.

    Args:
        bitcoin: Bitcoin object with price and halving data.
        kind: Type of artist ("static" or "interactive").
        theme: Theme colors — a preset name or a dict of overrides.
        overlay: Optional alt-coin to overlay on the chart.

    Raises:
        ValueError: If kind or theme is invalid.
    """

    def __init__(
        self,
        bitcoin: "Bitcoin",
        kind: Literal["static", "interactive"],
        theme: Literal["light", "dark"] | dict[str, str],
        overlay: "Coin | None" = None,
    ):
        self.theme: dict[str, str] = self.__unwrap_theme(theme)

        if kind == "static":
            self._kind = kind
            self.artist: StaticArtist | InteractiveArtist = StaticArtist(
                bitcoin, theme=self.theme, overlay=overlay
            )
        elif kind == "interactive":
            self._kind = kind
            self.artist = InteractiveArtist(bitcoin, theme=self.theme, overlay=overlay)
        else:
            raise ValueError("kind must be 'static' or 'interactive'")

    def __unwrap_theme(
        self,
        theme: Literal["light", "dark"] | dict[str, str],
    ) -> dict[str, str]:
        """Resolve theme to a concrete dict of color values."""
        if isinstance(theme, str) and theme in THEMES:
            return THEMES[theme].copy()
        elif isinstance(theme, dict):
            if set(theme.keys()) == set(THEMES["light"].keys()):
                return theme.copy()
            else:
                resolved = THEMES["light"].copy()
                for key in theme:
                    if key not in THEMES["light"]:
                        warnings.warn(
                            f"Theme key '{key}' not recognized. Ignoring it.",
                            stacklevel=3,
                        )
                    else:
                        resolved[key] = theme[key]
                return resolved
        else:
            raise ValueError(
                "theme must be 'light', 'dark' or a dictionary with the theme colors"
            )

    @property
    def kind(self) -> str:
        return self._kind

    def plot(
        self,
        from_date: str | datetime.datetime | None = None,
    ) -> Union["matplotlib.figure.Figure", "go.Figure"]:
        """Delegate to the underlying artist's plot method.

        Args:
            from_date: Start date for filtering displayed data.

        Returns:
            A matplotlib Figure (static) or Plotly Figure (interactive).
        """
        return self.artist.plot(from_date=from_date)
