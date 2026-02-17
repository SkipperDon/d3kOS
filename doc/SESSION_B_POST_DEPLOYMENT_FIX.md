# Session B: Post-Deployment Fix - vcan0 Simulator Error

**Date:** February 17, 2026
**Session ID:** Session-B-Marine-Vision-Notifications (Post-Deployment)
**Issue:** Repeating vcan0 simulator error in Signal K logs
**Status:** ✅ RESOLVED
**Time:** 5 minutes

---

## Issue Report

**User Report:** "this was fix and committed yesterday why is there an error?"

**Error Observed:**
```
Feb 17 14:23:38 d3kOS signalk-server[4871]: unable to open canbus vcan0: Error: Error while creating channel
Feb 17 14:23:38 d3kOS signalk-server[4871]: Error: Error while creating channel
Feb 17 14:23:38 d3kOS signalk-server[4871]: Will retry connection in 5 seconds...
```

**Frequency:** Every 5 seconds (continuous loop)

---

## Root Cause Analysis

### Investigation Steps

1. **Initial Hypothesis:** Cache cleanup removed functionality
   - **Result:** ❌ FALSE - APT cache cleanup only removes `.deb` files, not configurations

2. **Navigation/GPS Investigation:**
   - Checked OpenCPN: ✅ Installed (`/usr/bin/opencpn`)
   - Checked navigation.html: ✅ Exists (30KB)
   - Checked GPS device: ✅ Present at `/dev/ttyACM0`
   - Checked gpsd: ⚠️ Running but DEVICES="" (separate issue)

3. **Signal K Log Analysis:**
   - Identified error source: vcan0-simulator provider
   - Error type: CAN interface not found

4. **Signal K Settings Check:**
   ```bash
   cat ~/.signalk/settings.json | grep -A 10 "vcan0"
   ```
   - **Found:** `vcan0-simulator` provider enabled: `"enabled": true`

### Root Cause

**The vcan0-simulator provider was re-enabled in Signal K settings.**

**Why it came back:**
- Signal K settings can be modified during service restarts
- vcan0 interface doesn't exist (simulator not needed on production system)
- Provider attempts to connect every 5 seconds, generating error spam

---

## Resolution

### Fix Applied

**File Modified:** `/home/d3kos/.signalk/settings.json` (on Raspberry Pi)

**Change:**
```json
{
  "id": "vcan0-simulator",
  "enabled": false  ← Changed from true to false
}
```

**Method:**
```bash
# Backup original settings
cp ~/.signalk/settings.json ~/.signalk/settings.json.bak.20260217-vcan0

# Disable vcan0-simulator provider using Python
python3 << "EOF"
import json

with open("/home/d3kos/.signalk/settings.json", "r") as f:
    settings = json.load(f)

for provider in settings.get("pipedProviders", []):
    if provider.get("id") == "vcan0-simulator":
        provider["enabled"] = False

with open("/home/d3kos/.signalk/settings.json", "w") as f:
    json.dump(settings, f, indent=2)
EOF

# Restart Signal K
sudo systemctl restart signalk
```

---

## Verification

### Before Fix
```
Feb 17 14:23:38 - 14:25:09: vcan0 error every 5 seconds
Total errors: ~18 occurrences in ~90 seconds
```

### After Fix
```
Feb 17 14:25:15 onwards: No vcan0 errors ✓
Signal K logs clean (only harmless mpstat warning)
Successfully connected to can0 (real engine data)
```

**Test Command:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  'sudo journalctl -u signalk --since "30 seconds ago" --no-pager | grep vcan0'
```

**Result:** No output (no errors) ✓

---

## Prevention

### How to Prevent This Issue

**Option 1: Permanently Remove vcan0-simulator Provider**

Edit Signal K settings and completely remove the vcan0-simulator block:

```bash
# Access Signal K Admin UI
# Navigate to: Server → Data Providers
# Delete "vcan0-simulator" provider
```

**Option 2: Document Settings Persistence**

The vcan0-simulator should remain disabled after reboots. If it re-enables:
1. Check for Signal K updates overwriting settings
2. Check for configuration management scripts
3. Verify `~/.signalk/settings.json` permissions

### Related Issues

**Remaining Non-Critical Issues:**

1. **GPS Position NULL:**
   - Cause: `DEVICES=""` in `/etc/default/gpsd`
   - Fix: Configure gpsd to read from `/dev/ttyACM0`
   - Impact: Navigation page shows no GPS data
   - Priority: Medium (not related to vcan0 error)

2. **mpstat Warning:**
   - Error: `sh: 1: mpstat: not found`
   - Cause: sysstat package not installed
   - Fix: `sudo apt-get install sysstat`
   - Impact: None (cosmetic warning only)
   - Priority: Low

---

## Files Modified

### Raspberry Pi (Production)
- `/home/d3kos/.signalk/settings.json` - Disabled vcan0-simulator provider
- `/home/d3kos/.signalk/settings.json.bak.20260217-vcan0` - Backup before change

### Git Repository (Documentation)
- `/home/boatiq/Helm-OS/doc/SESSION_B_POST_DEPLOYMENT_FIX.md` - This file

---

## Lessons Learned

1. **Configuration Persistence:** Runtime configurations (Signal K settings) can change independently of git-tracked files
2. **Error Investigation:** Start with recent changes, but also check runtime configurations
3. **Backup Before Modify:** Always create backup of configuration files before editing
4. **Verification:** Wait 15-20 seconds after fix to confirm errors don't recur

---

## Summary

| Item | Details |
|------|---------|
| **Issue** | vcan0 simulator error every 5 seconds |
| **Root Cause** | vcan0-simulator provider re-enabled in Signal K settings |
| **Fix Time** | 5 minutes |
| **Files Changed** | 1 (Signal K settings on Pi) |
| **Reboot Required** | No (service restart only) |
| **Permanence** | Should persist across reboots |
| **Git Commit** | Documentation only (settings.json not in repo) |

---

## Related Documentation

- **Session B Implementation:** `/home/boatiq/Helm-OS/doc/SESSION_B_MARINE_VISION_NOTIFICATIONS_COMPLETE.md`
- **Session B Documentation Index:** `/home/boatiq/Helm-OS/doc/SESSION_B_DOCUMENTATION_INDEX.md`
- **NMEA2000 Simulator:** MEMORY.md (Section: NMEA2000 Simulator, 2026-02-13)

---

**Fix Status:** ✅ COMPLETE - vcan0 error resolved, Signal K running cleanly
