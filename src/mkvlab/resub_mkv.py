#!/usr/bin/env python3
"""
Replaces subtitle streams in MKV files with a corresponding SRT file.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def process_files(input_dir, output_dir):
    """Processes MKV and SRT files from the input directory and saves them in the output directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Input directory validation
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is invalid.")
        sys.exit(1)

    # Create output directory
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    elif not output_path.is_dir():
        print(f"Error: Output path '{output_dir}' is not a valid directory.")
        sys.exit(1)

    # Find MKV files
    mkv_files = list(input_path.glob("*.mkv"))
    mkv_files.sort()

    if not mkv_files:
        print("No MKV files found in the input directory.")
        return False

    success_count = 0
    total_files = len(mkv_files)

    print(f"Processing {total_files} MKV file(s)...")

    for i, mkv_file in enumerate(mkv_files, 1):
        # Corresponding SRT file
        srt_file = mkv_file.with_suffix(".srt")

        if not srt_file.exists():
            print(f"{i}. Warning: SRT not found for {mkv_file.name}")
            continue

        # Output MKV file
        out_file = output_path / mkv_file.name

        # FFmpeg command:
        #   -map 0        — include all streams from the input MKV
        #   -map -0:s     — then exclude all subtitle streams from it
        #   -map 1:s      — add the subtitle stream from the SRT file
        command = [
            "ffmpeg",
            "-i",
            str(mkv_file),
            "-i",
            str(srt_file),
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
            "language=en",
            "-metadata:s:s:0",
            "title=EN",
            "-disposition:s:0",
            "default",
            "-y",
            str(out_file),
        ]

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"{i}. {out_file.name} [OK]")
            success_count += 1

        except subprocess.CalledProcessError as e:
            print(f"{i}. Error processing {mkv_file.name}: {e.stderr.strip()}")
        except FileNotFoundError:
            print("Error: FFmpeg not found. Install with: sudo apt install ffmpeg")
            sys.exit(1)

    return success_count == total_files


def main():
    parser = argparse.ArgumentParser(
        description="Replace subtitle streams in MKV files with a corresponding SRT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos ./resubbed
  %(prog)s . ./output
        """,
    )

    parser.add_argument("input_dir", help="Input directory with MKV and SRT files")
    parser.add_argument(
        "output_dir", help="Output directory for the processed MKV files"
    )

    args = parser.parse_args()

    if process_files(args.input_dir, args.output_dir):
        print("Processing completed successfully!")
    else:
        print("Processing completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
