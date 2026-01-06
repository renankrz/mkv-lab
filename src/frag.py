#!/usr/bin/env python3
"""
Analyzes file fragmentation in a directory.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def analyze_fragmentation(directory, num_files=10):
    """Analyzes files and subdirectories to find the most fragmented files"""
    directory_path = Path(directory)

    # Directory validation
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is invalid.")
        sys.exit(1)

    print(f"Analyzing fragmentation in '{directory}'...")

    # Find all regular files
    files = []
    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            files.append(file_path)

    if not files:
        print("No files found in the directory.")
        return []

    results = []
    total_files = len(files)

    print(f"Processing {total_files} file(s)...")

    for i, file_path in enumerate(files, 1):
        try:
            # Run filefrag to get fragmentation info
            command = ['filefrag', '-v', str(file_path)]
            result = subprocess.run(
                command, capture_output=True, text=True, check=True)

            # Extract number of extents (fragments)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'extents found' in line:
                    # Extract the number before "extents found"
                    match = re.search(r'(\d+)\s+extents? found', line)
                    if match:
                        fragments = int(match.group(1))
                        results.append((file_path, fragments))

            print(f"{i}. {file_path.name} [OK]")

        except subprocess.CalledProcessError as e:
            print(f"{i}. Error analyzing {file_path.name}: {e.stderr.strip()}")
        except FileNotFoundError:
            print(
                "Error: filefrag not found. Install with: sudo apt install e2fsprogs")
            sys.exit(1)
        except Exception as e:
            print(f"{i}. Unexpected error processing {file_path.name}: {str(e)}")

    # Sort by fragmentation (highest first) and get top N
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:num_files]


def format_results(results):
    """Formats the results for display"""
    if not results:
        print("No results found.")
        return

    print("\n" + "="*80)
    print("MOST FRAGMENTED FILES")
    print("="*80)
    print(f"{'Position':<8} {'File':<50} {'Fragments':<12}")
    print("-"*80)

    for i, (file_path, fragments) in enumerate(results, 1):
        filename = str(file_path)
        if len(filename) > 47:
            filename = filename[:44] + "..."

        print(f"{i:<8} {filename:<50} {fragments:<12}")

    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Find the most fragmented files on disk',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /home/user/data
  %(prog)s /var/log 5
  %(prog)s . 20
        """
    )

    parser.add_argument(
        'directory',
        help='Directory to analyze fragmentation'
    )
    parser.add_argument(
        'num_files',
        nargs='?',
        type=int,
        default=10,
        help='Number of files to show (default: 10)'
    )

    args = parser.parse_args()

    results = analyze_fragmentation(args.directory, args.num_files)
    format_results(results)

    if results:
        print(
            f"\nAnalysis complete. Showing top {len(results)} most fragmented files.")
    else:
        print("Analysis complete with no results.")


if __name__ == "__main__":
    main()
