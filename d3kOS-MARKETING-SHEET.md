# d3kOS - Marine Intelligence Operating System

**Analogue Engine Monitoring Meets Modern AI**

---

## What is d3kOS?

d3kOS is an open-source, AI-powered diagnostic system that transforms analogue engine gauges into intelligent digital data using the CX5106 NMEA2000 gateway. The system captures analogue dashboard readings (RPM, oil pressure, temperature, fuel level, etc.) and converts them to NMEA2000 network data for real-time monitoring, performance analytics, and predictive diagnostics.

**The Core Innovation:**
- **Analogue-to-Digital Conversion:** CX5106 gateway reads your existing analogue gauges and broadcasts data on NMEA2000 network
- **Engine Analytics:** Captures performance data for diagnostics, trend analysis, and anomaly detection
- **AI-Powered Assistance:** Reads engine manuals (PDFs) and provides recommendations based on sensor data and technical documentation
- **Marine Integration:** Works alongside your existing chartplotter and fishfinder (not a replacement)

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

## How d3kOS Works

### Analogue Dashboard Conversion
Your boat's existing analogue gauges remain in place. The CX5106 NMEA2000 gateway connects to gauge senders (oil pressure sender, temperature sender, fuel sender, etc.) and converts analogue signals to digital NMEA2000 data. d3kOS reads this NMEA2000 data via PiCAN-M HAT and provides:
- Real-time monitoring dashboard
- Performance analytics and diagnostics
- AI-powered recommendations based on sensor data + uploaded manuals
- Data export for maintenance records

### Integration, Not Replacement
**d3kOS is NOT an OpenPlotter replacement.** It's designed to work *alongside* your existing marine electronics:
- Your chartplotter continues to work (Garmin, Simrad, Raymarine, Lowrance, etc.)
- Your fishfinder continues to work
- All devices share NMEA2000 data on the same network
- Optional OpenCPN installation available if you want open-source charts

### The d3kOS Advantage
Traditional chartplotters display engine data on basic gauge pages. d3kOS goes further:
- **Analytics:** Trend analysis, anomaly detection, baseline learning
- **AI Assistant:** Reads your engine manual, answers technical questions
- **Diagnostics:** Export data for mechanics, track maintenance history
- **Enhancements:** Weather radar, camera surveillance, fish identification (coming soon)

---

## Core Capabilities

### 🔌 CX5106 Analogue Dashboard Conversion
**Transform legacy gauges into NMEA2000 digital data**
- Reads analogue gauges: RPM, oil pressure, coolant temperature, fuel level, voltage, boost pressure
- Broadcasts on NMEA2000 network for integration with modern electronics
- Real-time data capture at 1Hz update rate
- No engine modifications required - non-invasive installation
- Works with existing analogue-equipped engines

### 📊 Engine Performance Analytics & Diagnostics
**Intelligent monitoring and trend analysis**
- Baseline establishment during break-in period
- Anomaly detection with >95% accuracy
- Historical performance graphing and trend analysis
- High/low threshold alerts for critical parameters
- 30-day data retention (Tier 0), unlimited (Tier 2+)
- Export data for spreadsheet analysis

### 🤖 AI-Powered Manual Reading & Recommendations
**Your engine expert at the helm**
- Upload PDF manuals: engine service manual, boat owner's manual, CX5106 manual
- AI reads and understands technical documentation
- Provides recommendations based on sensor data + manual knowledge
- Troubleshooting assistance: "Why is my oil pressure low?"
- Both online (OpenRouter GPT) and onboard AI available
- Voice or text interface for hands-free operation

### 🧭 Onboarding Wizard
**Captain-assisted system configuration**
- 20-step guided setup process
- Engine specifications (make, model, cylinders, compression ratio, idle/max RPM)
- CX5106 DIP switch configuration helper with visual diagram
- PDF manual upload integration
- QR code generation for mobile app pairing
- Takes 10-20 minutes to complete

### 📹 Marine Vision System (Phase 2.1 Complete)
**AI-powered camera surveillance**
- Reolink 4K IP67 waterproof camera support
- Live 8 FPS video streaming (720p/1080p)
- Video recording and photo capture
- YOLOv8 object detection (person detection working)
- Fish identification (Phase 2.2 - in development)

### 🗺️ Navigation & Chartplotter Integration
**Works with your existing electronics**
- **NOT an OpenPlotter replacement** - d3kOS integrates alongside your existing systems
- Broadcasts NMEA2000 data for proprietary chartplotters (Garmin, Simrad, Raymarine, Lowrance, Furuno, Humminbird)
- Broadcasts NMEA2000 data for fishfinders (all major brands read standard PGNs)
- Optional OpenCPN installation available (open-source chartplotter)
- GPS/AIS data integration
- Weather radar overlay (Windy.com) with touch-friendly controls

### 🖥️ Touchscreen Interface
**Designed for wet hands and rough seas**
- 7" touch-optimized display (1024×600 minimum)
- Large buttons (60px+ height)
- On-screen keyboard for all inputs
- Dark theme optimized for night vision
- Fullscreen kiosk mode

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
- **Analogue Gateway:** CX5106 NMEA2000 gateway (connects to analogue gauges)
- **Computer:** Raspberry Pi 4B (4GB RAM minimum, 8GB recommended)
- **NMEA2000 Interface:** PiCAN-M HAT (connects Pi to NMEA2000 bus)
- **Display:** 7" touchscreen (1024×600 minimum resolution)
- **Storage:** 16GB microSD card (32GB+ recommended for recordings)
- **Network:** NMEA2000 bus connection (12V, GND, CAN-H, CAN-L)

### Optional Hardware
- **Voice:** Anker S330 speakerphone (Tier 2+ AI voice assistant)
- **Camera:** Reolink RLC-810A (4K, IP67, night vision) for Marine Vision
- **GPS/AIS:** USB receiver for navigation features
- **Charts:** OpenCPN (optional installation, not required)

### Power Requirements
- **Input:** 12V DC (boat power via NMEA2000 bus)
- **Converter:** DC-DC step-down to 5V/3A for Raspberry Pi
- **Consumption:** ~15W typical, ~20W max (with camera)

---

## Key Features by Category

### CX5106 Analogue Dashboard Integration
✅ Reads analogue gauge senders (oil pressure, temperature, fuel, RPM, voltage, boost)
✅ Broadcasts NMEA2000 data to entire network
✅ Real-time 1Hz update rate
✅ Non-invasive installation (no engine modifications)
✅ Works with legacy analogue-equipped engines

### Engine Diagnostics & Analytics
✅ Real-time monitoring dashboard with digital gauges
✅ Anomaly detection with >95% accuracy
✅ Baseline establishment during engine break-in
✅ Trend analysis with historical graphing
✅ High/low threshold alerts for critical parameters
✅ CSV data export for maintenance records

### AI Manual Reading & Recommendations
✅ Upload PDF manuals via onboarding wizard
✅ AI reads and understands technical documentation
✅ Ask questions: "Why is my oil pressure low?" → AI references manual + sensor data
✅ Online AI (OpenRouter GPT) for complex queries (6-8 seconds)
✅ Onboard AI for simple queries (0.17-0.22 seconds, 13 patterns)
✅ Voice or text interface for hands-free operation

### Voice Control (Tier 2+)
✅ Three wake words: "helm", "advisor", "counsel"
✅ 13 instant-answer patterns (RPM, oil, temp, fuel, battery, speed, heading, boost, hours, location, time, help, status)
✅ Emergency voice reboot command when touchscreen fails
✅ 100% offline operation for simple queries
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
❌ **Fish identification:** Custom AI model training in progress (Phase 2.2+)
❌ **Species identification:** Requires pretrained model for common species
❌ **Fishing regulations:** Database integration not complete
❌ **Telegram notifications:** Backend ready but needs user configuration
❌ **Cloud sync:** Not implemented (local storage only)
❌ **Mobile app:** iOS/Android apps not developed yet
❌ **Stripe billing:** E-commerce integration not built (40-60 hours dev time)
❌ **o-charts addon:** Not installed in OpenCPN (optional)
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
4. **Hardware Assembly:**
   - Raspberry Pi 4B + PiCAN-M HAT + touchscreen
   - Connect to NMEA2000 bus (12V, GND, CAN-H, CAN-L)
   - CX5106 gateway already on NMEA2000 bus reading analogue gauges
5. **Boot:** Default login `d3kos` / `d3kos2026` (change password!)
6. **Connect WiFi:** Settings → Network Settings
7. **Onboarding Wizard:** Captain-assisted 20-step configuration (10-20 minutes)
   - Engine specifications (make, model, year, cylinders, RPM range, compression ratio)
   - CX5106 DIP switch configuration with visual diagram
   - Upload PDF manuals (engine service manual, boat owner's manual, CX5106 manual)
   - QR code generation for mobile app pairing
8. **Done:** System captures analogue data, AI reads manuals, ready for diagnostics

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

### For Analogue Engine Owners
- **Preserve Legacy Gauges:** No need to replace working analogue dashboard
- **Digital Diagnostics:** Get modern analytics without engine modifications
- **Predictive Maintenance:** Catch problems before they become failures
- **Performance Tracking:** Historical data shows engine health trends over time

### For DIY Boaters
- **AI Mechanic Assistant:** Upload your engine manual, ask questions, get expert advice
- **Non-Invasive Install:** CX5106 reads gauges, no engine wiring changes required
- **Integration Ready:** Works with your existing chartplotter and fishfinder
- **Open Source:** Modify and customize as needed

### For Diagnostic Analysis
- **Baseline Learning:** System learns normal engine behavior during break-in
- **Anomaly Detection:** 95%+ accuracy identifying unusual sensor readings
- **Trend Analysis:** Graph historical data to spot gradual degradation
- **Export Data:** CSV export for spreadsheet analysis and record keeping

### For Developers
- **Open Architecture:** RESTful APIs, Signal K, Node-RED
- **Microservices:** 12 independent services
- **Extensible:** Add custom sensors, integrations, features
- **Well Documented:** 50+ markdown documentation files

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
