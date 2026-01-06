#!/usr/bin/env python3
"""
Converts MP4+SRT pairs to MKV with embedded subtitles.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def process_files(input_dir, output_dir):
    """Processes MP4 and SRT files from the input directory and saves them in the output directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Input directory validation
    if not input_path.exists() or not input_path.is_dir():
        print(
            f"Error: Input directory '{input_dir}' does not exist or is invalid.")
        sys.exit(1)

    # Create output directory
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    elif not output_path.is_dir():
        print(
            f"Error: Output path '{output_dir}' is not a valid directory.")
        sys.exit(1)

    # Find MP4 files
    mp4_files = list(input_path.glob("*.mp4"))
    mp4_files.sort()

    if not mp4_files:
        print("No MP4 files found in the input directory.")
        return False

    success_count = 0
    total_files = len(mp4_files)

    print(f"Processing {total_files} MP4 file(s)...")

    for i, mp4_file in enumerate(mp4_files, 1):
        # Corresponding SRT file
        srt_file = mp4_file.with_suffix('.srt')

        if not srt_file.exists():
            print(f"{i}. Warning: SRT not found for {mp4_file.name}")
            continue

        # Output MKV file
        mkv_file = output_path / mp4_file.with_suffix('.mkv').name

        # FFmpeg command
        command = [
            'ffmpeg',
            '-i', str(mp4_file),
            '-i', str(srt_file),
            '-map', '0',
            '-map', '1',
            '-c', 'copy',
            '-c:s', 'srt',
            '-metadata:s:s:0', 'language=en',
            '-metadata:s:s:0', 'title=EN',
            '-disposition:s:0', 'default',
            '-y',
            str(mkv_file)
        ]

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"{i}. {mkv_file.name} [OK]")
            success_count += 1

        except subprocess.CalledProcessError as e:
            print(f"{i}. Error processing {mp4_file.name}: {e.stderr.strip()}")
        except FileNotFoundError:
            print("Error: FFmpeg not found. Install with: sudo apt install ffmpeg")
            sys.exit(1)

    return success_count == total_files


def main():
    parser = argparse.ArgumentParser(
        description='Convert MP4+SRT pairs to MKV with embedded subtitles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos ./converted
  %(prog)s . ./output
        """
    )

    parser.add_argument(
        'input_dir',
        help='Input directory with MP4 and SRT files'
    )
    parser.add_argument(
        'output_dir',
        help='Output directory for MKV files'
    )

    args = parser.parse_args()

    if process_files(args.input_dir, args.output_dir):
        print("Conversion completed successfully!")
    else:
        print("Conversion completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
