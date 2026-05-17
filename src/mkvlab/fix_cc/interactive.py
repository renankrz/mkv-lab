"""Interactive review of pipeline output.

While :class:`mkvlab.fix_cc.pipeline.Decider` operates per-step (and answers
a yes/no), the human review of an SRT file is more natural *per subtitle*:
the user wants to see the auto-applied changes versus the fully-cleaned
proposal and decide what to do for the whole subtitle in a single prompt.

:class:`InteractiveDecider` encapsulates that flow. It is fully testable by
injecting ``input_fn`` and ``output_fn``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional

from .model import Subtitle


class Choice(Enum):
    """User's verdict on a per-subtitle proposal."""

    ACCEPT_FULL = auto()  # apply the fully-cleaned version
    KEEP_AUTO = auto()  # keep only the auto-accepted changes
    REMOVE = auto()  # drop this subtitle from the file
    EDIT = auto()  # use ``edited_text`` provided by the user
    CANCEL = auto()  # abort the whole session


@dataclass
class Decision:
    choice: Choice
    edited_text: Optional[str] = None


class InteractiveDecider:
    """Prompts the user once per subtitle that has ambiguous changes."""

    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._input = input_fn
        self._output = output_fn

    def decide(
        self,
        original: Subtitle,
        auto: Subtitle,
        fully: Subtitle,
        position: tuple[int, int],
    ) -> Decision:
        """Shows ``auto`` vs ``fully`` and returns the user's :class:`Decision`."""
        count, total = position
        self._output(
            f"\n-------------- Subtitle #{original.number} "
            f"({count}/{total}) --------------"
        )
        self._output(auto.text)

        will_remove = not fully.text.strip()
        self._output("-----------------------------------------")
        if will_remove:
            self._output("⚠️  REMOVE SUBTITLE")
        else:
            self._output(fully.text)
        self._output("-----------------------------------------")

        self._output("\nOptions:")
        self._output("1 - Accept correction")
        self._output("2 - Keep original")
        self._output("3 - Remove subtitle completely")
        self._output("4 - Edit manually")
        self._output("0 - Exit")

        raw = self._input("\nChoose (1/2/3/4/0): ").strip()

        if raw == "0":
            return Decision(Choice.CANCEL)
        if raw == "1":
            return Decision(Choice.REMOVE if will_remove else Choice.ACCEPT_FULL)
        if raw == "2":
            return Decision(Choice.KEEP_AUTO)
        if raw == "3":
            return Decision(Choice.REMOVE)
        if raw == "4":
            edited = self._prompt_edit_lines(auto.lines)
            if edited:
                return Decision(Choice.EDIT, edited)
            self._output("✗ Empty text, keeping original")
            return Decision(Choice.KEEP_AUTO)
        # Unknown input — preserve previous behaviour: keep original.
        return Decision(Choice.KEEP_AUTO)

    def _prompt_edit_lines(self, lines: List[str]) -> str:
        edited: list[str] = []
        for i, line in enumerate(lines, 1):
            self._output(f"  Line {i} current: {line}")
            new_line = self._input(f"  Line {i} new: ").strip()
            if new_line:
                edited.append(new_line)
        return "\n".join(edited)
