"""Speaker identification removal — operates per line."""

from .. import patterns
from ..model import Confidence, Proposal, Subtitle
from ..pipeline import CleaningStep


class RemoveSpeakerStep(CleaningStep):
    """Strips ``NAME:`` prefixes at the start of each line.

    Empty lines that result from a full-line speaker tag are dropped.
    """

    name = "speaker"

    def propose(self, subtitle: Subtitle) -> Proposal:
        cleaned: list[str] = []
        for line in subtitle.text.split("\n"):
            line = patterns.SPEAKER.sub("", line).strip()
            if line:
                cleaned.append(line)
        new_text = "\n".join(cleaned)
        return Proposal(
            step_name=self.name,
            original=subtitle,
            proposed=subtitle.with_text(new_text),
            confidence=Confidence.AMBIGUOUS,
            rationale="Removes speaker identification (NAME:) at line starts.",
        )
