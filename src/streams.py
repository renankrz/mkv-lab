#!/usr/bin/env python3
"""
Lists stream information from media files using FFmpeg.
"""

import subprocess
import sys
import os


def streams(filename):
    # Check if the file exists
    if not os.path.isfile(filename):
        print(
            f"Error: The file '{filename}' was not found in the current directory.")
        return 1

    # Build the command
    command = ['ffmpeg', '-hide_banner', '-i', filename]

    try:
        # Run the command and capture the output
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True)

        # Filter lines containing "Stream"
        for line in result.stderr.split('\n'):
            if 'Stream' in line:
                print(line)

        return 0
    except FileNotFoundError:
        print("Error: The command 'ffmpeg' was not found. Make sure FFmpeg is installed.")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    script_name = os.path.basename(sys.argv[0])
    if len(sys.argv) != 2:
        print(f"Usage: {script_name} <file>")
        print(f"Example: {script_name} S01E10.mkv")
        sys.exit(1)

    filename = sys.argv[1]
    sys.exit(streams(filename))
