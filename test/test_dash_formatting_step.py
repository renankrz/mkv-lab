"""Tests for :class:`DashFormattingStep`.

The decision to format with leading dashes is the only place where the
*original* (pre-pipeline) subtitle matters; these tests exercise both the
detection helpers and the proposal output.
"""

from mkvlab.fix_cc.steps import DashFormattingStep

from .helpers import make_subtitle


def _propose(original_text, current_text=None):
    """Builds a Subtitle whose ``original_text`` differs from current ``text``
    (mimicking what previous pipeline steps would have produced)."""
    sub = make_subtitle(original_text)
    if current_text is not None and current_text != original_text:
        sub = sub.with_text(current_text)
    return DashFormattingStep().propose(sub)


class TestDashFormattingDecision:
    """Tests that exercise *when* the step decides to format."""

    def test_no_speakers_no_dashes_keeps_text(self):
        result = _propose("Hello world.\nHow are you?")
        assert result.proposed.text == "Hello world.\nHow are you?"

    def test_single_speaker_no_dashes_keeps_text(self):
        # One speaker only, no dash hint → no formatting.
        result = _propose("PERSON: How are you?", "How are you?")
        assert result.proposed.text == "How are you?"

    def test_two_speakers_triggers_formatting(self):
        result = _propose(
            "SHELDON: She's not that intelligent.\nLEONARD: She fixed your equation.",
            "She's not that intelligent.\nShe fixed your equation.",
        )
        assert (
            result.proposed.text
            == "-She's not that intelligent.\n-She fixed your equation."
        )

    def test_original_leading_dashes_triggers_formatting(self):
        result = _propose("-Hello world\n-This is a test")
        assert result.proposed.text == "-Hello world\n-This is a test"

    def test_current_leading_dash_triggers_formatting(self):
        # No speakers, no original dashes — but the current text has a dash.
        result = _propose("(noise)\n-Hello", "\n-Hello")
        assert "-Hello" in result.proposed.text

    def test_speaker_then_dash(self):
        result = _propose(
            "LESLIE: Good night, guys. Good job.\n-Thanks.",
            "Good night, guys. Good job.\n-Thanks.",
        )
        assert result.proposed.text == "-Good night, guys. Good job.\n-Thanks."

    def test_dash_then_speaker(self):
        result = _propose(
            "-Good night, guys. Good job.\nLESLIE: Thanks.",
            "-Good night, guys. Good job.\nThanks.",
        )
        assert result.proposed.text == "-Good night, guys. Good job.\n-Thanks."


class TestDashFormattingSpeakerExtraction:
    """The speaker counter ignores CC/SDH noise inside the name."""

    def test_speaker_with_parentheses_is_normalised(self):
        # SHELDON (excitedly) + LEONARD ⇒ two distinct speakers.
        result = _propose(
            "SHELDON (excitedly): I have a theory!\nLEONARD: Not again.",
            "I have a theory!\nNot again.",
        )
        assert result.proposed.text == "-I have a theory!\n-Not again."


class TestDashFormattingDashKinds:
    """Different leading-dash characters are all recognised as dialogue."""

    def test_en_dash_triggers_formatting(self):
        # Original used an en dash; current is the same.
        result = _propose("–Hello\n–World")
        assert result.proposed.text == "-Hello\n-World"

    def test_em_dash_triggers_formatting(self):
        result = _propose("—Hello\n—World")
        assert result.proposed.text == "-Hello\n-World"

    def test_dash_with_spaces_triggers_formatting(self):
        result = _propose(" - Hello world\n – World ")
        assert "-" in result.proposed.text.split("\n")[0]


class TestDashFormattingNonTriggers:
    """Mid-line or trailing dashes do not look like dialogue markers."""

    def test_non_leading_dash_ignored(self):
        result = _propose("Hello - world\nWorld - hello")
        assert result.proposed.text == "Hello - world\nWorld - hello"

    def test_internal_hyphen_ignored(self):
        result = _propose("Hello-world\nWorld-hello")
        assert result.proposed.text == "Hello-world\nWorld-hello"

    def test_trailing_dash_ignored(self):
        result = _propose("Hello world-\nWorld hello-")
        assert result.proposed.text == "Hello world-\nWorld hello-"


class TestDashFormattingEdgeCases:
    def test_empty_text_no_op(self):
        result = _propose("")
        assert result.proposed.text == ""
