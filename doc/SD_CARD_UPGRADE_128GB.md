# SD Card Upgrade: 16GB → 128GB

**Date:** February 25, 2026
**System:** d3kOS v2.0-T3 (0.9.1.2)
**Current:** 16GB SD @ 97% full (456MB free)
**Target:** 128GB SD (119GB usable)
**Purpose:** Enable worldwide fish species identification system

---

## Storage Allocation After Upgrade

**128GB SD Card Breakdown:**

| Component | Size | Purpose |
|-----------|------|---------|
| Base d3kOS System | 12GB | OS, services, dependencies |
| AI Models | 5GB | 1000+ fish species models |
| Training Datasets (cached) | 10GB | Species images for fine-tuning |
| Regulations Database | 1GB | Worldwide fishing regulations |
| Camera Recordings | 80GB | Marine Vision video storage |
| System Logs | 2GB | Service logs, debugging |
| User Data | 5GB | Captures, boatlog, configurations |
| **Free Space** | **13GB** | Buffer for updates, temp files |
| **Total** | **128GB** | (119GB usable after formatting) |

---

## Before You Start - What You Need

**Hardware:**
- ✅ 128GB microSD card (Class 10 or UHS-I recommended)
- ✅ SD card reader (USB or built-in on laptop)
- ✅ Raspberry Pi 4B (currently running d3kOS)

**Software:**
- ✅ Laptop/PC with Ubuntu (your WSL/development machine)
- ✅ SSH access to Pi (already configured: `~/.ssh/d3kos_key`)

**Time Required:**
- Backup: 30 minutes
- Clone: 45-60 minutes (depends on SD card reader speed)
- Expand filesystem: 5 minutes
- Verification: 15 minutes
- **Total: 2 hours**

---

## Method 1: Clone Entire SD Card (RECOMMENDED)

This preserves EVERYTHING - bootloader, partitions, data, configurations.

### Step 1: Shutdown Pi and Remove SD Card

```bash
# From your laptop, shutdown Pi safely
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo shutdown -h now'

# Wait 30 seconds for clean shutdown
# Power off Pi
# Remove 16GB SD card from Pi
# Insert 16GB card into laptop SD reader
```

### Step 2: Identify SD Card Device

```bash
# On your Ubuntu machine, find SD card device
lsblk

# Look for 16GB device (e.g., /dev/sdb or /dev/mmcblk0)
# Output example:
# NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
# sdb           8:16   1  14.9G  0 disk
# ├─sdb1        8:17   1   256M  0 part
# └─sdb2        8:18   1  14.6G  0 part

# ⚠️ CRITICAL: Make sure you have the RIGHT device!
# Wrong device = overwrite your laptop hard drive!
```

### Step 3: Clone 16GB to Image File

```bash
# Create backup directory
mkdir -p ~/d3kos-backup
cd ~/d3kos-backup

# Clone SD card to image file (takes 30-45 minutes)
# Replace /dev/sdb with YOUR SD card device
sudo dd if=/dev/sdb of=d3kos-16gb-backup.img bs=4M status=progress

# Expected output:
# 15GB transferred
# File size: ~16GB
# Time: 30-45 minutes
```

### Step 4: Insert 128GB Card and Write Image

```bash
# Remove 16GB card from reader
# Insert 128GB card into reader

# Verify new card detected
lsblk
# Should show ~128GB device (e.g., /dev/sdb)

# Write image to 128GB card
# ⚠️ This ERASES everything on 128GB card!
sudo dd if=d3kos-16gb-backup.img of=/dev/sdb bs=4M status=progress

# Expected output:
# 15GB written (only writes used space from 16GB image)
# Time: 30-45 minutes
```

### Step 5: Expand Filesystem to Use Full 128GB

```bash
# After dd completes, expand partition
sudo fdisk /dev/sdb

# Commands to type in fdisk:
p          # Print partition table (note partition 2 end sector)
d          # Delete partition
2          # Partition 2 (the root filesystem)
n          # New partition
p          # Primary
2          # Partition number 2
<ENTER>    # Start at default (same as before)
<ENTER>    # End at default (end of disk = 128GB)
N          # Don't remove ext4 signature
w          # Write changes

# Verify partition expanded
lsblk
# sdb2 should now show ~127GB
```

### Step 6: Resize Filesystem

```bash
# Check and resize ext4 filesystem
sudo e2fsck -f /dev/sdb2
sudo resize2fs /dev/sdb2

# Expected output:
# Resizing to 123GB
# Done
```

### Step 7: Insert Card in Pi and Boot

```bash
# Eject SD card safely
sync
sudo eject /dev/sdb

# Remove 128GB card from laptop
# Insert 128GB card into Raspberry Pi
# Power on Pi
# Wait 60 seconds for boot
```

### Step 8: Verify Upgrade Successful

```bash
# SSH into Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Check disk space
df -h /

# Expected output:
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/mmcblk0p2  119G   12G  102G  11% /

# Should show ~119GB total, ~102GB available ✅
```

---

## Method 2: Fresh Install + Data Migration (NOT RECOMMENDED)

This requires:
1. Flash fresh Debian Trixie to 128GB card
2. Reinstall all d3kOS services (22+ services)
3. Copy user data from backup
4. Reconfigure everything

**Time:** 6-8 hours
**Risk:** High (might miss configurations)
**Recommendation:** Use Method 1 instead

---

## Post-Upgrade Verification Checklist

After booting from 128GB card, verify all systems working:

```bash
# 1. Check disk space
df -h /
# Should show ~119GB total

# 2. Check all services running
systemctl list-units --state=running | grep d3kos
# Should show 22+ services active

# 3. Check voice assistant
systemctl status d3kos-voice.service
# Should be active (running)

# 4. Check camera streaming
curl http://localhost:8084/camera/status
# Should return connected: true

# 5. Check tier status
curl http://localhost/tier/status | jq .
# Should show tier: 2

# 6. Check license
curl http://localhost/license/info | jq .
# Should show installation_id

# 7. Check marine vision
curl http://localhost:8086/detect/status
# Should return service status

# 8. Test voice watchdog
sudo systemctl status d3kos-voice-watchdog.timer
# Should be active (running)

# 9. Check web interface
# Open http://192.168.1.237 in browser
# Navigate through pages (should all load)

# 10. Test camera feed
# Open http://192.168.1.237/marine-vision.html
# Should show live camera feed
```

---

## If Something Goes Wrong

### Problem: Pi Won't Boot from 128GB Card

**Solution:**
1. Power off Pi
2. Re-insert 16GB card (original still works)
3. Power on Pi
4. Review clone process - may need to retry

### Problem: Filesystem Shows 16GB Not 128GB

**Solution:**
```bash
# SSH into Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Expand filesystem from Pi
sudo raspi-config
# Navigate to: Advanced Options → Expand Filesystem
# Reboot

# Or manually:
sudo fdisk /dev/mmcblk0
# (Follow Step 5 commands above)
sudo reboot

# After reboot:
sudo resize2fs /dev/mmcblk0p2
```

### Problem: Services Not Starting

**Check logs:**
```bash
journalctl -xe | tail -100
sudo systemctl status d3kos-*.service
```

**Most common cause:** Permissions changed during clone
**Fix:**
```bash
sudo chown -R d3kos:d3kos /opt/d3kos
sudo chown -R d3kos:d3kos /home/d3kos
sudo systemctl restart d3kos-*.service
```

---

## After Successful Upgrade - Next Steps

**Storage Available:** ~102GB free
**Ready for:**
1. ✅ Download 1000+ species fish detection dataset
2. ✅ Train EfficientNet-B1 classification model
3. ✅ Install worldwide fishing regulations database
4. ✅ Enable high-resolution camera recordings
5. ✅ Future system expansion

**Proceed to:** `FISH_SPECIES_WORLDWIDE_IMPLEMENTATION.md`

---

## Backup Strategy Going Forward

With 128GB card:

**Weekly Automated Backups:**
- User data → USB drive or network storage
- Configuration files → git repository
- Database exports → cloud sync

**Monthly Full Image:**
- Clone 128GB → compressed image (~30GB compressed)
- Store on laptop or external drive
- Keep last 2 months

**Before Major Updates:**
- Create snapshot with `dd`
- Test update on clone first
- Keep rollback option ready

---

## Summary

**Before Upgrade:**
- 16GB SD card
- 97% full (456MB free)
- No room for fish species models
- Limited camera recording storage

**After Upgrade:**
- 128GB SD card
- 11% full (102GB free)
- Room for 1000+ fish species
- 80GB camera recording storage
- System expansion headroom

**Time Investment:** 2 hours
**Risk Level:** Low (if you follow instructions carefully)
**Benefit:** Worldwide fish identification system possible

---

**Ready to proceed?** Follow Method 1 steps above, then notify me when Pi boots from 128GB card and verification passes.
