"""SRT file I/O. Thin wrappers around the ``srt`` package."""

from __future__ import annotations

from pathlib import Path
from typing import List

import srt

from .model import Subtitle


def load_srt(file_path: str) -> List[Subtitle]:
    """Reads and parses an SRT file.

    Tries UTF-8 first (transparently handling a BOM via ``utf-8-sig``) and
    falls back to ``latin-1`` for legacy files. Raises :class:`ValueError`
    on unrecoverable I/O or parse errors.
    """
    path = Path(file_path)
    raw: str | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            raw = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    if raw is None:
        raise ValueError(f"Could not decode {file_path} with either utf-8 or latin-1.")
    try:
        return [Subtitle.from_srt(s) for s in srt.parse(raw)]
    except srt.SRTParseError as exc:
        raise ValueError(f"Error parsing SRT: {exc}") from exc


def save_srt(file_path: str, subtitles: List[Subtitle]) -> None:
    """Writes ``subtitles`` to ``file_path``; lets ``srt.compose`` reindex."""
    composed = srt.compose([s.to_srt() for s in subtitles], reindex=True, start_index=1)
    Path(file_path).write_text(composed, encoding="utf-8")
