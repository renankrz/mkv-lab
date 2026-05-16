#!/usr/bin/env python3
"""
Unified CLI entrypoint for mkvlab.

Usage:
    mkvlab <command> [args...]

Commands:
    extract-srt   Extract English subtitles from MKV files
    fix-cc        Interactively clean CC/SDH elements from SRT subtitles
    make-mkv      Convert MP4+SRT pairs to MKV with embedded subtitles
    resub-mkv     Replace subtitle streams in MKV files with SRT
    streams       List stream information from media files
    track-filter  Process MKV files keeping selected subtitles and audio
"""

import sys

COMMANDS = {
    "extract-srt": "mkvlab.extract_srt",
    "fix-cc": "mkvlab.fix_cc",
    "make-mkv": "mkvlab.make_mkv",
    "resub-mkv": "mkvlab.resub_mkv",
    "streams": "mkvlab.streams",
    "track-filter": "mkvlab.track_filter",
}


def print_help():
    print("Usage: mkvlab <command> [args...]\n")
    print("Commands:")
    print("  extract-srt    Extract English subtitles from MKV files")
    print("  fix-cc         Interactively clean CC/SDH elements from SRT subtitles")
    print("  make-mkv       Convert MP4+SRT pairs to MKV with embedded subtitles")
    print("  resub-mkv      Replace subtitle streams in MKV files with SRT")
    print("  streams        List stream information from media files")
    print("  track-filter   Process MKV files keeping selected subtitles and audio")
    print("\nUse 'mkvlab <command> --help' for more information on a command.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)

    command = sys.argv[1]

    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)

    # Remove 'mkvlab' from argv so the subcommand sees itself as sys.argv[0]
    sys.argv = sys.argv[1:]
    # Rewrite argv[0] to look like 'mkvlab <command>'
    sys.argv[0] = f"mkvlab {command}"

    # Import and run the subcommand's main()
    module_name = COMMANDS[command]
    module = __import__(module_name, fromlist=["main"])
    module.main()


if __name__ == "__main__":
    main()
