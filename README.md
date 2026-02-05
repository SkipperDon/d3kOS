# helm-OS

**Marine Intelligence Platform for Raspberry Pi 4B**

Helm-OS is a pre-built vessel monitoring and navigation system that integrates NMEA2000 marine electronics with AI-assisted configuration, real-time diagnostics, offline voice assistant, and intelligent health monitoring.

**Version**: 1.0.0  
**OS**: Raspberry Pi OS Trixie (Debian 13)  
**License**: Tiered (0-3)

---

## Features

### Core Capabilities
- **AI-Assisted Onboarding**: 13-question engine wizard with intelligent configuration
- **Offline Voice Assistant ("Helm")**: Wake word detection, STT, TTS, local LLM
- **NMEA2000 Integration**: Real-time engine and sensor data via CAN bus
- **Health Monitoring**: Continuous anomaly detection and performance tracking
- **Chartplotter Support**: Works with existing chartplotters or includes OpenCPN
- **Engine Benchmarking**: Baseline performance analysis and trend tracking
- **Mobile App Integration**: QR code pairing, notifications, cloud sync (Tier 1+)
- **Complete Offline Operation**: No internet required for core functionality

### Supported Equipment
- **Engine Gateways**: CX5106 with automatic DIP switch calculation
- **Chartplotters**: Garmin, Raymarine, Simrad, Furuno (auto-detected)
- **Navigation**: GPS, AIS receivers
- **Cameras**: IP67 marine cameras via PoE
- **Sensors**: Fuel, fresh water, black water tanks via NMEA2000

---

## Hardware Requirements

### Verified Configuration
- **Raspberry Pi 4B** - **8GB RAM** (required for voice assistant + LLM)
- **PiCAN-M HAT** with SMPS (NMEA2000 interface)
- **MicroSD Card** - 32GB minimum, 128GB recommended
- **10.1" Touchscreen** - 1920×1200, 1000 nit, capacitive touch
- **CX5106 Engine Gateway** - Analog-to-NMEA2000 conversion
- **USB GPS Receiver** - Position, speed, course
- **USB AIS Receiver** - Traffic awareness
- **Anker PowerConf S330** - Microphone + speaker for voice assistant
- **Reolink RLC-810A Camera** - IP67, night vision, bow-mounted
- **PoE Switch** - For IP camera power/data
- **NMEA2000 Backbone** - Connection to vessel network

### Display Requirements
- **Resolution**: 1920×1200 minimum
- **Brightness**: 1000 nit (sunlight readable)
- **Touch**: Capacitive, glove-operable
- **Connection**: USB or Mini-HDMI

---

## Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Raspberry Pi OS** | **Trixie (Debian 13)** | Base operating system (64-bit ARM) |
| **Node.js** | v18 or v20 LTS | Runtime environment (NOT v22) |
| **Signal K Server** | 2.x (latest) | Marine data hub |
| **Node-RED** | 3.x | UI and automation |
| **Node-RED Dashboard** | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue-based) |
| **OpenCPN** | 5.8.x | Navigation (auto-installed if needed) |
| **PocketSphinx** | Latest | Wake word detection ("Helm") |
| **Vosk** | Latest | Speech-to-text (offline) |
| **Piper** | Latest | Text-to-speech (offline) |
| **llama.cpp** | Latest | LLM runtime |
| **Phi-2** | 2.7B parameters | Local AI "brain" |

---

## Quick Start (5 Minutes)

### 1. Download Pre-Built Image

```bash
# Download latest release from GitHub
wget https://github.com/YOUR_USERNAME/helm-os/releases/latest/helm-os-v1.0.0-pi4b.img.gz

# Download checksum
wget https://github.com/YOUR_USERNAME/helm-os/releases/latest/helm-os-v1.0.0-pi4b.img.gz.sha256

# Verify integrity
sha256sum -c helm-os-v1.0.0-pi4b.img.gz.sha256
# Expected: helm-os-v1.0.0-pi4b.img.gz: OK
```

### 2. Flash to SD Card

#### Option A: Raspberry Pi Imager (Recommended)
1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Launch Imager
3. Click "Choose OS" → "Use custom"
4. Select downloaded `.img.gz` file
5. Click "Choose Storage" → Select your SD card (32GB minimum)
6. Click "Write" → Wait for completion (~15 minutes)

#### Option B: Command Line (Linux/Mac)
```bash
# Decompress (if needed)
gunzip helm-os-v1.0.0-pi4b.img.gz

# Flash to SD card (replace /dev/sdX with your card)
sudo dd if=helm-os-v1.0.0-pi4b.img of=/dev/sdX bs=4M status=progress
sync
```

#### Option C: Etcher (Windows)
1. Download and install [Etcher](https://www.balena.io/etcher/)
2. Select Helm-OS `.img.gz` file
3. Select SD card drive
4. Click "Flash"

### 3. First Boot
1. Insert SD card into Raspberry Pi 4B
2. Connect all hardware (touchscreen, GPS, AIS, microphone, camera)
3. Power on
4. Wait for boot (~60 seconds)
5. **Onboarding wizard launches automatically**

### 4. Complete Onboarding
Follow the on-screen wizard (10-20 minutes):
- Enter operator name
- Configure vessel information
- Answer 13 engine questions
- Receive CX5106 DIP switch diagram
- Scan QR code for mobile app pairing (optional)
- Complete baseline benchmark (optional but recommended)

---

## Voice Assistant - "Helm"

Helm-OS includes a fully offline voice assistant powered by local AI.

### Wake Word
Say **"Helm"** to activate listening mode

### Voice Pipeline
```
PocketSphinx → detects "Helm"
      ↓
Vosk → converts speech to text
      ↓
Phi-2 (llama.cpp) → interprets command
      ↓
Piper → speaks response
```

### Supported Commands

**System Control**:
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, query system status"
- "Helm, restart services"

**Navigation**:
- "Helm, open OpenCPN"
- "Helm, AIS status"
- "Helm, GPS status"

**Boat Log**:
- "Helm, record boat log"
- "Helm, post to boat log" (saves entry)
- "Helm end" (stops listening)

**Benchmarking**:
- "Helm, start benchmarking"
- "Helm, show benchmark report"

### Technology Stack
- **Wake Word**: PocketSphinx (offline)
- **STT**: Vosk with vosk-model-small-en-us-0.15 (offline)
- **TTS**: Piper with en_US-amy-medium voice (offline)
- **AI Brain**: Phi-2 (2.7B) via llama.cpp (offline)

**100% Offline** - No internet required, all processing on Raspberry Pi

---

## Licensing & Tiers

### Tier Structure

| Tier | Name | Features | Cost | Reset Limit |
|------|------|----------|------|-------------|
| **Tier 0** | Base Opensource | All core features, offline-only | **Free** | 10 resets |
| **Tier 1** | Mobile App Integration | Tier 0 + mobile app + cloud sync + notifications | **Free** | 10 resets |
| **Tier 2** | Premium Subscription | Tier 1 + AI analysis + recommendations | **Paid** | 10 resets |
| **Tier 3** | Enterprise/Fleet | Tier 2 + unlimited resets + multi-boat | **Paid** | Unlimited |

### Tier 0: Base Opensource (Default)
**Included**:
- All Helm-OS core functionality
- Offline voice assistant
- NMEA2000 integration
- OpenCPN auto-install
- Engine benchmarking
- Health monitoring
- Dashboard gauges
- Boat log (local storage)

**Limitations**:
- Maximum 10 onboarding resets
- No mobile app
- No cloud synchronization
- Local storage only

### Tier 1: Mobile App Integration (Free Upgrade)
**How to Upgrade**:
1. Complete onboarding wizard
2. Scan QR code with Helm-OS mobile app (iOS/Android)
3. Automatic upgrade to Tier 1

**Additional Features**:
- Mobile app for iOS/Android
- Cloud database synchronization
- Push notifications (health alerts, anomalies)
- Boat performance summaries in app
- Remote monitoring (when connected)

**Cost**: **Free** (just install mobile app)

### Tier 2: Premium Subscription
**Additional Features**:
- AI-powered performance analysis
- Predictive maintenance recommendations
- Trend analysis over time
- Performance optimization suggestions
- Detailed reports in mobile app
- Cloud backup of configurations

**Cost**: **$4.99/month** (example pricing)

### Tier 3: Enterprise/Fleet Management
**Additional Features**:
- **Unlimited onboarding resets**
- Multi-boat support (track entire fleet)
- Fleet-wide analytics
- PDF reports (individual boats + fleet summary)
- Advanced AI recommendations
- Priority support

**Use Case**: Charter companies, yacht management firms, multi-vessel owners

**Cost**: **$99/year for 5 boats** (example pricing)

---

## Main Menu Features

### System & Platform
- **Onboarding Wizard**
  - Operator setup
  - Vessel information
  - 13-question engine configuration
  - CX5106 DIP switch calculation
  - Chartplotter detection
  - QR code generation
  
- **System Health**
  - Raspberry Pi status (CPU, memory, storage, GPU)
  - Network status (WiFi, Ethernet, NMEA2000, Internet)
  - Service status

- **Benchmarking**
  - 30-minute engine baseline capture
  - Performance envelope calculation
  - Trend analysis

- **License Info**
  - Current tier display
  - Version number
  - Reset counter
  - Upgrade options

### Marine Data & Navigation
- **Signal K Server**
  - NMEA2000 integration
  - PGN detection
  - Real-time vessel monitoring

- **GPS & AIS**
  - Position, speed, course
  - Traffic awareness

- **Engine Health**
  - Real-time gauges
  - Anomaly detection
  - Historical trends

- **OpenCPN**
  - Auto-installed if no chartplotter
  - GPS/AIS integration
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
- Fuel Level (% full, gallons/liters)
- House Battery (%)

**Line 3 - System**:
- CPU Usage
- Memory Usage
- Storage Remaining
- GPU Usage

**Line 4 - Network**:
- WiFi (on/off, signal)
- Ethernet (on/off, IP)
- NMEA2000 (on/off, device count)
- Internet (on/off)

### Camera
- Full-screen view (Reolink RLC-810A)
- Night vision auto-switching
- Recording with storage management
- Stops recording at 18% disk remaining

### Boat Log
- Voice-to-text recording
- "Helm, record boat log"
- "Helm, post to boat log" (saves)
- Timestamp each entry
- Storage management (caps at 10% disk remaining)

---

## UI/UX Design

### AODA/WCAG 2.1 AA Compliant
- **Color Scheme**: Black background, white/green text
- **Font Size**: 22px minimum
- **Touch Targets**: 80×60px minimum (120×80px recommended)
- **On-Screen Keyboard**: Bottom 1/3 reserved
- **Navigation**: Back (left) and Main Menu (right) always visible

### Optimized for Marine Environment
- Readable in bright sunlight (1000 nit display)
- Large touch-friendly buttons
- Glove-operable interface
- Readable at distance (helm position)

---

## Documentation

- **[Installation Guide](docs/INSTALLATION_GUIDE.md)**: Image flashing and first boot
- **[Architecture](docs/ARCHITECTURE.md)**: System design and data flow
- **[Onboarding Flow](docs/ONBOARDING_FLOW.md)**: 13-question wizard details
- **[CX5106 Configuration](docs/CX5106_CONFIGURATION_GUIDE.md)**: DIP switch logic
- **[CX5106 User Manual](docs/CX5106_USER_MANUAL.md)**: Standalone setup guide
- **[CLAUDE.md](docs/CLAUDE.md)**: AI assistant development guidelines
- **[API Reference](docs/API_REFERENCE.md)**: Cloud API endpoints (Tier 1+)

---

## Network Configuration

### Wi-Fi Access Point
- **SSID**: "Helm-OS"
- **IP Range**: 10.42.0.1/24
- **DHCP**: Enabled
- **Password**: Configurable during onboarding

### Ethernet Sharing
- **Mode**: Shared (10.42.0.1/24)
- **DHCP**: Enabled for camera and other devices

### Offline-First Design
- All core features work without internet
- Optional cloud sync (Tier 1+)
- Updates via new image download only

---

## Project Structure

```
helm-os/
├── docs/                    # Documentation
├── services/                # Core services
│   ├── onboarding/         # Configuration wizard
│   ├── voice/              # Voice assistant ("Helm")
│   ├── .node-red/          # Node-RED flows
│   ├── signalk/            # Signal K configuration
│   └── opencpn/            # OpenCPN integration
├── config/                  # User configuration
│   ├── operator.json
│   ├── boat-identity.json
│   ├── boat-active.json
│   └── license.json        # Tier & entitlements
├── state/                   # Runtime state
│   ├── onboarding.json
│   ├── onboarding-reset-count.json
│   ├── baseline.json
│   └── health-status.json
├── system/                  # Systemd services
│   ├── helm-onboarding.service
│   ├── helm-voice.service
│   ├── helm-health.service
│   └── helm-benchmark.service
└── scripts/                 # Utility scripts
```

---

## CX5106 Engine Gateway

### Automatic Configuration
Helm-OS automatically calculates the correct CX5106 DIP switch settings based on your answers to the 13-question engine wizard.

### 8 DIP Switches Control:
- **SW 1-2**: Engine instance (0-3)
- **SW 3-4**: RPM signal source (alternator, ignition, magnetic, ECU)
- **SW 5-6**: Number of cylinders (3, 4, 6, 8)
- **SW 7**: Engine stroke (2-stroke or 4-stroke)
- **SW 8**: Gear ratio (1:1 or 2:1)

### Wizard Output:
- Visual DIP switch diagram
- Switch-by-switch instructions
- Explanation for each setting
- Non-standard ratio corrections (e.g., 1.5:1 Bravo II)

**See**: `CX5106_USER_MANUAL.md` for manual configuration without wizard

---

## Troubleshooting

### Image Won't Flash
- Verify SD card is at least 32GB (128GB recommended)
- Try different SD card (Class 10 or better)
- Verify image SHA256 checksum

### Won't Boot
- Check power supply (5V 3A minimum)
- Verify SD card is fully inserted
- Wait full 60 seconds for first boot
- Try re-flashing image

### Onboarding Doesn't Start
- Wait full 60 seconds after boot
- Check touchscreen connection
- Reboot and try again

### Voice Assistant Not Responding
- Check Anker PowerConf S330 connected via USB
- Test microphone: `arecord -l`
- Test speaker: `aplay -l`
- Check service: `systemctl status helm-voice`

### CAN0 Not Found
```bash
# Check CAN interface status
ip -details link show can0

# Expected: can state UP, bitrate 250000

# If not found, check hardware
dmesg | grep mcp251x
```

### Tier Not Upgrading
- Verify internet connection (for cloud sync)
- Check: `cat /opt/helm-os/config/license.json`
- Wait 24 hours for automatic poll
- Force update: Restart onboarding service

---

## Development

### Prerequisites
```bash
# Node.js development
npm install

# Python development
pip install -r requirements.txt --break-system-packages
```

### Running Services Locally
```bash
# Onboarding service
cd services/onboarding
npm install
npm start

# Voice assistant
cd services/voice
python3 assistant.py

# Node-RED (already runs as system service)
node-red

# Signal K (already runs as system service)
signalk-server
```

### Testing
```bash
# Run unit tests
npm test

# Test CAN interface
candump can0

# Test Signal K connection
curl http://localhost:3000/signalk/v1/api/

# Test voice assistant
echo "Helm, test" | python3 services/voice/test_stt.py
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Read `CLAUDE.md` for development guidelines
5. Add tests for new features
6. Update documentation
7. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Roadmap

### Tier 0 (Current - v1.0)
- [x] NMEA2000 integration
- [x] AI-assisted onboarding (13 questions)
- [x] Health monitoring
- [x] OpenCPN integration
- [x] Offline voice assistant
- [x] Engine benchmarking

### Tier 1 (v1.1 - In Progress)
- [ ] Mobile app (iOS/Android)
- [ ] QR code pairing
- [ ] Cloud database sync
- [ ] Push notifications

### Tier 2 (v1.2 - Planned)
- [ ] AI performance analysis
- [ ] Predictive maintenance
- [ ] Cloud backup
- [ ] Advanced reporting

### Tier 3 (v1.3 - Future)
- [ ] Multi-boat support
- [ ] Fleet management
- [ ] PDF report generation
- [ ] Priority support

---

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/helm-os/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/helm-os/discussions)
- **Documentation**: [Wiki](https://github.com/YOUR_USERNAME/helm-os/wiki)
- **Email**: support@helm-os.com

---

## Acknowledgments

Built with:
- [Signal K](https://signalk.org/) - Marine data standard
- [Node-RED](https://nodered.org/) - Flow-based programming
- [OpenCPN](https://opencpn.org/) - Navigation software
- [Vosk](https://alphacephei.com/vosk/) - Speech recognition
- [Piper](https://github.com/rhasspy/piper) - Text-to-speech
- [PocketSphinx](https://github.com/cmusphinx/pocketsphinx) - Wake word detection
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM runtime
- [Phi-2](https://huggingface.co/microsoft/phi-2) - Local AI model

Special thanks to the marine open-source community.

---

## License

Tiered licensing model:
- **Tier 0**: Open source (GPL v3)
- **Tier 1**: Free (with cloud sync)
- **Tier 2-3**: Commercial (see LICENSE.md)

---

## Version

**Current Version**: 1.0.0  
**Release Date**: February 2026  
**Status**: Production Ready

---

## Quick Links

- [Download Latest Release](https://github.com/YOUR_USERNAME/helm-os/releases/latest)
- [Installation Guide](docs/INSTALLATION_GUIDE.md)
- [CX5106 Manual](docs/CX5106_USER_MANUAL.md)
- [Voice Commands](docs/VOICE_ASSISTANT.md)
- [API Documentation](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
