"""
Typed wrappers around ``ffprobe`` for inspecting media streams.

This module centralises *all* parsing of ffprobe's plain-text ``[STREAM] ... [/STREAM]``
output so callers receive structured :class:`StreamInfo` objects instead of
re-implementing fragile state machines.

The selector helpers (:func:`select_audio_track`, :func:`select_portuguese_subtitle`,
:func:`select_english_subtitle_complete`, :func:`select_english_subtitle_default`)
encode the language- and disposition-preference rules used by the CLI commands.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Literal

from .languages import matches_language, normalize_code

StreamKind = Literal["audio", "subtitle", "video"]

_KIND_FLAG = {"audio": "a", "subtitle": "s", "video": "v"}

# Keywords that flag a subtitle title as "special" (CC/SDH/forced/etc.).
_SPECIAL_TITLE_KEYWORDS = ("forced", "sdh", "hi", "hearing", "signs", "dub")
_CC_TITLE_KEYWORDS = ("cc", "caption")
_HI_TITLE_KEYWORDS = ("sdh", "hi", "hearing", "impaired")


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StreamInfo:
    """A single media stream as reported by ``ffprobe``."""

    index: int
    kind: StreamKind
    language: str | None = None
    title: str | None = None
    forced: bool = False
    hearing_impaired: bool = False
    extras: dict[str, str] = field(default_factory=dict)

    @property
    def title_lower(self) -> str:
        return (self.title or "").lower()

    def title_flags_special(self) -> bool:
        """``True`` when the title text suggests a non-default subtitle variant."""
        return any(k in self.title_lower for k in _SPECIAL_TITLE_KEYWORDS)


# --------------------------------------------------------------------------- #
# Probing
# --------------------------------------------------------------------------- #


def probe_streams(path: str | Path, kind: StreamKind) -> list[StreamInfo]:
    """Return every stream of ``kind`` present in ``path``.

    Returns an empty list when ``ffprobe`` fails (treated as "no streams").
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=index:stream_tags=language,title:stream_disposition=forced,hearing_impaired",
        "-select_streams",
        _KIND_FLAG[kind],
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return []

    return list(_parse_streams(result.stdout, kind=kind))


def _parse_streams(output: str, *, kind: StreamKind) -> Iterable[StreamInfo]:
    """Parse ffprobe's flat ``[STREAM]`` blocks into :class:`StreamInfo` records."""
    current: dict[str, str] = {}
    in_block = False

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        low = line.lower()

        if low == "[stream]":
            current = {}
            in_block = True
            continue
        if low == "[/stream]":
            if in_block:
                info = _build_stream_info(current, kind=kind)
                if info is not None:
                    yield info
            in_block = False
            current = {}
            continue
        if not in_block:
            continue

        key, _, value = line.partition("=")
        if not _:
            continue
        current[key.strip().lower()] = value.strip()


def _build_stream_info(data: dict[str, str], *, kind: StreamKind) -> StreamInfo | None:
    """Materialise a single :class:`StreamInfo` from a flat key/value mapping."""
    raw_index = data.get("index")
    if raw_index is None:
        return None
    try:
        index = int(raw_index)
    except ValueError:
        return None

    return StreamInfo(
        index=index,
        kind=kind,
        language=data.get("tag:language"),
        title=data.get("tag:title"),
        forced=data.get("disposition:forced", "0") == "1",
        hearing_impaired=data.get("disposition:hearing_impaired", "0") == "1",
    )


# --------------------------------------------------------------------------- #
# Selectors
# --------------------------------------------------------------------------- #


def select_audio_track(path: str | Path, language: str) -> int | None:
    """Return the index of the first audio stream matching ``language``."""
    for stream in probe_streams(path, "audio"):
        if matches_language(stream.language, language):
            return stream.index
    return None


def select_portuguese_subtitle(path: str | Path) -> int | None:
    """Return a Portuguese subtitle stream, preferring ``pt-br`` over ``pt``.

    Brazilian Portuguese is always preferred when available; only when no
    Brazilian track exists do we fall back to a generic Portuguese one.
    """
    pt_br_index: int | None = None
    pt_index: int | None = None

    for stream in probe_streams(path, "subtitle"):
        code = normalize_code(stream.language)
        if not code:
            continue
        if matches_language(code, "pt-br"):
            pt_br_index = pt_br_index if pt_br_index is not None else stream.index
        elif matches_language(code, "pt") and pt_index is None:
            pt_index = stream.index

    return pt_br_index if pt_br_index is not None else pt_index


def select_english_subtitle_complete(path: str | Path) -> int | None:
    """Pick the *least polluted* complete English subtitle.

    Preference order — used by ``extract-srt``:

    1. ``normal``  — no CC/SDH/forced markers anywhere.
    2. ``hi``      — hearing-impaired (SDH).
    3. ``cc``      — closed captions (carries the most metadata).

    Forced subtitles are *never* returned (they are not complete tracks).
    """
    type_priority = {"normal": 0, "hi": 1, "cc": 2, "title_special": 3}
    best: tuple[int, int] | None = None  # (priority, index)

    for stream in probe_streams(path, "subtitle"):
        if not matches_language(stream.language, "en"):
            continue
        if stream.forced or "forced" in stream.title_lower:
            continue

        subtitle_type = "normal"
        special_by_title = False
        title = stream.title_lower
        if title:
            if any(k in title for k in _CC_TITLE_KEYWORDS):
                subtitle_type = "cc"
            if any(k in title for k in _HI_TITLE_KEYWORDS):
                subtitle_type = "hi"
            special_by_title = subtitle_type != "normal"

        if stream.hearing_impaired and subtitle_type == "normal":
            subtitle_type = "hi"

        if special_by_title and subtitle_type == "normal":
            subtitle_type = "title_special"

        priority = type_priority[subtitle_type]
        if best is None or priority < best[0]:
            best = (priority, stream.index)

    return best[1] if best else None


def select_english_subtitle_default(path: str | Path) -> int | None:
    """Pick an English subtitle suitable as the default track.

    Preference order — used by ``track-filter``:

    1. ``normal``           — no special dispositions or title markers.
    2. ``forced``           — forced narrative subtitle.
    3. ``hearing-impaired`` — SDH/CC as a last resort.
    """
    normal: int | None = None
    forced: int | None = None
    hearing: int | None = None

    for stream in probe_streams(path, "subtitle"):
        if not matches_language(stream.language, "en"):
            continue

        title_special = stream.title_flags_special()
        is_special = stream.forced or stream.hearing_impaired or title_special

        if not is_special and normal is None:
            normal = stream.index
        elif stream.forced and forced is None:
            forced = stream.index
        elif (stream.hearing_impaired or title_special) and hearing is None:
            hearing = stream.index

    return normal or forced or hearing
