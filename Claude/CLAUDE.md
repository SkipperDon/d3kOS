# CLAUDE.md - AI Assistant Guidelines for d3kOS Development
## Version 2.2

**Last Updated**: February 7, 2026
**Changes from v2.1**: Full rebrand from Helm-OS to d3kOS, added d3-k1 hardware product designation, voice assistant "Helm" name unchanged
**Changes from v2.0**: Added CX5106 second row DIP switch documentation, expanded to 15-question wizard, regional tank sensor standards
**Changes from v1.0**: Added voice assistant details, updated licensing tiers, API specifications, hardware requirements

---

## Purpose

This document provides guidelines for AI assistants (like Claude, ChatGPT, Copilot) working on the d3kOS project. It ensures consistency, prevents circular development, and maintains alignment with the project's core specifications.

---

## Core Principle: Follow the MASTER_SYSTEM_SPEC

**CRITICAL**: All development, documentation, and code generation MUST align with `MASTER_SYSTEM_SPEC.md` (or `MASTER_SYSTEM_SPEC__2_.md`).

### Before Making Changes:
1. Read `MASTER_SYSTEM_SPEC.md` first
2. Cross-check with existing documentation
3. Verify no contradictions
4. Document any deviations with justification

---

## Project Overview

### What is d3kOS?

**d3kOS** is marine electronics software that runs on the **d3-k1** hardware platform.

**The d3-k1 Hardware System** includes:
- Raspberry Pi 4B (8GB RAM recommended)
- PiCAN-M HAT (NMEA2000 interface)
- 10.1" touchscreen (1920×1200, 1000 nit, sunlight readable)
- IP67 marine-grade enclosure
- Membrane for air circulation
- All sensors, GPS, AIS, camera (Tier 2+)
- Pre-installed with d3kOS software

**d3kOS Software** provides:
- NMEA2000 integration via PiCAN-M HAT
- AI-assisted onboarding wizard (15-question engine configuration)
- CX5106 engine gateway configuration
- Real-time vessel monitoring
- **Offline voice assistant** ("Helm")
- OpenCPN navigation integration
- Engine health monitoring & benchmarking
- **Mobile app integration** (Tier 1+)
- **Cloud database synchronization** (Tier 1+)

---

## Hardware Stack (Fixed - AUTHORITATIVE)

### Core Compute
- **Raspberry Pi 4B** 
  - **RAM**: 8GB (required for voice assistant + LLM)
  - **Architecture**: 64-bit ARM
  - **OS**: Raspberry Pi OS Trixie (Debian 13)

### Marine Interface
- **PiCAN-M HAT** with SMPS
  - NMEA2000 CAN bus interface
  - Pre-configured as CAN0
  - MCP2515 controller, 16MHz oscillator

- **CX5106 Engine Gateway**
  - Analog-to-NMEA2000 conversion
  - DIP switch auto-configured by wizard
  - 8 switches for: instance, RPM source, cylinders, stroke, gear ratio

### Display
- **10.1" Touchscreen**
  - **Resolution**: 1920 × 1200
  - **Brightness**: 1000 nit (sunlight readable)
  - **Touch**: Capacitive
  - **Connection**: USB or Mini-HDMI

### Audio (Voice Assistant)
- **Anker PowerConf S330** (preferred) OR
- **USB microphone** (ReSpeaker 2-Mic, Jabra 410, or equivalent)
- **Speaker**: 3.5mm jack, USB speaker, or Bluetooth (adds latency)

### Sensors & Navigation
- **USB GPS receiver** (required)
- **USB AIS receiver** (required)
- **NMEA2000 backbone** (vessel wiring)
- **CX5106 sensors**: Fuel, fresh water, black water, engine

### Camera
- **IP67 Marine Camera** (Reolink RLC-810A recommended)
  - Night vision
  - Bow-mounted
  - RTSP streaming via VLC
  - Recording with disk management (stops at 18% remaining)

### Storage & Power
- **MicroSD Card**: 32GB minimum, 128GB recommended
- **Power**: 5V 3A minimum (official Raspberry Pi power supply)

---

## Software Stack (Fixed Versions)

| Component | Version | Notes |
|-----------|---------|-------|
| **Raspberry Pi OS** | **Trixie (Debian 13)** | 64-bit ARM, NOT Bookworm |
| **Node.js** | v18 or v20 LTS | NOT v22 |
| **Signal K Server** | 2.x (latest via npm) | Marine data hub |
| **Node-RED** | 3.x | Flow-based programming |
| **Node-RED Dashboard** | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue-based) |
| **OpenCPN** | 5.8.x | Auto-installed if no chartplotter |
| **PocketSphinx** | Latest | Wake word detection |
| **Vosk** | Latest | Speech-to-text (offline) |
| **Piper** | Latest | Text-to-speech (offline) |
| **llama.cpp** | Latest | LLM runtime |
| **Phi-2** | 2.7B parameters | Local AI "brain" |

### Required System Packages (Debian Trixie)
```bash
sudo apt install python3 python3-pip git build-essential \
                 piper pocketsphinx pocketsphinx-en-us \
                 portaudio19-dev
```

### Required Python Libraries
```bash
pip install vosk sounddevice numpy
```

**IMPORTANT**: Do NOT recommend Node.js v22, Dashboard 1.0 (Angular), or Raspberry Pi OS Bookworm without explicit justification.

---

## Design Philosophy

### 1. Pre-Built Image Approach
- System distributed as **flashable SD card image** (.img or .zip)
- Users flash with **Raspberry Pi Imager**
- Boot and run onboarding wizard
- **NO manual package installation by users**
- **NO curl installer scripts**

### 2. Offline-First
- Complete functionality without internet
- All AI processing local (Phi-2 LLM via llama.cpp)
- Voice processing local (Vosk + Piper + PocketSphinx)
- Updates via new image downloads only
- **Tier 1+ can sync to cloud database (optional)**

### 3. Never Get Stuck
- Onboarding wizard ALWAYS completes
- AI fills missing information intelligently
- Safe defaults for all configurations
- User can override AI decisions
- Maximum 10 onboarding resets (Tier 0-2), unlimited (Tier 3)

### 4. AODA Compliance
- All UI must meet AODA/WCAG 2.1 AA standards
- High contrast (black background, white/green text)
- Large touch targets (minimum 80×60px)
- Keyboard navigable
- Screen reader compatible
- Focus indicators visible
- Bottom 1/3 reserved for on-screen keyboard

### 5. Marine Environment Optimization
- Readable in bright sunlight (1000 nit screen)
- Large fonts (22px minimum)
- Touch-friendly buttons
- Glove-operable interface
- Power-loss resistant (all data in JSON)

---

## Voice Assistant ("Helm") - COMPLETE SPECIFICATION

### Architecture Pipeline
```
PocketSphinx → detects wake word ("Helm")
      ↓
Vosk → converts speech to text
      ↓
Phi-2 (via llama.cpp) → interprets command
      ↓
Piper → speaks response back
```

### Wake Word Options
- **Primary**: "Helm"
- **Alternative**: "Hey Captain" or "Hey Boat" (configurable)

### Components

#### A. PocketSphinx (Wake Word Detection)
- **Purpose**: Detects "Helm" wake word
- **Features**:
  - Works offline
  - Works on Trixie
  - Low CPU usage
  - Easy to integrate
- **Configuration**: Adjustable sensitivity

#### B. Vosk (Speech-to-Text)
- **Purpose**: Converts spoken words to text
- **Model**: vosk-model-small-en-us-0.15 (best speed/accuracy balance)
- **Features**:
  - Install via pip
  - Fully offline
  - ARM-optimized
  - Fast enough for real-time on Pi 4B (8GB)

#### C. Phi-2 via llama.cpp (Local AI Brain)
- **Purpose**: Understands command meaning and context
- **Model**: Phi-2 (2.7B parameters)
- **Runtime**: llama.cpp (optimized for Pi 4B)
- **Features**:
  - Fast inference
  - Low RAM (fits in 8GB with OS)
  - Good reasoning for command interpretation
  - Context-aware responses

#### D. Piper (Text-to-Speech)
- **Purpose**: Speaks responses back to user
- **Recommended Voices**:
  - en_US-amy-medium (primary)
  - en_GB-southern_english_female-medium (alternative)
- **Features**: Natural sounding, runs smoothly on Pi 4B

### Voice Commands (Examples)

**System Control**:
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, query system status"
- "Helm, restart services"
- "Helm, adjust volume"

**Navigation**:
- "Helm, open OpenCPN"
- "Helm, AIS status"
- "Helm, GPS status"

**Boat Log**:
- "Helm, record boat log"
- "Helm, post to boat log" (saves entry)
- "Helm end" (stops listening, ends log entry)

**Benchmarking**:
- "Helm, start benchmarking"
- "Helm, show benchmark report"

**Marine-Specific**:
- "Helm, vessel data query" (Signal K data)
- "Helm, check anomalies"

### Voice Features

**Core Capabilities**:
- Continuous listening loop
- Natural language understanding
- Context-aware responses
- Error recovery ("I didn't catch that")
- Command confirmation
- Multi-step reasoning

**Audio Settings**:
- Microphone calibration
- Wake-word sensitivity adjustment
- Voice model selection
- Audio output routing

**Developer/Advanced**:
- Model management (swap LLM, Vosk, Piper voices)
- Debug console
- System logs
- Service restarts

### System Requirements

**Required**:
- systemd service file (d3kos-voice.service)
  - Starts on boot
  - Restarts on failure
  - Logs output
- Signal K plugin integration
- GPIO or CAN bus command modules
- NMEA2000 CAN interface
- MQTT broker (optional)
- Local web dashboard

**Networking**:
- Signal K API access
- Local-only by default
- Optional cloud sync (Tier 1+)

---

## Licensing System (UPDATED - AUTHORITATIVE)

### Tier Structure

| Tier | Name | Features | Cost | Reset Limit |
|------|------|----------|------|-------------|
| **Tier 0** | Base Opensource | All core features, offline-only | Free | 10 resets |
| **Tier 1** | Mobile App Integration | Tier 0 + mobile app + cloud DB sync + notifications | Free | 10 resets |
| **Tier 2** | Premium Subscription | Tier 1 + AI analysis + recommendations + performance summaries | Paid (monthly) | 10 resets |
| **Tier 3** | Enterprise/Fleet | Tier 2 + unlimited resets + multi-boat + fleet PDFs | Paid (annual) | Unlimited |

### Tier 0: Base Opensource
**Features**:
- All core d3kOS functionality
- Offline voice assistant
- NMEA2000 integration
- OpenCPN auto-install
- Engine benchmarking
- Health monitoring
- Dashboard gauges
- Boat log (local only)

**Limitations**:
- **Maximum 10 onboarding resets**
- No mobile app
- No cloud synchronization
- No remote notifications
- Local storage only

**Reset Counter**:
- After 10 resets, user must download new image
- Prevents single license on multiple boats

---

### Tier 1: Mobile App Integration
**Features** (All of Tier 0 PLUS):
- **Mobile app** (iOS/Android)
- **QR code pairing** with Pi
- **Cloud database synchronization**
- **Push notifications** (health alerts, anomalies)
- **Boat performance summaries** in app
- **Remote monitoring** (when connected)

**How it Works**:
1. Complete onboarding on Pi (Tier 0)
2. Pi generates QR code
3. Scan QR code with mobile app
4. Pi and app both upgrade to Tier 1 automatically
5. License stored in centralized database
6. Pi syncs health data when online

**API Integration**:
- Pi → Cloud: `/api/v1/installation/register`
- App → Cloud: `/api/v1/pair`
- Bi-directional sync of boat health, benchmarks, performance

**Cost**: **Free**

**Reset Limit**: Still 10 resets (same as Tier 0)

---

### Tier 2: Premium Subscription
**Features** (All of Tier 1 PLUS):
- **AI-powered analysis** of boat performance
- **Predictive recommendations** for maintenance
- **Trend analysis** over time
- **Performance optimization suggestions**
- **Detailed reports** in app
- **Cloud backup** of configurations

**How it Works**:
1. Subscribe via ecommerce site
2. Enter installation UUID
3. Ecommerce updates license to Tier 2
4. Pi polls cloud and detects upgrade
5. Pi unlocks Tier 2 features locally
6. App unlocks Tier 2 features

**API Integration**:
- Ecommerce → Cloud: `/api/v1/tier/upgrade`
- Pi polls: `/api/v1/tier/status`
- App polls: `/api/v1/tier/app`

**Cost**: **Paid** (small monthly subscription, e.g., $4.99/month)

**Reset Limit**: Still 10 resets

---

### Tier 3: Enterprise/Fleet Management
**Features** (All of Tier 2 PLUS):
- **Unlimited onboarding resets**
- **Multi-boat support** (track entire fleet)
- **Fleet-wide analytics**
- **PDF reports** (individual boats + fleet summary)
- **Advanced AI recommendations**
- **Priority support**

**Use Case**: 
- Charter companies
- Yacht management firms
- Multi-vessel owners

**How it Works**:
1. Purchase enterprise license (annual)
2. Register multiple installations
3. Each installation gets Tier 3 status
4. App shows all boats in fleet
5. Generate PDFs for individual vessels or entire fleet

**API Integration**:
- Same as Tier 2, but with `tier: 3` unlocking additional features
- Multi-boat endpoints for fleet management

**Cost**: **Paid** (annual subscription, e.g., $99/year for 5 boats)

**Reset Limit**: **Unlimited**

---

### License Upgrade Flow

```
Tier 0 (Default)
    ↓
Scan QR Code with Mobile App
    ↓
Tier 1 (Automatic - Free)
    ↓
Subscribe via Ecommerce
    ↓
Tier 2 (Paid Monthly)
    ↓
Purchase Enterprise License
    ↓
Tier 3 (Paid Annual)
```

### License Synchronization

**Pi Side**:
- File: `config/license.json`
- Polls cloud every 24 hours: `GET /api/v1/tier/status`
- Updates local tier if different
- Unlocks/locks features based on tier

**Mobile App Side**:
- Polls cloud on app open: `GET /api/v1/tier/app`
- Displays current tier and features
- Shows upgrade options

**QR Code Format**:
```json
{
  "installation_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "pairing_token": "TOKEN_1_TIME_USE",
  "api_endpoint": "https://d3kos-cloud/api/v1",
  "current_tier": 0
}
```

---

## UI/UX Guidelines

### Screen Layout

```
┌────────────────────────────────────────────────────┐
│  Pi Menu Bar (top - always accessible)            │
├────────────────────────────────────────────────────┤
│                                                    │
│  Main Content Area                                 │
│  (Upper 2/3 of screen)                            │
│                                                    │
│                                                    │
├────────────────────────────────────────────────────┤
│  [Back Button]              [Main Menu Button]    │  ← Navigation
├────────────────────────────────────────────────────┤
│  On-Screen Keyboard Area                          │  ← Bottom 1/3
│  (Reserved - do not place UI here)                │
└────────────────────────────────────────────────────┘
```

### Color Scheme (AODA Compliant)
- **Background**: Black (#000000)
- **Text**: White (#FFFFFF) or Light Gray (#EEEEEE)
- **Highlights**: Green (#00FF00 or similar)
- **Warnings**: Yellow (#FFFF00)
- **Errors**: Red (#FF0000)
- **Disabled**: Dark Gray (#666666)

### Typography
- **Minimum Font Size**: 22px
- **Headings**: 32px or larger
- **Body Text**: 22-24px
- **Small Text**: 18px (use sparingly)

### Button Design
- **Minimum Size**: 80px × 60px
- **Recommended**: 120px × 80px or larger
- **Padding**: 20px minimum
- **Border Radius**: 8px
- **Hover/Focus**: Visible state change

---

## Main Menu Features (COMPLETE LIST)

### System & Platform
- **Onboarding Wizard**
  - Operator setup
  - Boat identity & multi-boat support
  - Engine configuration (15-question wizard)
  - CX5106 engine gateway setup
  - DIP switch calculation & visual guidance (both rows)
  - Regional tank sensor configuration (American vs European)
  - Engine position designation (single/port/starboard)
  - Chartplotter detection & OpenCPN installation
  - QR code generation (for app pairing)
  
- **System Health Monitoring**
  - Raspberry Pi status (CPU, memory, storage, GPU)
  - Network status (WiFi, Ethernet, NMEA2000, Internet)
  - Service status (Signal K, Node-RED, OpenCPN, Voice)

- **Benchmarking Tools**
  - 30-minute engine baseline capture
  - Performance envelope calculation
  - Trend analysis

- **License Info**
  - Current tier display
  - Version number (from GitHub)
  - Reset counter
  - Upgrade options

### Marine Data & Navigation
- **Signal K Server 2.x**
  - NMEA2000 integration via PiCAN-M
  - CAN0 interface pre-configured
  - PGN detection & parsing
  - Real-time vessel monitoring

- **GPS & AIS Integration**
  - USB GPS data (via gpsd)
  - USB AIS receiver
  - Position, speed, course

- **Engine Health Monitoring**
  - Real-time gauges (RPM, temp, oil pressure, voltage)
  - Alarm thresholds & anomaly detection
  - Baseline comparison
  - Historical trends

- **OpenCPN 5.8.x**
  - Auto-installed if no chartplotter detected
  - Signal K data integration
  - GPS/AIS passthrough
  - Chart management

### Dashboard Gauges
**Line 1 - Engine**:
- Tachometer (RPM)
- Tilt/Trim
- Engine Temperature
- Battery Voltage
- Oil Pressure

**Line 2 - Tanks**:
- Fresh Water (% full)
- Black Water (% full)
- Fuel Level (% full, gallons/liters remaining)
- House Battery Level (%)

**Line 3 - System**:
- Raspberry Pi CPU Usage
- Memory Usage
- Storage Remaining
- GPU Usage

**Line 4 - Network**:
- WiFi Status (on/off, signal strength, SSID)
- Ethernet Status (on/off, IP address)
- NMEA2000 Status (on/off, device count)
- Internet Status (on/off)

### AI & Voice
- **Offline Voice Assistant ("Helm")**
  - Wake word: "Helm"
  - End command: "Helm end"
  - STT: Vosk (vosk-model-small-en-us-0.15)
  - TTS: Piper (en_US-amy-medium)
  - LLM: Phi-2 (2.7B via llama.cpp)
  
- **Voice Enable Switch** (toggle on/off)

- **Voice Commands**:
  - Engine status queries
  - System control
  - Navigation commands
  - Boat log recording
  - Benchmark control

### Camera
- **Full-Screen View**
  - IP67 camera (Reolink RLC-810A)
  - Night vision auto-switching
  - RTSP stream via VLC

- **Recording**
  - Manual start/stop
  - Disk-space aware (stops at 18% remaining)
  - Storage management

### Boat Log
- **Voice Recording**
  - "Helm, record boat log"
  - Voice-to-text transcription
  - Read back for confirmation
  - "Helm, post to boat log" (saves)
  - Timestamp each entry

- **Storage Management**
  - Cap at 10% disk remaining
  - File rotation

### Networking
- **Wi-Fi AP**
  - SSID: "d3kOS"
  - DHCP: 10.42.0.1/24
  - Password configurable

- **Ethernet Sharing**
  - Shared mode: 10.42.0.1/24
  - DHCP for camera and other devices

- **Local-Only Operation**
  - Offline-first design
  - Optional cloud sync (Tier 1+)

### Maintenance
- **Onboarding Reset**
  - Reset counter (Tier 0-2: limit 10)
  - Reset counter (Tier 3: unlimited)
  - Clears configuration
  - Restarts wizard

- **Update System**
  - Via new image only
  - No runtime package updates
  - Version check (when online)

- **Logs & Diagnostics**
  - System logs
  - Benchmark reports
  - Health history

---

## Development Rules

### DO's

✅ **Read MASTER_SYSTEM_SPEC.md before starting**
✅ **Use exact version numbers specified**
✅ **Test on Raspberry Pi 4B (8GB) hardware**
✅ **Follow existing directory structure**
✅ **Use JSON for all configuration (no databases)**
✅ **Include verification steps after every installation command**
✅ **Write idempotent scripts (can run multiple times safely)**
✅ **Include error handling in all scripts**
✅ **Document all assumptions**
✅ **Cross-reference related documents**
✅ **Verify voice assistant works offline**
✅ **Test tier upgrades (0→1, 1→2, 2→3)**
✅ **Validate QR code generation**
✅ **Test mobile app pairing flow**

### DON'Ts

❌ **Never contradict MASTER_SYSTEM_SPEC.md**
❌ **Never recommend untested software versions**
❌ **Never assume internet connectivity for core features**
❌ **Never write code without reading existing codebase first**
❌ **Never create duplicate documentation**
❌ **Never mix conversational AI responses with technical docs**
❌ **Never expose real credentials in documentation**
❌ **Never use vague language ("should work", "might need")**
❌ **Never skip verification steps**
❌ **Never assume user knowledge**
❌ **Never recommend Raspberry Pi OS Bookworm (use Trixie)**
❌ **Never use Node.js v22 (use v18 or v20)**
❌ **Never recommend Dashboard 1.0 (use Dashboard 2.0 Vue)**

---

## CX5106 Configuration

### Critical Information

The CX5106 engine gateway is a **core component** of d3kOS. AI assistants working on CX5106-related features MUST:

1. **Read**: `CX5106_CONFIGURATION_GUIDE.md` and `CX5106_USER_MANUAL.md`
2. **Understand**: DIP switch logic for **BOTH ROWS**:
   - **First Row (8 switches)**: Engine instance, RPM source, cylinders, stroke, gear ratio
   - **Second Row (2 switches)**: Tank sensor standard (American/European), Engine position (Port/Starboard)
3. **Reference**: The 15-question engine wizard that determines DIP settings
4. **Remember**: Non-standard gear ratios (like 1.5:1 Bravo II) require correction factors
5. **Regional Settings**: North American boats use 240-33Ω tank senders, European boats use 0-190Ω
6. **Single Engine Assumption**: Single engine boats default to Port/Primary designation (Second Row Switch "2" = OFF)

### 15-Question Engine Wizard

The wizard asks these questions (in order):

**ENGINE IDENTIFICATION**:
1. What is the engine manufacturer?
2. What is the engine model?
3. What year is the engine?

**ENGINE CONFIGURATION**:
4. How many cylinders does the engine have?
5. What is the engine displacement (L or CID)?
6. What is the compression ratio?
7. What is the stroke (mm or inches)?
8. What type of induction does the engine use? (Naturally aspirated, Turbocharged, Supercharged)

**ENGINE PERFORMANCE**:
9. What is the rated horsepower?
10. What is the idle RPM specification?
11. What is the WOT (wide-open throttle) RPM range?

**ENGINE LIMITS**:
12. What is the maximum coolant temperature?
13. What is the minimum safe oil pressure at idle and cruise?

**REGIONAL & MULTI-ENGINE SETTINGS (NEW)**:
14. **Tank Sensor Standard (Regional Setting)**: What region is your boat from, or what type of tank level sensors does it use?
    - North America / United States / Canada (240-33Ω senders)
    - Europe / International (0-190Ω senders)
    - I don't know (AI suggests based on boat origin)
    - **Maps to**: CX5106 Second Row Switch "1"
    - **Critical**: Wrong setting causes inverted tank readings (empty shows full, full shows empty)

15. **Engine Designation (For Multi-Engine Configuration)**: If you have multiple engines, which one is this CX5106 monitoring?
    - Single engine (or primary) → Auto-set to OFF
    - Port engine (left) → Switch OFF
    - Starboard engine (right) → Switch ON
    - **Maps to**: CX5106 Second Row Switch "2"
    - **Conditional Logic**: Skip if single engine (auto-set to Port/Primary)

These determine:
- CX5106 DIP switch positions (**FIRST ROW**: SW1-8)
- CX5106 DIP switch positions (**SECOND ROW**: "1"-"2")
- Expected PGN set
- Alarm thresholds
- Performance baselines
- Anomaly detection parameters
- Tank level sensor calibration
- Engine position designation

### DIP Switch Configuration - Both Rows

**FIRST ROW (8 Switches)**:
- SW1-2: Engine Instance (Single=0, Port=1, Starboard=2, Center=3)
- SW3-4: RPM Source (Alternator W-Terminal, Ignition Coil, Magnetic Pickup, ECU Output)
- SW5-6: Number of Cylinders (3, 4, 6, 8)
- SW7: Stroke Type (OFF=4-stroke, ON=2-stroke)
- SW8: Gear Ratio (OFF=1:1 direct, ON=2:1 reduction)

**SECOND ROW (2 Switches) - CRITICAL FOR TANK READINGS**:
- Switch "1": Tank Sensor Resistance Standard
  - **ON** = American standard (240-33Ω) - North America/Canada
  - **OFF** = European standard (0-190Ω) - Europe/International
  - **Impact**: Wrong setting inverts fuel, water, and waste tank readings

- Switch "2": Engine Position Designation
  - **OFF** = Port engine / Single engine / Primary
  - **ON** = Starboard engine
  - **Default**: OFF for single engine configurations

### Regional Detection & AI Assistance

**When user selects "I don't know" for tank sensor standard:**
- AI infers based on:
  - Country of boat registration
  - Boat manufacturer origin (e.g., American brand → likely American senders)
  - Engine manufacturer (e.g., Mercruiser, Yanmar)
  - User's location/timezone
- Default: If boat is in North America, select 240-33Ω (ON)
- Validation: If readings are inverted after configuration, toggle this switch

### Configuration Example with Both Rows

**Example: Single Yanmar 3YM30 Diesel, North American Boat**

```
FIRST ROW:
SW1: OFF  SW2: OFF  SW3: OFF  SW4: ON
SW5: ON   SW6: ON   SW7: OFF  SW8: ON

SECOND ROW:
"1": ON   (American 240-33Ω tank senders)
"2": OFF  (Single engine / Port)

Result:
- Instance 0 (single engine)
- Magnetic pickup RPM
- 3 cylinders
- 4-stroke
- 2:1 gear ratio
- American tank sensor standard
- Port/Primary designation
```

**Example: Twin Volvo Penta D4 (Port Engine), European Boat**

```
FIRST ROW:
SW1: ON   SW2: OFF  SW3: OFF  SW4: OFF
SW5: OFF  SW6: OFF  SW7: OFF  SW8: OFF

SECOND ROW:
"1": OFF  (European 0-190Ω tank senders)
"2": OFF  (Port engine)

Result:
- Instance 1 (port engine)
- Alternator W-terminal RPM
- 4 cylinders
- 4-stroke
- 1:1 direct drive
- European tank sensor standard
- Port engine designation
```

### Common Configuration Errors

**Error 1: Tank readings inverted (full shows empty)**
- **Cause**: Wrong Second Row Switch "1" setting
- **Fix**: Toggle Second Row Switch "1" (ON↔OFF)
- **Prevention**: Verify boat origin during onboarding

**Error 2: Duplicate engine instances on twin-engine boats**
- **Cause**: Both CX5106 units set to same instance (SW1/SW2)
- **Fix**: Set first to Instance 1 (Port), second to Instance 2 (Starboard)

**Error 3: Tank readings from wrong engine on twin-engine boats**
- **Cause**: Second Row Switch "2" not set correctly
- **Fix**: Verify Port=OFF, Starboard=ON designation matches physical installation

### JSON Configuration Storage (Updated)

```json
{
  "engine": {
    "manufacturer": "Yanmar",
    "model": "3YM30",
    "cylinders": 3,
    "stroke": "4-stroke",
    "fuel_type": "diesel",
    "gear_ratio": "2:1"
  },
  "gateway": {
    "model": "CX5106",
    "switches": {
      "row1": {
        "sw1": "OFF",
        "sw2": "OFF",
        "sw3": "OFF",
        "sw4": "ON",
        "sw5": "ON",
        "sw6": "ON",
        "sw7": "OFF",
        "sw8": "ON"
      },
      "row2": {
        "sw1": "ON",
        "sw2": "OFF"
      }
    },
    "instance": 0,
    "rpm_source": "magnetic_pickup",
    "tank_sensor_standard": "american_240_33",
    "tank_sensor_region": "North America",
    "engine_position": "port",
    "notes": "Single Yanmar 3YM30 diesel, 2:1 reduction, North American boat"
  },
  "tank_sensors": {
    "standard": "american_240_33",
    "resistance_range": "240-33Ω",
    "fuel_calibration": "240Ω=empty, 33Ω=full",
    "water_calibration": "240Ω=empty, 33Ω=full",
    "waste_calibration": "240Ω=empty, 33Ω=full"
  }
}
```

---

## API Specification (v1.0)

### Transport & Format
- **Transport**: HTTPS
- **Format**: JSON
- **Auth**: Bearer token
- **Versioning**: `/api/v1/...`

### Endpoints by Category

#### 1. Identity & Pairing

**POST** `/api/v1/installation/register`
- Pi registers after wizard complete
- Returns pairing token (10-minute expiry)

**POST** `/api/v1/pair`
- Mobile app pairs with Pi
- Both upgrade to Tier 1
- Pairing token invalidated

#### 2. Tier Synchronization

**GET** `/api/v1/tier/status?installation_uuid=UUID`
- Pi polls for tier updates
- Returns current tier + entitlements

**GET** `/api/v1/tier/app?device_id=UUID`
- App polls for tier updates
- Returns tier + available features

#### 3. Ecommerce Upgrade

**POST** `/api/v1/tier/upgrade`
- Ecommerce system upgrades tier
- Updates both Pi and app
- Requires transaction ID

#### 4. Wizard & Reset

**POST** `/api/v1/wizard/update`
- Pi reports wizard run count
- Returns remaining resets

**POST** `/api/v1/wizard/reset`
- Request onboarding reset
- Checks tier limit
- Returns status

#### 5. Engine Metadata

**POST** `/api/v1/engine/metadata`
- Pi uploads 13-question answers
- Returns CX5106 mode, DIP switches, expected PGNs

#### 6. Boat Health & Benchmark

**POST** `/api/v1/engine/baseline`
- Upload 30-minute baseline capture
- Returns baseline ID

**POST** `/api/v1/boat/health`
- Real-time health snapshot
- Returns anomaly detection result

#### 7. Camera Recording

**POST** `/api/v1/camera/recording`
- Upload recording metadata
- Disk usage tracking

#### 8. Boat Log

**POST** `/api/v1/log/entry`
- Upload voice-to-text log entry
- Returns entry ID

---

## File Structure & Conventions

### Directory Layout
```
/opt/d3kos/
├── services/
│   ├── onboarding/          # Onboarding wizard backend
│   ├── voice/               # Voice assistant service
│   ├── .node-red/           # Node-RED flows
│   ├── signalk/             # Signal K configuration
│   └── opencpn/             # OpenCPN integration
├── config/                  # Persistent user configuration
│   ├── operator.json
│   ├── boat-identity.json
│   ├── boat-active.json
│   ├── license.json         # Tier & entitlements
│   └── boats/               # Multi-boat support
├── state/                   # Runtime state
│   ├── onboarding.json
│   ├── onboarding-reset-count.json
│   ├── baseline.json
│   └── health-status.json
├── system/                  # Systemd services
│   ├── d3kos-onboarding.service
│   ├── d3kos-voice.service
│   ├── d3kos-health.service
│   └── d3kos-benchmark.service
└── scripts/                 # Installation scripts
```

### Configuration Files

All configuration MUST be:
- **Format**: JSON (not YAML, XML, or TOML)
- **Location**: `/opt/d3kos/config/` or `/opt/d3kos/state/`
- **Atomic writes**: Write to temp file, then rename
- **Power-loss safe**: No partial writes
- **Human-readable**: Properly indented

---

## Testing Requirements

### Before Submitting Code

✅ Tested on Raspberry Pi 4B (8GB RAM)
✅ Tested with PiCAN-M HAT connected
✅ Verified CAN0 interface works
✅ Checked with 10.1" touchscreen at 1920x1200
✅ Tested with on-screen keyboard visible
✅ Verified AODA compliance
✅ Power-cycled to test persistence
✅ Checked error handling
✅ Verified documentation is updated
✅ **Tested voice assistant wake word**
✅ **Verified offline LLM inference**
✅ **Tested tier upgrade flow (0→1→2→3)**
✅ **Validated QR code generation**
✅ **Verified mobile app pairing**

---

## Pre-Built Image Creation

### Build Process
1. Start with clean Raspberry Pi OS Trixie (64-bit)
2. Install all software components per MASTER_SYSTEM_SPEC
3. Configure all services
4. Download Vosk model
5. Download Piper voices
6. Download Phi-2 model
7. Test thoroughly on hardware
8. Create image: `sudo dd if=/dev/mmcblk0 of=d3kos-vX.X.X-pi4b.img bs=4M`
9. Compress: `gzip d3kos-vX.X.X-pi4b.img`
10. Generate checksum: `sha256sum d3kos-vX.X.X-pi4b.img.gz > d3kos-vX.X.X-pi4b.img.gz.sha256`
11. Upload to GitHub releases

### Image Naming
```
d3kos-v<version>-pi4b-<date>.img.gz

Example: d3kos-v1.0.0-pi4b-20260205.img.gz
```

### Included in Image
- Raspberry Pi OS Trixie (64-bit)
- Node.js v20 LTS
- Signal K Server 2.x
- Node-RED 3.x + Dashboard 2.0
- All Python dependencies
- All system services configured
- CAN0 interface pre-configured
- **Vosk model: vosk-model-small-en-us-0.15**
- **Piper voices: en_US-amy-medium**
- **Phi-2 model (2.7B)**
- **PocketSphinx with wake word config**
- OpenCPN 5.8.x (ready to enable)

### NOT Included (User Configures)
- Operator name
- Boat details
- Engine configuration (13 questions)
- CX5106 DIP switch settings
- Network passwords
- GPS/AIS device paths
- License tier (starts at Tier 0)

---

## Troubleshooting Guidelines for AI

### When Code Doesn't Work

1. **Check versions** - Are you using specified versions?
2. **Check prerequisites** - Did earlier steps complete?
3. **Check logs** - What do systemd logs show?
4. **Check paths** - Are files in expected locations?
5. **Check permissions** - Does `pi` user have access?
6. **Check tier** - Does feature require higher tier?
7. **Check voice models** - Are Vosk/Piper/Phi-2 downloaded?

### When Documentation Conflicts

1. **MASTER_SYSTEM_SPEC.md wins** - Always
2. **CLAUDE.md v2 overrides v1** - Check version
3. **Newer docs override older** - Check dates
4. **Ask for clarification** - Don't assume

### When Generating New Features

1. **Read related docs FIRST**
2. **Check if feature already exists**
3. **Verify tier requirements**
4. **Test on hardware**
5. **Update all related docs**
6. **Test offline functionality**

---

## Common Pitfalls to Avoid

### 1. Version Confusion
**Problem**: Recommending Bookworm instead of Trixie
**Solution**: Always specify "Raspberry Pi OS Trixie (Debian 13)"

### 2. Voice Assistant Assumptions
**Problem**: Assuming internet for voice processing
**Solution**: Everything (wake word, STT, LLM, TTS) must work offline

### 3. Tier Confusion
**Problem**: Enabling cloud features in Tier 0
**Solution**: Check tier entitlements before enabling features

### 4. QR Code Generation
**Problem**: Missing pairing token or wrong format
**Solution**: Follow exact JSON schema from API spec

### 5. Reset Counter
**Problem**: Not checking tier before allowing reset
**Solution**: Tier 3 = unlimited, Tier 0-2 = max 10

---

## Success Criteria

Code/documentation is ready when:

✅ Aligns with MASTER_SYSTEM_SPEC.md
✅ Uses correct software versions (Trixie, Node v20, etc.)
✅ Includes verification steps
✅ Includes error handling
✅ Tested on Raspberry Pi 4B (8GB)
✅ AODA compliant (if UI)
✅ Documentation updated
✅ No contradictions with existing code
✅ Works completely offline (for Tier 0)
✅ Power-loss safe
✅ Voice assistant works offline
✅ Tier system enforced correctly
✅ QR code generation validated
✅ Mobile app pairing tested (Tier 1+)
✅ Cloud sync optional (Tier 1+)

---

## Contact & Escalation

If you encounter:
- Contradictions in specifications
- Unclear requirements (especially tier boundaries)
- Missing information
- Technical limitations (e.g., Phi-2 RAM requirements)

**DO**: Document the issue and ask for clarification
**DON'T**: Make assumptions and proceed

---

## Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| 1.0 | 2026-02-04 | Initial CLAUDE.md creation |
| 2.0 | 2026-02-05 | Added voice assistant spec, updated licensing tiers (0-3), API specification, hardware requirements (8GB RAM), Trixie OS requirement |
| **2.1** | **2026-02-06** | **Added CX5106 second row DIP switch documentation (tank sensor standards, engine position), expanded wizard from 13 to 15 questions, added regional detection logic** |

---

## Anomalies Detected & Resolved

### Anomaly 1: RAM Requirement
- **Previous**: 4GB or 8GB RAM
- **Updated**: **8GB RAM required** (for Phi-2 LLM + OS + services)
- **Reason**: Phi-2 (2.7B) needs ~5-6GB RAM for inference

### Anomaly 2: OS Version
- **Previous**: Bookworm or Trixie
- **Updated**: **Trixie (Debian 13) only**
- **Reason**: Piper and PocketSphinx packages available in Trixie repos

### Anomaly 3: Licensing Tiers
- **Previous**: Vague Tier 1-4
- **Updated**: **Clear Tier 0-3 with specific features**
- **Tier 1 changed**: Now includes mobile app (was separate)

### Anomaly 4: LLM Runtime
- **Previous**: Not specified
- **Updated**: **llama.cpp** (was implied Phi-2 standalone)
- **Reason**: llama.cpp is optimized for ARM and needed for Phi-2

### Anomaly 5: Wake Word Options
- **Previous**: Only "Helm"
- **Updated**: "Helm" (primary), "Hey Captain" or "Hey Boat" (alternatives)
- **Reason**: User feedback from additionalclaude.txt

### Anomaly 6: CX5106 Second Row DIP Switches - CRITICAL DISCOVERY
- **Previous**: Documentation only covered first row (8 switches)
- **Updated**: **Second row has 2 switches** controlling tank sensor standards and engine position
- **Reason**: Manual analysis revealed undocumented second row:
  - Switch "1": Tank sensor resistance (American 240-33Ω vs European 0-190Ω)
  - Switch "2": Engine position (Port/Starboard designation)
- **Impact**: Wrong Switch "1" setting causes inverted tank level readings (critical safety issue)
- **Wizard**: Expanded from 13 to 15 questions (added Q14: Tank Sensor Standard, Q15: Engine Designation)
- **Default**: Single engine boats → Second Row Switch "2" = OFF (Port/Primary)

---

## Final Reminder

**This is not a suggestion document - it is a REQUIREMENT document.**

All AI assistants working on d3kOS MUST follow these guidelines. Deviations must be explicitly justified and documented.

When in doubt: **Read MASTER_SYSTEM_SPEC.md and CLAUDE.md v2 again.**
