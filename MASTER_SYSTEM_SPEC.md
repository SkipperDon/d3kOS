# HELM-OS MASTER SYSTEM SPECIFICATION

**Version**: 2.0  
**Date**: February 6, 2026  
**Status**: APPROVED - All Recommendations Integrated  
**Previous Version**: 1.0 (February 4, 2026)

---

## DOCUMENT CONTROL

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-04 | Helm-OS Team | Initial specification |
| 2.0 | 2026-02-06 | Helm-OS Team | Integrated approved recommendations from gap analysis |

---

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

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview

Helm-OS is a comprehensive marine electronics system built on Raspberry Pi 4, designed to provide boat owners with advanced engine monitoring, navigation assistance, and voice-controlled operations. The system integrates NMEA2000 data, GPS/AIS information, camera surveillance, and AI-powered voice assistance into a unified, touchscreen-optimized interface.

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

- Boot time: < 60 seconds to operational
- Voice response time: < 2 seconds
- Dashboard update frequency: 1 Hz (1 second intervals)
- Anomaly detection accuracy: > 95%
- False positive rate: < 5%
- User onboarding completion: < 10 minutes

---

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
|-------|-----------|---------|---------|
| OS | Raspberry Pi OS (64-bit) | Bookworm | Base operating system |
| NMEA | Signal K Server | Latest | Marine data aggregation |
| Automation | Node-RED | 3.x | Data flow and dashboard |
| Navigation | OpenCPN | 5.8.x | Chart plotting (auto-install) |
| GPS | gpsd | Latest | GPS data processing |
| Voice (Wake) | PocketSphinx | Latest | Wake word detection |
| Voice (STT) | Vosk | 0.15 | Speech-to-text |
| Voice (TTS) | Piper | Latest | Text-to-speech |
| Voice (LLM) | Phi-2 | 2.7B | Local AI reasoning |
| Camera | VLC (libvlc) | Latest | RTSP stream viewer |
| UI | Chromium | Latest | Browser-based interface |
| Gestures | Touchégg | Latest | Touchscreen gestures |
| Keyboard | Onboard | Latest | On-screen keyboard |

---

## 3. HARDWARE SPECIFICATIONS

### 3.1 Minimum Requirements

| Component | Specification | Notes |
|-----------|---------------|-------|
| **Raspberry Pi** | 4 Model B, 4GB RAM | 8GB recommended for voice features |
| **SD Card** | 64GB Class 10 (A2) | 128GB recommended |
| **Power Supply** | 5V 3A USB-C | Official Raspberry Pi PSU required |
| **HAT** | PiCAN-M with micro-fit | NMEA2000 interface |
| **Display** | 10.1" 1920×1200 IPS | 1000 nit brightness, capacitive touch |
| **GPS** | USB GPS receiver | VK-162 or equivalent |
| **AIS** | USB AIS receiver | dAISy or equivalent |

### 3.2 Optional Hardware

| Component | Model | Purpose |
|-----------|-------|---------|
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

---

## 4. SOFTWARE ARCHITECTURE

### 4.1 Operating System Configuration

#### 4.1.1 Base OS
- **Distribution**: Raspberry Pi OS (64-bit) Bookworm
- **Kernel**: 6.1.x or later
- **Boot Mode**: Console auto-login → startx (no display manager)
- **Window Manager**: Openbox (lightweight)
- **Auto-start**: Chromium in maximized mode (NOT kiosk mode - preserve Pi menu access)

#### 4.1.2 System Services (systemd)

| Service | File | Purpose | Auto-start |
|---------|------|---------|------------|
| Signal K | `signalk.service` | Marine data server | Yes |
| Node-RED | `nodered.service` | Automation and dashboard | Yes |
| gpsd | `gpsd.service` | GPS data processing | Yes |
| Voice Assistant | `helm-voice.service` | Wake word and voice control | Yes (Tier 2+) |
| Camera Service | `helm-camera.service` | IP camera management | Yes (if camera detected) |
| Health Monitor | `helm-health.service` | System and engine monitoring | Yes |
| Boat Log | `helm-boatlog.service` | Voice log management | Yes (Tier 2+) |

#### 4.1.3 CAN Bus Configuration

```bash
# /etc/network/interfaces.d/can0
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 250000
    up /sbin/ifconfig can0 up
    down /sbin/ifconfig can0 down
```

### 4.2 Signal K Server Configuration

#### 4.2.1 Data Sources

```json
{
  "vessels": {
    "self": "urn:mrn:signalk:uuid:generated-on-install"
  },
  "pipedProviders": [
    {
      "id": "nmea2000-can0",
      "pipeElements": [
        {
          "type": "providers/simple",
          "options": {
            "type": "NMEA2000",
            "subOptions": {
              "type": "canbus",
              "interface": "can0"
            }
          }
        }
      ]
    },
    {
      "id": "gps-usb",
      "pipeElements": [
        {
          "type": "providers/gpsd",
          "options": {
            "port": 2947
          }
        }
      ]
    },
    {
      "id": "ais-usb",
      "pipeElements": [
        {
          "type": "providers/nmea0183",
          "options": {
            "port": "/dev/ttyUSB1",
            "baudrate": 38400
          }
        }
      ]
    }
  ]
}
```

#### 4.2.2 Data Keys (NMEA2000 PGNs)

| PGN | Description | Signal K Path | Update Rate |
|-----|-------------|---------------|-------------|
| 127488 | Engine Parameters, Rapid | `propulsion.*.rpm` | 100ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.*.oilPressure` | 500ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.*.temperature` | 500ms |
| 127505 | Fluid Level | `tanks.*.currentLevel` | 2500ms |
| 127508 | Battery Status | `electrical.batteries.*.voltage` | 1500ms |
| 128259 | Speed (Water Referenced) | `navigation.speedThroughWater` | 1000ms |
| 128267 | Water Depth | `environment.depth.belowTransducer` | 1000ms |
| 129025 | Position, Rapid Update | `navigation.position` | 100ms |
| 129026 | COG & SOG, Rapid Update | `navigation.courseOverGroundTrue` | 100ms |
| 129029 | GNSS Position Data | `navigation.gnss.*` | 1000ms |

### 4.3 Node-RED Configuration

#### 4.3.1 Dashboard Layout

**Dashboard 2.0 UI Configuration**:
- Base URL: `http://localhost:1880/dashboard`
- Theme: Dark (black background #000000)
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
```javascript
// Engine RPM monitoring
[signalk:in] → [threshold check] → [anomaly detector] → [dashboard gauge]
                                 ↓
                           [voice alert if critical]
                                 ↓
                           [log to file]
```

### 4.4 Voice Assistant Architecture

#### 4.4.1 Voice Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Microphone  │ --> │ PocketSphinx│ --> │    Vosk     │ --> │   Phi-2     │
│   (Audio)   │     │ (Wake Word) │     │    (STT)    │     │   (LLM)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                    "Helm" detected    Transcription        AI Response
                           │                   │                   │
                           └───────────────────┴───────────────────┘
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
```python
# /opt/helm-os/config/sphinx/helm.dict
HELM    HH EH L M

# /opt/helm-os/config/sphinx/helm.lm
# Language model with "Helm" as primary keyword
```

**Sensitivity Tuning**:
- Threshold: 1e-40 (adjust based on ambient noise)
- Buffer: 2048 samples
- Sample rate: 16kHz

#### 4.4.3 STT Configuration

**Vosk Model**:
- Model: `vosk-model-small-en-us-0.15`
- Size: 50MB
- Location: `/opt/helm-os/models/vosk/`
- Sample rate: 16kHz
- Real-time factor: < 0.5 (2x faster than real-time on Pi 4)

#### 4.4.4 TTS Configuration

**Piper Voice**:
- Voice: `en_US-amy-medium`
- Quality: Medium (balance speed vs quality)
- Sample rate: 22050Hz
- Speed: 1.0x (adjustable 0.8x - 1.5x)

#### 4.4.5 LLM Configuration

**Phi-2 (2.7B parameters)**:
- Quantization: Q4_K_M (5GB disk, 3GB RAM)
- Inference: llama.cpp (optimized for ARM)
- Context window: 2048 tokens
- Temperature: 0.7
- Max tokens: 100 (concise responses)

**Prompt Template**:
```
System: You are Helm, a concise marine assistant. Current boat status:
- Engine RPM: {rpm}
- Oil Pressure: {oil_psi} PSI
- Coolant Temperature: {coolant_temp}°F
- Fuel Level: {fuel_percent}%
- Battery Voltage: {voltage}V

User: {user_query}

Helm: [Respond in 1-2 sentences with actionable information]
```

#### 4.4.6 Command Parser

**Supported Commands**:
```javascript
const commands = {
  "what's the engine status": () => readEngineMetrics(),
  "any anomalies": () => checkAnomalies(),
  "open opencpn": () => launchOpenCPN(),
  "start benchmarking": () => startBenchmark(),
  "start onboarding": () => launchOnboarding(),
  "record boat log": () => startVoiceRecording(),
  "helm post": () => saveLogEntry(),
  "helm end": () => stopListening()
};
```

**Fuzzy Matching**:
- Use Levenshtein distance for command matching
- Threshold: 80% similarity
- Fallback: If no match, pass to LLM for interpretation

---

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
│  [< Back]               [Status Icons]        [Main Menu]  │
└─────────────────────────────────────────────────────────────┘
```

#### 5.1.2 Visual Design Specifications

**Colors**:
- Background: Pure black (#000000)
- Primary text: White (#FFFFFF)
- Accent: Green (#00CC00) for active elements
- Warning: Amber (#FFA500)
- Critical: Red (#FF0000)
- Disabled: Dark gray (#333333)

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
- Border: 2px solid #00CC00 (active) or #333333 (inactive)
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
   - Landmarks: `<nav>`, `<main>`, `<footer>`
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
```javascript
{
  "helm-os-voice-enabled": boolean,
  "helm-os-last-page": string,
  "helm-os-license-tier": 0 | 2 | 3,
  "helm-os-onboarding-complete": boolean,
  "helm-os-theme": "dark" (future: allow light theme)
}
```

**WebSocket Connection**:
```javascript
// Connect to backend services
const ws = new WebSocket('ws://localhost:3000/helm-os');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateUI(data);
};

// Send commands to backend
function sendCommand(cmd, params) {
  ws.send(JSON.stringify({ command: cmd, params }));
}
```

#### 5.1.5 Responsive Behavior

**Screen Size Adjustments**:
- 1920×1200 (primary): 3 columns, 4 rows
- 1280×800 (fallback): 2 columns, 6 rows
- Font scaling: Use CSS `clamp()` for fluid typography

**Keyboard Overlap Prevention**:
```css
.main-content {
  max-height: calc(100vh - 400px); /* Reserve 400px for keyboard */
  overflow-y: auto;
}

.keyboard-area {
  position: fixed;
  bottom: 0;
  height: 350px;
  z-index: 1000;
}
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
   1Hz        <10ms       <50ms       <100ms
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
```javascript
const thresholds = {
  rpm: { green: [0, 4500], yellow: [4500, 5500], red: [5500, 6000] },
  oilPressure: { green: [20, 100], yellow: [10, 20], red: [0, 10] },
  coolantTemp: { green: [100, 200], yellow: [200, 220], red: [220, 250] },
  voltage: { green: [12.5, 14.5], yellow: [11.5, 12.5], red: [10, 11.5] }
};
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
- Location: `/opt/helm-os/data/historical/`
- Format: SQLite database for efficient queries
- Retention: 90 days (auto-purge older data)
- Backup: Daily export to JSON (optional cloud sync in Tier 3)

### 5.3 Onboarding Wizard

#### 5.3.1 Wizard Flow

**13-Step Process**:
```
Welcome → Q1 → Q2 → ... → Q13 → CX5106 Config → QR Code → Complete
```

**Progress Indicator**:
- Visual: Progress bar (Step X of 13)
- Text: "Step 5 of 13: Engine Displacement"
- Navigation: Back, Next, Save & Exit

#### 5.3.2 Question Specifications

**Question 1: Engine Manufacturer**
- Input type: Autocomplete dropdown
- Data source: `/opt/helm-os/data/engine-manufacturers.json`
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
- Validation: Max > Min, reasonable range
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
- Validation: Cruise > Idle, reasonable range
- Default: 10 PSI idle, 40 PSI cruise

#### 5.3.3 CX5106 DIP Switch Configuration

**Output Format**:
```
┌─────────────────────────────────────────┐
│    CX5106 DIP Switch Configuration      │
├─────────────────────────────────────────┤
│                                         │
│   [Visual DIP Switch Diagram - 8 switches]
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
│   [Print] [Save PDF] [Next]             │
└─────────────────────────────────────────┘
```

**Calculation Logic**:
```javascript
function calculateDIPSwitches(engineData) {
  // Based on CLAUDE.md DIP switch rules
  const switches = {
    1: engineData.instance === 0 ? "ON" : "OFF",
    2: engineData.cylinders === 4 ? "ON" : "OFF",
    // ... (implement full logic from CLAUDE.md)
  };
  
  return {
    switches,
    explanation: generateExplanation(engineData, switches)
  };
}
```

#### 5.3.4 QR Code Generation

**Installation ID Generation**:
```javascript
const crypto = require('crypto');
const os = require('os');

function generateInstallationID() {
  const mac = os.networkInterfaces().eth0[0].mac;
  const timestamp = new Date().toISOString();
  const hash = crypto.createHash('sha256')
    .update(mac + timestamp)
    .digest('hex');
  
  return hash.substring(0, 16); // First 16 chars
}
```

**QR Code Content**:
```
helm-os://pair?id=abc123def456&version=1.0.3&tier=2
```

**Display**:
- Size: 300×300px
- Format: SVG (crisp on all displays)
- Label: "Scan to pair mobile app"
- Regenerate button: "Generate New Code"

#### 5.3.5 Reset Counter

**Counter File** (`/opt/helm-os/state/onboarding-reset-count.json`):
```json
{
  "reset_count": 7,
  "max_resets": 10,
  "last_reset": "2026-02-06T10:30:00Z",
  "warnings_shown": [8, 9],
  "tier": 0
}
```

**UI Display**:
- Location: Footer of every wizard page
- Text: "Resets used: 7/10 (Tier 0)"
- Color: Green (< 8), Yellow (8-9), Red (10)

**Warning Messages**:
- Reset 8: "Warning: Only 2 resets remaining. Consider upgrading to Tier 2 for unlimited resets."
- Reset 9: "Warning: This is your last reset. Next reset will require a fresh image download."
- Reset 10: "Maximum resets reached. Please download a fresh Helm-OS image or upgrade to Tier 2."

**Tier 2 Bypass**:
```javascript
if (tier >= 2) {
  // Unlimited resets for Tier 2+
  resetCount = 0; // Don't increment
}
```

### 5.4 Camera Interface

#### 5.4.1 Live View

**RTSP Stream Display**:
- Player: VLC (libvlc) embedded in HTML
- URL: `rtsp://admin:password@192.168.1.100:554/h264Preview_01_main`
- Resolution: 1920×1080 @ 30fps
- Latency: < 500ms
- Hardware decoding: GPU-accelerated (H.264)

**UI Controls**:
```
┌─────────────────────────────────────────┐
│         [Live Camera View]              │
│                                         │
│     (Full-screen RTSP stream)           │
│                                         │
├─────────────────────────────────────────┤
│ [● REC] [■ STOP] [⚫ SNAPSHOT] [PLAYBACK]│
│ Storage: 42% used (58% free)           │
│ Recording: 00:15:32                     │
└─────────────────────────────────────────┘
```

#### 5.4.2 Recording Management

**Storage Path**: `/opt/helm-os/data/camera/`

**File Naming**: `YYYYMMDD_HHMMSS_camera.mp4`

**Segmentation**: 10-minute chunks for easier playback

**Storage Safeguards**:
```javascript
function checkStorageBeforeRecording() {
  const diskFree = getDiskFreePercent();
  
  if (diskFree < 18) {
    alert("Cannot start recording. Disk space critically low (<18%).");
    return false;
  }
  
  if (diskFree < 20) {
    alert("Warning: Disk space low (<20%). Recording will auto-stop at 18%.");
  }
  
  return true;
}

function monitorStorageDuringRecording() {
  setInterval(() => {
    const diskFree = getDiskFreePercent();
    
    if (diskFree < 18) {
      stopRecording();
      alert("Recording stopped. Disk space critical (<18%).");
      deleteOldestRecordings(5); // Delete 5 oldest files
    }
  }, 10000); // Check every 10 seconds
}
```

**FIFO Deletion**:
```javascript
function deleteOldestRecordings(count) {
  const files = fs.readdirSync('/opt/helm-os/data/camera/')
    .filter(f => f.endsWith('.mp4'))
    .map(f => ({
      name: f,
      time: fs.statSync(`/opt/helm-os/data/camera/${f}`).mtime.getTime()
    }))
    .sort((a, b) => a.time - b.time);
  
  for (let i = 0; i < count && i < files.length; i++) {
    fs.unlinkSync(`/opt/helm-os/data/camera/${files[i].name}`);
    console.log(`Deleted: ${files[i].name}`);
  }
}
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

---

## 6. CORE FEATURES

### 6.1 Engine Health Monitoring

#### 6.1.1 Baseline Establishment

**Triggering**:
- Automatic: First engine start after onboarding
- Manual: "Engine Benchmark" button in main menu
- Voice: "Helm, start benchmarking"

**Data Collection** (30 minutes):
```javascript
const baseline = {
  timestamp: "2026-02-06T10:00:00Z",
  engine_hours: 245,
  samples: 1800, // 30 min × 60 sec × 1 Hz
  metrics: {
    rpm_idle: { mean: 720, stddev: 15, min: 690, max: 750 },
    rpm_cruise: { mean: 3200, stddev: 50, min: 3100, max: 3300 },
    temp_warmup_curve: [120, 140, 160, 175, 178, 180],
    temp_steady_state: 180,
    oil_pressure_idle: 12,
    oil_pressure_cruise: 45,
    fuel_rate_cruise: 4.2, // GPH
    voltage_charging: 14.2
  }
};
```

**Storage**: `/opt/helm-os/config/benchmark-results.json`

#### 6.1.2 Anomaly Detection

**Statistical Process Control (SPC)**:
```javascript
function detectAnomaly(current, baseline) {
  const deviation = Math.abs(current.value - baseline.mean);
  const sigma = baseline.stddev;
  
  if (deviation > 3 * sigma) {
    return { level: 'CRITICAL', message: `${current.name} is ${deviation.toFixed(1)} units from baseline (>3σ)` };
  } else if (deviation > 2 * sigma) {
    return { level: 'WARNING', message: `${current.name} is ${deviation.toFixed(1)} units from baseline (>2σ)` };
  } else if (deviation > 1 * sigma) {
    return { level: 'INFO', message: `${current.name} is slightly elevated` };
  }
  
  return { level: 'NORMAL', message: null };
}
```

**Example Anomalies**:
- RPM Instability: `stddev > 2 × baseline_stddev` → "Engine running rough"
- High Temperature: `temp > baseline + 15°F` → "Coolant temperature high"
- Low Oil Pressure: `pressure < baseline - 5 PSI` → "Oil pressure low"
- High Fuel Consumption: `rate > baseline × 1.2` → "Fuel consumption increased 20%"

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

**Monitoring Script** (`/opt/helm-os/services/health/pi-monitor.js`):
```javascript
const { exec } = require('child_process');

function getSystemMetrics() {
  return {
    cpu_temp: parseFloat(execSync('vcgencmd measure_temp').toString().match(/[\d.]+/)[0]),
    cpu_usage: parseFloat(execSync('top -bn1 | grep "Cpu(s)"').toString().match(/[\d.]+/)[0]),
    memory_usage: parseFloat(execSync('free | grep Mem').toString().split(/\s+/)[2]) / 
                   parseFloat(execSync('free | grep Mem').toString().split(/\s+/)[1]) * 100,
    disk_free: parseFloat(execSync('df -h / | tail -1').toString().split(/\s+/)[4].replace('%', '')),
    gpu_temp: parseFloat(execSync('vcgencmd measure_temp core').toString().match(/[\d.]+/)[0]),
    throttled: execSync('vcgencmd get_throttled').toString().includes('throttled=0x0') ? false : true
  };
}
```

**Update Frequency**: Every 10 seconds

**Storage**: `/opt/helm-os/state/pi-health-status.json`

#### 6.2.2 Thresholds and Alerts

**Alert Configuration**:
```javascript
const thresholds = {
  cpu_temp: { warning: 70, critical: 80 },
  cpu_usage: { warning: 70, critical: 90 },
  memory_usage: { warning: 70, critical: 90 },
  disk_free: { warning: 30, critical: 15 }
};
```

**Alert Actions**:
- **CPU Temp > 80°C**: 
  - Visual: Red gauge, flashing indicator
  - Voice: "Raspberry Pi overheating. Reduce load or improve cooling."
  - Action: None (user intervention required)

- **Memory > 95%**:
  - Visual: Red gauge
  - Voice: "Low memory. Restarting non-essential services."
  - Action: Restart camera service (if running)

- **Disk < 18%**:
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
[CPU: 45% @ 65°C] [Memory: 62%] [Storage: 42% used] [GPU: 58°C]
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

[View Logs] [Restart Services] [Close]
```

### 6.3 Licensing & Version Management

#### 6.3.1 Tier Detection

**License File** (`/opt/helm-os/config/license.json`):
```json
{
  "tier": 0,
  "installation_id": "abc123def456",
  "installed_apps": [],
  "reset_count": 7,
  "max_resets": 10,
  "version": "1.0.3",
  "last_update_check": "2026-02-06T14:30:00Z",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  }
}
```

**Tier Detection Logic**:
```javascript
function detectTier() {
  // Tier 2: OpenCPN or other paid apps installed
  if (fs.existsSync('/opt/opencpn')) {
    return { tier: 2, reason: 'OpenCPN installed' };
  }
  
  // Tier 3: Valid subscription key (future)
  if (fs.existsSync('/opt/helm-os/config/subscription.key')) {
    return { tier: 3, reason: 'Active subscription' };
  }
  
  // Tier 0: Default (opensource)
  return { tier: 0, reason: 'Default free tier' };
}
```

#### 6.3.2 Feature Restrictions

**Tier 0 (Opensource)**:
- ✓ Onboarding wizard (10 resets max)
- ✓ Dashboard (basic gauges)
- ✓ Engine health monitoring
- ✓ Pi health monitoring
- ✗ Voice assistant (disabled)
- ✗ Camera integration (disabled)
- ✓ Boat log (30 days retention)
- ✓ OpenCPN (can install to upgrade to Tier 2)

**Tier 2 (App-based)**:
- ✓ All Tier 0 features
- ✓ Unlimited onboarding resets
- ✓ Voice assistant (enabled)
- ✓ Camera integration (enabled)
- ✓ Boat log (unlimited retention)
- ✓ Historical graphs (90 days)
- ✗ Cloud sync (Tier 3 only)

**Tier 3 (Subscription)** (Future):
- ✓ All Tier 2 features
- ✓ Cloud sync
- ✓ Remote monitoring
- ✓ Multi-device access
- ✓ Priority support

#### 6.3.3 Version Management

**GitHub API Check**:
```javascript
async function checkForUpdates() {
  try {
    const response = await fetch('https://api.github.com/repos/helm-os/helm-os/releases/latest');
    const data = await response.json();
    const latestVersion = data.tag_name; // e.g., "v1.0.5"
    const currentVersion = "v1.0.3"; // From config
    
    if (latestVersion > currentVersion) {
      return {
        update_available: true,
        latest_version: latestVersion,
        download_url: data.assets[0].browser_download_url,
        release_notes: data.body
      };
    }
  } catch (error) {
    console.error('Failed to check for updates:', error);
  }
  
  return { update_available: false };
}
```

**UI Display**:
```
Main Menu Footer:
Version 1.0.3 | Latest: 1.0.5 - Update Available [View]

[Tap "View"]

Update Available: v1.0.5
Released: 2026-02-05

Release Notes:
- Fixed camera recording bug
- Improved voice assistant accuracy
- Updated dashboard gauges

[Download] [View on GitHub] [Close]
```

#### 6.3.4 QR Code Pairing

**QR Code Content**:
```
helm-os://pair?id=abc123def456&version=1.0.3&tier=2&boat=MyBoat
```

**Mobile App Use Case**:
- Scan QR code to pair mobile app with Helm-OS
- Mobile app can remotely view dashboard (Tier 3)
- Mobile app can view camera feed (Tier 2+)
- Mobile app can receive alerts (all tiers)

**Display Location**:
- Onboarding completion screen
- Main menu: "QR Code" button
- License info page

---

## 7. NETWORK ARCHITECTURE

### 7.1 WiFi Access Point

**Configuration** (`/etc/NetworkManager/system-connections/Helm-OS-AP`):
```ini
[connection]
id=Helm-OS-AP
type=wifi
autoconnect=true

[wifi]
mode=ap
ssid=Helm-OS

[wifi-security]
key-mgmt=wpa-psk
psk=helm-os-2026

[ipv4]
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
```bash
# Check if ethernet has internet
if ping -c 1 8.8.8.8 &> /dev/null; then
  # Enable sharing
  nmcli connection modify Helm-OS-AP ipv4.method shared
else
  # Direct mode
  nmcli connection modify Helm-OS-AP ipv4.method auto
fi
```

### 7.3 Network Services

**Firewall Configuration** (ufw):
```bash
# Allow incoming on WiFi interface (wlan0)
ufw allow in on wlan0 to any port 80     # HTTP
ufw allow in on wlan0 to any port 443    # HTTPS (future)
ufw allow in on wlan0 to any port 3000   # Signal K
ufw allow in on wlan0 to any port 1880   # Node-RED
ufw allow in on wlan0 to any port 554    # RTSP (camera)

# Block incoming on ethernet (eth0) for security
ufw deny in on eth0 to any port 22       # SSH
```

**mDNS (Avahi)**:
- Hostname: `helm-os.local`
- Service: `_http._tcp` (Web interface)
- Service: `_signalk._tcp` (Signal K server)
- Service: `_nodered._tcp` (Node-RED dashboard)

**Access URLs**:
- Main menu: `http://helm-os.local` or `http://10.42.0.1`
- Dashboard: `http://helm-os.local:1880/dashboard`
- Signal K: `http://helm-os.local:3000`
- Camera: `rtsp://helm-os.local:554/camera`

---

## 8. DATA MANAGEMENT

### 8.1 Data Storage Locations

| Data Type | Location | Format | Retention |
|-----------|----------|--------|-----------|
| Onboarding Config | `/opt/helm-os/config/onboarding.json` | JSON | Permanent |
| Engine Baseline | `/opt/helm-os/config/benchmark-results.json` | JSON | Permanent |
| License Info | `/opt/helm-os/config/license.json` | JSON | Permanent |
| Reset Counter | `/opt/helm-os/state/onboarding-reset-count.json` | JSON | Permanent |
| Pi Health Status | `/opt/helm-os/state/pi-health-status.json` | JSON | Overwrite |
| Boat Log | `/opt/helm-os/data/boat-log.txt` | Text | 30d (Tier 0), ∞ (Tier 2+) |
| Camera Recordings | `/opt/helm-os/data/camera/` | MP4 | Until disk full |
| Historical Data | `/opt/helm-os/data/historical.db` | SQLite | 90 days |
| Voice Recordings | `/opt/helm-os/data/voice/` | WAV | Temp (delete after STT) |

### 8.2 Backup & Restore

**Automated Backup** (Daily at 2 AM):
```bash
#!/bin/bash
# /opt/helm-os/scripts/backup.sh

BACKUP_DIR="/opt/helm-os/backups"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/helm-os/config/

# Backup state files
tar -czf $BACKUP_DIR/state_$DATE.tar.gz /opt/helm-os/state/

# Backup boat log
cp /opt/helm-os/data/boat-log.txt $BACKUP_DIR/boat-log_$DATE.txt

# Delete backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Restore Process**:
```bash
#!/bin/bash
# /opt/helm-os/scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: restore.sh <backup_file.tar.gz>"
  exit 1
fi

# Stop services
sudo systemctl stop signalk nodered

# Extract backup
tar -xzf $BACKUP_FILE -C /

# Restart services
sudo systemctl start signalk nodered

echo "Restore completed from: $BACKUP_FILE"
```

### 8.3 Data Export

**CSV Export** (for logs and historical data):
```javascript
// /opt/helm-os/services/export/csv-exporter.js

function exportToCSV(data, filename) {
  const csv = data.map(row => Object.values(row).join(',')).join('\n');
  const header = Object.keys(data[0]).join(',');
  const fullCSV = header + '\n' + csv;
  
  fs.writeFileSync(`/opt/helm-os/data/exports/${filename}`, fullCSV);
  
  return `/opt/helm-os/data/exports/${filename}`;
}

// Example usage
const historicalData = queryDatabase('SELECT * FROM engine_metrics WHERE timestamp > ?', [startDate]);
exportToCSV(historicalData, 'engine_data_2026-02.csv');
```

**JSON Export** (for configurations):
```javascript
function exportConfig() {
  const config = {
    onboarding: JSON.parse(fs.readFileSync('/opt/helm-os/config/onboarding.json')),
    baseline: JSON.parse(fs.readFileSync('/opt/helm-os/config/benchmark-results.json')),
    license: JSON.parse(fs.readFileSync('/opt/helm-os/config/license.json'))
  };
  
  fs.writeFileSync('/opt/helm-os/data/exports/helm-os-config.json', JSON.stringify(config, null, 2));
  
  return '/opt/helm-os/data/exports/helm-os-config.json';
}
```

---

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
- Run on boot: `/opt/helm-os/scripts/detect-tier.sh`
- Update license.json
- Enable/disable services based on tier

**No Phone-Home**:
- All tier detection is local (no cloud checks)
- No telemetry or analytics
- No license key validation servers

---

## 10. PERFORMANCE REQUIREMENTS

### 10.1 Boot Time

**Target**: < 60 seconds from power-on to fully operational

**Optimization Strategies**:
1. **Systemd Parallel Boot**: Enable parallel service startup
2. **Remove Unnecessary Services**: Disable Bluetooth, printer services
3. **Preload Models**: Cache Vosk and Piper models in RAM
4. **Fast SD Card**: Use Class 10 A2 for faster I/O
5. **Reduce Boot Messages**: Quiet kernel boot

**Measurement**:
```bash
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
```

### 10.2 Real-Time Performance

**Dashboard Update Frequency**:
- Engine metrics: 1 Hz (1000ms)
- Target latency: < 100ms from Signal K to UI update

**Voice Response Time**:
- Wake word detection: < 500ms
- STT transcription: < 1 second
- LLM inference: < 1 second
- TTS generation: < 500ms
- **Total**: < 2 seconds from "Helm" to response start

**Camera Latency**:
- RTSP stream: < 500ms from camera to display
- Recording start: < 1 second

### 10.3 Resource Usage

**CPU**:
- Idle: < 10%
- Dashboard only: < 20%
- Voice active: < 50%
- Camera recording: < 30%
- **Combined**: < 70% sustained

**Memory**:
- Base OS: 500MB
- Signal K + Node-RED: 300MB
- Voice (Phi-2 loaded): 3GB
- Camera buffering: 200MB
- **Total**: < 4GB (fits in 4GB Pi)

**Disk I/O**:
- Historical logging: < 1 MB/min
- Camera recording: 10 MB/min @ 1080p
- Total writes: < 100 MB/hour

**Network**:
- Signal K updates: < 10 KB/sec
- Camera stream (local): 5 MB/sec @ 1080p
- Dashboard updates: < 1 KB/sec

### 10.4 Storage Management

**Disk Usage Monitoring**:
```javascript
function monitorDiskUsage() {
  setInterval(() => {
    const diskFree = getDiskFreePercent();
    
    if (diskFree < 15) {
      // Critical: Delete oldest logs
      deleteOldestLogs(10);
    }
    
    if (diskFree < 18) {
      // Warning: Delete oldest camera recordings
      deleteOldestRecordings(5);
    }
    
    if (diskFree < 20) {
      // Info: Notify user
      showNotification('Disk space low (<20%). Consider deleting old data.');
    }
  }, 60000); // Check every minute
}
```

**Auto-Cleanup Priorities**:
1. Temporary files (voice recordings)
2. Oldest camera recordings
3. Logs older than 90 days
4. Historical data older than 90 days

---

## 11. TESTING & QUALITY ASSURANCE

### 11.1 Hardware Testing Matrix

| Hardware | Test Case | Expected Result | Pass/Fail |
|----------|-----------|-----------------|-----------|
| Pi 4 (4GB) | Boot time | < 60 seconds | |
| Pi 4 (8GB) | Voice + Camera + Dashboard | CPU < 70% | |
| PiCAN-M | NMEA2000 data reception | All PGNs received | |
| Touchscreen | Touch accuracy | < 5px error | |
| Touchscreen | On-screen keyboard | No overlap with content | |
| USB GPS | Position accuracy | < 10m error | |
| USB AIS | AIS message parsing | All messages decoded | |
| Anker S330 | Wake word detection | > 95% accuracy | |
| Reolink Camera | RTSP stream | < 500ms latency | |

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
- [ ] Main menu loads in < 5 seconds
- [ ] Onboarding wizard completes successfully
- [ ] All 13 questions collect valid data
- [ ] CX5106 DIP switches generate correctly
- [ ] Dashboard displays all gauges at 1Hz
- [ ] No AODA violations

**Phase 2 (Intelligence)**:
- [ ] Voice wake word detection > 95% accuracy
- [ ] Voice commands execute correctly
- [ ] Engine anomaly detection catches real issues
- [ ] False positive rate < 5%
- [ ] Pi health monitoring accurate
- [ ] Voice response time < 2 seconds

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

---

## 12. DEPLOYMENT & DISTRIBUTION

### 12.1 Pre-Built Image

**Image Build Process**:
```bash
#!/bin/bash
# /opt/helm-os/scripts/create-image.sh

# Install all dependencies
./install-signalk.sh
./install-nodered.sh
./install-opencpn.sh
./install-voice.sh
./install-camera.sh

# Configure services
./configure-autostart.sh
./configure-network.sh
./configure-touchscreen.sh

# Clean up
rm -rf /var/log/*
rm -rf /tmp/*
rm -rf ~/.bash_history

# Shrink filesystem
./shrink-filesystem.sh

# Create image
dd if=/dev/mmcblk0 of=/mnt/usb/helm-os-v1.0.3.img bs=4M status=progress

# Compress
gzip -9 /mnt/usb/helm-os-v1.0.3.img

# Generate checksum
sha256sum /mnt/usb/helm-os-v1.0.3.img.gz > /mnt/usb/helm-os-v1.0.3.img.gz.sha256
```

**Image Hosting**:
- Platform: GitHub Releases
- File: `helm-os-v1.0.3.img.gz` (~4GB compressed)
- Checksum: `helm-os-v1.0.3.img.gz.sha256`
- Release notes: Changelog + known issues

### 12.2 Flashing Guide

**Recommended Tool**: Raspberry Pi Imager

**Steps**:
1. Download `helm-os-v1.0.3.img.gz` from GitHub
2. Verify checksum: `sha256sum -c helm-os-v1.0.3.img.gz.sha256`
3. Open Raspberry Pi Imager
4. Choose OS → Use custom → Select downloaded .img.gz
5. Choose storage → Select SD card
6. Write → Wait for completion
7. Insert SD card into Raspberry Pi
8. Power on → Wait for first boot (2-3 minutes)
9. Connect to WiFi "Helm-OS" (password: helm-os-2026)
10. Open browser → `http://helm-os.local` or `http://10.42.0.1`
11. Complete onboarding wizard

### 12.3 First Boot Configuration

**Auto-Start Sequence**:
1. Expand filesystem to full SD card size
2. Generate unique installation ID
3. Create default license.json (Tier 0)
4. Start Signal K, Node-RED, gpsd
5. Launch Chromium in maximized mode
6. Display onboarding wizard

**First-Time Setup**:
- Onboarding wizard auto-launches
- User completes 13 questions
- CX5106 DIP switches displayed
- QR code generated
- Main menu loads

---

## 13. MAINTENANCE & SUPPORT

### 13.1 Logging

**Log Locations**:
- System logs: `/var/log/syslog`
- Signal K logs: `/home/signalk/.signalk/logs/`
- Node-RED logs: `/home/pi/.node-red/logs/`
- Helm-OS logs: `/opt/helm-os/logs/`

**Log Rotation**:
```bash
# /etc/logrotate.d/helm-os
/opt/helm-os/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### 13.2 Troubleshooting

**Common Issues**:

1. **Boot fails** → Check SD card, reflash image
2. **No dashboard display** → Check Node-RED service: `sudo systemctl status nodered`
3. **No NMEA2000 data** → Check CAN0 interface: `ifconfig can0`
4. **Voice not responding** → Check microphone: `arecord -l`
5. **Camera not connecting** → Check RTSP URL and network

**Debug Mode**:
```bash
# Enable verbose logging
export HELM_DEBUG=1
sudo systemctl restart helm-*
```

### 13.3 Updates

**Update Process**:
1. Download new image from GitHub
2. Backup configuration: `/opt/helm-os/scripts/backup.sh`
3. Flash new image to new SD card
4. Boot with new SD card
5. Restore configuration: `/opt/helm-os/scripts/restore.sh backup_file.tar.gz`

**In-Place Updates** (Future):
```bash
# /opt/helm-os/scripts/update.sh
wget https://github.com/helm-os/helm-os/releases/latest/download/helm-os-update.tar.gz
tar -xzf helm-os-update.tar.gz
./install.sh
sudo systemctl restart helm-*
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

---

## 14. APPENDICES

### Appendix A: Hardware Bill of Materials

| Item | Part Number | Quantity | Estimated Cost (USD) |
|------|-------------|----------|----------------------|
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
| **Total** | | | **$532** |

### Appendix B: Software Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| signalk-server | Latest | Apache 2.0 | Marine data aggregation |
| node-red | 3.x | Apache 2.0 | Automation and dashboard |
| gpsd | Latest | BSD | GPS data processing |
| pocketsphinx | Latest | BSD | Wake word detection |
| vosk | 0.15 | Apache 2.0 | Speech-to-text |
| piper | Latest | MIT | Text-to-speech |
| llama.cpp | Latest | MIT | LLM inference |
| opencpn | 5.8.x | GPL | Chart plotting |
| chromium | Latest | BSD | Web browser |
| touchegg | Latest | GPL | Gesture support |
| onboard | Latest | GPL | On-screen keyboard |

### Appendix C: PGN Mapping Reference

| PGN | Parameter | Signal K Path | Unit |
|-----|-----------|---------------|------|
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
POST /signalk/v1/api/vessels/self/_attr
```

**Helm-OS API**:
```
GET  /api/health                  # System health status
GET  /api/engine/baseline         # Engine baseline data
GET  /api/engine/current          # Current engine metrics
POST /api/engine/benchmark/start  # Start benchmarking
POST /api/voice/enable            # Enable voice assistant
POST /api/onboarding/reset        # Reset onboarding wizard
GET  /api/license                 # License information
```

### Appendix E: File System Layout

```
/opt/helm-os/
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
│   ├── install-*.sh
│   ├── configure-*.sh
│   ├── backup.sh
│   └── restore.sh
├── models/
│   ├── vosk/
│   ├── piper/
│   └── phi2/
└── logs/
    ├── onboarding.log
    ├── voice.log
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

---

## DOCUMENT APPROVAL

This specification has been reviewed and approved by:

- [ ] Technical Lead
- [ ] UX/UI Designer
- [ ] QA Engineer
- [ ] Project Manager

**Approval Date**: _________________

**Next Review Date**: After Phase 1 completion

---

**END OF DOCUMENT**

---

## CHANGE LOG

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
