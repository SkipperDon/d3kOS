# d3kOS Image Build Guide

**Version**: 0.9.1.2
**Date**: February 20, 2026

---

## Overview

This guide explains how to create a distributable d3kOS image from a running Raspberry Pi installation.

---

## Prerequisites

### Hardware Requirements
- Raspberry Pi 4B with d3kOS installed
- 16GB+ SD card (system running on)
- USB drive for image storage (128GB recommended)
- Stable power supply (image creation takes 30-60 minutes)

### Software Requirements
- d3kOS v0.9.1.2 installed and configured
- All services running correctly
- Root access (sudo)

### Time Requirements
- Pre-cleanup: 2-5 minutes
- Image creation: 30-60 minutes (depends on SD card size)
- Compression: 10-20 minutes
- **Total: 45-85 minutes**

---

## Preparation Steps

### 1. Verify System State

Before creating the image, ensure the system is in a clean state:

```bash
# Check d3kOS version
curl http://localhost/license/info | jq '.version'
# Expected: "0.9.1.2"

# Check all services are running
systemctl list-units 'd3kos-*' --state=running --no-pager
# Expected: 15+ services active

# Check tier setting
curl http://localhost/tier/status | jq '.tier'
# Expected: 3 (for testing build)

# Check disk usage
df -h /
# Should have some free space (10%+ recommended)
```

### 2. Remove Sensitive Data

**IMPORTANT**: Remove any sensitive or personal data before creating image:

```bash
# Clear bash history
history -c
cat /dev/null > ~/.bash_history

# Remove SSH known_hosts (will regenerate on first boot)
rm -f ~/.ssh/known_hosts

# Clear temporary files
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Review and remove any test data
# - /opt/d3kos/data/boatlog.db (if contains test entries)
# - /opt/d3kos/data/exports/ (test exports)
# - /home/d3kos/camera-recordings/ (test videos/photos)
```

### 3. Optional: Reset to Defaults

If you want a "fresh install" image:

```bash
# Reset installation ID (will regenerate on first boot)
# Only do this if you want each user to have unique ID
sudo rm /opt/d3kos/config/license.json
# NOTE: First-boot service will regenerate it

# Clear onboarding state (user will go through wizard)
sudo rm -f /opt/d3kos/config/onboarding.json
sudo rm -f /opt/d3kos/state/onboarding-reset-count.json
```

---

## Building the Image

### Method 1: Automated Script (Recommended)

```bash
# Run the image build script
sudo /opt/d3kos/scripts/create-image.sh
```

**Script will:**
1. Verify running on Raspberry Pi
2. Check for root privileges
3. Display system information
4. Ask for confirmation
5. Clean APT cache
6. Vacuum journal logs to 50MB
7. Remove temporary files
8. Create full SD card image using dd
9. Compress with gzip -9 (maximum compression)
10. Display SHA-256 checksum
11. Save to `/opt/d3kos/images/`

**Output:**
```
Location: /opt/d3kos/images/d3kos-v0.9.1.2-20260220.img.gz
Size: ~2.5GB (for 16GB SD card)
```

### Method 2: Manual Image Creation

If the script doesn't work, create image manually:

```bash
# 1. Pre-cleanup
sudo apt-get clean
sudo journalctl --vacuum-size=50M
sudo rm -rf /tmp/* /var/tmp/*

# 2. Create image
sudo dd if=/dev/mmcblk0 of=/opt/d3kos/images/d3kos-v0.9.1.2-$(date +%Y%m%d).img bs=4M status=progress

# 3. Compress
gzip -9 /opt/d3kos/images/d3kos-v0.9.1.2-$(date +%Y%m%d).img

# 4. Generate checksum
sha256sum /opt/d3kos/images/d3kos-v0.9.1.2-*.img.gz > /opt/d3kos/images/d3kos-v0.9.1.2-$(date +%Y%m%d).img.gz.sha256
```

---

## Image Verification

### Verify Checksum

```bash
# Generate checksum
sha256sum /opt/d3kos/images/d3kos-v0.9.1.2-*.img.gz

# Save to file
sha256sum /opt/d3kos/images/d3kos-v0.9.1.2-*.img.gz > /opt/d3kos/images/checksum.txt
```

### Verify Image Integrity

```bash
# Test decompression (without writing)
gunzip -t /opt/d3kos/images/d3kos-v0.9.1.2-*.img.gz

# If no errors, image is valid
echo $?
# Expected: 0
```

---

## Distribution

### 1. Transfer Image to Computer

```bash
# From your computer (not Pi):
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/opt/d3kos/images/d3kos-v0.9.1.2-*.img.gz ~/Downloads/
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/opt/d3kos/images/checksum.txt ~/Downloads/
```

### 2. Upload to GitHub Releases

1. Go to https://github.com/SkipperDon/d3kOS/releases
2. Click "Create new release"
3. Tag: `v0.9.1.2`
4. Title: `d3kOS v0.9.1.2 - Tier 0 Installation Complete`
5. Description: Copy from CHANGELOG.md
6. Attach files:
   - `d3kos-v0.9.1.2-YYYYMMDD.img.gz`
   - `checksum.txt`
7. Check "Set as latest release"
8. Click "Publish release"

### 3. Create Installation Instructions

Include in release notes:

```markdown
## Installation

### Requirements
- Raspberry Pi 4B (4GB+ RAM recommended)
- 16GB+ SD card (32GB+ recommended)
- Etcher or dd tool
- Download: d3kos-v0.9.1.2-YYYYMMDD.img.gz

### Flash to SD Card

**Using Etcher (Recommended):**
1. Download Raspberry Pi Imager or Etcher
2. Select d3kos-v0.9.1.2-YYYYMMDD.img.gz
3. Select your SD card
4. Flash!

**Using dd (Linux/Mac):**
```bash
# Verify checksum
sha256sum d3kos-v0.9.1.2-YYYYMMDD.img.gz

# Flash to SD card
gunzip -c d3kos-v0.9.1.2-YYYYMMDD.img.gz | sudo dd of=/dev/sdX bs=4M status=progress

# Replace /dev/sdX with your SD card device
# Find it with: lsblk
```

### First Boot
1. Insert SD card into Raspberry Pi 4B
2. Connect HDMI display
3. Connect keyboard/mouse
4. Power on
5. System boots to desktop in ~60 seconds
6. Open Chromium browser
7. Navigate to http://localhost or http://d3kos.local
8. Complete onboarding wizard (20 steps)

### Default Credentials
- Username: `d3kos`
- Password: `d3kos2026`
- WiFi AP: SSID `d3kOS`, Password `d3kos-2026`

**⚠️ Change default password after first login!**
```

---

## Image Specifications

### Image Size Expectations

| SD Card Size | Raw Image | Compressed | Compression Ratio |
|--------------|-----------|------------|-------------------|
| 16GB | ~16GB | ~2.5-3GB | ~80-85% |
| 32GB | ~32GB | ~4-5GB | ~80-85% |
| 64GB | ~64GB | ~8-10GB | ~80-85% |

### Included Software

- Debian GNU/Linux 13 (Trixie)
- Raspberry Pi OS (64-bit, headless base)
- Wayland + Labwc compositor
- Chromium browser (kiosk mode)
- Node.js v20.20.0
- Node-RED v4.1.4
- Signal K Server
- d3kOS services (15+ systemd services)
- Python 3.12
- Flask APIs

### d3kOS Version Info

```json
{
  "version": "0.9.1.2",
  "tier": 3,
  "release_date": "2026-02-20",
  "status": "Tier 0 Installation Complete",
  "build": "opensource-testing"
}
```

---

## Troubleshooting

### Image Creation Fails

**Error: "No space left on device"**
- Solution: Clean up disk space before creating image
- Free up at least 1GB on /opt/d3kos/images/ partition

**Error: "dd: error reading '/dev/mmcblk0'"**
- Solution: SD card may be failing, try different card
- Check: `dmesg | tail` for hardware errors

**Error: "Permission denied"**
- Solution: Run with sudo
- Command: `sudo /opt/d3kos/scripts/create-image.sh`

### Compression Takes Too Long

**Slow compression (>30 minutes):**
- Normal for 16GB+ cards
- gzip -9 provides maximum compression (80-85% reduction)
- Alternative: Use gzip -6 for faster compression (70-75% reduction)
  ```bash
  gzip -6 /opt/d3kos/images/d3kos-v0.9.1.2-*.img
  ```

### Image Won't Boot After Flashing

**Black screen on boot:**
- Verify checksum matches (file not corrupted)
- Try reflashing with Etcher instead of dd
- Check HDMI cable and display

**Boots to console instead of desktop:**
- Normal for first boot (services starting)
- Wait 60-90 seconds
- If still console, check: `systemctl status graphical.target`

---

## Best Practices

### Before Creating Image

1. ✅ Complete full testing matrix (see TESTING_MATRIX_v0.9.1.2.md)
2. ✅ Verify all services running
3. ✅ Remove sensitive/personal data
4. ✅ Clear logs and temporary files
5. ✅ Document any custom configurations

### After Creating Image

1. ✅ Verify checksum
2. ✅ Test image on different SD card/Pi (if possible)
3. ✅ Document image creation date and version
4. ✅ Upload to GitHub releases
5. ✅ Update README.md with download link

### Storage

- Keep original uncompressed image (optional, for quick reflash)
- Keep compressed .gz file for distribution
- Keep checksum.txt with image file
- Store in /opt/d3kos/images/ or external USB drive

---

## Next Steps

After creating the image:

1. Test image on fresh SD card
2. Verify onboarding wizard works
3. Verify all services auto-start
4. Upload to GitHub releases
5. Update documentation with download links
6. Announce release to community

---

**Image build complete! Ready for distribution.**
