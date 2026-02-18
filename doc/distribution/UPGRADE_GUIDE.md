# d3kOS Upgrade Guide

**Version**: 1.0.3
**Last Updated**: February 18, 2026

---

## 📋 Table of Contents

1. [Upgrade Methods](#upgrade-methods)
2. [Before You Upgrade](#before-you-upgrade)
3. [Method 1: SD Card Swap (Recommended)](#method-1-sd-card-swap-recommended)
4. [Method 2: In-Place Upgrade (Tier 2/3 Only)](#method-2-in-place-upgrade-tier-23-only)
5. [Backup & Restore](#backup--restore)
6. [Version Migration Notes](#version-migration-notes)
7. [Rollback Procedure](#rollback-procedure)
8. [Troubleshooting Upgrades](#troubleshooting-upgrades)

---

## 1. Upgrade Methods

d3kOS supports **two upgrade methods** depending on your tier:

### Method 1: SD Card Swap (All Tiers)

**Supported**: Tier 0, 1, 2, 3
**Procedure**: Flash new image to new SD card, swap cards, restore configuration
**Downtime**: 15-30 minutes
**Risk**: Low (old SD card kept as backup)

**Pros**:
- ✅ Safe - old SD card is complete backup
- ✅ Fast rollback (swap back to old SD card)
- ✅ Works for all tiers (Tier 0/1 have NO other upgrade option)

**Cons**:
- ❌ Requires spare SD card
- ❌ Manual configuration restore (Tier 0 only)
- ❌ Requires computer with SD card reader

---

### Method 2: In-Place Upgrade (Tier 2/3 Only)

**Supported**: Tier 2, 3 (NOT Tier 0/1)
**Procedure**: Download update package, run upgrade script, reboot
**Downtime**: 5-10 minutes
**Risk**: Medium (backup required before upgrade)

**Pros**:
- ✅ No spare SD card required
- ✅ Faster (download + reboot only)
- ✅ Configuration auto-preserved
- ✅ Can be triggered via mobile app

**Cons**:
- ❌ Requires Tier 2 or Tier 3 license
- ❌ Requires internet connection
- ❌ Rollback more complex (restore from backup)

**⚠️ Tier 0/1 Limitation**: In-place upgrades are **disabled** for Tier 0/1 to prevent breaking systems without support options. Tier 0/1 users must use SD card swap method.

---

## 2. Before You Upgrade

### Step 2.1: Check Current Version

**Via Web Interface**:
1. Navigate to Settings → System → About
2. Note current version (e.g., 1.0.2)

**Via SSH**:
```bash
cat /opt/d3kos/version.txt
# Output: 1.0.2
```

### Step 2.2: Check Release Notes

**CRITICAL**: Always read release notes before upgrading.

1. Visit GitHub Releases: https://github.com/SkipperDon/d3kos/releases
2. Find target version (e.g., v1.0.3)
3. Read RELEASE_NOTES and CHANGELOG
4. Check for:
   - **Breaking changes** - May require configuration changes
   - **Known issues** - May affect your use case
   - **Migration notes** - Special upgrade procedures

### Step 2.3: Verify Tier Requirements

**Check Your Tier**:
```bash
# Via web interface
Settings → System → License Information

# Via SSH
cat /opt/d3kos/config/license.json | grep tier
```

**Tier Upgrade Matrix**:

| From Version | To Version | Tier 0/1 | Tier 2/3 |
|--------------|------------|----------|----------|
| 1.0.0 → 1.0.1 | Minor | SD Card Swap | SD Card Swap or In-Place |
| 1.0.2 → 1.0.3 | Minor | SD Card Swap | SD Card Swap or In-Place |
| 1.x → 2.x | Major | SD Card Swap | SD Card Swap (recommended) |

### Step 2.4: Backup Data

**⚠️ CRITICAL**: Always backup before upgrading!

**What to Backup**:
- ✅ `/opt/d3kos/config/` - Configuration files
- ✅ `/opt/d3kos/data/boat-log.txt` - Boat log entries
- ✅ `/opt/d3kos/config/onboarding.json` - Initial Setup answers
- ✅ `/opt/d3kos/config/license.json` - Installation ID and tier
- ✅ `/home/d3kos/camera-recordings/` - Camera photos/videos (optional)

**Backup Script**:
```bash
# Run backup script
/opt/d3kos/scripts/backup.sh

# Output: /opt/d3kos/backups/d3kos-backup-YYYYMMDD-HHMMSS.tar.gz
```

**Manual Backup** (via SSH):
```bash
# Create backup directory
mkdir -p /tmp/d3kos-backup

# Copy configuration
cp -r /opt/d3kos/config /tmp/d3kos-backup/
cp -r /opt/d3kos/data /tmp/d3kos-backup/

# Create archive
tar -czf /tmp/d3kos-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /tmp/d3kos-backup .

# Copy to USB drive or download via scp
scp d3kos@d3kos.local:/tmp/d3kos-backup-*.tar.gz ~/Downloads/
```

**Tier 1+ Auto-Backup** (via Mobile App):
- Mobile app can backup configuration automatically
- Stored in cloud (encrypted with installation_id)
- Restored automatically after image update

---

## 3. Method 1: SD Card Swap (Recommended)

**Tier**: All (0, 1, 2, 3)
**Duration**: 30-45 minutes
**Requirements**: Spare SD card (32GB minimum, 128GB recommended), computer with SD card reader

### Step 3.1: Download New Image

```bash
# Download image
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz

# Download checksum
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz.sha256

# Verify checksum
sha256sum -c d3kos-v1.0.3.img.gz.sha256
# Expected: d3kos-v1.0.3.img.gz: OK
```

### Step 3.2: Flash New SD Card

**Using Raspberry Pi Imager**:
1. Insert spare SD card into computer
2. Open Raspberry Pi Imager
3. Choose OS → Use custom → Select d3kos-v1.0.3.img.gz
4. Choose Storage → Select spare SD card
5. Click "Write" → Wait for completion (10-20 minutes)
6. Eject SD card

**See INSTALLATION_GUIDE.md Section 4 for detailed flashing instructions**

### Step 3.3: Backup Old SD Card (Optional but Recommended)

**Before removing old SD card**, create image backup:

```bash
# Insert old SD card into computer (via USB reader)
# Find device name
lsblk
# Example output: /dev/sdb (32GB SD card)

# Create image backup (WARNING: This creates a 32GB file!)
sudo dd if=/dev/sdb of=~/d3kos-v1.0.2-backup.img bs=4M status=progress

# Compress backup (optional, saves space)
gzip ~/d3kos-v1.0.2-backup.img

# Result: ~/d3kos-v1.0.2-backup.img.gz (~4GB compressed)
```

**Note**: This backup allows you to restore the EXACT state of your old system if upgrade fails.

### Step 3.4: Swap SD Cards

1. **Power off** Raspberry Pi:
   ```bash
   sudo poweroff
   ```
2. Wait 30 seconds for complete shutdown
3. Remove old SD card from Raspberry Pi
4. Insert new SD card (with v1.0.3 image)
5. **Store old SD card safely** (this is your rollback backup!)

### Step 3.5: First Boot (New Image)

1. Power on Raspberry Pi
2. Wait 60-90 seconds for first boot (filesystem expansion)
3. Connect to WiFi AP: SSID `d3kOS`, Password `d3kos-2026`
4. Navigate to http://d3kos.local

**Expected Behavior**:
- ✅ Initial Setup wizard appears (new installation)
- ⚠️ Configuration NOT automatically restored (Tier 0 only)
- ✅ Tier 1+ users: Mobile app can restore configuration

### Step 3.6: Restore Configuration

#### Option A: Tier 0 - Manual Restore

**Complete Initial Setup wizard again** (20 steps):
- Use same boat/engine information as before
- DIP switches will be recalculated (should match old values)
- New QR code generated (different installation ID)

**⚠️ WARNING**: New installation ID means you'll need to re-pair mobile app (Tier 1+).

---

#### Option B: Tier 1 - Mobile App Restore

1. Open d3kOS mobile app
2. Tap "Restore Configuration" on welcome screen
3. Select your boat (via cloud backup)
4. App downloads configuration from cloud
5. App uploads configuration to new Pi
6. **Result**: All wizard answers restored, same installation ID

**Files Restored**:
- `/opt/d3kos/config/onboarding.json` - Initial Setup answers
- `/opt/d3kos/config/license.json` - Installation ID (preserved!)
- `/opt/d3kos/data/boat-log.txt` - Boat log entries

---

#### Option C: Manual Restore (All Tiers, Advanced)

**If you have backup tarball** (from Step 2.4):

```bash
# Copy backup to Pi
scp ~/d3kos-backup-20260215-120000.tar.gz d3kos@d3kos.local:/tmp/

# SSH into Pi
ssh d3kos@d3kos.local

# Extract backup
cd /tmp
tar -xzf d3kos-backup-20260215-120000.tar.gz

# Restore configuration
sudo cp -r config/* /opt/d3kos/config/
sudo cp -r data/* /opt/d3kos/data/

# Restart services
sudo systemctl restart d3kos-*

# Reboot (recommended)
sudo reboot
```

**After Reboot**:
- Navigate to http://d3kos.local
- Configuration should be restored (no wizard)
- Dashboard shows previous boat/engine data

---

### Step 3.7: Verify Upgrade

**Web Interface Checks**:
- ✅ Navigate to Settings → System → About
- ✅ Verify version shows "1.0.3"
- ✅ Dashboard displays engine data (if CX5106 connected)
- ✅ Navigation page shows GPS position
- ✅ Boat log contains previous entries (if restored)

**SSH Checks**:
```bash
# Verify version
cat /opt/d3kos/version.txt
# Expected: 1.0.3

# Verify services running
sudo systemctl status d3kos-*

# Check logs for errors
journalctl -b -p err
```

**If Upgrade Failed**: See Step 7 (Rollback Procedure)

---

## 4. Method 2: In-Place Upgrade (Tier 2/3 Only)

**⚠️ IMPORTANT**: This method is **ONLY available for Tier 2 and Tier 3** users.

**Tier 0/1 users**: Must use Method 1 (SD Card Swap) - in-place upgrades are disabled.

### Step 4.1: Check Tier Eligibility

```bash
# Via web interface
Settings → System → License Information
# Must show: Tier 2 or Tier 3

# Via SSH
cat /opt/d3kos/config/license.json | grep '"tier"'
# Expected: "tier": 2 or "tier": 3
```

**If Tier 0 or 1**: Use Method 1 (SD Card Swap) instead.

### Step 4.2: Trigger Upgrade (Mobile App)

**Via d3kOS Mobile App** (Recommended):
1. Open mobile app
2. Navigate to Settings → System → Software Update
3. Tap "Check for Updates"
4. App displays: "Update available: v1.0.3"
5. Read release notes
6. Tap "Download and Install"
7. App downloads update package (~500MB)
8. App uploads to Pi via WiFi
9. App triggers upgrade script
10. Pi reboots automatically
11. After 5 minutes, app reconnects and shows "Update complete: v1.0.3"

**Duration**: 10-15 minutes (download + install + reboot)

---

### Step 4.3: Trigger Upgrade (Web Interface)

**Via Web Browser** (Alternative):
1. Navigate to Settings → System → Software Update
2. Click "Check for Updates"
3. Web page displays: "Update available: v1.0.3"
4. Read release notes
5. Click "Download and Install"
6. Browser shows progress bar (download ~500MB)
7. After download complete: "Installing update..."
8. Pi reboots automatically
9. After 5 minutes, navigate to http://d3kos.local
10. Verify version: Settings → System → About → "1.0.3"

---

### Step 4.4: Trigger Upgrade (SSH, Advanced)

**Via SSH** (Advanced users):

```bash
# SSH into Pi
ssh d3kos@d3kos.local

# Check current version
cat /opt/d3kos/version.txt
# Output: 1.0.2

# Download upgrade package
cd /tmp
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-upgrade-v1.0.3.tar.gz

# Verify checksum
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-upgrade-v1.0.3.tar.gz.sha256
sha256sum -c d3kos-upgrade-v1.0.3.tar.gz.sha256
# Expected: d3kos-upgrade-v1.0.3.tar.gz: OK

# Run upgrade script
sudo /opt/d3kos/scripts/upgrade.sh /tmp/d3kos-upgrade-v1.0.3.tar.gz

# Script output:
# Extracting upgrade package...
# Backing up current configuration...
# Installing new files...
# Updating services...
# Upgrade complete. System will reboot in 10 seconds.

# System reboots automatically
```

**After Reboot** (2-3 minutes):
```bash
# Reconnect via SSH
ssh d3kos@d3kos.local

# Verify version
cat /opt/d3kos/version.txt
# Expected: 1.0.3

# Check services
sudo systemctl status d3kos-*
```

---

### Step 4.5: Upgrade Script Details

**What the upgrade script does**:
1. ✅ Verifies checksum of upgrade package
2. ✅ Creates backup: `/opt/d3kos/backups/pre-upgrade-v1.0.2-YYYYMMDD.tar.gz`
3. ✅ Extracts upgrade package to `/tmp/d3kos-upgrade/`
4. ✅ Stops all d3kOS services
5. ✅ Copies new files to `/opt/d3kos/`, `/var/www/html/`, `/etc/systemd/system/`
6. ✅ Preserves configuration: `/opt/d3kos/config/` (NOT overwritten)
7. ✅ Updates systemd services (daemon-reload)
8. ✅ Restarts services
9. ✅ Cleans up temporary files
10. ✅ Reboots system

**Configuration Preserved**:
- ✅ `/opt/d3kos/config/license.json` - Installation ID, tier
- ✅ `/opt/d3kos/config/onboarding.json` - Initial Setup answers
- ✅ `/opt/d3kos/data/boat-log.txt` - Boat log entries
- ✅ `/opt/d3kos/data/historical.db` - Historical data
- ✅ `/home/d3kos/camera-recordings/` - Camera media

---

## 5. Backup & Restore

### Automatic Backup Script

**Location**: `/opt/d3kos/scripts/backup.sh`

**Usage**:
```bash
# Run backup
/opt/d3kos/scripts/backup.sh

# Output: /opt/d3kos/backups/d3kos-backup-20260218-103045.tar.gz
```

**What's Backed Up**:
```
/opt/d3kos/config/
  ├── license.json
  ├── onboarding.json
  ├── ai-config.json
  ├── camera-ip.txt
  └── ...

/opt/d3kos/data/
  ├── boat-log.txt
  ├── historical.db
  ├── exports/
  └── ...

/opt/d3kos/state/
  ├── onboarding-reset-count.json
  └── ...
```

**What's NOT Backed Up** (too large):
- ❌ `/home/d3kos/camera-recordings/` - Camera media files
- ❌ `/opt/d3kos/models/` - AI models (part of image)
- ❌ `/var/log/` - System logs (regenerated)

---

### Manual Restore

**Restore from backup tarball**:
```bash
# Copy backup to Pi
scp ~/d3kos-backup-20260218-103045.tar.gz d3kos@d3kos.local:/tmp/

# SSH into Pi
ssh d3kos@d3kos.local

# Run restore script
sudo /opt/d3kos/scripts/restore.sh /tmp/d3kos-backup-20260218-103045.tar.gz

# Script output:
# Extracting backup...
# Restoring configuration files...
# Restoring data files...
# Restarting services...
# Restore complete.

# Reboot (recommended)
sudo reboot
```

---

## 6. Version Migration Notes

### v1.0.0 → v1.0.1

**Release Date**: February 10, 2026
**Changes**: Bug fixes, touchscreen improvements

**Migration Notes**: No special steps required. Standard upgrade procedure.

---

### v1.0.1 → v1.0.2

**Release Date**: February 14, 2026
**Changes**: Marine Vision Phase 1, camera integration

**Migration Notes**:
- New services added: `d3kos-camera-stream`, `d3kos-fish-detector`
- Camera configuration page added: Settings → Camera
- No breaking changes

---

### v1.0.2 → v1.0.3

**Release Date**: February 18, 2026
**Changes**: Installation ID system, tier system, data export, Telegram notifications

**⚠️ BREAKING CHANGES**:

**1. Installation ID Format Changed**:
- **Old**: `XXXX-XXXX-XXXX` (12-char random, browser localStorage)
- **New**: 16-char hex (file-based, persistent)
- **Impact**: Old installation IDs discarded, new ID generated on upgrade
- **Workaround**: Re-pair mobile app with new QR code

**2. Tier System Enforced**:
- **Old**: All features enabled by default
- **New**: Tier-based feature restrictions
- **Impact**: Voice assistant and camera disabled for Tier 0/1
- **Workaround**: Install OpenCPN (auto-upgrades to Tier 2) or purchase Tier 2 subscription

**3. Voice Assistant Not Working** (Known Issue):
- Wake word detection broken (PipeWire/PocketSphinx issue)
- Workaround: Use text-based AI Assistant instead

**Migration Steps**:
1. Upgrade using Method 1 (SD Card Swap) or Method 2 (In-Place)
2. After upgrade, navigate to Settings → System → License Information
3. Verify tier (should auto-detect OpenCPN if installed)
4. If Tier 0: Install OpenCPN to unlock Tier 2 features (FREE upgrade)
5. Re-pair mobile app (scan new QR code in Settings)

---

### v1.x → v2.x (Future Major Release)

**⚠️ WARNING**: Major version upgrades (1.x → 2.x) may require full re-installation.

**Recommendation**: Always use Method 1 (SD Card Swap) for major version upgrades.

**Migration Notes**: TBD (not yet released)

---

## 7. Rollback Procedure

### Scenario 1: Upgrade Failed (SD Card Swap Method)

**Solution**: Swap back to old SD card (kept from Step 3.3)

1. Power off Raspberry Pi: `sudo poweroff`
2. Remove new SD card
3. Insert old SD card (with working v1.0.2 image)
4. Power on
5. System boots to previous working state
6. **Duration**: 2 minutes (no data loss)

---

### Scenario 2: Upgrade Failed (In-Place Method)

**Solution**: Restore from pre-upgrade backup

**Step 1: Boot into recovery mode** (if system won't boot):
```bash
# Connect HDMI monitor and USB keyboard
# At boot, press 'e' to edit GRUB entry
# Add 'init=/bin/bash' to kernel line
# Press Ctrl+X to boot

# Remount root filesystem as read-write
mount -o remount,rw /

# Restore backup
cd /opt/d3kos/backups
tar -xzf pre-upgrade-v1.0.2-*.tar.gz -C /

# Reboot
reboot -f
```

**Step 2: Normal boot restore** (if system boots but broken):
```bash
# SSH into Pi
ssh d3kos@d3kos.local

# Run restore script
sudo /opt/d3kos/scripts/restore.sh /opt/d3kos/backups/pre-upgrade-v1.0.2-*.tar.gz

# Downgrade version file
echo "1.0.2" | sudo tee /opt/d3kos/version.txt

# Reboot
sudo reboot
```

---

### Scenario 3: Partial Upgrade (Services Not Starting)

**Solution**: Re-run upgrade script or manually restart services

```bash
# Check which services failed
sudo systemctl --failed

# Restart all d3kOS services
sudo systemctl restart d3kos-*

# Check logs
journalctl -u d3kos-ai-api -n 50
journalctl -u d3kos-camera-stream -n 50

# If still broken, restore from backup (see Scenario 2)
```

---

## 8. Troubleshooting Upgrades

### Problem: Checksum Verification Failed

**Symptoms**: `sha256sum -c` shows "FAILED"

**Solution**:
1. Delete downloaded image
2. Re-download from GitHub Releases
3. Verify checksum again
4. If still fails, file a GitHub issue (corrupted release)

---

### Problem: Upgrade Script Says "Tier 0/1 Not Supported"

**Symptoms**:
```
Error: In-place upgrades are not supported for Tier 0/1.
Please use SD card swap method (see UPGRADE_GUIDE.md).
```

**Solution**: Use Method 1 (SD Card Swap) instead of Method 2 (In-Place).

---

### Problem: Configuration Not Restored After Upgrade

**Symptoms**:
- Initial Setup wizard appears after upgrade
- Previous boat/engine data missing

**Cause**: Configuration files not restored correctly

**Solution**:
```bash
# Restore from backup
sudo /opt/d3kos/scripts/restore.sh /path/to/backup.tar.gz

# Or manually copy config
sudo cp -r /tmp/backup/config/* /opt/d3kos/config/

# Restart services
sudo systemctl restart d3kos-*
```

---

### Problem: Services Won't Start After Upgrade

**Symptoms**: `systemctl status d3kos-*` shows failed services

**Solution**:
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Re-enable and restart services
sudo systemctl enable d3kos-*.service
sudo systemctl restart d3kos-*

# Check logs for specific errors
journalctl -u d3kos-ai-api -n 100
```

---

### Problem: New Version Not Showing After Upgrade

**Symptoms**: Settings → About still shows old version

**Solution**:
```bash
# Verify version file
cat /opt/d3kos/version.txt

# If wrong, manually update
echo "1.0.3" | sudo tee /opt/d3kos/version.txt

# Hard refresh browser (Ctrl+Shift+R)
```

---

## 📞 Getting Help with Upgrades

**Before asking for help**:
1. ✅ Read release notes for target version
2. ✅ Check CHANGELOG.md for breaking changes
3. ✅ Review this upgrade guide completely
4. ✅ Collect logs: `journalctl -b > /tmp/upgrade-logs.txt`

**Where to ask**:
- GitHub Discussions: https://github.com/SkipperDon/d3kos/discussions
- GitHub Issues: https://github.com/SkipperDon/d3kos/issues (bugs only)

**Include in bug report**:
- Current version (before upgrade)
- Target version (attempting to upgrade to)
- Upgrade method used (SD card swap or in-place)
- Tier (0, 1, 2, or 3)
- Error messages (full output)
- System logs (`journalctl -b`)

---

**Document Version**: 1.0.3
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
