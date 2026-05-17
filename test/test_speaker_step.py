"""Tests for :class:`RemoveSpeakerStep`."""

from mkvlab.fix_cc.steps import RemoveSpeakerStep

from .helpers import make_subtitle


def _apply(text):
    return RemoveSpeakerStep().propose(make_subtitle(text)).proposed.text


class TestRemoveSpeakerStep:
    def test_uppercase_name(self):
        assert _apply("PERSON: How are you?") == "How are you?"

    def test_name_with_dot(self):
        assert _apply("MRS. WOLOWITZ: How are you?") == "How are you?"

    def test_name_with_apostrophe(self):
        assert _apply("O'BRIEN: How are you?") == "How are you?"

    def test_hyphenated_name(self):
        assert _apply("MARY-ANN: How are you?") == "How are you?"

    def test_capitalised_name(self):
        assert _apply("Person: How are you?") == "How are you?"

    def test_lowercase_name(self):
        assert _apply("person: how are you?") == "how are you?"

    def test_padded_name(self):
        assert _apply(" person : how are you?") == "how are you?"

    def test_multiline_strips_each_line(self):
        text = "SHELDON: She's not that intelligent.\nLEONARD: She fixed your equation."
        expected = "She's not that intelligent.\nShe fixed your equation."
        assert _apply(text) == expected

    def test_drops_lines_left_empty(self):
        # When a line is only a speaker tag the empty result is discarded.
        assert _apply("BACKGROUND:\nHello") == "Hello"

    def test_lines_without_colon_untouched(self):
        assert _apply("Hello world\n-Already dashed") == "Hello world\n-Already dashed"
