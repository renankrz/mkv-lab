"""Domain model for the `fix_cc` pipeline.

Defines the immutable-ish :class:`Subtitle` value object that flows through
the cleaning pipeline, and the :class:`Proposal` / :class:`Confidence`
types produced by each :class:`CleaningStep`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum, auto
from typing import List

import srt


class Confidence(Enum):
    """Whether a proposed transformation is safe to apply unattended."""

    CERTAIN = auto()  # always safe — applied even in unattended mode
    AMBIGUOUS = auto()  # requires a policy/user decision


@dataclass
class Subtitle:
    """A single SRT subtitle as it flows through the pipeline.

    ``text`` is the *current* content; ``original_text`` is preserved across
    pipeline steps so that steps which need to look at the unprocessed input
    (e.g. dash formatting based on the original speaker layout) can do so.
    """

    number: int
    start_time: str
    end_time: str
    text: str
    original_text: str = ""

    def __post_init__(self) -> None:
        if not self.original_text:
            self.original_text = self.text

    @property
    def lines(self) -> List[str]:
        return self.text.split("\n")

    @property
    def original_lines(self) -> List[str]:
        return self.original_text.split("\n")

    def with_text(self, new_text: str) -> "Subtitle":
        """Returns a copy with ``text`` replaced; ``original_text`` preserved."""
        return Subtitle(
            number=self.number,
            start_time=self.start_time,
            end_time=self.end_time,
            text=new_text,
            original_text=self.original_text,
        )

    # ---- srt-package adapters -------------------------------------------------

    @classmethod
    def from_srt(cls, sub: srt.Subtitle) -> "Subtitle":
        """Builds a domain `Subtitle` from a `srt.Subtitle`."""
        return cls(
            number=sub.index,
            start_time=srt.timedelta_to_srt_timestamp(sub.start),
            end_time=srt.timedelta_to_srt_timestamp(sub.end),
            text=sub.content,
        )

    def to_srt(self) -> srt.Subtitle:
        """Converts this subtitle back into a `srt.Subtitle`."""
        return srt.Subtitle(
            index=self.number,
            start=(
                srt.srt_timestamp_to_timedelta(self.start_time)
                if self.start_time
                else timedelta(0)
            ),
            end=(
                srt.srt_timestamp_to_timedelta(self.end_time)
                if self.end_time
                else timedelta(0)
            ),
            content=self.text,
        )


@dataclass
class Proposal:
    """A transformation proposed by a :class:`CleaningStep`.

    A proposal is *not* applied to its ``original`` until a :class:`Decider`
    accepts it. The ``confidence`` and ``rationale`` fields are inspected by
    deciders to choose a policy.
    """

    step_name: str
    original: "Subtitle"
    proposed: "Subtitle"
    confidence: Confidence
    rationale: str = ""

    @property
    def changed(self) -> bool:
        return self.proposed.text != self.original.text
