# Session B: GPS Configuration Fix

**Date:** February 17, 2026
**Session ID:** Session-B-Marine-Vision-Notifications (GPS Fix)
**Issue:** GPS position showing as NULL in Signal K, navigation page empty
**Status:** ✅ RESOLVED
**Time:** 20 minutes

---

## Issue Report

**User Report:** "GPS position is green but no data in navigation"

**Symptoms:**
```
Signal K errors (repeating continuously):
- Cannot read properties of null (reading 'latitude')
- [signalk-to-nmea0183] GGA: no position, not converting

Navigation page:
- GPS status: Green (connected)
- Position data: Empty/NULL
- No latitude, longitude, speed, or course displayed
```

---

## Root Cause Analysis

### Investigation Steps

1. **Initial Check - GPS Hardware:**
   - GPS device exists: `/dev/ttyACM0` ✓
   - GPS symlink exists: `/dev/gps → ttyACM0` ✓
   - u-blox GPS receiver detected ✓

2. **gpsd Configuration Check:**
   ```bash
   cat /etc/default/gpsd
   ```
   - **Found:** `DEVICES=""` (EMPTY!)
   - **Problem:** gpsd wasn't reading from any GPS device

3. **GPS Position Verification:**
   ```bash
   gpspipe -w
   ```
   - **After fix:** Mode 2 (2D fix), 43.687°N, 79.520°W ✓
   - **Satellites:** 3 used, 13 visible
   - **Accuracy:** HDOP 3.57 (moderate - indoor location)

4. **Signal K GPS Provider Check:**
   ```bash
   cat ~/.signalk/settings.json | grep -A 20 "gps"
   ```
   - **Found:** Signal K reading directly from `/dev/gps` (serial)
   - **Problem:** Both gpsd AND Signal K trying to read same serial device
   - **Conflict:** Only one process can read serial device at a time

### Root Cause

**Two-part problem:**

1. **gpsd not configured:** `DEVICES=""` in `/etc/default/gpsd`
   - gpsd service running but not monitoring any GPS device
   - No GPS data being collected

2. **Signal K/gpsd conflict:** After configuring gpsd
   - Signal K reads GPS via direct serial (`/dev/gps`)
   - gpsd also reads GPS via direct serial (`/dev/ttyACM0`)
   - Serial device can only be opened by one process
   - Result: Neither gets consistent data

---

## Resolution

### Fix Part 1: Configure gpsd

**File Modified:** `/etc/default/gpsd`

**Change:**
```bash
# Before:
DEVICES=""

# After:
DEVICES="/dev/ttyACM0"
```

**Commands:**
```bash
# Backup original
sudo cp /etc/default/gpsd /etc/default/gpsd.bak.20260217-gps

# Update configuration
sudo nano /etc/default/gpsd
# Set: DEVICES="/dev/ttyACM0"

# Restart gpsd
sudo systemctl restart gpsd

# Verify GPS fix
gpspipe -w
# Result: Mode 2, position data flowing ✓
```

**Result:** gpsd now receiving GPS data (43.687°N, 79.520°W)

---

### Fix Part 2: Configure Signal K to Use gpsd

**Problem:** Signal K still trying to read `/dev/gps` directly (conflicts with gpsd)

**File Modified:** `~/.signalk/settings.json`

**Change:**
```json
// Before (direct serial):
{
  "id": "gps",
  "pipeElements": [{
    "type": "providers/simple",
    "options": {
      "type": "NMEA0183",
      "subOptions": {
        "type": "serial",
        "device": "/dev/gps",
        "baudrate": 9600
      }
    }
  }]
}

// After (gpsd protocol):
{
  "id": "gps",
  "pipeElements": [{
    "type": "providers/simple",
    "options": {
      "type": "NMEA0183",
      "subOptions": {
        "type": "gpsd",
        "hostname": "localhost",
        "port": 2947
      }
    }
  }]
}
```

**Commands:**
```bash
# Backup Signal K settings
cp ~/.signalk/settings.json ~/.signalk/settings.json.bak.20260217-gpsd

# Update GPS provider to use gpsd
python3 << EOF
import json

with open("/home/d3kos/.signalk/settings.json", "r") as f:
    settings = json.load(f)

for provider in settings.get("pipedProviders", []):
    if provider.get("id") == "gps":
        provider["pipeElements"][0]["options"]["type"] = "NMEA0183"
        provider["pipeElements"][0]["options"]["subOptions"] = {
            "type": "gpsd",
            "hostname": "localhost",
            "port": 2947
        }
        break

with open("/home/d3kos/.signalk/settings.json", "w") as f:
    json.dump(settings, f, indent=2)
EOF

# Restart Signal K
sudo systemctl restart signalk

# Wait 15 seconds for startup
sleep 15

# Verify position data in Signal K
curl -s "http://localhost:3000/signalk/v1/api/" | python3 -m json.tool | grep latitude
```

**Result:** Signal K now receiving GPS data via gpsd ✓

---

## Verification

### Before Fix
```
gpsd: DEVICES="" (not reading any device)
Signal K position: null
Navigation page: Empty
Errors: "Cannot read properties of null (latitude)" every second
```

### After Fix
```
gpsd: Reading /dev/ttyACM0, Mode 2 fix, 3 satellites
Signal K position: 43.6866°N, 79.5196°W
Navigation page: Displaying GPS data ✓
Errors: None (0 errors in last 5 minutes)
```

### Test Results

**GPS Data Flow:**
```
GPS Hardware (/dev/ttyACM0)
    ↓
gpsd (localhost:2947)
    ↓
Signal K (gpsd client)
    ↓
Navigation API & Web UI
```

**Position Accuracy:**
- **Indoor (current):** HDOP 3.57, ±10-30m accuracy, 3 satellites
- **Shows movement:** 1-2 knots drift (normal with weak signals)
- **Expected outdoors:** HDOP <2.0, ±3-5m accuracy, 8+ satellites, 0 knots when stationary

**API Response:**
```bash
curl http://localhost:3000/signalk/v1/api/ | grep latitude
# Output: "latitude": 43.68658333333333
```

---

## GPS Drift Explanation

**User observed:** Navigation showing 2 knots speed and 100° course when stationary

**Explanation:** This is **normal GPS behavior** with weak satellite signals, NOT test/simulated data.

**Why GPS Shows Movement When Stationary:**

| Factor | Current (Indoor) | Ideal (Outdoors) |
|--------|------------------|------------------|
| **Satellites used** | 3 | 8-12 |
| **HDOP (accuracy)** | 3.57 (moderate) | 0.8-1.5 (excellent) |
| **Position error** | ±10-30 meters | ±3-5 meters |
| **Stationary speed** | 1-3 knots (drift) | 0.0-0.1 knots |

**GPS Drift:**
- Position estimate "wanders" within the error circle
- With only 3 satellites, error circle is large (10-30m radius)
- GPS thinks it's moving as position drifts
- Course changes randomly as drift direction changes
- **This is real GPS data, not simulation**

**On the water:**
- Clear sky view = 8+ satellites
- HDOP improves to 0.8-1.5
- Position stable within ±3m
- Stationary shows 0.0-0.1 knots
- Course stable when actually moving

---

## Files Modified

### Raspberry Pi (Production)

1. **`/etc/default/gpsd`**
   - Changed: `DEVICES="/dev/ttyACM0"`
   - Backup: `/etc/default/gpsd.bak.20260217-gps`

2. **`~/.signalk/settings.json`**
   - Changed: GPS provider from direct serial to gpsd protocol
   - Backup: `~/.signalk/settings.json.bak.20260217-gpsd`

### Git Repository (Documentation)

3. **`/home/boatiq/Helm-OS/doc/SESSION_B_GPS_FIX.md`** - This file

---

## Architecture After Fix

```
┌─────────────────┐
│  GPS Hardware   │
│  (u-blox)       │
│  /dev/ttyACM0   │
└────────┬────────┘
         │
         │ Serial NMEA
         ↓
┌─────────────────┐
│     gpsd        │
│  Port 2947      │
│  JSON Protocol  │
└────────┬────────┘
         │
         │ TCP/JSON
         ↓
┌─────────────────┐
│   Signal K      │
│  Port 3000      │
│  gpsd client    │
└────────┬────────┘
         │
         │ HTTP API
         ↓
┌─────────────────┐
│ Navigation Page │
│  Web Browser    │
└─────────────────┘
```

**Key Points:**
- Only gpsd reads from serial device (exclusive access)
- Signal K reads from gpsd via TCP (no conflict)
- Multiple clients can connect to gpsd simultaneously
- GPS data flows reliably from hardware to web UI

---

## Prevention

### How to Avoid This Issue

**Never configure multiple processes to read from the same serial device:**

❌ **Wrong:**
```
gpsd → /dev/ttyACM0
Signal K → /dev/ttyACM0 (CONFLICT!)
```

✓ **Correct:**
```
gpsd → /dev/ttyACM0
Signal K → gpsd (localhost:2947)
```

**Best Practices:**
1. Use gpsd as the single GPS data source
2. Configure all applications to use gpsd protocol
3. Test GPS configuration after system updates
4. Verify DEVICES= is set in `/etc/default/gpsd` after OS reinstall

---

## Troubleshooting

### GPS Position is NULL

1. Check gpsd configuration:
   ```bash
   cat /etc/default/gpsd
   # Should have: DEVICES="/dev/ttyACM0"
   ```

2. Verify GPS device exists:
   ```bash
   ls -la /dev/ttyACM0 /dev/gps
   # Should show: /dev/gps -> ttyACM0
   ```

3. Check if gpsd has GPS fix:
   ```bash
   gpspipe -w | grep TPV
   # Should show: "mode":2 or 3, "lat":..., "lon":...
   ```

4. Check Signal K GPS provider:
   ```bash
   cat ~/.signalk/settings.json | grep -A 10 '"id": "gps"'
   # Should have: "type": "gpsd"
   ```

### GPS Shows Movement When Stationary

**This is normal with weak satellite signals.**

Check accuracy:
```bash
gpspipe -w | grep SKY | head -1
# Look for: "uSat" (satellites used) and "hdop" (accuracy)
```

- **uSat < 4:** Poor accuracy, expect drift
- **HDOP > 3.0:** Moderate accuracy, some drift
- **HDOP < 2.0:** Good accuracy, minimal drift

**Solution:** Move GPS antenna outdoors or near window for better satellite reception.

---

## Related Issues

### Signal K Latitude Errors (Resolved)

Before GPS fix, Signal K logged continuous errors:
```
Cannot read properties of null (reading 'latitude')
```

**Cause:** GPS provider enabled but no position data available

**Resolution:** GPS configuration fix provides position data, errors stopped

### vcan0 Simulator Error (Previously Fixed)

See: `SESSION_B_POST_DEPLOYMENT_FIX.md`

Not related to GPS issue.

---

## Summary

| Item | Details |
|------|---------|
| **Issue** | GPS position NULL in Signal K and navigation page |
| **Root Cause** | gpsd not configured + Signal K/gpsd serial conflict |
| **Fix Time** | 20 minutes (investigation + 2-part fix) |
| **Files Changed** | 2 (gpsd config + Signal K settings) |
| **Reboot Required** | No (service restarts only) |
| **Permanence** | Persistent across reboots ✓ |

---

## Lessons Learned

1. **Serial Device Access:** Only one process can read from a serial device at a time
2. **gpsd Best Practice:** Use gpsd as single GPS data source, other apps connect to gpsd
3. **GPS Drift is Normal:** Weak satellite signals cause position "wander" when stationary
4. **Configuration Persistence:** Changes to `/etc/default/gpsd` and `~/.signalk/settings.json` survive reboots
5. **Satellite Count Matters:** 3 satellites = poor accuracy, 8+ satellites = excellent accuracy

---

## Related Documentation

- **Session B Implementation:** `SESSION_B_MARINE_VISION_NOTIFICATIONS_COMPLETE.md`
- **vcan0 Fix:** `SESSION_B_POST_DEPLOYMENT_FIX.md`
- **NMEA2000 Setup:** MEMORY.md (Section: NMEA2000 Simulator)

---

**GPS Fix Status:** ✅ COMPLETE - Position data flowing to Signal K and navigation page
