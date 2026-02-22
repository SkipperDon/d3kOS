#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# This script should be copied to /opt/d3kos/scripts/package-release.sh on the Pi
# See INSTALLATION_GUIDE.md for deployment instructions

echo "This is the d3kOS packaging script"
echo "Copy to: /opt/d3kos/scripts/package-release.sh"
echo ""
echo "Usage: sudo ./package-release.sh [version] [source] [output_dir]"
echo "Example: sudo ./package-release.sh 1.0.3 /dev/mmcblk0 /mnt/usb/releases"
