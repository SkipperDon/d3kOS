#  d3kOS MASTER SYSTEM SPECIFICATION

**Version**: 3.8 **Date**: February 26, 2026 **Status**: APPROVED - Bug Fix: Added sysstat dependency **Previous Version**: 3.7 (February 22, 2026)


## DOCUMENT CONTROL

| Version | Date | Author | Changes |
| - | - | - | - |
| 1.0 | 2026-02-04 | d3kOS Team | Initial specification |
| 2.0 | 2026-02-06 | d3kOS Team | Integrated approved recommendations from gap analysis |
| 2.1 | 2026-02-11 | d3kOS Team | Added Step 4 (Chartplotter Detection) to Initial Setup wizard, clarified standard PGN compatibility |
| 2.2 | 2026-02-11 | d3kOS Team | Implemented Step 4 with nginx proxy, WebSocket detection, and fullscreen toggle |
| 2.3 | 2026-02-12 | d3kOS Team | Added hybrid AI assistant system (Perplexity + Phi-2), skills.md context management, automatic document retrieval, text input interface, learning/memory features |
| 2.4 | 2026-02-12 | d3kOS Team | Updated wake words: Navigator→Counsel, added "Aye Aye Captain" acknowledgment response |
| 2.5 | 2026-02-13 | d3kOS Team | Added Weather Radar feature (Section 5.5): GPS-based animated radar, marine conditions panel, auto-logging to boatlog every 30 minutes |
| 2.6 | 2026-02-13 | d3kOS Team | Added large touch-friendly map controls (80px buttons): Zoom In/Out, Recenter on Position, Wind/Clouds/Radar overlay toggle |
| 2.7 | 2026-02-13 | d3kOS Team | Added Marine Vision System (Section 5.6): IP67 camera integration, fish capture mode, forward watch mode, species ID, fishing regulations |
| 2.8 | 2026-02-16 | d3kOS Team | Completely rewrote Section 8.3 Data Export: Added central database sync, export formats (JSON with installation\_id), automatic boot-time upload, export queue system, Tier 1+ requirement, API endpoints, 7 export categories (benchmark, boatlog, marine vision, QR code, settings, alerts, snapshots) |
| 2.9 | 2026-02-16 | d3kOS Team | Updated Section 6.3.2: Added tier-based update restrictions (Tier 0/1: image-only updates, Tier 2/3: OTA updates), added Tier 1 configuration preservation via mobile app, added onboarding export (8th category) with reset counter tracking, renamed all "Onboarding Wizard" references to "Initial Setup" |
| 3.0 | 2026-02-16 | d3kOS Team | Added Section 8.3.1 Category \#9: Comprehensive telemetry & analytics export (system performance, user interaction, AI metrics, device environment, business intelligence) - background collection via d3kos-telemetry.service, Tier 1+ only with user consent, 30-day local retention, SQLite storage |
| 3.1 | 2026-02-16 | d3kOS Team | Added Section 6.3.4: E-commerce Integration & Mobile App In-App Purchases - Stripe (primary), Apple App Store IAP (iOS), Google Play Billing (Android), PayPal (alternative), subscription management APIs, payment webhooks, failed payment grace period (3/7/14/24 days), updated Tier 2 pricing to $9.99/month and Tier 3 to $99.99/year (17% annual discount) |
| 3.2 | 2026-02-16 | d3kOS Team | Expanded Section 6.3.4 with comprehensive Stripe Billing implementation details: complete database schema (3 new tables: subscriptions, payments, tier\_upgrades), backend services architecture (webhook handler + subscription API), 8 API endpoints, iOS StoreKit 2 integration guide, Android Billing Library 5.0+ integration guide, detailed 40-60 hour development time breakdown, cost estimates, and complete implementation guide at /doc/STRIPE\_BILLING\_IMPLEMENTATION\_GUIDE.md with working code examples |
| 3.3 | 2026-02-17 | d3kOS Team | Completely rewrote Section 6.3.3 Version Management & Upgrade System: Added d3kOS version tracking (current: 0.9.1-beta), GitHub repository (SkipperDon/d3kos), tier-based upgrade capabilities (Tier 0: NO upgrades - new installation only, Tier 1: NO upgrades - new installation only with config restore, Tier 2/3: YES - curl-based OTA upgrades via mobile app), System Management API (port 8095, 4 endpoints), automated upgrade script with SHA-256 verification and backup, mobile app upgrade flow, and manual rollback process |
| 3.4 | 2026-02-17 | d3kOS Team | Added Section 6.4 AI-Powered Self-Healing System: 5-tier architecture (detection, correlation, AI diagnosis, auto-remediation, user notification), engine anomaly detection with statistical process control, Pi system monitoring (CPU temp, memory, disk, services), pattern matching for common failures (failing SD card, overheating, low power, stuck processes), AI integration for root cause analysis, safe auto-remediation actions (restart services, kill stuck processes, clear temp files), user-friendly error translation, voice alerts (Tier 2+), remediation history tracking. Renamed "factory reset" to "Initial Setup Reset" throughout specification. |
| 3.5 | 2026-02-17 | d3kOS Team | Added Section 4.1.4 Timezone Auto-Detection: 3-tier automatic detection (GPS coordinates → internet geolocation → UTC fallback), runs on first boot via d3kos-timezone-setup.service, detection script at /opt/d3kos/scripts/detect-timezone.sh, config file at /opt/d3kos/config/timezone.txt, manual override in Settings page (no onboarding wizard question). Prevents hardcoded Toronto timezone issue for worldwide deployment. Critical for accurate timestamps in boatlogs, health monitoring, GPS sync, and legal compliance (fishing regulations). |
| 3.6 | 2026-02-20 | d3kOS Team | **Session A Implementation for v0.9.1.2**: Updated system version from 1.0.3 to 0.9.1.2, set tier from 2 to 3 for testing mode with all features enabled, implemented complete timezone auto-detection system (GPS→Internet→UTC with timezonefinder library), created timezone API service on port 8098 with nginx proxy (/api/timezone), enabled and verified voice assistant service with Vosk wake word detection (helm/advisor/counsel), Anker S330 microphone at plughw:2,0. All Session A changes verified, tested, and documented in doc/SESSION\_A\_FOUNDATION\_COMPLETE.md. Foundation ready for Sessions B/C/D. |
| 3.7 | 2026-02-22 | d3kOS Team | **CRITICAL UPDATE - OS Version Corrected**: Updated all OS references from Bookworm to Trixie (Debian 13), kernel from 6.1.x to 6.12.x, window manager from Openbox to Labwc (Wayland compositor). **Phi-2 LLM REMOVED** (Feb 16, 2026): Removed due to 60-180s response time (unusable on boat helm), freed 1.7GB storage. Replaced with OpenRouter (gpt-3.5-turbo, 6-8s) for online queries + rule-based system (13 patterns, 0.17s) for offline simple queries. Updated Node-RED from 3.x to v4.1.4. Documented actual system state: d3kOS v0.9.1.2, Tier 3, 22+ services running. Complete architecture audit performed, architecture.md v3.0 created. |
| 3.8 | 2026-02-26 | d3kOS Team | **Bug Fix**: Added `sysstat` package to Appendix B Software Dependencies. Signal K's rpi-monitor plugin requires `mpstat` command for CPU core utilization monitoring. Missing package caused recurring "mpstat: not found" errors every 30 seconds in Signal K logs. Reported by Holger (Linz/Danube) during field testing. Fix: `sudo apt install sysstat`. Also documented UART GPIO configuration for Moitessier HAT GPS/AIS and MCP2515 oscillator frequency configuration (12MHz vs 16MHz). |



## DEFAULT CREDENTIALS

**⚠️ Security Notice: Change after first login**

| Component | Username | Password |
| - | - | - |
| **System User** | `d3kos` | `d3kos2026` |
| **SSH Access** | `d3kos` | `d3kos2026` |
| **Desktop Login** | `d3kos` | `d3kos2026` |
| ~~**WiFi AP~~** | ~~SSID: `d3kOS`~~ | ~~`d3kos-2026`~~ ❌ **NOT SUPPORTED** |
| **Web Interface** | [http://d3kos.local](http://d3kos.local/) or http://\[IP-ADDRESS\] | (no auth required) |


**Change Password**: Run `passwd` after first login


## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)

2. [System Overview](#system-overview)

3. [Hardware Specifications](#hardware-specifications)

4. [Software Architecture](#software-architecture)

5. [User Interface Specifications](#user-interface-specifications)

6. [Core Features](#core-features)

7. [Network Architecture](#network-architecture)

8. [Data Management](#data-management)

9. [Security & Licensing](#security--licensing)

10. [Performance Requirements](#performance-requirements)

11. [Testing & Quality Assurance](#testing--quality-assurance)

12. [Deployment & Distribution](#deployment--distribution)

13. [Maintenance & Support](#maintenance--support)

14. [Appendices](#appendices)


## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview

d3kOS is a comprehensive marine electronics system built on Raspberry Pi 4, designed to provide boat owners with advanced engine monitoring, navigation assistance, and voice-controlled operations. The system integrates NMEA2000 data, GPS/AIS information, camera surveillance, and AI-powered voice assistance into a unified, touchscreen-optimized interface.

### 1.2 Key Objectives

- **Engine Health Monitoring**: Real-time monitoring with baseline comparison and anomaly detection

- **Voice Control**: Offline AI assistant ("Helm") for hands-free operation

- **Navigation Integration**: Auto-install OpenCPN for users without dedicated chartplotters

- **Camera Integration**: IP camera support with intelligent storage management

- **AODA Compliance**: Accessibility-first design for marine environments

- **Offline-First**: Full functionality without internet connectivity

### 1.3 Target Users

- Recreational boat owners

- Commercial vessel operators

- Marine electronics enthusiasts

- DIY boating community

### 1.4 Success Metrics

- Boot time: \< 60 seconds to operational

- Voice response time: \< 2 seconds

- Dashboard update frequency: 1 Hz (1 second intervals)

- Anomaly detection accuracy: \> 95%

- False positive rate: \< 5%

- User onboarding completion: \< 10 minutes


## 2. SYSTEM OVERVIEW

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐  
│                        USER INTERFACE LAYER                      │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │  Main Menu   │  │  Dashboard   │  │   OpenCPN    │          │  
│  │   (HTML)     │  │ (Node-RED)   │  │  (Charts)    │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
└─────────────────────────────────────────────────────────────────┘  
                              ▼  
┌─────────────────────────────────────────────────────────────────┐  
│                      APPLICATION LAYER                           │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │   Voice      │  │   Camera     │  │    Health    │          │  
│  │  Assistant   │  │  Management  │  │  Monitoring  │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │  Onboarding  │  │   Boat Log   │  │   License    │          │  
│  │   Wizard     │  │   System     │  │  Management  │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
└─────────────────────────────────────────────────────────────────┘  
                              ▼  
┌─────────────────────────────────────────────────────────────────┐  
│                       DATA LAYER                                 │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │  Signal K    │  │   Node-RED   │  │    GPSd      │          │  
│  │   Server     │  │   Flows      │  │   Daemon     │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
└─────────────────────────────────────────────────────────────────┘  
                              ▼  
┌─────────────────────────────────────────────────────────────────┐  
│                      HARDWARE LAYER                              │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │   PiCAN-M    │  │   USB GPS    │  │  USB AIS     │          │  
│  │  (NMEA2000)  │  │              │  │              │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  
│  │  Touchscreen │  │  IP Camera   │  │ USB Mic/Spkr │          │  
│  │ (1920×1200)  │  │  (Reolink)   │  │  (Anker)     │          │  
│  └──────────────┘  └──────────────┘  └──────────────┘          │  
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

1. **Raspberry Pi 4 Model B**: Main processing unit

2. **PiCAN-M HAT**: NMEA2000 interface with micro-fit connector

3. **10.1" Touchscreen**: Primary user interface (1920×1200, 1000 nit)

4. **USB GPS Receiver**: Position and time synchronization

5. **USB AIS Receiver**: Automatic Identification System data

6. **Anker PowerConf S330**: USB speakerphone for voice control

7. **Reolink RLC-810A**: IP camera for surveillance (optional)

### 2.3 Software Stack

| Layer | Component | Version | Purpose |
| - | - | - | - |
| OS | Raspberry Pi OS (64-bit) | Trixie (Debian 13) | Base operating system |
| NMEA | Signal K Server | Latest | Marine data aggregation |
| Automation | Node-RED | v4.1.4 | Data flow and dashboard |
| Navigation | OpenCPN | 5.8.x | Chart plotting (auto-install) |
| GPS | gpsd | Latest | GPS data processing |
| Voice (Wake) | PocketSphinx | Latest | Wake word detection |
| Voice (STT) | Vosk | 0.15 | Speech-to-text |
| Voice (TTS) | Piper | Latest | Text-to-speech |
| AI (Onboard) | Rule-based | 13 patterns | Fast responses for simple queries (0.17s) |
| AI (Online) | OpenRouter | gpt-3.5-turbo | Online AI (6-8s response, internet required) |
| AI Context | skills.md | Custom | Unified knowledge base |
| AI Memory | SQLite | 3.x | Conversation history database |
| Camera | VLC (libvlc) | Latest | RTSP stream viewer |
| UI | Chromium | Latest | Browser-based interface |
| Gestures | Touchégg | Latest | Touchscreen gestures |
| Keyboard | Onboard | Latest | On-screen keyboard |



## 3. HARDWARE SPECIFICATIONS

### 3.1 Minimum Requirements

| Component | Specification | Notes |
| - | - | - |
| **Raspberry Pi** | 4 Model B, 4GB RAM | 8GB recommended for voice features |
| **SD Card** | 64GB Class 10 (A2) | 128GB recommended |
| **USB Storage** | 128GB USB drive | Installed at `/media/d3kos/6233-3338` (119.2GB usable) |
| **Power Supply** | 5V 3A USB-C | Official Raspberry Pi PSU required |
| **HAT** | PiCAN-M with micro-fit | NMEA2000 interface |
| **Display** | 10.1" 1920×1200 IPS | 1000 nit brightness, capacitive touch |
| **GPS** | USB GPS receiver | VK-162 or equivalent |
| **AIS** | USB AIS receiver | dAISy or equivalent |


### 3.2 Optional Hardware

| Component | Model | Purpose |
| - | - | - |
| **Camera** | Reolink RLC-810A | IP camera with night vision |
| **Speakerphone** | Anker PowerConf S330 | Voice control (Tier 2+) |
| **Ethernet** | USB to Ethernet | Internet connectivity |
| **WiFi Adapter** | USB WiFi dongle | Extended range (if Pi 4 WiFi insufficient) |


### 3.3 Environmental Specifications

- **Operating Temperature**: 0°C to 50°C (32°F to 122°F)

- **Storage Temperature**: -20°C to 60°C (-4°F to 140°F)

- **Humidity**: 5% to 95% non-condensing

- **Ingress Protection**: IP20 (electronics enclosure required for marine use)

- **Vibration**: Tested for marine vibration (engine room mounting)

### 3.4 Power Requirements

- **Voltage**: 12V DC (boat power) → 5V DC (Raspberry Pi via converter)

- **Current Draw**: 3A peak, 2A typical

- **Power Consumption**: 15W peak, 10W typical

- **Recommended Converter**: Victron Orion-Tr 12/12-9A or equivalent with noise filtering

### 3.5 Physical Mounting

- **Enclosure**: Custom 3D-printed or aluminum case (STL files provided)

- **Mounting**: VESA 75mm or custom bracket

- **Cable Management**: Strain relief required for all connections

- **Cooling**: Passive heatsink + case ventilation (no fans for marine reliability)


## 4. SOFTWARE ARCHITECTURE

### 4.1 Operating System Configuration

#### 4.1.1 Base OS

- **Distribution**: Raspberry Pi OS (64-bit) Trixie (Debian 13)

- **Kernel**: 6.12.x or later

- **Boot Mode**: Console auto-login → startx (no display manager)

- **Window Manager**: Labwc (Wayland compositor)

- **Auto-start**: Chromium in maximized mode (NOT kiosk mode - preserve Pi menu access)

#### 4.1.2 System Services (systemd)

| Service | File | Purpose | Auto-start |
| - | - | - | - |
| Signal K | `signalk.service` | Marine data server | Yes |
| Node-RED | `nodered.service` | Automation and dashboard | Yes |
| gpsd | `gpsd.service` | GPS data processing | Yes |
| Voice Assistant | `d3kos-voice.service` | Wake word and voice control | Yes (Tier 2+) |
| Camera Service | `helm-camera.service` | IP camera management | Yes (if camera detected) |
| Health Monitor | `d3kos-health.service` | System and engine monitoring | Yes |
| Boat Log | `helm-boatlog.service` | Voice log management | Yes (Tier 2+) |


#### 4.1.3 CAN Bus Configuration

```
\# /etc/network/interfaces.d/can0  
auto can0  
iface can0 inet manual  
    pre-up /sbin/ip link set can0 type can bitrate 250000  
    up /sbin/ifconfig can0 up  
    down /sbin/ifconfig can0 down
```

#### 4.1.4 Timezone Auto-Detection

**Problem**: Base image has timezone hardcoded to America/Toronto (EST/EDT), causing incorrect timestamps for users worldwide.

**Solution**: Automatic timezone detection on first boot using 3-tier fallback system.


##### Detection Flow (First Boot)

**Execution**: Before onboarding wizard, via systemd service

```
d3kos-timezone-setup.service (oneshot, first boot)  
    ↓  
/opt/d3kos/scripts/detect-timezone.sh  
    ↓  
┌─────────────────────────────────────────┐  
│  Tier 1: GPS Coordinate Detection      │  
│  Wait up to 30 seconds for GPS fix     │  
│  Use lat/lon → timezone lookup          │  
└─────────────────────────────────────────┘  
    ↓ (if GPS unavailable)  
┌─────────────────────────────────────────┐  
│  Tier 2: Internet Geolocation          │  
│  Use IP address → timezone via API      │  
│  (worldtimeapi.org or ip-api.com)       │  
└─────────────────────────────────────────┘  
    ↓ (if internet unavailable)  
┌─────────────────────────────────────────┐  
│  Tier 3: Default to UTC                │  
│  Safe fallback, user can change later   │  
└─────────────────────────────────────────┘  
    ↓  
timedatectl set-timezone \<detected\_timezone\>  
    ↓  
Save to /opt/d3kos/config/timezone.txt
```


##### Detection Script

**File**: `/opt/d3kos/scripts/detect-timezone.sh`

**Method 1: GPS (Best)**

```
\# Wait up to 30 seconds for GPS fix  
GPS\_DATA=$(gpspipe -w -n 10 | grep -m 1 "TPV")  
LAT=$(echo "$GPS\_DATA" | jq -r '.lat')  
LON=$(echo "$GPS\_DATA" | jq -r '.lon')  
  
\# Lookup timezone from coordinates (GeoNames API)  
TIMEZONE=$(curl -s "http://api.geonames.org/timezoneJSON?lat=$LAT&lng=$LON&username=d3kos" | jq -r '.timezoneId')  
  
\# Example: lat=28.5383, lon=-81.3792 → "America/New\_York"
```

**Method 2: Internet Geolocation (Fallback)**

```
\# Use IP-based geolocation  
TIMEZONE=$(curl -s http://worldtimeapi.org/api/ip | jq -r '.timezone')  
  
\# Example: User in Miami → "America/New\_York"
```

**Method 3: UTC Default (Last Resort)**

```
TIMEZONE="UTC"
```

**Set System Timezone**:

```
timedatectl set-timezone "$TIMEZONE"  
  
\# Save detection metadata  
cat \> /opt/d3kos/config/timezone.txt \<\<EOF  
\{  
  "timezone": "$TIMEZONE",  
  "detection\_method": "GPS|Internet|Default",  
  "detected\_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",  
  "latitude": "$LAT",  
  "longitude": "$LON"  
\}  
EOF
```


##### Systemd Service

**File**: `/etc/systemd/system/d3kos-timezone-setup.service`

```
\[Unit\]  
Description=d3kOS Timezone Auto-Detection  
After=network.target gpsd.service  
Before=d3kos-first-boot.service  
  
\[Service\]  
Type=oneshot  
ExecStart=/opt/d3kos/scripts/detect-timezone.sh  
RemainAfterExit=yes  
StandardOutput=journal  
StandardError=journal  
  
\[Install\]  
WantedBy=multi-user.target
```


##### Config File

**File**: `/opt/d3kos/config/timezone.txt`

```
\{  
  "timezone": "America/New\_York",  
  "detection\_method": "GPS",  
  "detected\_at": "2026-02-17T23:30:00Z",  
  "latitude": 28.5383,  
  "longitude": -81.3792  
\}
```


##### Manual Override (Settings Page)

**Location**: Settings → System → Timezone

**API Endpoint**: `POST /system/timezone` (port 8095)

**Request**:

```
\{  
  "timezone": "America/Los\_Angeles"  
\}
```

**Response**:

```
\{  
  "success": true,  
  "timezone": "America/Los\_Angeles",  
  "message": "Timezone updated successfully"  
\}
```

**Common Timezones** (Settings UI dropdown):

- America/New\_York (Eastern Time - US/Canada)

- America/Chicago (Central Time - US/Canada)

- America/Denver (Mountain Time - US/Canada)

- America/Los\_Angeles (Pacific Time - US/Canada)

- America/Halifax (Atlantic Time - Canada)

- America/Anchorage (Alaska Time)

- Pacific/Honolulu (Hawaii Time)

- Europe/London (UK Time - GMT/BST)

- Europe/Paris (Central Europe Time)

- Australia/Sydney (Australian Eastern Time)

- UTC (Universal Time)

**Settings UI**:

```
┌─────────────────────────────────────────┐  
│  Timezone Configuration                 │  
├─────────────────────────────────────────┤  
│  Current Timezone:                      │  
│  America/New\_York (Eastern Time)        │  
│                                         │  
│  Current Time: 6:30 PM                  │  
│  UTC Time: 11:30 PM                     │  
│                                         │  
│  Detection Method: GPS                  │  
│  Last Updated: Feb 17, 2026 11:30 PM    │  
│                                         │  
│  \[ Change Timezone \]                    │  
└─────────────────────────────────────────┘
```


##### Why This is Critical

**Impacts**:

- ❌ **Boatlog timestamps** - Wrong time in all log entries

- ❌ **Health monitoring** - Incorrect anomaly detection times

- ❌ **Data exports** - Wrong timestamps in cloud database

- ❌ **GPS synchronization** - Time mismatch between GPS and system

- ❌ **Legal compliance** - Fishing regulations are time-based (dawn/dusk, seasonal)

- ❌ **User experience** - Confusing to see wrong time everywhere

**Example Issue**:

```
User in California sees:  
  Boatlog entry: "Started engine at 10:00 AM" (Toronto time)  
  Actual local time: 7:00 AM (Pacific time)  
  
User confused: "I didn't start the engine at 10 AM!"
```


##### Implementation Status

**Status**: ⏳ NOT IMPLEMENTED (Specification Only)

**Estimated Time**: 4-6 hours

- Detection script: 2 hours

- Systemd service: 1 hour

- Settings UI: 1 hour

- API endpoint: 1 hour

- Testing: 1 hour

**Priority**: High

- Affects all timestamps system-wide

- Critical for worldwide deployment

- Legal compliance issue

**Workaround Until Implemented**:

- Users must manually run: `sudo timedatectl set-timezone \<timezone\>`

- Or accept Toronto time and mentally adjust


### 4.2 Signal K Server Configuration

#### 4.2.1 Data Sources

```
\{  
  "vessels": \{  
    "self": "urn:mrn:signalk:uuid:generated-on-install"  
  \},  
  "pipedProviders": \[  
    \{  
      "id": "nmea2000-can0",  
      "pipeElements": \[  
        \{  
          "type": "providers/simple",  
          "options": \{  
            "type": "NMEA2000",  
            "subOptions": \{  
              "type": "canbus",  
              "interface": "can0"  
            \}  
          \}  
        \}  
      \]  
    \},  
    \{  
      "id": "gps-usb",  
      "pipeElements": \[  
        \{  
          "type": "providers/gpsd",  
          "options": \{  
            "port": 2947  
          \}  
        \}  
      \]  
    \},  
    \{  
      "id": "ais-usb",  
      "pipeElements": \[  
        \{  
          "type": "providers/nmea0183",  
          "options": \{  
            "port": "/dev/ttyUSB1",  
            "baudrate": 38400  
          \}  
        \}  
      \]  
    \}  
  \]  
\}
```

#### 4.2.2 Data Keys (NMEA2000 PGNs)

| PGN | Description | Signal K Path | Update Rate |
| - | - | - | - |
| 127488 | Engine Parameters, Rapid | `propulsion.\*.rpm` | 100ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.\*.oilPressure` | 500ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.\*.temperature` | 500ms |
| 127505 | Fluid Level | `tanks.\*.currentLevel` | 2500ms |
| 127508 | Battery Status | `electrical.batteries.\*.voltage` | 1500ms |
| 128259 | Speed (Water Referenced) | `navigation.speedThroughWater` | 1000ms |
| 128267 | Water Depth | `environment.depth.belowTransducer` | 1000ms |
| 129025 | Position, Rapid Update | `navigation.position` | 100ms |
| 129026 | COG & SOG, Rapid Update | `navigation.courseOverGroundTrue` | 100ms |
| 129029 | GNSS Position Data | `navigation.gnss.\*` | 1000ms |


### 4.3 Node-RED Configuration

#### 4.3.1 Dashboard Layout

**Dashboard 2.0 UI Configuration**:

- Base URL: `http://localhost:1880/dashboard`

- Theme: Dark (black background \#000000)

- Font: 22px minimum

- Touch targets: 120×80px minimum

**Page Layout**:

```
Page 1: Engine Gauges  
├─ Row 1: Tachometer, Tilt/Trim, Temp, Voltage, Oil Pressure  
├─ Row 2: Tank Levels (Fresh, Black, Fuel, Battery)  
├─ Row 3: System Status (CPU, Memory, Storage, GPU)  
└─ Row 4: Network Status (WiFi, Ethernet, NMEA2000, Internet)  
  
Page 2: Boat Log  
├─ Voice recording interface  
├─ Log entry list (last 30 days)  
└─ Export options  
  
Page 3: Health Reports  
├─ Engine health summary  
├─ Anomaly history  
├─ Trend graphs  
└─ Maintenance recommendations
```

#### 4.3.2 Flow Architecture

**Main Flows**:

1. **Signal K Input**: Subscribe to all relevant paths

2. **Data Processing**: Unit conversions, threshold checks, anomaly detection

3. **Dashboard Output**: Update gauges and charts

4. **Logging**: Write to files for historical analysis

5. **Alerts**: Trigger voice/visual warnings on anomalies

**Example Flow Snippet**:

```
// Engine RPM monitoring  
\[signalk:in\] → \[threshold check\] → \[anomaly detector\] → \[dashboard gauge\]  
                                 ↓  
                           \[voice alert if critical\]  
                                 ↓  
                           \[log to file\]
```

### 4.4 Voice Assistant Architecture

#### 4.4.1 Voice Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────────┐  
│ Microphone  │ --\> │ PocketSphinx│ --\> │    Vosk     │ --\> │  Query Handler   │  
│   (Audio)   │     │ (Wake Word) │     │    (STT)    │     │  (AI Router)     │  
└─────────────┘     └─────────────┘     └─────────────┘     └──────────────────┘  
                           │                   │                   │  
                           ▼                   ▼                   │  
                    "Helm" detected    Transcription               │  
                                                                    ▼  
                                              ┌─────────────────────┴─────────────┐  
                                              │                                   │  
                                              ▼                                   ▼  
                                    ┌──────────────────┐              ┌──────────────────┐  
                                    │   Rule-Based     │              │   OpenRouter     │  
                                    │  (13 patterns)   │              │ (gpt-3.5-turbo)  │  
                                    │   0.17-0.22s     │              │      6-8s        │  
                                    └──────────────────┘              └──────────────────┘  
                                              │                                   │  
                                              └─────────────┬─────────────────────┘  
                                                            ▼  
                                                     ┌─────────────┐  
                                                     │    Piper    │  
                                                     │    (TTS)    │  
                                                     └─────────────┘  
                                                            ▼  
                                                        Speaker
```

#### 4.4.2 Wake Word Training

**PocketSphinx Configuration**:

```
\# /opt/d3kos/config/sphinx/helm.dict  
HELM    HH EH L M  
  
\# /opt/d3kos/config/sphinx/helm.lm  
\# Language model with "Helm" as primary keyword
```

**Sensitivity Tuning**:

- Threshold: 1e-40 (adjust based on ambient noise)

- Buffer: 2048 samples

- Sample rate: 16kHz

#### 4.4.3 STT Configuration

**Vosk Model**:

- Model: `vosk-model-small-en-us-0.15`

- Size: 50MB

- Location: `/opt/d3kos/models/vosk/`

- Sample rate: 16kHz

- Real-time factor: \< 0.5 (2x faster than real-time on Pi 4)

#### 4.4.4 TTS Configuration

**Piper Voice**:

- Voice: `en\_US-amy-medium`

- Quality: Medium (balance speed vs quality)

- Sample rate: 22050Hz

- Speed: 1.0x (adjustable 0.8x - 1.5x)

#### 4.4.5 AI Backend Configuration

**⚠️ IMPORTANT: Phi-2 LLM REMOVED (February 16, 2026)**

- **Reason**: 60-180 second response time unusable on boat helm

- **Storage Freed**: 1.7GB (model file removed)

- **Replacement**: Hybrid online/offline system

**Current AI Architecture**:

**Online AI (OpenRouter - Primary)**:

- Provider: OpenRouter API ([https://openrouter.ai](https://openrouter.ai/))

- Model: openai/gpt-3.5-turbo

- Response Time: 6-8 seconds

- Requirements: Internet connection

- Use Case: Complex queries, natural language understanding

**Offline AI (Rule-Based - Fallback)**:

- Pattern Matching: 13 predefined query types

- Response Time: 0.17-0.22 seconds (with Signal K cache)

- Supported Queries: rpm, oil, temperature, fuel, battery, speed, heading, boost, hours, location, time, help, status

- Use Case: Simple sensor queries when offline

**AI Configuration File** (`/opt/d3kos/config/ai-config.json`):

```
\{  
  "openrouter": \{  
    "api\_key": "sk-or-v1-...",  
    "model": "openai/gpt-3.5-turbo",  
    "base\_url": "https://openrouter.ai/api/v1/chat/completions"  
  \},  
  "cache\_ttl": 3.0,  
  "default\_provider": "auto"  
\}
```

**Wake Word Routing**:

- **"helm"** → Auto-select (online if available, offline if not)

- **"advisor"** → Force offline (rule-based only)

- **"counsel"** → Force online (OpenRouter)

#### 4.4.6 Command Parser

**Supported Commands**:

```
const commands = \{  
  "what's the engine status": () =\> readEngineMetrics(),  
  "any anomalies": () =\> checkAnomalies(),  
  "open opencpn": () =\> launchOpenCPN(),  
  "start benchmarking": () =\> startBenchmark(),  
  "start onboarding": () =\> launchOnboarding(),  
  "record boat log": () =\> startVoiceRecording(),  
  "helm post": () =\> saveLogEntry(),  
  "helm end": () =\> stopListening()  
\};
```

**Fuzzy Matching**:

- Use Levenshtein distance for command matching

- Threshold: 80% similarity

- Fallback: If no match, pass to LLM for interpretation

### 4.5 Hybrid AI Assistant System Architecture

#### 4.5.1 System Overview

**⚠️ UPDATED (February 16, 2026)**: Phi-2 LLM removed, replaced with rule-based + OpenRouter system.

d3kOS implements a hybrid AI system that intelligently routes queries between two backends:

- **Online AI** (OpenRouter gpt-3.5-turbo): Fast (6-8s), powerful, requires internet

- **Offline AI** (Rule-based patterns): Ultra-fast (0.17s), 13 query types, no internet

**Routing Logic**:

```
User Query (Voice OR Text)  
         ↓  
    Pattern Match?  
    ┌────────┴────────┐  
    │                 │  
 Match            No Match  
 Found               ↓  
    ↓          Check Internet  
Rule-Based          │  
Response       ┌────┴────┐  
0.17-0.22s     │         │  
    ↓        Online   Offline  
Store in DB    │         │  
    ↓     OpenRouter  Message  
Response  gpt-3.5     "Need  
    │      6-8s    internet"  
    └────┬───┘         │  
         ↓             │  
    Store in DB       │  
         │            │  
         └─────┬──────┘  
               ▼  
          Response
```

#### 4.5.2 Online AI Configuration (OpenRouter)

**API Configuration** (`/opt/d3kos/config/ai-config.json`):

```
\{  
  "openrouter": \{  
    "api\_key": "sk-or-v1-...",  
    "base\_url": "https://openrouter.ai/api/v1/chat/completions",  
    "model": "openai/gpt-3.5-turbo",  
    "enabled": true,  
    "max\_tokens": 500,  
    "temperature": 0.7,  
    "timeout": 30  
  \},  
  "cache\_ttl": 3.0,  
  "default\_provider": "auto"  
\}
```

**API Request Format**:

```
async function queryOpenRouter(question, context) \{  
  const config = loadAIConfig();  
  
  const response = await fetch(config.openrouter.base\_url, \{  
    method: 'POST',  
    headers: \{  
      'Authorization': \`Bearer $\{config.openrouter.api\_key\}\`,  
      'Content-Type': 'application/json',  
      'HTTP-Referer': 'https://d3kos.local',  
      'X-Title': 'd3kOS Marine Assistant'  
    \},  
    body: JSON.stringify(\{  
      model: config.openrouter.model,  
      messages: \[  
        \{  
          role: 'system',  
          content: \`You are a marine assistant for d3kOS. Context:\\n$\{context.skills\}\\n\\nCurrent boat data:\\n$\{JSON.stringify(context.currentData)\}\`  
        \},  
        \{  
          role: 'user',  
          content: question  
        \}  
      \],  
      max\_tokens: config.openrouter.max\_tokens,  
      temperature: config.openrouter.temperature  
    \})  
  \});  
  
  const data = await response.json();  
  return data.choices\[0\].message.content;  
\}
```

**Rate Limiting**:

- OpenRouter: Varies by model (gpt-3.5-turbo: generous limits)

- Handle 429 (rate limit) errors gracefully

- Display estimated wait time to user

- Fallback to rule-based responses

**Error Handling**:

```
async function queryOnlineAI(question) \{  
  try \{  
    return await queryOpenRouter(question, context);  
  \} catch (error) \{  
    if (error.status === 429) \{  
      speak("API rate limit reached. Using offline mode.");  
      return ruleBasedResponse(question);  
    \} else if (error.status === 401) \{  
      speak("API key invalid. Please check settings. Using offline mode.");  
      return ruleBasedResponse(question);  
    \} else \{  
      speak("Online AI unavailable. Using offline mode.");  
      return ruleBasedResponse(question);  
    \}  
  \}  
\}
```

#### 4.5.3 Internet Detection

**Method 1: HTTP HEAD Request**:

```
async function checkInternetConnection() \{  
  try \{  
    const controller = new AbortController();  
    const timeout = setTimeout(() =\> controller.abort(), 3000);  
  
    const response = await fetch('https://www.google.com/favicon.ico', \{  
      method: 'HEAD',  
      signal: controller.signal  
    \});  
  
    clearTimeout(timeout);  
    return response.ok;  
  \} catch (error) \{  
    return false;  
  \}  
\}
```

**Method 2: DNS Resolution**:

```
const dns = require('dns');  
  
function checkInternetDNS() \{  
  return new Promise((resolve) =\> \{  
    dns.resolve('google.com', (err) =\> \{  
      resolve(!err);  
    \});  
  \});  
\}
```

**Cache Result** (avoid checking on every query):

```
let internetCache = \{  
  available: false,  
  lastCheck: 0,  
  ttl: 30000  // 30 seconds  
\};  
  
async function hasInternet() \{  
  const now = Date.now();  
  if (now - internetCache.lastCheck \< internetCache.ttl) \{  
    return internetCache.available;  
  \}  
  
  internetCache.available = await checkInternetConnection();  
  internetCache.lastCheck = now;  
  return internetCache.available;  
\}
```

#### 4.5.4 Skills.md Context Management

**File Location**: `/opt/d3kos/config/skills.md`

**Structure**:

```
\# d3kOS Skills Database  
  
\#\# System Information  
- Installation ID: XXXX-XXXX-XXXX  
- Installation Date: 2026-02-12  
- Last Updated: 2026-02-12 08:00:00  
- Skills Version: 1.0  
  
\#\# Boat Information  
\[Boat details from onboarding\]  
  
\#\# Engine Information  
\[Engine specs from onboarding\]  
  
\#\# Engine Manual (Text Extracted)  
\[Compressed text from engine PDF manual\]  
  
\#\# Boat Owner's Manual (Text Extracted)  
\[Compressed text from boat PDF manual\]  
  
\#\# Regional Regulations  
\[Local boating regulations\]  
  
\#\# Best Practices  
\[BoatUS.org best practices\]  
  
\#\# Conversation History (Recent)  
\[Last 50 Q&A pairs\]
```

**Loading Context**:

```
async function loadContext() \{  
  const skills = fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8');  
  const onboarding = JSON.parse(fs.readFileSync('/opt/d3kos/config/onboarding.json'));  
  const recentData = await getRecentEngineData();  
  
  return \{  
    skills,  
    onboarding,  
    currentData: \{  
      rpm: recentData.rpm,  
      oilPressure: recentData.oilPressure,  
      temperature: recentData.temperature,  
      fuelLevel: recentData.fuelLevel,  
      voltage: recentData.voltage  
    \}  
  \};  
\}
```

**Context Size Management**:

- OpenRouter (gpt-3.5-turbo): 16K token context window (can send full skills.md)

- Rule-based: No context window (uses pattern matching only)

**Signal K Data Caching**:

```
// Cache Signal K data for 3 seconds to speed up responses  
let signalKCache = \{  
  data: null,  
  timestamp: 0,  
  ttl: 3000  // 3 seconds  
\};  
  
async function getBoatStatus() \{  
  const now = Date.now();  
  if (now - signalKCache.timestamp \< signalKCache.ttl) \{  
    return signalKCache.data;  // Return cached data (0.001s)  
  \}  
  
  // Fetch fresh data from Signal K (18s)  
  signalKCache.data = await fetchSignalKData();  
  signalKCache.timestamp = now;  
  return signalKCache.data;  
\}
```

**Performance Optimization**:

- First query: 18s (fetch Signal K data + AI response)

- Subsequent queries (within 3s): 0.17s (cached data + rule-based) or 6s (cached data + OpenRouter)

- Result: 100× speedup for rapid-fire questions

#### 4.5.5 Document Retrieval System

**Automatic Retrieval During Onboarding**:

During Initial Setup wizard (Step 19-20), if internet is available:

1. **Boat Manual Retrieval**:

```
async function searchBoatManual(make, model, year) \{  
  // Search manualslib.com  
  const searchUrl = \`https://www.manualslib.com/search.html?q=$\{make\}+$\{model\}+$\{year\}+boat\`;  
  const searchResults = await fetch(searchUrl);  
  const html = await searchResults.text();  
  
  // Parse results for PDF links  
  const pdfLinks = extractPDFLinks(html);  
  
  if (pdfLinks.length \> 0) \{  
    // Download first result  
    const pdfUrl = pdfLinks\[0\];  
    const pdfBuffer = await downloadPDF(pdfUrl);  
  
    // Extract text  
    const text = await extractPDFText(pdfBuffer);  
  
    return text;  
  \}  
  
  return null;  
\}
```

1. **Engine Manual Retrieval**:

```
async function searchEngineManual(manufacturer, model, year) \{  
  const sources = \[  
    'manualslib.com',  
    'boats.net/manuals',  
    manufacturer.toLowerCase() + '.com/manuals'  
  \];  
  
  for (const source of sources) \{  
    try \{  
      const manual = await searchManualOnSite(source, manufacturer, model, year);  
      if (manual) return manual;  
    \} catch (error) \{  
      console.log(\`Failed to retrieve from $\{source\}, trying next...\`);  
    \}  
  \}  
  
  return null;  
\}
```

1. **Regulations Retrieval**:

```
async function fetchRegulations(country, state) \{  
  const sources = \{  
    'US': 'https://www.uscgboating.org/regulations/',  
    'Canada': 'https://tc.canada.ca/en/marine-transportation/marine-safety/boating-safety',  
    'UK': 'https://www.rya.org.uk/knowledge/regulations'  
  \};  
  
  const baseUrl = sources\[country\];  
  if (!baseUrl) return 'No regulations available for this region';  
  
  // Fetch and parse regulations page  
  const response = await fetch(baseUrl);  
  const html = await response.text();  
  
  // Extract relevant sections  
  const regulations = parseRegulationsHTML(html, state);  
  
  return regulations;  
\}
```

1. **BoatUS Best Practices**:

```
async function fetchBoatUSPractices() \{  
  const topics = \[  
    'pre-departure-checklist',  
    'float-plan',  
    'fuel-management',  
    'anchoring',  
    'storm-preparation'  
  \];  
  
  let practices = '\#\# Best Practices from BoatUS.org\\n\\n';  
  
  for (const topic of topics) \{  
    const url = \`https://www.boatus.org/study-guide/$\{topic\}\`;  
    const response = await fetch(url);  
    const html = await response.text();  
    const content = extractMainContent(html);  
  
    practices += \`\#\#\# $\{topic.replace(/-/g, ' ').toUpperCase()\}\\n$\{content\}\\n\\n\`;  
  \}  
  
  return practices;  
\}
```

**PDF Processing**:

```
const pdfParse = require('pdf-parse');  
  
async function extractPDFText(pdfBuffer) \{  
  const data = await pdfParse(pdfBuffer);  
  
  let text = data.text  
    .replace(/\\s+/g, ' ')           // Collapse whitespace  
    .replace(/Page \\d+/gi, '')      // Remove page numbers  
    .replace(/\\f/g, '\\n\\n')         // Form feed to paragraph break  
    .trim();  
  
  // Limit size (50KB per document)  
  if (text.length \> 50000) \{  
    text = text.substring(0, 50000) + '\\n\\n\[Document truncated for space...\]';  
  \}  
  
  return text;  
\}
```

**Progress UI During Retrieval**:

```
\<div class="document-retrieval-progress"\>  
  \<h3\>Building Your AI Knowledge Base\</h3\>  
  
  \<div class="progress-item"\>  
    \<span class="status"\>⏳\</span\> Searching for boat manual...  
    \<div class="progress-bar"\>\<div class="progress" style="width: 20%"\>\</div\>\</div\>  
  \</div\>  
  
  \<div class="progress-item"\>  
    \<span class="status"\>⏳\</span\> Searching for engine manual...  
    \<div class="progress-bar"\>\<div class="progress" style="width: 0%"\>\</div\>\</div\>  
  \</div\>  
  
  \<div class="progress-item"\>  
    \<span class="status"\>⏳\</span\> Fetching marine best practices...  
    \<div class="progress-bar"\>\<div class="progress" style="width: 0%"\>\</div\>\</div\>  
  \</div\>  
  
  \<div class="progress-item"\>  
    \<span class="status"\>⏳\</span\> Fetching regional regulations...  
    \<div class="progress-bar"\>\<div class="progress" style="width: 0%"\>\</div\>\</div\>  
  \</div\>  
\</div\>
```

#### 4.5.6 Conversation History Database

**Schema** (`/opt/d3kos/data/conversation-history.db`):

```
CREATE TABLE conversations (  
  id INTEGER PRIMARY KEY AUTOINCREMENT,  
  timestamp DATETIME DEFAULT CURRENT\_TIMESTAMP,  
  question TEXT NOT NULL,  
  answer TEXT NOT NULL,  
  ai\_used TEXT NOT NULL CHECK(ai\_used IN ('online', 'onboard')),  
  context\_size INTEGER,  
  response\_time\_ms INTEGER,  
  user\_rating INTEGER CHECK(user\_rating BETWEEN 1 AND 5),  
  important BOOLEAN DEFAULT 0,  
  added\_to\_skills BOOLEAN DEFAULT 0  
);  
  
CREATE INDEX idx\_timestamp ON conversations(timestamp);  
CREATE INDEX idx\_important ON conversations(important);  
CREATE INDEX idx\_ai\_used ON conversations(ai\_used);
```

**Storage Operations**:

```
const sqlite3 = require('sqlite3');  
const db = new sqlite3.Database('/opt/d3kos/data/conversation-history.db');  
  
async function storeConversation(question, answer, aiUsed, responseTime) \{  
  const query = \`  
    INSERT INTO conversations  
    (question, answer, ai\_used, response\_time\_ms)  
    VALUES (?, ?, ?, ?)  
  \`;  
  
  await db.run(query, \[question, answer, aiUsed, responseTime\]);  
\}  
  
async function getRecentConversations(limit = 50) \{  
  const query = \`  
    SELECT \* FROM conversations  
    ORDER BY timestamp DESC  
    LIMIT ?  
  \`;  
  
  return await db.all(query, \[limit\]);  
\}  
  
async function getImportantConversations() \{  
  const query = \`  
    SELECT \* FROM conversations  
    WHERE important = 1  
    ORDER BY timestamp DESC  
  \`;  
  
  return await db.all(query);  
\}
```

**Automatic Learning**:

```
async function evaluateAndLearn(question, answer, aiUsed) \{  
  // Criteria for marking as important:  
  // 1. Technical questions about boat/engine  
  // 2. Procedural questions (how to, what is, procedure for)  
  // 3. Not already in skills.md  
  
  const importanceKeywords = \[  
    'how to', 'what is', 'normal', 'procedure', 'regulation',  
    'requirement', 'specification', 'temperature', 'pressure',  
    'maintenance', 'troubleshoot', 'problem'  
  \];  
  
  const isImportant = importanceKeywords.some(keyword =\>  
    question.toLowerCase().includes(keyword)  
  );  
  
  if (isImportant) \{  
    // Add to skills.md conversation history  
    const entry = \`  
\*\*Q\*\*: $\{question\}  
\*\*A\*\*: $\{answer\}  
\*\*Date\*\*: $\{new Date().toISOString()\}  
\*\*Source\*\*: $\{aiUsed === 'online' ? 'Online AI' : 'Onboard AI'\}  
  
\`;  
  
    appendToSkillsFile(entry);  
  
    // Mark in database  
    await db.run(  
      'UPDATE conversations SET important = 1, added\_to\_skills = 1 WHERE id = last\_insert\_rowid()'  
    );  
  \}  
\}
```

#### 4.5.7 Wake Word Routing

**Extended Wake Words**:

```
\# /opt/d3kos/config/sphinx/wake-words.dict  
HELM        HH EH L M  
ADVISOR     AE D V AY Z ER  
COUNSEL     K AW N S AH L
```

**Routing Logic**:

```
const wakeWordRouting = \{  
  'helm': \{  
    ai: 'auto',             // Use online if available, else onboard  
    response: 'Aye Aye Captain'  
  \},  
  'advisor': \{  
    ai: 'onboard',          // Force offline (rule-based patterns only)  
    response: 'Aye Aye Captain'  
  \},  
  'counsel': \{  
    ai: 'online',           // Force online AI (OpenRouter)  
    response: 'Aye Aye Captain',  
    fallback: 'Internet unavailable, using offline mode'  
  \}  
\};  
  
async function processWakeWord(wakeWord, spokenCommand) \{  
  const routing = wakeWordRouting\[wakeWord\];  
  
  if (routing.ai === 'auto') \{  
    const hasInternet = await checkInternetConnection();  
    // Try rule-based first (always fast)  
    const ruleResponse = ruleBasedResponse(spokenCommand);  
    if (ruleResponse) \{  
      return ruleResponse;  
    \}  
  
    // Complex query: check internet for OpenRouter  
    const hasInternet = await checkInternetConnection();  
    if (hasInternet) \{  
      return await queryOpenRouter(spokenCommand, context);  
    \} else \{  
      speak("That's a complex question. I can only answer simple queries offline. Please connect to internet.");  
      return null;  
    \}  
  \} else if (routing.ai === 'online') \{  
    const hasInternet = await checkInternetConnection();  
    if (hasInternet) \{  
      speak(routing.response);  
      return await queryOpenRouter(spokenCommand, context);  
    \} else \{  
      speak(routing.fallback);  
      return ruleBasedResponse(spokenCommand) || "Sorry, I need internet for complex questions.";  
    \}  
  \} else if (routing.ai === 'onboard') \{  
    speak(routing.response);  
    return ruleBasedResponse(spokenCommand) || "I can only answer simple questions offline: rpm, oil, temperature, fuel, battery, speed, heading, boost, hours, location, time, help, status.";  
  \}  
\}
```

#### 4.5.8 Rule-Based Response Patterns

**Pattern Matching System** (13 predefined patterns):

```
function ruleBasedResponse(question) \{  
  const q = question.toLowerCase();  
  const boatStatus = getBoatStatus();  // Cached 3s TTL  
  
  // Pattern: RPM  
  if (/\\b(rpm|engine speed|revolutions)\\b/.test(q)) \{  
    return \`Engine RPM is $\{boatStatus.rpm || 0\}\`;  
  \}  
  
  // Pattern: Oil Pressure  
  if (/\\b(oil|oil pressure)\\b/.test(q)) \{  
    return \`Oil pressure is $\{boatStatus.oil\_pressure || 'not available'\}\`;  
  \}  
  
  // Pattern: Temperature  
  if (/\\b(temp|temperature|coolant|engine temp)\\b/.test(q)) \{  
    return \`Coolant temperature is $\{boatStatus.coolant\_temp || 'not available'\}\`;  
  \}  
  
  // ... 10 more patterns (fuel, battery, speed, heading, boost, hours, location, time, help, status)  
  
  return \{ answer, responseTime \};  
\}
```

**Visual Progress Indicator**:

```
\<div class="ai-processing-indicator onboard"\>  
  \<div class="spinner"\>\</div\>  
  \<div class="status-text"\>  
    Onboard AI processing... (this may take up to 60 seconds)  
  \</div\>  
  \<div class="progress-bar"\>  
    \<div class="progress" style="width: 0%"\>\</div\>  
  \</div\>  
\</div\>  
  
\<style\>  
.ai-processing-indicator.onboard \{  
  background: \#1a1a1a;  
  border: 2px solid \#ff9800;  
  padding: 20px;  
  border-radius: 8px;  
\}  
  
.spinner \{  
  border: 4px solid \#333;  
  border-top: 4px solid \#ff9800;  
  border-radius: 50%;  
  width: 40px;  
  height: 40px;  
  animation: spin 1s linear infinite;  
\}  
  
@keyframes spin \{  
  0% \{ transform: rotate(0deg); \}  
  100% \{ transform: rotate(360deg); \}  
\}  
\</style\>
```


## 5. USER INTERFACE SPECIFICATIONS

### 5.1 Main Menu (index.html)

#### 5.1.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐  
│                      TOP 2/3 OF SCREEN                      │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  
│  │ Voice Enable │  │   Camera     │  │   OpenCPN    │      │  
│  │  (Toggle)    │  │  (Full View) │  │   (Launch)   │      │  
│  └──────────────┘  └──────────────┘  └──────────────┘      │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  
│  │ License Info │  │   Version    │  │   QR Code    │      │  
│  │   (View)     │  │  (Display)   │  │ (Generate)   │      │  
│  └──────────────┘  └──────────────┘  └──────────────┘      │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  
│  │  Onboarding  │  │OpenCPN Mgmt  │  │   Engine     │      │  
│  │   (Wizard)   │  │(Install/Del) │  │  Benchmark   │      │  
│  └──────────────┘  └──────────────┘  └──────────────┘      │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  
│  │ Boat Health  │  │    Boat      │  │  Raspberry   │      │  
│  │  (Monitor)   │  │ Performance  │  │ Pi Status    │      │  
│  └──────────────┘  └──────────────┘  └──────────────┘      │  
│                     (Scrollable Grid)                       │  
├─────────────────────────────────────────────────────────────┤  
│                    BOTTOM 1/3 OF SCREEN                     │  
│                   (Reserved for Keyboard)                   │  
│  ┌──────────────────────────────────────────────────────┐  │  
│  │              On-Screen Keyboard Area                 │  │  
│  └──────────────────────────────────────────────────────┘  │  
│  \[\< Back\]               \[Status Icons\]        \[Main Menu\]  │  
└─────────────────────────────────────────────────────────────┘
```

#### 5.1.2 Visual Design Specifications

**Colors**:

- Background: Pure black (\#000000)

- Primary text: White (\#FFFFFF)

- Accent: Green (\#00CC00) for active elements

- Warning: Amber (\#FFA500)

- Critical: Red (\#FF0000)

- Disabled: Dark gray (\#333333)

**Typography**:

- Font family: "Roboto", "Arial", sans-serif

- Base font size: 22px (minimum for AODA)

- Button text: 24px bold

- Headings: 32px bold

- Line height: 1.5 (for readability)

**Buttons**:

- Size: 120px W × 80px H (minimum)

- Padding: 16px

- Border radius: 8px

- Border: 2px solid \#00CC00 (active) or \#333333 (inactive)

- Touch target: Entire button + 8px margin

- Ripple effect on tap

**Icons**:

- Format: SVG (scalable, crisp)

- Size: 48×48px

- Color: White or green (match button state)

- Source: Material Design Icons or custom nautical icons

**Grid Layout**:

- Columns: 3

- Rows: 4 visible (scrollable for more)

- Gap: 20px horizontal, 16px vertical

- Responsive: Adjust for 1280×800 displays (2 columns if needed)

#### 5.1.3 AODA Compliance

**Accessibility Features**:

1. **Keyboard Navigation**:

   - Tab: Move between buttons

   - Enter: Activate button

   - Escape: Go back

   - Arrow keys: Navigate grid

2. **Screen Reader Support**:

   - All buttons have `aria-label` attributes

   - Headings use proper hierarchy (h1, h2, h3)

   - Landmarks: `\<nav\>`, `\<main\>`, `\<footer\>`

   - Live regions for dynamic updates: `aria-live="polite"`

3. **Color Contrast**:

   - White on black: 21:1 ratio (exceeds WCAG AAA 7:1 requirement)

   - Green on black: 12:1 ratio (exceeds requirement)

   - All text meets minimum 4.5:1 contrast

4. **Focus Indicators**:

   - Visible focus ring: 3px solid green

   - High contrast: Clearly visible on black background

5. **Text Alternatives**:

   - Icons have text labels

   - Status indicators have text descriptions

   - Error messages are text-based (not just color-coded)

#### 5.1.4 State Management

**localStorage Keys**:

```
\{  
  "d3kos-voice-enabled": boolean,  
  "d3kos-last-page": string,  
  "d3kos-license-tier": 0 | 2 | 3,  
  "d3kos-onboarding-complete": boolean,  
  "d3kos-theme": "dark" (future: allow light theme)  
\}
```

**WebSocket Connection**:

```
// Connect to backend services  
const ws = new WebSocket('ws://localhost:3000/d3kos');  
  
ws.onmessage = (event) =\> \{  
  const data = JSON.parse(event.data);  
  updateUI(data);  
\};  
  
// Send commands to backend  
function sendCommand(cmd, params) \{  
  ws.send(JSON.stringify(\{ command: cmd, params \}));  
\}
```

#### 5.1.5 Responsive Behavior

**Screen Size Adjustments**:

- 1920×1200 (primary): 3 columns, 4 rows

- 1280×800 (fallback): 2 columns, 6 rows

- Font scaling: Use CSS `clamp()` for fluid typography

**Keyboard Overlap Prevention**:

```
.main-content \{  
  max-height: calc(100vh - 400px); /\* Reserve 400px for keyboard \*/  
  overflow-y: auto;  
\}  
  
.keyboard-area \{  
  position: fixed;  
  bottom: 0;  
  height: 350px;  
  z-index: 1000;  
\}
```

### 5.2 Dashboard Gauges

#### 5.2.1 Gauge Types and Specifications

**Circular Gauges** (Analog Style):

- Diameter: 180px

- Arc: 270° (leaving 90° gap at bottom)

- Needle: Red pointer, 2px width

- Scale: White tick marks, 10 major ticks, 5 minor ticks

- Value: Large center text (32px)

- Label: Bottom text (18px)

**Linear Gauges** (Horizontal Bars):

- Width: 280px

- Height: 40px

- Fill: Gradient from green → yellow → red

- Current value: Vertical indicator line

- Text: Left-aligned label, right-aligned value

**Status Indicators**:

- Icon: 32×32px

- Text: Status label + detail (e.g., "WiFi: 192.168.1.100")

- Color: Green (connected), red (disconnected), yellow (connecting)

#### 5.2.2 Real-Time Update Pipeline

**Data Flow**:

```
Signal K → WebSocket → Node-RED → Dashboard UI  
   1Hz        \<10ms       \<50ms       \<100ms
```

**Update Frequency**:

- Engine metrics: 1 Hz (1000ms)

- System metrics: 0.2 Hz (5000ms)

- Tank levels: 0.1 Hz (10000ms)

- Network status: 0.033 Hz (30000ms)

**Optimization**:

- Use `requestAnimationFrame()` for smooth gauge animations

- Batch DOM updates to minimize reflows

- Use CSS transforms for needle rotation (GPU-accelerated)

#### 5.2.3 Threshold Configuration

**Engine Gauges**:

```
const thresholds = \{  
  rpm: \{ green: \[0, 4500\], yellow: \[4500, 5500\], red: \[5500, 6000\] \},  
  oilPressure: \{ green: \[20, 100\], yellow: \[10, 20\], red: \[0, 10\] \},  
  coolantTemp: \{ green: \[100, 200\], yellow: \[200, 220\], red: \[220, 250\] \},  
  voltage: \{ green: \[12.5, 14.5\], yellow: \[11.5, 12.5\], red: \[10, 11.5\] \}  
\};
```

**Color Application**:

- Green zone: Normal operation, no alerts

- Yellow zone: Caution, log event, no voice alert

- Red zone: Warning, log event, visual alert, voice alert if critical

#### 5.2.4 Historical Graphs

**Chart.js Configuration**:

- Type: Line chart with time-series x-axis

- Time range: Selectable (1h, 6h, 24h, 7d, 30d)

- Data points: Max 1000 points (downsample older data)

- Interaction: Tap gauge to expand, pinch-to-zoom

- Export: Button to download as CSV

**Data Storage**:

- Location: `/opt/d3kos/data/historical/`

- Format: SQLite database for efficient queries

- Retention: 90 days (auto-purge older data)

- Backup: Daily export to JSON (optional cloud sync in Tier 3)

### 5.3 Onboarding Wizard

#### 5.3.1 Wizard Flow

**Complete Onboarding Process**:

```
Welcome → Operator Setup → Boat Identity → Chartplotter Detection →  
Engine Q1-15 → CX5106 Config → QR Code → Complete
```

**Step Breakdown**:

- Step 1: Welcome & Operator Setup

- Step 2: Boat Identity

- Step 3: Multi-Boat Configuration (if applicable)

- **Step 4: Chartplotter Detection** (NEW)

- Steps 5-19: Engine Configuration (15 questions)

- Step 20: CX5106 DIP Switch Configuration

- Step 21: QR Code Generation

- Step 22: Completion Summary

**Progress Indicator**:

- Visual: Progress bar (Step X of 22)

- Text: "Step 4 of 22: Chartplotter Detection"

- Navigation: Back, Next, Save & Exit

#### 5.3.2 Question Specifications

**Question 1: Engine Manufacturer**

- Input type: Autocomplete dropdown

- Data source: `/opt/d3kos/data/engine-manufacturers.json`

- AI assist: Suggest based on partial input

- Validation: Required field

- Fallback: Manual text entry if not in list

**Question 2: Engine Model**

- Input type: Autocomplete dropdown (filtered by manufacturer)

- AI assist: Auto-populate based on Q1

- Validation: Required field

- Fallback: Manual text entry

**Question 3: Engine Year**

- Input type: Number input (1950-2026)

- AI assist: Suggest likely year based on model

- Validation: Year must be between 1950 and current year

- Default: 2010

**Question 4: Number of Cylinders**

- Input type: Dropdown (3, 4, 6, 8)

- AI assist: Auto-populate from model if known

- Validation: Required field

- Default: 4

**Question 5: Engine Displacement**

- Input type: Dual number input (Liters OR Cubic Inches)

- Conversion: Real-time (1 L = 61.024 CID)

- AI assist: Calculate from cylinders + stroke if Q7 answered first

- Validation: 0.5 L to 15 L (marine range)

- Default: 5.0 L

**Question 6: Compression Ratio**

- Input type: Number input (decimal, e.g., 9.5:1)

- AI assist: Suggest typical range (gasoline: 8-11, diesel: 15-22)

- Validation: 7:1 to 22:1

- Default: 9.5:1 (gasoline)

**Question 7: Stroke Length**

- Input type: Dual number input (mm OR inches)

- Conversion: Real-time (1 inch = 25.4 mm)

- AI assist: Calculate from displacement + cylinders

- Validation: 50mm to 200mm

- Default: 90mm

**Question 8: Induction Type**

- Input type: Radio buttons

- Options: Naturally Aspirated, Turbocharged, Supercharged

- AI assist: Infer from model name (e.g., "Turbo" → Turbocharged)

- Validation: Required field

- Default: Naturally Aspirated

**Question 9: Rated Horsepower**

- Input type: Number input with unit (HP or kW)

- Conversion: Real-time (1 HP = 0.746 kW)

- AI assist: Suggest from manufacturer specs

- Validation: 10 HP to 1000 HP

- Default: 200 HP

**Question 10: Idle RPM Specification**

- Input type: Number input

- AI assist: Suggest 700 RPM (gasoline) or 650 RPM (diesel)

- Validation: 400 RPM to 1200 RPM

- Default: 700 RPM

**Question 11: WOT RPM Range**

- Input type: Two number inputs (Min, Max)

- AI assist: Calculate from manufacturer specs

- Validation: Max \> Min, reasonable range

- Default: 4800-5200 RPM

**Question 12: Maximum Coolant Temperature**

- Input type: Number input with unit (°F or °C)

- Conversion: Real-time (°F = °C × 9/5 + 32)

- AI assist: Suggest 180°F (82°C) freshwater, 160°F (71°C) raw water

- Validation: 120°F to 220°F

- Default: 180°F

**Question 13: Minimum Oil Pressure**

- Input type: Two number inputs (Idle PSI, Cruise PSI)

- AI assist: Suggest 10 PSI @ idle, 40 PSI @ cruise

- Validation: Cruise \> Idle, reasonable range

- Default: 10 PSI idle, 40 PSI cruise

#### 5.3.2a Step 4: Chartplotter Detection (NEW)

**Purpose**: Determine if a third-party chartplotter is installed on the NMEA2000 network to decide whether to install OpenCPN.

**UI Layout**:

```
┌──────────────────────────────────────────────────────┐  
│  Step 4 of 22: Navigation Display                    │  
├──────────────────────────────────────────────────────┤  
│                                                      │  
│  How will you view charts and navigation?           │  
│                                                      │  
│  ○ I have a chartplotter installed                  │  
│    (Garmin, Simrad, Raymarine, Lowrance, etc.)     │  
│    → d3kOS will NOT install OpenCPN                 │  
│                                                      │  
│  ○ I don't have a chartplotter                      │  
│    → d3kOS will install OpenCPN for navigation      │  
│                                                      │  
│  ○ I'm not sure - Auto-detect                       │  
│    → d3kOS will scan the NMEA2000 network           │  
│                                                      │  
│  ℹ️ Note: Your chartplotter will automatically       │  
│     display engine data from the CX5106 gateway.    │  
│     No special configuration needed.                │  
│                                                      │  
│  \[\< Back\]          \[Detect Now\]          \[Next \>\]   │  
└──────────────────────────────────────────────────────┘
```

**Auto-Detection Logic** (IMPLEMENTED 2026-02-11):

**Prerequisites - Nginx Proxy Configuration**: Signal K Server runs on port 3000 (IPv6 only), so nginx proxy is required for browser WebSocket connections:

```
\# /etc/nginx/sites-enabled/default  
\# Signal K WebSocket Proxy  
location /signalk/ \{  
    proxy\_pass http://localhost:3000/signalk/;  
    proxy\_http\_version 1.1;  
    proxy\_set\_header Upgrade $http\_upgrade;  
    proxy\_set\_header Connection "upgrade";  
    proxy\_set\_header Host $host;  
    proxy\_set\_header X-Real-IP $remote\_addr;  
    proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for;  
    proxy\_set\_header X-Forwarded-Proto $scheme;  
    proxy\_read\_timeout 86400;  
\}
```

**JavaScript Implementation** (`/var/www/html/onboarding.html`):

```
function detectChartplotter() \{  
  // Connect to Signal K via nginx proxy on port 80  
  const wsUrl = 'ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=none';  
  const navigationPGNs = \[  
    129025,  // Position, Rapid Update  
    129026,  // COG & SOG, Rapid Update  
    129029   // GNSS Position Data  
  \];  
  const detectedNavPGNs = new Set();  
  let detectionComplete = false;  
  
  console.log("Connecting to Signal K:", wsUrl);  
  
  const ws = new WebSocket(wsUrl);  
  const wsTimeout = setTimeout(() =\> \{  
    ws.close();  
    displayResult(false, "Signal K unavailable");  
  \}, 10000); // 10-second connection timeout  
  
  ws.onopen = function() \{  
    clearTimeout(wsTimeout);  
    console.log('✓ Connected to Signal K successfully');  
  
    // Subscribe to all updates  
    ws.send(JSON.stringify(\{  
      context: 'vessels.self',  
      subscribe: \[\{ path: '\*', period: 1000 \}\]  
    \}));  
  
    // Start 5-second detection timer  
    startDetectionTimer(ws, navigationPGNs, detectedNavPGNs);  
  \};  
  
  ws.onmessage = function(event) \{  
    const data = JSON.parse(event.data);  
  
    // Check for PGNs in Signal K updates  
    if (data.updates) \{  
      data.updates.forEach(update =\> \{  
        if (update.$source && update.$source.pgn) \{  
          const pgn = update.$source.pgn;  
  
          // Display all detected PGNs in real-time  
          displayPGN(pgn);  
  
          // Check if it's a navigation PGN  
          if (navigationPGNs.includes(pgn)) \{  
            detectedNavPGNs.add(pgn);  
            console.log('✓ Navigation PGN detected:', pgn);  
          \}  
        \}  
      \});  
    \}  
  \};  
  
  ws.onerror = function(error) \{  
    console.error('WebSocket error:', error);  
  \};  
  
  ws.onclose = function() \{  
    console.log('WebSocket closed');  
  \};  
\}  
  
function startDetectionTimer(ws, navigationPGNs, detectedNavPGNs) \{  
  const detectionDuration = 5000; // 5 seconds  
  const startTime = Date.now();  
  
  const timer = setInterval(() =\> \{  
    const elapsed = Date.now() - startTime;  
    const progress = (elapsed / detectionDuration) \* 100;  
  
    // Update progress bar  
    updateProgressBar(progress);  
  
    if (elapsed \>= detectionDuration) \{  
      clearInterval(timer);  
      ws.close();  
  
      // Determine result  
      const hasChartplotter = detectedNavPGNs.size \> 0;  
      displayResult(hasChartplotter, detectedNavPGNs);  
  
      // Auto-select appropriate radio option  
      if (hasChartplotter) \{  
        document.getElementById('has-chartplotter').checked = true;  
      \} else \{  
        document.getElementById('no-chartplotter').checked = true;  
      \}  
    \}  
  \}, 100); // Update every 100ms  
\}
```

**Detection Display**:

```
┌──────────────────────────────────────────────────────┐  
│  Scanning NMEA2000 Network...                        │  
├──────────────────────────────────────────────────────┤  
│                                                      │  
│  🔍 Listening for navigation PGNs                    │  
│  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ 50% (2.5s / 5.0s)            │  
│                                                      │  
│  Detected PGNs:                                      │  
│  • 127488 - Engine Parameters (CX5106)              │  
│  • 127505 - Fluid Level (CX5106)                    │  
│  • 129026 - COG & SOG (Chartplotter) ✓              │  
│  • 129029 - GNSS Position (Chartplotter) ✓          │  
│                                                      │  
│  Result: Chartplotter detected!                      │  
│                                                      │  
│  \[Continue\]                                          │  
└──────────────────────────────────────────────────────┘
```

**Data Storage** (`/opt/d3kos/config/onboarding.json`):

```
\{  
  "chartplotter": \{  
    "present": true,  
    "detected\_pgns": \[129026, 129029\],  
    "detection\_method": "auto",  
    "install\_opencpn": false,  
    "timestamp": "2026-02-11T10:30:00Z"  
  \}  
\}
```

**Important Notes**:

- **Standard NMEA2000 PGNs**: CX5106 outputs standard PGNs (127488, 127489, 127505, 127508) that ALL chartplotters can read automatically

- **No Vendor-Specific Handling**: Chartplotters from Garmin, Simrad, Raymarine, Lowrance, Furuno, and Humminbird all support standard PGNs

- **No PGN Translation Required**: d3kOS does NOT need to translate or convert PGNs for chartplotter compatibility

- **Bi-Directional Not Required**: d3kOS receives data from NMEA2000; chartplotter also receives the same data

- **Engine Gauge Display**: Third-party chartplotters will display CX5106 engine data on their built-in engine gauge pages without any d3kOS configuration

**Why This Step Matters**:

- Avoids installing OpenCPN when user already has a chartplotter

- Saves disk space (~500MB)

- Prevents duplicate navigation displays

- Informs user that chartplotter will automatically see engine data

**Fullscreen Toggle on Wizard Completion** (IMPLEMENTED 2026-02-11):

When the Initial Setup wizard completes, it automatically restores kiosk mode (fullscreen) before redirecting to the main menu. This is necessary because the wizard exits fullscreen to allow on-screen keyboard access.

**Implementation** (`/var/www/html/onboarding.html`):

```
function goToMainMenu() \{  
  // Increment wizard run counter  
  let wizardRuns = parseInt(localStorage.getItem('d3kos-wizard-runs') || '0');  
  wizardRuns++;  
  localStorage.setItem('d3kos-wizard-runs', wizardRuns.toString());  
  
  // Mark onboarding as complete  
  localStorage.setItem('d3kos-onboarding-complete', 'true');  
  
  // Alert user  
  alert('Onboarding complete! You will be redirected to the main menu.');  
  
  // Toggle fullscreen (return to kiosk mode)  
  fetch('http://localhost:1880/toggle-fullscreen', \{  
    method: 'POST',  
    headers: \{ 'Content-Type': 'application/json' \}  
  \}).then(() =\> \{  
    console.log('✓ Toggled to fullscreen/kiosk mode');  
  \}).catch(err =\> \{  
    console.warn('Could not toggle fullscreen:', err);  
  \});  
  
  // Wait for fullscreen toggle, then redirect  
  setTimeout(() =\> \{  
    window.location.href = '/';  
  \}, 500);  
\}
```

**Node-RED Endpoint**: `POST http://localhost:1880/toggle-fullscreen`

- Executes `/usr/local/bin/toggle-fullscreen.sh` script

- Script uses `wtype -k F11` (Wayland keyboard input tool)

- F11 toggles fullscreen mode in Chromium

#### 5.3.3 CX5106 DIP Switch Configuration

**Output Format**:

```
┌─────────────────────────────────────────┐  
│    CX5106 DIP Switch Configuration      │  
├─────────────────────────────────────────┤  
│                                         │  
│   \[Visual DIP Switch Diagram - 8 switches\]  
│                                         │  
│   Switch 1: ON   - Engine Instance 0    │  
│   Switch 2: OFF  - Not Used             │  
│   Switch 3: ON   - RPM Source: Direct   │  
│   Switch 4: OFF  - ...                  │  
│   ...                                   │  
│                                         │  
│   WHY THESE SETTINGS:                   │  
│   - Your engine (Mercury 5.0L V8)      │  
│     requires direct RPM measurement     │  
│   - Cylinders: 8 → Use 4-pole sensor    │  
│   - ...                                 │  
│                                         │  
│   \[Print\] \[Save PDF\] \[Next\]             │  
└─────────────────────────────────────────┘
```

**Calculation Logic**:

```
function calculateDIPSwitches(engineData) \{  
  // Based on CLAUDE.md DIP switch rules  
  const switches = \{  
    1: engineData.instance === 0 ? "ON" : "OFF",  
    2: engineData.cylinders === 4 ? "ON" : "OFF",  
    // ... (implement full logic from CLAUDE.md)  
  \};  
    
  return \{  
    switches,  
    explanation: generateExplanation(engineData, switches)  
  \};  
\}
```

#### 5.3.4 QR Code Generation

**Installation ID Generation**:

```
const crypto = require('crypto');  
const os = require('os');  
  
function generateInstallationID() \{  
  const mac = os.networkInterfaces().eth0\[0\].mac;  
  const timestamp = new Date().toISOString();  
  const hash = crypto.createHash('sha256')  
    .update(mac + timestamp)  
    .digest('hex');  
    
  return hash.substring(0, 16); // First 16 chars  
\}
```

**QR Code Content**:

```
d3kos://pair?id=abc123def456&version=1.0.3&tier=2
```

**Display**:

- Size: 300×300px

- Format: SVG (crisp on all displays)

- Label: "Scan to pair mobile app"

- Regenerate button: "Generate New Code"

#### 5.3.5 Reset Counter

**Counter File** (`/opt/d3kos/state/onboarding-reset-count.json`):

```
\{  
  "reset\_count": 7,  
  "max\_resets": 10,  
  "last\_reset": "2026-02-06T10:30:00Z",  
  "warnings\_shown": \[8, 9\],  
  "tier": 0  
\}
```

**UI Display**:

- Location: Footer of every wizard page

- Text: "Resets used: 7/10 (Tier 0)"

- Color: Green (\< 8), Yellow (8-9), Red (10)

**Warning Messages**:

- Reset 8: "Warning: Only 2 resets remaining. Consider upgrading to Tier 2 for unlimited resets."

- Reset 9: "Warning: This is your last reset. Next reset will require a fresh image download."

- Reset 10: "Maximum resets reached. Please download a fresh d3kOS image or upgrade to Tier 2."

**Tier 2 Bypass**:

```
if (tier \>= 2) \{  
  // Unlimited resets for Tier 2+  
  resetCount = 0; // Don't increment  
\}
```

### 5.4 Camera Interface

#### 5.4.1 Live View

**RTSP Stream Display**:

- Player: VLC (libvlc) embedded in HTML

- URL: `rtsp://admin:password@192.168.1.100:554/h264Preview\_01\_main`

- Resolution: 1920×1080 @ 30fps

- Latency: \< 500ms

- Hardware decoding: GPU-accelerated (H.264)

**UI Controls**:

```
┌─────────────────────────────────────────┐  
│         \[Live Camera View\]              │  
│                                         │  
│     (Full-screen RTSP stream)           │  
│                                         │  
├─────────────────────────────────────────┤  
│ \[● REC\] \[■ STOP\] \[⚫ SNAPSHOT\] \[PLAYBACK\]│  
│ Storage: 42% used (58% free)           │  
│ Recording: 00:15:32                     │  
└─────────────────────────────────────────┘
```

#### 5.4.2 Recording Management

**Storage Path**: `/opt/d3kos/data/camera/`

**File Naming**: `YYYYMMDD\_HHMMSS\_camera.mp4`

**Segmentation**: 10-minute chunks for easier playback

**Storage Safeguards**:

```
function checkStorageBeforeRecording() \{  
  const diskFree = getDiskFreePercent();  
    
  if (diskFree \< 18) \{  
    alert("Cannot start recording. Disk space critically low (\<18%).");  
    return false;  
  \}  
    
  if (diskFree \< 20) \{  
    alert("Warning: Disk space low (\<20%). Recording will auto-stop at 18%.");  
  \}  
    
  return true;  
\}  
  
function monitorStorageDuringRecording() \{  
  setInterval(() =\> \{  
    const diskFree = getDiskFreePercent();  
      
    if (diskFree \< 18) \{  
      stopRecording();  
      alert("Recording stopped. Disk space critical (\<18%).");  
      deleteOldestRecordings(5); // Delete 5 oldest files  
    \}  
  \}, 10000); // Check every 10 seconds  
\}
```

**FIFO Deletion**:

```
function deleteOldestRecordings(count) \{  
  const files = fs.readdirSync('/opt/d3kos/data/camera/')  
    .filter(f =\> f.endsWith('.mp4'))  
    .map(f =\> (\{  
      name: f,  
      time: fs.statSync(\`/opt/d3kos/data/camera/$\{f\}\`).mtime.getTime()  
    \}))  
    .sort((a, b) =\> a.time - b.time);  
    
  for (let i = 0; i \< count && i \< files.length; i++) \{  
    fs.unlinkSync(\`/opt/d3kos/data/camera/$\{files\[i\].name\}\`);  
    console.log(\`Deleted: $\{files\[i\].name\}\`);  
  \}  
\}
```

#### 5.4.3 Playback Interface

**Timeline Scrubber**:

- Width: Full screen width

- Thumbnails: Every 10 seconds

- Click to jump: Instant seek

- Speed controls: 1x, 2x, 4x, 8x

**Export Clip**:

- Select start/end time

- Generate new MP4 segment

- Save to exports folder


### 5.5 Weather Radar (NEW - 2026-02-13)

#### 5.5.1 Overview

The Weather Radar feature provides GPS-based real-time marine weather information with animated radar display and comprehensive conditions panel. Weather data is automatically logged to boatlog every 30 minutes.

**Access**: Main Menu → Weather button (cloud + lightning icon)

**URL**: `/weather.html`

**Documentation**: `/home/boatiq/Helm-OS/doc/WEATHER\_2026-02-13.md`

#### 5.5.2 Data Sources & APIs

**GPS Position**:

- Source: Signal K WebSocket (`navigation.position`)

- Update: Real-time (5-second subscription)

**Marine Weather**:

- API: Open-Meteo Marine API

- Endpoint: `https://marine-api.open-meteo.com/v1/marine`

- Data: Wave height, direction, period, wind waves

- Update: Every 5 minutes

**Atmospheric Weather**:

- API: Open-Meteo Weather API

- Endpoint: `https://api.open-meteo.com/v1/forecast`

- Data: Wind, temp, humidity, pressure, precipitation, visibility

- Update: Every 5 minutes

**Animated Radar**:

- Service: Windy.com Embedded Map

- Overlay: Wind / Clouds / Radar (user-selectable toggle)

- Model: ECMWF

- Units: Knots (wind), Celsius (temp)

- **Large Touch Controls** (80px × 80px buttons):

  - Zoom In (+)

  - Zoom Out (−)

  - Recenter on Position (⊙)

  - Wind/Clouds/Radar overlay toggle

#### 5.5.3 Essential Marine Data

**Wind**: Speed (kt), Direction (°), Gusts (kt) **Seas**: Wave height (m), Direction (°), Period (s), State description **Atmospheric**: Weather description, Visibility (km), Temp (°C), Humidity (%), Pressure (hPa), Precipitation (mm/hr)

#### 5.5.4 Weather Alerts

- High Wind: Orange (\>25kt), Red (\>35kt)

- High Seas: Orange (\>2.0m), Red (\>3.5m)

- Heavy Precipitation: Orange (\>5mm/hr), Red (\>10mm/hr)

#### 5.5.5 Auto-Logging

- Interval: Every 30 minutes

- Destination: Boatlog (via POST /api/boatlog/entry)

- Status: Bottom-right corner display

- Feedback: "Saved ✓" (green) or "Failed ✗" (red)

#### 5.5.6 User Interface

**Layout**: Split-screen (Radar 2/3, Conditions 1/3)

**Large Touch-Friendly Map Controls**:

- **Size**: 80px × 80px (4x larger than standard)

- **Position**: Right side of map, vertically centered

- **Buttons**:

  - Zoom In (+) - Increases map zoom level (3-15)

  - Zoom Out (−) - Decreases map zoom level

  - Recenter (⊙) - Recenters map on current GPS position

- **Overlay Toggle** (top-left):

  - Wind (default) - Wind speed and direction

  - Clouds - Cloud coverage

  - Radar - Precipitation radar

- **Touch Support**: All buttons support both click and touchend events

- **Visual Feedback**: Green border, dark background, scale animation on press

#### 5.5.7 Implementation

**Files**:

- `/var/www/html/weather.html` (30KB standalone HTML with large controls)

- `/var/www/html/index.html` (Weather button added)

**Known Limitations**:

1. Requires internet connection

2. Missing: Tides, water temp, lightning

3. Boatlog API not yet implemented (logs to console)

4. Windy iframe play/pause button cannot be enlarged (CORS restriction)

See `/home/boatiq/Helm-OS/doc/WEATHER\_2026-02-13.md` for complete technical documentation.


### 5.6 Marine Vision System (PLANNED - 2026-02-14)

#### 5.6.1 Overview

The Marine Vision System provides AI-powered computer vision for two primary use cases: automatic fish capture with species identification and forward-watch marine hazard detection. The system uses an IP67-rated night-vision camera mounted on a 360° motorized searchlight and automatically switches modes based on camera orientation.

**Access**: Main Menu → Marine Vision button

**URL**: `/marine-vision.html`

**Documentation**: `/home/boatiq/Helm-OS/doc/MARINE\_VISION.md`

#### 5.6.2 Operating Modes

**Mode Selection**:

- Automatic switching based on camera orientation

- Manual mode override via web interface

- Three states: Fish Capture, Forward Watch, Idle

**Fish Capture Mode** (camera oriented toward user):

- Person detection + fish-like object detection

- Auto-capture high-resolution still image

- Fish species identification (pretrained + fine-tuned model)

- Fishing regulations check (size/bag limits by location/date)

- Notification sent to user (Telegram/Signal/email)

- Event logging with timestamp, species, location

**Forward Watch Mode** (camera oriented toward bow):

- Real-time marine object detection (people, boats, kayaks, buoys, logs, debris, docks)

- Distance estimation using AI-based monocular depth

- Visual and audible alerts

- Object tracking with position/distance

- Detection logging with timestamps

#### 5.6.3 Camera Specifications

**Hardware**:

- IP67-rated marine camera with RTSP/ONVIF streaming

- Integrated night vision / IR mode

- Mounted on 360° motorized searchlight

- 1080p or higher resolution

- Network: 10.42.0.0/24 subnet (auto-discovery)

**Streaming**:

- Protocol: RTSP (rtsp://d3kos:d3kos2026@CAMERA\_IP:554/h264Preview\_01\_main)

- Recording: VLC integration for on-demand recording

- Storage: 128GB USB drive at `/media/d3kos/6233-3338/camera-recordings/`

- Format: H.264 MP4 (~1GB/hour at 1080p30fps)

#### 5.6.4 AI Models & Detection

**Fish Capture Mode**:

- YOLOv8 (person + fish detection)

- ResNet50 or EfficientNet (species classification)

- Pretrained fish classification model (FishNet/FishID)

- Optional fine-tuning with user-provided images (20-50 per species)

**Forward Watch Mode**:

- YOLOv8-Marine (person/boat/kayak/buoy/debris detection)

- MiDaS v3.0 or ZoeDepth (monocular depth estimation)

- Real-time processing: 10+ FPS object detection, 5+ FPS depth

**Model Storage**: ~250MB total

- YOLOv8n: ~6MB

- ResNet50: ~100MB

- YOLOv8-Marine: ~25MB

- MiDaS: ~100MB

#### 5.6.5 Fishing Regulations Integration

**Data Sources**:

- Ontario MNR regulations database (parsed from PDF)

- FishBase API ([https://fishbase.ropensci.org/](https://fishbase.ropensci.org/)) - species info

- GBIF API ([https://api.gbif.org/](https://api.gbif.org/)) - taxonomy, occurrence

- iNaturalist API ([https://api.inaturalist.org/](https://api.inaturalist.org/)) - photo-based ID

**Regulation Features**:

- Species → minimum/maximum size limits

- Species → daily bag limits

- Species → open/closed season dates

- Zone-specific rules

- Location-aware (GPS coordinates)

- Date/time aware

**Local Database**: `/opt/d3kos/data/fishing-regulations.db` (SQLite)

#### 5.6.6 Camera Orientation Detection

**Primary Method** (preferred):

- Read orientation data from searchlight control interface

- Protocols: RS-485, NMEA-0183, CAN, PWM feedback

- Real-time angle (0-360°)

**Secondary Method** (fallback):

- Physical sensor (Hall effect + magnet)

- Detects known reference positions

- Simple, reliable, low-cost

**Tertiary Method** (emergency fallback):

- Computer vision cues (deck geometry, bow rail)

- Less reliable in low light

**Mode Thresholds**:

- Fish Capture: 135° - 225° (camera toward stern/user)

- Forward Watch: 315° - 45° (camera toward bow)

- Idle: All other angles

#### 5.6.7 Distance Estimation

**Calibration Parameters**:

- Camera height above waterline (meters)

- Focal length and field of view

- Optional reference objects (buoys, markers)

**Output**:

- Distance in meters

- Confidence score (0.0 - 1.0)

- Logged with each detection event

**Accuracy**: ±20% at 10-50m, ±40% beyond 50m (typical for monocular depth)

#### 5.6.8 Notification System

**Supported Channels**:

- Telegram bot (recommended - easiest API)

- Signal API

- Email (SMTP)

- d3kOS notification bus (internal)

**Fish Capture Notifications Include**:

- Captured image (high-res)

- Species name (common + scientific)

- Confidence score

- Fishing regulations (size/bag limits)

- Timestamp

- GPS location (if available)

**Forward Watch Notifications Include**:

- Detected object type

- Estimated distance

- Screenshot with bounding box

- Timestamp

- Threat level (info/warning/critical)

#### 5.6.9 Performance Requirements

- Minimum 10 FPS object detection (Forward Watch)

- Minimum 5 FPS depth estimation

- Fish Capture trigger within 1 second of detection

- Notifications sent within 5 seconds of capture

- Offline operation (except notifications)

#### 5.6.10 Service Architecture

**Multiple Services Approach**:

1. **d3kos-camera-stream** (Port 8084)

   - RTSP connection management

   - VLC recording control

   - Frame extraction

   - Camera health monitoring

2. **d3kos-vision-core** (Port 8085)

   - Camera orientation tracking

   - Mode selection and switching

   - System health monitoring

3. **d3kos-fish-detector** (Port 8086)

   - Person + fish detection

   - Species classification

   - Regulations lookup

   - Capture event logging

4. **d3kos-forward-watch** (Port 8087) **\[SEE FORWARD WATCH SUB-PROJECT\]**

   - Marine object detection (people, boats, kayaks, buoys, logs, debris, docks)

   - Distance estimation (monocular depth)

   - GPS coordinate mapping for chartplotter integration

   - Alert generation

   - Detection logging

   - **Note:** Forward Watch is implemented as Signal K plugin (`signalk-forward-watch`)

   - **Documentation:** `/home/boatiq/Helm-OS/doc/FORWARD\_WATCH\_SPECIFICATION.md`

   - **See Section 5.6.12** for chartplotter integration details

5. **d3kos-marine-vision-api** (Port 8089)

   - Unified REST API

   - Web UI interface

   - Configuration management

   - Historical data access

#### 5.6.11 Implementation Phases

**Phase 1: Camera Streaming** (1-2 days)

- Camera discovery (10.42.0.0/24 network scan)

- RTSP connection establishment

- VLC recording integration

- Web preview interface

**Phase 2: Fish Capture Mode** (3-5 days)

- Person + fish detection (YOLOv8)

- Auto-capture functionality

- Basic species classification

- Telegram/Signal notifications

**Phase 3: Regulations Integration** (2-3 days)

- Parse Ontario MNR regulations PDF

- Create species database

- Size/bag limit checking

- Location-aware rules

**Phase 4: Forward Watch Mode** (4-6 days)

- Marine object detection

- Distance estimation

- Alert system

- Detection logging

**Phase 5: Mode Switching** (1-2 days)

- Orientation detection implementation

- Automatic mode switching

- Manual override controls

#### 5.6.12 Chartplotter Integration (Forward Watch Sub-Project)

**Implementation:** Signal K Plugin (`signalk-forward-watch`)

**Purpose:** Display Forward Watch detections as targets on NMEA2000 chartplotters

**Architecture:**

```
Camera Detection → GPS Calculation → Signal K Delta → NMEA2000 PGN → Chartplotter Display
```

**Key Features:**

- **Object GPS Mapping:** Converts camera detections to latitude/longitude coordinates

- **Distance Estimation:** MiDaS monocular depth AI (±20% accuracy @ 50m)

- **Bearing Calculation:** Uses boat heading + camera field of view

- **Signal K Output:** Delta messages in standard vessels format

- **NMEA2000 Conversion:** PGN 129038 (AIS-like targets) or PGN 129285 (waypoints)

- **Universal Compatibility:** Works with Garmin, Raymarine, Simrad, Lowrance, Furuno, OpenCPN

**Training Requirements:**

- **YOLOv8-Marine:** Custom training on marine datasets (SeaShips, floating debris)

- **MiDaS Depth:** Pre-trained, no custom training needed

- **Training Time:** 12-16 hours on RTX 3060 Ti GPU

- **Datasets Available:** SeaShips (31,455 images), Marine Surveillance (Roboflow), Floating Debris

**Documentation:**

- **Technical Spec:** `/home/boatiq/Helm-OS/doc/FORWARD\_WATCH\_SPECIFICATION.md`

- **One-Pager:** `/home/boatiq/Helm-OS/doc/FORWARD\_WATCH\_ONEPAGER.md`

- **README:** `/home/boatiq/Helm-OS/signalk-forward-watch-README.md`

**Development Status:** Specification complete, ready for implementation

**Repository:** [https://github.com/d3kOS/signalk-forward-watch](https://github.com/d3kOS/signalk-forward-watch) (planned)

#### 5.6.13 Known Limitations

1. Requires internet for notifications (offline detection still works)

2. Species ID accuracy depends on photo quality and lighting

3. Distance estimation ±20-40% accuracy (monocular limitations)

4. Night vision reduces detection accuracy

5. Raspberry Pi 4B may achieve 5-10 FPS (consider Coral USB Accelerator for 5-10× boost)

6. Fishing regulations require manual database updates (annual)

#### 5.6.13 Safety & Reliability

- System provides situational awareness only (not autopilot)

- Does not control vessel movement

- Fails gracefully: defaults to Forward Watch if orientation unknown

- Continues processing if detection fails (logs error)

- Adjusts thresholds automatically for night vision

See `/home/boatiq/Helm-OS/doc/MARINE\_VISION.md` for complete technical implementation guide.


## 6. CORE FEATURES

### 6.1 Engine Health Monitoring

#### 6.1.1 Baseline Establishment

**Triggering**:

- Automatic: First engine start after onboarding

- Manual: "Engine Benchmark" button in main menu

- Voice: "Helm, start benchmarking"

**Data Collection** (30 minutes):

```
const baseline = \{  
  timestamp: "2026-02-06T10:00:00Z",  
  engine\_hours: 245,  
  samples: 1800, // 30 min × 60 sec × 1 Hz  
  metrics: \{  
    rpm\_idle: \{ mean: 720, stddev: 15, min: 690, max: 750 \},  
    rpm\_cruise: \{ mean: 3200, stddev: 50, min: 3100, max: 3300 \},  
    temp\_warmup\_curve: \[120, 140, 160, 175, 178, 180\],  
    temp\_steady\_state: 180,  
    oil\_pressure\_idle: 12,  
    oil\_pressure\_cruise: 45,  
    fuel\_rate\_cruise: 4.2, // GPH  
    voltage\_charging: 14.2  
  \}  
\};
```

**Storage**: `/opt/d3kos/config/benchmark-results.json`

#### 6.1.2 Anomaly Detection

**Statistical Process Control (SPC)**:

```
function detectAnomaly(current, baseline) \{  
  const deviation = Math.abs(current.value - baseline.mean);  
  const sigma = baseline.stddev;  
    
  if (deviation \> 3 \* sigma) \{  
    return \{ level: 'CRITICAL', message: \`$\{current.name\} is $\{deviation.toFixed(1)\} units from baseline (\>3σ)\` \};  
  \} else if (deviation \> 2 \* sigma) \{  
    return \{ level: 'WARNING', message: \`$\{current.name\} is $\{deviation.toFixed(1)\} units from baseline (\>2σ)\` \};  
  \} else if (deviation \> 1 \* sigma) \{  
    return \{ level: 'INFO', message: \`$\{current.name\} is slightly elevated\` \};  
  \}  
    
  return \{ level: 'NORMAL', message: null \};  
\}
```

**Example Anomalies**:

- RPM Instability: `stddev \> 2 × baseline\_stddev` → "Engine running rough"

- High Temperature: `temp \> baseline + 15°F` → "Coolant temperature high"

- Low Oil Pressure: `pressure \< baseline - 5 PSI` → "Oil pressure low"

- High Fuel Consumption: `rate \> baseline × 1.2` → "Fuel consumption increased 20%"

#### 6.1.3 Real-Time Monitoring

**Dashboard Integration**:

- Traffic light indicator: Green (Normal), Yellow (Warning), Red (Critical)

- Tap for detailed anomaly report

- Voice alert for CRITICAL anomalies only

**Voice Alert Example**:

```
"Helm alert: Engine temperature is 210 degrees Fahrenheit,   
30 degrees above normal. Please check coolant system."
```

**Alert Frequency**:

- INFO: Log only, no alert

- WARNING: Visual alert, log

- CRITICAL: Visual + voice alert every 5 minutes until acknowledged

#### 6.1.4 Health Reports

**Report Sections**:

1. **Current Status**: All metrics vs baseline (table format)

2. **Anomaly History**: Last 30 days (timeline)

3. **Trend Graphs**: Show degradation over time

4. **Maintenance Recommendations**: AI-generated suggestions

**Example Report**:

```
Engine Health Report  
Date: 2026-02-06 14:30  
  
CURRENT STATUS:  
✓ RPM: 3200 (Normal, within 1σ)  
⚠ Oil Pressure: 35 PSI (Warning, -10 PSI from baseline)  
✓ Coolant Temp: 178°F (Normal)  
✓ Fuel Rate: 4.3 GPH (Normal)  
  
ANOMALY HISTORY:  
2026-02-05: Oil pressure trending down (-5 PSI)  
2026-02-04: Oil pressure trending down (-3 PSI)  
2026-02-01: All systems normal  
  
TRENDS:  
Oil Pressure: Declining 2 PSI/week over last 2 weeks  
  
RECOMMENDATIONS:  
- Check engine oil level immediately  
- Inspect oil filter for clogs  
- Consider oil change within 10 engine hours  
- If pressure continues to decline, inspect oil pump
```

### 6.2 Raspberry Pi Health Monitoring

#### 6.2.1 System Metrics Collection

**Monitoring Script** (`/opt/d3kos/services/health/pi-monitor.js`):

```
const \{ exec \} = require('child\_process');  
  
function getSystemMetrics() \{  
  return \{  
    cpu\_temp: parseFloat(execSync('vcgencmd measure\_temp').toString().match(/\[\\d.\]+/)\[0\]),  
    cpu\_usage: parseFloat(execSync('top -bn1 | grep "Cpu(s)"').toString().match(/\[\\d.\]+/)\[0\]),  
    memory\_usage: parseFloat(execSync('free | grep Mem').toString().split(/\\s+/)\[2\]) /   
                   parseFloat(execSync('free | grep Mem').toString().split(/\\s+/)\[1\]) \* 100,  
    disk\_free: parseFloat(execSync('df -h / | tail -1').toString().split(/\\s+/)\[4\].replace('%', '')),  
    gpu\_temp: parseFloat(execSync('vcgencmd measure\_temp core').toString().match(/\[\\d.\]+/)\[0\]),  
    throttled: execSync('vcgencmd get\_throttled').toString().includes('throttled=0x0') ? false : true  
  \};  
\}
```

**Update Frequency**: Every 10 seconds

**Storage**: `/opt/d3kos/state/pi-health-status.json`

#### 6.2.2 Thresholds and Alerts

**Alert Configuration**:

```
const thresholds = \{  
  cpu\_temp: \{ warning: 70, critical: 80 \},  
  cpu\_usage: \{ warning: 70, critical: 90 \},  
  memory\_usage: \{ warning: 70, critical: 90 \},  
  disk\_free: \{ warning: 30, critical: 15 \}  
\};
```

**Alert Actions**:

- **CPU Temp \> 80°C**:

  - Visual: Red gauge, flashing indicator

  - Voice: "Raspberry Pi overheating. Reduce load or improve cooling."

  - Action: None (user intervention required)

- **Memory \> 95%**:

  - Visual: Red gauge

  - Voice: "Low memory. Restarting non-essential services."

  - Action: Restart camera service (if running)

- **Disk \< 18%**:

  - Visual: Red gauge

  - Voice: "Disk space critically low. Deleting oldest recordings."

  - Action: Auto-delete oldest camera recordings

- **Throttling Detected**:

  - Visual: Orange warning icon

  - Voice: "Performance throttled. Check power supply and cooling."

  - Action: Log event for troubleshooting

#### 6.2.3 Dashboard Integration

**System Status Row**:

```
\[CPU: 45% @ 65°C\] \[Memory: 62%\] \[Storage: 42% used\] \[GPU: 58°C\]
```

**Tap for Details**:

```
Raspberry Pi Status  
  
CPU: 45.2% @ 65.3°C (Normal)  
Memory: 2.5 GB / 4 GB (62%)  
Storage: 27 GB / 64 GB (42% used)  
GPU: 58°C (Normal)  
Throttling: No  
Uptime: 3 days, 14 hours  
  
\[View Logs\] \[Restart Services\] \[Close\]
```

### 6.3 Licensing & Version Management

#### 6.3.1 Tier Detection

**License File** (`/opt/d3kos/config/license.json`):

```
\{  
  "tier": 0,  
  "installation\_id": "abc123def456",  
  "installed\_apps": \[\],  
  "reset\_count": 7,  
  "max\_resets": 10,  
  "version": "1.0.3",  
  "last\_update\_check": "2026-02-06T14:30:00Z",  
  "features": \{  
    "voice\_assistant": false,  
    "camera": false,  
    "unlimited\_resets": false,  
    "cloud\_sync": false  
  \}  
\}
```

**Tier Detection Logic**:

```
function detectTier() \{  
  // Tier 2: OpenCPN or other paid apps installed  
  if (fs.existsSync('/opt/opencpn')) \{  
    return \{ tier: 2, reason: 'OpenCPN installed' \};  
  \}  
    
  // Tier 3: Valid subscription key (future)  
  if (fs.existsSync('/opt/d3kos/config/subscription.key')) \{  
    return \{ tier: 3, reason: 'Active subscription' \};  
  \}  
    
  // Tier 0: Default (opensource)  
  return \{ tier: 0, reason: 'Default free tier' \};  
\}
```

#### 6.3.2 Feature Restrictions & Update Capabilities

**Tier 0 (Opensource)**:

- ✓ Initial Setup wizard (10 resets max)

- ✓ Dashboard (basic gauges)

- ✓ Engine health monitoring

- ✓ Pi health monitoring

- ✗ Voice assistant (disabled)

- ✗ Camera integration (disabled)

- ✗ Data export (disabled)

- ✓ Boat log (30 days retention)

- ✓ OpenCPN (can install to upgrade to Tier 2)

- **Updates:** ✗ Cannot incrementally update - must download new image

- **Config Preservation:** ✗ No configuration backup - must re-run Initial Setup after update

**Tier 1 (Mobile App Integration)** (Free):

- ✓ All Tier 0 features

- ✓ Mobile app (iOS/Android)

- ✓ QR code pairing

- ✓ Cloud database synchronization

- ✓ Data export (enabled)

- ✓ Push notifications

- ✓ Remote monitoring

- **Updates:** ✗ Cannot incrementally update - must download new image

- **Config Preservation:** ✓ Mobile app stores onboarding + settings with installation\_id

- **Config Restore:** ✓ After update, mobile app restores configuration automatically

**Tier 2 (Premium Subscription)** (Paid):

- ✓ All Tier 1 features

- ✓ Voice assistant (enabled)

- ✓ Camera integration (enabled)

- ✓ AI-powered analysis

- ✓ Predictive maintenance recommendations

- ✓ Historical graphs (90 days)

- **Updates:** ✓ CAN incrementally update via OTA (apt/dpkg)

- **Config Preservation:** ✓ Automatic (no reinstall needed)

**Tier 3 (Enterprise/Fleet)** (Paid Annual):

- ✓ All Tier 2 features

- ✓ Unlimited resets

- ✓ Cloud sync

- ✓ Remote monitoring

- ✓ Multi-boat support

- ✓ Fleet management

- ✓ Priority support

- **Updates:** ✓ CAN incrementally update via OTA (apt/dpkg)

- **Config Preservation:** ✓ Automatic (no reinstall needed)

- **Fleet Updates:** ✓ Centralized update management

#### 6.3.3 Version Management & Upgrade System

**Current d3kOS Version**: 0.9.1-beta **GitHub Repository**: [https://github.com/SkipperDon/d3kos](https://github.com/SkipperDon/d3kos) **Version Format**: `MAJOR.MINOR.PATCH-STAGE` (e.g., 0.9.1-beta, 1.0.0-stable)


##### Version Tracking

**Storage Locations**:

1. **`/opt/d3kos/VERSION`** - Plain text version file

```
0.9.1-beta
```

2. **`/opt/d3kos/config/license.json`** - Version metadata

```
\{  
  "installation\_id": "3861513b314c5ee7",  
  "version": "0.9.1-beta",  
  "version\_installed\_at": "2026-02-17T10:00:00Z",  
  "tier": 2,  
  "reset\_count": 0,  
  "features": \{ ... \}  
\}
```


##### Tier-Based Upgrade Capabilities

| Tier | Can Upgrade? | Method | User Action |
| - | - | - | - |
| **Tier 0** | ❌ **NO** | New installation only | Download new image, re-flash SD card, re-run Initial Setup |
| **Tier 1** | ❌ **NO** | New installation only | Download new image, re-flash SD card, restore config via mobile app |
| **Tier 2** | ✅ **YES** | OTA curl-based upgrade | Approve in mobile app → automatic install |
| **Tier 3** | ✅ **YES** | OTA curl-based upgrade | Approve in mobile app → automatic install |


**Rationale**:

- **Tier 0**: No mobile app = no upgrade trigger mechanism, prevents incremental updates

- **Tier 1**: Free tier limitation to encourage Tier 2 upgrade for OTA convenience

- **Tier 2/3**: Paid tiers receive OTA upgrade as premium feature

**CRITICAL**: Tier 0 and Tier 1 **CANNOT** incrementally upgrade. Only Tier 2 and Tier 3 support over-the-air updates.


##### System Management API (Port 8095)

**Service**: `d3kos-system-api.service` **File**: `/opt/d3kos/services/system/system-api.py` **Nginx Proxy**: `/system/` → `localhost:8095/system/`

**API Endpoints**:

###### GET /system/version

Returns current d3kOS version and tier.

**Response** (Success):

```
\{  
  "success": true,  
  "version": "0.9.1-beta",  
  "version\_installed\_at": "2026-02-17T10:00:00Z",  
  "tier": 2,  
  "installation\_id": "3861513b314c5ee7"  
\}
```


###### GET /system/check-update

Checks GitHub for latest release version.

**Response** (Update Available):

```
\{  
  "success": true,  
  "current\_version": "0.9.1-beta",  
  "latest\_version": "0.9.2-beta",  
  "update\_available": true,  
  "release\_url": "https://github.com/SkipperDon/d3kos/releases/tag/v0.9.2-beta",  
  "release\_notes": "\#\# What's New\\n- Bug fixes\\n- Performance improvements",  
  "published\_at": "2026-02-20T15:30:00Z",  
  "tier": 2  
\}
```

**Response** (Tier 0 - Forbidden):

```
\{  
  "success": false,  
  "error": "Updates require Tier 1 or higher",  
  "tier": 0  
\}
```


###### POST /system/upgrade

Triggers upgrade process (Tier 2/3 only).

**Request**:

```
\{  
  "installation\_id": "3861513b314c5ee7"  
\}
```

**Response** (Success):

```
\{  
  "success": true,  
  "message": "Upgrade started",  
  "log\_file": "/opt/d3kos/logs/upgrade.log",  
  "note": "System will restart after upgrade completes"  
\}
```

**Response** (Tier 0/1 - Forbidden):

```
\{  
  "success": false,  
  "error": "Upgrades require Tier 2 or higher",  
  "tier": 0  
\}
```


###### GET /system/upgrade-status

Monitor upgrade progress.

**Response**:

```
\{  
  "success": true,  
  "log\_tail": "\[2026-02-20 10:15:32\] Downloading upgrade package...\\n\[2026-02-20 10:15:45\] Verifying checksum...\\n\[2026-02-20 10:15:46\] ✓ Checksum verified",  
  "log\_file": "/opt/d3kos/logs/upgrade.log"  
\}
```


##### GitHub Release Structure

**Release Tag Format**: `vMAJOR.MINOR.PATCH-STAGE` (e.g., `v0.9.1-beta`)

**Required Release Assets**:

1. `d3kos-upgrade.tar.gz` - Upgrade package

2. `d3kos-upgrade.tar.gz.sha256` - SHA-256 checksum

**Upgrade Package Contents**:

```
d3kos-upgrade/  
├── install.sh              \# Main installation script  
├── pre-upgrade.sh          \# Pre-upgrade checks (optional)  
├── post-upgrade.sh         \# Post-upgrade tasks (optional)  
├── services/               \# Updated service files  
├── scripts/                \# Updated scripts  
├── html/                   \# Updated web UI files  
└── etc/                    \# Updated system configs
```


##### Mobile App Upgrade Flow (Tier 2/3 Only)

**Step-by-Step Process**:

1. **Check Tier**

   - Mobile app: GET `/tier/status`

   - If Tier 0 or 1: Display "Upgrade to Tier 2 for automatic updates"

   - If Tier 2 or 3: Continue to step 2

2. **Check for Updates**

   - Mobile app: GET `/system/check-update`

   - Compare `current\_version` vs `latest\_version`

3. **Display Update Prompt** (if available)

```
┌─────────────────────────────────────┐  
│  Update Available                   │  
│  Current: 0.9.1-beta                │  
│  Latest:  0.9.2-beta                │  
│                                     │  
│  Release Notes:                     │  
│  • Bug fixes                        │  
│  • Performance improvements         │  
│                                     │  
│  \[ View Details \]  \[ Install Now \]  │  
└─────────────────────────────────────┘
```

4. **User Approves Upgrade**

   - Mobile app: POST `/system/upgrade` with `installation\_id`

   - Pi executes `/opt/d3kos/scripts/upgrade.sh` in background

5. **Monitor Upgrade Progress**

   - Mobile app: GET `/system/upgrade-status` every 5 seconds

   - Display log tail and progress spinner to user

6. **Upgrade Completes**

   - Pi services restart automatically

   - Mobile app detects version change via GET `/system/version`

   - Display "Upgrade Complete!" success message


##### Upgrade Script Process

**File**: `/opt/d3kos/scripts/upgrade.sh`

**Automated Steps**:

1. ✅ Check internet connection (ping 8.8.8.8)

2. ✅ Fetch latest release from GitHub API

3. ✅ Download `d3kos-upgrade.tar.gz`

4. ✅ Download `d3kos-upgrade.tar.gz.sha256`

5. ✅ **Verify SHA-256 checksum** (security)

6. ✅ Create backup in `/opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/`

   - Config files (`/opt/d3kos/config/`)

   - Data files (`/opt/d3kos/data/`)

   - License file (`license.json`)

7. ✅ Extract upgrade package

8. ✅ Run `pre-upgrade.sh` (if exists)

9. ✅ Stop d3kOS services (`d3kos-\*.service`, `signalk`, `nodered`)

10. ✅ Execute `install.sh` from upgrade package

11. ✅ Update `version` and `version\_installed\_at` in `license.json`

12. ✅ Run `post-upgrade.sh` (if exists)

13. ✅ Restart services

14. ✅ Verify critical services started successfully

15. ✅ Cleanup temporary files

16. ✅ Log completion to `/opt/d3kos/logs/upgrade.log`

**Security**:

- SHA-256 checksum verification prevents tampered packages

- `installation\_id` authentication prevents unauthorized upgrades

- Automatic backup enables manual rollback if needed


##### Rollback Process (Manual)

If upgrade fails, restore from backup:

```
\# 1. Stop services  
sudo systemctl stop d3kos-\*.service  
  
\# 2. Restore config  
sudo cp -r /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/config/\* /opt/d3kos/config/  
  
\# 3. Restore data  
sudo cp -r /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/data/\* /opt/d3kos/data/  
  
\# 4. Restore license  
sudo cp /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/license.json /opt/d3kos/config/  
  
\# 5. Restart services  
sudo systemctl restart d3kos-\*.service
```


##### First-Time Installation

**During Initial Image Flash**:

- Version set by `/opt/d3kos/scripts/generate-installation-id.sh` on first boot

- Reads version from `/opt/d3kos/VERSION`

- Writes to `license.json` with timestamp

**Example**:

```
\{  
  "installation\_id": "3861513b314c5ee7",  
  "version": "0.9.1-beta",  
  "version\_installed\_at": "2026-02-17T10:00:00Z",  
  "tier": 0,  
  "reset\_count": 0  
\}
```

#### 6.3.4 E-commerce Integration & Mobile App In-App Purchases

**Purpose**: Enable users to purchase Tier 2 ($9.99/month) and Tier 3 ($99.99/year) subscriptions directly within the mobile app, with seamless integration to central database for automatic tier upgrades.

**IMPORTANT**: Traditional e-commerce platforms (OpenCart, PrestaShop, osCommerce, Zen Cart, etc.) are **NOT suitable** for mobile app subscription billing. Apple and Google mandate use of their native payment systems (Apple IAP and Google Play Billing) for in-app subscriptions. Stripe Billing is used for web-based subscriptions and cross-platform management.

**Implementation Guide**: See `/home/boatiq/Helm-OS/doc/STRIPE\_BILLING\_IMPLEMENTATION\_GUIDE.md` for complete 40-60 hour development breakdown with code examples.


##### Supported Payment Platforms

| Platform | Use Case | Commission | Required For |
| - | - | - | - |
| **Stripe Billing** | Web checkout, subscription management, API | 2.9% + $0.30 | Primary payment processor (RECOMMENDED) |
| **Apple App Store IAP** | iOS app subscriptions | 15-30% | iOS apps (mandatory per App Store rules) |
| **Google Play Billing** | Android app subscriptions | 15-30% | Android apps (mandatory per Play Store rules) |
| **PayPal** | Alternative payment method | 2.9% + $0.30 | Optional (user preference) |


**Recommended Architecture**:

- **Primary**: Stripe Billing (lowest fees, best API, works cross-platform)

- **iOS**: Apple In-App Purchase (StoreKit 2) - mandatory per App Store guidelines

- **Android**: Google Play Billing Library 5.0+ - mandatory per Play Store guidelines

- **Alternative**: PayPal Subscriptions API for users without credit cards

**Why Not Traditional E-commerce Platforms?**

- ❌ No native Apple IAP integration

- ❌ No native Google Play Billing integration

- ❌ Designed for product sales, not SaaS subscriptions

- ❌ Poor API support for mobile apps

- ❌ Complex to customize for webhook-based tier upgrades

- ✅ Stripe Billing is specifically designed for subscription businesses


##### Database Schema & Implementation

**Required Database Tables** (MySQL/PostgreSQL):

**Table 1: `subscriptions`** (stores active subscriptions)

```
CREATE TABLE subscriptions (  
  subscription\_id VARCHAR(50) PRIMARY KEY,  
  installation\_id VARCHAR(16) NOT NULL,  
  tier INTEGER NOT NULL CHECK (tier IN (2, 3)),  
  status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'past\_due', 'canceled', 'expired')),  
  
  payment\_provider VARCHAR(20) NOT NULL CHECK (payment\_provider IN ('stripe', 'apple\_iap', 'google\_play', 'paypal')),  
  provider\_subscription\_id VARCHAR(100) NOT NULL,  
  provider\_customer\_id VARCHAR(100),  
  
  started\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP,  
  current\_period\_start TIMESTAMP NOT NULL,  
  current\_period\_end TIMESTAMP NOT NULL,  
  canceled\_at TIMESTAMP NULL,  
  expires\_at TIMESTAMP NULL,  
  
  amount\_cents INTEGER NOT NULL,  
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',  
  billing\_interval VARCHAR(10) NOT NULL CHECK (billing\_interval IN ('month', 'year')),  
  
  payment\_failed\_count INTEGER DEFAULT 0,  
  last\_payment\_at TIMESTAMP NULL,  
  next\_payment\_at TIMESTAMP NULL,  
  
  user\_email VARCHAR(255),  
  user\_name VARCHAR(255),  
  
  created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
  updated\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP,  
  
  INDEX idx\_installation\_id (installation\_id),  
  INDEX idx\_status (status),  
  INDEX idx\_provider\_subscription\_id (provider\_subscription\_id),  
  FOREIGN KEY (installation\_id) REFERENCES installations(installation\_id)  
);
```

**Table 2: `payments`** (payment transaction history)

```
CREATE TABLE payments (  
  payment\_id VARCHAR(50) PRIMARY KEY,  
  installation\_id VARCHAR(16) NOT NULL,  
  subscription\_id VARCHAR(50) NOT NULL,  
  
  provider\_payment\_id VARCHAR(100) NOT NULL,  
  amount\_cents INTEGER NOT NULL,  
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',  
  
  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded')),  
  failure\_reason TEXT NULL,  
  
  invoice\_url TEXT NULL,  
  receipt\_url TEXT NULL,  
  
  paid\_at TIMESTAMP NULL,  
  created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
  
  INDEX idx\_installation\_id (installation\_id),  
  INDEX idx\_subscription\_id (subscription\_id),  
  FOREIGN KEY (installation\_id) REFERENCES installations(installation\_id),  
  FOREIGN KEY (subscription\_id) REFERENCES subscriptions(subscription\_id)  
);
```

**Table 3: `tier\_upgrades`** (audit log of tier changes)

```
CREATE TABLE tier\_upgrades (  
  upgrade\_id VARCHAR(50) PRIMARY KEY,  
  installation\_id VARCHAR(16) NOT NULL,  
  
  from\_tier INTEGER NOT NULL,  
  to\_tier INTEGER NOT NULL,  
  
  upgrade\_method VARCHAR(20) NOT NULL CHECK (upgrade\_method IN ('payment', 'promo\_code', 'manual', 'opencpn\_detect')),  
  subscription\_id VARCHAR(50) NULL,  
  payment\_id VARCHAR(50) NULL,  
  
  user\_email VARCHAR(255),  
  user\_name VARCHAR(255),  
  
  upgraded\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,  
  
  INDEX idx\_installation\_id (installation\_id),  
  FOREIGN KEY (installation\_id) REFERENCES installations(installation\_id),  
  FOREIGN KEY (subscription\_id) REFERENCES subscriptions(subscription\_id)  
);
```

**Update existing `installations` table:**

```
ALTER TABLE installations  
ADD COLUMN is\_paid\_tier BOOLEAN DEFAULT FALSE,  
ADD COLUMN subscription\_status VARCHAR(20) CHECK (subscription\_status IN ('none', 'active', 'past\_due', 'canceled', 'expired')),  
ADD COLUMN subscription\_expires\_at TIMESTAMP NULL;
```


##### Backend Services Required

**Service 1: Stripe Webhook Handler** (Python/Flask or Node.js/Express)

- **File**: `/opt/d3kos/services/billing/stripe\_webhook\_handler.py`

- **Port**: 5000 (proxied via nginx)

- **Purpose**: Receives Stripe webhook events and updates database

- **Events Handled**:

  - `customer.subscription.created` → Create subscription, upgrade tier

  - `customer.subscription.updated` → Update subscription status

  - `customer.subscription.deleted` → Expire subscription, downgrade tier

  - `invoice.payment\_succeeded` → Record payment, reset failure counter

  - `invoice.payment\_failed` → Increment failure counter, start grace period

  - `customer.subscription.trial\_will\_end` → Send reminder email

**Service 2: Subscription Management API** (Python/Flask or Node.js/Express)

- **File**: `/opt/d3kos/services/billing/subscription\_api.py`

- **Port**: 5001 (proxied via nginx)

- **Purpose**: Mobile app endpoints for subscription management

**API Endpoints**:

**Stripe Integration:**

- `POST /api/v1/stripe/checkout/session` - Create Stripe checkout session

- ```
Request: \{  
  "installation\_id": "550e8400e29b41d4",  
  "tier": 2,  
  "billing\_interval": "month"  
\}  
Response: \{  
  "checkout\_url": "https://checkout.stripe.com/...",  
  "session\_id": "cs\_test\_abc123"  
\}
```

- `POST /api/v1/webhooks/stripe` - Receive Stripe webhooks (signature verified)

- `GET /api/v1/stripe/customer-portal` - Get Stripe Customer Portal URL for subscription management

**Apple IAP Integration:**

- `POST /api/v1/apple/verify-receipt` - Validate App Store receipt

- ```
Request: \{  
  "installation\_id": "550e8400e29b41d4",  
  "receipt\_data": "base64\_encoded\_receipt",  
  "transaction\_id": "1000000123456789"  
\}
```

- `POST /api/v1/webhooks/apple` - Receive Apple server-to-server notifications

**Google Play Integration:**

- `POST /api/v1/google/verify-purchase` - Validate Google Play purchase

- ```
Request: \{  
  "installation\_id": "550e8400e29b41d4",  
  "purchase\_token": "abc123...",  
  "product\_id": "tier2\_monthly"  
\}
```

- `POST /api/v1/webhooks/google` - Receive Google Real-Time Developer Notifications

**Tier Management:**

- `GET /api/v1/tier/status?installation\_id=XXX` - Get current tier and subscription status

- ```
Response: \{  
  "installation\_id": "550e8400e29b41d4",  
  "tier": 2,  
  "is\_paid\_tier": true,  
  "subscription\_status": "active",  
  "subscription\_expires\_at": "2026-03-16T10:00:00Z",  
  "subscription": \{  
    "id": "sub\_abc123",  
    "provider": "stripe",  
    "interval": "month",  
    "amount": 9.99,  
    "next\_billing\_date": "2026-03-16T10:00:00Z",  
    "canceled": false  
  \}  
\}
```

- `POST /api/v1/subscription/cancel` - Cancel active subscription

- `POST /api/v1/subscription/reactivate` - Reactivate canceled subscription (before expiration)

- `GET /api/v1/subscription/history` - Get payment history (last 50 transactions)

**Systemd Services:**

```
sudo systemctl enable d3kos-stripe-webhook.service  
sudo systemctl enable d3kos-subscription-api.service  
sudo systemctl start d3kos-stripe-webhook.service  
sudo systemctl start d3kos-subscription-api.service
```


##### Mobile App Purchase Flow

**Stripe Flow** (Web-based, works on iOS/Android/Web):

1. App calls: `POST /api/v1/stripe/checkout/session` with installation\_id + tier

2. Backend creates Stripe Checkout Session, returns checkout URL

3. App opens URL in in-app browser (SafariViewController on iOS, Chrome Custom Tab on Android)

4. User enters payment details on Stripe-hosted page (PCI compliant)

5. Stripe processes payment

6. Stripe webhook fires: `customer.subscription.created`

7. Backend webhook handler:

   - Verifies signature

   - Creates subscription record

   - Updates `installations.tier = 2`, `is\_paid\_tier = TRUE`

   - Logs tier upgrade in `tier\_upgrades` table

8. App polls: `GET /api/v1/tier/status` every 2 seconds for 30 seconds

9. App receives `\{"tier": 2, "status": "active"\}` and unlocks Tier 2 features

10. Pi polls cloud on next boot (24-hour interval), detects upgrade, enables Tier 2 features

**Apple IAP Flow** (iOS only):

1. App requests product info: `Product.products(for: \["com.d3kos.tier2.monthly"\])`

2. App displays localized price from App Store

3. User taps "Subscribe", triggers: `product.purchase()`

4. iOS shows native payment sheet (Face ID/Touch ID)

5. User confirms purchase

6. App receives transaction: `Transaction.updates` stream

7. App sends receipt to backend: `POST /api/v1/apple/verify-receipt`

8. Backend validates receipt with Apple server

9. Backend creates subscription record, updates tier

10. Backend returns success to app

11. App unlocks Tier 2 features immediately

12. Apple sends server-to-server notifications for renewals/cancellations

**Google Play Flow** (Android only):

1. App queries product details: `billingClient.queryProductDetailsAsync()`

2. App displays localized price from Play Store

3. User taps "Subscribe", triggers: `billingClient.launchBillingFlow()`

4. Android shows native payment sheet (Google Pay)

5. User confirms purchase

6. App receives purchase token: `onPurchasesUpdated()`

7. App sends token to backend: `POST /api/v1/google/verify-purchase`

8. Backend verifies purchase with Google Play Developer API

9. Backend creates subscription record, updates tier

10. Backend returns success to app

11. App acknowledges purchase: `billingClient.acknowledgePurchase()`

12. App unlocks Tier 2 features immediately

13. Google sends Real-Time Developer Notifications for renewals/cancellations


##### Failed Payment Handling (Grace Period)

**Grace Period Logic:**

- **Day 0**: 1st failure → Status = 'past\_due', retry in 3 days, send email notification

- **Day 3**: 2nd failure → Retry in 7 days (total: 10 days), send warning email

- **Day 10**: 3rd failure → Retry in 14 days (total: 24 days), send final warning email

- **Day 24**: 4th failure → Status = 'expired', downgrade tier to 1, disable Tier 2/3 features

**During Grace Period** (status = 'past\_due'):

- ✅ Tier 2/3 features remain active

- ⚠️ Mobile app shows persistent warning banner: "⚠️ Payment Issue - Update Payment Method"

- 📧 Email notifications sent before each retry

- 🔧 User can update payment method via:

  - Stripe: Customer Portal (one-click link in email)

  - Apple: iOS Settings → Subscriptions

  - Google: Google Play → Subscriptions

**After Grace Period Expiration:**

- ❌ Subscription expires, status = 'expired'

- ⬇️ Tier downgrade: Tier 2→1 or Tier 3→1

- 🔒 Tier 2/3 features disabled on next Pi boot

- 📱 Mobile app shows: "Subscription expired - Tap to reactivate"

- 💳 User can reactivate by purchasing new subscription


##### Development Time & Cost Estimate

**Total Development Time: 40-60 hours**

| Phase | Hours | Tasks |
| - | - | - |
| **Phase 1: Stripe Setup** | 4-6 | Account setup, product configuration, webhook setup, customer portal |
| **Phase 2: Backend API** | 16-24 | Database schema, webhook handler, subscription API, systemd services, nginx config |
| **Phase 3: Mobile App Integration** | 12-18 | iOS StoreKit 2 integration, Android Billing Library 5.0+, UI design |
| **Phase 4: Testing & Deployment** | 8-12 | Local testing, iOS Sandbox, Android testing, production deployment |


**Development Costs:**

- Developer time: 40-60 hours × $50-150/hour = **$2,000 - $9,000**

**Monthly Operational Costs:**

- Stripe fees: 2.9% + $0.30 per transaction

- Apple IAP fees: 15-30% (automatically deducted by Apple)

- Google Play fees: 15-30% (automatically deducted by Google)

- Server hosting: $10-50/month (VPS for API)

- Email notifications: $0-10/month (SendGrid free tier: 100 emails/day)

- Database: $0-20/month (included with VPS)

**Revenue Example** (100 Tier 2 subscribers):

- Gross revenue: $999/month

- Stripe fees: ~$30/month (if 30% use Stripe)

- Apple IAP fees: ~$200/month (if 40% use iOS, 30% commission)

- Google Play fees: ~$100/month (if 30% use Android, 15-30% commission)

- **Net revenue: $669/month**

- **Break-even: 3-13 months** depending on development costs

**Detailed Implementation Guide:**

- See `/home/boatiq/Helm-OS/doc/STRIPE\_BILLING\_IMPLEMENTATION\_GUIDE.md`

- Complete code examples for webhook handler, subscription API, iOS StoreKit 2, Android Billing Library

- Step-by-step setup instructions

- Testing procedures

- Deployment checklist


#### 6.3.5 QR Code Pairing

**QR Code Content**:

```
d3kos://pair?id=abc123def456&version=1.0.3&tier=2&boat=MyBoat
```

**Mobile App Use Case**:

- Scan QR code to pair mobile app with d3kOS

- Mobile app can remotely view dashboard (Tier 3)

- Mobile app can view camera feed (Tier 2+)

- Mobile app can receive alerts (all tiers)

**Display Location**:

- Onboarding completion screen

- Main menu: "QR Code" button

- License info page


### 6.4 AI-Powered Self-Healing System

**Purpose**: Automatically detect, diagnose, and remediate system issues with minimal user intervention. Critical for marine environments where technical support is limited and boat operators need reliable, self-maintaining systems.

**Implementation Status**: ⏳ NOT IMPLEMENTED (Specification Only)


#### 6.4.1 Architecture Overview

**5-Tier Self-Healing Architecture**:

1. **Detection Layer** - Monitor system health (engine, Pi, services, network)

2. **Correlation Engine** - Pattern match known failure modes

3. **AI Diagnosis** - Root cause analysis via AI Assistant

4. **Auto-Remediation** - Execute safe fixes automatically

5. **User Notification** - Translate errors to plain English, voice alerts

**Data Flow**:

```
Anomaly Detected → Correlate with Patterns → AI Diagnosis → Auto-Remediate → Notify User
```


#### 6.4.2 Detection Layer (Tier 1)

##### Engine Anomaly Detection

**Baseline Comparison** (Statistical Process Control):

Uses benchmark data from Section 6.1.1:

```
function detectAnomaly(current, baseline) \{  
  const deviation = Math.abs(current.value - baseline.mean);  
  const sigma = baseline.stddev;  
  
  if (deviation \> 3 \* sigma) \{  
    return \{  
      level: 'CRITICAL',  
      message: \`$\{current.name\} is $\{deviation.toFixed(1)\} units from baseline (\>3σ)\`,  
      type: 'ENGINE\_ANOMALY',  
      timestamp: Date.now()  
    \};  
  \} else if (deviation \> 2 \* sigma) \{  
    return \{ level: 'WARNING', type: 'ENGINE\_ANOMALY' \};  
  \}  
  
  return \{ level: 'NORMAL', message: null \};  
\}
```

**Monitored Metrics**:

- RPM (idle, cruise) - instability detection

- Oil pressure - low pressure warnings

- Coolant temperature - overheating detection

- Fuel consumption - efficiency anomalies

- Voltage - charging system issues

##### Pi System Monitoring

**Metrics Collection** (every 10 seconds):

```
const systemMetrics = \{  
  cpu\_temp: vcgencmd('measure\_temp'),     // °C  
  cpu\_usage: top('-bn1'),                 // %  
  memory\_usage: free(),                   // %  
  disk\_free: df('-h /'),                  // % remaining  
  gpu\_temp: vcgencmd('measure\_temp core'),  
  throttled: vcgencmd('get\_throttled')    // undervoltage/throttling  
\};
```

**Thresholds**:

```
const thresholds = \{  
  cpu\_temp: \{ warning: 70, critical: 80 \},    // °C  
  cpu\_usage: \{ warning: 70, critical: 90 \},   // %  
  memory\_usage: \{ warning: 70, critical: 90 \}, // %  
  disk\_free: \{ warning: 30, critical: 15 \}     // % remaining  
\};
```

**Storage**: `/opt/d3kos/state/health-metrics.json` (last 1000 samples, ~10 min history)

##### Service Status Monitoring

**Services Checked**:

- CAN interface: `ifconfig can0` (up/down)

- Signal K: `systemctl is-active signalk`

- Node-RED: `systemctl is-active nodered`

- d3kOS services: `systemctl is-active d3kos-\*.service`

- Network: `ping -c 1 8.8.8.8` (internet connectivity)

**Anomaly Types**:

- `SERVICE\_DOWN` - Critical service stopped

- `SERVICE\_CRASHED` - Service exited with error

- `NETWORK\_LOST` - No internet connectivity

- `CAN\_DISCONNECTED` - NMEA2000 bus offline


#### 6.4.3 Correlation Engine (Tier 2)

**Known Failure Patterns**:

```
const failure\_patterns = \{  
  FAILING\_SD\_CARD: \{  
    symptoms: \["DISK\_IO\_SPIKE", "NETWORK\_DROPPED", "SERVICE\_CRASHED"\],  
    time\_window: 10,  // seconds  
    confidence: 0.85,  
    root\_cause: "SD card failure",  
    explanation: "Network dropped at same time disk I/O spiked - likely failing SD card",  
    recommended\_action: "REPLACE\_SD\_CARD"  
  \},  
  
  OVERHEATING: \{  
    symptoms: \["CPU\_TEMP\_HIGH", "THROTTLED", "SLOW\_RESPONSE"\],  
    time\_window: 60,  
    confidence: 0.90,  
    root\_cause: "CPU overheating",  
    explanation: "CPU temperature above 80°C causing throttling",  
    recommended\_action: "IMPROVE\_COOLING"  
  \},  
  
  LOW\_POWER: \{  
    symptoms: \["UNDERVOLTAGE", "USB\_DEVICE\_DISCONNECT", "RANDOM\_REBOOT"\],  
    time\_window: 5,  
    confidence: 0.95,  
    root\_cause: "Inadequate power supply",  
    explanation: "Power supply cannot provide 5V 3A required",  
    recommended\_action: "REPLACE\_POWER\_SUPPLY"  
  \},  
  
  STUCK\_PROCESS: \{  
    symptoms: \["CPU\_100\_PERCENT", "PROCESS\_AGE\_5MIN", "NO\_USER\_ACTIVITY"\],  
    time\_window: 300,  // 5 minutes  
    confidence: 0.85,  
    root\_cause: "Process deadlock or infinite loop",  
    explanation: "Process consuming 100% CPU for extended period",  
    recommended\_action: "KILL\_RESTART\_PROCESS"  
  \},  
  
  OUT\_OF\_MEMORY: \{  
    symptoms: \["MEMORY\_90\_PERCENT", "SERVICE\_CRASHED", "OOM\_KILLER"\],  
    time\_window: 30,  
    confidence: 0.95,  
    root\_cause: "Insufficient memory",  
    explanation: "System ran out of memory and killed processes",  
    recommended\_action: "RESTART\_SERVICES"  
  \}  
\};
```

**Correlation Algorithm**:

```
function correlateEvents(events, time\_window\_seconds) \{  
  const matches = \[\];  
  
  for (const pattern\_name in failure\_patterns) \{  
    const pattern = failure\_patterns\[pattern\_name\];  
  
    // Find events matching pattern symptoms within time window  
    const symptom\_matches = events.filter(e =\>  
      pattern.symptoms.includes(e.type) &&  
      e.timestamp \> (Date.now() - pattern.time\_window \* 1000)  
    );  
  
    // Pattern matched if at least 2 symptoms present  
    if (symptom\_matches.length \>= 2) \{  
      matches.push(\{  
        pattern: pattern\_name,  
        confidence: pattern.confidence,  
        evidence: symptom\_matches,  
        root\_cause: pattern.root\_cause,  
        explanation: pattern.explanation,  
        recommended\_action: pattern.recommended\_action  
      \});  
    \}  
  \}  
  
  // Return highest confidence match  
  return matches.sort((a, b) =\> b.confidence - a.confidence)\[0\];  
\}
```


#### 6.4.4 AI Diagnosis (Tier 3)

**Integration with AI Assistant**:

Extends existing AI Assistant (Section 4.5) with diagnostic capabilities.

**Diagnostic Request Format**:

```
\{  
  "query": "System health diagnostic needed",  
  "context": \{  
    "system\_state": \{  
      "cpu\_temp": 85,  
      "cpu\_usage": 95,  
      "memory\_free": 10,  
      "disk\_free": 5,  
      "services": \{  
        "signalk": "running",  
        "nodered": "crashed",  
        "camera": "running"  
      \},  
      "engine\_metrics": \{  
        "rpm": 3200,  
        "oil\_pressure": 35,  
        "coolant\_temp": 178  
      \}  
    \},  
    "anomalies": \[  
      \{"type": "CPU\_OVERHEATING", "severity": "WARNING"\},  
      \{"type": "NODERED\_CRASHED", "severity": "CRITICAL"\}  
    \],  
    "recent\_events": \[  
      "User started camera recording 2 minutes ago",  
      "Node-RED crashed 30 seconds ago"  
    \],  
    "correlation": \{  
      "pattern": "STUCK\_PROCESS",  
      "confidence": 0.85,  
      "root\_cause": "Process deadlock"  
    \}  
  \}  
\}
```

**AI Diagnostic Prompt** (added to skills.md):

```
\#\# System Diagnostics (Self-Healing)  
  
You are a marine system diagnostician. When given system health data:  
  
1. \*\*Identify root cause\*\* - Single most likely issue  
2. \*\*Explain in plain English\*\* - Non-technical, boat operator friendly  
3. \*\*Suggest fixes\*\* - Prioritized by confidence (0-1.0)  
4. \*\*Indicate urgency\*\* - Low/Medium/High/Critical  
5. \*\*User action needed\*\* - What operator should do (if any)  
  
Focus on marine safety and reliability. Be concise.
```

**AI Response Format**:

```
\{  
  "root\_cause": "Camera recording consuming excessive CPU",  
  "explanation": "Node-RED crashed due to CPU starvation caused by camera process",  
  "urgency": "High",  
  "suggested\_fixes": \[  
    \{  
      "action": "STOP\_CAMERA\_RECORDING",  
      "confidence": 0.90,  
      "user\_message": "Stop camera recording to free up CPU resources",  
      "requires\_approval": true  
    \},  
    \{  
      "action": "RESTART\_NODERED",  
      "confidence": 0.95,  
      "user\_message": "Restart Node-RED to restore dashboard functionality",  
      "requires\_approval": false  
    \}  
  \],  
  "user\_action\_needed": "Consider stopping camera recording during critical operations"  
\}
```


#### 6.4.5 Auto-Remediation Engine (Tier 4)

**Remediation Actions** (safe, reversible):

```
const remediation\_actions = \{  
  RESTART\_SERVICE: \{  
    severity\_threshold: "CRITICAL",  
    requires\_approval: false,  // Auto-execute  
    command: "systemctl restart \{service\_name\}",  
    rollback: "systemctl stop \{service\_name\}",  
    timeout: 30,  // seconds  
    verification: "systemctl is-active \{service\_name\}"  
  \},  
  
  KILL\_STUCK\_PROCESS: \{  
    severity\_threshold: "CRITICAL",  
    requires\_approval: false,  // Auto-execute  
    command: "kill -9 \{pid\}",  
    conditions: \["cpu\_usage \> 90%", "process\_age \> 5min"\],  
    timeout: 5,  
    verification: "! ps -p \{pid\}"  
  \},  
  
  CLEAR\_TEMP\_FILES: \{  
    severity\_threshold: "WARNING",  
    requires\_approval: false,  // Auto-execute  
    command: "find /tmp -type f -atime +7 -delete",  
    timeout: 60,  
    verification: "df -h /tmp | awk '\{print $5\}'"  
  \},  
  
  STOP\_CAMERA\_RECORDING: \{  
    severity\_threshold: "WARNING",  
    requires\_approval: true,  // Ask user first  
    command: "curl -X POST http://localhost:8084/camera/record/stop",  
    timeout: 10  
  \},  
  
  INITIAL\_SETUP\_RESET: \{  
    severity\_threshold: "CRITICAL",  
    requires\_approval: true,  // ALWAYS ask user  
    command: "/opt/d3kos/scripts/initial-setup-reset.sh",  
    timeout: 30  
  \}  
\};
```

**Remediation Flow**:

```
async function executeRemediation(action\_name, params) \{  
  const action = remediation\_actions\[action\_name\];  
  
  // Step 1: Check if approval required  
  if (action.requires\_approval) \{  
    const approved = await askUserApproval(action\_name, params);  
    if (!approved) \{  
      logRemediation(\{ action: action\_name, status: "declined", timestamp: Date.now() \});  
      return \{ success: false, reason: "User declined" \};  
    \}  
  \}  
  
  // Step 2: Log remediation attempt  
  logRemediation(\{  
    action: action\_name,  
    params: params,  
    timestamp: Date.now(),  
    auto\_executed: !action.requires\_approval  
  \});  
  
  // Step 3: Execute command  
  try \{  
    const result = await executeCommand(action.command, params, action.timeout);  
  
    // Step 4: Verify remediation worked  
    const verified = await verifySuccess(action.verification, params);  
  
    if (verified) \{  
      logRemediation(\{ action: action\_name, status: "success", result: result \});  
      notifyUser(\`✅ Issue resolved: $\{action\_name\}\`, "success");  
      return \{ success: true, result: result \};  
    \} else \{  
      // Step 5: Rollback if verification failed  
      if (action.rollback) \{  
        await executeCommand(action.rollback, params, action.timeout);  
      \}  
      logRemediation(\{ action: action\_name, status: "failed", reason: "Verification failed" \});  
      notifyUser(\`⚠️ Remediation failed: $\{action\_name\}\`, "warning");  
      return \{ success: false, reason: "Verification failed" \};  
    \}  
  
  \} catch (error) \{  
    logRemediation(\{ action: action\_name, status: "error", error: error.message \});  
    notifyUser(\`❌ Remediation error: $\{action\_name\}\`, "error");  
    return \{ success: false, reason: error.message \};  
  \}  
\}
```

**Remediation Log** (`/var/log/d3kos-remediation.log`):

```
\[2026-02-17 14:30:15\] ACTION: RESTART\_SERVICE (nodered), AUTO: true, RESULT: success  
\[2026-02-17 14:31:22\] ACTION: STOP\_CAMERA\_RECORDING, AUTO: false, APPROVED: yes, RESULT: success  
\[2026-02-17 15:45:10\] ACTION: CLEAR\_TEMP\_FILES, AUTO: true, RESULT: success, FREED: 1.2GB
```


#### 6.4.6 User Notification (Tier 5)

##### Error Translation (Technical → Plain English)

**Translation Database** (`/opt/d3kos/config/error-translations.json`):

```
\{  
  "systemd\[1\]: your-app.service: Main process exited, code=killed, status=9/KILL":  
    "The main program crashed and had to be stopped. Restarting now.",  
  
  "vcgencmd: throttled=0x50000":  
    "Power supply issue detected. Use official 5V 3A power adapter.",  
  
  "can0: No such device":  
    "NMEA2000 connection lost. Check CAN bus wiring.",  
  
  "Out of memory: Killed process 1234 (node)":  
    "System ran out of memory and stopped Node-RED. Try closing other programs.",  
  
  "SD card I/O error":  
    "SD card may be failing. Back up data and replace card soon.",  
  
  "CPU temperature 85°C (expected 45°C)":  
    "System is overheating. Improve ventilation or reduce workload."  
\}
```

**Translation Function**:

```
function translateForUser(technical\_error) \{  
  const translations = loadErrorTranslations();  
  const plain\_english = translations\[technical\_error\] ||  
                        "Something went wrong with the system.";  
  
  return \{  
    display: plain\_english,  
    voice: plain\_english,  
    action\_taken: "System automatically fixed the issue.",  
    user\_action\_needed: "None - monitoring for repeat issues."  
  \};  
\}
```

##### Voice Alerts (Tier 2+ Only)

**Alert Trigger**:

```
async function voiceAlert(message, severity) \{  
  const tier = getTier();  
  if (tier \< 2) return;  // Voice requires Tier 2+  
  
  const voice\_message = \`Helm alert: $\{message\}\`;  
  
  // Text-to-speech via Piper (from Section 4.3.3)  
  await textToSpeech(voice\_message);  
  
  // Log alert  
  logAlert(\{  
    message: message,  
    severity: severity,  
    voice\_alert\_sent: true,  
    timestamp: Date.now()  
  \});  
\}
```

**Alert Examples**:

- INFO: No voice alert (log only)

- WARNING: Visual alert only

- CRITICAL: Visual + voice alert every 5 minutes until acknowledged

##### Dashboard Notifications

**Banner Display** (top of dashboard):

```
\<div id="healing-banner" class="banner banner-success" style="display: none;"\>  
  \<span id="healing-message"\>✅ Issue resolved: Node-RED restarted\</span\>  
  \<button onclick="viewRemediationHistory()"\>View Details\</button\>  
  \<button onclick="closeBanner()"\>×\</button\>  
\</div\>
```

**Banner Types**:

- `banner-success` - Green: Issue resolved automatically

- `banner-warning` - Yellow: Issue detected, awaiting user approval

- `banner-error` - Red: Remediation failed, manual intervention needed

##### Remediation History Page

**Location**: `/var/www/html/remediation-history.html`

**UI Layout**:

```
┌─────────────────────────────────────────┐  
│  Self-Healing History                   │  
│  \[ Last 7 Days ▼ \]  \[ Export CSV \]      │  
├─────────────────────────────────────────┤  
│  Feb 17, 2026 2:15 PM                   │  
│  ✅ Node-RED Restarted                  │  
│  Issue: Process stuck (100% CPU)        │  
│  Root Cause: Infinite loop detected     │  
│  Action: Automatic restart              │  
│  Result: Successful (verified)          │  
│  \[ View Technical Details \]             │  
├─────────────────────────────────────────┤  
│  Feb 17, 2026 11:30 AM                  │  
│  ✅ Disk Space Cleared                  │  
│  Issue: Disk 92% full                   │  
│  Root Cause: Temp files accumulation    │  
│  Action: Deleted files older than 7 days│  
│  Result: 78% full (14% freed)           │  
│  \[ View Technical Details \]             │  
├─────────────────────────────────────────┤  
│  Feb 16, 2026 6:45 PM                   │  
│  ⚠️ User Declined Action                │  
│  Issue: Camera using excessive CPU      │  
│  Suggested: Stop camera recording       │  
│  User Response: Declined                │  
│  Result: Issue persists, monitoring     │  
│  \[ View Technical Details \]             │  
└─────────────────────────────────────────┘
```

**Data Storage**: `/opt/d3kos/data/remediation-history.json`

**Retention**:

- Tier 0/1: 30 days

- Tier 2: 1 year

- Tier 3: Unlimited (with export to cloud)


#### 6.4.7 Tier-Based Feature Matrix

| Feature | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
| - | - | - | - | - |
| **Detection** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full |
| **Correlation** | ✅ Local | ✅ Local | ✅ Local + Cloud | ✅ Local + Cloud |
| **AI Diagnosis** | ❌ No | ⚠️ Limited (cached) | ✅ Full | ✅ Full + Priority |
| **Auto-Remediation** | ⚠️ Manual only | ⚠️ Manual only | ✅ Safe actions auto | ✅ All actions auto |
| **Voice Alerts** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **History Tracking** | ✅ 30 days | ✅ 90 days | ✅ 1 year | ✅ Unlimited |
| **Predictive Maintenance** | ❌ No | ❌ No | ✅ Basic | ✅ Advanced |
| **Cloud Logging** | ❌ No | ⚠️ Manual export | ✅ Auto-sync | ✅ Auto-sync + alerts |



#### 6.4.8 Implementation Roadmap

**Phase 1: Enhanced Health Monitoring** (8-10 hours)

- Expand `/usr/local/bin/d3kos-health.sh` to monitor CPU temp, memory, disk

- Add engine metrics monitoring (RPM, temp, pressure from Signal K)

- Store metrics in `/opt/d3kos/state/health-metrics.json`

- Implement threshold-based alerting

**Phase 2: Anomaly Detection** (6-8 hours)

- Implement statistical anomaly detection (SPC) for engine metrics

- Add pattern matching for common failures

- Severity classification (INFO/WARNING/CRITICAL)

- Event logging to `/var/log/d3kos-anomalies.log`

**Phase 3: AI Integration** (8-10 hours)

- Extend AI Assistant with `diagnose()` function

- Add system health context to AI queries

- Create error translation database

- Implement confidence scoring

**Phase 4: Auto-Remediation** (6-8 hours)

- Implement safe remediation actions (restart services, kill processes)

- Create approval workflow for risky actions

- Add remediation logging to `/var/log/d3kos-remediation.log`

- Implement rollback mechanism

**Phase 5: User Interface** (6-8 hours)

- Create health dashboard page (`/health-dashboard.html`)

- Create remediation history page (`/remediation-history.html`)

- Add voice alerts integration (Tier 2+)

- Add dashboard banner notifications

**Total Estimated Effort**: 30-40 hours

**Files to Create**:

- `/opt/d3kos/services/health/health-monitor.py` - Detection layer

- `/opt/d3kos/services/health/correlation-engine.py` - Pattern matching

- `/opt/d3kos/services/health/remediation-engine.py` - Auto-fix actions

- `/opt/d3kos/services/ai/ai\_diagnostic.py` - AI diagnosis integration

- `/var/www/html/remediation-history.html` - User interface

- `/opt/d3kos/config/error-translations.json` - Error translation database

- `/var/log/d3kos-remediation.log` - Action log

- `/var/log/d3kos-anomalies.log` - Anomaly detection log


#### 6.4.9 Why This is Critical for d3kOS

**Marine Environment Challenges**:

1. ✅ Limited technical support availability

2. ✅ Non-technical boat operators need simple, reliable systems

3. ✅ Safety-critical - engine/system failures at sea are dangerous

4. ✅ Often operates offline or with limited connectivity

5. ✅ Harsh environment (heat, vibration, moisture) increases failure rates

**Unique Differentiator**:

- No other marine system offers AI-powered self-healing

- Proactive issue resolution vs. reactive troubleshooting

- Reduces reliance on technical expertise

- Improves safety and reliability at sea


## 7. NETWORK ARCHITECTURE

### 7.1 WiFi Access Point

**Configuration** (`/etc/NetworkManager/system-connections/d3kOS-AP`):

```
\[connection\]  
id=d3kOS-AP  
type=wifi  
autoconnect=true  
  
\[wifi\]  
mode=ap  
ssid=d3kOS  
  
\[wifi-security\]  
key-mgmt=wpa-psk  
psk=d3kos-2026  
  
\[ipv4\]  
method=shared  
address=10.42.0.1/24
```

**DHCP Range**: 10.42.0.2 - 10.42.0.254

**Services Available**:

- HTTP: Port 80 → Main menu

- WebSocket: Port 3000 → Signal K

- Dashboard: Port 1880 → Node-RED

- Camera: Port 554 → RTSP stream (if enabled)

### 7.2 Ethernet Sharing

**Shared Mode**:

- WiFi clients can access internet via Raspberry Pi's ethernet connection

- Use cases: Download charts, check for updates, cloud sync (Tier 3)

**Direct Mode**:

- Raspberry Pi gets IP via DHCP from boat's network

- No internet sharing

- Use case: Integration with existing boat network

**Auto-Detection**:

```
\# Check if ethernet has internet  
if ping -c 1 8.8.8.8 &\> /dev/null; then  
  \# Enable sharing  
  nmcli connection modify d3kOS-AP ipv4.method shared  
else  
  \# Direct mode  
  nmcli connection modify d3kOS-AP ipv4.method auto  
fi
```

### 7.3 Network Services

**Firewall Configuration** (ufw):

```
\# Allow incoming on WiFi interface (wlan0)  
ufw allow in on wlan0 to any port 80     \# HTTP  
ufw allow in on wlan0 to any port 443    \# HTTPS (future)  
ufw allow in on wlan0 to any port 3000   \# Signal K  
ufw allow in on wlan0 to any port 1880   \# Node-RED  
ufw allow in on wlan0 to any port 554    \# RTSP (camera)  
  
\# Block incoming on ethernet (eth0) for security  
ufw deny in on eth0 to any port 22       \# SSH
```

**mDNS (Avahi)**:

- Hostname: `d3kos.local`

- Service: `\_http.\_tcp` (Web interface)

- Service: `\_signalk.\_tcp` (Signal K server)

- Service: `\_nodered.\_tcp` (Node-RED dashboard)

**Access URLs**:

- Main menu: `http://d3kos.local` or `http://10.42.0.1`

- Dashboard: `http://d3kos.local:1880/dashboard`

- Signal K: `http://d3kos.local:3000`

- Camera: `rtsp://d3kos.local:554/camera`


## 8. DATA MANAGEMENT

### 8.1 Data Storage Locations

| Data Type | Location | Format | Retention |
| - | - | - | - |
| Onboarding Config | `/opt/d3kos/config/onboarding.json` | JSON | Permanent |
| Engine Baseline | `/opt/d3kos/config/benchmark-results.json` | JSON | Permanent |
| License Info | `/opt/d3kos/config/license.json` | JSON | Permanent |
| Reset Counter | `/opt/d3kos/state/onboarding-reset-count.json` | JSON | Permanent |
| Pi Health Status | `/opt/d3kos/state/pi-health-status.json` | JSON | Overwrite |
| Boat Log | `/opt/d3kos/data/boat-log.txt` | Text | 30d (Tier 0), ∞ (Tier 2+) |
| Camera Recordings | `/opt/d3kos/data/camera/` | MP4 | Until disk full |
| Historical Data | `/opt/d3kos/data/historical.db` | SQLite | 90 days |
| Voice Recordings | `/opt/d3kos/data/voice/` | WAV | Temp (delete after STT) |


### 8.2 Backup & Restore

**Automated Backup** (Daily at 2 AM):

```
\#!/bin/bash  
\# /opt/d3kos/scripts/backup.sh  
  
BACKUP\_DIR="/opt/d3kos/backups"  
DATE=$(date +%Y%m%d)  
  
\# Create backup directory  
mkdir -p $BACKUP\_DIR  
  
\# Backup configuration files  
tar -czf $BACKUP\_DIR/config\_$DATE.tar.gz /opt/d3kos/config/  
  
\# Backup state files  
tar -czf $BACKUP\_DIR/state\_$DATE.tar.gz /opt/d3kos/state/  
  
\# Backup boat log  
cp /opt/d3kos/data/boat-log.txt $BACKUP\_DIR/boat-log\_$DATE.txt  
  
\# Delete backups older than 30 days  
find $BACKUP\_DIR -type f -mtime +30 -delete  
  
echo "Backup completed: $DATE"
```

**Restore Process**:

```
\#!/bin/bash  
\# /opt/d3kos/scripts/restore.sh  
  
BACKUP\_FILE=$1  
  
if \[ -z "$BACKUP\_FILE" \]; then  
  echo "Usage: restore.sh \<backup\_file.tar.gz\>"  
  exit 1  
fi  
  
\# Stop services  
sudo systemctl stop signalk nodered  
  
\# Extract backup  
tar -xzf $BACKUP\_FILE -C /  
  
\# Restart services  
sudo systemctl start signalk nodered  
  
echo "Restore completed from: $BACKUP\_FILE"
```

### 8.3 Data Export & Central Database Sync

**Tier Requirement**: Tier 1, 2, and 3 only (Tier 0 does NOT have export capability)

**Purpose**: Export all boat data in format suitable for central database import, enabling cloud sync, mobile app features, fleet management, and remote monitoring.


#### 8.3.1 Export Data Categories

All exports must include:

- **installation\_id** (16-char hex from `/opt/d3kos/config/license.json`)

- **export\_timestamp** (ISO-8601 format)

- **tier** (1, 2, or 3)

- **format\_version** (e.g., "1.0")

**Data Types Requiring Export**:

1. **Engine Benchmark Data**

   - Baseline RPM values (idle, cruise, max)

   - Oil pressure ranges (min, normal, max)

   - Coolant temperature ranges

   - Performance metrics

   - Anomaly thresholds

   - Last benchmark timestamp

2. **Boatlog Entries**

   - Entry ID (unique per entry)

   - Timestamp

   - Entry type (voice, text, auto, weather)

   - Content/transcription

   - GPS coordinates (latitude, longitude)

   - Weather conditions (if weather auto-log)

3. **Marine Vision Captures** (Metadata Only - NO Files)

   - Installation ID (system\_id)

   - Capture ID (unique per photo)

   - Timestamp (when photo was taken)

   - File size (bytes)

   - File path (local storage path on Pi)

   - Image metadata (resolution, format)

   - Detection results (species, confidence score)

   - Size measurements (if applicable)

   - Legal compliance (size/bag limit check)

   - GPS coordinates

   - **NOTE:** Actual image files are NOT exported to central database. Files are transferred via Tier 1/2/3 mobile app only.

4. **Marine Vision Snapshots** (Metadata Only - NO Files)

   - Installation ID (system\_id)

   - Snapshot ID (unique per snapshot)

   - Timestamp (when snapshot was taken)

   - File size (bytes)

   - File path (local storage path on Pi)

   - Camera orientation (degrees)

   - Detection events (object type, count, distance estimate)

   - GPS coordinates

   - **NOTE:** Actual video/snapshot files are NOT exported to central database. Files are transferred via Tier 1/2/3 mobile app only.

5. **QR Code Data**

   - Installation UUID

   - Pairing token (one-time use)

   - Generation timestamp

   - Tier level at generation

   - API endpoint

6. **Settings Configuration**

   - User preferences (voice enabled, camera enabled, etc.)

   - Feature toggles

   - Network configuration (WiFi SSID, AP mode)

   - Alert thresholds (oil pressure min, temp max, etc.)

7. **System Alerts**

   - Alert ID (unique per alert)

   - Timestamp (when alert triggered)

   - Alert type (health, anomaly, system, network)

   - Severity level (info, warning, critical)

   - Message/description

   - Resolved status (true/false)

   - Resolved timestamp (if resolved)

   - Related sensor values

8. **Onboarding/Initial Setup Configuration**

   - Installation ID (system\_id)

   - All Initial Setup wizard answers (20 steps)

   - Boat information (manufacturer, year, model, chartplotter)

   - Engine information (make, model, year, cylinders, displacement, power, compression, RPM ranges, type)

   - Regional settings (tank sensor standard, engine position)

   - Reset counter (resets\_used, resets\_remaining)

   - Max resets allowed (10 for Tier 0/1, unlimited for Tier 3)

   - Last reset timestamp

   - Completion status and timestamp

   - **Purpose:** Enables Tier 1 mobile app to restore configuration after d3kOS image update

9. **Telemetry & Analytics** (Background Collection)

   - **Tier Requirement:** Tier 1, 2, and 3 only (user consent required)

   - **Collection Method:** Automatic background service (`d3kos-telemetry.service`)

   - **Privacy:** Anonymized, no personally identifiable information

   - **Retention:** 30 days local storage, unlimited in central database

   - **User Control:** Can disable via Settings → Privacy → Telemetry

**System Performance Metrics:**

   - Boot time (power-on to fully operational, seconds)

   - Memory usage (RAM consumption: average MB, peak MB)

   - CPU usage patterns (average %, peak %, idle %)

   - Network connectivity (WiFi/ethernet uptime %, latency ms)

   - Error/crash logs (count, frequency, error types)

   - System uptime between reboots (hours)

   - Battery level (if applicable - future UPS integration)

   - Storage usage (SD card usage %, growth rate)

   - Service restart counts (per service: d3kos-voice, d3kos-ai-api, etc.)

**User Interaction Data:**

   - Menu navigation patterns (click counts per menu/button)

   - Feature usage frequency (which features used most/least)

   - User flow paths (which menus lead to which actions)

   - Abandoned actions (started but not completed, count)

   - Settings changes (frequency and types)

   - Voice command success/failure rates (percentage)

   - Time spent per page/screen (average session duration per page)

   - Onboarding completion time (first boot to wizard done, minutes)

**AI Assistance Metrics:**

   - Number of AI queries per session (total, average per session)

   - AI response time/latency (average ms, p95 ms, p99 ms)

   - Query types/categories (simple patterns vs complex, onboard vs online)

   - Provider usage distribution (OpenRouter vs onboard rules, percentage)

   - Cache hit rate (Signal K data caching effectiveness, percentage)

   - Follow-up question patterns (chains of related queries, count)

   - Query abandonment rate (user closes page before response, percentage)

**Device & Environment Data:**

   - Connected device count (other devices on 10.42.0.0/24 network)

   - Camera connection status and uptime (percentage)

   - Time of day usage patterns (hourly heatmap: 00-06, 06-12, 12-18, 18-24)

   - d3kOS software version (e.g., "2.9")

   - Raspberry Pi model and RAM size (e.g., "Pi 4B 8GB")

   - SD card size and type (GB)

   - Network mode (AP mode vs client mode, WiFi vs ethernet)

**Business Intelligence Metrics:**

   - Days since installation (installation age)

   - Days since last use (user retention indicator)

   - First-time vs returning user patterns

   - Feature adoption rate over time

   - Session duration and frequency (daily, weekly, monthly averages)

   - Current tier and tier upgrade history (0→1, 1→2, 2→3)

   - Reset counter trends (approaching limit? retention risk)

   - Retention score (calculated metric: 0.0-1.0)

**Collection Service:**

   - Service: `d3kos-telemetry.service` (systemd)

   - Frequency: Every 5 minutes (collects metrics)

   - Local storage: `/opt/d3kos/data/telemetry/telemetry.db` (SQLite)

   - Export frequency: Daily export (Tier 2+) or manual export (Tier 1)

   - Aggregation: Metrics aggregated to hourly/daily summaries before export


#### 8.3.2 Export File Format

**Primary Format**: JSON (structured for database import)

**File Location**: `/opt/d3kos/data/exports/`

**File Naming Convention**: `d3kos\_export\_\{installation\_id\}\_\{timestamp\}.json`

**Example**: `d3kos\_export\_abc123def456\_20260216143000.json`

**JSON Structure**:

```
\{  
  "export\_metadata": \{  
    "installation\_id": "abc123def456",  
    "export\_timestamp": "2026-02-16T14:30:00.000Z",  
    "tier": 2,  
    "format\_version": "1.0",  
    "export\_type": "full",  
    "software\_version": "2.7.0"  
  \},  
  "boat\_info": \{  
    "manufacturer": "Sea Ray",  
    "year": 2018,  
    "model": "Sundancer 320",  
    "chartplotter": "Garmin GPSMAP 7412xsv",  
    "engine\_make": "Mercury",  
    "engine\_model": "8.2L Mag HO",  
    "engine\_year": 2018,  
    "engine\_position": "single"  
  \},  
  "benchmark\_data": \{  
    "baseline\_rpm": \{  
      "idle": 700,  
      "cruise": 3200,  
      "max": 4800  
    \},  
    "oil\_pressure": \{  
      "min": 10,  
      "normal": 45,  
      "max": 65  
    \},  
    "coolant\_temp": \{  
      "min": 160,  
      "normal": 180,  
      "max": 195  
    \},  
    "last\_benchmark": "2026-02-10T10:00:00.000Z",  
    "benchmark\_count": 3  
  \},  
  "boatlog\_entries": \[  
    \{  
      "entry\_id": "log\_20260216\_143000\_001",  
      "timestamp": "2026-02-16T14:30:00.000Z",  
      "type": "voice",  
      "content": "Engine running smooth, heading to marina",  
      "gps": \{  
        "latitude": 43.6817,  
        "longitude": -79.5214  
      \},  
      "weather": null  
    \},  
    \{  
      "entry\_id": "log\_20260216\_150000\_002",  
      "timestamp": "2026-02-16T15:00:00.000Z",  
      "type": "weather\_auto",  
      "content": "Wind: 12 kts NW, Waves: 0.5m, Temp: 22°C",  
      "gps": \{  
        "latitude": 43.6850,  
        "longitude": -79.5300  
      \},  
      "weather": \{  
        "wind\_speed": 12,  
        "wind\_direction": "NW",  
        "wave\_height": 0.5,  
        "temperature": 22  
      \}  
    \}  
  \],  
  "marine\_vision\_captures": \[  
    \{  
      "installation\_id": "abc123def456",  
      "capture\_id": "capture\_20260216\_120000\_001",  
      "timestamp": "2026-02-16T12:00:00.000Z",  
      "file\_size\_bytes": 524288,  
      "file\_path\_local": "/home/d3kos/camera-recordings/captures/capture\_20260216\_120000\_001.jpg",  
      "resolution": "1920x1080",  
      "format": "JPEG",  
      "species": "Largemouth Bass",  
      "confidence": 0.92,  
      "size\_cm": 38,  
      "legal\_size": true,  
      "bag\_limit\_check": "within\_limit",  
      "gps": \{  
        "latitude": 43.6817,  
        "longitude": -79.5214  
      \}  
    \}  
  \],  
  "marine\_vision\_snapshots": \[  
    \{  
      "installation\_id": "abc123def456",  
      "snapshot\_id": "snapshot\_20260216\_130000\_001",  
      "timestamp": "2026-02-16T13:00:00.000Z",  
      "file\_size\_bytes": 102400,  
      "file\_path\_local": "/home/d3kos/camera-recordings/snapshots/snapshot\_20260216\_130000\_001.jpg",  
      "camera\_orientation": 45,  
      "detection\_events": \[  
        \{  
          "object\_type": "boat",  
          "count": 1,  
          "distance\_estimate": 150  
        \}  
      \],  
      "gps": \{  
        "latitude": 43.6830,  
        "longitude": -79.5250  
      \}  
    \}  
  \],  
  "qr\_code\_data": \{  
    "installation\_uuid": "550e8400-e29b-41d4-a716-446655440000",  
    "pairing\_token": "TOKEN\_1\_TIME\_USE\_XYZ",  
    "generation\_timestamp": "2026-02-16T10:00:00.000Z",  
    "tier": 2,  
    "api\_endpoint": "https://d3kos-cloud/api/v1"  
  \},  
  "settings": \{  
    "voice\_enabled": true,  
    "camera\_enabled": true,  
    "auto\_logging": true,  
    "wifi\_ssid": "d3kOS",  
    "alert\_thresholds": \{  
      "oil\_pressure\_min": 10,  
      "coolant\_temp\_max": 195,  
      "rpm\_max": 5000,  
      "voltage\_min": 12.0  
    \}  
  \},  
  "onboarding\_config": \{  
    "installation\_id": "abc123def456",  
    "completed": true,  
    "completion\_timestamp": "2026-02-10T10:00:00.000Z",  
    "reset\_count": 2,  
    "max\_resets": 10,  
    "resets\_remaining": 8,  
    "last\_reset\_timestamp": "2026-02-10T10:00:00.000Z",  
    "wizard\_answers": \{  
      "step\_0": "Welcome",  
      "step\_1": "Sea Ray",  
      "step\_2": 2018,  
      "step\_3": "Sundancer 320",  
      "step\_4": "Garmin GPSMAP 7412xsv",  
      "step\_5": "Mercury",  
      "step\_6": "8.2L Mag HO",  
      "step\_7": 2018,  
      "step\_8": 8,  
      "step\_9": "8.2",  
      "step\_10": "425",  
      "step\_11": "9.0:1",  
      "step\_12": 700,  
      "step\_13": 4800,  
      "step\_14": "gasoline",  
      "step\_15": "North America",  
      "step\_16": "single"  
    \}  
  \},  
  "alerts": \[  
    \{  
      "alert\_id": "alert\_20260216\_100000\_001",  
      "timestamp": "2026-02-16T10:00:00.000Z",  
      "type": "anomaly",  
      "severity": "warning",  
      "message": "Oil pressure below normal range (8 PSI)",  
      "sensor\_values": \{  
        "oil\_pressure": 8,  
        "rpm": 3200,  
        "coolant\_temp": 175  
      \},  
      "resolved": true,  
      "resolved\_timestamp": "2026-02-16T10:15:00.000Z"  
    \},  
    \{  
      "alert\_id": "alert\_20260216\_110000\_002",  
      "timestamp": "2026-02-16T11:00:00.000Z",  
      "type": "system",  
      "severity": "info",  
      "message": "System reboot completed",  
      "resolved": true,  
      "resolved\_timestamp": "2026-02-16T11:00:05.000Z"  
    \}  
  \],  
  "telemetry\_data": \{  
    "collection\_period": \{  
      "start": "2026-02-15T00:00:00.000Z",  
      "end": "2026-02-16T14:30:00.000Z",  
      "duration\_hours": 38.5  
    \},  
    "system\_performance": \{  
      "boot\_time\_seconds": 45.2,  
      "average\_ram\_usage\_mb": 1250,  
      "peak\_ram\_usage\_mb": 1850,  
      "average\_cpu\_percent": 15.3,  
      "peak\_cpu\_percent": 78.5,  
      "network\_uptime\_percent": 98.2,  
      "average\_latency\_ms": 12,  
      "error\_count": 3,  
      "crash\_count": 0,  
      "system\_uptime\_hours": 168.5,  
      "reboot\_count": 2,  
      "storage\_used\_percent": 85,  
      "service\_restarts": \{  
        "d3kos-voice": 0,  
        "d3kos-ai-api": 1,  
        "d3kos-camera-stream": 2  
      \}  
    \},  
    "user\_interaction": \{  
      "total\_sessions": 15,  
      "average\_session\_duration\_minutes": 8.5,  
      "menu\_clicks": \{  
        "dashboard": 45,  
        "boatlog": 12,  
        "navigation": 8,  
        "helm": 22,  
        "weather": 10,  
        "settings": 5,  
        "ai\_assistant": 18  
      \},  
      "feature\_usage": \{  
        "voice\_commands": 5,  
        "ai\_queries": 23,  
        "camera\_access": 8,  
        "manual\_upload": 2  
      \},  
      "abandoned\_actions": 3,  
      "settings\_changes": 4,  
      "voice\_command\_success\_rate": 0.80  
    \},  
    "ai\_assistance": \{  
      "total\_queries": 23,  
      "average\_response\_time\_ms": 850,  
      "p95\_response\_time\_ms": 18500,  
      "query\_types": \{  
        "simple\_patterns": 18,  
        "complex\_online": 5  
      \},  
      "provider\_usage": \{  
        "rules": 18,  
        "openrouter": 5  
      \},  
      "cache\_hit\_rate": 0.78,  
      "follow\_up\_chains": 4,  
      "query\_abandonment\_rate": 0.04  
    \},  
    "device\_environment": \{  
      "connected\_devices\_count": 3,  
      "camera\_uptime\_percent": 95.5,  
      "usage\_by\_hour": \{  
        "00-06": 0,  
        "06-12": 5,  
        "12-18": 8,  
        "18-24": 2  
      \},  
      "software\_version": "2.9",  
      "hardware": \{  
        "model": "Raspberry Pi 4B",  
        "ram\_gb": 8,  
        "sd\_card\_gb": 32  
      \},  
      "network\_mode": "ap"  
    \},  
    "business\_intelligence": \{  
      "days\_since\_installation": 6,  
      "days\_since\_last\_use": 0,  
      "current\_tier": 1,  
      "tier\_upgrade\_history": \[  
        \{  
          "from": 0,  
          "to": 1,  
          "timestamp": "2026-02-11T10:00:00.000Z"  
        \}  
      \],  
      "retention\_score": 0.92  
    \}  
  \}  
\}
```


#### 8.3.3 Export Triggers

**1. Manual Export** (User-initiated)

**Location**: Settings → Data Management → Export All Data

**Process**:

1. User taps "Export All Data Now" button

2. System collects all data from databases and config files

3. Generates JSON export file with timestamp

4. Saves to `/opt/d3kos/data/exports/`

5. Adds to export queue (`export\_queue.json`)

6. Attempts immediate upload to central database

7. Displays result notification

**UI Feedback**:

- "Exporting data..." (spinner)

- "Export complete. Uploading to cloud..." (progress)

- "✓ Data synced successfully" (green, 3 seconds)

- "✗ Upload failed. Will retry automatically." (red, 5 seconds)


**2. Automatic Export on Boot**

**Process**:

1. System boots and services start

2. Export service (`d3kos-export.service`) runs after network is online

3. Check for pending exports in `/opt/d3kos/data/exports/export\_queue.json`

4. If pending exports exist:

   - Check internet connectivity

   - Attempt upload to central database

   - Retry failed uploads (max 3 attempts)

   - Mark successful uploads in `export\_history.json`

5. No user notification (silent background sync)

**Service Configuration**:

```
\[Unit\]  
Description=d3kOS Data Export Service  
After=network-online.target  
  
\[Service\]  
Type=oneshot  
ExecStart=/opt/d3kos/services/export/export-manager.js --auto  
User=d3kos  
RemainAfterExit=no  
  
\[Install\]  
WantedBy=multi-user.target
```


**3. Scheduled Export** (Tier 2+ only)

**Schedule**: Daily at 3:00 AM (if online)

**Process**:

1. Cron job or systemd timer triggers export

2. Incremental export (only new data since last successful export)

3. Background process, no user notification

4. Automatic upload attempt

**Cron Configuration**:

```
\# /etc/cron.d/d3kos-export  
0 3 \* \* \* d3kos /opt/d3kos/services/export/export-manager.js --scheduled
```


#### 8.3.4 Export Queue System

**Queue File**: `/opt/d3kos/data/exports/export\_queue.json`

**Structure**:

```
\{  
  "pending\_exports": \[  
    \{  
      "export\_id": "export\_20260216\_143000",  
      "file\_path": "/opt/d3kos/data/exports/d3kos\_export\_abc123def456\_20260216143000.json",  
      "created": "2026-02-16T14:30:00.000Z",  
      "upload\_attempts": 0,  
      "status": "pending",  
      "last\_attempt": null,  
      "error\_message": null  
    \},  
    \{  
      "export\_id": "export\_20260215\_030000",  
      "file\_path": "/opt/d3kos/data/exports/d3kos\_export\_abc123def456\_20260215030000.json",  
      "created": "2026-02-15T03:00:00.000Z",  
      "upload\_attempts": 2,  
      "status": "retrying",  
      "last\_attempt": "2026-02-16T10:00:00.000Z",  
      "error\_message": "Network timeout"  
    \}  
  \]  
\}
```

**Upload Process**:

1. Check internet connectivity (`ping 8.8.8.8` or HTTP HEAD request)

2. Read export JSON file

3. POST to `https://d3kos-cloud/api/v1/data/import`

4. Send JSON metadata only (NO media files - those are transferred via mobile app)

5. Wait for 200 OK response with confirmation ID

6. Update queue status to "completed"

7. Move file to `/opt/d3kos/data/exports/archive/`

8. Log success in `export\_history.json`

**Retry Logic**:

- **Attempt 1**: Immediate (on boot, manual trigger, or scheduled time)

- **Attempt 2**: 5 minutes after first failure

- **Attempt 3**: 15 minutes after second failure

- **After 3 failures**: Mark as "failed", require manual retry via Settings page

**Error Handling**:

- Network timeout: Retry

- 4xx HTTP error (bad request): Mark as failed, notify user

- 5xx HTTP error (server error): Retry

- No internet: Skip, retry on next boot


#### 8.3.5 Central Database API

**Base URL**: `https://d3kos-cloud/api/v1`

**Authentication**: Installation ID in header


**POST /data/import** - Import full export to central database

**NOTE:** This endpoint receives JSON metadata only. Marine vision media files (photos/videos) are NOT uploaded here. Actual media files are transferred via Tier 1/2/3 mobile app.

**Headers**:

```
Authorization: Bearer abc123def456  
Content-Type: application/json
```

**Body**: Full JSON export object (see Section 8.3.2 for structure)

**Response** (200 OK):

```
\{  
  "status": "success",  
  "import\_id": "import\_550e8400e29b41d4",  
  "records\_imported": \{  
    "boatlog\_entries": 12,  
    "marine\_vision\_captures": 3,  
    "alerts": 5,  
    "settings": 1,  
    "benchmark\_data": 1  
  \},  
  "timestamp": "2026-02-16T14:30:15.000Z",  
  "storage\_used\_mb": 5.2  
\}
```

**Response** (400 Bad Request):

```
\{  
  "status": "error",  
  "error\_code": "INVALID\_FORMAT",  
  "message": "Export format\_version not supported",  
  "required\_version": "1.0"  
\}
```

**Response** (401 Unauthorized):

```
\{  
  "status": "error",  
  "error\_code": "INVALID\_INSTALLATION\_ID",  
  "message": "Installation ID not found or tier insufficient"  
\}
```


**GET /data/export/status** - Check export sync status

**Query Parameters**:

- `installation\_id`: Installation ID (required)

**Response**:

```
\{  
  "installation\_id": "abc123def456",  
  "tier": 2,  
  "last\_export": "2026-02-16T14:30:00.000Z",  
  "records\_synced": 1247,  
  "pending\_records": 3,  
  "storage\_used\_mb": 142.5,  
  "next\_scheduled\_export": "2026-02-17T03:00:00.000Z"  
\}
```


#### 8.3.6 UI Implementation

**Settings → Data Management Page**

**File**: `/var/www/html/settings-data.html`

**Layout**:

```
┌────────────────────────────────────────────────┐  
│ ← Settings          Data Management            │  
├────────────────────────────────────────────────┤  
│                                                 │  
│ Export & Cloud Sync (Tier 2)                   │  
│                                                 │  
│ Last Export: Feb 16, 2026 2:30 PM              │  
│ Status: ✓ Synced to cloud                      │  
│ Records synced: 1,247                           │  
│                                                 │  
│ ┌──────────────────────────────────────────┐  │  
│ │   \[Export All Data Now\]                  │  │  
│ └──────────────────────────────────────────┘  │  
│                                                 │  
│ Export History:                                 │  
│ • Feb 16, 2026 2:30 PM - 47 records ✓          │  
│ • Feb 15, 2026 3:00 AM - 23 records ✓          │  
│ • Feb 14, 2026 3:00 AM - 15 records ✓          │  
│ • Feb 13, 2026 3:00 AM - Failed (retry)        │  
│                                                 │  
│ Pending Uploads: 0                              │  
│ Storage Used: 142.5 MB                          │  
│                                                 │  
│ ┌──────────────────────────────────────────┐  │  
│ │   \[View Export Files\]                    │  │  
│ │   \[Retry Failed Exports\]                 │  │  
│ │   \[Clear Export Archive\]                 │  │  
│ └──────────────────────────────────────────┘  │  
│                                                 │  
│ Automatic Export: ✓ Enabled (Daily 3:00 AM)    │  
│                                                 │  
└────────────────────────────────────────────────┘
```

**Boot-time Notification** (only if export fails):

- Small banner at top: "Unable to sync data to cloud. Will retry later."

- Auto-dismiss after 5 seconds

- Tap for details


#### 8.3.7 Storage Management

**Directory Structure**:

```
/opt/d3kos/data/exports/  
├── export\_queue.json           \# Pending uploads queue  
├── export\_history.json         \# Successful uploads log (last 100)  
├── d3kos\_export\_\*.json         \# Current pending export files  
└── archive/                    \# Completed/failed exports  
    ├── 2026-02/  
    │   ├── d3kos\_export\_abc123def456\_20260216143000.json  
    │   └── d3kos\_export\_abc123def456\_20260215030000.json  
    └── 2026-01/  
        └── d3kos\_export\_\*.json
```

**Cleanup Policy**:

- **Archive exports**: Delete after 30 days

- **Failed exports**: Delete after 7 days (user notified first)

- **Successful exports**: Move to archive immediately after upload confirmation

- **Export queue**: Maintain last 50 entries, purge older

**Disk Space Management**:

- If `/opt/d3kos/data/` exceeds 90% full:

  - Delete oldest archived exports first

  - Alert user: "Storage nearly full. Older exports deleted."

- Reserve 500MB minimum free space

**Marine Vision Media File Management**:

**IMPORTANT:** Marine vision media files (photos, videos, snapshots) are NOT exported to the central database. Only metadata is exported. Actual media files are transferred via the Tier 1/2/3 mobile app.

**Media Storage Locations:**

- Captures (photos): `/home/d3kos/camera-recordings/captures/`

- Snapshots: `/home/d3kos/camera-recordings/snapshots/`

- Recordings (videos): `/home/d3kos/camera-recordings/`

**Automatic Deletion Policy:**

- **Default:** Media files are deleted after 7 days

- **Low Storage:** Files may be deleted sooner if storage exceeds 90% full

- **Priority:** Oldest files deleted first (by timestamp)

- **Notification:** User is notified when automatic deletion occurs

**Storage Management Service:**

- Service: `d3kos-media-cleanup.service`

- Schedule: Daily at 4:00 AM (systemd timer)

- Cleanup Logic:

  1. Files older than 7 days → Delete

  2. If storage still \> 90% full → Delete files older than 5 days

  3. If storage still \> 90% full → Delete files older than 3 days

  4. If storage still \> 95% full → Alert user (critical storage warning)

**Systemd Timer Configuration:**

```
\# /etc/systemd/system/d3kos-media-cleanup.timer  
\[Unit\]  
Description=d3kOS Media Cleanup Timer  
Requires=d3kos-media-cleanup.service  
  
\[Timer\]  
OnCalendar=daily  
Persistent=true  
Unit=d3kos-media-cleanup.service  
  
\[Install\]  
WantedBy=timers.target
```

**Cleanup Service:**

```
\#!/bin/bash  
\# /opt/d3kos/scripts/media-cleanup.sh  
  
CAPTURES\_DIR="/home/d3kos/camera-recordings/captures"  
SNAPSHOTS\_DIR="/home/d3kos/camera-recordings/snapshots"  
RECORDINGS\_DIR="/home/d3kos/camera-recordings"  
  
\# Get storage usage percentage  
STORAGE\_USAGE=$(df /home/d3kos | tail -1 | awk '\{print $5\}' | sed 's/%//')  
  
\# Function to delete files older than N days  
delete\_old\_files() \{  
  local dir=$1  
  local days=$2  
  find "$dir" -type f -mtime +$days -delete  
  echo "Deleted files older than $days days in $dir"  
\}  
  
\# Default cleanup: 7 days  
delete\_old\_files "$CAPTURES\_DIR" 7  
delete\_old\_files "$SNAPSHOTS\_DIR" 7  
delete\_old\_files "$RECORDINGS\_DIR" 7  
  
\# If storage \> 90%, more aggressive cleanup  
if \[ $STORAGE\_USAGE -gt 90 \]; then  
  logger "d3kOS: Storage at $\{STORAGE\_USAGE\}%, deleting files older than 5 days"  
  delete\_old\_files "$CAPTURES\_DIR" 5  
  delete\_old\_files "$SNAPSHOTS\_DIR" 5  
  delete\_old\_files "$RECORDINGS\_DIR" 5  
  
  \# Notify user  
  echo "Media files older than 5 days deleted due to limited storage ($\{STORAGE\_USAGE\}% full)." \> /tmp/d3kos-media-cleanup-notification.txt  
fi  
  
\# Update storage usage  
STORAGE\_USAGE=$(df /home/d3kos | tail -1 | awk '\{print $5\}' | sed 's/%//')  
  
\# If still \> 90%, delete 3-day-old files  
if \[ $STORAGE\_USAGE -gt 90 \]; then  
  logger "d3kOS: Storage still at $\{STORAGE\_USAGE\}%, deleting files older than 3 days"  
  delete\_old\_files "$CAPTURES\_DIR" 3  
  delete\_old\_files "$SNAPSHOTS\_DIR" 3  
  delete\_old\_files "$RECORDINGS\_DIR" 3  
  
  \# Notify user  
  echo "Media files older than 3 days deleted due to limited storage ($\{STORAGE\_USAGE\}% full)." \> /tmp/d3kos-media-cleanup-notification.txt  
fi  
  
\# Update storage usage again  
STORAGE\_USAGE=$(df /home/d3kos | tail -1 | awk '\{print $5\}' | sed 's/%//')  
  
\# If still \> 95%, critical warning  
if \[ $STORAGE\_USAGE -gt 95 \]; then  
  logger "d3kOS: CRITICAL - Storage at $\{STORAGE\_USAGE\}%"  
  echo "CRITICAL: Storage critically low ($\{STORAGE\_USAGE\}% full). Please transfer media to mobile app or expand SD card." \> /tmp/d3kos-storage-critical.txt  
fi
```

**User Notifications:**

- **Daily cleanup (7 days):** No notification (silent cleanup)

- **Low storage cleanup (5/3 days):** Yellow banner: "Media files older than X days deleted due to limited storage (XX% full)."

- **Critical storage (\>95%):** Red banner: "CRITICAL: Storage critically low. Please transfer media to mobile app or expand SD card."

- Notifications displayed on main menu for 10 seconds

**Mobile App Transfer:**

- Tier 1/2/3 mobile app can browse and download media files from Pi

- App connects via local network (WiFi) using installation\_id authentication

- HTTPS file transfer (GET `/media/captures/\{capture\_id\}.jpg`)

- After successful transfer to mobile app, user can manually delete from Pi via app

- App shows storage usage and recommends cleanup

**Storage Expansion Recommendations:**

- **Minimum:** 32GB SD card (current testing setup)

- **Recommended:** 128GB SD card (8-10 days of continuous recording)

- **Optimal:** 256GB SD card (15-20 days of continuous recording)

- User can adjust retention period in Settings → Data Management (3, 7, 14, 30 days)


#### 8.3.8 Export Service Implementation

**Service**: `/opt/d3kos/services/export/export-manager.js`

**Key Functions**:

```
// Collect all data for export  
async function collectExportData() \{  
  const license = JSON.parse(fs.readFileSync('/opt/d3kos/config/license.json'));  
  
  return \{  
    export\_metadata: \{  
      installation\_id: license.installation\_id,  
      export\_timestamp: new Date().toISOString(),  
      tier: license.tier,  
      format\_version: "1.0",  
      export\_type: "full"  
    \},  
    boat\_info: getBoatInfo(),  
    benchmark\_data: getBenchmarkData(),  
    boatlog\_entries: getBoatlogEntries(),  
    marine\_vision\_captures: getMarineVisionCaptures(),  
    marine\_vision\_snapshots: getMarineVisionSnapshots(),  
    qr\_code\_data: getQRCodeData(),  
    settings: getSettings(),  
    alerts: getAlerts()  
  \};  
\}  
  
// Create export file  
async function createExportFile() \{  
  const data = await collectExportData();  
  const filename = \`d3kos\_export\_$\{data.export\_metadata.installation\_id\}\_$\{Date.now()\}.json\`;  
  const filepath = \`/opt/d3kos/data/exports/$\{filename\}\`;  
  
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));  
  
  return \{ filename, filepath \};  
\}  
  
// Upload to central database (JSON metadata only - NO media files)  
async function uploadExport(filepath) \{  
  const exportData = JSON.parse(fs.readFileSync(filepath));  
  
  // NOTE: Marine vision media files (photos/videos) are NOT uploaded here  
  // Only metadata is sent to central database  
  // Actual media files are transferred via Tier 1/2/3 mobile app  
  
  const response = await fetch('https://d3kos-cloud/api/v1/data/import', \{  
    method: 'POST',  
    headers: \{  
      'Authorization': \`Bearer $\{exportData.export\_metadata.installation\_id\}\`,  
      'Content-Type': 'application/json'  
    \},  
    body: JSON.stringify(exportData)  
  \});  
  
  if (response.ok) \{  
    const result = await response.json();  
    return \{ success: true, result \};  
  \} else \{  
    const error = await response.json();  
    return \{ success: false, error \};  
  \}  
\}  
  
// Add to export queue  
async function queueExport(filepath) \{  
  const queue = JSON.parse(fs.readFileSync('/opt/d3kos/data/exports/export\_queue.json'));  
  
  queue.pending\_exports.push(\{  
    export\_id: path.basename(filepath, '.json'),  
    file\_path: filepath,  
    created: new Date().toISOString(),  
    upload\_attempts: 0,  
    status: 'pending',  
    last\_attempt: null,  
    error\_message: null  
  \});  
  
  fs.writeFileSync('/opt/d3kos/data/exports/export\_queue.json', JSON.stringify(queue, null, 2));  
\}  
  
// Process export queue (run on boot)  
async function processQueue() \{  
  const queue = JSON.parse(fs.readFileSync('/opt/d3kos/data/exports/export\_queue.json'));  
  
  for (const exportItem of queue.pending\_exports) \{  
    if (exportItem.status === 'pending' || exportItem.status === 'retrying') \{  
      if (exportItem.upload\_attempts \< 3) \{  
        const result = await uploadExport(exportItem.file\_path);  
  
        if (result.success) \{  
          exportItem.status = 'completed';  
          archiveExport(exportItem.file\_path);  
          logExportHistory(exportItem, result.result);  
        \} else \{  
          exportItem.upload\_attempts++;  
          exportItem.last\_attempt = new Date().toISOString();  
          exportItem.error\_message = result.error.message;  
          exportItem.status = exportItem.upload\_attempts \< 3 ? 'retrying' : 'failed';  
        \}  
      \}  
    \}  
  \}  
  
  fs.writeFileSync('/opt/d3kos/data/exports/export\_queue.json', JSON.stringify(queue, null, 2));  
\}
```


## 9. SECURITY & LICENSING

### 9.1 Security Measures

**SSH Access**:

- Default: Disabled on first boot

- Enable via Main Menu: Settings → Enable SSH

- Strong password required (12+ chars, mixed case, numbers, symbols)

- Key-based authentication recommended

**Web Interface**:

- HTTP only on local network (10.42.0.x)

- HTTPS optional (requires certificate)

- No authentication for local access (trusted network)

- Authentication required for remote access (Tier 3, future)

**Firewall**:

- UFW enabled by default

- Allow: 80 (HTTP), 3000 (Signal K), 1880 (Node-RED), 554 (RTSP)

- Deny: 22 (SSH) on ethernet interface

- Rate limiting on HTTP endpoints

**Software Updates**:

- Auto-update disabled (manual update via image reflash)

- Security patches: Announced on GitHub

- Critical vulnerabilities: Immediate patch release

### 9.2 Licensing Enforcement

**Tier 0 Restrictions**:

- Reset counter: Hard limit at 10 resets

- Voice assistant: Disabled (service won't start)

- Camera: Disabled (UI buttons hidden)

**Tier Detection**:

- Run on boot: `/opt/d3kos/scripts/detect-tier.sh`

- Update license.json

- Enable/disable services based on tier

**No Phone-Home**:

- All tier detection is local (no cloud checks)

- No telemetry or analytics

- No license key validation servers


## 10. PERFORMANCE REQUIREMENTS

### 10.1 Boot Time

**Target**: \< 60 seconds from power-on to fully operational

**Optimization Strategies**:

1. **Systemd Parallel Boot**: Enable parallel service startup

2. **Remove Unnecessary Services**: Disable Bluetooth, printer services

3. **Preload Models**: Cache Vosk and Piper models in RAM

4. **Fast SD Card**: Use Class 10 A2 for faster I/O

5. **Reduce Boot Messages**: Quiet kernel boot

**Measurement**:

```
systemd-analyze  
systemd-analyze blame  
systemd-analyze critical-chain
```

### 10.2 Real-Time Performance

**Dashboard Update Frequency**:

- Engine metrics: 1 Hz (1000ms)

- Target latency: \< 100ms from Signal K to UI update

**Voice Response Time**:

- Wake word detection: \< 500ms

- STT transcription: \< 1 second

- Query classification: \< 50ms

- AI inference: 0.17s (rule-based, cached) OR 6-8s (OpenRouter)

- TTS generation: \< 500ms

- **Total**: 2-3 seconds (simple queries) OR 8-10 seconds (complex queries)

**Camera Latency**:

- RTSP stream: \< 500ms from camera to display

- Recording start: \< 1 second

### 10.3 Resource Usage

**CPU**:

- Idle: \< 10%

- Dashboard only: \< 20%

- Voice active: \< 50%

- Camera recording: \< 30%

- **Combined**: \< 70% sustained

**Memory**:

- Base OS: 500MB

- Signal K + Node-RED: 300MB

- Voice (PocketSphinx + Vosk + Piper): 350MB

- AI (rule-based + OpenRouter API calls): 50MB

- Camera + Marine Vision (YOLOv8n ONNX): 350MB

- **Total**: \< 1.6GB (8GB Pi recommended, 4GB minimum)

**Disk I/O**:

- Historical logging: \< 1 MB/min

- Camera recording: 10 MB/min @ 1080p

- Total writes: \< 100 MB/hour

**Network**:

- Signal K updates: \< 10 KB/sec

- Camera stream (local): 5 MB/sec @ 1080p

- Dashboard updates: \< 1 KB/sec

### 10.4 Storage Management

**Disk Usage Monitoring**:

```
function monitorDiskUsage() \{  
  setInterval(() =\> \{  
    const diskFree = getDiskFreePercent();  
      
    if (diskFree \< 15) \{  
      // Critical: Delete oldest logs  
      deleteOldestLogs(10);  
    \}  
      
    if (diskFree \< 18) \{  
      // Warning: Delete oldest camera recordings  
      deleteOldestRecordings(5);  
    \}  
      
    if (diskFree \< 20) \{  
      // Info: Notify user  
      showNotification('Disk space low (\<20%). Consider deleting old data.');  
    \}  
  \}, 60000); // Check every minute  
\}
```

**Auto-Cleanup Priorities**:

1. Temporary files (voice recordings)

2. Oldest camera recordings

3. Logs older than 90 days

4. Historical data older than 90 days


## 11. TESTING & QUALITY ASSURANCE

### 11.1 Hardware Testing Matrix

| Hardware | Test Case | Expected Result | Pass/Fail |
| - | - | - | - |
| Pi 4 (4GB) | Boot time | \< 60 seconds |  |
| Pi 4 (8GB) | Voice + Camera + Dashboard | CPU \< 70% |  |
| PiCAN-M | NMEA2000 data reception | All PGNs received |  |
| Touchscreen | Touch accuracy | \< 5px error |  |
| Touchscreen | On-screen keyboard | No overlap with content |  |
| USB GPS | Position accuracy | \< 10m error |  |
| USB AIS | AIS message parsing | All messages decoded |  |
| Anker S330 | Wake word detection | \> 95% accuracy |  |
| Reolink Camera | RTSP stream | \< 500ms latency |  |


### 11.2 Software Testing

**Functional Tests**:

1. Onboarding wizard completion (all 13 questions)

2. CX5106 DIP switch generation (verify accuracy)

3. Voice assistant wake word detection (100 trials)

4. Voice commands (test all supported commands)

5. Dashboard gauge updates (verify 1Hz refresh)

6. Engine anomaly detection (simulate anomalies)

7. Camera recording and playback

8. OpenCPN auto-install

**Integration Tests**:

1. Signal K → Node-RED → Dashboard (end-to-end data flow)

2. CAN0 → Signal K (NMEA2000 integration)

3. GPS → Signal K → OpenCPN (position data)

4. Voice → Actions → Feedback (voice control loop)

5. Camera → Storage → Playback (video pipeline)

**Performance Tests**:

1. Boot time (10 trials, average)

2. Voice response time (100 trials, average)

3. Dashboard update frequency (measure actual Hz)

4. CPU usage under load (stress test)

5. Memory usage over time (24-hour test)

6. Storage growth rate (1-week test)

**UI/UX Tests**:

1. AODA compliance validation (automated tools)

2. Color contrast testing (1000 nit screen)

3. Font size readability (arm's length test)

4. Button size and spacing (touch accuracy)

5. Keyboard overlap prevention (all pages)

6. Navigation flow (task completion time)

### 11.3 Acceptance Criteria

**Phase 1 (Core)**:

- [ ] Main menu loads in \< 5 seconds

- [ ] Onboarding wizard completes successfully

- [ ] All 13 questions collect valid data

- [ ] CX5106 DIP switches generate correctly

- [ ] Dashboard displays all gauges at 1Hz

- [ ] No AODA violations

**Phase 2 (Intelligence)**:

- [ ] Voice wake word detection \> 95% accuracy

- [ ] Voice commands execute correctly

- [ ] Engine anomaly detection catches real issues

- [ ] False positive rate \< 5%

- [ ] Pi health monitoring accurate

- [ ] Voice response time \< 2 seconds

**Phase 3 (Integration)**:

- [ ] Camera records and plays back correctly

- [ ] Storage management prevents disk full

- [ ] Boat log saves entries correctly

- [ ] OpenCPN installs and launches

- [ ] QR code generates and scans

- [ ] Licensing system enforces tiers

**Phase 4 (Polish)**:

- [ ] Touchscreen gestures work smoothly

- [ ] Performance tracking accurate

- [ ] All documentation complete

- [ ] Image builds successfully

- [ ] Flashing guide tested

- [ ] Zero critical bugs


## 12. DEPLOYMENT & DISTRIBUTION

### 12.1 Pre-Built Image

**Image Build Process**:

```
\#!/bin/bash  
\# /opt/d3kos/scripts/create-image.sh  
  
\# Install all dependencies  
./install-signalk.sh  
./install-nodered.sh  
./install-opencpn.sh  
./install-voice.sh  
./install-camera.sh  
  
\# Configure services  
./configure-autostart.sh  
./configure-network.sh  
./configure-touchscreen.sh  
  
\# Clean up  
rm -rf /var/log/\*  
rm -rf /tmp/\*  
rm -rf ~/.bash\_history  
  
\# Shrink filesystem  
./shrink-filesystem.sh  
  
\# Create image  
dd if=/dev/mmcblk0 of=/mnt/usb/d3kos-v1.0.3.img bs=4M status=progress  
  
\# Compress  
gzip -9 /mnt/usb/d3kos-v1.0.3.img  
  
\# Generate checksum  
sha256sum /mnt/usb/d3kos-v1.0.3.img.gz \> /mnt/usb/d3kos-v1.0.3.img.gz.sha256
```

**Image Hosting**:

- Platform: GitHub Releases

- File: `d3kos-v1.0.3.img.gz` (~4GB compressed)

- Checksum: `d3kos-v1.0.3.img.gz.sha256`

- Release notes: Changelog + known issues

### 12.2 Flashing Guide

**Recommended Tool**: Raspberry Pi Imager

**Steps**:

1. Download `d3kos-v1.0.3.img.gz` from GitHub

2. Verify checksum: `sha256sum -c d3kos-v1.0.3.img.gz.sha256`

3. Open Raspberry Pi Imager

4. Choose OS → Use custom → Select downloaded .img.gz

5. Choose storage → Select SD card

6. Write → Wait for completion

7. Insert SD card into Raspberry Pi

8. Power on → Wait for first boot (2-3 minutes)

9. Connect to WiFi "d3kOS" (password: d3kos-2026)

10. Open browser → `http://d3kos.local` or `http://10.42.0.1`

11. Complete Initial Setup wizard

### 12.3 First Boot Configuration

**Auto-Start Sequence**:

1. Expand filesystem to full SD card size

2. Generate unique installation ID

3. Create default license.json (Tier 0)

4. Start Signal K, Node-RED, gpsd

5. Launch Chromium in maximized mode

6. Display Initial Setup wizard

**First-Time Setup**:

- Onboarding wizard auto-launches

- User completes 13 questions

- CX5106 DIP switches displayed

- QR code generated

- Main menu loads


## 13. MAINTENANCE & SUPPORT

### 13.1 Logging

**Log Locations**:

- System logs: `/var/log/syslog`

- Signal K logs: `/home/signalk/.signalk/logs/`

- Node-RED logs: `/home/pi/.node-red/logs/`

- d3kOS logs: `/opt/d3kos/logs/`

**Log Rotation**:

```
\# /etc/logrotate.d/d3kos  
/opt/d3kos/logs/\*.log \{  
    daily  
    rotate 7  
    compress  
    missingok  
    notifempty  
\}
```

### 13.2 Troubleshooting

**Common Issues**:

1. **Boot fails** → Check SD card, reflash image

2. **No dashboard display** → Check Node-RED service: `sudo systemctl status nodered`

3. **No NMEA2000 data** → Check CAN0 interface: `ifconfig can0`

4. **Voice not responding** → Check microphone: `arecord -l`

5. **Camera not connecting** → Check RTSP URL and network

**Debug Mode**:

```
\# Enable verbose logging  
export HELM\_DEBUG=1  
sudo systemctl restart helm-\*
```

### 13.3 Updates

**Update Process**:

1. Download new image from GitHub

2. Backup configuration: `/opt/d3kos/scripts/backup.sh`

3. Flash new image to new SD card

4. Boot with new SD card

5. Restore configuration: `/opt/d3kos/scripts/restore.sh backup\_file.tar.gz`

**In-Place Updates** (Future):

```
\# /opt/d3kos/scripts/update.sh  
wget https://github.com/SkipperDon/d3kos/releases/latest/download/d3kos-update.tar.gz  
tar -xzf d3kos-update.tar.gz  
./install.sh  
sudo systemctl restart helm-\*
```

### 13.4 Community Support

**Resources**:

- GitHub Issues: Bug reports and feature requests

- GitHub Discussions: Q&A and community support

- Wiki: Detailed guides and tutorials

- Discord: Real-time community chat (future)

**Support Tiers**:

- Tier 0: Community support via GitHub

- Tier 2: Priority response on GitHub (48 hours)

- Tier 3: Direct email support (24 hours)


## 14. APPENDICES

### Appendix A: Hardware Bill of Materials

| Item | Part Number | Quantity | Estimated Cost (USD) |
| - | - | - | - |
| Raspberry Pi 4 Model B (4GB) | RPI4-MODBP-4GB | 1 | $55 |
| PiCAN-M HAT | PICAN-M | 1 | $60 |
| 10.1" Touchscreen (1920×1200) | Generic | 1 | $120 |
| USB GPS Receiver | VK-162 | 1 | $15 |
| USB AIS Receiver | dAISy | 1 | $80 |
| Anker PowerConf S330 | A3302 | 1 | $130 |
| SD Card (64GB Class 10 A2) | SanDisk Extreme | 1 | $12 |
| 12V to 5V DC Converter | Victron Orion-Tr | 1 | $35 |
| Micro-Fit Connector | Molex 43025-0400 | 1 | $5 |
| Enclosure | Custom 3D-printed | 1 | $20 |
| **Total** |  |  | **$532** |


### Appendix B: Software Dependencies

| Package | Version | License | Purpose |
| - | - | - | - |
| signalk-server | Latest | Apache 2.0 | Marine data aggregation |
| node-red | 3.x | Apache 2.0 | Automation and dashboard |
| gpsd | Latest | BSD | GPS data processing |
| sysstat | Latest | GPL | System performance monitoring (mpstat, iostat) |
| pocketsphinx | Latest | BSD | Wake word detection |
| vosk | 0.15 | Apache 2.0 | Speech-to-text |
| piper | Latest | MIT | Text-to-speech |
| opencpn | 5.8.x | GPL | Chart plotting |
| chromium | Latest | BSD | Web browser |
| touchegg | Latest | GPL | Gesture support |
| onboard | Latest | GPL | On-screen keyboard |


### Appendix C: PGN Mapping Reference

| PGN | Parameter | Signal K Path | Unit |
| - | - | - | - |
| 127488 | Engine RPM | `propulsion.main.revolutions` | RPM |
| 127489 | Oil Pressure | `propulsion.main.oilPressure` | Pa |
| 127489 | Coolant Temp | `propulsion.main.temperature` | K |
| 127505 | Fuel Level | `tanks.fuel.0.currentLevel` | % |
| 127508 | Battery Voltage | `electrical.batteries.0.voltage` | V |
| 128259 | Water Speed | `navigation.speedThroughWater` | m/s |
| 128267 | Depth | `environment.depth.belowTransducer` | m |
| 129025 | Latitude | `navigation.position.latitude` | rad |
| 129025 | Longitude | `navigation.position.longitude` | rad |
| 129026 | COG | `navigation.courseOverGroundTrue` | rad |
| 129026 | SOG | `navigation.speedOverGround` | m/s |


### Appendix D: API Endpoints

**Signal K REST API**:

```
GET  /signalk/v1/api/vessels/self/propulsion/main/revolutions  
GET  /signalk/v1/api/vessels/self/navigation/position  
POST /signalk/v1/api/vessels/self/\_attr
```

**d3kOS API**:

```
GET  /api/health                  \# System health status  
GET  /api/engine/baseline         \# Engine baseline data  
GET  /api/engine/current          \# Current engine metrics  
POST /api/engine/benchmark/start  \# Start benchmarking  
POST /api/voice/enable            \# Enable voice assistant  
POST /api/onboarding/reset        \# Reset Initial Setup wizard  
GET  /api/license                 \# License information
```

### Appendix E: File System Layout

```
/opt/d3kos/  
├── config/  
│   ├── onboarding.json  
│   ├── benchmark-results.json  
│   ├── license.json  
│   └── engine-manufacturers.json  
├── state/  
│   ├── onboarding-reset-count.json  
│   └── pi-health-status.json  
├── data/  
│   ├── boat-log.txt  
│   ├── camera/  
│   ├── historical.db  
│   └── exports/  
├── services/  
│   ├── onboarding/  
│   ├── voice/  
│   ├── camera/  
│   └── health/  
├── scripts/  
│   ├── install-\*.sh  
│   ├── configure-\*.sh  
│   ├── backup.sh  
│   └── restore.sh  
├── models/  
│   ├── vosk/  
│   ├── piper/  
│   └── marine-vision/  
│       └── yolov8n.onnx  
└── logs/  
    ├── onboarding.log  
    ├── voice.log  
    ├── ai-api.log  
    └── health.log
```

### Appendix F: Glossary

- **AODA**: Accessibility for Ontarians with Disabilities Act

- **AIS**: Automatic Identification System

- **CAN**: Controller Area Network (bus protocol)

- **COG**: Course Over Ground

- **DIP**: Dual In-line Package (switch configuration)

- **GPSd**: GPS daemon (service)

- **HAT**: Hardware Attached on Top (Raspberry Pi expansion board)

- **LLM**: Large Language Model

- **NMEA**: National Marine Electronics Association

- **PGN**: Parameter Group Number (NMEA2000 message ID)

- **RTSP**: Real-Time Streaming Protocol

- **Signal K**: Open-source marine data standard

- **SOG**: Speed Over Ground

- **STT**: Speech-to-Text

- **TTS**: Text-to-Speech

- **WOT**: Wide Open Throttle

### Appendix G: Acknowledgments

- Signal K Project for marine data standards

- Node-RED community for automation platform

- OpenCPN project for navigation software

- Anthropic for Claude AI assistance in specification development

- Raspberry Pi Foundation for affordable computing platform


## DOCUMENT APPROVAL

This specification has been reviewed and approved by:

- [ ] Technical Lead

- [ ] UX/UI Designer

- [ ] QA Engineer

- [ ] Project Manager

**Approval Date**: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Next Review Date**: After Phase 1 completion


**END OF DOCUMENT**


## CHANGE LOG

### Version 2.4 (2026-02-12)

- **Updated wake words** from "Navigator" to "Counsel" for online AI selection

- **Changed all acknowledgment responses** to "Aye Aye Captain" for nautical authenticity

- **Updated PocketSphinx dictionary** with COUNSEL phonetic pronunciation (K AW N S AH L)

- **Updated wake word routing logic** in Section 4.5.7

- **Updated implementation checklist** to reflect new wake words

### Version 2.3 (2026-02-12)

- **Added hybrid AI assistant system** with online (Perplexity) and onboard (Phi-2) backends

- **Implemented intelligent AI routing** based on internet connectivity

- **Added skills.md context management system** for unified knowledge base

- **Implemented automatic document retrieval** during onboarding (boat manuals, engine manuals, regulations, best practices)

- **Added text input interface** in main menu for AI queries

- **Implemented conversation history database** with SQLite for learning and memory

- **Added multiple wake words** ("Helm", "Advisor", "Navigator") for AI selection

- **Implemented status updates** for slow onboard AI processing (every 40 seconds)

- **Updated software stack** with Perplexity API, SQLite conversation database

- **Added Section 4.5** Hybrid AI Assistant System Architecture with complete technical specifications

- **Updated Initial Setup wizard** to include document retrieval with progress indicators

### Version 2.2 (2026-02-11)

- **Implemented Step 4 (Chartplotter Detection)** with working code

- **Added nginx proxy configuration** for Signal K WebSocket on port 80

- **Implemented JavaScript detection code** with real-time PGN display and 5-second timer

- **Added fullscreen toggle** on wizard completion to restore kiosk mode

- **Tested and verified** detection correctly identifies navigation vs engine PGNs

- **Fixed WebSocket connection** issues (IPv4/IPv6, localhost vs network IP)

- **Documented** complete implementation in Section 5.3.2a

### Version 2.1 (2026-02-11)

- **Added Step 4 (Chartplotter Detection)** to Initial Setup wizard

- Clarified that CX5106 outputs standard NMEA2000 PGNs

- Documented universal chartplotter compatibility (Garmin, Simrad, Raymarine, Lowrance, Furuno, Humminbird)

- Confirmed no vendor-specific PGN translation required

- Added auto-detection logic for navigation PGNs (129025, 129026, 129029)

- Updated wizard flow from 13 steps to 22 steps total

- Added detailed UI specification for chartplotter detection step

### Version 2.0 (2026-02-06)

- Integrated all recommendations from gap analysis

- Added detailed specifications for 18 missing components

- Expanded UI/UX sections with AODA compliance

- Added voice assistant architecture and implementation details

- Included camera integration with storage safeguards

- Added licensing and version management specifications

- Expanded testing and quality assurance sections

- Added deployment and distribution details

### Version 1.0 (2026-02-04)

- Initial specification document

- Core system architecture defined

- Hardware requirements specified

- Basic software stack outlined

