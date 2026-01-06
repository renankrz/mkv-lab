#!/usr/bin/env python3
"""
Renames files to UPPERCASE, keeping extensions lowercase.
"""


import os
import sys


def rename_files_to_upper(directory):
    """Renames file names (except extension) to UPPERCASE"""
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Ignore directories
        if os.path.isdir(filepath):
            continue

        # Split name and extension
        name, ext = os.path.splitext(filename)
        # Name in uppercase, extension in lowercase
        new_filename = name.upper() + ext.lower()
        new_filepath = os.path.join(directory, new_filename)

        # Avoid renaming if there is no change
        if new_filename != filename:
            try:
                os.rename(filepath, new_filepath)
                print(f"Renamed: {filename} -> {new_filename}")
            except OSError as e:
                print(f"Error renaming {filename}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        print("Use '.' for the current directory")
        sys.exit(1)

    directory = sys.argv[1]
    if directory == ".":
        directory = os.getcwd()

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory")
        sys.exit(1)

    print(
        f"Renaming files in {directory} (keeping extensions lowercase)...")
    rename_files_to_upper(directory)
    print("Done.")
