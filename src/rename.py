#!/usr/bin/env python3
"""
Renames files using names from an external file.
"""

import argparse
import sys
from pathlib import Path


def rename_files(input_dir, names_file, append_mode=True):
    """
    Renames files using names from an external file
    Append mode: adds the name to the original
    Replace mode: completely replaces the name
    """
    input_path = Path(input_dir)
    names_path = Path(names_file)

    # Check if input directory exists
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Input directory '{input_dir}' not found!")
        return False

    # Check if names file exists
    if not names_path.exists():
        print(f"Error: Names file '{names_file}' not found!")
        return False

    # Read names from file
    try:
        with open(names_path, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading names file: {e}")
        return False

    # List files in directory (ignore subdirectories)
    try:
        files = [f for f in input_path.iterdir() if f.is_file()]
        files.sort()  # Sort to ensure consistent order
    except Exception as e:
        print(f"Error listing files in directory: {e}")
        return False

    # Check if counts match
    if len(files) != len(names):
        print(
            f"Error: Number of files ({len(files)}) does not match number of names ({len(names)})!")
        return False

    mode = "APPEND" if append_mode else "REPLACE"
    print(f"Processing {len(files)} file(s) in {mode} mode...")

    # Rename the files
    success_count = 0
    for i, (old_file, new_name_text) in enumerate(zip(files, names), 1):
        # Determine new name based on mode
        if append_mode:
            # Append mode
            name_base = old_file.stem
            extension = old_file.suffix
            new_name = f"{name_base}{new_name_text}{extension}"
        else:
            # Replace mode
            extension = old_file.suffix
            new_name = f"{new_name_text}{extension}"

        new_path = old_file.parent / new_name

        try:
            old_file.rename(new_path)
            print(f"{i}. {old_file.name} -> {new_name}")
            success_count += 1

        except Exception as e:
            print(f"{i}. {old_file.name} [FAIL: {e}]")

    return success_count == len(files)


def main():
    parser = argparse.ArgumentParser(
        description='Renames files using names from an external file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /media/john/S03 ./full-names.txt          (replace mode)
  %(prog)s --append /media/john/S03 ./names-append.txt    (append mode)
  %(prog)s -a ./photos /path/name_list.txt           (append mode)

The names file must contain one name per line, in the same order as the files.
        """
    )

    parser.add_argument(
        'input_dir',
        help='Directory containing the files to be renamed'
    )
    parser.add_argument(
        'names',
        help='File containing the names (one per line)'
    )
    parser.add_argument(
        '-a', '--append',
        action='store_true',
        help='Append mode: adds the name to the original (default: replace mode)'
    )

    args = parser.parse_args()

    # Append mode is activated by the flag, default mode is replace
    if rename_files(args.input_dir, args.names, append_mode=args.append):
        mode = "APPEND" if args.append else "REPLACE"
        print(f"Renaming in {mode} mode completed successfully!")
    else:
        print("Renaming completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
