# MKV Lab

A toolkit for automating, cleaning, and managing video and subtitle files, focused on MKV and SRT formats.

## Installation

```bash
pip install -e .
```

This installs the `mkvlab` command-line tool.

## Features

- **extract-srt**: Extracts English subtitles from MKV files, preferring the least polluted tracks.
- **fix-cc**: Interactively cleans CC/SDH elements from SRT subtitles, removing noise and improving readability.
- **make-mkv**: Converts MP4+SRT pairs to MKV files with embedded English subtitles.
- **resub-mkv**: Replaces subtitle streams in MKV files with a corresponding SRT file.
- **streams**: Lists stream information from media files using FFmpeg.
- **track-filter**: Processes MKV files, keeping selected subtitles (Portuguese/English) and audio tracks.

## Usage

```bash
mkvlab <command> [args...]
mkvlab --help
mkvlab extract-srt <input_dir> [output_dir]
mkvlab fix-cc <subtitle.srt>
mkvlab make-mkv <input_dir> <output_dir>
mkvlab resub-mkv <input_dir> <output_dir>
mkvlab streams <file>
mkvlab track-filter [--pt] [--en] [--default=pt|en] [--audio=pt|en|jp] <input_dir> <output_dir>
```

## Requirements

- Python 3.10+
- FFmpeg and FFprobe (for video/subtitle processing)
- pytest (for running unit tests)

```bash
pip install -r requirements.txt
```

## Project Structure

- `src/mkvlab/` — Main package (CLI + all commands)
- `test/` — Unit tests
- `scripts-misc/` — Utility scripts not related to MKV (rename, upper, frag)
