#!/bin/bash
#
# Pre-Image Cleanup Script for d3kOS
# Cleans up temporary files, caches, and logs before creating SD card image
#
# Usage: sudo ./pre-image-cleanup.sh
#

set -e

echo "==============================================="
echo "d3kOS Pre-Image Cleanup"
echo "==============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (sudo ./pre-image-cleanup.sh)"
    exit 1
fi

# Show disk usage before cleanup
echo "Disk usage BEFORE cleanup:"
df -h / | tail -1
echo ""

# 1. Clean APT cache
echo "[1/12] Cleaning APT package cache..."
apt-get clean
apt-get autoclean
echo "  ✓ APT cache cleaned"

# 2. Remove old kernels (keep current)
echo "[2/12] Checking for old kernels..."
CURRENT_KERNEL=$(uname -r)
OLD_KERNELS=$(dpkg -l 'linux-image-*' | grep '^ii' | awk '{print $2}' | grep -v "$CURRENT_KERNEL" || true)
if [ -n "$OLD_KERNELS" ]; then
    echo "  Found old kernels, removing..."
    apt-get autoremove --purge -y $OLD_KERNELS
    echo "  ✓ Old kernels removed"
else
    echo "  ✓ No old kernels to remove"
fi

# 3. Clean temporary files
echo "[3/12] Cleaning temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*
echo "  ✓ Temporary files cleaned"

# 4. Clean log files (keep structure, truncate content)
echo "[4/12] Truncating log files..."
find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
find /var/log -type f -name "*.log.*" -delete
journalctl --vacuum-time=1d
echo "  ✓ Log files truncated"

# 5. Clean bash history for all users
echo "[5/12] Cleaning bash history..."
rm -f /root/.bash_history
rm -f /home/*/.bash_history
history -c
echo "  ✓ Bash history cleaned"

# 6. Clean Python cache
echo "[6/12] Cleaning Python cache..."
find /opt/d3kos /home -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find /opt/d3kos /home -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Python cache cleaned"

# 7. Clean Chromium cache (d3kos user)
echo "[7/12] Cleaning Chromium cache..."
rm -rf /home/d3kos/.cache/chromium/* 2>/dev/null || true
rm -rf /home/d3kos/.config/chromium/Default/Cache/* 2>/dev/null || true
rm -rf /home/d3kos/.config/chromium/Default/Code\ Cache/* 2>/dev/null || true
echo "  ✓ Chromium cache cleaned"

# 8. Clean Node-RED cache
echo "[8/12] Cleaning Node-RED cache..."
rm -rf /home/d3kos/.node-red/.npm/* 2>/dev/null || true
echo "  ✓ Node-RED cache cleaned"

# 9. Clean old backup files
echo "[9/12] Cleaning old backup files..."
find /opt/d3kos -type f -name "*.bak" -mtime +7 -delete 2>/dev/null || true
find /var/www/html -type f -name "*.bak" -mtime +7 -delete 2>/dev/null || true
echo "  ✓ Old backup files cleaned"

# 10. Clean swap file if exists
echo "[10/12] Disabling swap..."
swapoff -a 2>/dev/null || true
echo "  ✓ Swap disabled"

# 11. Clean SSH known_hosts (will be regenerated)
echo "[11/12] Cleaning SSH known_hosts..."
rm -f /home/d3kos/.ssh/known_hosts
rm -f /root/.ssh/known_hosts
echo "  ✓ SSH known_hosts cleaned"

# 12. Clean systemd journal
echo "[12/12] Cleaning systemd journal..."
journalctl --rotate
journalctl --vacuum-size=10M
echo "  ✓ Systemd journal cleaned"

echo ""
echo "==============================================="
echo "Cleanup Complete!"
echo "==============================================="
echo ""

# Show disk usage after cleanup
echo "Disk usage AFTER cleanup:"
df -h / | tail -1
echo ""

echo "IMPORTANT NOTES:"
echo "1. System is ready for imaging"
echo "2. Bash history has been cleared"
echo "3. Logs have been truncated (will regenerate)"
echo "4. SSH known_hosts cleared (will regenerate)"
echo "5. Swap is disabled (will re-enable on boot)"
echo ""
echo "You can now shutdown and create the image:"
echo "  sudo shutdown -h now"
echo ""
