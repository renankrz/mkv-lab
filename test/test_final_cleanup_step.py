"""Tests for :class:`FinalCleanupStep`."""

from mkvlab.fix_cc import Confidence
from mkvlab.fix_cc.steps import FinalCleanupStep

from .helpers import make_subtitle


def _apply(text):
    return FinalCleanupStep().propose(make_subtitle(text)).proposed.text


class TestFinalCleanupStep:
    def test_collapses_multiple_spaces(self):
        assert _apply("Hello     world") == "Hello world"
        assert _apply("Hello   there   world") == "Hello there world"
        assert _apply("  Leading  and  trailing  ") == "Leading and trailing"

    def test_removes_spaces_before_punctuation(self):
        assert _apply("Hello , world !") == "Hello, world!"
        assert _apply("Hello . Goodbye !") == "Hello. Goodbye!"
        assert _apply("Question ? Answer : Yes") == "Question? Answer: Yes"
        assert _apply("Hello , world ! How are you ?") == "Hello, world! How are you?"

    def test_trims_multiline_whitespace(self):
        assert _apply("  Line 1  \n  Line 2  ") == "Line 1\nLine 2"
        assert _apply("   \n  Line 1  \n   \n  Line 2  \n   ") == "Line 1\nLine 2"
        assert _apply("Line 1   \n   \n   Line 2") == "Line 1\nLine 2"

    def test_tightens_dash_formatting(self):
        assert _apply(" -Line 1 \n - Line 2 ") == "-Line 1\n-Line 2"
        assert _apply("- Line 1 \n-  Line 2") == "-Line 1\n-Line 2"
        assert _apply(" - ") == "-"
        assert _apply("–Line 1 \n – Line 2 ") == "–Line 1\n–Line 2"
        assert _apply("—Line 1 \n — Line 2 ") == "—Line 1\n—Line 2"

    def test_drops_empty_lines(self):
        assert _apply("Line 1\n\nLine 2") == "Line 1\nLine 2"
        assert _apply("\nLine 1\n\nLine 2\n") == "Line 1\nLine 2"
        assert _apply("\n\n\n") == ""

    def test_preserves_valid_content(self):
        assert _apply("Hello world.") == "Hello world."
        assert _apply("Line 1\nLine 2") == "Line 1\nLine 2"
        assert _apply("-Dialog line") == "-Dialog line"

    def test_is_certain(self):
        proposal = FinalCleanupStep().propose(make_subtitle("hello"))
        assert proposal.confidence is Confidence.CERTAIN
