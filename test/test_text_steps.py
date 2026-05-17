"""Tests for the text-regex steps (parentheses, brackets, etc.).

Each step's job is a single substitution on the subtitle text. We test the
*proposed text* against curated inputs.
"""

import pytest

from mkvlab.fix_cc import Confidence
from mkvlab.fix_cc.steps import (
    FixDoubleHyphensStep,
    FixLengthyEllipsisStep,
    RemoveBracketsStep,
    RemoveCurlyBracketsStep,
    RemoveHashStep,
    RemoveMusicSignStep,
    RemoveParenthesesStep,
)

from .helpers import make_subtitle


def _apply(step, text):
    return step.propose(make_subtitle(text)).proposed.text


# ---------------------------------------------------------------------------
# Parentheses
# ---------------------------------------------------------------------------


class TestRemoveParenthesesStep:
    step = RemoveParenthesesStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("(Hello) World", " World"),
            ("( Hello ) World", " World"),
            ("Hello (whispering) world", "Hello  world"),
            ("Hello ( whispering ) world", "Hello  world"),
            ("Hello (World)", "Hello "),
            ("( )", ""),
            ("()", ""),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected

    def test_is_ambiguous(self):
        assert (
            self.step.propose(make_subtitle("(x)")).confidence is Confidence.AMBIGUOUS
        )

    def test_multiline(self):
        text = '(2001: A SPACE ODYSSEY\'S "MAIN TITLE"\nPLAYS OVER SPEAKERS)'
        assert _apply(self.step, text) == ""

    def test_multiline_partial(self):
        assert (
            _apply(self.step, "Hello (this spans\ntwo lines) world.") == "Hello  world."
        )


# ---------------------------------------------------------------------------
# Brackets
# ---------------------------------------------------------------------------


class TestRemoveBracketsStep:
    step = RemoveBracketsStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("[Hello] World", " World"),
            ("[ Hello ] World", " World"),
            ("Hello [whispering] world", "Hello  world"),
            ("Hello [ whispering ] world", "Hello  world"),
            ("Hello [World]", "Hello "),
            ("[ ]", ""),
            ("[]", ""),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected

    def test_multiline(self):
        assert _apply(self.step, "[DRAMATIC MUSIC\nPLAYING]") == ""

    def test_multiline_partial(self):
        assert (
            _apply(self.step, "Hello [this spans\ntwo lines] world.") == "Hello  world."
        )


# ---------------------------------------------------------------------------
# Curly brackets
# ---------------------------------------------------------------------------


class TestRemoveCurlyBracketsStep:
    step = RemoveCurlyBracketsStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("{Hello} World", " World"),
            ("{ Hello } World", " World"),
            ("Hello {whispering} world", "Hello  world"),
            ("Hello {World}", "Hello "),
            ("{ }", ""),
            ("{}", ""),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected

    def test_multiline(self):
        assert _apply(self.step, "{DRAMATIC MUSIC\nPLAYING}") == ""


# ---------------------------------------------------------------------------
# Hash
# ---------------------------------------------------------------------------


class TestRemoveHashStep:
    step = RemoveHashStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("#Hello# World", " World"),
            ("# Hello # World", " World"),
            ("Hello #whispering# world", "Hello  world"),
            ("Hello #World#", "Hello "),
            ("# #", ""),
            ("##", ""),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected


# ---------------------------------------------------------------------------
# Music sign
# ---------------------------------------------------------------------------


class TestRemoveMusicSignStep:
    step = RemoveMusicSignStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("♪ Hello ♪ world", " Hello  world"),
            ("♪Hello♪ world", "Hello world"),
            ("Hello ♪ singing ♪ world", "Hello  singing  world"),
            ("Hello ♪singing♪ world", "Hello singing world"),
            ("Hello ♪ world ♪", "Hello  world "),
            ("Hello ♪world♪", "Hello world"),
            ("♪ ♪", " "),
            ("♪♪", ""),
            ("♪", ""),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected


# ---------------------------------------------------------------------------
# Double hyphens
# ---------------------------------------------------------------------------


class TestFixDoubleHyphensStep:
    step = FixDoubleHyphensStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("It wasn't--", "It wasn't\u2014"),
            ("It was not--", "It was not\u2014"),
            ("Wait-- no--", "Wait\u2014 no\u2014"),
            ("Hello world", "Hello world"),
            ("single-hyphen", "single-hyphen"),
            (
                "It wasn't-- It was not--\nYou are a nutcase.",
                "It wasn't\u2014 It was not\u2014\nYou are a nutcase.",
            ),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected


# ---------------------------------------------------------------------------
# Lengthy ellipsis (the only CERTAIN text step)
# ---------------------------------------------------------------------------


class TestFixLengthyEllipsisStep:
    step = FixLengthyEllipsisStep()

    @pytest.mark.parametrize(
        "src,expected",
        [
            ("Leslie Winkle....", "Leslie Winkle..."),
            ("Leslie Winkle.....", "Leslie Winkle..."),
            ("Leslie Winkle......", "Leslie Winkle..."),
            ("Hello world...", "Hello world..."),
            ("Hello world..", "Hello world.."),
            ("Hello world.", "Hello world."),
            ("Hello world", "Hello world"),
            ("Wait.... no....", "Wait... no..."),
            (
                "There was, uh, Joyce Kim,\nLeslie Winkle....",
                "There was, uh, Joyce Kim,\nLeslie Winkle...",
            ),
        ],
    )
    def test_substitution(self, src, expected):
        assert _apply(self.step, src) == expected

    def test_is_certain(self):
        proposal = self.step.propose(make_subtitle("...."))
        assert proposal.confidence is Confidence.CERTAIN
