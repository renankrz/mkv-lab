#!/usr/bin/env python3
"""
Processes MKV files, keeping selected subtitles and audio tracks.
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path


def parse_arguments():
    """Parses command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Processes MKV files keeping selected subtitles and audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pt ./videos ./output
  %(prog)s --en --default=en --audio=en ./movies ./processed
  %(prog)s --pt --en --default=pt --audio=pt ./series ./final
        """
    )

    # Subtitle options
    parser.add_argument('--pt', action='store_true',
                        help='Keep Portuguese subtitles')
    parser.add_argument('--en', action='store_true',
                        help='Keep English subtitles')
    parser.add_argument(
        '--default', choices=['pt', 'en'], help='Default subtitle (required with --pt and --en)')

    # Audio option
    parser.add_argument('--audio', choices=['pt', 'en', 'jp'],
                        help='Keep only audio in the specified language')

    # Directories
    parser.add_argument(
        'input_dir', help='Input directory with MKV files')
    parser.add_argument(
        'output_dir', help='Output directory for processed files')

    args = parser.parse_args()

    # Validations
    if not args.pt and not args.en:
        parser.error("Specify at least one subtitle (--pt and/or --en)")

    if args.pt and args.en and not args.default:
        parser.error("With --pt and --en, --default is required")

    # Automatically set default if only one subtitle
    if not args.default:
        args.default = 'pt' if args.pt else 'en'

    # Check if default matches selected subtitles
    if (args.default == 'pt' and not args.pt) or (args.default == 'en' and not args.en):
        parser.error(
            f"Default subtitle '{args.default}' is not among the selected ones")
    return args.pt, args.en, args.default, args.audio, Path(args.input_dir), Path(args.output_dir)


def find_audio_track(input_file, target_lang):
    """Finds the index of the audio track in the specified language"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'stream=index:stream_tags=language',
            '-select_streams', 'a',
            input_file
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        current_index = None
        found_index = None

        for line in output.split('\n'):
            if line.startswith('index='):
                current_index = line.split('=')[1]
            elif line.startswith('TAG:language='):
                lang = line.split('=')[1].strip().lower()

                # Maps common language variations
                lang_variations = {
                    'pt': ['pt', 'por', 'portuguese', 'pt-br', 'pt_br', 'ptbr', 'por-br', 'por_br', 'porbr', 'bra', 'brasil', 'brazil'],
                    'en': ['en', 'eng', 'english', 'en-us', 'en_us', 'enus', 'en-gb', 'en_gb', 'engb'],
                    'jp': ['jp', 'jpn', 'japanese', 'ja', 'jap']
                }

                # Checks if the found language matches the target language
                if lang in lang_variations.get(target_lang, []):
                    found_index = current_index
                    break  # Gets the first track found in the desired language

        return found_index

    except subprocess.CalledProcessError:
        return None


def find_portuguese_subtitle(input_file):
    """Finds the index of the Portuguese subtitle, preferring pt-BR"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'stream=index:stream_tags=language',
            '-select_streams', 's',
            input_file
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        pt_br_index = None
        pt_index = None
        current_index = None

        for line in output.split('\n'):
            if line.startswith('index='):
                current_index = line.split('=')[1]
            elif line.startswith('TAG:language='):
                lang = line.split('=')[1].strip().lower()

                if lang in ('pt-br', 'pt_br', 'ptbr', 'por-br', 'por_br', 'porbr', 'bra', 'brasil', 'brazil'):
                    pt_br_index = current_index
                elif lang in ('pt', 'por', 'portuguese') and pt_br_index is None:
                    pt_index = current_index

        return pt_br_index if pt_br_index is not None else pt_index

    except subprocess.CalledProcessError:
        return None


def find_english_subtitle(input_file):
    """Finds the index of the English subtitle (prefers non-forced)"""
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

        normal_sub_index = None
        forced_sub_index = None
        hearing_impaired_sub_index = None

        current_index = None
        current_lang = None
        current_title = None
        current_forced = False
        current_hearing_impaired = False

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
                # Process complete stream
                if current_lang and current_lang in ('en', 'eng', 'english'):
                    # Checks if it's special by the title
                    title_special = False
                    if current_title:
                        title_special = any(special in current_title
                                            for special in ['forced', 'sdh', 'hi', 'hearing', 'signs', 'dub'])

                    is_special = current_forced or current_hearing_impaired or title_special

                    if not is_special:
                        normal_sub_index = current_index
                    elif current_forced:
                        forced_sub_index = current_index
                    elif current_hearing_impaired or title_special:
                        hearing_impaired_sub_index = current_index

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

        # Preference order
        return normal_sub_index or forced_sub_index or hearing_impaired_sub_index

    except subprocess.CalledProcessError:
        return None


def process_mkv_file(input_file, output_file, keep_pt, keep_en, default_lang, audio_lang, file_index):
    """Processes an MKV file keeping the specified subtitles and audio"""
    input_path = Path(input_file)
    file_name = input_path.name

    # Ensures output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_name(f"{output_file.stem}_temp.mkv")

    # Finds subtitles
    pt_sub_index = find_portuguese_subtitle(input_file) if keep_pt else None
    en_sub_index = find_english_subtitle(input_file) if keep_en else None

    # Finds audio if specified
    audio_index = find_audio_track(
        input_file, audio_lang) if audio_lang else None

    # Validates found subtitles
    if keep_pt and not pt_sub_index:
        print(f"{file_index}. {file_name} [FAIL: PT subtitle not found]")
        return False
    if keep_en and not en_sub_index:
        print(f"{file_index}. {file_name} [FAIL: EN subtitle not found]")
        return False

    # Validates found audio
    if audio_lang and not audio_index:
        print(
            f"{file_index}. {file_name} [FAIL: audio {audio_lang.upper()} not found]")
        return False

    try:
        # Builds ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_file,
            '-map', '0:v', '-c', 'copy',
        ]

        # Adds selected audio or all audio tracks
        if audio_index:
            ffmpeg_cmd.extend(['-map', f'0:{audio_index}'])
        else:
            ffmpeg_cmd.extend(['-map', '0:a'])

        # Adds selected subtitles
        subtitle_dispositions = []
        if pt_sub_index:
            ffmpeg_cmd.extend(['-map', f'0:{pt_sub_index}'])
            subtitle_dispositions.append(('pt', pt_sub_index))
        if en_sub_index:
            ffmpeg_cmd.extend(['-map', f'0:{en_sub_index}'])
            subtitle_dispositions.append(('en', en_sub_index))

        # Sets subtitle metadata
        for i, (lang, _) in enumerate(subtitle_dispositions):
            ffmpeg_cmd.extend([
                f'-metadata:s:s:{i}', f'language={lang}',
                f'-metadata:s:s:{i}', f'title={lang.upper()}',
            ])
            if lang == default_lang:
                ffmpeg_cmd.extend([f'-disposition:s:{i}', 'default'])

        # Sets audio codec (copy to keep quality)
        ffmpeg_cmd.extend(['-c:a', 'copy'])

        ffmpeg_cmd.append(str(temp_file))

        # Executes conversion
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)

        # Moves final file
        if temp_file.exists():
            if output_file.exists():
                output_file.unlink()
            shutil.move(str(temp_file), str(output_file))

        print(f"{file_index}. {file_name} [OK]")
        return True

    except subprocess.CalledProcessError:
        print(f"{file_index}. {file_name} [FAIL: ffmpeg error]")
        if temp_file.exists():
            temp_file.unlink()
        return False
    except OSError as e:
        print(f"{file_index}. {file_name} [FAIL: file error]")
        if temp_file.exists():
            temp_file.unlink()
        return False


def main():
    """Main function"""
    # Checks dependencies
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        subprocess.run(['ffprobe', '-version'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Install ffmpeg and ffprobe: sudo apt install ffmpeg")
        sys.exit(1)

    # Parse arguments
    keep_pt, keep_en, default_lang, audio_lang, input_dir, output_dir = parse_arguments()

    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Creates output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Processes files
    mkv_files = sorted(input_dir.glob('*.mkv'))

    if not mkv_files:
        print("No MKV files found.")
        return

    print(f"Processing {len(mkv_files)} MKV file(s)...")

    success_count = 0
    for i, mkv_file in enumerate(mkv_files, 1):
        output_file = output_dir / mkv_file.name
        if process_mkv_file(str(mkv_file), output_file, keep_pt, keep_en, default_lang, audio_lang, i):
            success_count += 1

    print(
        f"Processing completed! {success_count}/{len(mkv_files)} file(s) processed.")


if __name__ == "__main__":
    main()
