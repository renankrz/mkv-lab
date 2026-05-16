#!/usr/bin/env python3
"""
Extract English subtitles from MKV files, preferring the least polluted track.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .ffmpeg import (
    ensure_ffmpeg_toolchain,
    extract_subtitle_to_srt,
    select_english_subtitle_complete,
)


def parse_arguments() -> tuple[Path, Path]:
    """Parse command-line arguments and return ``(input_dir, output_dir)``."""
    parser = argparse.ArgumentParser(
        description="Extract English subtitles from MKV files, preferring the least polluted track",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos
  %(prog)s ./videos ./subtitles
        """,
    )
    parser.add_argument("input_dir", help="Input directory containing MKV files")
    parser.add_argument(
        "output_dir",
        nargs="?",
        help="Output directory for SRT files (defaults to input directory)",
    )

    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    return input_dir, output_dir


def extract_from_file(mkv_file: Path, output_dir: Path, file_index: int) -> bool:
    """Extract the best English subtitle from ``mkv_file`` into ``output_dir``."""
    subtitle_index = select_english_subtitle_complete(str(mkv_file))
    if subtitle_index is None:
        print(
            f"{file_index}. {mkv_file.name} [FAIL: no suitable English subtitle found]"
        )
        return False

    output_file = output_dir / f"{mkv_file.stem}.srt"
    try:
        extract_subtitle_to_srt(str(mkv_file), subtitle_index, output_file)
    except subprocess.CalledProcessError:
        print(f"{file_index}. {mkv_file.name} [FAIL: ffmpeg error]")
        if output_file.exists():
            output_file.unlink()
        return False
    except OSError:
        print(f"{file_index}. {mkv_file.name} [FAIL: file error]")
        if output_file.exists():
            output_file.unlink()
        return False

    print(f"{file_index}. {mkv_file.name} [OK]")
    return True


def main() -> None:
    ensure_ffmpeg_toolchain()
    input_dir, output_dir = parse_arguments()

    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    mkv_files = sorted(input_dir.glob("*.mkv"))
    if not mkv_files:
        print("No MKV files found.")
        return

    print(f"Processing {len(mkv_files)} MKV file(s)...")
    success = sum(
        extract_from_file(mkv, output_dir, i)
        for i, mkv in enumerate(mkv_files, start=1)
    )
    print(f"Processing complete! {success}/{len(mkv_files)} file(s) processed.")


if __name__ == "__main__":
    main()
