#!/bin/bash
# Script to add GPL v3 headers to all d3kOS source files

PYTHON_HEADER="# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com
"

SHELL_HEADER="#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com
"

# Function to add header to Python file
add_python_header() {
    local file="$1"
    local temp_file="${file}.tmp"

    # Check if file already has GPL header
    if grep -q "GNU General Public License" "$file" 2>/dev/null || grep -q "skipperdon@atmyboat.com" "$file" 2>/dev/null; then
        echo "  Skipping $file (already has GPL header)"
        return
    fi

    # Check if file has shebang
    if head -n1 "$file" | grep -q "^#!"; then
        # Keep shebang, add header after it
        head -n1 "$file" > "$temp_file"
        echo "$PYTHON_HEADER" >> "$temp_file"
        tail -n +2 "$file" >> "$temp_file"
    else
        # No shebang, add header at top
        echo "$PYTHON_HEADER" > "$temp_file"
        cat "$file" >> "$temp_file"
    fi

    mv "$temp_file" "$file"
    echo "  ✓ Added GPL header to $file"
}

# Function to add header to shell script
add_shell_header() {
    local file="$1"
    local temp_file="${file}.tmp"

    # Check if file already has GPL header
    if grep -q "GNU General Public License" "$file" 2>/dev/null || grep -q "skipperdon@atmyboat.com" "$file" 2>/dev/null; then
        echo "  Skipping $file (already has GPL header)"
        return
    fi

    # Shell scripts always need shebang - replace or add header after
    if head -n1 "$file" | grep -q "^#!"; then
        # Has shebang, replace it with our header (which includes shebang)
        echo "$SHELL_HEADER" > "$temp_file"
        tail -n +2 "$file" >> "$temp_file"
    else
        # No shebang, add full header
        echo "$SHELL_HEADER" > "$temp_file"
        cat "$file" >> "$temp_file"
    fi

    mv "$temp_file" "$file"
    chmod +x "$file"
    echo "  ✓ Added GPL header to $file"
}

echo "Adding GPL v3 headers to d3kOS source files..."
echo ""

# Process Python files
echo "Processing Python files:"
find /home/boatiq/Helm-OS -name "*.py" -type f | while read file; do
    add_python_header "$file"
done

echo ""
echo "Processing Shell scripts:"
find /home/boatiq/Helm-OS -name "*.sh" -type f | while read file; do
    add_shell_header "$file"
done

echo ""
echo "Done! GPL v3 headers added to all source files."
echo "LICENSE file updated at /home/boatiq/Helm-OS/LICENSE"
