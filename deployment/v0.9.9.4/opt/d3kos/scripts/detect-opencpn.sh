#!/bin/bash
# detect-opencpn.sh - Detect OpenCPN installation for Tier 2 auto-upgrade
# Part of d3kOS Tier Management System

set -e

OPENCPN_PATHS=(
    "/usr/bin/opencpn"
    "/usr/local/bin/opencpn"
    "/opt/opencpn/bin/opencpn"
)

# Check if OpenCPN is installed
for path in "${OPENCPN_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "true"
        exit 0
    fi
done

# Check via dpkg (Debian package manager)
if dpkg -l | grep -q "^ii.*opencpn"; then
    echo "true"
    exit 0
fi

# Check via flatpak
if command -v flatpak &> /dev/null; then
    if flatpak list | grep -q "opencpn"; then
        echo "true"
        exit 0
    fi
fi

echo "false"
exit 0
