"""Shared helpers for the fix_cc test suite."""

from mkvlab.fix_cc import Subtitle


def make_subtitle(text: str, number: int = 1) -> Subtitle:
    """Builds a Subtitle with placeholder timestamps for unit tests."""
    return Subtitle(
        number=number,
        start_time="00:00:01,000",
        end_time="00:00:03,000",
        text=text,
    )
