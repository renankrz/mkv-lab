"""
Typed wrappers around ``ffmpeg`` for muxing, remuxing and stream extraction.

Every function here builds the ``ffmpeg`` command line, runs it silently and
raises :class:`subprocess.CalledProcessError` on failure. Callers are expected
to handle errors and print user-facing messages — this module never prints.

A small helper, :func:`list_streams_text`, intentionally uses ``ffmpeg`` rather
than ``ffprobe`` because the ``streams`` CLI command reproduces ffmpeg's banner
output verbatim.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .languages import canonical_tag

# --------------------------------------------------------------------------- #
# Generic runner
# --------------------------------------------------------------------------- #


def run_ffmpeg(args: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess:
    """Invoke ``ffmpeg`` with ``args``; raises on non-zero exit.

    When ``quiet`` is true (default), stdout/stderr are captured; otherwise
    they are forwarded to the parent process.
    """
    cmd = ["ffmpeg", *args]
    if quiet:
        return subprocess.run(cmd, capture_output=True, text=True, check=True)
    return subprocess.run(cmd, check=True)


# --------------------------------------------------------------------------- #
# Subtitle extraction
# --------------------------------------------------------------------------- #


def extract_subtitle_to_srt(
    input_path: str | Path,
    subtitle_index: int | str,
    output_path: str | Path,
) -> None:
    """Extract a single subtitle stream from ``input_path`` to an SRT file."""
    run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-map",
            f"0:{subtitle_index}",
            "-c",
            "srt",
            str(output_path),
        ]
    )


# --------------------------------------------------------------------------- #
# SRT embedding / replacement
# --------------------------------------------------------------------------- #


def embed_external_srt(
    video_path: str | Path,
    srt_path: str | Path,
    output_path: str | Path,
    *,
    language: str = "en",
    title: str | None = None,
    default: bool = True,
) -> None:
    """Mux ``video_path`` + ``srt_path`` into ``output_path`` (e.g. MP4 → MKV).

    All original streams from the video are copied; the SRT is added as a new
    subtitle stream with the language metadata for ``language``.
    """
    title = title or language.upper()
    args = [
        "-i",
        str(video_path),
        "-i",
        str(srt_path),
        "-map",
        "0",
        "-map",
        "1",
        "-c",
        "copy",
        "-c:s",
        "srt",
        "-metadata:s:s:0",
        f"language={canonical_tag(language)}",
        "-metadata:s:s:0",
        f"title={title}",
    ]
    if default:
        args.extend(["-disposition:s:0", "default"])
    args.extend(["-y", str(output_path)])
    run_ffmpeg(args)


def replace_subtitle_streams(
    video_path: str | Path,
    srt_path: str | Path,
    output_path: str | Path,
    *,
    language: str = "en",
    title: str | None = None,
    default: bool = True,
) -> None:
    """Replace every subtitle stream in ``video_path`` with ``srt_path``.

    Mapping rationale:
      * ``-map 0``      include every stream from the input;
      * ``-map -0:s``   exclude the original subtitle streams;
      * ``-map 1:s``    add the subtitle stream from the SRT file.
    """
    title = title or language.upper()
    args = [
        "-i",
        str(video_path),
        "-i",
        str(srt_path),
        "-map",
        "0",
        "-map",
        "-0:s",
        "-map",
        "1:s",
        "-c",
        "copy",
        "-c:s",
        "srt",
        "-metadata:s:s:0",
        f"language={canonical_tag(language)}",
        "-metadata:s:s:0",
        f"title={title}",
    ]
    if default:
        args.extend(["-disposition:s:0", "default"])
    args.extend(["-y", str(output_path)])
    run_ffmpeg(args)


# --------------------------------------------------------------------------- #
# Track filtering
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SubtitleSelection:
    """A subtitle stream to keep when filtering tracks."""

    language: str  # canonical key, e.g. "pt", "en"
    source_index: int | str
    is_default: bool = False


def filter_tracks(
    input_path: str | Path,
    output_path: str | Path,
    *,
    subtitles: list[SubtitleSelection],
    audio_index: int | str | None = None,
) -> None:
    """Remux ``input_path`` keeping only selected audio and subtitle tracks.

    The video stream is always preserved. When ``audio_index`` is ``None`` all
    audio streams are kept; otherwise only the indicated audio track survives.
    """
    args: list[str] = ["-i", str(input_path), "-map", "0:v", "-c", "copy"]

    if audio_index is not None:
        args.extend(["-map", f"0:{audio_index}"])
    else:
        args.extend(["-map", "0:a"])

    for selection in subtitles:
        args.extend(["-map", f"0:{selection.source_index}"])

    for i, selection in enumerate(subtitles):
        args.extend(
            [
                f"-metadata:s:s:{i}",
                f"language={canonical_tag(selection.language)}",
                f"-metadata:s:s:{i}",
                f"title={selection.language.upper()}",
            ]
        )
        if selection.is_default:
            args.extend([f"-disposition:s:{i}", "default"])

    args.extend(["-c:a", "copy", str(output_path)])
    run_ffmpeg(args)


# --------------------------------------------------------------------------- #
# Stream listing (banner-style)
# --------------------------------------------------------------------------- #


def list_streams_text(path: str | Path) -> list[str]:
    """Return ``ffmpeg`` banner lines containing ``Stream`` for ``path``.

    Uses ``ffmpeg`` (not ``ffprobe``) to preserve the verbose,
    human-friendly format users are familiar with.
    """
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path)],
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return [line for line in result.stderr.split("\n") if "Stream" in line]
