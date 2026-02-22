# d3kOS System Update Safety Guide

**Date**: February 22, 2026
**d3kOS Version**: 0.9.1.2
**Purpose**: Protect the system from breaking during apt updates

---

## ✅ GOOD NEWS: System is Already Protected!

Your system has **built-in safeguards** that prevent critical packages from being updated:

### Protected Packages (apt-mark hold):
```
✓ can-utils         - NMEA2000 CAN bus tools (CRITICAL)
✓ linux-image-rpi-v8 - Kernel 6.12.62 (CRITICAL)
✓ nodejs            - Node.js v20.20.0 (CRITICAL)
✓ raspi-firmware    - Raspberry Pi firmware (CRITICAL)
```

### APT Pinning (prevents version changes):
```
✓ /etc/apt/preferences.d/nodejs - Locks Node.js to 20.x branch
✓ /etc/apt/preferences.d/nsolid - Additional Node.js protection
```

### npm Packages (not managed by apt):
```
✓ node-red@4.1.4      - Won't be touched by apt updates
✓ signalk-server@2.20.3 - Won't be touched by apt updates
```

### Python pip Packages (not managed by apt):
```
✓ Flask, flask-cors, onnxruntime - Installed via pip3, safe from apt
```

---

## ⚠️ POTENTIAL RISKS (unprotected packages)

### 1. **Python 3.13.5** - NOT held/pinned
**Current**: Python 3.13.5
**Risk**: Could upgrade to 3.13.6, 3.14.x, etc.
**Impact**:
- Minor version (3.13.5 → 3.13.6): **LOW RISK** (usually safe)
- Major version (3.13 → 3.14): **MEDIUM RISK** (could break pip packages)

**Recommendation**: Add Python to hold list (see commands below)

### 2. **Chromium** - NOT held/pinned
**Current**: Chromium 144.0.7559.109
**Risk**: Could upgrade to newer versions
**Impact**: **LOW RISK** - Chromium updates are usually backward compatible
**Note**: Security updates are GOOD, but could change flags/behavior

**Recommendation**: Monitor but don't hold (security updates are important)

### 3. **System Libraries** (libc, drivers, etc.)
**Risk**: General Debian updates could affect drivers
**Impact**: **LOW-MEDIUM RISK**
**Most likely to break**:
- Audio drivers (PocketSphinx, Vosk, Piper)
- CAN drivers (NMEA2000)
- USB drivers (Touchscreen, Microphone, Camera)

---

## 🛡️ RECOMMENDED SAFEGUARDS

### Add Python to Hold List:
```bash
sudo apt-mark hold python3.13 python3.13-minimal python3.13-dev libpython3.13-stdlib
```

### Verify Current Holds:
```bash
apt-mark showhold
```

**Expected output:**
```
can-utils
linux-image-rpi-v8
nodejs
python3.13
python3.13-dev
python3.13-minimal
raspi-firmware
```

### Check What Would Update (BEFORE running apt upgrade):
```bash
sudo apt update
apt list --upgradable
```

This shows what would change **without actually changing it**.

---

## 📋 SAFE UPDATE PROCEDURE

### Step 1: Check Available Updates
```bash
sudo apt update
apt list --upgradable
```

### Step 2: Review the List
**SAFE to update:**
- Security patches for held packages (won't upgrade due to hold)
- Minor version bumps (1.2.3 → 1.2.4)
- Documentation packages (python3-doc, etc.)
- Firmware updates (if comfortable with risk)

**RISKY to update:**
- Major Python version changes (3.13 → 3.14)
- Kernel updates (already held, so safe)
- Audio/driver package changes
- Libraries ending in "-dev" that pip packages depend on

### Step 3: Selective Update (if needed)
```bash
# Update ONLY specific packages:
sudo apt install --only-upgrade <package-name>

# Example: Update only security patches
sudo apt upgrade --with-new-pkgs --no-install-recommends
```

### Step 4: Full Update (use with caution)
```bash
# Full system update (not recommended without review)
sudo apt full-upgrade
```

**⚠️ WARNING**: `apt full-upgrade` can install NEW packages and remove OLD ones.
This is the MOST RISKY option.

---

## 🚨 WHAT TO DO IF UPDATES BREAK SOMETHING

### 1. Check Service Status
```bash
systemctl status d3kos-voice.service
systemctl status d3kos-ai-api.service
systemctl status signalk.service
systemctl status nodered.service
```

### 2. Check Logs for Errors
```bash
journalctl -u d3kos-voice.service -n 100
journalctl -u signalk.service -n 100
```

### 3. Rollback if Possible
```bash
# Downgrade a specific package:
sudo apt install <package-name>=<old-version>

# Example:
# sudo apt install python3.13=3.13.5-2
```

### 4. Reinstall pip Packages
```bash
pip3 install --force-reinstall flask onnxruntime
```

### 5. Last Resort: Restore from Backup
- If you have a full SD card backup, restore it
- GitHub repo has all configuration files

---

## 📊 UPDATE RISK MATRIX

| Package Type | Managed By | Auto-Update Risk | Protected |
|--------------|------------|------------------|-----------|
| **Node.js** | apt | **NONE** | ✅ Held + Pinned |
| **Kernel** | apt | **NONE** | ✅ Held |
| **CAN Tools** | apt | **NONE** | ✅ Held |
| **Pi Firmware** | apt | **NONE** | ✅ Held |
| **Node-RED** | npm | **NONE** | ✅ Not in apt |
| **Signal K** | npm | **NONE** | ✅ Not in apt |
| **Python pip** | pip3 | **NONE** | ✅ Not in apt |
| **Python 3.13** | apt | **MEDIUM** | ❌ NOT held |
| **Chromium** | apt | **LOW** | ❌ NOT held |
| **System libs** | apt | **LOW-MEDIUM** | ❌ Varies |

---

## 🎯 FINAL RECOMMENDATION

### Conservative Approach (Safest):
**NEVER run `apt upgrade` or `apt full-upgrade`**

Instead:
1. Hold Python: `sudo apt-mark hold python3.13 python3.13-minimal python3.13-dev`
2. Update only security patches manually: `sudo apt install --only-upgrade <specific-package>`
3. Only update when you have time to troubleshoot if something breaks

### Moderate Approach (Balanced):
1. Add Python to hold list
2. Run `apt update && apt list --upgradable` monthly
3. Review the list carefully
4. Update only low-risk packages
5. Test everything after updates

### Aggressive Approach (NOT recommended):
- Run `apt full-upgrade` regularly
- High risk of breaking voice, CAN, camera, or other services
- Only do this if you're confident troubleshooting Linux issues

---

## ✅ RECOMMENDED: Add Python Holds NOW

Run these commands to protect Python from updates:

```bash
ssh d3kos@192.168.1.237

sudo apt-mark hold python3.13
sudo apt-mark hold python3.13-minimal
sudo apt-mark hold python3.13-dev
sudo apt-mark hold libpython3.13-stdlib

# Verify:
apt-mark showhold
```

After this, your system will be **fully protected** from breaking during updates.

---

## 📝 Summary

**Your system is SAFER than you thought!**
- Critical packages already protected ✅
- Just need to add Python to the hold list ✅
- After that, `apt update` is safe (won't change anything held)
- Be cautious with `apt upgrade` (review list first)
- AVOID `apt full-upgrade` unless you know what you're doing

**Bottom line**: Add Python holds, then you can safely run `apt update` without fear.
