"""Tests for :class:`InteractiveDecider` using mocked I/O.

The decider's logic is driven entirely by the user's typed choice ("1".."4",
"0"); injecting fake ``input_fn`` and ``output_fn`` lets us assert the
returned :class:`Decision` without touching a real terminal.
"""

import pytest

from mkvlab.fix_cc import Choice, InteractiveDecider

from .helpers import make_subtitle


class _ScriptedIO:
    """Helper that feeds canned answers and captures output lines."""

    def __init__(self, answers):
        self._answers = list(answers)
        self.output: list[str] = []

    def input(self, prompt=""):
        return self._answers.pop(0)

    def print(self, msg=""):
        self.output.append(str(msg))


@pytest.fixture
def trio():
    """Returns ``(original, auto, fully)`` — three distinct texts."""
    original = make_subtitle("PERSON: Hello (noise)")
    auto = original.with_text("PERSON: Hello (noise)")  # auto unchanged here
    fully = original.with_text("Hello")
    return original, auto, fully


def _decide(answers, trio, position=(1, 1)):
    io = _ScriptedIO(answers)
    decider = InteractiveDecider(input_fn=io.input, output_fn=io.print)
    decision = decider.decide(*trio, position=position)
    return decision, io


class TestInteractiveDecider:
    def test_accept_correction(self, trio):
        decision, _ = _decide(["1"], trio)
        assert decision.choice is Choice.ACCEPT_FULL

    def test_keep_original(self, trio):
        decision, _ = _decide(["2"], trio)
        assert decision.choice is Choice.KEEP_AUTO

    def test_remove(self, trio):
        decision, _ = _decide(["3"], trio)
        assert decision.choice is Choice.REMOVE

    def test_cancel(self, trio):
        decision, _ = _decide(["0"], trio)
        assert decision.choice is Choice.CANCEL

    def test_unknown_input_keeps_original(self, trio):
        decision, _ = _decide(["xyz"], trio)
        assert decision.choice is Choice.KEEP_AUTO

    def test_accept_when_fully_is_empty_means_remove(self):
        original = make_subtitle("(applause)")
        auto = original
        fully = original.with_text("")
        decision, io = _decide(["1"], (original, auto, fully))
        assert decision.choice is Choice.REMOVE
        # The user-facing warning was shown.
        assert any("REMOVE SUBTITLE" in line for line in io.output)

    def test_manual_edit_returns_typed_text(self):
        original = make_subtitle("SHELDON: Foo\nLEONARD: Bar")
        auto = original.with_text("SHELDON: Foo\nLEONARD: Bar")
        fully = original.with_text("-Foo\n-Bar")
        # "4" → edit; then one replacement per line.
        decision, _ = _decide(["4", "Foo!", "Bar!"], (original, auto, fully))
        assert decision.choice is Choice.EDIT
        assert decision.edited_text == "Foo!\nBar!"

    def test_manual_edit_empty_falls_back_to_keep(self):
        original = make_subtitle("X")
        auto = original.with_text("X")
        fully = original.with_text("Y")
        # User picks edit but submits nothing for the single line.
        decision, _ = _decide(["4", ""], (original, auto, fully))
        assert decision.choice is Choice.KEEP_AUTO

    def test_output_includes_diff_and_options(self, trio):
        _, io = _decide(["2"], trio)
        joined = "\n".join(io.output)
        assert "Subtitle #1" in joined
        assert "Options:" in joined
        assert "1 - Accept correction" in joined
        assert "0 - Exit" in joined
