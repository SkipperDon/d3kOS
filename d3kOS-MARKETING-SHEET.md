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
The CX5106 NMEA2000 gateway connects to your engine's gauge senders (oil pressure sender, temperature sender, fuel sender, etc.) and converts analogue signals to digital NMEA2000 data. **Note:** CX5106 operates in either analogue OR digital mode, not both simultaneously. d3kOS reads this NMEA2000 data via PiCAN-M HAT and provides:
- Real-time digital monitoring dashboard
- Performance analytics and diagnostics
- AI-powered recommendations based on sensor data + uploaded manuals
- Data export for maintenance records
- Shore-side testing via built-in NMEA2000 simulator (test before deployment)

### Integration, Not Replacement
**d3kOS is NOT an OpenPlotter replacement.** It's designed to work *alongside* your existing marine electronics:
- Your chartplotter continues to work (Garmin, Simrad, Raymarine, Lowrance, etc.)
- Your fishfinder continues to work
- All devices share NMEA2000 data on the same network
- Optional OpenCPN installation available if you want open-source charts

### The d3kOS Advantage
Traditional chartplotters display engine data on basic gauge pages. d3kOS goes further:
- **Analytics:** Trend analysis, anomaly detection, baseline learning
- **AI Assistant:** Reads your engine manual, answers technical questions (online OR offline)
- **Document Management:** Upload and organize all boat/engine documentation, automatic manual search
- **Conversation History:** Review past troubleshooting sessions, learn from historical AI interactions
- **Shore-Side Testing:** NMEA2000 simulator validates system before boat installation
- **Diagnostics:** Export data for mechanics, track maintenance history
- **Enhancements:** Weather radar, camera surveillance, fish identification (coming soon)

---

## Core Capabilities

### 🔌 CX5106 Analogue Dashboard Conversion
**Transform legacy gauges into NMEA2000 digital data**
- Reads analogue sensor signals: RPM, oil pressure, coolant temperature, fuel level, voltage, boost pressure
- Broadcasts on NMEA2000 network for integration with modern electronics
- Real-time data capture at 1Hz update rate
- No engine modifications required - non-invasive installation
- **Note:** CX5106 operates in either analogue OR digital mode, not both simultaneously

### 📊 Digital Dashboard
**Real-time engine monitoring display**
- Live digital gauges for all engine parameters
- 4 rows: Engine Metrics, Tank Levels, System Status, Network Status
- Updates every second via Signal K WebSocket
- Touch-optimized interface with large fonts (48px gauge values)
- Dark theme (#000000 background, #00CC00 accents)
- Accessible via main menu or browser at port 80

### 📈 Benchmark System
**Engine performance baseline and trending**
- Establishes normal operating parameters during break-in period
- Anomaly detection with >95% accuracy
- Historical performance graphing and trend analysis
- Compares current readings against established baseline
- High/low threshold alerts for critical parameters
- 30-day data retention (Tier 0), unlimited (Tier 2+)

### 🧭 Navigation
**GPS/AIS position tracking and display**
- Real-time GPS position, speed, heading
- Satellite count and HDOP (signal quality)
- WebSocket connection to Signal K for live data
- Touch-optimized map display
- Integration with NMEA2000 bus for vessel traffic (AIS)

### 📓 Boatlog
**Voice and text boat log entries**
- Voice-to-text entry (Tier 2+)
- Manual text entry via on-screen keyboard
- Automatic weather logging
- CSV export for spreadsheet analysis
- 30-day retention (Tier 0), unlimited (Tier 2+)
- Timestamped entries with GPS coordinates

### ☁️ Weather Radar
**Real-time weather overlay and forecasts**
- Windy.com integration with live radar
- Touch-friendly zoom controls (80px buttons)
- Current GPS position centering
- Wind, clouds, rain, temperature overlays
- Auto-updates based on boat position

### 📹 Marine Vision
**AI-powered camera surveillance**
- Reolink 4K IP67 waterproof camera support
- Live 8 FPS video streaming (720p/1080p sub-stream)
- Video recording and photo capture
- YOLOv8 object detection (person detection working)
- Fish identification (Phase 2.2 - in development)
- Telegram notifications (backend ready)
- Storage management with 7-day retention

### 🗺️ Charts (OpenCPN)
**Optional open-source chartplotter**
- OpenCPN auto-installation and configuration
- NMEA2000 data integration
- GPS/AIS display on charts
- Touch-friendly navigation controls
- **Optional** - d3kOS works with proprietary chartplotters too

### 📱 QR Code & Mobile Pairing
**Installation ID for mobile app integration**
- 16-character hex installation ID (file-based, persistent)
- QR code generation in onboarding wizard (Step 19)
- Simplified format for easy mobile scanning (400x400px, black on white)
- Used for mobile app pairing and cloud sync

### ⚙️ Settings
**System configuration and management**
- Network Settings (WiFi scan, connect, status)
- Data Management (export, backup, installation ID)
- Telegram Configuration (notifications setup)
- System Information (tier, version, services)
- Manual Management (view, upload, delete PDFs)
- Touch-optimized interface with on-screen keyboard

### 🎛️ Helm
**Voice and text AI assistant interface**
- Text-based chat interface for AI queries
- Voice command support (Tier 2+: "helm", "advisor", "counsel")
- Real-time sensor data display
- Emergency voice reboot capability
- Fullscreen toggle for on-screen keyboard access

### 🤖 AI Assistant
**Text-based AI chat interface**
- Dedicated chat page at /ai-assistant.html
- Provider selector (Auto, Online, Onboard)
- Real-time response with metadata display
- Newest messages at top, scroll down for history
- Input field at bottom with on-screen keyboard
- 13 instant-answer patterns (0.17-0.22s cached)

### 📚 Manual Management
**PDF documentation library**
- Upload engine service manuals, boat owner's manuals, CX5106 manual
- Automatic search for manuals online (DuckDuckGo + manufacturer links)
- View, organize, delete uploaded PDFs
- AI reads manuals for recommendations
- Validation (PDF format check)
- Accessible via Settings → Manual Management

### 💬 History
**AI conversation tracking**
- Stored chat history with both online and onboard AI responses
- Review past troubleshooting sessions
- SQLite database: `/opt/d3kos/data/conversation-history.db`
- Learn from historical AI interactions
- Useful for tracking diagnostic patterns over time

### 🧪 NMEA2000 Simulator
**Shore-side testing before deployment**
- Built-in virtual CAN interface (vcan0)
- Generates realistic engine data (RPM varies 800-2400, boost, trim)
- Test dashboard, alerts, AI without real engine
- Toggle on/off via dashboard or systemd service
- Perfect for system validation before boat installation

### 🧭 Onboarding Wizard
**Captain-assisted 20-step configuration**
- Engine specifications (make, model, year, cylinders, compression ratio, idle/max RPM)
- Regional and position information
- CX5106 DIP switch configuration with visual diagram
- PDF manual upload integration
- Configuration review (Step 17)
- QR code generation (Step 19)
- Takes 10-20 minutes to complete

### 🌐 Remote Access Methods
**Multiple ways to connect to d3kOS**
- **Web Browser:** http://192.168.1.237/ (any device on network)
- **RealVNC:** Remote desktop access (graphical interface)
- **SSH:** Terminal access via `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- **Raspberry Pi Connect:** Cloud-based remote access (optional)
- All methods work from shore or remote locations

### 🖥️ Touchscreen Interface
**Designed for wet hands and rough seas**
- 7" touch-optimized display (1024×600 minimum)
- Large buttons (60px+ height), 22-24px fonts
- On-screen keyboard (Squeekboard) for all inputs
- Dark theme optimized for night vision (#000000 bg, #00CC00 green, #FFFFFF white)
- Fullscreen kiosk mode
- Auto-focus on input fields for keyboard activation

### 🔧 Self-Healing System
**Automated monitoring and recovery**
- CPU temperature, memory, disk space monitoring
- Service health checks (12 microservices on ports 8080-8101)
- Automatic service restarts on failure
- Temp file cleanup and log rotation
- Real-time status dashboard at port 8099

### 💾 Data Management & Export
**Backup and data export automation**
- Boatlog CSV export (spreadsheet download)
- Queue-based export with 3 retry attempts (5s delay)
- 8 export categories (engine data, boatlog, marine vision metadata, QR code, settings, alerts, onboarding)
- Automated 36MB compressed backups (Backup API port 8100)
- Installation ID and license tracking
- Export API at port 8094

### 📡 Network Management
**Touch-optimized WiFi control**
- WiFi network scan and connect (Network API port 8101)
- Password entry via on-screen keyboard
- Real-time connection status with auto-refresh
- PolicyKit authorization (no sudo required)
- Client mode only (no AP/hotspot - hardware limitation BCM4345/6)

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

### Main Menu Pages (Touch-Optimized Interface)
✅ **Digital Dashboard** - Real-time engine gauges, 4-row layout
✅ **Onboarding** - 20-step wizard with QR code generation
✅ **Boatlog** - Voice/text entries with CSV export
✅ **Navigation** - GPS/AIS position tracking
✅ **Helm** - Voice and text AI assistant
✅ **Weather** - Windy.com radar with touch controls
✅ **AI Assistant** - Dedicated chat interface
✅ **Settings** - Network, data, manual, Telegram config
✅ **Charts** - OpenCPN chartplotter (optional)
✅ **Marine Vision** - Camera surveillance and AI detection

### CX5106 Integration & Data Flow
✅ Reads analogue sensor signals (oil, temp, fuel, RPM, voltage, boost)
✅ Broadcasts NMEA2000 data to entire network
✅ Real-time 1Hz update rate via Signal K
✅ Non-invasive installation (no engine modifications)
✅ Digital OR analogue mode (not both simultaneously)

### Engine Diagnostics & Benchmarking
✅ Digital dashboard with real-time gauges (48px values)
✅ Benchmark system with baseline establishment
✅ Anomaly detection with >95% accuracy
✅ Trend analysis with historical graphing
✅ High/low threshold alerts for critical parameters
✅ CSV data export for maintenance records

### AI System (Online + Onboard)
✅ **PDF Manual Management:** Upload, organize, search, delete
✅ **Automatic Manual Search:** DuckDuckGo + manufacturer links
✅ **Conversation History:** SQLite database, review past sessions
✅ **Online AI:** OpenRouter GPT, 6-8s response time
✅ **Onboard AI:** 13 instant patterns (0.17-0.22s), complex queries (60-180s offline-capable)
✅ **Patient Diagnostics:** Offline troubleshooting, references manuals + sensor data
✅ **Voice or Text:** Hands-free operation at helm
✅ **Example:** "Why is my oil pressure low?" → AI checks manual specs + current readings

### Voice Control (Tier 2+)
✅ Three wake words: "helm" (auto), "advisor" (onboard), "counsel" (online)
✅ 13 instant-answer patterns (RPM, oil, temp, fuel, battery, speed, heading, boost, hours, location, time, help, status)
✅ Emergency voice reboot: "HELM, reboot" when touchscreen fails
✅ 100% offline operation for simple queries
✅ Response caching (100× speed boost: 18s → 0.17s)
✅ PocketSphinx wake word + Vosk transcription + Piper TTS

### Navigation & Positioning
✅ GPS position, speed, heading display
✅ Satellite count and HDOP (signal quality)
✅ WebSocket connection to Signal K
✅ AIS vessel traffic integration (NMEA2000 bus)
✅ Weather radar overlay (Windy.com)
✅ Touch-friendly zoom controls (80px buttons)

### Boatlog & Data Logging
✅ Voice-to-text entry (Tier 2+)
✅ Manual text entry via on-screen keyboard
✅ Automatic weather logging
✅ CSV export for spreadsheet analysis
✅ 30-day retention (Tier 0), unlimited (Tier 2+)
✅ Timestamped entries with GPS coordinates

### Marine Vision (Camera System)
✅ Reolink RLC-810A 4K IP67 support
✅ Live 8 FPS video streaming (720p/1080p)
✅ Video recording and photo capture
✅ YOLOv8n object detection (person detection working)
✅ Fish identification (Phase 2.2 - in development)
✅ Telegram notifications (backend ready, needs config)
✅ Storage management with 7-day retention

### Charts & Chartplotter Integration
✅ **NOT OpenPlotter replacement** - works alongside existing chartplotters
✅ Broadcasts NMEA2000 data (Garmin, Simrad, Raymarine, Lowrance, Furuno, Humminbird)
✅ Fishfinders read NMEA2000 data (all major brands)
✅ Optional OpenCPN installation (open-source chartplotter)
✅ GPS/AIS integration, touch-friendly controls

### Settings & Configuration
✅ Network Settings: WiFi scan, connect, password entry (on-screen keyboard)
✅ Data Management: Export, backup, installation ID display
✅ Telegram Configuration: Bot token, chat ID, test notifications
✅ Manual Management: View, upload, delete PDFs
✅ System Information: Tier, version, services status
✅ Touch-optimized interface, auto-refresh status

### QR Code & Mobile Pairing
✅ 16-character hex installation ID (file-based: `/opt/d3kos/config/license.json`)
✅ QR code generation in onboarding (Step 19)
✅ Simplified format (400x400px, black on white, plain text)
✅ Used for mobile app pairing and cloud sync
✅ Persistent across reboots (not browser cache)

### NMEA2000 Simulator
✅ Built-in virtual CAN interface (vcan0)
✅ Realistic engine data (RPM 800-2400, boost, trim)
✅ Shore-side testing before deployment
✅ Toggle on/off via dashboard or systemd
✅ Test all features without real engine

### Remote Access
✅ **Web Browser:** http://[IP]/ (any device on network)
✅ **RealVNC:** Remote desktop (graphical)
✅ **SSH:** Terminal access (key-based auth)
✅ **Pi Connect:** Cloud-based remote access (optional)

### Self-Healing & Monitoring
✅ CPU temperature, memory, disk space monitoring
✅ Service health checks (12 microservices, ports 8080-8101)
✅ Automatic service restarts on failure
✅ Temp file cleanup and log rotation
✅ Real-time status dashboard (port 8099)

### Data Export & Backup
✅ Boatlog CSV export (spreadsheet download)
✅ Queue-based export with 3 retry attempts (5s delay)
✅ 8 export categories (engine, boatlog, marine vision metadata, QR, settings, alerts, onboarding)
✅ Automated 36MB compressed backups (port 8100)
✅ Export API (port 8094)

### Safety Features
✅ Emergency voice reboot when touchscreen fails
✅ Self-healing auto-recovery from failures
✅ Thermal protection (throttling at 80°C)
✅ Low storage alerts (90% warning, 95% critical)
✅ Service health monitoring (auto-restart on crash)

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
- **AI Mechanic Assistant:** Upload your engine manual, ask questions, get expert advice (even offline!)
- **Document Library:** Automatic manual search + management system for all your boat documentation
- **Shore-Side Testing:** Built-in NMEA2000 simulator - verify everything works before installing on boat
- **Non-Invasive Install:** CX5106 reads sensor signals, no engine wiring changes required
- **Integration Ready:** Works with your existing chartplotter and fishfinder
- **Open Source:** Modify and customize as needed

### For Diagnostic Analysis
- **Baseline Learning:** System learns normal engine behavior during break-in
- **Anomaly Detection:** 95%+ accuracy identifying unusual sensor readings
- **Trend Analysis:** Graph historical data to spot gradual degradation
- **Conversation History:** Review past AI troubleshooting sessions (online and onboard)
- **Offline Diagnostics:** Onboard AI works without internet - patient troubleshooting (1-2 minutes) when needed
- **Manual Integration:** AI cross-references sensor data with uploaded engine manuals
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
