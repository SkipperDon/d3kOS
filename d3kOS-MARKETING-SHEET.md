# d3kOS - Marine Intelligence Operating System

**Smart Marine Electronics for Modern Boaters**

---

## What is d3kOS?

d3kOS is an open-source, AI-powered marine operating system that transforms a Raspberry Pi into a professional-grade helm control system. Designed specifically for marine environments, d3kOS provides real-time engine monitoring, voice-controlled assistance, GPS/AIS navigation, IP camera surveillance, and intelligent anomaly detection—all at a fraction of traditional marine electronics costs.

**Cost Comparison:**
- Traditional marine electronics: $5,000 - $15,000+
- d3kOS system: ~$500 hardware + free open-source software

---

## ⚠️ BETA TESTING BUILD - NOT PRODUCTION READY

**Current Status: v2.0-T3 (Testing Build)**

This is a **BETA/TESTING release** for early adopters and testers. The system is functional but:
- ❌ **NOT for production marine use**
- ❌ **NOT for safety-critical applications**
- ❌ **NOT for commercial vessels**
- ✅ **FOR testing, feedback, and evaluation only**

**Use at your own risk.** Always maintain traditional backup navigation and monitoring systems.

---

## Core Capabilities

### 🚢 Marine Electronics Integration
**Professional NMEA2000 connectivity**
- Real-time engine monitoring (RPM, oil pressure, temperature, fuel)
- GPS/AIS position tracking and vessel traffic awareness
- Works with standard marine sensors via PiCAN-M HAT
- Signal K data hub for cross-platform compatibility
- CX5106 NMEA2000 gateway integration

### 🤖 AI-Powered Voice Assistant
**Hands-free helm control with natural language**
- Wake word detection: Say "HELM" to activate (100% offline)
- 13 instant-answer queries (0.17-0.22 second response)
- Emergency voice reboot: "HELM, reboot" when touchscreen fails
- Real-time sensor data integration
- Complex queries via online AI (6-8 seconds)

### 📹 Marine Vision System
**AI-powered camera surveillance**
- Reolink 4K IP67 waterproof camera support
- Live 8 FPS video streaming (720p/1080p)
- Video recording and photo capture
- YOLOv8 object detection (person detection working)
- Auto-cleanup storage management (7-day retention)

### 🖥️ Touchscreen Interface
**Designed for wet hands and rough seas**
- 7" touch-optimized display (1024×600 minimum)
- Large buttons (60px+ height)
- On-screen keyboard for all inputs
- Dark theme optimized for night vision
- Fullscreen kiosk mode

### 🗺️ Navigation Integration
**Seamless OpenCPN chartplotter**
- Auto-installation and configuration
- NMEA2000 data integration
- GPS/AIS display
- Weather radar overlay (Windy.com)
- Touch-friendly controls (80px zoom buttons)

### 🔧 Self-Healing System
**Automated monitoring and recovery**
- CPU temperature, memory, disk space monitoring
- Service health checks (12 microservices)
- Automatic service restarts on failure
- Temp file cleanup and log rotation
- Real-time status dashboard

### 💾 Data Management
**Export and backup automation**
- Boatlog CSV export (spreadsheet download)
- Queue-based export with 3 retry attempts
- 8 export categories (engine data, logs, settings)
- Automated 36MB compressed backups
- Installation ID and license tracking

### 📡 Network Management
**Touch-optimized WiFi control**
- WiFi network scan and connect
- Password entry via on-screen keyboard
- Real-time connection status
- Client mode only (no AP/hotspot due to hardware)

---

## System Requirements

### Minimum Hardware
- **Computer:** Raspberry Pi 4B (4GB RAM minimum, 8GB recommended)
- **Storage:** 16GB microSD card (32GB+ recommended for recordings)
- **Interface:** PiCAN-M HAT or compatible NMEA2000 interface
- **Display:** 7" touchscreen (1024×600 minimum resolution)
- **Network:** NMEA2000 bus connection (12V, GND, CAN-H, CAN-L)

### Optional Hardware
- **Voice:** Anker S330 speakerphone (Tier 2+ features)
- **Camera:** Reolink RLC-810A (4K, IP67, night vision)
- **GPS/AIS:** USB receiver for navigation features

### Power Requirements
- **Input:** 12V DC (boat power via NMEA2000 bus)
- **Converter:** DC-DC step-down to 5V/3A for Raspberry Pi
- **Consumption:** ~15W typical, ~20W max (with camera)

---

## Key Features by Category

### Engine Monitoring
✅ Real-time gauges (1Hz update rate)
✅ Anomaly detection (>95% accuracy)
✅ Baseline establishment and trend analysis
✅ High/low threshold alerts
✅ Historical data graphing

### Voice Control
✅ Three wake words: "helm", "advisor", "counsel"
✅ 13 instant-answer patterns (RPM, oil, temp, fuel, battery, speed, heading, boost, hours, location, time, help, status)
✅ Emergency voice reboot command
✅ 100% offline operation (no internet required)
✅ Response caching (100× speed boost)

### Safety Features
✅ Emergency reboot via voice when touchscreen fails
✅ Self-healing system (auto-recovery from failures)
✅ Thermal protection (automatic throttling at 80°C)
✅ Low storage alerts (warnings at 90%, critical at 95%)
✅ Service health monitoring (auto-restart on crash)

### Data & Logs
✅ Boat log with voice-to-text entry
✅ 30-day data retention (Tier 0), unlimited (Tier 2+)
✅ CSV export for spreadsheet analysis
✅ Automated backups (36MB compressed)
✅ Installation ID for multi-device pairing

### Connectivity
✅ WiFi client mode (connect to existing networks)
✅ Ethernet support (wired connection)
✅ Signal K WebSocket streaming
✅ RESTful APIs (11 endpoints across 12 services)
✅ Node-RED integration (flow-based automation)

---

## What's NOT Ready Yet

### Known Limitations (Beta Testing)
❌ **Fish detection:** Custom model not trained yet (person detection works)
❌ **Telegram notifications:** Backend ready but needs user configuration
❌ **Cloud sync:** Not implemented (local storage only)
❌ **Mobile app:** iOS/Android apps not developed yet
❌ **Stripe billing:** E-commerce integration not built (40-60 hours dev time)
❌ **o-charts addon:** Not installed in OpenCPN
❌ **WiFi hotspot:** Hardware limitation (BCM4345/6 firmware error)

### Critical Known Issues
⚠️ **Voice/touchscreen conflict:** Stopping voice service breaks touchscreen (use emergency voice reboot)
⚠️ **GPS drift indoors:** 3 satellites causes ±10-30m position wander (normal with weak signal)
⚠️ **Storage limited:** 11GB used / 15GB total (80% full) - 32GB+ SD card recommended
⚠️ **Camera 4K unstable:** Use 720p/1080p sub-stream for stability

---

## Installation Overview

### Quick Start (30-60 minutes)
1. **Download:** 9.2 GB image from Google Drive
2. **Verify:** SHA256 checksum `51f5a3115...53ec368`
3. **Flash:** Win32DiskImager/Balena Etcher to 16GB+ SD card
4. **Assemble:** Pi 4B + PiCAN-M HAT + touchscreen + NMEA2000
5. **Boot:** Default login `d3kos` / `d3kos2026` (change password!)
6. **Connect WiFi:** Settings → Network Settings
7. **Onboarding:** 13-question engine wizard (10-20 minutes)
8. **Done:** System ready for testing

### Default Credentials
- **Username:** `d3kos`
- **Password:** `d3kos2026`
- **⚠️ CRITICAL:** Change password immediately after first login!

---

## Licensing & Tiers

### Tier 0: Open Source (FREE)
✅ NMEA2000 integration
✅ Real-time dashboard
✅ Engine health monitoring
✅ GPS/AIS integration
✅ Boat log (30-day retention)
✅ OpenCPN chartplotter
❌ Voice assistant (disabled)
❌ Camera integration (disabled)

### Tier 2: Premium (Mobile App - FREE)
✅ All Tier 0 features
✅ **Voice assistant enabled**
✅ **Camera integration enabled**
✅ Unlimited boat log retention
✅ Unlimited onboarding resets
✅ Extended data retention (90 days)

### Tier 3: Enterprise (Subscription - $9.99/mo planned)
✅ All Tier 2 features
✅ Cloud sync (not implemented yet)
✅ Remote monitoring (not implemented yet)
✅ Multi-device support (not implemented yet)
✅ Priority support

**Current Testing Build:** Tier 3 enabled for evaluation (all features unlocked)

---

## Support & Documentation

### Getting Help
- **GitHub:** https://github.com/SkipperDon/d3kOS
- **Issues:** https://github.com/SkipperDon/d3kOS/issues
- **Email:** support@atmyboat.com
- **Website:** https://atmyboat.com

### Documentation
- **README:** Complete system overview
- **MASTER_SYSTEM_SPEC:** 2,000+ line technical specification
- **AI Assistant Guide:** Voice and text interface usage
- **Marine Vision API:** Camera system reference
- **Release Notes:** v2.0-T3 complete changelog

### Testing & Feedback
**We need your help!** Report issues with:
- Installation ID (from Settings)
- Hardware specs (Pi model, SD card size)
- Steps to reproduce
- Log output: `journalctl -u <service-name> -n 100`

---

## Why d3kOS?

### For DIY Boaters
- **Affordable:** $500 vs $5,000+ traditional systems
- **Customizable:** Open source, modify as needed
- **Modern:** AI, voice control, touchscreen interface
- **Maintainable:** Standard Raspberry Pi hardware

### For Developers
- **Open Architecture:** RESTful APIs, Signal K, Node-RED
- **Microservices:** 12 independent services
- **Extensible:** Add custom sensors, integrations, features
- **Well Documented:** 50+ markdown documentation files

### For Marine Enthusiasts
- **Innovative:** Voice control at the helm
- **Intelligent:** AI anomaly detection, self-healing
- **Connected:** Camera surveillance, GPS/AIS tracking
- **Future-Proof:** Regular updates, active development

---

## Download & Try It

**Latest Release:** v2.0-T3 (February 22, 2026)
**Download:** [Google Drive - 9.2 GB](https://drive.google.com/file/d/1pGdv_EGTI4CZ5JDrbiIRJYr09Dz5dvIS/view?usp=sharing)
**GitHub:** [Release Page](https://github.com/SkipperDon/d3kOS/releases/tag/v2.0-T3)

---

## Legal Disclaimer

**⚠️ BETA SOFTWARE - USE AT YOUR OWN RISK**

d3kOS v2.0-T3 is BETA/TESTING software not suitable for production marine use. By downloading and using d3kOS, you acknowledge:

- This software is provided "AS IS" without warranty of any kind
- Not for navigation, safety, or critical marine operations
- Always maintain redundant backup systems
- Developer assumes no liability for damages, injuries, or losses
- Not certified or approved by maritime authorities
- Testing and evaluation purposes only

**DO NOT rely on d3kOS as your primary marine electronics system.**

---

## Credits

**Developed by:** Skipper Don (donmo) @ AtMyBoat.com
**AI Development Partner:** Claude Sonnet 4.5 (Anthropic)
**Open Source Components:** Debian, Signal K, Node-RED, Vosk, Piper, YOLOv8, OpenCPN

---

**© 2026 AtMyBoat.com | d3kOS is open-source software | Tier 2/3 features proprietary**
