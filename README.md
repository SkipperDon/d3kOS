# d3kOS

**Marine Intelligence Platform - d3-k1 Hardware**

d3kOS is marine electronics software that runs on the d3-k1 hardware platform. The d3-k1 is a comprehensive marine electronics system that integrates NMEA2000 data, GPS/AIS information, camera surveillance, and AI-powered voice assistance into a unified, touchscreen-optimized interface for boat owners.

**Version**: 2.0
**Date**: February 6, 2026
**OS**: Raspberry Pi OS Bookworm (Debian 12, 64-bit)
**Status**: APPROVED - Production Ready

---

## Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Stack](#software-stack)
- [Quick Start](#quick-start)
- [Licensing & Tiers](#licensing--tiers)
- [Voice Assistant](#voice-assistant)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### Core Capabilities (All Tiers)

- **AI-Assisted Onboarding**: 13-question engine wizard with automatic CX5106 DIP switch configuration
- **NMEA2000 Integration**: Real-time engine and sensor data via PiCAN-M HAT
- **Engine Health Monitoring**: Baseline establishment, anomaly detection (>95% accuracy), trend analysis
- **Raspberry Pi Monitoring**: CPU, memory, storage, GPU, thermal monitoring with auto-protection
- **Dashboard**: Real-time gauges at 1Hz update rate with Node-RED Dashboard 2.0
- **OpenCPN Integration**: Auto-install chartplotter software for navigation
- **Boat Log**: Voice-to-text logging system
- **GPS/AIS Support**: Position tracking and vessel traffic awareness
- **Offline-First Design**: Full functionality without internet connectivity
- **AODA Compliant**: Accessibility-first UI for marine environments

### Premium Features (Tier 2+)

- **Offline Voice Assistant ("Helm")**: Wake word detection, STT, TTS, local LLM (Phi-2)
- **IP Camera Integration**: Live view, recording, intelligent storage management
- **Unlimited Onboarding Resets**: No limit on configuration changes
- **Extended Data Retention**: Unlimited boat log and historical data storage

### Advanced Features (Tier 3)

- **Cloud Sync**: Optional backup and remote access
- **Remote Monitoring**: Access dashboard from anywhere
- **Multi-Device Support**: Synchronized across devices
- **Priority Support**: Direct email support (24-hour response)

---

## Hardware Requirements

### Core Components (Required)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| **Raspberry Pi 4 Model B** | 4GB RAM minimum, 8GB recommended | $55-$75 |
| **PiCAN-M HAT** | NMEA2000 interface with micro-fit connector | $60 |
| **MicroSD Card** | 64GB minimum (Class 10 A2), 128GB recommended | $12-$20 |
| **Touchscreen** | 10.1" 1920×1200, 1000 nit, capacitive touch | $120 |
| **DC-DC Converter** | 12V→5V, 5A, galvanic isolation (Victron Orion-Tr) | $35 |
| **USB GPS Receiver** | VK-162 or equivalent | $15 |
| **USB AIS Receiver** | dAISy or equivalent | $80 |
| **Enclosure** | Aluminum or 3D-printed case | $20-$50 |

**Total Core System**: ~$470

### Optional Hardware (Tier 2+)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| **Anker PowerConf S330** | USB speakerphone for voice assistant | $130 |
| **Reolink RLC-810A** | 4K IP camera with night vision | $90 |
| **PoE Injector** | For IP camera power | $12 |

**Total with Voice + Camera**: ~$837

### Display Requirements

- **Resolution**: 1920×1200 (minimum for AODA compliance)
- **Brightness**: 1000 nit (sunlight readable, critical for marine use)
- **Touch**: Capacitive multi-touch, glove-operable
- **Connection**: HDMI + USB (for touch)

### Environmental Specifications

- **Operating Temperature**: 0°C to 50°C (32°F to 122°F)
- **Humidity**: 5% to 95% non-condensing
- **IP Rating**: IP20 (enclosure required for marine use)
- **Vibration**: Marine-grade mounting with strain relief required

**See**: [HARDWARE.md](doc/reference/HARDWARE.md) for complete specifications, assembly guide, and troubleshooting

---

## Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Raspberry Pi OS** | Bookworm (64-bit) | Base operating system (Debian 12) |
| **Signal K Server** | Latest | Marine data aggregation hub |
| **Node-RED** | 3.x | Data flow automation and dashboard |
| **Node-RED Dashboard** | 2.0 | Vue-based dashboard UI |
| **GPSd** | Latest | GPS data processing |
| **OpenCPN** | 5.8.x | Chart plotting (auto-installed) |
| **PocketSphinx** | Latest | Wake word detection ("Helm") - Tier 2+ |
| **Vosk** | 0.15 | Speech-to-text (offline) - Tier 2+ |
| **Piper** | Latest | Text-to-speech (offline) - Tier 2+ |
| **Phi-2** (llama.cpp) | 2.7B | Local AI reasoning - Tier 2+ |
| **VLC (libvlc)** | Latest | RTSP camera stream viewer - Tier 2+ |
| **Chromium** | Latest | Browser-based interface |

**All Processing Local** - No cloud dependencies for core functionality

---

## Quick Start

### 1. Download Pre-Built Image

```bash
# Download latest release from GitHub
wget https://github.com/SkipperDon/d3kOS/releases/latest/d3kos-v2.0.img.gz

# Download checksum
wget https://github.com/SkipperDon/d3kOS/releases/latest/d3kos-v2.0.img.gz.sha256

# Verify integrity
sha256sum -c d3kos-v2.0.img.gz.sha256
```

### 2. Flash to SD Card

#### Raspberry Pi Imager (Recommended)
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Launch Imager
3. **Choose OS** → **Use custom** → Select downloaded `.img.gz` file
4. **Choose Storage** → Select SD card (64GB minimum)
5. **Write** → Wait for completion (~10-15 minutes)

#### Command Line (Linux/Mac)
```bash
# Decompress
gunzip d3kos-v2.0.img.gz

# Flash (replace /dev/sdX with your SD card)
sudo dd if=d3kos-v2.0.img of=/dev/sdX bs=4M status=progress conv=fsync
```

### 3. Hardware Assembly

1. **Attach PiCAN-M HAT** to Raspberry Pi GPIO header
2. **Insert microSD card** into Raspberry Pi
3. **Connect touchscreen** (HDMI + USB)
4. **Connect peripherals** (GPS, AIS, speakerphone if Tier 2+)
5. **Connect NMEA2000** via micro-fit 4-pin connector:
   - Pin 1 (red): 12V+
   - Pin 2 (black): GND
   - Pin 3 (white): CAN-H
   - Pin 4 (blue): CAN-L
6. **Connect power** via DC-DC converter (12V boat power → 5V Pi)

**See**: [HARDWARE.md](doc/reference/HARDWARE.md) for detailed assembly instructions

### 4. First Boot

1. Power on (wait ~60 seconds for boot)
2. **Default credentials** (SSH/Desktop):
   - Username: `d3kos`
   - Password: `d3kos2026`
   - ⚠️ **Change password after first login**: `passwd`
3. Touchscreen shows Chromium with onboarding wizard
4. Connect to WiFi network: **"d3kOS"** (password: `d3kos-2026`)
5. From mobile device, navigate to: `http://d3kos.local` or `http://10.42.0.1`

### 5. Complete Onboarding Wizard

The 13-question wizard collects engine specifications:

1. Engine Manufacturer (autocomplete)
2. Engine Model
3. Engine Year (1950-2026)
4. Number of Cylinders (3, 4, 6, 8)
5. Engine Displacement (Liters or Cubic Inches)
6. Compression Ratio
7. Stroke Length (mm or inches)
8. Induction Type (NA, Turbo, Supercharged)
9. Rated Horsepower
10. Idle RPM Specification
11. WOT RPM Range
12. Maximum Coolant Temperature
13. Minimum Oil Pressure (Idle & Cruise)

**Output**:
- CX5106 DIP switch configuration diagram with explanations
- QR code for mobile app pairing
- Installation ID generation

**Time**: 10-20 minutes

---

## Licensing & Tiers

### Tier Structure

| Feature | Tier 0 (Free) | Tier 2 (App) | Tier 3 (Subscription) |
|---------|---------------|--------------|----------------------|
| Dashboard & Gauges | ✓ | ✓ | ✓ |
| Engine Health Monitoring | ✓ | ✓ | ✓ |
| Pi Health Monitoring | ✓ | ✓ | ✓ |
| OpenCPN Integration | ✓ | ✓ | ✓ |
| Boat Log (30 days) | ✓ | Unlimited | Unlimited |
| Onboarding Resets | 10 max | Unlimited | Unlimited |
| **Voice Assistant** | ✗ | ✓ | ✓ |
| **Camera Integration** | ✗ | ✓ | ✓ |
| Historical Graphs | 30 days | 90 days | 90 days |
| Cloud Sync | ✗ | ✗ | ✓ |
| Remote Access | ✗ | ✗ | ✓ |
| Priority Support | ✗ | ✗ | ✓ |

### Tier 0: Opensource (Default)

**Free and Open Source**

Includes all core functionality:
- NMEA2000 integration via Signal K
- Real-time dashboard at 1Hz
- Engine health monitoring with anomaly detection
- Raspberry Pi health monitoring
- GPS/AIS integration
- OpenCPN auto-installation
- Boat log (30-day retention)
- Manual onboarding (10 resets maximum)

**Limitation**: Maximum 10 onboarding resets. After 10th reset, must download fresh image or upgrade to Tier 2+.

### Tier 2: App-Based Upgrade

**Free upgrade by installing paid app (OpenCPN or other)**

**How to Upgrade**:
- Install OpenCPN (included, free to enable)
- Or install other paid marine apps
- System automatically detects and upgrades to Tier 2

**Additional Features**:
- ✓ Offline voice assistant ("Helm")
- ✓ IP camera integration
- ✓ Unlimited onboarding resets
- ✓ Unlimited boat log retention
- ✓ Extended historical data (90 days)

**Cost**: Free (OpenCPN included, just enable it)

### Tier 3: Cloud Subscription (Future)

**Planned Features**:
- Cloud backup and sync
- Remote monitoring from anywhere
- Multi-device access
- Advanced analytics
- Priority email support (24-hour response)

**Cost**: TBD (subscription model)

### Reset Counter

Located in footer of onboarding wizard:
- **Displays**: "Resets used: 7/10 (Tier 0)"
- **Warning at 8**: "Only 2 resets remaining. Consider upgrading to Tier 2."
- **Warning at 9**: "This is your last reset."
- **At 10**: "Maximum resets reached. Download fresh image or upgrade to Tier 2."

**Tier 2+ Bypass**: Unlimited resets (counter doesn't increment)

---

## Voice Assistant

### "Helm" - Offline AI Assistant (Tier 2+ Only)

Fully offline voice assistant with wake word detection, speech recognition, and local AI reasoning.

### Voice Pipeline

```
Microphone (16kHz)
      ↓
PocketSphinx (Wake Word Detection)
      ↓ "Helm" detected (<500ms)
Vosk (Speech-to-Text)
      ↓ Transcription (<1s)
Phi-2 via llama.cpp (AI Reasoning)
      ↓ Response generation (<1s)
Piper (Text-to-Speech)
      ↓ Audio output (<500ms)
Speaker
```

**Total Response Time**: < 2 seconds from wake word to response

### Supported Commands

**Engine & Health**:
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, show benchmark report"
- "Helm, start benchmarking"

**Navigation**:
- "Helm, open OpenCPN"
- "Helm, GPS status"
- "Helm, AIS status"

**Boat Log**:
- "Helm, record boat log" (starts recording)
- "Helm, post to boat log" (saves entry)
- "Helm end" (stops listening)

**System**:
- "Helm, query system status"
- "Helm, restart services"

### Technology Stack

| Component | Technology | Size | Purpose |
|-----------|-----------|------|---------|
| Wake Word | PocketSphinx | ~10MB | Detect "Helm" |
| STT | Vosk (small-en-us) | 50MB | Speech to text |
| LLM | Phi-2 (Q4_K_M) | 5GB | AI reasoning |
| TTS | Piper (en_US-amy) | ~20MB | Text to speech |

**100% Offline** - All processing on Raspberry Pi, no cloud required

**RAM Requirement**: 8GB Pi recommended for voice features (3GB RAM for Phi-2 model)

---

## Documentation

### Core Documentation

- **[MASTER_SYSTEM_SPEC.md](MASTER_SYSTEM_SPEC.md)** - Complete system specification (2,040 lines)
- **[architecture.md](architecture.md)** - System architecture, data flow, component diagrams
- **[HARDWARE.md](doc/reference/HARDWARE.md)** - Hardware specs, assembly guide, troubleshooting
- **[CLAUDE.md](CLAUDE.md)** - AI assistant development guidelines

### CX5106 Documentation

- **[CX5106_USER_MANUAL.md](doc/CX5106_USER_MANUAL.md)** - Complete manual for CX5106 engine gateway
- **[CX5106_CONFIGURATION_GUIDE.md](doc/CX5106_CONFIGURATION_GUIDE.md)** - DIP switch configuration logic
- **[CX5106_DIP_SWITCH.md](reference/CX5106_DIP_SWITCH.md)** - Quick reference

---

## Main Features

### Dashboard Gauges (Node-RED Dashboard 2.0)

**Page 1: Engine & System**
- **Row 1**: Engine gauges
  - Tachometer (circular, 270° arc)
  - Tilt/Trim
  - Engine Temperature (with thresholds)
  - Battery Voltage
  - Oil Pressure
- **Row 2**: Tank levels (horizontal bars with gradients)
  - Fresh Water (%)
  - Black Water (%)
  - Fuel Level (%, gallons/liters)
  - House Battery (%)
- **Row 3**: System status
  - CPU Usage (with temp monitoring)
  - Memory Usage
  - Storage Remaining
  - GPU Temperature
- **Row 4**: Network status (color-coded indicators)
  - WiFi (SSID, signal strength)
  - Ethernet (IP address)
  - NMEA2000 (device count)
  - Internet (connected/disconnected)

**Page 2: Boat Log**
- Voice recording interface
- Log entry list (last 30 days for Tier 0, unlimited for Tier 2+)
- Export options (CSV/JSON)

**Page 3: Health Reports**
- Engine health summary
- Anomaly history timeline
- Trend graphs (CPU, memory, engine metrics)
- Maintenance recommendations

### Engine Health Monitoring

**Baseline Establishment**:
- 30-minute benchmark run
- Captures: RPM (idle/cruise), temperature warmup curve, oil pressure, fuel rate
- Statistical analysis: mean, stddev, min/max for each metric
- Stored in: `/opt/d3kos/config/benchmark-results.json`

**Anomaly Detection**:
- Statistical Process Control (SPC) method
- Alerts:
  - **INFO**: 1σ deviation (log only)
  - **WARNING**: 2σ deviation (visual alert)
  - **CRITICAL**: 3σ deviation (visual + voice alert)
- False positive rate: < 5%
- Accuracy: > 95%

**Example Alerts**:
- "Engine temperature is 210°F, 30 degrees above normal. Please check coolant system."
- "Oil pressure declining 2 PSI/week over last 2 weeks. Consider oil change within 10 engine hours."

### Camera Integration (Tier 2+ Only)

**Supported Camera**: Reolink RLC-810A (4K, night vision, IP66)

**Features**:
- Live RTSP stream view (< 500ms latency)
- Hardware-accelerated H.264 decode (GPU)
- Manual recording with 10-minute segments
- Intelligent storage management:
  - Warning at 20% free space
  - Auto-stop recording at 18% free space
  - FIFO deletion of oldest recordings
- Playback interface with timeline scrubber
- Night vision auto-switching

**Storage Path**: `/opt/d3kos/data/camera/`
**Format**: MP4 (H.264), 1080p @ 30fps

### Network Configuration

**WiFi Access Point**:
- **SSID**: d3kOS
- **Password**: d3kos-2026 (default)
- **IP Address**: 10.42.0.1/24
- **DHCP Range**: 10.42.0.2 - 10.42.0.254
- **Security**: WPA2-PSK

**Services**:
- Main Menu: `http://d3kos.local` or `http://10.42.0.1`
- Dashboard: `http://d3kos.local:1880/dashboard`
- Signal K: `http://d3kos.local:3000`
- Camera: `rtsp://d3kos.local:554/camera` (Tier 2+)

**Ethernet Sharing**: Internet sharing enabled if ethernet connected

---

## UI/UX Design

### AODA/WCAG 2.1 AA Compliant

**Color Scheme**:
- Background: Pure black (#000000)
- Primary text: White (#FFFFFF)
- Accent: Green (#00CC00)
- Warning: Amber (#FFA500)
- Critical: Red (#FF0000)

**Typography**:
- Font: Roboto, Arial, sans-serif
- Minimum size: 22px
- Button text: 24px bold
- Headings: 32px bold
- Line height: 1.5

**Touch Targets**:
- Minimum: 120×80px
- Padding: 16px
- Gap: 20px horizontal, 16px vertical

**Accessibility Features**:
- Keyboard navigation (Tab, Enter, Escape, Arrows)
- Screen reader support (aria-labels)
- High contrast (21:1 white on black)
- Focus indicators (3px solid green)
- Text alternatives for all icons

**Marine Optimization**:
- 1000 nit display (sunlight readable)
- Large touch targets (glove-operable)
- Bottom 1/3 reserved for on-screen keyboard
- Minimal scrolling (critical info always visible)

---

## Performance Specifications

### Boot Time
- **Target**: < 60 seconds from power-on to operational
- **Actual**: ~45-60 seconds on Pi 4 with Class 10 A2 SD card

### Response Times
- **Dashboard update**: 1 Hz (1000ms intervals)
- **Voice response**: < 2 seconds (wake word to audio output)
- **Anomaly detection**: Real-time (< 100ms)
- **Camera latency**: < 500ms (RTSP stream)

### Resource Usage
- **CPU**: < 70% sustained (dashboard + voice + camera)
- **Memory**: < 4GB (fits in 4GB Pi), 8GB recommended for voice
- **Storage writes**: < 100 MB/hour
- **Network**: < 10 KB/sec (Signal K updates)

### Thermal Management
- **Normal**: < 60°C CPU temperature
- **Warning**: 70°C (visual alert)
- **Critical**: 80°C (voice alert, reduce services)
- **Throttle**: 82°C (hardware thermal throttling)

---

## CX5106 Engine Gateway

### Automatic DIP Switch Configuration

d3kOS calculates correct CX5106 settings from onboarding answers.

**8 DIP Switches**:
- **SW 1-2**: Engine instance (0-3)
- **SW 3-4**: RPM source (alternator, ignition, magnetic, ECU)
- **SW 5-6**: Cylinders (3, 4, 6, 8)
- **SW 7**: Stroke (2-stroke, 4-stroke)
- **SW 8**: Gear ratio (1:1, 2:1, or custom)

**Output Includes**:
- Visual DIP switch diagram (which switches ON/OFF)
- Explanation for each setting
- Special handling for non-standard ratios (e.g., Bravo II 1.5:1)

**See**: [CX5106_USER_MANUAL.md](doc/CX5106_USER_MANUAL.md) for manual configuration

---

## Troubleshooting

### Power Issues

**Pi won't power on (no LED)**:
1. Check voltage at USB-C: must be 5.0V ±0.25V
2. Verify USB-C cable quality (use official Pi cable)
3. Check 12V input polarity (red=+, black=-)
4. Test with known-good 5V 3A power supply

**Random reboots**:
1. Check for undervoltage: `vcgencmd get_throttled`
2. Monitor CPU temp: `vcgencmd measure_temp` (should be < 80°C)
3. Test SD card: `sudo fsck /dev/mmcblk0p2`

### NMEA2000 Issues

**No CAN0 data**:
```bash
# Check CAN interface
ifconfig can0

# Monitor bus traffic
candump can0

# Check for devices
dmesg | grep mcp251x
```

**Solutions**:
- Verify 12V present on NMEA2000 bus
- Check termination: 60Ω between CAN-H and CAN-L
- Swap CAN-H/CAN-L if wired backwards
- Reseat PiCAN-M HAT on GPIO header

### Display Issues

**No display output**:
1. Reseat HDMI cable (both ends)
2. Try different HDMI cable
3. Verify touchscreen power LED is on
4. Check Pi green LED flashing (SD card activity)

**Touchscreen not responding**:
1. Check USB touch cable connected
2. Verify device detected: `lsusb | grep -i touch`
3. Test with USB mouse to verify OS running
4. Recalibrate: `xinput-calibrator`

### GPS/AIS Issues

**No GPS fix**:
1. Check GPS LED blinking (satellite acquisition)
2. Verify USB connection: `lsusb | grep -i prolific`
3. Check gpsd: `systemctl status gpsd`
4. View GPS data: `cgps -s`
5. Ensure clear view of sky (not inside metal cabin)
6. Wait 5 minutes for cold start

**No AIS data**:
1. Check AIS LED flashing (messages received)
2. Verify USB: `lsusb | grep -i ftdi`
3. Monitor serial: `cat /dev/ttyUSB1`
4. Check antenna connected (SMA connector)
5. Verify antenna location (high = better range)

### Voice Assistant Issues (Tier 2+ Only)

**Wake word not detected**:
1. Check service: `systemctl status d3kos-voice`
2. Verify microphone: `arecord -l`
3. Test audio levels: `arecord -d 5 test.wav && aplay test.wav`
4. Check logs: `/var/log/d3kos-voice.log`

**Slow or no response**:
1. Check CPU temp (thermal throttling slows inference)
2. Verify Phi-2 model loaded: `ps aux | grep llama`
3. Check RAM usage: `free -h` (need ~3GB free for LLM)
4. Verify 8GB Pi for best performance

**See**: [HARDWARE.md](doc/reference/HARDWARE.md) for comprehensive troubleshooting

---

## Project Structure

```
d3kOS/
├── MASTER_SYSTEM_SPEC.md           # Complete system specification (v2.0)
├── architecture.md                  # System architecture documentation
├── README.md                        # This file
├── LICENSE                          # License file
├── CLAUDE.md                        # AI development guidelines
│
├── doc/                             # Documentation
│   ├── CX5106_USER_MANUAL.md       # CX5106 complete manual
│   ├── CX5106_CONFIGURATION_GUIDE.md # DIP switch logic
│   └── reference/                   # Reference documentation
│       └── HARDWARE.md              # Hardware specs & assembly
│
├── reference/                       # Quick references
│   └── CX5106_DIP_SWITCH.md        # Quick DIP switch guide
│
├── services/                        # System services (on image)
│   ├── onboarding/                 # Configuration wizard
│   ├── voice/                      # Voice assistant (Tier 2+)
│   ├── camera/                     # Camera management (Tier 2+)
│   ├── health/                     # Health monitoring
│   └── boatlog/                    # Boat log system
│
├── config/                          # Configuration files (on image)
│   ├── onboarding.json             # User responses
│   ├── benchmark-results.json      # Engine baseline
│   ├── license.json                # Tier & features
│   └── engine-manufacturers.json   # Manufacturer database
│
├── state/                           # Runtime state (on image)
│   ├── onboarding-reset-count.json # Reset tracking
│   └── pi-health-status.json       # System metrics
│
└── scripts/                         # Utility scripts (on image)
    ├── install-*.sh                # Component installers
    ├── configure-*.sh              # Configuration scripts
    ├── backup.sh                   # Backup automation
    └── restore.sh                  # Restore from backup
```

---

## Development

### Prerequisites

```bash
# For Node.js development
npm install

# For Python development
pip3 install -r requirements.txt

# For voice assistant (Tier 2+)
# Install Vosk, Piper, llama.cpp, Phi-2 model
```

### Running Services Locally

```bash
# Signal K Server
signalk-server

# Node-RED
node-red

# Voice Assistant (Tier 2+)
cd services/voice
python3 assistant.py
```

### Testing

```bash
# Test CAN interface
candump can0

# Test Signal K API
curl http://localhost:3000/signalk/v1/api/

# Test GPS
cgps -s

# Test voice (Tier 2+)
echo "Helm, test" | python3 services/voice/test_stt.py
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Read `CLAUDE.md` for development guidelines
4. Follow existing code style
5. Add tests for new features
6. Update documentation
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

---

## Roadmap

### Version 2.0 (Current - Feb 2026) ✅
- [x] NMEA2000 integration via Signal K
- [x] AI-assisted onboarding (13 questions)
- [x] CX5106 DIP switch auto-configuration
- [x] Engine health monitoring with anomaly detection
- [x] Raspberry Pi health monitoring
- [x] Offline voice assistant (Tier 2+)
- [x] IP camera integration (Tier 2+)
- [x] OpenCPN auto-install
- [x] AODA-compliant UI
- [x] Tiered licensing system

### Version 2.1 (Q2 2026) - Planned
- [ ] Mobile app (iOS/Android)
- [ ] QR code pairing functional
- [ ] Cloud sync for Tier 3
- [ ] Remote monitoring dashboard
- [ ] Push notifications

### Version 2.2 (Q3 2026) - Future
- [ ] Multi-boat support (Tier 3)
- [ ] Fleet management dashboard
- [ ] Advanced AI recommendations
- [ ] PDF report generation
- [ ] Integration with more engine gateways

---

## Support

- **Issues**: [GitHub Issues](https://github.com/SkipperDon/d3kOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SkipperDon/d3kOS/discussions)
- **Documentation**: [Master Spec](MASTER_SYSTEM_SPEC.md) | [Architecture](architecture.md) | [Hardware](doc/reference/HARDWARE.md)

---

## Acknowledgments

Built with exceptional open-source projects:

- **[Signal K](https://signalk.org/)** - Universal marine data standard
- **[Node-RED](https://nodered.org/)** - Flow-based automation platform
- **[OpenCPN](https://opencpn.org/)** - Open-source chartplotter
- **[Vosk](https://alphacephei.com/vosk/)** - Offline speech recognition
- **[Piper](https://github.com/rhasspy/piper)** - Fast neural text-to-speech
- **[PocketSphinx](https://github.com/cmusphinx/pocketsphinx)** - Wake word detection
- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** - Efficient LLM inference
- **[Phi-2](https://huggingface.co/microsoft/phi-2)** - Microsoft's small language model

Special thanks to the marine open-source community and all contributors.

---

## License

**Tiered Open-Source Model**:
- **Tier 0**: GNU General Public License v3.0 (GPL-3.0)
- **Tier 2+**: Commercial features with open-source core

Core system remains fully open-source. Premium features (voice, camera) are enablements, not restrictions.

See [LICENSE](LICENSE) for details.

---

## Version History

| Version | Date | Status | Key Changes |
|---------|------|--------|-------------|
| 2.0 | Feb 6, 2026 | **Current** | Integrated gap analysis, added voice/camera, comprehensive docs |
| 1.0 | Feb 4, 2026 | Legacy | Initial release, core features only |

---

## Quick Links

- 📥 [Download Latest Release](https://github.com/SkipperDon/d3kOS/releases/latest)
- 📖 [Master System Spec](MASTER_SYSTEM_SPEC.md)
- 🏗️ [System Architecture](architecture.md)
- 🔧 [Hardware Guide](doc/reference/HARDWARE.md)
- 🎛️ [CX5106 Manual](doc/CX5106_USER_MANUAL.md)
- 💬 [GitHub Discussions](https://github.com/SkipperDon/d3kOS/discussions)

---

**d3kOS v2.0 - Software for the d3-k1 Marine Platform** - *Marine Intelligence, Simplified.*

*Built by boaters, for boaters. Powered by open source.*
