#!/bin/bash

# Script to set executable permissions and create symbolic
# links in $HOME/bin for Python scripts in the src/ directory.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SRC_DIR="$SCRIPT_DIR/src"

echo "Processing .py files in: $SRC_DIR"
echo "-------------------------------------"

if ! compgen -G "$SRC_DIR/*.py" > /dev/null; then
    echo "No .py files found in src/."
    exit 1
fi

for file in "$SRC_DIR"/*.py; do
    fname="$(basename "$file")"
    # Ensure we are working with a regular file
    if [ -f "$file" ]; then
        echo "Processing: $fname"
        chmod 744 "$file"
        echo "  ✓ Permissions set to 744"
        link_name="${fname%.py}"
        # Remove existing symlink if present to avoid conflicts
        if [ -L "$HOME/bin/$link_name" ]; then
            rm "$HOME/bin/$link_name"
            echo "  ! Existing link removed: ~/bin/$link_name"
        fi
        # Create $HOME/bin if it doesn't exist
        if [ ! -d "$HOME/bin" ]; then
            mkdir -p "$HOME/bin"
            echo "  + ~/bin directory created"
        fi
        # Create symbolic link without .py extension
        ln -s "$file" "$HOME/bin/$link_name"
        # Check if symlink creation was successful
        if [ $? -eq 0 ]; then
            echo "  ✓ Symbolic link created: ~/bin/$link_name -> $fname"
        else
            echo "  ✗ Error creating symbolic link for $fname"
        fi
        echo ""
    fi
done

echo "Processing completed!"
