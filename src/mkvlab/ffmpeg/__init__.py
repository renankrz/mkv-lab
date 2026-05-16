"""
Wrappers around the external ``ffmpeg`` / ``ffprobe`` binaries.

Sub-modules
-----------
- :mod:`mkvlab.ffmpeg.languages`    — language-code catalog and matching.
- :mod:`mkvlab.ffmpeg.dependencies` — runtime checks for ``ffmpeg``/``ffprobe``.
- :mod:`mkvlab.ffmpeg.probe`        — ``ffprobe`` wrappers + stream selectors.
- :mod:`mkvlab.ffmpeg.mux`          — ``ffmpeg`` wrappers (extract / mux / remux).
"""

from .dependencies import MissingDependencyError, ensure_ffmpeg_toolchain
from .languages import (
    EN_CODES,
    JP_CODES,
    PT_BR_CODES,
    PT_PT_CODES,
    canonical_tag,
    matches_language,
    normalize_code,
)
from .mux import (
    SubtitleSelection,
    embed_external_srt,
    extract_subtitle_to_srt,
    filter_tracks,
    list_streams_text,
    replace_subtitle_streams,
    run_ffmpeg,
)
from .probe import (
    StreamInfo,
    probe_streams,
    select_audio_track,
    select_english_subtitle_complete,
    select_english_subtitle_default,
    select_portuguese_subtitle,
)

__all__ = [
    # dependencies
    "MissingDependencyError",
    "ensure_ffmpeg_toolchain",
    # languages
    "EN_CODES",
    "JP_CODES",
    "PT_BR_CODES",
    "PT_PT_CODES",
    "canonical_tag",
    "matches_language",
    "normalize_code",
    # probe
    "StreamInfo",
    "probe_streams",
    "select_audio_track",
    "select_english_subtitle_complete",
    "select_english_subtitle_default",
    "select_portuguese_subtitle",
    # mux
    "SubtitleSelection",
    "embed_external_srt",
    "extract_subtitle_to_srt",
    "filter_tracks",
    "list_streams_text",
    "replace_subtitle_streams",
    "run_ffmpeg",
]
