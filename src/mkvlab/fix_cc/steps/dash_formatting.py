"""Dialogue-dash formatting step.

This is the only step that needs to consult the *original* subtitle: the
decision to prefix each line with ``-`` depends on whether the input
originally encoded multiple speakers or already used leading dashes.

The analysis lives here, next to its sole consumer.
"""

from __future__ import annotations

from .. import patterns
from ..model import Confidence, Proposal, Subtitle
from ..pipeline import CleaningStep

# Cleaners applied to a raw speaker name so that "SHELDON (excitedly)" and
# plain "SHELDON" count as the same speaker.
_NAME_CLEANERS = (
    patterns.PARENTHESES,
    patterns.BRACKETS,
    patterns.CURLY_BRACKETS,
    patterns.HASH,
    patterns.MUSIC_SIGN,
)


def _clean_speaker_name(raw: str) -> str:
    cleaned = raw
    for p in _NAME_CLEANERS:
        cleaned = p.sub("", cleaned)
    return cleaned.strip()


def _extract_speakers(text: str) -> set[str]:
    speakers: set[str] = set()
    for line in text.split("\n"):
        match = patterns.SPEAKER.match(line.strip())
        if match:
            name = _clean_speaker_name(match.group(1).strip())
            if name:
                speakers.add(name)
    return speakers


def _has_leading_dashes(text: str) -> bool:
    return any(
        patterns.LEADING_DASHES.match(line.strip())
        for line in text.split("\n")
        if line.strip()
    )


class DashFormattingStep(CleaningStep):
    """Prefixes each line with ``-`` when the subtitle encodes dialogue.

    Triggered when the *original* subtitle had multiple distinct speakers
    or already used leading dashes, or when the current text still does.
    """

    name = "dash_formatting"

    def propose(self, subtitle: Subtitle) -> Proposal:
        if not subtitle.text.strip() or not self._should_format(subtitle):
            return self._noop(subtitle)

        formatted: list[str] = []
        for line in subtitle.text.split("\n"):
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue
            without_dash = patterns.LEADING_DASHES.sub("", stripped)
            formatted.append(f"-{without_dash}" if without_dash else stripped)
        new_text = "\n".join(formatted)

        return Proposal(
            step_name=self.name,
            original=subtitle,
            proposed=subtitle.with_text(new_text),
            confidence=Confidence.AMBIGUOUS,
            rationale="Original encoded dialogue; normalise to leading dashes.",
        )

    def _should_format(self, subtitle: Subtitle) -> bool:
        original_speakers = _extract_speakers(subtitle.original_text)
        return (
            len(original_speakers) > 1
            or _has_leading_dashes(subtitle.original_text)
            or _has_leading_dashes(subtitle.text)
        )

    def _noop(self, subtitle: Subtitle) -> Proposal:
        return Proposal(
            step_name=self.name,
            original=subtitle,
            proposed=subtitle,
            confidence=Confidence.CERTAIN,
            rationale="No dialogue formatting required.",
        )
