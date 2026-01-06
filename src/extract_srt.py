#!/usr/bin/env python3
"""
Extracts English subtitles from MKV files, preferring the least polluted ones.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_arguments():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser(
        description='Extracts English subtitles from MKV files, preferring the least polluted ones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./videos
  %(prog)s ./videos ./subtitles
        """
    )

    # Directories
    parser.add_argument(
        'input_dir', help='Input directory with MKV files')
    parser.add_argument(
        'output_dir', nargs='?', help='Output directory for SRT files (optional)')

    args = parser.parse_args()

    # Set output directory (if not provided, use the same as input)
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.input_dir)

    return Path(args.input_dir), output_dir


def find_complete_english_subtitle(input_file):
    """
    Finds a complete English subtitle (not forced) based on the following preference order:
    1. Normal subtitles (no special tags, not forced)
    2. Subtitles with less 'pollution' (fewer extra elements)

    Preference order for complete subtitles:
    - normal (best)
    - hi/sdh (contains audio descriptions)
    - cc (most polluted, with metadata)

    Completely ignores forced subtitles
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'stream=index:stream_tags=language,title',
            '-show_entries', 'stream_disposition=forced,hearing_impaired',
            '-select_streams', 's',
            input_file
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        subtitle_candidates = []  # List of (index, type, title)

        current_index = None
        current_lang = None
        current_title = None
        current_forced = False
        current_hearing_impaired = False

        # Map common language variations
        lang_variations = {
            'en': ['en', 'eng', 'english', 'en-us', 'en_us', 'enus', 'en-gb', 'en_gb', 'engb']
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip().lower()

            if line.startswith('[stream]'):
                # Reset for new stream
                current_index = None
                current_lang = None
                current_title = None
                current_forced = False
                current_hearing_impaired = False

            elif line.startswith('[/stream]'):
                # Process complete stream - IGNORE forced subtitles
                if (current_lang and any(current_lang in lang_variations.get('en', []) for current_lang in [current_lang])
                        and not current_forced):

                    # Determine subtitle type based on tags and dispositions
                    subtitle_type = 'normal'

                    # Check if special by title
                    title_special = False
                    special_tags = []
                    if current_title:
                        title_lower = current_title.lower()

                        # Ignore forced subtitles by title as well
                        if 'forced' in title_lower:
                            continue  # Skip forced subtitles
                        if any(tag in title_lower for tag in ['cc', 'caption']):
                            subtitle_type = 'cc'
                            special_tags.append('cc')
                        if any(tag in title_lower for tag in ['sdh', 'hi', 'hearing', 'impaired']):
                            subtitle_type = 'hi'
                            special_tags.append('hi')

                        # Mark as special if there are relevant tags
                        title_special = bool(special_tags)

                    # Check dispositions (already ensured not forced above)
                    if current_hearing_impaired and subtitle_type == 'normal':
                        subtitle_type = 'hi'
                        special_tags.append('hi')

                    # Add to candidate list
                    subtitle_candidates.append({
                        'index': current_index,
                        'type': subtitle_type,
                        'title': current_title,
                        'special_tags': special_tags,
                        'hearing_impaired': current_hearing_impaired,
                        'title_special': title_special
                    })

            elif line.startswith('index='):
                current_index = line.split('=')[1]
            elif line.startswith('tag:language='):
                current_lang = line.split('=')[1].strip()
            elif line.startswith('tag:title='):
                current_title = line.split('=')[1].strip()
            elif line.startswith('disposition:forced='):
                current_forced = line.split('=')[1].strip() == '1'
            elif line.startswith('disposition:hearing_impaired='):
                current_hearing_impaired = line.split('=')[1].strip() == '1'

        # Preference order: normal > hi > cc > title_special
        type_priority = {'normal': 0, 'hi': 1, 'cc': 2, 'title_special': 3}

        # Find the best subtitle based on priority
        best_subtitle = None
        for candidate in subtitle_candidates:
            candidate_type = candidate['type']
            if candidate['title_special'] and candidate_type == 'normal':
                candidate_type = 'title_special'

            if best_subtitle is None or type_priority[candidate_type] < type_priority[best_subtitle['type']]:
                best_subtitle = candidate

        return best_subtitle['index'] if best_subtitle else None

    except subprocess.CalledProcessError:
        return None


def extract_subtitle(input_file, output_file, subtitle_index, file_index):
    """Extracts the subtitle to SRT file"""
    input_path = Path(input_file)
    file_name = input_path.name

    try:
        # Build ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_file,
            '-map', f'0:{subtitle_index}',
            '-c', 'srt',
            str(output_file)
        ]

        # Run conversion
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)

        print(f"{file_index}. {file_name} [OK]")
        return True

    except subprocess.CalledProcessError:
        print(f"{file_index}. {file_name} [FAIL: ffmpeg error]")
        if output_file.exists():
            output_file.unlink()
        return False
    except OSError as e:
        print(f"{file_index}. {file_name} [FAIL: file error]")
        if output_file.exists():
            output_file.unlink()
        return False


def main():
    """Main function"""
    # Check dependencies
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        subprocess.run(['ffprobe', '-version'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Please install ffmpeg and ffprobe: sudo apt install ffmpeg")
        sys.exit(1)

    # Parse arguments
    input_dir, output_dir = parse_arguments()

    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process files
    mkv_files = sorted(input_dir.glob('*.mkv'))

    if not mkv_files:
        print("No MKV files found.")
        return

    print(f"Processing {len(mkv_files)} MKV file(s)...")

    success_count = 0
    for i, mkv_file in enumerate(mkv_files, 1):
        # Find the best complete English subtitle (not forced)
        subtitle_index = find_complete_english_subtitle(str(mkv_file))

        if not subtitle_index:
            print(f"{i}. {mkv_file.name} [FAIL: no suitable English subtitle found]")
            continue

        # Set output file with same name but .srt extension
        output_file = output_dir / f"{mkv_file.stem}.srt"

        if extract_subtitle(str(mkv_file), output_file, subtitle_index, i):
            success_count += 1

    print(
        f"Processing complete! {success_count}/{len(mkv_files)} file(s) processed.")


if __name__ == "__main__":
    main()
