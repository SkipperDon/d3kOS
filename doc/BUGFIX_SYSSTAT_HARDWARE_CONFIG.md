# d3kOS Bug Fix: Missing sysstat Package & Hardware Configuration

**Date:** 2026-02-26
**Reporter:** Holger (Linz/Danube, Austria)
**Status:** ✅ FIXED - Documentation Updated
**Severity:** Low (cosmetic error logs, but prevents CPU monitoring)

---

## 🐛 Bug Report

### Issue: Recurring Signal K Error

**Symptoms:**
```
Feb 26 06:20:58 sh: 1: mpstat: not found
Feb 26 06:21:28 sh: 1: mpstat: not found
Feb 26 06:21:58 sh: 1: mpstat: not found
```

**Frequency:** Every 30 seconds
**Impact:**
- Cosmetic error spam in Signal K logs
- Prevents CPU core utilization monitoring
- Signal K's rpi-monitor plugin cannot display CPU graphs

### Root Cause

**Missing Package:** `sysstat` is NOT included in d3kOS base installation

**Why This Happened:**
- d3kOS built on minimal Debian Trixie
- `sysstat` not in base package list
- Signal K's `@signalk/rpi-monitor-plugin` requires `mpstat` command
- `mpstat` is part of `sysstat` package
- **Documentation gap:** Not listed in MASTER_SYSTEM_SPEC.md Appendix B

---

## ✅ Fix: Install sysstat Package

### Quick Fix (5 seconds)

```bash
sudo apt install sysstat
```

### Verify Fix

```bash
# Check mpstat command exists
which mpstat

# Test CPU monitoring
mpstat 1 3

# Check Signal K logs (errors should be gone)
journalctl -u signalk -n 50 --no-pager
```

### Result After Fix

✅ No more `mpstat: not found` errors
✅ CPU core utilization graphs appear in Signal K dashboard
✅ System monitoring data available via rpi-monitor plugin

![Signal K CPU Monitoring](Bildschirmfoto 2026-02-26 um 12.33.28.jpg)

---

## 📝 Documentation Updates

**Files Updated:**
1. `MASTER_SYSTEM_SPEC.md` v3.8 - Added `sysstat` to Appendix B Software Dependencies
2. `BUGFIX_SYSSTAT_HARDWARE_CONFIG.md` - This document (bug report + hardware config guide)

**Installation Instructions Updated:**
- Fresh d3kOS installations now include `sysstat` in package list
- Existing installations: Run `sudo apt install sysstat`

---

## 🔧 Holger's Hardware Configuration

Holger reported using different hardware than d3kOS default setup. Here's how to configure d3kOS for alternative hardware:

### Configuration 1: Moitessier HAT (GPS/AIS via UART)

**Hardware:** [Moitessier HAT](https://openplotter.readthedocs.io/3.x.x/moitessier/configuration.html)
**Difference:** GPS/AIS via serial UART pins (not USB)

#### Step 1: Enable UART in config.txt

**File:** `/boot/firmware/config.txt`

```ini
# Enable hardware UART for Moitessier HAT
enable_uart=1
```

**Apply changes:**
```bash
sudo reboot
```

#### Step 2: Verify UART Device

```bash
# Check UART device exists
ls -l /dev/ttyAMA0
# or
ls -l /dev/serial0

# See raw NMEA data
cat /dev/ttyAMA0
# Should show GPS sentences: $GPGGA, $GPRMC, $GPGSV, etc.
# Should show AIS sentences: !AIVDM, !AIVDO, etc.
```

#### Step 3: Configure Signal K for UART

**File:** `~/.signalk/settings.json`

**Find GPS provider section:**
```json
{
  "id": "gps",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "logging": false,
        "type": "NMEA0183",
        "subOptions": {
          "type": "serial",
          "device": "/dev/ttyACM0",  ← CHANGE THIS
          "baudrate": 4800
        }
      }
    }
  ]
}
```

**Change to:**
```json
{
  "id": "gps",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "logging": false,
        "type": "NMEA0183",
        "subOptions": {
          "type": "serial",
          "device": "/dev/ttyAMA0",   ← Moitessier HAT
          "baudrate": 38400            ← Check Moitessier docs for baud rate
        }
      }
    }
  ]
}
```

**Restart Signal K:**
```bash
sudo systemctl restart signalk
```

#### Step 4: Verify GPS/AIS Data

```bash
# Check GPS position
curl http://localhost:3000/signalk/v1/api/vessels/self/navigation/position

# Check AIS targets
curl http://localhost:3000/signalk/v1/api/vessels/self/

# Monitor Signal K logs
journalctl -u signalk -f
```

---

### Configuration 2: Alternative MCP2515 CAN HAT (12 MHz Oscillator)

**Hardware:** MCP2515 CAN HAT with 12 MHz oscillator (not 16 MHz)
**Difference:** CX5106 uses 16 MHz, some HATs use 12 MHz or 8 MHz

#### Step 1: Identify Oscillator Frequency

**Check your CAN HAT documentation:**
- CX5106 NMEA2000 Gateway: 16 MHz (d3kOS default)
- Waveshare RS485 CAN HAT: 12 MHz
- Seeed Studio 2-Channel CAN-BUS HAT: 16 MHz
- Canable Candlelight: 8 MHz

**Or check physically:**
- Look at crystal oscillator on board (metal component labeled 12.000, 16.000, etc.)

#### Step 2: Modify config.txt

**File:** `/boot/firmware/config.txt`

**Find CAN configuration line:**
```ini
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
```

**Change oscillator frequency:**
```ini
# For 12 MHz oscillator (Holger's HAT)
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25

# For 8 MHz oscillator
dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25
```

#### Step 3: Apply Changes

```bash
sudo reboot
```

#### Step 4: Verify CAN Interface

```bash
# Check CAN interface exists
ip link show can0

# Bring up CAN interface (125 kbps for NMEA2000)
sudo ip link set can0 up type can bitrate 125000

# Monitor CAN bus
candump can0

# Should see NMEA2000 PGN data
```

#### Step 5: Verify Signal K Receiving Data

```bash
# Check engine RPM
curl http://localhost:3000/signalk/v1/api/vessels/self/propulsion/port/revolutions

# Check all engine data
curl http://localhost:3000/signalk/v1/api/vessels/self/propulsion/
```

---

## 🔍 Troubleshooting

### GPS/AIS Not Working

**Problem:** No GPS data in Signal K

**Check:**
```bash
# 1. Device exists
ls -l /dev/ttyAMA0

# 2. UART enabled in config.txt
grep "enable_uart" /boot/firmware/config.txt

# 3. NMEA data flowing
cat /dev/ttyAMA0
# Should see: $GPGGA,$GPRMC,!AIVDM, etc.

# 4. Baud rate correct (38400 for Moitessier, 4800 for most USB GPS)
stty -F /dev/ttyAMA0

# 5. Signal K provider enabled
cat ~/.signalk/settings.json | grep -A 10 "gps"
```

**Fix:**
- Verify `enable_uart=1` in `/boot/firmware/config.txt`
- Check baud rate matches HAT specification (38400, 4800, 9600, etc.)
- Verify device path `/dev/ttyAMA0` or `/dev/serial0`
- Restart Signal K after changes

---

### CAN Bus Not Working

**Problem:** No NMEA2000 data in Signal K

**Check:**
```bash
# 1. CAN interface exists
ip link show can0

# 2. Oscillator frequency correct in config.txt
grep "mcp2515-can0" /boot/firmware/config.txt

# 3. Bring up CAN interface manually
sudo ip link set can0 up type can bitrate 125000

# 4. Monitor raw CAN frames
candump can0
# Should see CAN frames with IDs like 1DEFFF64, 1DF50564, etc.

# 5. Check Signal K provider
cat ~/.signalk/settings.json | grep -A 10 "can0"
```

**Fix:**
- Verify oscillator frequency in config.txt (12000000 or 16000000)
- Check CAN bitrate is 125000 (NMEA2000 standard)
- Verify CAN interface auto-starts: `/etc/systemd/network/80-can.network`
- Check physical CAN wiring (CAN-H, CAN-L, GND, 120Ω termination)

---

## 📊 Hardware Compatibility Matrix

| Hardware | d3kOS Default | Alternative | Config Required |
|----------|---------------|-------------|-----------------|
| **GPS/AIS** | USB GPS (ttyACM0) | Moitessier HAT (ttyAMA0) | config.txt + Signal K |
| **CAN HAT** | CX5106 (16 MHz) | Waveshare (12 MHz) | config.txt oscillator |
| **Camera** | Reolink RLC-810A | Any RTSP camera | Update camera URL |
| **Touchscreen** | Official 7" | Any USB touchscreen | No config needed |
| **Microphone** | Anker S330 | Any USB microphone | Update plughw device |

---

## 🙏 Credits

**Bug Reporter:** Holger (Linz/Danube, Austria)
**Hardware:** Moitessier HAT + 12 MHz CAN HAT
**Date:** February 26, 2026

**Thank you for field testing and reporting this issue!** Your feedback helps make d3kOS better for everyone. 🎯

---

## 📚 Related Documentation

- **MASTER_SYSTEM_SPEC.md** - Section 3 (Hardware Specifications)
- **MASTER_SYSTEM_SPEC.md** - Appendix B (Software Dependencies)
- **Moitessier HAT Configuration:** https://openplotter.readthedocs.io/3.x.x/moitessier/configuration.html
- **MCP2515 CAN HAT Guide:** https://www.waveshare.com/wiki/RS485_CAN_HAT

---

**Version:** 1.0
**Last Updated:** 2026-02-26
**Status:** RESOLVED - Documentation Updated
