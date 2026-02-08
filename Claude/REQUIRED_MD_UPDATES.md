# Required Updates to Existing .md Files

**Analysis Date**: February 4, 2026  
**Status**: Identifies gaps between current documentation and actual requirements

---

## SUMMARY OF REQUIRED UPDATES

| Document | Current State | Updates Needed | Priority |
|----------|---------------|----------------|----------|
| README.md | Good base | 8 major updates | HIGH |
| INSTALLATION_GUIDE.md | Complete for manual install | 5 major updates | HIGH |
| ARCHITECTURE.md | Good technical detail | 7 major updates | MEDIUM |
| ONBOARDING_FLOW.md | Incomplete | 10 major updates | HIGH |
| SCRIPTS_REFERENCE.md | Good foundation | 3 major updates | LOW |

---

## 1. README.md - REQUIRED UPDATES

### ❌ CRITICAL MISSING CONTENT

#### 1.1 Pre-Built Image Approach (HIGH PRIORITY)
**Current**: Describes manual installation via scripts  
**Required**: Change to pre-built image download and flash

**Add Section**:
```markdown
## Quick Start (5 Minutes)

### Download Pre-Built Image
```bash
# Download latest release from GitHub
wget https://github.com/YOUR_USERNAME/d3kos/releases/latest/d3kos-v1.0.0-pi4b.img.gz

# Verify SHA256 checksum
sha256sum d3kos-v1.0.0-pi4b.img.gz
# Compare with: <CHECKSUM_HERE>
```

### Flash to SD Card
```bash
# Linux/Mac
gunzip d3kos-v1.0.0-pi4b.img.gz
sudo dd if=d3kos-v1.0.0-pi4b.img of=/dev/sdX bs=4M status=progress
sync

# Windows: Use Raspberry Pi Imager or Etcher
```

### First Boot
1. Insert SD card into Raspberry Pi 4B
2. Connect monitor, keyboard (optional)
3. Power on
4. Wait for automatic boot (~60 seconds)
5. Follow on-screen onboarding wizard
```

---

#### 1.2 Voice Assistant Information (HIGH PRIORITY)
**Current**: Brief mention only  
**Required**: Full "Helm" voice assistant description

**Add Section**:
```markdown
## Voice Assistant - "Helm"

d3kOS includes a fully offline voice assistant called "Helm".

### Wake Word
Say **"Helm"** to activate listening mode

### Supported Commands
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, open OpenCPN"
- "Helm, start benchmarking"
- "Helm, record boat log"
- "Helm, post to boat log"
- "Helm end" (stop listening)

### Technology Stack
- **Wake Word**: PocketSphinx
- **Speech-to-Text**: Vosk (offline)
- **Text-to-Speech**: Piper (offline)
- **AI Brain**: Phi-2 (2.7B parameters, local)

**100% Offline** - No internet required, all processing on Raspberry Pi
```

---

#### 1.3 Licensing Tiers (HIGH PRIORITY)
**Current**: Says "To be determined"  
**Required**: Full tier breakdown

**Replace License Section**:
```markdown
## Licensing

### Tier Structure

| Tier | Features | Cost | Onboarding Resets |
|------|----------|------|-------------------|
| **Tier 0** | All core features | Free | 10 maximum |
| **Tier 1** | Reserved for future | TBD | TBD |
| **Tier 2** | App integration | TBD | TBD |
| **Tier 3** | Premium + cloud sync | Paid | Unlimited |
| **Tier 4** | Enterprise/fleet | Paid | Unlimited |

### Tier 0 Limitations
- Maximum 10 onboarding resets
- After 10 resets, download new image
- Prevents single license on multiple boats
- All opensource components included

### Upgrading
Tier 3 and 4 available via ecommerce site (future)
```

---

#### 1.4 Hardware Requirements Update (MEDIUM PRIORITY)
**Current**: Generic list  
**Required**: Match lookandfeeld3kos.txt exactly

**Update Hardware Section**:
```markdown
## Hardware Requirements

### Verified Configuration (Raspberry Pi 4B)
- **Raspberry Pi 4B** (4GB or 8GB RAM) - Required
- **PiCAN-M HAT** with SMPS - Required
- **MicroSD Card** (32GB minimum) - Required
- **10.1" Touchscreen** (1920x1200, 1000 nit brightness) - Required
- **CX5106 Engine Gateway** - For analog engine data
- **USB GPS Receiver** - Required
- **USB AIS Receiver** - Required
- **Anker PowerConf S330** - Microphone + speaker for voice
- **PoE Switch** - For IP camera
- **Reolink RLC-810A Camera** - IP67, night vision
- **NMEA2000 Backbone** - Connection to vessel network

### Display Requirements
- Minimum resolution: 1920x1200
- Brightness: 1000 nit (sunlight readable)
- Touch-enabled
- USB or Mini-HDMI connection
```

---

#### 1.5 Software Stack Version Update (MEDIUM PRIORITY)
**Current**: Shows Node.js v20, Node-RED 3.1.x  
**Required**: Clarify Raspberry Pi OS version

**Update Software Stack Table**:
```markdown
| Component           | Version  | Purpose                        |
|---------------------|----------|--------------------------------|
| Raspberry Pi OS     | Trixie (Debian 13) | Base operating system |
| Node.js             | v18 or v20 LTS | Runtime (NOT v22) |
| Signal K Server     | 2.x (latest) | Marine data hub |
| Node-RED            | 3.x | UI and automation |
| Node-RED Dashboard  | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue) |
| OpenCPN             | 5.8.x | Navigation (optional) |
| Vosk                | Latest | Speech-to-text |
| Piper               | Latest | Text-to-speech |
| PocketSphinx        | Latest | Wake word detection |
| Phi-2               | 2.7B | Local AI brain |
```

---

#### 1.6 Main Menu Features (MEDIUM PRIORITY)
**Current**: Not mentioned  
**Required**: List all main menu buttons

**Add Section**:
```markdown
## Main Menu Features

The d3kOS main menu provides access to:

### System Functions
- **Voice Enable** - Toggle voice assistant on/off
- **Camera** - Live view and recording from bow camera
- **OpenCPN** - Launch/manage navigation software
- **Dashboard** - Real-time engine and system gauges

### Configuration
- **Onboarding Wizard** - Initial setup or reconfiguration
- **License Info** - View tier and version information
- **QR Code** - Mobile app pairing

### Monitoring
- **Engine Benchmark** - Establish performance baseline
- **Boat Health** - Real-time health monitoring
- **Boat Performance** - Historical performance tracking
- **Raspberry Pi Status** - System health metrics
- **Boat Log** - Voice-to-text logging system
```

---

#### 1.7 UI/UX Information (LOW PRIORITY)
**Current**: Not mentioned  
**Required**: AODA compliance and design specs

**Add Section**:
```markdown
## User Interface

### Design Specifications
- **AODA/WCAG 2.1 AA Compliant**
- **Color Scheme**: Black background, white/green text
- **Font Size**: 22px minimum for readability
- **Touch Targets**: 80x60px minimum (120x80px recommended)
- **On-Screen Keyboard**: Bottom 1/3 reserved
- **Navigation**: Back (left) and Main Menu (right) always visible

### Display Optimization
- Optimized for 1000 nit sunlight-readable displays
- Large touch-friendly buttons
- Glove-operable interface
- Readable at distance (helm position)
```

---

#### 1.8 QR Code Pairing (LOW PRIORITY)
**Current**: Not mentioned  
**Required**: Mobile app pairing explanation

**Add Section**:
```markdown
## Mobile App Integration

After completing onboarding, d3kOS generates a unique QR code for pairing with the mobile app (future feature).

### QR Code Contains
- Installation UUID
- Vessel identification
- License tier
- Configuration snapshot
```

---

## 2. INSTALLATION_GUIDE.md - REQUIRED UPDATES

### ❌ CRITICAL CHANGES NEEDED

#### 2.1 Change from Manual Install to Image Flashing (HIGH PRIORITY)
**Current**: 11-step manual installation  
**Required**: Image flashing guide

**Replace Entire Document** with:
```markdown
# d3kOS Installation Guide

## Overview

d3kOS is distributed as a **pre-built Raspberry Pi image**. Simply flash to an SD card and boot.

## Prerequisites

### Required Hardware
- Raspberry Pi 4B (4GB or 8GB RAM)
- MicroSD card (32GB minimum, Class 10 or better)
- MicroSD card reader
- Computer (Windows, Mac, or Linux)

### Required Software
- Raspberry Pi Imager (recommended) OR
- Etcher OR
- dd command (Linux/Mac)

---

## Installation Steps

### Step 1: Download d3kOS Image

```bash
# Download latest release
wget https://github.com/YOUR_USERNAME/d3kos/releases/latest/d3kos-vX.X.X-pi4b.img.gz

# Download SHA256 checksum file
wget https://github.com/YOUR_USERNAME/d3kos/releases/latest/d3kos-vX.X.X-pi4b.img.gz.sha256
```

### Step 2: Verify Image Integrity

```bash
# Linux/Mac
sha256sum -c d3kos-vX.X.X-pi4b.img.gz.sha256

# Expected output:
# d3kos-vX.X.X-pi4b.img.gz: OK
```

### Step 3: Flash Image to SD Card

#### Option A: Raspberry Pi Imager (Recommended)
1. Launch Raspberry Pi Imager
2. Click "Choose OS" → "Use custom"
3. Select downloaded .img.gz file
4. Click "Choose Storage" → Select your SD card
5. Click "Write"
6. Wait for completion (~15 minutes)

#### Option B: Linux/Mac Command Line
```bash
# Decompress image
gunzip d3kos-vX.X.X-pi4b.img.gz

# Flash to SD card (replace /dev/sdX with your SD card device)
sudo dd if=d3kos-vX.X.X-pi4b.img of=/dev/sdX bs=4M status=progress
sync
```

#### Option C: Windows (Etcher)
1. Download and install Etcher
2. Select d3kOS .img.gz file
3. Select SD card drive
4. Click "Flash"

### Step 4: First Boot

1. **Eject SD card safely** from computer
2. **Insert SD card** into Raspberry Pi 4B
3. **Connect hardware**:
   - PiCAN-M HAT installed
   - 10.1" touchscreen connected
   - USB GPS and AIS connected
   - Anker PowerConf S330 connected
   - Power supply connected (but not powered on yet)
4. **Power on** the Raspberry Pi
5. **Wait** for boot (~60 seconds)

**Expected Behavior**:
- Screen shows d3kOS logo
- Boot messages scroll (if monitor connected)
- Onboarding wizard launches automatically

### Step 5: Complete Onboarding

Follow the on-screen onboarding wizard to configure:
1. Operator name
2. Vessel information
3. Engine details (13 questions)
4. Chartplotter detection
5. CX5106 DIP switch configuration
6. Baseline benchmark (optional)

**Duration**: 10-20 minutes depending on configuration

---

## Verification

After onboarding completes:

```bash
# SSH into d3kOS (optional)
ssh pi@d3kos.local

# Check all services running
systemctl status signalk
systemctl status nodered
systemctl status can0
systemctl status d3kos-onboarding
```

**Expected**: All services show "Active: active (running)"

---

## Troubleshooting

### Image Won't Flash
- Verify SD card is at least 32GB
- Try different SD card
- Verify image SHA256 checksum

### Won't Boot
- Check power supply (5V 3A minimum)
- Verify SD card is fully inserted
- Try re-flashing image

### Onboarding Doesn't Start
- Wait full 60 seconds after boot
- Check touchscreen connection
- Reboot and try again

---

## Network Configuration (Post-Installation)

After onboarding, d3kOS creates:
- **WiFi AP**: SSID "d3kOS"
- **Ethernet**: Shared mode at 10.42.0.1/24

Access points:
- **Main UI**: http://d3kos.local:1880
- **Signal K**: http://d3kos.local:3000
- **OpenCPN**: Launch from main menu

---

## What's Pre-Installed

The image includes everything:
- Raspberry Pi OS Trixie (64-bit)
- Node.js v20 LTS
- Signal K Server 2.x
- Node-RED 3.x + Dashboard 2.0
- OpenCPN 5.8.x
- Vosk STT models
- Piper TTS voices
- Phi-2 (2.7B) LLM
- All system services configured
- CAN0 interface pre-configured

**No additional software installation required.**
```

---

#### 2.2 Add Image Creation Section (MEDIUM PRIORITY)
**Current**: Not documented  
**Required**: For developers creating custom images

**Add Section**:
```markdown
## For Developers: Creating Custom Images

### Build Your Own Image

```bash
# Start with clean Pi
# Install all components per MASTER_SYSTEM_SPEC.md
# Test thoroughly

# Create image
sudo dd if=/dev/mmcblk0 of=d3kos-custom.img bs=4M status=progress

# Compress
gzip d3kos-custom.img

# Generate checksum
sha256sum d3kos-custom.img.gz > d3kos-custom.img.gz.sha256
```

See `DEPLOYMENT.md` for complete build process.
```

---

#### 2.3 Remove Manual Installation Steps (HIGH PRIORITY)
**Current**: Steps 1-11 for manual install  
**Required**: Delete entirely (pre-built image only)

**Action**: Replace with image flashing guide above

---

#### 2.4 Update Version Table (MEDIUM PRIORITY)
**Current**: Shows Node-RED 3.1.x  
**Required**: Clarify Dashboard 2.0

**Update Table**:
```markdown
| Component           | Version  | Notes                          |
|---------------------|----------|--------------------------------|
| Raspberry Pi OS     | Trixie | Debian 13, 64-bit |
| Node.js             | v18 or v20 LTS | NOT v22 |
| Signal K Server     | 2.x (latest) | Install via npm |
| Node-RED            | 3.x | Install via npm |
| Node-RED Dashboard  | 2.0.4-1 | Dashboard 2.0 (Vue-based) |
| OpenCPN             | 5.8.x | Auto-installed if needed |
| Python              | 3.11+ | System default on Trixie |
```

---

#### 2.5 Add First-Boot Configuration (MEDIUM PRIORITY)
**Current**: Not documented  
**Required**: What happens on first boot

**Add Section**:
```markdown
## First Boot Process

1. **Boot Sequence** (~60 seconds):
   - Raspberry Pi logo
   - System initialization
   - Service startup
   - Network configuration

2. **Automatic Actions**:
   - CAN0 interface brought up
   - Signal K server started
   - Node-RED started
   - Onboarding wizard launched

3. **User Interaction**:
   - Touchscreen displays onboarding welcome
   - User proceeds through configuration
   - System configures based on answers
   - CX5106 DIP switch diagram shown
   - Completion screen with QR code

4. **Post-Onboarding**:
   - Main menu displayed
   - All services running
   - Voice assistant enabled
   - System ready for use
```

---

## 3. ONBOARDING_FLOW.md - REQUIRED UPDATES

### ❌ CRITICAL MISSING CONTENT

#### 3.1 Add 13 Engine Questions (HIGH PRIORITY)
**Current**: Only shows 8 generic steps  
**Required**: Complete 13-question engine wizard

**Add New Step 3 (Engine Configuration)**:
```markdown
### Step 3: Engine Configuration (13 Questions)

#### Purpose
Collect complete engine metadata for CX5106 configuration, performance baselines, and health monitoring.

#### Questions

**ENGINE IDENTIFICATION**

**Q1: What is the engine manufacturer?**
- Dropdown with AI assist
- Options: Yanmar, Volvo Penta, Mercruiser, Cummins, Caterpillar, Custom
- AI fills if detectable from NMEA2000

**Q2: What is the engine model?**
- Text input with autocomplete
- AI suggests based on manufacturer
- Examples: "3YM30", "D4-260", "7.4L"

**Q3: What year is the engine?**
- Number input (1970-2026)
- Validation: Reasonable range
- AI suggests based on model

**ENGINE CONFIGURATION**

**Q4: How many cylinders?**
- Dropdown: 3, 4, 6, 8
- Maps to CX5106 SW5/SW6
- Critical for DIP switch calculation

**Q5: Engine displacement?**
- Number input with unit selection (Liters or CID)
- Auto-converts between units
- Used for performance calculations

**Q6: Compression ratio?**
- Number input (e.g., 9.5:1, 17:1)
- Optional but recommended
- Used for anomaly detection

**Q7: Stroke length?**
- Number input with unit (mm or inches)
- Optional
- Used for advanced calculations

**Q8: Induction type?**
- Radio buttons:
  - Naturally aspirated
  - Turbocharged
  - Supercharged
- Affects expected pressure ranges

**ENGINE PERFORMANCE**

**Q9: Rated horsepower?**
- Number input (HP or kW)
- Unit selection
- Auto-converts

**Q10: Idle RPM specification?**
- Number input (typical: 600-900)
- Used for anomaly detection
- Validates against manufacturer specs

**Q11: WOT RPM range?**
- Two inputs: Min and Max
- Example: 4200-4800 RPM
- Used for performance envelope

**ENGINE LIMITS**

**Q12: Maximum coolant temperature?**
- Number input with unit (°C or °F)
- Auto-converts
- Sets alarm threshold

**Q13: Minimum safe oil pressure?**
- Two inputs:
  - Idle pressure (PSI or kPa)
  - Cruise pressure (PSI or kPa)
- Sets alarm thresholds

#### AI Assistance

For each question:
- If user selects "I don't know", AI suggests based on:
  - Engine make/model/year
  - Manufacturer specifications
  - Similar vessel configurations
  - Industry standards

- Confidence levels:
  - High: Show suggestion, allow override
  - Medium: Show suggestion with warning
  - Low: Require user input

#### Validation

- Cross-check answers for consistency
- Example: 8-cylinder but displacement is 30L → Warning
- Example: Diesel but compression ratio is 9:1 → Warning
- Example: Turbocharged but boost limits not set → Prompt

#### Output

Generates:
- `config/boat-active.json` (engine section)
- CX5106 DIP switch positions
- Alarm thresholds
- Performance envelope
- Anomaly detection parameters
```

---

#### 3.2 Add Onboarding Reset Counter (HIGH PRIORITY)
**Current**: Not mentioned  
**Required**: Tier 0 limit of 10 resets

**Add New Section**:
```markdown
### Onboarding Reset System

#### Reset Counter
- Location: `state/onboarding-reset-count.json`
- Format:
```json
{
  "count": 3,
  "lastReset": "2026-02-04T14:30:00Z",
  "installationId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Reset Flow
1. User clicks "Reset Onboarding" button
2. System checks current count
3. If count < 10:
   - Increment counter
   - Delete `state/onboarding.json`
   - Delete `config/boat-active.json`
   - Restart onboarding wizard
   - Display: "Reset X of 10"
4. If count = 8 or 9:
   - Show warning: "You have X resets remaining"
   - Proceed with reset
5. If count = 10:
   - Show error: "Maximum resets reached"
   - Display: "Download new image from d3kos.github.io"
   - Do NOT reset
   - Provide download link

#### Tier 3+ Override
- Tier 3 and 4 licenses have unlimited resets
- Checked via license file
- Override display shows "Unlimited (Tier 3)"
```

---

#### 3.3 Add QR Code Generation Step (MEDIUM PRIORITY)
**Current**: Not mentioned  
**Required**: Mobile app pairing

**Add to Step 10 (Complete)**:
```markdown
### Step 10: Completion & QR Code

#### Completion Actions
- Save all configuration
- Mark onboarding complete
- Generate installation UUID
- Create QR code

#### QR Code Content
```json
{
  "installationId": "550e8400-e29b-41d4-a716-446655440000",
  "vessel": {
    "name": "Sea Breeze",
    "mmsi": "123456789"
  },
  "licenseTier": 0,
  "version": "1.0.0",
  "configuredDate": "2026-02-04T15:45:00Z"
}
```

#### Display
- Large QR code (center of screen)
- Instructions: "Scan with d3kOS mobile app"
- "Continue to Main Menu" button
- QR code also accessible from main menu
```

---

#### 3.4 Add Voice Guidance (MEDIUM PRIORITY)
**Current**: Not mentioned  
**Required**: Optional voice-guided onboarding

**Add Section**:
```markdown
### Voice-Guided Onboarding

#### Enable Voice Guidance
- Toggle switch on welcome screen
- "Would you like voice guidance?"
- Uses Piper TTS

#### Voice Prompts
Each step includes:
- Voice reads question aloud
- Voice reads options
- Voice confirms selection
- Voice provides help text

#### Voice Input
- Wake word "Helm" activates
- User can speak answers
- Voice-to-text fills forms
- Confirmation required

#### Example Flow
```
[Voice]: "Welcome to d3kOS. Let's configure your vessel."
[User]: "Helm, I'm ready"
[Voice]: "What is your operator name?"
[User]: "Captain Don"
[Voice]: "I heard Captain Don. Is that correct?"
[User]: "Yes"
[Voice]: "Great. What is your vessel name?"
```
```

---

#### 3.5 Update API Specification (MEDIUM PRIORITY)
**Current**: Basic endpoints listed  
**Required**: Complete API with request/response examples

**Expand API Section**:
```markdown
## Complete API Specification

### POST /onboarding/engine

**Request Body**:
```json
{
  "manufacturer": "Yanmar",
  "model": "3YM30",
  "year": 2015,
  "cylinders": 3,
  "displacement": 30,
  "displacementUnit": "liters",
  "compressionRatio": 17.5,
  "stroke": 95,
  "strokeUnit": "mm",
  "induction": "naturally_aspirated",
  "horsepower": 29,
  "horsepowerUnit": "hp",
  "idleRPM": 700,
  "wotRPMMin": 3000,
  "wotRPMMax": 3600,
  "maxCoolantTemp": 95,
  "coolantTempUnit": "celsius",
  "oilPressureIdleMin": 10,
  "oilPressureCruiseMin": 40,
  "pressureUnit": "psi"
}
```

**Response**:
```json
{
  "success": true,
  "nextStep": "chartplotter",
  "dipSwitches": {
    "sw1": "OFF",
    "sw2": "OFF",
    "sw3": "OFF",
    "sw4": "ON",
    "sw5": "ON",
    "sw6": "ON",
    "sw7": "OFF",
    "sw8": "ON"
  },
  "alarmThresholds": {
    "maxCoolantTemp": 95,
    "minOilPressureIdle": 10,
    "minOilPressureCruise": 40
  }
}
```
```

---

#### 3.6-3.10 Additional Updates (LOWER PRIORITY)
- Add error handling flows
- Add data persistence details
- Add rollback procedures
- Add multi-language support
- Add accessibility features

---

## 4. ARCHITECTURE.md - REQUIRED UPDATES

### Updates Needed:

#### 4.1 Add Voice Assistant Architecture (HIGH PRIORITY)
#### 4.2 Add Camera Integration Architecture (MEDIUM PRIORITY)
#### 4.3 Add Licensing System Architecture (MEDIUM PRIORITY)
#### 4.4 Add Boat Log System (MEDIUM PRIORITY)
#### 4.5 Update UI/UX Section with AODA Requirements (MEDIUM PRIORITY)
#### 4.6 Add Touchscreen Gesture System (LOW PRIORITY)
#### 4.7 Add Multi-Boot Support Architecture (LOW PRIORITY)

---

## 5. SCRIPTS_REFERENCE.md - REQUIRED UPDATES

### Updates Needed:

#### 5.1 Add Image Creation Script (HIGH PRIORITY)
#### 5.2 Add Voice Assistant Installation Script (MEDIUM PRIORITY)
#### 5.3 Add Camera Setup Script (LOW PRIORITY)

---

## PRIORITY ORDER FOR UPDATES

### Phase 1 - Immediate (This Week)
1. ✅ README.md - Pre-built image approach
2. ✅ README.md - Voice assistant section
3. ✅ README.md - Licensing tiers
4. ✅ INSTALLATION_GUIDE.md - Complete rewrite for image flashing
5. ✅ ONBOARDING_FLOW.md - Add 13 engine questions

### Phase 2 - Soon (Next Week)
6. ONBOARDING_FLOW.md - Add reset counter
7. ONBOARDING_FLOW.md - Add QR code generation
8. ARCHITECTURE.md - Add voice assistant architecture
9. README.md - Main menu features
10. README.md - UI/UX specifications

### Phase 3 - Later (Following Week)
11. ARCHITECTURE.md - Camera integration
12. ARCHITECTURE.md - Licensing system
13. ONBOARDING_FLOW.md - Voice guidance
14. ONBOARDING_FLOW.md - Complete API specs
15. SCRIPTS_REFERENCE.md - Image creation

---

## SUMMARY

**Total Updates Needed**: 35+
**Critical Updates**: 12
**High Priority**: 8
**Medium Priority**: 10
**Low Priority**: 5

**Recommendation**: Start with Phase 1 updates (README.md and INSTALLATION_GUIDE.md complete rewrites) before building new components.
