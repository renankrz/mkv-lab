#!/usr/bin/env python3
"""
Print the stream lines from an ``ffmpeg`` probe of a single media file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ffmpeg import ensure_ffmpeg_toolchain, list_streams_text


def show_streams(path: Path) -> int:
    """Print every line containing ``Stream`` from ffmpeg's banner output."""
    if not path.is_file():
        print(f"Error: The file '{path}' was not found.")
        return 1

    for line in list_streams_text(path):
        print(line)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List stream information from a media file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s S01E10.mkv
        """,
    )
    parser.add_argument("file", help="Path to the media file to inspect")
    args = parser.parse_args()

    ensure_ffmpeg_toolchain(require_ffprobe=False)
    sys.exit(show_streams(Path(args.file)))


if __name__ == "__main__":
    main()
