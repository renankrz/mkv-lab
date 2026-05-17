"""Cleaning steps and the default pipeline assembly.

Steps are intentionally exported individually so users can build custom
pipelines (e.g. dropping ``RemoveMusicSignStep`` for karaoke files).
"""

from typing import List

from ..model import Subtitle
from ..pipeline import AcceptAllDecider, CleaningStep, run_pipeline
from .dash_formatting import DashFormattingStep
from .final_cleanup import FinalCleanupStep
from .speaker import RemoveSpeakerStep
from .text_steps import (
    FixDoubleHyphensStep,
    FixLengthyEllipsisStep,
    RemoveBracketsStep,
    RemoveCurlyBracketsStep,
    RemoveHashStep,
    RemoveMusicSignStep,
    RemoveParenthesesStep,
)

__all__ = [
    "DashFormattingStep",
    "FinalCleanupStep",
    "FixDoubleHyphensStep",
    "FixLengthyEllipsisStep",
    "RemoveBracketsStep",
    "RemoveCurlyBracketsStep",
    "RemoveHashStep",
    "RemoveMusicSignStep",
    "RemoveParenthesesStep",
    "RemoveSpeakerStep",
    "clean_subtitle",
    "default_pipeline",
]


def default_pipeline() -> List[CleaningStep]:
    """Returns the canonical ordered list of cleaning steps.

    Order matters: text-level removers run before per-line speaker stripping,
    which runs before dash formatting (which inspects the previous results),
    which runs before the final cleanup pass.
    """
    return [
        RemoveParenthesesStep(),
        RemoveBracketsStep(),
        RemoveCurlyBracketsStep(),
        RemoveHashStep(),
        RemoveMusicSignStep(),
        FixDoubleHyphensStep(),
        FixLengthyEllipsisStep(),
        RemoveSpeakerStep(),
        DashFormattingStep(),
        FinalCleanupStep(),
    ]


def clean_subtitle(subtitle: Subtitle) -> Subtitle:
    """Convenience: runs the default pipeline accepting every proposal.

    Mirrors the behaviour of the previous ``TextCleaner.clean_subtitle``;
    handy for testing and scripted use.
    """
    return run_pipeline(subtitle, default_pipeline(), AcceptAllDecider())
