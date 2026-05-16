#!/usr/bin/env python3
"""
Replace every subtitle stream in MKV files with a sibling SRT file.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .ffmpeg import ensure_ffmpeg_toolchain, replace_subtitle_streams


def process_directory(input_dir: Path, output_dir: Path) -> bool:
    """Re-mux every ``*.mkv`` in ``input_dir``, replacing its subtitles with
    the sibling ``.srt`` file. Returns ``True`` on full success.
    """
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is invalid.")
        sys.exit(1)

    if output_dir.exists() and not output_dir.is_dir():
        print(f"Error: Output path '{output_dir}' is not a valid directory.")
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)

    mkv_files = sorted(input_dir.glob("*.mkv"))
    if not mkv_files:
        print("No MKV files found in the input directory.")
        return False

    print(f"Processing {len(mkv_files)} MKV file(s)...")

    success = 0
    for i, mkv_file in enumerate(mkv_files, start=1):
        srt_file = mkv_file.with_suffix(".srt")
        if not srt_file.exists():
            print(f"{i}. Warning: SRT not found for {mkv_file.name}")
            continue

        out_file = output_dir / mkv_file.name
        try:
            replace_subtitle_streams(
                mkv_file, srt_file, out_file, language="en", default=True
            )
            print(f"{i}. {out_file.name} [OK]")
            success += 1
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
            print(f"{i}. Error processing {mkv_file.name}: {stderr}")

    return success == len(mkv_files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace subtitle streams in MKV files with a sibling SRT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos ./resubbed
  %(prog)s . ./output
        """,
    )
    parser.add_argument(
        "input_dir", help="Input directory containing MKV and SRT files"
    )
    parser.add_argument(
        "output_dir", help="Output directory for the processed MKV files"
    )
    args = parser.parse_args()

    ensure_ffmpeg_toolchain(require_ffprobe=False)

    if process_directory(Path(args.input_dir), Path(args.output_dir)):
        print("Processing completed successfully!")
    else:
        print("Processing completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
