#!/usr/bin/env bash

# Script to set executable permissions and create symbolic
# links in $HOME/.local/bin for Python scripts in the src/ directory.

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SRC_DIR="$SCRIPT_DIR/src"
BIN_DIR="$HOME/.local/bin"

echo "Processing .py files in: $SRC_DIR"
echo "-------------------------------------"

shopt -s nullglob
files=("$SRC_DIR"/*.py)

if [ ${#files[@]} -eq 0 ]; then
    echo "No .py files found in src/"
    exit 1
fi

mkdir -p "$BIN_DIR"

for file in "${files[@]}"; do
    fname="$(basename "$file")"

    # Ignore Python special files like __init__.py, __main__.py, etc.
    [[ "$fname" == __*.py ]] && continue

    link_name="${fname%.py}"

    echo "Processing: $fname"

    chmod 755 "$file"
    echo "  ✓ Permissions set"

    ln -sf "$file" "$BIN_DIR/$link_name"
    echo "  ✓ Symlink created: $BIN_DIR/$link_name"

    echo
done

echo "Processing completed!"
