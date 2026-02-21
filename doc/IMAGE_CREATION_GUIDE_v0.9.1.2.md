# d3kOS Image Creation Guide - v0.9.1.2

**Purpose**: Create distributable system image from current d3kOS installation
**Date**: February 21, 2026
**Version**: 0.9.1.2
**Source System**: Raspberry Pi 4B, 16GB SD card, Tier 3 testing build

---

## Prerequisites

**On Ubuntu/WSL Machine:**
- SSH access to Pi: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- 20GB free disk space (for compressed image + working files)
- Tools: `dd`, `gzip`, `sha256sum`, `parted`, `gdrive` (for Google Drive upload)

**On Raspberry Pi:**
- System fully updated and tested
- All services running correctly
- Simulator disabled (if any test data present)

---

## Phase 1: Pre-Image Preparation (ON RASPBERRY PI)

### 1.1 Connect to Pi

```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
```

### 1.2 Clean System Before Imaging

```bash
# Remove temporary files
sudo rm -rf /tmp/* /var/tmp/*
sudo rm -rf /home/d3kos/.cache/*
sudo rm -rf /home/d3kos/.local/share/Trash/*

# Clear journal logs older than 7 days (keep recent for debugging)
sudo journalctl --vacuum-time=7d

# Remove bash history (will contain development commands)
history -c
rm ~/.bash_history

# Remove SSH authorized keys for security (users will add their own)
# SKIP THIS - Keep d3kos_key for access

# Clear APT cache
sudo apt-get clean
sudo apt-get autoclean

# Remove old kernel packages (if any)
sudo apt-get autoremove --purge -y

# Clear systemd failed units
sudo systemctl reset-failed
```

### 1.3 Verify System State

```bash
# Check all d3kOS services are running
systemctl --user list-units 'd3kos-*' --all
sudo systemctl list-units 'd3kos-*' --all

# Verify tier status
curl -s http://localhost:8093/tier/status | jq

# Verify installation ID
curl -s http://localhost:8091/license/info | jq

# Check disk usage (should be ~85-90% on 16GB SD card)
df -h /

# List all network interfaces (verify vcan0 NOT present)
ip link show
```

### 1.4 Set Tier to 3 for Image (Testing Mode)

```bash
# Verify tier is already 3 (testing build)
curl -s http://localhost:8093/tier/status | jq '.tier'

# If not 3, set it:
# sudo nano /opt/d3kos/config/license.json
# Change "tier": 2 to "tier": 3
# sudo systemctl restart d3kos-tier-manager
```

### 1.5 Verify Voice Assistant Configuration

```bash
# Check voice service is enabled but not auto-starting
systemctl --user is-enabled d3kos-voice
# Should be: enabled

# Verify wake words file
cat /opt/d3kos/config/sphinx/wake-words.kws
# Should show: helm, advisor, counsel

# Check microphone device
arecord -l | grep -i "anker\|S330"
# Should show: card 2, device 0 (plughw:2,0)
```

### 1.6 Create Image Metadata File

```bash
cat > /boot/firmware/d3kos-image-info.txt <<'EOF'
d3kOS System Image - v0.9.1.2
Created: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Source: Raspberry Pi 4B (8GB RAM)
SD Card: 16GB (SanDisk/Samsung)
OS: Debian GNU/Linux 13 (Trixie)

Included Services:
- License API (port 8091)
- Tier API (port 8093)
- Export Manager (port 8094)
- System Management API (port 8095)
- Timezone API (port 8098)
- Self-Healing API (port 8099)
- Backup API (port 8100)
- Network API (port 8101)
- AI Assistant API (port 8080)
- Camera Stream (port 8084)
- Fish Detection (port 8086)
- Marine Vision API (port 8089)
- Notifications API (port 8088)

Default Credentials:
- User: d3kos
- Password: d3kos2026
- SSH: Enabled (change password after first boot)
- WiFi: Client-only (hotspot NOT supported)

Features:
- Tier 3 (Testing Build) - All features enabled
- Voice Assistant: Configured but disabled by default
- Timezone: Auto-detection on first boot
- Camera: Reolink RLC-810A support
- Self-Healing: Enabled
- Export: Tier 1+ functionality
- Backup: Automated 36MB compressed backups

Installation ID: Generated on first boot
Reset Counter: 0 (unlimited resets in Tier 3)

IMPORTANT: Change default password after first login!
EOF
```

### 1.7 Final Shutdown

```bash
# Sync all filesystems
sync

# Shutdown cleanly
sudo shutdown -h now
```

**Wait for Pi to fully power off before proceeding to Phase 2**

---

## Phase 2: Create Image (FROM UBUNTU/WSL)

### 2.1 Remove SD Card from Pi

**CRITICAL**: Ensure Pi is completely powered off, then remove the 16GB microSD card

### 2.2 Insert SD Card into Card Reader

Connect card reader to your Ubuntu machine or Windows PC (for WSL access)

### 2.3 Identify SD Card Device

```bash
# List all block devices
lsblk

# Find your SD card (typically /dev/sdb or /dev/mmcblk0)
# Look for ~16GB device with two partitions (boot + root)
# Example output:
# sdb           8:16   1  14.9G  0 disk
# ├─sdb1        8:17   1   512M  0 part   (boot partition)
# └─sdb2        8:18   1  14.4G  0 part   (root partition)

# DOUBLE CHECK - this is critical!
sudo fdisk -l /dev/sdb  # Replace 'sdb' with your device
```

**⚠️ WARNING**: Using the wrong device will destroy data. Verify carefully!

### 2.4 Create Raw Image

```bash
# Navigate to working directory
cd ~/d3kOS-images
mkdir -p v0.9.1.2
cd v0.9.1.2

# Create image (replace /dev/sdb with your SD card device)
# This takes ~15-20 minutes for 16GB
sudo dd if=/dev/sdb of=d3kos-v0.9.1.2-raw.img bs=4M status=progress conv=fsync

# Sync to ensure all data written
sync
```

### 2.5 Shrink Image (Remove Empty Space)

The raw image is 16GB, but the filesystem only uses ~13GB. Let's shrink it:

```bash
# Install required tools
sudo apt-get install -y parted e2fsck resize2fs

# Check current image size
ls -lh d3kos-v0.9.1.2-raw.img
# Should show: ~15G

# Mount the image
sudo losetup -fP d3kos-v0.9.1.2-raw.img
LOOP_DEVICE=$(losetup -j d3kos-v0.9.1.2-raw.img | cut -d: -f1)
echo "Loop device: $LOOP_DEVICE"

# Check filesystem
sudo e2fsck -f ${LOOP_DEVICE}p2

# Shrink filesystem to minimum size
sudo resize2fs -M ${LOOP_DEVICE}p2

# Get new filesystem size
NEW_SIZE=$(sudo tune2fs -l ${LOOP_DEVICE}p2 | grep 'Block count' | awk '{print $3}')
BLOCK_SIZE=$(sudo tune2fs -l ${LOOP_DEVICE}p2 | grep 'Block size' | awk '{print $3}')
FS_SIZE_MB=$(( ($NEW_SIZE * $BLOCK_SIZE) / 1024 / 1024 ))
echo "Filesystem size: ${FS_SIZE_MB} MB"

# Detach loop device
sudo losetup -d $LOOP_DEVICE

# Truncate image to new size (filesystem size + 512MB boot + 100MB buffer)
NEW_IMG_SIZE=$(( $FS_SIZE_MB + 612 ))
echo "Truncating image to ${NEW_IMG_SIZE} MB"
truncate -s ${NEW_IMG_SIZE}M d3kos-v0.9.1.2-raw.img

# Result: Image should now be ~14.5GB instead of 16GB
ls -lh d3kos-v0.9.1.2-raw.img
```

### 2.6 Compress Image

```bash
# Compress using gzip (maximum compression)
# This takes ~5-10 minutes
gzip -9 -c d3kos-v0.9.1.2-raw.img > d3kos-v0.9.1.2.img.gz

# Check compressed size
ls -lh d3kos-v0.9.1.2.img.gz
# Expected: ~3.2 GB (78% compression from 14.5GB)
```

### 2.7 Generate Checksums

```bash
# SHA-256 checksum
sha256sum d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2.img.gz.sha256

# Display checksum
cat d3kos-v0.9.1.2.img.gz.sha256

# MD5 (optional, for compatibility)
md5sum d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2.img.gz.md5
```

### 2.8 Create Release Notes

```bash
cat > d3kos-v0.9.1.2-RELEASE_NOTES.txt <<'EOF'
d3kOS v0.9.1.2 - Official Release
Released: February 21, 2026

SYSTEM IMAGE INFORMATION
========================
Compressed Size: 3.2 GB
Uncompressed Size: 14.5 GB
Required SD Card: 16GB minimum, 32GB+ recommended
OS: Debian GNU/Linux 13 (Trixie)
Kernel: 6.6.x (Raspberry Pi)

WHAT'S INCLUDED
===============
✅ Session A: Timezone Auto-Detection (GPS→Internet→UTC)
✅ Session A: Voice Assistant Enabled (Vosk wake words)
✅ Session B: Self-Healing System (auto-remediation)
✅ Session C: Data Export & Backup (queue + retry)
✅ Session E: Chromium Session Reset (no restore prompt)
✅ Session F: Network Settings UI (WiFi client mode)
✅ Marine Vision Phase 1 & 2.1 (camera + fish detection)
✅ AI Assistant (OpenRouter online + rule-based offline)
✅ Installation ID System (file-based, persistent)
✅ Tier System (Tier 3 testing mode by default)
✅ All 13 d3kOS microservices

DEFAULT CONFIGURATION
=====================
Tier: 3 (Testing Build - All Features Enabled)
Installation ID: Generated on first boot
Reset Counter: 0 (unlimited in Tier 3)
Voice Assistant: Configured, disabled by default
WiFi: Client-only (hotspot NOT supported - BCM4345/6 limitation)

Credentials:
- User: d3kos
- Password: d3kos2026
- ⚠️ CHANGE AFTER FIRST LOGIN: Run 'passwd'

Network Access:
- Main Menu: http://d3kos.local or http://[IP-ADDRESS]
- Dashboard: http://d3kos.local:1880/dashboard
- Signal K: http://d3kos.local:3000

FIRST BOOT INSTRUCTIONS
========================
1. Flash image to 16GB+ SD card using Raspberry Pi Imager
2. Insert SD card into Raspberry Pi 4B
3. Connect touchscreen (HDMI + USB touch)
4. Connect peripherals (GPS, AIS, microphone if using voice)
5. Power on (wait ~60 seconds for boot)
6. System loads to Chromium main menu automatically
7. Navigate to Settings → Network Settings
8. Connect to WiFi (home network, phone hotspot, Starlink, etc.)
9. Change default password: Open terminal, run 'passwd'
10. Complete onboarding wizard (13 questions, ~10 minutes)

KNOWN ISSUES
============
❌ WiFi Hotspot: Built-in WiFi cannot act as Access Point (hardware limitation)
   Workaround: Connect to existing WiFi network or use external WiFi adapter

⚠️ Voice Assistant: PipeWire audio interference (17x signal reduction)
   Status: Functional with direct hardware access (plughw:2,0)
   Workaround: Voice service enabled but not auto-starting by default

⚠️ GPS Drift Indoors: Weak satellite signals cause position "wandering"
   Expected: 8+ satellites outdoors provides stable position

⚠️ Simulator: vcan0 simulator may need manual disable if re-enabled
   Fix: Disable vcan0-simulator in Signal K settings if errors appear

UPGRADE PATH
============
Tier 0 → Tier 2: Install OpenCPN (included, free to enable)
Tier 2 → Tier 3: Subscribe via mobile app ($9.99/month or $99.99/year)

OTA Updates: Tier 2/3 only (Tier 0/1 require new image download)

SUPPORT
=======
Documentation: https://github.com/SkipperDon/d3kOS
Issues: https://github.com/SkipperDon/d3kOS/issues
Community: AtMyBoat.com forums

CHECKSUMS
=========
SHA-256: (see d3kos-v0.9.1.2.img.gz.sha256)
MD5: (see d3kos-v0.9.1.2.img.gz.md5)

LICENSE
=======
d3kOS is open source software.
See LICENSE file for full details.

---
Built with ❤️ by the d3kOS Team
EOF
```

---

## Phase 3: Test Image (CRITICAL - DO NOT SKIP)

### 3.1 Prepare Test SD Card

**Use a DIFFERENT SD card** (not your production one) - 16GB minimum

### 3.2 Flash Test Image

```bash
# Decompress
gunzip -c d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2-test.img

# Flash to test SD card (replace /dev/sdc with test card)
sudo dd if=d3kos-v0.9.1.2-test.img of=/dev/sdc bs=4M status=progress conv=fsync
sync

# Remove test SD card
```

### 3.3 Boot Test System

1. Insert test SD card into Raspberry Pi
2. Power on
3. Wait for boot (~60 seconds)
4. Verify:
   - ✅ Chromium main menu loads
   - ✅ All buttons clickable
   - ✅ Settings page accessible
   - ✅ Network settings working
   - ✅ Can connect to WiFi
   - ✅ Services running: `systemctl --user list-units 'd3kos-*'`
   - ✅ Tier status: `curl http://localhost:8093/tier/status`
   - ✅ Installation ID generated: `curl http://localhost:8091/license/info`

### 3.4 Test Checklist

```bash
# SSH into test Pi
ssh d3kos@[TEST-PI-IP]
# Password: d3kos2026

# Run verification tests
echo "=== SYSTEM VERSION ==="
cat /etc/os-release | grep VERSION

echo -e "\n=== D3KOS SERVICES ==="
systemctl --user list-units 'd3kos-*' --no-legend | awk '{print $1, $3}'

echo -e "\n=== TIER STATUS ==="
curl -s http://localhost:8093/tier/status | jq

echo -e "\n=== INSTALLATION ID ==="
curl -s http://localhost:8091/license/info | jq '.installation_id'

echo -e "\n=== TIMEZONE ==="
curl -s http://localhost:8098/api/timezone/status | jq

echo -e "\n=== DISK USAGE ==="
df -h / | tail -1

echo -e "\n=== MEMORY USAGE ==="
free -h

echo -e "\n=== CPU TEMP ==="
vcgencmd measure_temp

echo -e "\n=== NETWORK INTERFACES ==="
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

**Expected Results**:
- All d3kOS services: active (running)
- Tier: 3
- Installation ID: 16-char hex (newly generated)
- Timezone: Detected or UTC
- Disk usage: ~85-90%
- Memory: ~1.5-2GB used (out of 8GB)
- CPU temp: <60°C idle

### 3.5 Test Boot Reliability

```bash
# Reboot 3 times to verify stability
for i in 1 2 3; do
  echo "Reboot test $i of 3..."
  sudo reboot
  # Wait 2 minutes, then SSH back in and check services
  sleep 120
  ssh d3kos@[TEST-PI-IP] "systemctl --user is-active d3kos-tier-manager"
done
```

### 3.6 Test Chromium Session Reset

```bash
# Verify Chromium doesn't show "Restore pages?" after reboot
# Check reset script ran
sudo journalctl -u reset-chromium-session.service
# Should show: "Chromium session reset - clean exit state set"

# Reboot and verify main menu loads without prompt
sudo reboot
```

**If any tests fail, DO NOT PROCEED. Fix issues and recreate image.**

---

## Phase 4: Upload to Google Drive

### 4.1 Install Google Drive CLI (if not already installed)

```bash
# Install gdrive tool
wget https://github.com/prasmussen/gdrive/releases/download/2.1.1/gdrive_2.1.1_linux_amd64.tar.gz
tar -xzf gdrive_2.1.1_linux_amd64.tar.gz
sudo mv gdrive /usr/local/bin/
sudo chmod +x /usr/local/bin/gdrive

# Authenticate (first time only)
gdrive about
# Follow browser authentication flow
```

### 4.2 Upload Image Files

```bash
cd ~/d3kOS-images/v0.9.1.2

# Upload compressed image
gdrive upload --parent [FOLDER_ID] d3kos-v0.9.1.2.img.gz
# Note the file ID from output

# Upload checksum
gdrive upload --parent [FOLDER_ID] d3kos-v0.9.1.2.img.gz.sha256

# Upload MD5 (optional)
gdrive upload --parent [FOLDER_ID] d3kos-v0.9.1.2.img.gz.md5

# Upload release notes
gdrive upload --parent [FOLDER_ID] d3kos-v0.9.1.2-RELEASE_NOTES.txt
```

### 4.3 Create Shareable Links

```bash
# Make files publicly accessible (anyone with link can download)
gdrive share [FILE_ID] --type anyone --role reader

# Get shareable link
gdrive info [FILE_ID] | grep "ViewUrl"

# Copy the link for README update
```

### 4.4 Alternative: Manual Upload via Browser

1. Go to https://drive.google.com
2. Navigate to d3kOS folder
3. Drag and drop: `d3kos-v0.9.1.2.img.gz` (3.2 GB)
4. Upload takes ~15-30 minutes depending on connection
5. Right-click → Share → Anyone with link → Viewer
6. Copy link

---

## Phase 5: Update GitHub

### 5.1 Update README.md (Already Done)

✅ Image size information already updated
✅ WiFi hotspot struck through
✅ Download links ready for replacement

### 5.2 Create GitHub Release

```bash
# Navigate to Helm-OS repo
cd ~/Helm-OS

# Verify current status
git status

# Stage documentation updates
git add README.md
git add MASTER_SYSTEM_SPEC.md
git add doc/IMAGE_CREATION_GUIDE_v0.9.1.2.md

# Commit
git commit -m "Release v0.9.1.2: Image ready, documentation updated

- Updated README with v0.9.1.2 image specifications
- Compressed size: ~3.2 GB, Uncompressed: ~14.5 GB
- Struck through WiFi hotspot references (hardware limitation)
- Added comprehensive image creation guide
- Updated MASTER_SYSTEM_SPEC.md credentials table

Image includes:
- Timezone auto-detection (Session A)
- Voice assistant configured (Session A)
- Self-healing system (Session B)
- Data export & backup (Session C)
- Network settings UI (Session F)
- Marine Vision Phase 1 & 2.1
- All 13 d3kOS microservices
- Tier 3 testing mode by default"

# Push to GitHub
git push origin main
```

### 5.3 Create Release on GitHub

**Via GitHub Web Interface:**

1. Go to: https://github.com/SkipperDon/d3kOS/releases
2. Click **"Draft a new release"**
3. **Tag version**: `v0.9.1.2`
4. **Release title**: `d3kOS v0.9.1.2 - Testing Build`
5. **Description**: Paste release notes from `d3kos-v0.9.1.2-RELEASE_NOTES.txt`
6. **Attach files** (Upload from `~/d3kOS-images/v0.9.1.2/`):
   - `d3kos-v0.9.1.2.img.gz` (3.2 GB)
   - `d3kos-v0.9.1.2.img.gz.sha256`
   - `d3kos-v0.9.1.2.img.gz.md5`
   - `d3kos-v0.9.1.2-RELEASE_NOTES.txt`
7. Check **"This is a pre-release"** (since it's v0.9.x)
8. Click **"Publish release"**

**Via GitHub CLI (gh):**

```bash
# Install gh if not present
# sudo apt install gh

# Authenticate
gh auth login

# Create release
cd ~/Helm-OS
gh release create v0.9.1.2 \
  --title "d3kOS v0.9.1.2 - Testing Build" \
  --notes-file ~/d3kOS-images/v0.9.1.2/d3kos-v0.9.1.2-RELEASE_NOTES.txt \
  --prerelease \
  ~/d3kOS-images/v0.9.1.2/d3kos-v0.9.1.2.img.gz \
  ~/d3kOS-images/v0.9.1.2/d3kos-v0.9.1.2.img.gz.sha256 \
  ~/d3kOS-images/v0.9.1.2/d3kos-v0.9.1.2.img.gz.md5 \
  ~/d3kOS-images/v0.9.1.2/d3kos-v0.9.1.2-RELEASE_NOTES.txt
```

### 5.4 Update README Download Links

Replace `PLACEHOLDER` in README.md with actual Google Drive link:

```bash
# Get Google Drive direct download link
# Format: https://drive.google.com/uc?id=[FILE_ID]&export=download

# Edit README
nano ~/Helm-OS/README.md

# Find line:
# - Direct Link: [d3kos-v0.9.1.2.img.gz](https://drive.google.com/PLACEHOLDER)

# Replace with actual link, commit, push
git add README.md
git commit -m "Updated Google Drive download link for v0.9.1.2"
git push origin main
```

---

## Phase 6: Verification

### 6.1 Test GitHub Release Download

```bash
# Download from GitHub release
wget https://github.com/SkipperDon/d3kOS/releases/download/v0.9.1.2/d3kos-v0.9.1.2.img.gz

# Verify checksum
wget https://github.com/SkipperDon/d3kOS/releases/download/v0.9.1.2/d3kos-v0.9.1.2.img.gz.sha256
sha256sum -c d3kos-v0.9.1.2.img.gz.sha256
# Should output: d3kos-v0.9.1.2.img.gz: OK
```

### 6.2 Test Google Drive Download

```bash
# Download from Google Drive
wget --no-check-certificate 'https://drive.google.com/uc?id=[FILE_ID]&export=download' -O d3kos-v0.9.1.2-gdrive.img.gz

# Verify checksum matches GitHub version
sha256sum d3kos-v0.9.1.2-gdrive.img.gz d3kos-v0.9.1.2.img.gz
# Both should show same checksum
```

### 6.3 Verify README Instructions

1. Open https://github.com/SkipperDon/d3kOS
2. Verify README shows:
   - ✅ Image size: ~3.2 GB compressed
   - ✅ Version: v0.9.1.2
   - ✅ WiFi hotspot struck through
   - ✅ Download links working
3. Follow "Quick Start" instructions with test SD card
4. Verify all steps work as documented

---

## Cleanup

```bash
# Keep compressed image and checksums
# Delete raw/uncompressed images to save space
cd ~/d3kOS-images/v0.9.1.2
rm d3kos-v0.9.1.2-raw.img
rm d3kos-v0.9.1.2-test.img

# Final file list
ls -lh
# Should show:
# d3kos-v0.9.1.2.img.gz (3.2 GB)
# d3kos-v0.9.1.2.img.gz.sha256
# d3kos-v0.9.1.2.img.gz.md5
# d3kos-v0.9.1.2-RELEASE_NOTES.txt
```

---

## Troubleshooting

### Image Too Large

If compressed image > 4GB:
- Remove /home/d3kos/.cache/* before imaging
- Run `sudo apt-get clean` before imaging
- Check for large log files: `sudo du -sh /var/log/*`

### Image Won't Boot

- Verify SD card is good quality (Class 10 A2)
- Try different card reader
- Re-flash with Raspberry Pi Imager instead of dd
- Check Pi hardware (power supply, HDMI cable)

### Services Not Starting

- Check systemd logs: `sudo journalctl -xe`
- Verify all services enabled: `systemctl --user list-unit-files 'd3kos-*'`
- Check for missing dependencies: `sudo apt-get install -f`

### Checksum Mismatch

- Re-download image
- Verify no corruption during compression
- Check disk for errors: `sudo fsck /dev/sdb2`

---

## Summary Checklist

- [ ] Phase 1: Pi prepared and cleanly shutdown
- [ ] Phase 2: Image created and compressed (~3.2 GB)
- [ ] Phase 2: Checksums generated (SHA-256 + MD5)
- [ ] Phase 3: Image tested on different SD card
- [ ] Phase 3: All services verified working
- [ ] Phase 3: Boot reliability confirmed (3 reboots)
- [ ] Phase 4: Uploaded to Google Drive
- [ ] Phase 4: Shareable links created
- [ ] Phase 5: GitHub release created
- [ ] Phase 5: Files attached to release
- [ ] Phase 5: README updated with Google Drive link
- [ ] Phase 6: Downloads verified from both sources
- [ ] Phase 6: Checksums confirmed matching
- [ ] Cleanup: Raw images deleted

---

**IMPORTANT**: Do not distribute image until ALL tests pass!

**Time Estimate**:
- Phase 1 (Prep): 30 minutes
- Phase 2 (Image): 45 minutes
- Phase 3 (Test): 60 minutes
- Phase 4 (Upload): 30 minutes
- Phase 5 (GitHub): 20 minutes
- Phase 6 (Verify): 15 minutes
**Total: ~3.5 hours**

---

**Questions or Issues?**
Contact: SkipperDon via GitHub Issues

**Document Version**: 1.0
**Last Updated**: February 21, 2026
