# d3kOS — OpenPlotter Reference Guide
**Version:** 1.0.0 | **Phase:** 4 | **Updated:** 2026-03-13
**Applies to:** OpenPlotter on Raspberry Pi 4B, Debian Trixie

---

## What is OpenPlotter?

OpenPlotter is the infrastructure layer of d3kOS. It manages the connection between physical marine hardware (GPS receiver, AIS dongle, NMEA instruments) and the software stack. It is intentionally kept in the background — you should rarely need to interact with it directly.

**OpenPlotter URL:** `http://localhost:8081`

---

## What OpenPlotter Manages

| Component | What It Does | d3kOS Relevance |
|-----------|-------------|-----------------|
| Signal K Server | Central data broker — aggregates all instrument data | GPS, AIS, depth appear in AvNav and AI |
| NMEA 0183 plugin | Reads NMEA sentences from GPS/instruments via serial/USB | Raw GPS input |
| AIS plugin | Decodes AIS VHF transmissions from AIS dongle | Other vessel positions |
| OpenCPN plugin | Connects Signal K to OpenCPN (emergency fallback) | OpenCPN chart data |
| pypilot | Autopilot support (optional) | Not active in base d3kOS |

---

## Port Reference

| Service | Port | Purpose |
|---------|------|---------|
| OpenPlotter web UI | `localhost:8081` | Configuration, plugin management |
| Signal K server | `localhost:8099` | Data broker — all instrument data |
| Signal K WebSocket | `ws://localhost:8099/signalk/v1/stream` | Live streaming data |

> **Hard rule:** Signal K WebSocket is `ws://localhost:8099` — never `:3000` (that is the d3kOS dashboard).

---

## Signal K — Core Data Broker

Signal K is the heart of d3kOS's instrument integration. It aggregates NMEA 0183, NMEA 2000, and AIS data into a standardized JSON format, then makes it available to AvNav, Node-RED, and the Phase 5 AI Bridge.

**Data flow:**
```
GPS / NMEA instruments
        ↓
    OpenPlotter (plugins)
        ↓
    Signal K (:8099)
        ↓
  ┌─────┴──────────┐
AvNav            AI Bridge
(:8080)          (:3002, Phase 5)
```

**Signal K configuration:**
- Config file: `/home/d3kos/.signalk/settings.json`
- mDNS: disabled (reduces latency from 5300ms → normal)
- Heap limit: `--max-old-space-size=2048` in systemd unit
- Version: v2.22.1 (upgraded from v2.20.3 for AIS memory leak fix)

---

## When to Access OpenPlotter

You should access `http://localhost:8081` when:

- Adding a new GPS or AIS device
- Changing which serial port a device is on
- Enabling or disabling a plugin
- Troubleshooting why Signal K is not receiving data
- Changing WiFi or hotspot settings

You should **not** access OpenPlotter for:
- Normal daily navigation (use AvNav at :8080)
- AI queries (use Gemini Nav at :3001)
- Dashboard navigation (use d3kOS at :3000)

---

## OpenPlotter Plugins

### NMEA 0183 Plugin

Reads GPS and instrument data from serial or USB devices.

**Config:** OpenPlotter → NMEA 0183 → add connection → select serial port (e.g. `/dev/ttyUSB0`) → baud rate (usually 4800 for GPS, 38400 for fast NMEA).

### Signal K Plugin

Forwards all NMEA data into Signal K. This is what makes GPS appear in AvNav.

**Verify:** OpenPlotter → Signal K → Status should show "Running" and AvNav SK plugin should show a live position.

### AIS Plugin

Decodes AIS VHF data from a USB AIS dongle.

**Common AIS dongle:** dAISy, SH-AIS, others with RTL-SDR or direct USB.

**Config:** OpenPlotter → AIS → select device → verify targets appear in Signal K Data Browser.

---

## Signal K Data Browser

Use the Signal K Data Browser to verify what data is flowing:

1. Open `http://localhost:8099` in a browser
2. Go to **Data Browser** (top menu)
3. Navigate to `vessels.self.navigation.position` — should show current GPS coordinates
4. Navigate to `vessels.self.navigation.speedOverGround` — should show SOG in m/s

If data is missing here, the problem is in OpenPlotter (upstream), not in AvNav or d3kOS.

---

## Troubleshooting Signal K + OpenPlotter

| Problem | Check |
|---------|-------|
| No GPS in Signal K | OpenPlotter → NMEA 0183 → verify device shows green/connected |
| No GPS in AvNav | AvNav → SignalK plugin → verify URL is `http://localhost:8099` |
| Signal K slow responses | Check mDNS is disabled in `/home/d3kos/.signalk/settings.json` |
| Signal K crashes / restarts | Check systemd: `journalctl -u signalk -n 50` — look for OOM errors |
| AIS targets missing | OpenPlotter → AIS → verify dongle detected, signal strength OK |
| OpenPlotter not loading | `sudo systemctl status openplotter` — check for errors |

---

## Service Management

All d3kOS services are managed by systemd. Use the d3kOS Settings page → System Actions to restart services without needing a terminal.

| Service | systemd unit | Port |
|---------|-------------|------|
| Signal K | `signalk.service` | 8099 |
| OpenPlotter | `openplotter*.service` (multiple) | 8081 |
| AvNav | `avnav.service` | 8080 |
| Node-RED | `nodered.service` | 1880 |
| d3kOS Dashboard | `d3kos-dashboard.service` | 3000 |
| d3kOS Gemini Proxy | `d3kos-gemini.service` | 3001 |

**Restart Signal K from settings:** d3kOS Settings → System Actions → Restart Signal K

---

## Why OpenPlotter is Hidden from the Main Menu

OpenPlotter is a configuration tool, not a navigation tool. Sailors should not need to interact with it during a voyage. d3kOS hides it behind the Settings → OpenPlotter section deliberately:

- Normal navigation: AvNav at `:8080`
- AI queries: Gemini Nav at `:3001`
- System status: d3kOS dashboard at `:3000`
- Infrastructure config only: OpenPlotter at `:8081`

---

*d3kOS v2.0 — deployment/d3kOS/docs/OPENPLOTTER_REFERENCE.md*
