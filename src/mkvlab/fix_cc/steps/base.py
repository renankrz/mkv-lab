"""Reusable base for cleaning steps whose transformation is a single
regex substitution on the subtitle text.

Most CC/SDH markers (parentheses, brackets, etc.) share this shape, so
declaring the regex, replacement and rationale is enough.
"""

from __future__ import annotations

import re

from ..model import Confidence, Proposal, Subtitle
from ..pipeline import CleaningStep


class TextRegexStep(CleaningStep):
    """Step that produces ``proposed = pattern.sub(replacement, text)``."""

    pattern: re.Pattern
    replacement: str = ""
    confidence: Confidence = Confidence.AMBIGUOUS
    rationale: str = ""

    def propose(self, subtitle: Subtitle) -> Proposal:
        new_text = self.pattern.sub(self.replacement, subtitle.text)
        return Proposal(
            step_name=self.name,
            original=subtitle,
            proposed=subtitle.with_text(new_text),
            confidence=self.confidence,
            rationale=self.rationale,
        )
