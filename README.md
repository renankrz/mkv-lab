# MKV Lab

A toolkit for automating, cleaning, and managing video and subtitle files, focused on MKV, MP4, and SRT formats.

## Features

- **extract_srt.py**: Extracts English subtitles from MKV files, preferring the least polluted tracks.
- **fix_cc.py**: Interactively cleans CC/SDH elements from SRT subtitles, removing noise and improving readability.
- **frag.py**: Analyzes file fragmentation in a directory, listing the most fragmented files.
- **make_mkv.py**: Converts MP4+SRT pairs to MKV files with embedded English subtitles.
- **rename.py**: Renames files using names from an external file, supporting append and replace modes.
- **streams.py**: Lists stream information from media files using FFmpeg.
- **track_filter.py**: Processes MKV files, keeping selected subtitles (Portuguese/English) and audio tracks.
- **upper.py**: Renames files to UPPERCASE, keeping extensions lowercase.

## Usage

Each script is standalone and can be run from the command line. See the docstring and argument help in each file for usage examples.

Example:
```bash
python3 src/extract_srt.py <input_dir> [output_dir]
python3 src/fix_cc.py <subtitle.srt>
python3 src/frag.py <directory> [num_files]
python3 src/make_mkv.py <input_dir> <output_dir>
python3 src/rename.py <input_dir> <names_file> [--append]
python3 src/streams.py <file>
python3 src/track_filter.py [--pt] [--en] [--default=pt|en] [--audio=pt|en|jp] <input_dir> <output_dir>
python3 src/upper.py <directory>
```

## Requirements

- Python 3.6+
- FFmpeg and FFprobe (for video/subtitle processing)
- e2fsprogs (for filefrag, used in frag.py)
- pytest (for running unit tests)

All Python dependencies are listed in `requirements.txt`. To install them in your virtual environment:

```bash
pip install -r requirements.txt
```

## Project Structure

- `src/` — All main scripts
- `test/` — Unit tests for cleaning and subtitle logic
