# d3kOS - Marine Helm Control System

**Version**: 1.0.3
**Release Date**: February 18, 2026
**Platform**: Raspberry Pi 4B (4GB/8GB RAM)
**License**: Open Source (see LICENSE.txt)

---

## 📋 Overview

d3kOS is a comprehensive marine electronics system designed for boat operators who want professional-grade engine monitoring, navigation assistance, and AI-powered voice control - all in one touchscreen-optimized interface.

Built on Raspberry Pi 4, d3kOS integrates NMEA2000 engine data, GPS/AIS navigation, IP camera surveillance, and offline AI assistance into a unified system that works reliably on the water.

**Primary Interface**: 10.1" touchscreen with on-screen keyboard
**Primary Input**: Voice commands (hands-free operation)
**Operating Mode**: Fullscreen kiosk (no desktop, automatic startup)

---

## ✨ Key Features

### 🔧 Engine Monitoring & Health
- **Real-time dashboard** - RPM, oil pressure, temperature, fuel, battery
- **Baseline comparison** - Automatic engine benchmarking on first run
- **Anomaly detection** - Alerts for out-of-range conditions
- **Historical graphs** - Track performance over time (Tier 2+)
- **Boat log** - Automatic and manual logging with GPS timestamps

### 🎤 AI Voice Assistant (Tier 2+)
- **Wake words**: "Helm" (auto), "Advisor" (onboard), "Counsel" (online)
- **Hands-free queries** - "What's the RPM?" "What's the oil pressure?"
- **13 instant responses** - Engine data, location, time, help
- **Online AI** - Complex questions via OpenRouter (gpt-3.5-turbo)
- **Response times** - 0.17-0.22s (cached), 6-8s (online)

### 🗺️ Navigation & Charts
- **GPS integration** - Position, speed, heading, satellite count
- **OpenCPN auto-install** - Full chart plotting software (optional)
- **Chartplotter detection** - Auto-detects third-party devices
- **Weather radar** - Windy.com integration with large touch controls
- **AIS support** - Track nearby vessels (with AIS receiver)

### 📷 Marine Vision System (Tier 2+)
- **IP camera integration** - Reolink RLC-810A (4K/1080p, IP67, night vision)
- **Fish capture mode** - Auto-detect person + fish, species identification
- **Forward watch mode** - Marine object detection, distance estimation
- **Telegram notifications** - Instant photo alerts to your phone
- **Recording & snapshots** - Save photos and videos to SD card

### 🌐 Network & Connectivity
- **WiFi Access Point** - SSID: `d3kOS`, Password: `d3kos-2026`
- **Ethernet sharing** - Share internet connection to boat network (10.42.0.0/24)
- **NMEA2000 integration** - PiCAN-M HAT with CAN bus support
- **Signal K server** - Real-time marine data aggregation
- **Web interface** - Access at `http://d3kos.local` or `http://10.42.0.1`

### 📊 Data Export & Cloud Sync (Tier 1+)
- **Automatic export** - Boot-time upload of boat data
- **8 export categories** - Benchmark, boatlog, marine vision metadata, QR code, settings, alerts, onboarding, snapshots
- **Queue & retry system** - 3 retry attempts with exponential backoff
- **JSON format** - Standardized data structure with installation_id
- **Mobile app integration** - Restore configuration after image updates

---

## 🎯 Tier System

d3kOS uses a 4-tier licensing system to unlock features:

| Feature | Tier 0 (FREE) | Tier 1 (FREE) | Tier 2 ($9.99/mo) | Tier 3 ($99.99/yr) |
|---------|---------------|---------------|-------------------|-------------------|
| **Dashboard** | ✓ | ✓ | ✓ | ✓ |
| **Boat log** | ✓ (30 days) | ✓ (60 days) | ✓ (90 days) | ✓ (Unlimited) |
| **Initial Setup resets** | ✓ (10 max) | ✓ (10 max) | ✓ (Unlimited) | ✓ (Unlimited) |
| **Mobile app pairing** | ❌ | ✓ | ✓ | ✓ |
| **Data export** | ❌ | ✓ | ✓ | ✓ |
| **Voice assistant** | ❌ | ❌ | ✓ | ✓ |
| **Camera** | ❌ | ❌ | ✓ | ✓ |
| **Cloud sync** | ❌ | ❌ | ❌ | ✓ |
| **Multi-boat support** | ❌ | ❌ | ❌ | ✓ |

**Auto-Upgrade to Tier 2**: Installing OpenCPN automatically upgrades to Tier 2 (FREE)

---

## 🚀 Quick Start

### 1. Download & Flash Image

```bash
# Download latest image from GitHub Releases
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz

# Verify checksum (IMPORTANT - prevents corrupted image)
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz.sha256
sha256sum -c d3kos-v1.0.3.img.gz.sha256

# Flash to SD card using Raspberry Pi Imager
# - Choose OS → Use custom → Select d3kos-v1.0.3.img.gz
# - Choose storage → Select your SD card (32GB minimum, 128GB recommended)
# - Write → Wait for completion
```

### 2. Hardware Assembly

1. Insert PiCAN-M HAT onto Raspberry Pi GPIO pins
2. Connect touchscreen via HDMI + USB
3. Insert SD card into Raspberry Pi
4. Connect GPS receiver (USB)
5. Connect speaker (Anker S330, USB)
6. Connect 12V power supply → DC converter → Pi USB-C

**See HARDWARE_SETUP_GUIDE.md for detailed wiring diagrams**

### 3. First Boot

1. Power on Raspberry Pi
2. Wait 60-90 seconds for first boot (filesystem expansion)
3. System auto-launches Initial Setup wizard
4. Connect to WiFi AP: SSID `d3kOS`, Password `d3kos-2026`
5. Open web browser on laptop/phone → `http://d3kos.local` or `http://10.42.0.1`

### 4. Complete Initial Setup Wizard

The wizard collects boat and engine information (20 steps, ~5 minutes):

- **Steps 1-4**: Boat info (Manufacturer, Year, Model, Chartplotter)
- **Steps 5-14**: Engine info (Make, Model, Year, Cylinders, Size, Power, RPM range)
- **Steps 15-16**: Regional info (Boat Origin, Engine Position)
- **Steps 17-20**: Completion (Review, DIP Switches, QR Code, Finish)

**Important**: Write down the DIP switch configuration (Step 18) - required for CX5106 gateway setup

### 5. Start Using d3kOS

After completing the wizard:
- Main menu loads automatically
- Dashboard displays engine data (if CX5106 connected)
- Voice assistant ready (Tier 2+)
- Camera accessible (Tier 2+)
- Boat log, navigation, weather, AI assistant pages available

---

## ⚠️ Default Credentials (CHANGE IMMEDIATELY)

**Security Notice**: Change these credentials after first login to protect your system.

| Component | Username | Password |
|-----------|----------|----------|
| **System User** | `d3kos` | `d3kos2026` |
| **SSH Access** | `d3kos` | `d3kos2026` |
| **Desktop Login** | `d3kos` | `d3kos2026` |
| **WiFi AP** | SSID: `d3kOS` | `d3kos-2026` |
| **Web Interface** | `http://d3kos.local` or `http://10.42.0.1` | (no auth) |

**Change system password**:
```bash
ssh d3kos@d3kos.local
passwd
# Enter current password: d3kos2026
# Enter new password: [your secure password]
# Confirm new password: [your secure password]
```

**Change WiFi password**: Settings → Network → Change WiFi Password

---

## 📦 What's Included

### Hardware Requirements

- **Raspberry Pi 4B** (4GB or 8GB RAM)
- **PiCAN-M HAT** (NMEA2000 interface)
- **10.1" Touchscreen** (1920×1200 recommended)
- **32GB SD Card** (minimum, 128GB recommended)
- **USB GPS Receiver** (VK-162 or similar)
- **USB Speaker** (Anker PowerConf S330 for voice)
- **12V to 5V DC Converter** (Victron Orion-Tr or similar)
- **CX5106 Engine Gateway** (NMEA2000 to analog engine sensors)

**Total Cost**: ~$530 USD (see HARDWARE_SETUP_GUIDE.md for BOM)

### Pre-Installed Software

- **Debian 13 (Trixie)** - Operating system
- **Signal K Server** - Marine data aggregation
- **Node-RED** - Automation and API services
- **OpenCPN** - Chart plotting (auto-installed if needed)
- **Chromium Browser** - Web interface renderer (kiosk mode)
- **Wayland + labwc** - Display server and compositor
- **gpsd** - GPS daemon
- **Voice Assistant** - PocketSphinx + Vosk + Piper (Tier 2+)
- **AI Assistant** - OpenRouter integration (online AI)
- **Marine Vision** - YOLOv8 object detection (Tier 2+)
- **13 d3kOS Services** - License, tier, export, camera, fish detection, AI, etc.

---

## 📚 Documentation

- **INSTALLATION_GUIDE.md** - Complete installation walkthrough
- **HARDWARE_SETUP_GUIDE.md** - Bill of materials, wiring diagrams, assembly
- **TROUBLESHOOTING_GUIDE.md** - Common issues and solutions
- **UPGRADE_GUIDE.md** - How to update to newer versions
- **CHANGELOG.md** - Version history and release notes
- **RELEASE_NOTES_v1.0.3.md** - What's new in this version
- **AI_ASSISTANT_USER_GUIDE.md** - Using the AI assistant (text + voice)
- **MARINE_VISION_API.md** - Developer reference for camera system

---

## 🐛 Known Issues (v1.0.3)

### 1. Voice Assistant Wake Word Detection (CRITICAL)

**Status**: Not working reliably
**Affected**: Tier 2+ users
**Issue**: PocketSphinx wake word detection fails to trigger ("helm", "advisor", "counsel")
**Workaround**: Use text-based AI Assistant at `http://d3kos.local/ai-assistant.html`
**Root Cause**: Under investigation - PipeWire audio interference, PocketSphinx subprocess integration issues
**Tracking**: GitHub Issue #TBD

**Evidence**:
- Microphone captures audio correctly (`arecord` works)
- PocketSphinx process runs but doesn't detect speech
- PipeWire reduces microphone signal by 17× (0.18% vs 3.1% direct)
- Service logs show "Listening for wake words..." but no detections

**Recommendation**: Dedicated debugging session planned (2-3 hours)

### 2. Boatlog Export Button Crash

**Status**: Known issue
**Affected**: All tiers
**Issue**: Export button on Boatlog page causes browser crash
**Workaround**: Use Settings → Data Management → Export All Data Now
**Fix**: Scheduled for v1.0.4

### 3. Charts Page Missing o-charts Addon

**Status**: Known limitation
**Affected**: Users without third-party chartplotters
**Issue**: OpenCPN launches but no charts installed by default
**Workaround**: Manually install o-charts plugin and charts (see OpenCPN docs)
**Fix**: Auto-install planned for v1.0.5

### 4. GPS Drift Indoors

**Status**: Expected behavior
**Issue**: GPS shows 2 knots speed and changing course when stationary indoors
**Cause**: Weak satellite signals (3 satellites, HDOP 3.57) cause position "wander" within error circle
**Workaround**: GPS is designed for outdoor use - indoors accuracy is ±10-30m
**Outdoor Expected**: 8+ satellites, HDOP <2.0, 0 knots when stationary

### 5. Small SD Card Storage Warnings

**Status**: User configuration issue
**Issue**: 16GB SD cards fill up quickly (456MB free after installation)
**Recommendation**: Use 128GB SD card for camera recordings and system logs
**Workaround**:
  - Automatic media cleanup after 7 days
  - Manual cleanup: Settings → Data Management → Clear Old Files
  - Transfer camera recordings to mobile app

---

## 🔧 Support & Community

### Getting Help

1. **Documentation First** - Check TROUBLESHOOTING_GUIDE.md for common issues
2. **GitHub Discussions** - Q&A and community support
3. **GitHub Issues** - Bug reports and feature requests
4. **Email Support** - Tier 3 subscribers only (24-hour response)

### Community Resources

- **GitHub Repository**: https://github.com/SkipperDon/d3kos
- **Wiki**: Detailed guides and tutorials
- **At My Boat Blog**: https://atmyboat.com (boating stories, DIY guides)
- **Discord** (future): Real-time community chat

### Contributing

d3kOS is open source! Contributions welcome:
- Bug fixes and feature improvements
- Documentation updates
- Hardware testing and compatibility
- Translations (future)

**See CONTRIBUTING.md** (coming soon)

---

## 📄 License

d3kOS is released under open source licensing:
- **d3kOS Core Software**: MIT License
- **Third-Party Components**: Various (see LICENSE.txt)

**Commercial Use**: Allowed with attribution
**Modifications**: Allowed and encouraged
**Distribution**: Allowed with original license

---

## 🙏 Acknowledgments

- **Signal K Project** - Marine data standards and server
- **Node-RED Community** - Automation platform
- **OpenCPN Project** - Open-source chart plotting
- **Anthropic** - Claude AI assistance in development
- **Raspberry Pi Foundation** - Affordable computing platform
- **SkipperDon** - Project creator and maintainer
- **At My Boat Community** - Beta testing and feedback

---

## 🚢 Ready to Deploy?

1. Read INSTALLATION_GUIDE.md for complete setup instructions
2. Download d3kOS image from GitHub Releases
3. Flash to SD card, assemble hardware, power on
4. Complete Initial Setup wizard
5. Start monitoring your engine!

**Questions?** Check TROUBLESHOOTING_GUIDE.md or ask in GitHub Discussions.

**Happy boating! ⚓**

---

**Project**: d3kOS Marine Helm Control System
**Version**: 1.0.3
**Release Date**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
**Repository**: https://github.com/SkipperDon/d3kos
