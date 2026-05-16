"""
Runtime-dependency checks for the external ``ffmpeg`` / ``ffprobe`` binaries.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


class MissingDependencyError(RuntimeError):
    """Raised when a required external binary is not available on ``PATH``."""


def ensure_binary_available(binary: str) -> None:
    """Verify that ``binary`` can be executed; raise on failure."""
    if shutil.which(binary) is None:
        raise MissingDependencyError(
            f"Required binary '{binary}' was not found on PATH."
        )
    try:
        subprocess.run(
            [binary, "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        raise MissingDependencyError(
            f"Required binary '{binary}' failed to execute."
        ) from exc


def ensure_ffmpeg_toolchain(*, require_ffprobe: bool = True) -> None:
    """Ensure ``ffmpeg`` (and optionally ``ffprobe``) are installed and usable.

    Exits the process with status ``1`` and a helpful message when missing.
    Designed to be called once at the start of CLI entrypoints.
    """
    try:
        ensure_binary_available("ffmpeg")
        if require_ffprobe:
            ensure_binary_available("ffprobe")
    except MissingDependencyError as exc:
        print(f"Error: {exc} Install with: sudo apt install ffmpeg")
        sys.exit(1)
