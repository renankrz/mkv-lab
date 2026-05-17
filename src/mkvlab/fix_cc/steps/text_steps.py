"""Text-level regex steps for each CC/SDH marker family."""

from .. import patterns
from ..model import Confidence
from .base import TextRegexStep


class RemoveParenthesesStep(TextRegexStep):
    """Removes ``(...)`` annotations — typically SDH sound cues."""

    name = "parentheses"
    pattern = patterns.PARENTHESES
    rationale = "Content in parentheses is usually a CC/SDH annotation."


class RemoveBracketsStep(TextRegexStep):
    """Removes ``[...]`` annotations."""

    name = "brackets"
    pattern = patterns.BRACKETS
    rationale = "Content in square brackets is usually a CC/SDH annotation."


class RemoveCurlyBracketsStep(TextRegexStep):
    """Removes ``{...}`` annotations."""

    name = "curly_brackets"
    pattern = patterns.CURLY_BRACKETS
    rationale = "Content in curly brackets is usually a CC/SDH annotation."


class RemoveHashStep(TextRegexStep):
    """Removes ``#...#`` annotations (legacy SDH style)."""

    name = "hash"
    pattern = patterns.HASH
    rationale = "Content between hash symbols is usually a CC/SDH annotation."


class RemoveMusicSignStep(TextRegexStep):
    """Removes the ``♪`` music marker."""

    name = "music_sign"
    pattern = patterns.MUSIC_SIGN
    rationale = "The music symbol is a CC/SDH marker."


class FixDoubleHyphensStep(TextRegexStep):
    """Converts ``--`` into an em dash (``—``)."""

    name = "double_hyphens"
    pattern = patterns.DOUBLE_HYPHENS
    replacement = "\u2014"
    rationale = "Double hyphens are an ASCII surrogate for the em dash."


class FixLengthyEllipsisStep(TextRegexStep):
    """Normalises ``....+`` to exactly three dots. Safe to apply unattended."""

    name = "lengthy_ellipsis"
    pattern = patterns.LENGTHY_ELLIPSIS
    replacement = "..."
    confidence = Confidence.CERTAIN
    rationale = "Sequences of 4+ dots are typos of a 3-dot ellipsis."
