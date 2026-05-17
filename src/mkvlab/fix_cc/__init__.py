"""Public API of the ``fix_cc`` package.

Cleaning of CC/SDH elements from SRT subtitles, organised as a small
pipeline of :class:`CleaningStep` instances driven by a :class:`Decider`.
"""

from .cli import SubtitleSession, main
from .interactive import Choice, Decision, InteractiveDecider
from .model import Confidence, Proposal, Subtitle
from .pipeline import (
    AcceptAllDecider,
    AutoDecider,
    CleaningStep,
    Decider,
    run_pipeline,
)
from .srt_io import load_srt, save_srt
from .steps import clean_subtitle, default_pipeline

__all__ = [
    "AcceptAllDecider",
    "AutoDecider",
    "Choice",
    "CleaningStep",
    "Confidence",
    "Decider",
    "Decision",
    "InteractiveDecider",
    "Proposal",
    "Subtitle",
    "SubtitleSession",
    "clean_subtitle",
    "default_pipeline",
    "load_srt",
    "main",
    "run_pipeline",
    "save_srt",
]
