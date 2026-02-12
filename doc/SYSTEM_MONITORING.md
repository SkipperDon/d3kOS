# d3kOS System Monitoring

**Version:** 2.0
**Last Updated:** February 8, 2026

This document describes the automated system monitoring and health checks built into d3kOS.

---

## Overview

d3kOS includes automated monitoring services that check critical system components and attempt automatic recovery when issues are detected. All monitoring services log to the system journal and display critical alerts on the console.

---

## CAN0 Health Monitoring

### Purpose

The CAN0 health monitor ensures the NMEA2000 CAN bus interface remains operational at all times. This is critical for receiving marine data from connected devices (GPS, depth sounder, wind instruments, AIS, etc.).

### Features

- **Automatic detection** of CAN0 interface failures
- **Auto-recovery** attempts to bring CAN0 back online
- **Periodic checks** every 5 minutes
- **Boot-time verification** runs 1 minute after system startup
- **Console alerts** for critical failures

### Implementation

**Location:** `/usr/local/bin/check-can0.sh`

**Services:**
- `can0-check.service` - Health check service
- `can0-check.timer` - Periodic execution timer

**Configuration:** `/etc/systemd/system/can0-check.{service,timer}`

### Status Messages

#### Normal Operation
```
[timestamp] ✓ CAN0 is running normally
```
Logged to journal only (silent operation).

#### Recovery Mode
```
[timestamp] ⚠ CAN0 is down, attempting recovery...
[timestamp] Attempting to start can0...
[timestamp] ✓ CAN0 started successfully
```
Displayed on console and logged to journal.

#### Critical Failure
```
[timestamp] ✗ FAILED: CAN0 is not running - Check PiCAN-M hardware connection
```
Displayed on console and logged to journal. Indicates hardware problem requiring user intervention.

### Manual Checks

**Check CAN0 status:**
```bash
ip link show can0 | grep state
```

**Check timer status:**
```bash
systemctl status can0-check.timer
```

**View recent logs:**
```bash
journalctl -u can0-check.service -n 20
```

**Manually run health check:**
```bash
sudo /usr/local/bin/check-can0.sh
```

### Troubleshooting

#### CAN0 Won't Stay Up

**Symptoms:**
- Frequent recovery attempts in logs
- CAN0 goes down shortly after recovery

**Possible Causes:**
1. Loose PiCAN-M HAT connection
2. Power supply insufficient (use 3A+ power supply)
3. CAN bus termination issues
4. Hardware failure

**Solutions:**
1. Power down Pi completely
2. Reseat PiCAN-M HAT firmly
3. Check NMEA2000 backbone termination
4. Verify 12V power to NMEA2000 bus
5. Test with known-good NMEA2000 device

#### No Recovery After Hardware Fix

If you've fixed a hardware issue but CAN0 still shows as down:

```bash
# Manually bring up CAN0
sudo ip link set can0 up type can bitrate 250000

# Restart monitoring
sudo systemctl restart can0-check.service
```

#### Disable CAN0 Monitoring

If you need to temporarily disable monitoring:

```bash
# Stop and disable timer
sudo systemctl stop can0-check.timer
sudo systemctl disable can0-check.timer
```

To re-enable:
```bash
sudo systemctl enable can0-check.timer
sudo systemctl start can0-check.timer
```

---

## GPS Monitoring

### Purpose

The GPS monitor ensures the USB GPS receiver is connected and providing valid position data.

### Universal Device Name

The GPS is automatically mapped to `/dev/gps` via udev rules, regardless of which USB port it's plugged into.

**udev Rule Location:** `/etc/udev/rules.d/99-marine-usb.rules`

### Manual Checks

**Check GPS device:**
```bash
# Verify /dev/gps symlink exists
ls -la /dev/gps

# Check raw GPS output
timeout 3 cat /dev/gps
```

**Check GPS data in Signal K:**
```bash
# Check position
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position

# Check satellites
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/gnss/satellites
```

**View Signal K GPS logs:**
```bash
sudo journalctl -u signalk -n 50 | grep -i gps
```

### Troubleshooting

#### GPS No Fix (Position is Null)

**Symptoms:**
- Signal K shows position as `null`
- No latitude/longitude data

**Possible Causes:**
1. GPS needs clear view of sky
2. Cold start requires 1-5 minutes to acquire satellites
3. Indoor location

**Solutions:**
1. Move to location with clear sky view
2. Wait 2-5 minutes for GPS to acquire satellites
3. Check satellite count (need 4+ for fix)

#### GPS Device Not Found

**Symptoms:**
- `/dev/gps` symlink doesn't exist
- Signal K shows GPS connection errors

**Solutions:**
```bash
# Check if USB device is detected
lsusb | grep -i "u-blox\|1546:01a7"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Replug USB GPS device
```

---

## AIS Monitoring

### Purpose

The AIS monitor ensures the RTL-SDR receiver is decoding AIS VHF transmissions and feeding Signal K.

### AIS Service

**Service:** `rtl-ais.service`
**Auto-start:** Enabled
**Auto-restart:** Yes (restarts on failure)

### Manual Checks

**Check AIS service:**
```bash
# Service status
systemctl status rtl-ais.service

# View logs
sudo journalctl -u rtl-ais.service -n 50
```

**Test AIS decoder output:**
```bash
# Should show NMEA AIS sentences (!AIVDM, !AIVDO)
timeout 5 nc localhost 10110
```

**Check AIS targets in Signal K:**
```bash
# List AIS vessels (by MMSI)
curl -s http://localhost:3000/signalk/v1/api/vessels/ | grep mmsi
```

### Troubleshooting

#### No AIS Targets

**Symptoms:**
- rtl-ais service running but no targets appear
- Signal K shows no AIS vessels

**Possible Causes:**
1. No AIS-equipped vessels within VHF range (20-40 NM)
2. Antenna not connected or poor placement
3. RTL-SDR device failure

**Solutions:**
1. Wait for vessels to come within range
2. Check antenna connection to RTL-SDR
3. Verify RTL-SDR is working:
```bash
rtl_test -t
```

#### AIS Service Won't Start

**Symptoms:**
- `systemctl status rtl-ais.service` shows failed
- No output on TCP port 10110

**Solutions:**
```bash
# Check detailed error logs
sudo journalctl -u rtl-ais.service -n 100

# Test rtl-ais manually
rtl_ais -n

# Check USB device
lsusb | grep -i "realtek\|2838"

# Restart service
sudo systemctl restart rtl-ais.service
```

---

## System Health Monitor

### Purpose

The d3kOS health monitor provides comprehensive system health checking including:
- Signal K server status
- Node-RED status
- CAN bus interface
- System temperature
- Network connectivity
- GPS status
- AIS receiver status

### Implementation

**Location:** `/usr/local/bin/d3kos-health.sh`

**Service:** `d3kos-health.service`

**Configuration:** `/etc/systemd/system/d3kos-health.service`

**Log File:** `/var/log/d3kos-health.log`

### Health Checks

The health monitor runs continuously with checks every 60 seconds:

1. **CAN Bus** - Verifies can0 interface is UP
2. **Signal K** - Checks if signalk service is active
3. **Node-RED** - Checks if nodered service is active
4. **Temperature** - Monitors CPU temperature (warning at >80°C)

### View Health Logs

```bash
# View last 50 entries
sudo tail -50 /var/log/d3kos-health.log

# Follow live updates
sudo tail -f /var/log/d3kos-health.log

# View service status
systemctl status d3kos-health.service
```

### Example Log Output

```
[2026-02-08 12:34:56] === d3kOS Health Monitor Started ===
[2026-02-08 12:34:56] CAN: OK (can0 UP)
[2026-02-08 12:34:56] Signal K: OK
[2026-02-08 12:34:56] Node-RED: OK
[2026-02-08 12:34:56] TEMP: OK (45.2°C)
```

---

## Voice Assistant Monitor

**Note:** Voice assistant monitoring is only active for Tier 2+ (d3kOS-PRO) licenses.

### Purpose

Monitors the "Helm" voice assistant components:
- Wake word detection (PocketSphinx)
- Speech recognition (Vosk)
- AI inference (Phi-2/llama.cpp)
- Text-to-speech (Piper)

### Implementation

**Service:** `d3kos-voice.service`

**Configuration:** `/etc/systemd/system/d3kos-voice.service`

### License Check

The voice service includes automatic license tier verification:
- **Tier 0:** Service disabled with upgrade prompt
- **Tier 2+:** Service enabled and operational

### Status Check

```bash
systemctl status d3kos-voice.service
```

**Tier 0 Expected Output:**
```
● d3kos-voice.service - Loaded but inactive (license required)
```

**Tier 2+ Expected Output:**
```
● d3kos-voice.service - Active and running
```

---

## Monitoring Best Practices

### Daily Checks

For production marine use, verify these daily:

```bash
# Quick system health check
systemctl is-active signalk nodered
ip link show can0 | grep state
vcgencmd measure_temp
```

### Weekly Checks

```bash
# View system health logs
sudo tail -100 /var/log/d3kos-health.log

# Check for service failures
journalctl -p err -n 50

# Verify monitoring services
systemctl status can0-check.timer d3kos-health.service
```

### Pre-Departure Checklist

Before leaving the dock:

- [ ] CAN0 receiving data: `candump can0` (should show traffic)
- [ ] Signal K accessible: `http://10.42.0.1:3000`
- [ ] Node-RED accessible: `http://10.42.0.1:1880`
- [ ] Temperature normal: `vcgencmd measure_temp` (<60°C idle)
- [ ] No errors in logs: `journalctl -p err --since today`

---

## Alert Notifications

### Console Alerts

Critical issues are displayed on the console (visible on HDMI display):
- CAN0 failures
- Service crashes
- High temperature warnings

### Future Enhancements

Planned for v1.0:
- Email alerts (SMTP configuration)
- Push notifications (via Signal K app)
- SMS alerts (GSM modem support)
- Audible alarms (speaker/buzzer)

---

## Customization

### Adjust CAN0 Check Frequency

Edit the timer interval:

```bash
sudo nano /etc/systemd/system/can0-check.timer
```

Change `OnUnitActiveSec=5min` to desired interval (e.g., `1min`, `10min`).

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart can0-check.timer
```

### Adjust Health Check Interval

Edit the health monitor script:

```bash
sudo nano /usr/local/bin/d3kos-health.sh
```

Change `INTERVAL=60` to desired seconds.

Restart service:
```bash
sudo systemctl restart d3kos-health.service
```

### Add Custom Health Checks

Add your own checks to `/usr/local/bin/d3kos-health.sh`:

```bash
check_my_service() {
    if systemctl is-active --quiet my-service; then
        log "My Service: OK"
    else
        log "My Service: WARN"
    fi
}
```

Add the check to the main loop:
```bash
while true; do
    check_can
    check_signalk
    check_nodered
    check_temperature
    check_my_service  # Add your check here
    sleep "$INTERVAL"
done
```

---

## Troubleshooting

### Monitoring Services Not Running

**Check all monitoring services:**
```bash
systemctl status can0-check.timer d3kos-health.service d3kos-voice.service
```

**Restart all monitoring:**
```bash
sudo systemctl restart can0-check.timer d3kos-health.service
```

### No Logs Appearing

**Check journald status:**
```bash
systemctl status systemd-journald
```

**Check log permissions:**
```bash
ls -la /var/log/d3kos-health.log
```

Should be writable by root or d3kos user.

### High CPU Usage from Monitoring

If monitoring causes performance issues:

1. Increase check intervals (see Customization above)
2. Disable verbose logging
3. Consider disabling non-critical checks

---

## Related Documentation

- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Hardware Reference](reference/HARDWARE.md)
- [Network Configuration](reference/NETWORK.md)
- [API Reference](API_REFERENCE.md)

---

## Support

**Issues:** https://github.com/SkipperDon/d3kOS/issues
**Email:** Skipperdon@atmyboat.com
**Website:** https://atmyboat.com/d3kos

---

*This documentation is part of the d3kOS project by Atmyboat.com*
