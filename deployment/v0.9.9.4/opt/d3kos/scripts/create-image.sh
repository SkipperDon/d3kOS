#!/bin/bash
# d3kOS Image Creation Script

VERSION="0.9.1.2"
DATE=$(date +%Y%m%d)
IMAGE_NAME="d3kos-v${VERSION}-${DATE}.img"
OUTPUT_DIR="/opt/d3kos/images"

echo "=== d3kOS Image Builder v${VERSION} ==="
echo ""

# Check if running on Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Error: Must run on Raspberry Pi"
    exit 1
fi

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Must run as root (use sudo)"
    exit 1
fi

# Display system info
echo "Raspberry Pi Model: $(cat /proc/device-tree/model)"
echo "d3kOS Version: $VERSION"
echo "Output: ${OUTPUT_DIR}/${IMAGE_NAME}.gz"
echo ""

# Confirmation
read -p "This will create a full SD card image. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Image creation cancelled"
    exit 0
fi

mkdir -p "$OUTPUT_DIR"

echo ""
echo "Step 1: Pre-image cleanup..."
echo "  - Cleaning APT cache..."
apt-get clean
echo "  - Vacuuming journal logs (limit to 50MB)..."
journalctl --vacuum-size=50M
echo "  - Removing temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*
echo "  - Cleanup complete"

echo ""
echo "Step 2: Creating image from SD card..."
echo "This will take 30-60 minutes depending on SD card size..."
echo ""

# Detect SD card device
SD_DEVICE="/dev/mmcblk0"
if [ ! -b "$SD_DEVICE" ]; then
    echo "Error: SD card device not found at $SD_DEVICE"
    exit 1
fi

# Get SD card size
SD_SIZE=$(blockdev --getsize64 $SD_DEVICE)
SD_SIZE_GB=$((SD_SIZE / 1024 / 1024 / 1024))

echo "SD Card: $SD_DEVICE (${SD_SIZE_GB}GB)"
echo "Starting image creation..."
echo ""

# Use dd to create image with progress
dd if=$SD_DEVICE of="${OUTPUT_DIR}/${IMAGE_NAME}" bs=4M status=progress

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Image creation failed"
    exit 1
fi

echo ""
echo "Step 3: Compressing image..."
echo "This may take 10-20 minutes..."
echo ""

gzip -9 "${OUTPUT_DIR}/${IMAGE_NAME}"

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Compression failed"
    exit 1
fi

IMAGE_SIZE=$(du -h "${OUTPUT_DIR}/${IMAGE_NAME}.gz" | cut -f1)
IMAGE_PATH="${OUTPUT_DIR}/${IMAGE_NAME}.gz"

echo ""
echo "========================================="
echo "✓ Image created successfully!"
echo "========================================="
echo ""
echo "Location: ${IMAGE_PATH}"
echo "Size: ${IMAGE_SIZE}"
echo ""
echo "SHA-256 checksum:"
sha256sum "${IMAGE_PATH}"
echo ""
echo "To verify the checksum later:"
echo "  sha256sum ${IMAGE_PATH}"
echo ""
echo "To flash to a new SD card:"
echo "  gunzip -c ${IMAGE_PATH} | sudo dd of=/dev/sdX bs=4M status=progress"
echo "  (replace /dev/sdX with your SD card device)"
echo ""
echo "Image creation complete!"
