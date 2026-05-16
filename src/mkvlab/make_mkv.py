#!/usr/bin/env python3
"""
Convert MP4 + SRT pairs into MKV files with an embedded English subtitle stream.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .ffmpeg import embed_external_srt, ensure_ffmpeg_toolchain


def process_directory(input_dir: Path, output_dir: Path) -> bool:
    """Mux every ``*.mp4`` in ``input_dir`` with its sibling ``*.srt``.

    Returns ``True`` when *all* files were converted successfully.
    """
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is invalid.")
        sys.exit(1)

    if output_dir.exists() and not output_dir.is_dir():
        print(f"Error: Output path '{output_dir}' is not a valid directory.")
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)

    mp4_files = sorted(input_dir.glob("*.mp4"))
    if not mp4_files:
        print("No MP4 files found in the input directory.")
        return False

    print(f"Processing {len(mp4_files)} MP4 file(s)...")

    success = 0
    for i, mp4_file in enumerate(mp4_files, start=1):
        srt_file = mp4_file.with_suffix(".srt")
        if not srt_file.exists():
            print(f"{i}. Warning: SRT not found for {mp4_file.name}")
            continue

        mkv_file = output_dir / mp4_file.with_suffix(".mkv").name
        try:
            embed_external_srt(
                mp4_file, srt_file, mkv_file, language="en", default=True
            )
            print(f"{i}. {mkv_file.name} [OK]")
            success += 1
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
            print(f"{i}. Error processing {mp4_file.name}: {stderr}")

    return success == len(mp4_files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert MP4+SRT pairs to MKV with an embedded English subtitle stream",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos ./converted
  %(prog)s . ./output
        """,
    )
    parser.add_argument(
        "input_dir", help="Input directory containing MP4 and SRT files"
    )
    parser.add_argument(
        "output_dir", help="Output directory for the resulting MKV files"
    )
    args = parser.parse_args()

    ensure_ffmpeg_toolchain(require_ffprobe=False)

    if process_directory(Path(args.input_dir), Path(args.output_dir)):
        print("Conversion completed successfully!")
    else:
        print("Conversion completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
