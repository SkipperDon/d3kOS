# d3kOS ARCHITECTURE

**Version**: 3.0
**Date**: February 22, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v3.6
**System Version**: d3kOS 0.9.1.2
**Last Verified**: February 22, 2026 via live system inspection

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Hardware Architecture](#hardware-architecture)
4. [Software Architecture](#software-architecture)
5. [Service Architecture](#service-architecture)
6. [Network Architecture](#network-architecture)
7. [Data Architecture](#data-architecture)
8. [AI Assistant Architecture](#ai-assistant-architecture)
9. [Tier System Architecture](#tier-system-architecture)
10. [Security Architecture](#security-architecture)
11. [Appendices](#appendices)

---

## 1. SYSTEM OVERVIEW

d3kOS is a comprehensive marine electronics system built on Raspberry Pi 4, providing boat owners with advanced engine monitoring, navigation assistance, AI-powered voice control, and marine vision capabilities.

### 1.1 Core Principles

- **Offline-First**: Full functionality without internet connectivity
- **Touchscreen Primary**: On-screen keyboard is THE primary input (wet hands, gloves)
- **Voice Control**: Hands-free operation via wake words
- **Accessibility**: AODA-compliant design for marine environments
- **Modularity**: Tiered licensing enables/disables features
- **Real-Time**: 1Hz dashboard updates, sub-second AI responses
- **Marine-Grade**: Designed for harsh marine environments

### 1.2 Target Performance

- Boot time: < 60 seconds to operational
- Voice response: < 2 seconds (rule-based), 6-8s (online AI)
- Dashboard update: 1 Hz (1000ms)
- Anomaly detection: > 95% accuracy
- Resource usage: < 70% CPU, < 50% RAM (8GB total)

### 1.3 Current System Status

- **Version**: 0.9.1.2 (beta)
- **Tier**: 3 (all features enabled for testing)
- **Installation ID**: 3861513b314c5ee7 (16-char hex)
- **OS**: Debian GNU/Linux 13 (trixie)
- **Kernel**: 6.12.62+rpt-rpi-v8
- **Storage**: 16GB SD card (85% full), 128GB USB drive (119.2GB usable)

---

## 2. ARCHITECTURE LAYERS

### 2.1 Five-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Main Menu   │  │  Dashboard   │  │   OpenCPN    │          │
│  │   (HTML)     │  │ (Node-RED)   │  │  (Charts)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ AI Assistant │  │ Marine Vision│  │  Settings    │          │
│  │ (HTML/JS)    │  │   (HTML)     │  │  (HTML)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REVERSE PROXY LAYER (Nginx)                    │
│  Port 80 → Routes to 11+ backend services                       │
│  /ai/ → 8080 | /camera/ → 8084 | /license/ → 8091 | etc.      │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Voice      │  │   Camera     │  │ Fish Detect  │          │
│  │  Assistant   │  │  Streaming   │  │  (YOLOv8n)   │          │
│  │  (8080)      │  │  (8084)      │  │  (8086)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  License/    │  │  Tier        │  │  Export      │          │
│  │  Tier Mgmt   │  │  Detection   │  │  Manager     │          │
│  │  (8091,8093) │  │  (boot)      │  │  (8094)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Telegram    │  │  Network     │  │  Timezone    │          │
│  │  Notify      │  │  Manager     │  │  API         │          │
│  │  (8088)      │  │  (8101)      │  │  (8098)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Signal K    │  │   Node-RED   │  │    GPSd      │          │
│  │   Server     │  │   Flows      │  │   Daemon     │          │
│  │  (3000)      │  │  (1880)      │  │  (2947)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     HARDWARE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   PiCAN-M    │  │   USB GPS    │  │  USB AIS     │          │
│  │  (NMEA2000)  │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Touchscreen │  │  IP Camera   │  │ USB Mic/Spkr │          │
│  │ (1920×1200)  │  │ RLC-810A     │  │ Anker S330   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **User Interface** | Visual interaction, touch input | Chromium, HTML/CSS/JS, Node-RED Dashboard |
| **Reverse Proxy** | Route traffic to backend services | Nginx (port 80 → 11+ services) |
| **Application** | Business logic, features | 22+ services (voice, camera, AI, license, etc.) |
| **Data** | Data aggregation, processing | Signal K, Node-RED flows, GPSd |
| **Hardware** | Physical devices, sensors | PiCAN-M, GPS, AIS, Touchscreen, Camera |

---

## 3. HARDWARE ARCHITECTURE

### 3.1 Core Hardware

```
                    ┌─────────────────────┐
                    │   Raspberry Pi 4B   │
                    │   8GB RAM (required)│
                    │   64-bit Trixie     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌────▼────┐  ┌───────▼────────┐
     │   PiCAN-M HAT   │ │ USB Hub │  │  10.1" Touch   │
     │   (NMEA2000)    │ │         │  │  1920×1200     │
     └────────┬────────┘ └────┬────┘  │  1000 nit      │
              │               │        └────────────────┘
              │     ┌─────────┼─────────┐
              │     │         │         │
         ┌────▼────┐│  ┌──────▼──┐  ┌──▼──────┐
         │ N2K Bus ││  │ GPS USB │  │ AIS USB │
         │ (CAN0)  ││  │ VK-162  │  │ dAISy   │
         └─────────┘│  └─────────┘  └─────────┘
                    │
              ┌─────▼──────┐     ┌──────────────┐
              │ Anker S330 │     │ Reolink      │
              │Speakerphone│     │ RLC-810A     │
              │(Mic+Spkr)  │     │ IP Camera    │
              └────────────┘     │ 10.42.0.100  │
                                 └──────────────┘
```

### 3.2 Hardware Specifications

| Component | Model | Specifications | Purpose |
|-----------|-------|----------------|---------|
| **Compute** | Raspberry Pi 4B | 8GB RAM, 64-bit ARM | Main processor |
| **NMEA Interface** | PiCAN-M HAT | MCP2515, 250kbps CAN | NMEA2000 bus access |
| **Display** | 10.1" Touchscreen | 1920×1200, 1000 nit, capacitive | Primary UI |
| **GPS** | VK-162 (or equiv) | USB, NMEA0183 | Position/time data |
| **AIS** | dAISy (or equiv) | USB, 38400 baud | Vessel traffic |
| **Audio** | Anker PowerConf S330 | USB speakerphone | Voice I/O |
| **Camera** | Reolink RLC-810A | IP67, 4K/1080p, night vision | Marine vision |
| **Storage (OS)** | MicroSD | 16GB (85% full, 2.2GB free) | Operating system |
| **Storage (Data)** | USB Drive | 128GB (119.2GB usable) | Camera recordings |

### 3.3 Hardware Interfaces

| Interface | Protocol | Device | Address/Port | Purpose |
|-----------|----------|--------|--------------|---------|
| **GPIO (HAT)** | SPI/CAN | PiCAN-M | can0 | NMEA2000 bus access |
| **USB** | Serial | GPS Receiver | /dev/ttyACM0 | Position/time data |
| **USB** | Serial | AIS Receiver | /dev/ttyUSB1 | Vessel traffic data |
| **USB** | Audio | Anker S330 | plughw:2,0 | Voice I/O |
| **DSI** | Display | Touchscreen | - | User interface |
| **Ethernet** | IP | Camera | 10.42.0.100 | RTSP video stream |
| **WiFi** | 802.11ac | Built-in | wlan0 | **Client mode only** |

### 3.4 Network Connectivity

**⚠️ IMPORTANT: WiFi Access Point NOT SUPPORTED**

- **WiFi Client Mode**: ✅ SUPPORTED (Session F - Network UI complete)
- **WiFi Access Point Mode**: ❌ NOT SUPPORTED (BCM4345/6 firmware limitation)
- **Ethernet**: ✅ SUPPORTED (optional internet connectivity)
- **Hotspot Workaround**: Connect to phone/Starlink/marina WiFi via Network Settings UI

**Why No WiFi AP?**
- BCM4345/6 firmware error: `brcmf_vif_set_mgmt_ie: vndr ie set error : -52` (EOPNOTSUPP)
- Tested 5 configurations (WPA2, mixed, open) - all failed
- Hardware limitation, not software issue
- Session E/F (Feb 20, 2026) documented and verified

**Network Management UI**: http://192.168.1.237/settings-network.html
- Scan WiFi networks
- Connect/disconnect
- Status monitoring
- PolicyKit integration (no sudo required)

### 3.5 Power Architecture

```
12V Boat Battery
      │
      ▼
┌─────────────┐
│ DC-DC Conv  │  Victron Orion-Tr 12/12-9A (recommended)
│ 12V → 5V    │  Noise filtering + voltage regulation
└──────┬──────┘
       │ 5V 3A (USB-C)
       ▼
┌─────────────┐
│ Raspberry   │  Peak: 15W, Typical: 10W
│ Pi 4B       │  Current: 3A peak, 2A typical
└─────────────┘
```

---

## 4. SOFTWARE ARCHITECTURE

### 4.1 Operating System Stack

```
┌───────────────────────────────────────────┐
│         User Applications                 │
│  Chromium 144, OpenCPN 5.8.x              │
├───────────────────────────────────────────┤
│         Display Server                    │
│  Labwc (Wayland compositor)               │
├───────────────────────────────────────────┤
│         System Services (22+)             │
│  Signal K, Node-RED, GPSd, Voice, etc.    │
├───────────────────────────────────────────┤
│         Systemd Init                      │
│  Service management, auto-start           │
├───────────────────────────────────────────┤
│         Raspberry Pi OS (64-bit)          │
│  Debian Trixie (13), Kernel 6.12.62       │
└───────────────────────────────────────────┘
```

### 4.2 Software Components

| Component | Version | Purpose | Port/Interface |
|-----------|---------|---------|----------------|
| **Raspberry Pi OS** | Trixie (Debian 13) | Base operating system | - |
| **Kernel** | 6.12.62+rpt-rpi-v8 | Linux kernel | - |
| **Display Server** | Labwc (Wayland) | Window management | - |
| **Python** | 3.13.5 | Application runtime | - |
| **Node.js** | v20.20.0 | JavaScript runtime | - |
| **Chromium** | 144.0.7559.109 | Browser UI | - |
| **Signal K Server** | Latest (Node v20) | Marine data hub | 3000 (WS/HTTP) |
| **Node-RED** | v4.1.4 | Automation & dashboard | 1880 (HTTP) |
| **GPSd** | Latest | GPS data processing | 2947 (TCP) |
| **PocketSphinx** | 0.8+5prealpha | Wake word detection | - |
| **ONNX Runtime** | 1.24.1 | AI inference engine | - |
| **OpenCPN** | 5.8.x | Chart plotting (Tier 2+) | - |
| **VLC (libvlc)** | Latest | RTSP stream handling | - |
| **Nginx** | Latest | Reverse proxy | 80 (HTTP) |

### 4.3 AI/ML Stack

**IMPORTANT: Phi-2 LLM REMOVED (Feb 16, 2026)**
- Reason: 60-180s response time (unusable on boat helm)
- Freed: 1.7GB storage
- Replacement: OpenRouter (online) + rule-based (offline)

| Component | Technology | Size | Purpose |
|-----------|-----------|------|---------|
| **Wake Word** | PocketSphinx | ~10MB | Detect "helm/advisor/counsel" |
| **Online AI** | OpenRouter (gpt-3.5-turbo) | API | 6-8s responses, requires internet |
| **Offline AI** | Rule-based (13 patterns) | ~1KB | 0.17s responses, no internet |
| **Object Detection** | YOLOv8n ONNX | 13MB | Fish/person detection |
| **No TTS/STT** | - | - | Voice removed (wake word detection broken) |

---

## 5. SERVICE ARCHITECTURE

### 5.1 Complete Service List (22 Services)

| Service | Port | Auto-start | Tier | Purpose |
|---------|------|------------|------|---------|
| **signalk.service** | 3000 | Yes | All | Marine data server (WebSocket/HTTP) |
| **nodered.service** | 1880 | Yes | All | Automation & dashboard |
| **gpsd.service** | 2947 | Yes | All | GPS data processing |
| **nginx.service** | 80 | Yes | All | Reverse proxy for all services |
| **d3kos-first-boot.service** | - | Once | All | Generate installation ID on first boot |
| **d3kos-license-api.service** | 8091 | Yes | All | License information API |
| **d3kos-tier-api.service** | 8093 | Yes | All | Tier status API |
| **d3kos-tier-manager.service** | - | Boot | All | Detect tier (OpenCPN check) |
| **d3kos-timezone-setup.service** | - | Once | All | Auto-detect timezone (GPS→Internet→UTC) |
| **d3kos-timezone-api.service** | 8098 | Yes | All | Timezone management API |
| **d3kos-export-manager.service** | 8094 | Yes | Tier 1+ | Data export & sync API |
| **d3kos-network-api.service** | 8101 | Yes | All | WiFi management API |
| **d3kos-ai-api.service** | 8080 | Yes | All | AI assistant API (OpenRouter/rules) |
| **d3kos-voice.service** | - | Disabled | Tier 2+ | Voice assistant (wake word broken) |
| **d3kos-camera-stream.service** | 8084 | Yes | Tier 2+ | Camera stream manager (RTSP→MJPEG) |
| **d3kos-fish-detector.service** | 8086 | Yes | Tier 2+ | YOLOv8n object detection API |
| **d3kos-notifications.service** | 8088 | Yes | Tier 2+ | Telegram notification manager |
| **d3kos-health.service** | - | Yes | All | System health monitoring |
| **d3kos-telemetry.service** | - | Yes | Tier 1+ | Analytics collection (user consent) |
| **d3kos-media-cleanup.service** | - | Daily | Tier 2+ | Delete old camera recordings (7 days) |
| **d3kos-self-healing.service** | - | Yes | All | AI-powered anomaly detection & auto-remediation |

### 5.2 Service Dependency Tree

```
                    Systemd Init
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    ┌─────▼─────┐  ┌─────▼─────┐  ┌────▼──────┐
    │ signalk   │  │ nodered   │  │  gpsd     │
    └─────┬─────┘  └─────┬─────┘  └────┬──────┘
          │              │              │
    ┌─────▼──────────────▼──────────────▼─────┐
    │         nginx (reverse proxy)            │
    └─────┬─────┬─────┬─────┬─────┬────┬──────┘
          │     │     │     │     │    │
    ┌─────▼─┐ ┌─▼───┐ │  ┌──▼──┐ │ ┌──▼─────┐
    │ AI API│ │Tier │ │  │Exprt│ │ │Network │
    │ 8080  │ │8093 │ │  │8094 │ │ │  8101  │
    └───────┘ └─────┘ │  └─────┘ │ └────────┘
                      │          │
              ┌───────▼──┐   ┌───▼────────┐
              │Camera    │   │Telegram    │
              │8084/8086 │   │    8088    │
              └──────────┘   └────────────┘
```

### 5.3 Nginx Reverse Proxy Configuration

**Location**: `/etc/nginx/sites-enabled/default`

| URL Path | Backend Service | Port | Purpose |
|----------|----------------|------|---------|
| `/` | HTML files | `/var/www/html/` | Main UI |
| `/signalk/` | Signal K | 3000 | Marine data API |
| `/sk-admin/` | Signal K | 3000 | Admin interface |
| `/ai/` | AI API | 8080 | AI assistant |
| `/camera/` | Camera Stream | 8084 | Video stream |
| `/detect/` | Fish Detector | 8086 | Object detection |
| `/notify/` | Telegram | 8088 | Notifications |
| `/license/` | License API | 8091 | License info |
| `/tier/` | Tier API | 8093 | Tier status |
| `/export/` | Export Manager | 8094 | Data export |
| `/api/timezone/` | Timezone API | 8098 | Timezone config |
| `/network/` | Network API | 8101 | WiFi management |

---

## 6. NETWORK ARCHITECTURE

### 6.1 Network Topology

**⚠️ WiFi Access Point NOT SUPPORTED - Client Mode Only**

```
┌────────────────────────────────────────────────┐
│             Raspberry Pi 4B                    │
│                                                │
│  ┌──────────┐              ┌──────────┐       │
│  │  wlan0   │              │  eth0    │       │
│  │  (Client)│              │(Optional)│       │
│  └────┬─────┘              └────┬─────┘       │
│       │                         │             │
└───────┼─────────────────────────┼─────────────┘
        │                         │
        │ DHCP Client             │ DHCP Client
        │ (from router/phone)     │ (if connected)
        │                         │
   ┌────▼────┐              ┌─────▼──────┐
   │ Router/ │              │ Boat       │
   │ Phone   │              │ Network    │
   │ Hotspot │              │ (Optional) │
   └─────────┘              └────────────┘
        │                         │
        │                         │
   Mobile/Tablets          Internet (optional)
   Connect to same WiFi
```

**Access URLs** (when connected to same WiFi):
- Main Menu: `http://192.168.1.237/` (or DHCP-assigned IP)
- Dashboard: `http://192.168.1.237:1880/dashboard`
- Signal K: `http://192.168.1.237:3000`

### 6.2 Network Services

| Service | Protocol | Port | Access | Purpose |
|---------|----------|------|--------|---------|
| **Main UI** | HTTP | 80 | All devices | Web interface (via Nginx) |
| **Signal K** | WebSocket/HTTP | 3000 | All devices | Marine data API |
| **Node-RED** | HTTP | 1880 | All devices | Dashboard access |
| **Camera** | RTSP | 554 | Camera only | Reolink RLC-810A |
| **SSH** | SSH | 22 | Disabled | Remote admin (security) |

### 6.3 Camera Network

- **Camera IP**: 10.42.0.100 (static via DHCP reservation)
- **Camera MAC**: ec:71:db:f9:7c:7c
- **Network**: Pi eth0 shared connection (10.42.0.0/24)
- **RTSP URL**: `rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub`
- **Stream**: Sub-stream (720p/1080p) for stability

---

## 7. DATA ARCHITECTURE

### 7.1 Data Storage Structure

```
/opt/d3kos/
├── config/              # Permanent configuration
│   ├── license.json     # Installation ID, tier, features
│   ├── onboarding.json  # Wizard answers (20 questions)
│   ├── ai-config.json   # OpenRouter API key
│   ├── telegram-config.json # Telegram bot config
│   ├── timezone.txt     # Auto-detected timezone
│   └── camera-ip.txt    # Camera IP address
├── state/               # Runtime state
│   ├── onboarding-reset-count.json
│   └── pi-health-status.json
├── data/                # User data
│   ├── boat-log.txt     # Boat log entries
│   ├── historical.db    # SQLite database
│   ├── conversation-history.db # AI chat history
│   ├── captures.db      # Marine vision captures
│   ├── exports/         # JSON export queue
│   └── telemetry/       # Analytics (Tier 1+, consent)
├── models/              # AI models
│   ├── vosk/            # STT model (50MB) - NOT USED
│   ├── piper/           # TTS voice (20MB) - NOT USED
│   └── marine-vision/   # YOLOv8n ONNX (13MB)
├── services/            # Service scripts
│   ├── ai/              # AI assistant service
│   ├── voice/           # Voice assistant (broken)
│   ├── marine-vision/   # Camera + fish detection
│   ├── export/          # Data export manager
│   ├── license/         # License API
│   └── network/         # Network management
├── scripts/             # Utility scripts
│   ├── detect-timezone.sh
│   ├── generate-installation-id.sh
│   └── media-cleanup.sh
└── logs/                # Application logs
    ├── ai-api.log
    ├── camera-stream.log
    └── export-manager.log
```

### 7.2 Data Persistence

| Data Type | Location | Format | Retention | Tier |
|-----------|----------|--------|-----------|------|
| Installation ID | `/opt/d3kos/config/license.json` | JSON | Permanent | All |
| Onboarding config | `/opt/d3kos/config/onboarding.json` | JSON | Permanent | All |
| License/Tier info | `/opt/d3kos/config/license.json` | JSON | Permanent | All |
| Boat log | `/opt/d3kos/data/boat-log.txt` | Text | 30d (T0), ∞ (T2+) | All |
| Camera recordings | `/home/d3kos/camera-recordings/` | MP4 | 7 days (auto-delete) | Tier 2+ |
| Fish captures | `/home/d3kos/camera-recordings/captures/` | JPEG | 7 days | Tier 2+ |
| Historical metrics | `/opt/d3kos/data/historical.db` | SQLite | 90 days | All |
| AI conversations | `/opt/d3kos/data/conversation-history.db` | SQLite | 30 days | All |
| Export queue | `/opt/d3kos/data/exports/` | JSON | Until synced | Tier 1+ |
| Telemetry | `/opt/d3kos/data/telemetry/` | SQLite | 30 days | Tier 1+ |

### 7.3 Signal K Data Schema

**NMEA2000 PGN to Signal K Mapping**:

| PGN | Parameter | Signal K Path | Update Rate |
|-----|-----------|---------------|-------------|
| 127488 | Engine RPM | `propulsion.main.revolutions` | 100ms |
| 127489 | Oil Pressure | `propulsion.main.oilPressure` | 500ms |
| 127489 | Coolant Temp | `propulsion.main.temperature` | 500ms |
| 127505 | Fuel Level | `tanks.fuel.0.currentLevel` | 2500ms |
| 127508 | Battery Voltage | `electrical.batteries.0.voltage` | 1500ms |
| 128259 | Water Speed | `navigation.speedThroughWater` | 1000ms |
| 128267 | Depth | `environment.depth.belowTransducer` | 1000ms |
| 129025 | Position | `navigation.position` | 100ms |
| 129026 | COG/SOG | `navigation.courseOverGroundTrue` | 100ms |
| 129029 | GNSS Data | `navigation.gnss.*` | 1000ms |

### 7.4 Database Schema (SQLite)

**Historical Engine Metrics** (`historical.db`):
```sql
CREATE TABLE engine_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    engine_hours REAL,
    rpm INTEGER,
    oil_pressure REAL,
    coolant_temp REAL,
    fuel_rate REAL,
    voltage REAL
);
```

**AI Conversations** (`conversation-history.db`):
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    ai_used TEXT NOT NULL,  -- 'openrouter' or 'onboard'
    response_time REAL,
    important BOOLEAN DEFAULT 0
);
```

**Marine Vision Captures** (`captures.db`):
```sql
CREATE TABLE captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_path TEXT NOT NULL,
    species TEXT,
    species_confidence REAL,
    latitude REAL,
    longitude REAL,
    detection_type TEXT,  -- 'person', 'fish', 'boat', etc.
    sent_telegram BOOLEAN DEFAULT 0
);
```

---

## 8. AI ASSISTANT ARCHITECTURE

### 8.1 Hybrid AI System (Post-Phi-2 Removal)

**Architecture** (Updated Feb 16, 2026):

```
User Query (Text OR Voice*)
         ↓
    Classify Query
    ┌────────┴────────┐
    │                 │
Simple Pattern        Complex Query
(13 patterns)         + Internet?
    ↓                 ┌────┴────┐
Rule-Based            │         │
Response         Internet    No Internet
(0.17-0.22s)         ↓         ↓
    ↓            OpenRouter   Error:
Signal K Cache    (gpt-3.5)   "Need internet"
(3s TTL)          6-8s
    ↓                ↓
Response         Response
    ↓                ↓
   Store in conversation-history.db

*Voice currently broken (wake word detection issue)
```

### 8.2 Rule-Based AI (Onboard)

**13 Instant-Response Patterns** (0.17-0.22s):
1. **rpm** - "Engine RPM is 0"
2. **oil** - "Oil pressure is N/A"
3. **temperature** - "Coolant temperature is..."
4. **fuel** - "Fuel level is..."
5. **battery** - "Battery voltage is..."
6. **speed** - "Speed is..."
7. **heading** - "Heading is..."
8. **boost** - "Boost pressure is..."
9. **hours** - "Engine hours are..."
10. **location** - "Position is 43.687°N, 79.520°W"
11. **time** - "Current time is 10:30 AM on..."
12. **help** - Lists available query types
13. **status** - Full system status

**Signal K Caching**:
- Cache TTL: 3.0 seconds
- First query: 18s (fetch from Signal K)
- Cached queries: 0.17s (100× faster)
- Enabled: Feb 16, 2026 (Session 3)

### 8.3 Online AI (OpenRouter)

**Configuration** (`/opt/d3kos/config/ai-config.json`):
```json
{
  "online_ai": {
    "provider": "openrouter",
    "api_key": "sk-or-v1-...",
    "model": "openai/gpt-3.5-turbo",
    "enabled": true,
    "max_tokens": 500,
    "temperature": 0.7
  }
}
```

**Performance**:
- Response time: 6-8 seconds
- Context window: 16K tokens
- Cost: Free tier available
- Requires: Internet connectivity

### 8.4 Voice Assistant Status

**⚠️ VOICE CURRENTLY BROKEN**

**Issue**: Wake word detection not working (Session 2026-02-17)
- PocketSphinx process runs but doesn't detect "HELM"
- PipeWire interference suspected (17× signal reduction)
- Attempted fixes: Direct hardware access, threshold tuning
- Status: Needs dedicated 2-3 hour debugging session

**Wake Words** (when working):
- **"helm"** - Auto-select (online if available, else onboard)
- **"advisor"** - Force onboard AI (rule-based)
- **"counsel"** - Force online AI (OpenRouter)

**Workaround**: Use text-based AI Assistant at http://192.168.1.237/ai-assistant.html

### 8.5 API Endpoints

**AI API** (port 8080, service: `d3kos-ai-api.service`):
- `POST /ai/query` - Submit question (text input)
  - Request: `{"question": "What's the RPM?", "provider": "auto|online|onboard"}`
  - Response: `{"answer": "...", "provider_used": "...", "response_time": ...}`

**Files**:
- Service: `/opt/d3kos/services/ai/ai_api.py` (Flask, persistent handler)
- Query handler: `/opt/d3kos/services/ai/query_handler.py` (v5, Signal K caching)
- Signal K client: `/opt/d3kos/services/ai/signalk_client.py` (3s cache TTL)

---

## 9. TIER SYSTEM ARCHITECTURE

### 9.1 Tier Overview

| Tier | Price | Upgrade Method | Features Enabled |
|------|-------|----------------|------------------|
| **Tier 0** | Free | Default | Dashboard, health monitoring, boat log (30d), onboarding (10 resets) |
| **Tier 1** | Free | Mobile app pairing | T0 + Mobile app, data export, cloud sync, config restore |
| **Tier 2** | $9.99/mo | OpenCPN installed OR Stripe subscription | T1 + Voice assistant, camera, premium features, unlimited resets |
| **Tier 3** | $99.99/yr | Stripe subscription | T2 + Enterprise features, multi-boat, advanced analytics |

**Current System**: Tier 3 (all features enabled for testing)

### 9.2 Tier Detection Logic

**File**: `/opt/d3kos/scripts/detect-tier.sh` (runs on boot via `d3kos-tier-manager.service`)

```bash
# Pseudo-code
if [ -f "/usr/bin/opencpn" ]; then
    TIER=2  # OpenCPN installed = auto-upgrade to Tier 2
elif [ -f "/opt/d3kos/config/license.json" ] && [ subscription_active == true ]; then
    TIER=2  # or 3 based on subscription type
else
    TIER=0  # Default
fi

# Update license.json with detected tier
# Enable/disable services based on tier
```

### 9.3 Feature Restrictions

**Enforced by**:
- Service auto-start (systemd conditionals)
- API endpoint checks (tier verification)
- UI element visibility (JavaScript tier checks)

| Feature | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|--------|
| Dashboard | ✓ | ✓ | ✓ | ✓ |
| Engine Monitoring | ✓ | ✓ | ✓ | ✓ |
| Boat Log | 30 days | ∞ | ∞ | ∞ |
| Onboarding Resets | 10 max | 10 max | ∞ | ∞ |
| Mobile App | ✗ | ✓ | ✓ | ✓ |
| Data Export | ✗ | ✓ | ✓ | ✓ |
| Cloud Sync | ✗ | ✓ | ✓ | ✓ |
| Voice Assistant | ✗ | ✗ | ✓ | ✓ |
| Camera/Marine Vision | ✗ | ✗ | ✓ | ✓ |
| AI Assistant | Basic | Basic | Premium | Premium |
| Historical Graphs | 30d | 90d | 90d | ∞ |

### 9.4 Tier APIs

**Tier Status API** (port 8093):
- `GET /tier/status` - Get current tier and features
  - Response: `{"tier": 3, "features": {...}, "subscription_status": "active"}`

**License API** (port 8091):
- `GET /license/info` - Basic info (installation_id, tier, features)
- `GET /license/full` - Complete license.json

---

## 10. SECURITY ARCHITECTURE

### 10.1 Security Layers

```
┌─────────────────────────────────────────┐
│         Application Security            │
│  - Local-only by default                │
│  - API authentication (future)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Network Security                │
│  - No external exposure (behind router) │
│  - WiFi client mode only                │
│  - SSH disabled by default              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         System Security                 │
│  - Default password: CHANGE REQUIRED    │
│  - Service isolation (systemd)          │
│  - File permissions (d3kos user)        │
└─────────────────────────────────────────┘
```

### 10.2 Default Credentials

**⚠️ CHANGE AFTER FIRST LOGIN**

| Account | Username | Password | Notes |
|---------|----------|----------|-------|
| System User | `d3kos` | `d3kos2026` | Change via `passwd` |
| Camera | `admin` | `d3kos2026` | Reolink web UI |
| WiFi AP | N/A | N/A | NOT SUPPORTED |

### 10.3 Data Privacy

**Installation ID**:
- Format: 16-char hex (e.g., `3861513b314c5ee7`)
- Generated: SHA-256(MAC address + timestamp)
- Purpose: Anonymous system identification
- NOT personally identifiable

**Telemetry** (Tier 1+):
- Collection: Opt-in only (user consent required)
- Data: System performance, usage patterns (NO personal data)
- Storage: Local (30 days), optional cloud sync
- Service: `d3kos-telemetry.service`

**AI Conversations**:
- Storage: Local SQLite database only
- Retention: 30 days
- NOT sent to cloud (except when using OpenRouter for query)

---

## 11. APPENDICES

### Appendix A: Component Versions (Verified Feb 22, 2026)

| Component | Version | License | Source |
|-----------|---------|---------|--------|
| Raspberry Pi OS | Trixie (Debian 13) | Various | raspberrypi.org |
| Kernel | 6.12.62+rpt-rpi-v8 | GPL | linux.org |
| Python | 3.13.5 | PSF | python.org |
| Node.js | v20.20.0 | MIT | nodejs.org |
| Chromium | 144.0.7559.109 | BSD | chromium.org |
| Signal K | Latest (requires Node v20) | Apache 2.0 | signalk.org |
| Node-RED | v4.1.4 | Apache 2.0 | nodered.org |
| GPSd | Latest (Debian repo) | BSD | gpsd.org |
| PocketSphinx | 0.8+5prealpha+1-15 | BSD | cmusphinx.org |
| ONNX Runtime | 1.24.1 | MIT | onnxruntime.ai |
| OpenCPN | 5.8.x | GPL v2 | opencpn.org |
| Nginx | Latest (Debian repo) | BSD | nginx.org |

### Appendix B: Marine Vision System

**Status**: Phase 1, 2.1, 2.6 Complete

**Components**:
- Camera Stream Manager (port 8084)
- Fish Detector (port 8086, YOLOv8n ONNX)
- Telegram Notifications (port 8088)

**Model**: YOLOv8n ONNX (13MB)
- Format: ONNX (optimized for ONNX Runtime)
- Classes: 80 COCO classes (person detection working)
- Performance: 2-3 seconds per detection on Pi 4B
- Storage: `/opt/d3kos/models/marine-vision/yolov8n.onnx`

**Telegram Integration**:
- Bot configuration: `/opt/d3kos/config/telegram-config.json`
- Features: Photo uploads, GPS tagging, instant notifications
- Status: Implemented, ready for user configuration

**Camera**: Reolink RLC-810A
- IP: 10.42.0.100 (DHCP reserved)
- Resolution: 4K/1080p (sub-stream used for stability)
- Night vision: IR LEDs, 30m range
- Waterproof: IP67 rating

### Appendix C: Data Export System

**Status**: Task #2 Complete (Session A, Feb 17, 2026)

**Export Manager** (port 8094):
- Service: `d3kos-export-manager.service`
- API: `/export/status`, `/export/generate`
- Format: JSON with installation_id

**Export Categories** (9 total):
1. Engine benchmark data
2. Boatlog entries (voice, text, auto, weather)
3. Marine vision captures (metadata only, no images)
4. Marine vision snapshots (metadata only, no videos)
5. QR code data
6. Settings configuration
7. System alerts
8. Onboarding/Initial Setup configuration
9. Telemetry & analytics (Tier 1+, consent required)

**Triggers**:
- Manual: Settings → Data Management → Export Now
- Automatic: Boot-time sync (if internet available)
- Scheduled: Daily 3:00 AM (Tier 2+)

### Appendix D: Network Management UI

**Status**: Session F Complete (Feb 20, 2026)

**Network API** (port 8101):
- Service: `d3kos-network-api.service`
- Endpoints: `/network/status`, `/network/scan`, `/network/connect`

**Features**:
- WiFi network scanning
- Connect/disconnect (WPA2/Open)
- Status monitoring
- PolicyKit integration (no sudo required)

**UI**: http://192.168.1.237/settings-network.html
- Touch-optimized (60px+ buttons)
- Real-time status updates
- On-screen keyboard compatible

### Appendix E: Timezone Auto-Detection

**Status**: Session A Complete (Feb 20, 2026)

**Detection Script**: `/opt/d3kos/scripts/detect-timezone.sh`

**3-Tier Detection**:
1. GPS coordinates → timezone (best, requires GPS fix)
2. Internet geolocation → timezone (fallback, requires internet)
3. Default to UTC (last resort)

**Service**: `d3kos-timezone-setup.service` (runs once on first boot)

**API** (port 8098):
- `GET /api/timezone/status` - Current timezone
- `POST /api/timezone/set` - Manual override

**Current**: America/Toronto (detected via GPS, 43.687°N 79.520°W)

### Appendix F: Known Issues

1. **Voice Assistant** - Wake word detection broken (PipeWire interference suspected)
   - Workaround: Use text-based AI at `/ai-assistant.html`
   - Priority: High (needs 2-3 hour debugging session)

2. **WiFi Access Point** - Hardware incompatible (BCM4345/6 limitation)
   - Status: Documented as NOT SUPPORTED
   - Workaround: Connect to phone/Starlink/marina WiFi

3. **Chromium "Restore pages?" prompt** - ✅ FIXED (deployed & tested Feb 22, 2026)
   - **Solution**: Delete session files + Chromium flags in autostart
   - **Location**: `/home/d3kos/.config/autostart/d3kos-browser.desktop`
   - **Method**:
     - Deletes `Sessions/*`, `Current*`, `Last*` files before Chromium launch
     - Chromium flags: `--disable-restore-session-state --disable-session-crashed-bubble --hide-crash-restore-bubble`
   - **Status**: ✅ Tested and working (no prompt after reboot)
   - **Note**: Initial Preferences modification approach didn't work; session file deletion is more reliable

4. **Storage 85% full** - 16GB SD card needs upgrade to 32GB+ or cleanup
   - Freed: 1.7GB by removing Phi-2 (Feb 16)
   - Recommendation: Upgrade to 32GB+ SD card

### Appendix G: Future Enhancements

**Not Yet Implemented**:
- Custom fish detection model (Marine Vision Phase 2.2+)
- Stripe Billing integration (40-60 hour project)
- Mobile app development (iOS/Android)
- Boatlog export button fix
- Charts page (o-charts addon installation)
- Skills.md context system (AI knowledge base)
- Self-healing system (anomaly auto-remediation)

---

**END OF ARCHITECTURE DOCUMENT**

**Verified Against**: Live system inspection via SSH (Feb 22, 2026)
**Authoritative Source**: MASTER_SYSTEM_SPEC.md v3.6, CLAUDE.md v3.7
**Next Update**: After major feature additions or system changes
