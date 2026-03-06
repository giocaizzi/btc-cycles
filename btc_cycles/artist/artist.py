"""artist module"""

import datetime
import warnings
from typing import TYPE_CHECKING, Literal

from .static import StaticArtist

if TYPE_CHECKING:
    import matplotlib.figure

    from ..core.bitcoin import Bitcoin

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
        kind: Type of artist ("static" or "dynamic").
        theme: Theme colors — a preset name or a dict of overrides.

    Raises:
        NotImplementedError: If kind is "dynamic".
        ValueError: If kind or theme is invalid.
    """

    def __init__(
        self,
        bitcoin: "Bitcoin",
        kind: Literal["static", "dynamic"],
        theme: Literal["light", "dark"] | dict[str, str],
    ):
        self.theme: dict[str, str] = self.__unwrap_theme(theme)

        if kind == "static":
            self._kind = kind
            self.artist: StaticArtist = StaticArtist(bitcoin, theme=self.theme)
        elif kind == "dynamic":
            raise NotImplementedError
        else:
            raise ValueError("kind must be 'static' or 'dynamic'")

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
    ) -> "matplotlib.figure.Figure":
        """Delegate to the underlying artist's plot method.

        Args:
            from_date: Start date for filtering displayed data.

        Returns:
            The matplotlib figure.
        """
        return self.artist.plot(from_date=from_date)
