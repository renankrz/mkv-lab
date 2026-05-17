"""Final whitespace / punctuation normalisation. Always safe."""

from .. import patterns
from ..model import Confidence, Proposal, Subtitle
from ..pipeline import CleaningStep


class FinalCleanupStep(CleaningStep):
    """Collapses whitespace, trims, removes empty lines, tightens punctuation."""

    name = "final_cleanup"

    def propose(self, subtitle: Subtitle) -> Proposal:
        cleaned: list[str] = []
        for line in subtitle.text.split("\n"):
            line = patterns.MULTIPLE_SPACES.sub(" ", line).strip()
            line = patterns.DASH_TRAILING_SPACE.sub(r"\1", line)
            line = patterns.SPACES_BEFORE_PUNCTUATION.sub(r"\1", line)
            if line:
                cleaned.append(line)
        new_text = "\n".join(cleaned)

        return Proposal(
            step_name=self.name,
            original=subtitle,
            proposed=subtitle.with_text(new_text),
            confidence=Confidence.CERTAIN,
            rationale="Normalises whitespace, dashes and punctuation.",
        )
