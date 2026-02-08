# HELM-OS ARCHITECTURE

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Hardware Architecture](#hardware-architecture)
4. [Software Architecture](#software-architecture)
5. [Network Architecture](#network-architecture)
6. [Data Architecture](#data-architecture)
7. [Voice Assistant Pipeline](#voice-assistant-pipeline)
8. [Security Architecture](#security-architecture)

---

## 1. SYSTEM OVERVIEW

d3kOS is a comprehensive marine electronics system built on Raspberry Pi 4, providing boat owners with advanced engine monitoring, navigation assistance, and voice-controlled operations.

### 1.1 Core Principles

- **Offline-First**: Full functionality without internet connectivity
- **Accessibility**: AODA-compliant design for marine environments
- **Modularity**: Tiered licensing enables/disables features
- **Real-Time**: 1Hz dashboard updates, <2s voice response
- **Marine-Grade**: Designed for harsh marine environments

### 1.2 Target Performance

- Boot time: < 60 seconds
- Voice response: < 2 seconds
- Dashboard update: 1 Hz (1000ms)
- Anomaly detection: > 95% accuracy
- Resource usage: < 70% CPU, < 4GB RAM

---

## 2. ARCHITECTURE LAYERS

### 2.1 Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Main Menu   │  │  Dashboard   │  │   OpenCPN    │          │
│  │   (HTML)     │  │ (Node-RED)   │  │  (Charts)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
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
│                     HARDWARE LAYER                               │
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

### 2.2 Layer Responsibilities

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **User Interface** | Visual interaction, touch input | Chromium, HTML/CSS/JS, Node-RED Dashboard |
| **Application** | Business logic, features | Voice, Camera, Health Monitoring, Licensing |
| **Data** | Data aggregation, processing | Signal K, Node-RED flows, GPSd |
| **Hardware** | Physical devices, sensors | PiCAN-M, GPS, AIS, Touchscreen, Camera |

---

## 3. HARDWARE ARCHITECTURE

### 3.1 Core Hardware

```
                    ┌─────────────────────┐
                    │   Raspberry Pi 4    │
                    │   4GB/8GB RAM       │
                    │   64-bit Bookworm   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌────▼────┐  ┌───────▼────────┐
     │   PiCAN-M HAT   │ │ USB Hub │  │  10.1" Touch   │
     │   (NMEA2000)    │ │         │  │  1920×1200     │
     └────────┬────────┘ └────┬────┘  └────────────────┘
              │               │
              │     ┌─────────┼─────────┐
              │     │         │         │
         ┌────▼────┐│  ┌──────▼──┐  ┌──▼──────┐
         │ N2K Bus ││  │ GPS USB │  │ AIS USB │
         │ (CAN0)  ││  │ VK-162  │  │ dAISy   │
         └─────────┘│  └─────────┘  └─────────┘
                    │
              ┌─────▼──────┐
              │ Anker S330 │
              │ Speakerphone│
              └────────────┘
```

### 3.2 Hardware Interfaces

| Interface | Protocol | Device | Purpose |
|-----------|----------|--------|---------|
| **GPIO (HAT)** | SPI/CAN | PiCAN-M | NMEA2000 bus access |
| **USB** | Serial | GPS Receiver | Position/time data |
| **USB** | Serial | AIS Receiver | Vessel traffic data |
| **USB** | Audio | Anker PowerConf | Voice I/O |
| **DSI/HDMI** | Display | Touchscreen | User interface |
| **Network** | RTSP | IP Camera | Video surveillance |

### 3.3 Power Architecture

```
12V Boat Battery
      │
      ▼
┌─────────────┐
│ DC-DC Conv  │  (Victron Orion-Tr 12/12-9A)
│ 12V → 5V    │  Noise filtering + voltage regulation
└──────┬──────┘
       │ 5V 3A
       ▼
┌─────────────┐
│ Raspberry   │  Peak: 15W, Typical: 10W
│ Pi 4        │  Current: 3A peak, 2A typical
└─────────────┘
```

---

## 4. SOFTWARE ARCHITECTURE

### 4.1 Operating System Stack

```
┌───────────────────────────────────────────┐
│         User Applications                 │
│  Chromium, OpenCPN, Custom Services       │
├───────────────────────────────────────────┤
│         Window Manager                    │
│  Openbox (lightweight)                    │
├───────────────────────────────────────────┤
│         System Services                   │
│  Signal K, Node-RED, GPSd, Voice, Camera  │
├───────────────────────────────────────────┤
│         Systemd                           │
│  Service management, auto-start           │
├───────────────────────────────────────────┤
│         Raspberry Pi OS (64-bit)          │
│  Debian Bookworm, Kernel 6.1+             │
└───────────────────────────────────────────┘
```

### 4.2 Software Components

| Component | Version | Purpose | Port/Interface |
|-----------|---------|---------|----------------|
| **Raspberry Pi OS** | Bookworm (64-bit) | Base operating system | - |
| **Signal K Server** | Latest | Marine data hub | 3000 (WS/HTTP) |
| **Node-RED** | 3.x | Automation & dashboard | 1880 (HTTP) |
| **GPSd** | Latest | GPS data processing | 2947 (TCP) |
| **PocketSphinx** | Latest | Wake word detection | - |
| **Vosk** | 0.15 | Speech-to-text | - |
| **Piper** | Latest | Text-to-speech | - |
| **Phi-2** (llama.cpp) | 2.7B | Local AI reasoning | - |
| **OpenCPN** | 5.8.x | Chart plotting (optional) | - |
| **Chromium** | Latest | Browser UI | - |
| **VLC (libvlc)** | Latest | Camera stream viewer | - |

### 4.3 Service Architecture

```
                    Systemd Init
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    ┌─────▼─────┐  ┌─────▼─────┐  ┌────▼──────┐
    │ signalk.  │  │ nodered.  │  │  gpsd.    │
    │ service   │  │ service   │  │  service  │
    └─────┬─────┘  └─────┬─────┘  └────┬──────┘
          │              │              │
    ┌─────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐
    │helm-voice. │ │helm-camera.│ │d3kos-health.│
    │  service   │ │  service   │ │  service   │
    │ (Tier 2+)  │ │ (optional) │ │            │
    └────────────┘ └────────────┘ └────────────┘
```

### 4.4 Systemd Services

| Service | Description | Auto-start | Tier Requirement |
|---------|-------------|------------|------------------|
| `signalk.service` | Marine data server | Yes | All |
| `nodered.service` | Automation & dashboard | Yes | All |
| `gpsd.service` | GPS processing | Yes | All |
| `d3kos-voice.service` | Voice assistant | Yes | Tier 2+ |
| `helm-camera.service` | IP camera management | Conditional | Tier 2+ |
| `d3kos-health.service` | System monitoring | Yes | All |
| `helm-boatlog.service` | Voice log management | Yes | Tier 2+ |

### 4.5 Data Flow Architecture

```
Hardware → Data Layer → Application Layer → UI Layer

Example: Engine RPM Display
┌──────────────┐
│ NMEA2000 Bus │  PGN 127488 (Engine RPM)
└──────┬───────┘
       │ CAN frames
       ▼
┌──────────────┐
│ PiCAN-M HAT  │  Decode CAN frames
└──────┬───────┘
       │ can0 interface
       ▼
┌──────────────┐
│  Signal K    │  Convert to Signal K path:
│   Server     │  propulsion.main.revolutions
└──────┬───────┘
       │ WebSocket (1Hz)
       ▼
┌──────────────┐
│  Node-RED    │  Process, threshold check
│   Flows      │  Apply anomaly detection
└──────┬───────┘
       │ HTTP/WS
       ▼
┌──────────────┐
│  Dashboard   │  Update gauge (circular dial)
│  (Browser)   │  Display: 3200 RPM
└──────────────┘
```

---

## 5. NETWORK ARCHITECTURE

### 5.1 Network Topology

```
┌────────────────────────────────────────────────┐
│             Raspberry Pi 4                     │
│                                                │
│  ┌──────────┐              ┌──────────┐       │
│  │  wlan0   │              │  eth0    │       │
│  │ (WiFi AP)│              │(Ethernet)│       │
│  └────┬─────┘              └────┬─────┘       │
│       │                         │             │
└───────┼─────────────────────────┼─────────────┘
        │                         │
        │ 10.42.0.1              │ DHCP
        │                         │
   ┌────▼────┐              ┌─────▼──────┐
   │ Mobile  │              │ Boat       │
   │ Devices │              │ Network    │
   │ Tablets │              │ (Optional) │
   └─────────┘              └────────────┘
        │                         │
        │                         │
   WiFi Clients          Internet (optional)
   10.42.0.2 - .254
```

### 5.2 Network Services

| Service | Protocol | Port | Access | Purpose |
|---------|----------|------|--------|---------|
| **Main Menu** | HTTP | 80 | WiFi clients | Web interface |
| **Signal K** | WebSocket/HTTP | 3000 | WiFi clients | Marine data API |
| **Node-RED** | HTTP | 1880 | WiFi clients | Dashboard access |
| **Camera RTSP** | RTSP | 554 | WiFi clients | Video stream |
| **mDNS** | mDNS | 5353 | Local network | Service discovery |
| **SSH** | SSH | 22 | WiFi only (disabled by default) | Remote admin |

### 5.3 WiFi Access Point Configuration

```ini
SSID: d3kOS
Password: d3kos-2026
IP Address: 10.42.0.1/24
DHCP Range: 10.42.0.2 - 10.42.0.254
Security: WPA2-PSK
Mode: Access Point (hostapd)
Internet Sharing: Yes (if eth0 connected)
```

### 5.4 Access URLs

- Main Menu: `http://d3kos.local` or `http://10.42.0.1`
- Dashboard: `http://d3kos.local:1880/dashboard`
- Signal K: `http://d3kos.local:3000`
- Camera: `rtsp://d3kos.local:554/camera`

---

## 6. DATA ARCHITECTURE

### 6.1 Data Storage Structure

```
/opt/d3kos/
├── config/              # Permanent configuration
│   ├── onboarding.json
│   ├── benchmark-results.json
│   ├── license.json
│   └── engine-manufacturers.json
├── state/               # Runtime state
│   ├── onboarding-reset-count.json
│   └── pi-health-status.json
├── data/                # User data
│   ├── boat-log.txt
│   ├── camera/          # MP4 recordings
│   ├── historical.db    # SQLite database
│   └── exports/         # CSV/JSON exports
├── models/              # AI models
│   ├── vosk/            # STT model (50MB)
│   ├── piper/           # TTS voice
│   └── phi2/            # LLM (5GB)
└── logs/                # Application logs
    ├── onboarding.log
    ├── voice.log
    └── health.log
```

### 6.2 Data Persistence

| Data Type | Location | Format | Retention | Backup |
|-----------|----------|--------|-----------|--------|
| Onboarding config | `/opt/d3kos/config/` | JSON | Permanent | Daily |
| Engine baseline | `/opt/d3kos/config/` | JSON | Permanent | Daily |
| License info | `/opt/d3kos/config/` | JSON | Permanent | Daily |
| Boat log | `/opt/d3kos/data/` | Text | 30d (T0), ∞ (T2+) | Daily |
| Camera recordings | `/opt/d3kos/data/camera/` | MP4 | Until disk full | None |
| Historical metrics | `/opt/d3kos/data/` | SQLite | 90 days | Weekly |
| Voice recordings | `/opt/d3kos/data/voice/` | WAV | Temp (deleted after STT) | None |

### 6.3 Signal K Data Schema

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

### 6.4 Database Schema (SQLite)

```sql
-- Historical engine metrics
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

-- Anomaly log
CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT CHECK(level IN ('INFO', 'WARNING', 'CRITICAL')),
    metric TEXT,
    value REAL,
    baseline_value REAL,
    deviation REAL,
    message TEXT
);

-- Boat log entries
CREATE TABLE boat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entry TEXT,
    audio_file TEXT,
    transcription TEXT
);
```

---

## 7. VOICE ASSISTANT PIPELINE

### 7.1 Voice Processing Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Microphone  │ --> │ PocketSphinx│ --> │    Vosk     │ --> │   Phi-2     │
│   (Audio)   │     │ (Wake Word) │     │    (STT)    │     │   (LLM)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     16kHz             "Helm" detect      Transcription      AI Response
      WAV              < 500ms            < 1 second         < 1 second
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                     ▼
                              ┌─────────────┐
                              │    Piper    │
                              │    (TTS)    │
                              └─────────────┘
                                     ▼
                                  Speaker
                                 < 500ms
```

### 7.2 Pipeline Components

| Component | Technology | Size | Latency | Purpose |
|-----------|-----------|------|---------|---------|
| **Wake Word** | PocketSphinx | ~10MB | < 500ms | Detect "Helm" keyword |
| **STT** | Vosk (small-en-us) | 50MB | < 1s | Speech to text |
| **LLM** | Phi-2 (Q4_K_M) | 5GB | < 1s | Natural language understanding |
| **TTS** | Piper (en_US-amy) | ~20MB | < 500ms | Text to speech |

### 7.3 Voice Service Architecture

```
d3kos-voice.service (systemd)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Wake Word] [Command Parser]
  Thread      Thread
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │  Voice  │
    │ Engine  │
    └────┬────┘
         │
    ┌────┼────┐────┐
    ▼    ▼    ▼    ▼
  [STT] [LLM][TTS][Actions]
```

### 7.4 Command Architecture

**Supported Commands**:
- "What's the engine status?" → Read engine metrics
- "Any anomalies?" → Check anomaly log
- "Open OpenCPN" → Launch navigation software
- "Start benchmarking" → Begin baseline capture
- "Record boat log" → Start voice recording
- "Helm post" → Save log entry
- "Helm end" → Stop listening

---

## 8. SECURITY ARCHITECTURE

### 8.1 Security Layers

```
┌─────────────────────────────────────────┐
│         Application Security            │
│  - Local-only authentication            │
│  - Session management                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Network Security                │
│  - UFW firewall                         │
│  - WiFi WPA2-PSK encryption             │
│  - Rate limiting                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         System Security                 │
│  - SSH disabled by default              │
│  - Strong password policy               │
│  - Service isolation                    │
└─────────────────────────────────────────┘
```

### 8.2 Firewall Configuration

```bash
# UFW Rules
ufw allow in on wlan0 to any port 80      # HTTP
ufw allow in on wlan0 to any port 3000    # Signal K
ufw allow in on wlan0 to any port 1880    # Node-RED
ufw allow in on wlan0 to any port 554     # RTSP
ufw deny in on eth0 to any port 22        # Block SSH on ethernet
```

### 8.3 Licensing Architecture

**Tier Detection Logic**:
```
Boot → detect-tier.sh → Check for:
                         ├─ OpenCPN installed? → Tier 2
                         ├─ Subscription key? → Tier 3
                         └─ Neither → Tier 0
                              ↓
                         Update license.json
                              ↓
                         Enable/disable services
```

**Feature Matrix**:

| Feature | Tier 0 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|
| Dashboard | ✓ | ✓ | ✓ |
| Engine Monitoring | ✓ | ✓ | ✓ |
| Voice Assistant | ✗ | ✓ | ✓ |
| Camera | ✗ | ✓ | ✓ |
| Onboarding Resets | 10 max | Unlimited | Unlimited |
| Cloud Sync | ✗ | ✗ | ✓ |
| Remote Access | ✗ | ✗ | ✓ |

---

## APPENDIX: Component Versions

| Component | Version | License | Repository |
|-----------|---------|---------|------------|
| Raspberry Pi OS | Bookworm (64-bit) | Various | raspberrypi.org |
| Signal K | Latest stable | Apache 2.0 | signalk.org |
| Node-RED | 3.x | Apache 2.0 | nodered.org |
| GPSd | Latest | BSD | gpsd.org |
| PocketSphinx | Latest | BSD | cmusphinx.org |
| Vosk | 0.15 | Apache 2.0 | alphacephei.com/vosk |
| Piper | Latest | MIT | github.com/rhasspy/piper |
| llama.cpp | Latest | MIT | github.com/ggerganov/llama.cpp |
| OpenCPN | 5.8.x | GPL v2 | opencpn.org |

---

**END OF ARCHITECTURE DOCUMENT**
