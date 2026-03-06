"""test artist theme handling — behaviour tests"""

import pytest

from btc_cycles.artist.artist import THEMES, Artist


class TestThemeResolution:
    def test_light_theme_applies(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="static", theme="light")
        assert artist.theme["background"] == "white"

    def test_dark_theme_applies(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="static", theme="dark")
        assert artist.theme["background"] == "black"

    def test_partial_override_changes_only_specified_key(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="static", theme={"now_line": "red"})
        assert artist.theme["now_line"] == "red"
        assert artist.theme["background"] == "white"

    def test_partial_override_does_not_mutate_global_themes(self, mock_bitcoin):
        original = THEMES["light"].copy()
        Artist(mock_bitcoin, kind="static", theme={"now_line": "red"})
        assert THEMES["light"] == original

    def test_repeated_overrides_are_independent(self, mock_bitcoin):
        """Two artists with different overrides don't share state."""
        a1 = Artist(mock_bitcoin, kind="static", theme={"now_line": "red"})
        a2 = Artist(mock_bitcoin, kind="static", theme={"now_line": "blue"})
        assert a1.theme["now_line"] == "red"
        assert a2.theme["now_line"] == "blue"

    def test_full_dict_override_accepted(self, mock_bitcoin):
        """A dict with all theme keys is accepted as-is."""
        custom = {k: "purple" for k in THEMES["light"]}
        artist = Artist(mock_bitcoin, kind="static", theme=custom)
        assert all(v == "purple" for v in artist.theme.values())

    def test_unknown_key_warns(self, mock_bitcoin):
        with pytest.warns(UserWarning, match="not recognized"):
            Artist(mock_bitcoin, kind="static", theme={"bogus_key": "red"})

    def test_invalid_string_raises(self, mock_bitcoin):
        with pytest.raises(ValueError):
            Artist(mock_bitcoin, kind="static", theme="neon")

    def test_interactive_kind_accepted(self, mock_bitcoin):
        artist = Artist(mock_bitcoin, kind="interactive", theme="light")
        assert artist.kind == "interactive"

    def test_invalid_kind_raises(self, mock_bitcoin):
        with pytest.raises(ValueError):
            Artist(mock_bitcoin, kind="invalid", theme="light")
