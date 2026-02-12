# d3kOS Signal K Configuration Guide

**Version:** 2.0
**Last Updated:** February 8, 2026

This document describes the Signal K server configuration in d3kOS, including data source setup, plugin configuration, and integration with navigation software.

---

## Overview

Signal K is the central data hub in d3kOS, receiving data from multiple sources and making it available via a modern web API:

**Data Sources:**
- NMEA2000 (CAN bus) - Engine data, instruments
- USB GPS - Position, satellites, time
- USB AIS - AIS targets from RTL-SDR receiver
- System monitoring - CPU, GPU, memory, storage

**Data Consumers:**
- OpenCPN (navigation software)
- Node-RED (dashboard and automation)
- Web-based instruments
- Mobile apps (Signal K compatible)

---

## NMEA2000 Configuration

### Overview

d3kOS receives NMEA2000 data from the CAN0 interface (PiCAN-M HAT) using the canboatjs provider. The system operates in **receive-only mode** and does not transmit on the NMEA2000 network.

### Configuration File

**Location:** `~/.signalk/settings.json`

### NMEA2000 Provider Configuration

```json
{
  "id": "can0",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "type": "NMEA2000",
        "subOptions": {
          "type": "canbus-canboatjs",
          "interface": "can0",
          "uniqueNumber": 1918532
        },
        "logging": false
      }
    }
  ],
  "enabled": true
}
```

### Configuration Details

- **Provider Type:** `canbus-canboatjs` - Uses Node.js socketcan library
- **Interface:** `can0` - Linux CAN interface
- **Unique Number:** Randomly generated N2K device address
- **Mode:** Receive-only (does not transmit on N2K network)

### Supported PGNs

Signal K automatically decodes common NMEA2000 Parameter Group Numbers (PGNs):

| PGN | Description | Signal K Path |
|-----|-------------|---------------|
| 127488 | Engine Parameters, Rapid Update | `propulsion.*.revolutions`, `propulsion.*.boostPressure` |
| 127489 | Engine Parameters, Dynamic | `propulsion.*.temperature`, `propulsion.*.pressure` |
| 127505 | Fluid Level | `tanks.*` |
| 128259 | Speed, Water Referenced | `navigation.speedThroughWater` |
| 128267 | Water Depth | `environment.depth.belowTransducer` |
| 129025 | Position, Rapid Update | `navigation.position` |
| 129026 | COG & SOG, Rapid Update | `navigation.courseOverGroundTrue`, `navigation.speedOverGround` |
| 129029 | GNSS Position Data | `navigation.position`, `navigation.gnss.*` |
| 129033 | Time & Date | `navigation.datetime` |
| 130306 | Wind Data | `environment.wind.*` |
| 130310 | Environmental Parameters | `environment.outside.temperature`, `environment.outside.pressure` |

### Verification

Check if NMEA2000 data is being received:

```bash
# Check Signal K logs
sudo journalctl -u signalk -n 50 | grep can0

# Check for N2K data in API
curl -s http://localhost:3000/signalk/v1/api/vessels/self/propulsion

# View live data stream
timeout 5 curl -s http://localhost:3000/signalk/v1/stream
```

---

## USB GPS Configuration

### Overview

d3kOS uses a U-Blox 7 USB GPS receiver with automatic device detection via udev rules. The GPS provides position, velocity, time, and satellite information.

### Universal Device Names

The GPS is automatically mapped to `/dev/gps` regardless of which USB port it's plugged into.

**udev Rule:** `/etc/udev/rules.d/99-marine-usb.rules`

```bash
# U-Blox GPS - creates /dev/gps symlink
SUBSYSTEM=="tty", ATTRS{idVendor}=="1546", ATTRS{idProduct}=="01a7", SYMLINK+="gps", GROUP="dialout", MODE="0666"
```

### Signal K GPS Configuration

**Configuration in settings.json:**

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
          "validateChecksum": true,
          "type": "serial",
          "device": "/dev/gps",
          "baudrate": 9600,
          "sentenceEvent": "nmea0183"
        }
      }
    }
  ],
  "enabled": true
}
```

### GPS Data Paths

| NMEA Sentence | Signal K Path | Description |
|---------------|---------------|-------------|
| GGA | `navigation.position` | GPS position fix |
| RMC | `navigation.position`, `navigation.speedOverGround`, `navigation.courseOverGroundTrue` | Recommended minimum data |
| GSA | `navigation.gnss.methodQuality`, `navigation.gnss.dilutionOfPrecision` | GPS DOP and active satellites |
| GSV | `navigation.gnss.satellites` | GPS satellites in view |
| VTG | `navigation.speedOverGround`, `navigation.courseOverGroundTrue` | Track and speed |
| ZDA | `navigation.datetime` | Time and date |

### Verification

```bash
# Check GPS device exists
ls -la /dev/gps

# Test GPS is outputting NMEA sentences
timeout 3 cat /dev/gps

# Check Signal K GPS data
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/gnss/satellites
```

### Troubleshooting GPS

**No GPS fix (position is null):**
- GPS needs clear view of sky to acquire satellites
- First fix can take 1-5 minutes (cold start)
- Move to location with clear sky view
- Check satellite count: should see 4+ satellites for fix

**GPS not detected:**
```bash
# Check USB device
lsusb | grep -i "u-blox\|1546:01a7"

# Check if /dev/gps symlink exists
ls -la /dev/gps

# Reload udev rules if needed
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## USB AIS Configuration

### Overview

d3kOS uses an RTL-SDR USB dongle (RTL2838) to receive AIS VHF transmissions and decode them into NMEA AIS sentences. The rtl-ais software decodes the 161.975 MHz and 162.025 MHz AIS channels.

### Universal Device Names

The RTL-SDR device is automatically mapped via udev rules:

```bash
# RTL-SDR AIS - creates /dev/rtlsdr_ais symlink
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666", GROUP="plugdev", SYMLINK+="rtlsdr_ais"
```

### AIS Decoder Service

**Service:** `rtl-ais.service`
**Location:** `/etc/systemd/system/rtl-ais.service`

```ini
[Unit]
Description=RTL-SDR AIS Receiver
After=network.target signalk.service
Wants=signalk.service

[Service]
Type=simple
User=d3kos
ExecStart=/usr/bin/rtl_ais -h 127.0.0.1 -P 10110 -n
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### AIS Service Configuration

- **Frequency:** 162 MHz (AIS channels A/B)
- **Output:** TCP localhost:10110
- **Format:** NMEA AIS sentences (!AIVDM, !AIVDO)
- **Auto-start:** Enabled on boot
- **Auto-restart:** Restarts if service fails

### Signal K AIS Configuration

**Configuration in settings.json:**

```json
{
  "id": "ais",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "logging": false,
        "type": "NMEA0183",
        "subOptions": {
          "validateChecksum": true,
          "type": "tcp",
          "host": "127.0.0.1",
          "port": "10110",
          "sentenceEvent": "nmea0183"
        }
      }
    }
  ],
  "enabled": true
}
```

### AIS Data

AIS targets appear in Signal K at:
- `vessels.<mmsi>.*` - Each AIS target has a unique MMSI
- `vessels.<mmsi>.navigation.position`
- `vessels.<mmsi>.navigation.courseOverGroundTrue`
- `vessels.<mmsi>.navigation.speedOverGround`
- `vessels.<mmsi>.name` - Vessel name
- `vessels.<mmsi>.communication.callsignVhf` - Call sign

### Verification

```bash
# Check rtl-ais service
systemctl status rtl-ais.service

# View rtl-ais logs
sudo journalctl -u rtl-ais.service -n 50

# Test if AIS sentences are being output
timeout 5 nc localhost 10110

# Check for AIS targets in Signal K
curl -s http://localhost:3000/signalk/v1/api/vessels/ | grep mmsi
```

### AIS Troubleshooting

**No AIS targets received:**
- AIS requires vessels within VHF range (~20-40 nautical miles)
- Antenna must be properly connected to RTL-SDR
- Check rtl-ais service is running: `systemctl status rtl-ais.service`

**RTL-SDR not detected:**
```bash
# Check USB device
lsusb | grep -i "realtek\|2838"

# Check rtl-sdr tools work
rtl_test -t
```

**Service won't start:**
```bash
# Check logs for errors
sudo journalctl -u rtl-ais.service -n 50

# Manually test rtl_ais
rtl_ais -n
```

---

## Signal K Plugins

### Installed Plugins

d3kOS comes with essential Signal K plugins pre-installed:

1. **signalk-rpi-monitor** - Raspberry Pi system monitoring
2. **@signalk/signalk-to-nmea0183** - Convert Signal K → NMEA0183
3. **signalk-n2kais-to-nmea0183** - Convert N2K AIS → NMEA0183 AIS

### Raspberry Pi Monitor Plugin

**Plugin ID:** `signalk-rpi-monitor`

Monitors Raspberry Pi system health and exposes data via Signal K.

**Signal K Data Paths:**

| Metric | Signal K Path | Units |
|--------|---------------|-------|
| CPU Temperature | `environment.rpi.cpu.temperature` | K (Kelvin) |
| GPU Temperature | `environment.rpi.gpu.temperature` | K (Kelvin) |
| CPU Utilization | `environment.rpi.cpu.utilisation` | ratio (0-1) |
| Memory Usage | `environment.rpi.memory.utilisation` | ratio (0-1) |
| SD Card Usage | `environment.rpi.sd.utilisation` | ratio (0-1) |

**Configuration:**

Plugin is enabled by default. Access configuration at:
- **Web UI:** http://10.42.0.1:3000/admin → Server → Plugin Config → RPI Monitor

**Example API Query:**

```bash
# Get CPU temperature
curl -s http://localhost:3000/signalk/v1/api/vessels/self/environment/rpi/cpu/temperature

# Get all RPi metrics
curl -s http://localhost:3000/signalk/v1/api/vessels/self/environment/rpi
```

### Convert Signal K to NMEA0183 Plugin

**Plugin ID:** `sk-to-nmea0183`

Converts Signal K data back to NMEA0183 format for legacy devices or software.

**Use Case:** OpenCPN can connect to Signal K directly, but this plugin is available for applications that only support NMEA0183.

**Configuration File:** `~/.signalk/plugin-config-data/sk-to-nmea0183.json`

**Supported Sentences:**
- GGA, RMC, GSA, GSV, GLL - GPS position and satellites
- HDT, HDM, HDG - Heading
- VHW - Speed through water
- DPT, DBT, DBS - Depth
- MWV, VWR, VWT - Wind
- VTG - Course and speed over ground
- XDR - Transducer measurements
- ZDA - Time and date

**Configuration:**

Each NMEA sentence can be individually enabled/disabled with throttle rate control.

### N2K AIS to NMEA0183 Plugin

**Plugin ID:** `signalk-n2kais-to-nmea0183`

Specifically converts NMEA2000 AIS messages (PGNs 129038, 129039, 129040, 129041, 129809, 129810) to NMEA0183 AIS sentences (!AIVDM).

**Use Case:** For applications that expect NMEA0183 AIS format from NMEA2000 sources.

**Configuration:**

Plugin automatically converts N2K AIS PGNs when detected. No manual configuration required.

---

## OpenCPN Integration

### Overview

OpenCPN (Open Chart Plotter Navigator) is marine navigation software that integrates with Signal K to display boat data, AIS targets, and navigation information.

### Connection Method

**Recommended:** Direct Signal K WebSocket connection (OpenCPN 5.0+)

OpenCPN can connect directly to Signal K without needing NMEA0183 conversion.

### OpenCPN Configuration

**When OpenCPN is installed on a connected device:**

1. Open OpenCPN
2. Go to **Options → Connections → Add Connection**
3. Configure:
   - **Type:** Signal K
   - **Address:** `10.42.0.1`
   - **Port:** `3000`
   - **Protocol:** Automatic (WebSocket)
4. Click **Apply**
5. OpenCPN will auto-discover the WebSocket endpoint: `ws://10.42.0.1:3000/signalk/v1/stream`

### Data Available to OpenCPN

Via Signal K connection, OpenCPN receives:

- **Position** - GPS position from USB GPS or N2K
- **COG/SOG** - Course and speed over ground
- **Heading** - True/magnetic heading from compass
- **Speed** - Speed through water
- **Depth** - Water depth from depth sounder
- **Wind** - Wind speed and angle
- **AIS Targets** - All AIS vessels within range
- **Engine Data** - RPM, temperature, pressure (display only)
- **Environmental** - Outside temp, barometric pressure

### Alternative: NMEA0183 TCP Connection

If OpenCPN version doesn't support Signal K:

1. Enable and configure `sk-to-nmea0183` plugin in Signal K
2. Set TCP port (e.g., 10111)
3. In OpenCPN:
   - **Type:** Network (TCP)
   - **Address:** `10.42.0.1`
   - **Port:** `10111`
   - **Protocol:** NMEA0183

### Verification

**Test Signal K WebSocket endpoint:**

```bash
# Check endpoint is accessible (will show "Upgrade Required" - this is correct)
curl -s http://10.42.0.1:3000/signalk/v1/stream

# Check data is flowing
timeout 5 curl -s http://localhost:3000/signalk/v1/stream
```

**Check OpenCPN connection in Signal K:**

After connecting OpenCPN, check Signal K logs:

```bash
sudo journalctl -u signalk -n 50 | grep -i websocket
```

---

## Web Interface Access

### Signal K Admin Interface

**URL:** http://10.42.0.1:3000/admin

**Features:**
- View all data sources
- Configure plugins
- Manage data connections
- View security settings
- Install additional plugins from App Store

### Signal K REST API

**Base URL:** http://10.42.0.1:3000/signalk/v1/api/

**Common Endpoints:**

```bash
# Vessel information
curl http://10.42.0.1:3000/signalk/v1/api/vessels/self

# Navigation data
curl http://10.42.0.1:3000/signalk/v1/api/vessels/self/navigation

# Engine data
curl http://10.42.0.1:3000/signalk/v1/api/vessels/self/propulsion

# Environment data
curl http://10.42.0.1:3000/signalk/v1/api/vessels/self/environment

# AIS targets
curl http://10.42.0.1:3000/signalk/v1/api/vessels/

# System health
curl http://10.42.0.1:3000/signalk/v1/api/vessels/self/environment/rpi
```

### Signal K WebSocket Stream

**URL:** ws://10.42.0.1:3000/signalk/v1/stream

Real-time data stream in Signal K delta format. Used by:
- OpenCPN
- Mobile apps
- Web-based instruments
- Custom applications

---

## System Status Verification

### Quick Status Check

```bash
# Check all data sources
echo "=== d3kOS Signal K Data Sources ==="
echo "CAN0 (NMEA2000): $(ip link show can0 2>/dev/null | grep -q 'state UP' && echo 'UP' || echo 'DOWN')"
echo "GPS (/dev/gps): $(test -e /dev/gps && echo 'Connected' || echo 'Not found')"
echo "AIS (rtl-ais): $(systemctl is-active rtl-ais.service)"
echo "Signal K: $(systemctl is-active signalk)"
echo ""

# Check Signal K sources
curl -s http://localhost:3000/signalk/v1/api/ | grep -o '"can0":\|"gps":\|"ais":'
```

### Detailed Verification

```bash
# Check Signal K service
systemctl status signalk

# View Signal K logs
sudo journalctl -u signalk -n 100

# Check all data sources are receiving
sudo journalctl -u signalk -n 50 | grep -i "connected\|gps\|ais\|can0"

# Test live data stream
timeout 10 curl -s http://localhost:3000/signalk/v1/stream | head -50
```

### Expected Output

**Healthy System:**
```
CAN0 (NMEA2000): UP
GPS (/dev/gps): Connected
AIS (rtl-ais): active
Signal K: active

Data Sources: can0, gps, ais, signalk-rpi-monitor
```

---

## Troubleshooting

### Signal K Won't Start

```bash
# Check service status
systemctl status signalk

# View detailed logs
sudo journalctl -u signalk -n 100 --no-pager

# Check for port conflicts
sudo netstat -tuln | grep 3000

# Verify configuration
cat ~/.signalk/settings.json
```

### No Data from Source

**NMEA2000 (CAN0) not receiving:**
```bash
# Check CAN0 interface
ip link show can0

# Check for CAN traffic
candump can0

# Verify PiCAN-M HAT installation
ls -la /dev/pican*
```

**GPS not receiving:**
```bash
# Check GPS device
ls -la /dev/gps

# Test raw GPS output
timeout 3 cat /dev/gps

# Check Signal K logs for GPS errors
sudo journalctl -u signalk | grep -i gps
```

**AIS not receiving:**
```bash
# Check rtl-ais service
systemctl status rtl-ais.service

# Test rtl-ais output
timeout 5 nc localhost 10110

# Verify RTL-SDR device
lsusb | grep Realtek
rtl_test -t
```

### Plugin Not Working

```bash
# List installed plugins
cd ~/.signalk && npm list --depth=0

# Check plugin configuration
ls -la ~/.signalk/plugin-config-data/

# View plugin-specific logs
sudo journalctl -u signalk | grep -i "plugin-name"

# Restart Signal K
sudo systemctl restart signalk
```

### Performance Issues

```bash
# Check CPU temperature
vcgencmd measure_temp

# Check memory usage
free -h

# Check Signal K resource usage
top -p $(pgrep -f signalk-server)

# Check for excessive logging
du -sh ~/.signalk/logs/
```

---

## Advanced Configuration

### Adding Additional Data Sources

1. Edit `~/.signalk/settings.json`
2. Add new entry to `pipedProviders` array
3. Restart Signal K: `sudo systemctl restart signalk`

**Example - Adding NMEA0183 serial device:**

```json
{
  "id": "my-instrument",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "logging": false,
        "type": "NMEA0183",
        "subOptions": {
          "type": "serial",
          "device": "/dev/ttyUSB0",
          "baudrate": 4800,
          "sentenceEvent": "nmea0183"
        }
      }
    }
  ],
  "enabled": true
}
```

### Installing Additional Plugins

**Via Web Interface:**
1. Go to http://10.42.0.1:3000/admin
2. Server → Appstore
3. Search for plugins
4. Click Install

**Via Command Line:**
```bash
cd ~/.signalk
npm install <plugin-name>
sudo systemctl restart signalk
```

### Security Configuration

**Enable authentication:**

1. Go to http://10.42.0.1:3000/admin
2. Security → Users → Add User
3. Enable "Require authentication"
4. Restart Signal K

**SSL/TLS:**

For encrypted connections, configure SSL certificates in Signal K settings.

---

## Related Documentation

- [System Monitoring](SYSTEM_MONITORING.md) - CAN0 health monitoring, system checks
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [API Reference](API_REFERENCE.md) - Signal K API endpoints
- [Hardware Reference](reference/HARDWARE.md) - Hardware specifications

---

## References

- **Signal K Website:** https://signalk.org
- **Signal K Documentation:** https://signalk.org/documentation/
- **Signal K Server GitHub:** https://github.com/SignalK/signalk-server
- **OpenCPN:** https://opencpn.org
- **Canboat:** https://github.com/canboat/canboat

---

## Support

**Issues:** https://github.com/SkipperDon/d3kOS/issues
**Email:** Skipperdon@atmyboat.com
**Website:** https://atmyboat.com/d3kos

---

*This documentation is part of the d3kOS project by Atmyboat.com*
