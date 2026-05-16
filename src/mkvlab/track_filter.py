#!/usr/bin/env python3
"""
Filter MKV tracks: keep selected subtitles (PT and/or EN) and optionally one
audio track in a chosen language.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .ffmpeg import (
    SubtitleSelection,
    ensure_ffmpeg_toolchain,
    filter_tracks,
    select_audio_track,
    select_english_subtitle_default,
    select_portuguese_subtitle,
)

# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments, validating mutually-dependent flags."""
    parser = argparse.ArgumentParser(
        description="Process MKV files keeping selected subtitles and audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pt ./videos ./output
  %(prog)s --en --default=en --audio=en ./movies ./processed
  %(prog)s --pt --en --default=pt --audio=pt ./series ./final
        """,
    )

    parser.add_argument(
        "--pt",
        action="store_true",
        help="Keep Portuguese subtitles (prefers pt-BR over pt-PT)",
    )
    parser.add_argument("--en", action="store_true", help="Keep English subtitles")
    parser.add_argument(
        "--default",
        choices=["pt", "en"],
        help="Default subtitle language (required when both --pt and --en are given)",
    )
    parser.add_argument(
        "--audio",
        choices=["pt", "en", "jp"],
        help="Keep only the audio track in the specified language",
    )

    parser.add_argument("input_dir", help="Input directory containing MKV files")
    parser.add_argument("output_dir", help="Output directory for processed files")

    args = parser.parse_args()

    if not args.pt and not args.en:
        parser.error("Specify at least one subtitle language (--pt and/or --en)")

    if args.pt and args.en and not args.default:
        parser.error("With both --pt and --en, --default is required")

    if not args.default:
        args.default = "pt" if args.pt else "en"

    if (args.default == "pt" and not args.pt) or (args.default == "en" and not args.en):
        parser.error(
            f"Default subtitle '{args.default}' is not among the selected ones"
        )

    args.input_dir = Path(args.input_dir)
    args.output_dir = Path(args.output_dir)
    return args


# --------------------------------------------------------------------------- #
# Core processing
# --------------------------------------------------------------------------- #


def process_mkv_file(
    mkv_file: Path,
    output_file: Path,
    *,
    keep_pt: bool,
    keep_en: bool,
    default_lang: str,
    audio_lang: str | None,
    file_index: int,
) -> bool:
    """Process a single MKV file, writing the filtered output to ``output_file``."""
    file_name = mkv_file.name
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_name(f"{output_file.stem}_temp.mkv")

    pt_index = select_portuguese_subtitle(str(mkv_file)) if keep_pt else None
    en_index = select_english_subtitle_default(str(mkv_file)) if keep_en else None
    audio_index = select_audio_track(str(mkv_file), audio_lang) if audio_lang else None

    if keep_pt and pt_index is None:
        print(f"{file_index}. {file_name} [FAIL: PT subtitle not found]")
        return False
    if keep_en and en_index is None:
        print(f"{file_index}. {file_name} [FAIL: EN subtitle not found]")
        return False
    if audio_lang and audio_index is None:
        print(f"{file_index}. {file_name} [FAIL: audio {audio_lang.upper()} not found]")
        return False

    selections: list[SubtitleSelection] = []
    if pt_index is not None:
        selections.append(
            SubtitleSelection("pt", pt_index, is_default=default_lang == "pt")
        )
    if en_index is not None:
        selections.append(
            SubtitleSelection("en", en_index, is_default=default_lang == "en")
        )

    try:
        filter_tracks(
            str(mkv_file),
            temp_file,
            subtitles=selections,
            audio_index=audio_index,
        )
        if temp_file.exists():
            if output_file.exists():
                output_file.unlink()
            shutil.move(str(temp_file), str(output_file))
    except subprocess.CalledProcessError:
        print(f"{file_index}. {file_name} [FAIL: ffmpeg error]")
        if temp_file.exists():
            temp_file.unlink()
        return False
    except OSError:
        print(f"{file_index}. {file_name} [FAIL: file error]")
        if temp_file.exists():
            temp_file.unlink()
        return False

    print(f"{file_index}. {file_name} [OK]")
    return True


def main() -> None:
    ensure_ffmpeg_toolchain()
    args = parse_arguments()

    if not args.input_dir.is_dir():
        print(f"Error: Input directory not found: {args.input_dir}")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    mkv_files = sorted(args.input_dir.glob("*.mkv"))
    if not mkv_files:
        print("No MKV files found.")
        return

    print(f"Processing {len(mkv_files)} MKV file(s)...")
    success = 0
    for i, mkv_file in enumerate(mkv_files, start=1):
        output_file = args.output_dir / mkv_file.name
        if process_mkv_file(
            mkv_file,
            output_file,
            keep_pt=args.pt,
            keep_en=args.en,
            default_lang=args.default,
            audio_lang=args.audio,
            file_index=i,
        ):
            success += 1

    print(f"Processing completed! {success}/{len(mkv_files)} file(s) processed.")


if __name__ == "__main__":
    main()
