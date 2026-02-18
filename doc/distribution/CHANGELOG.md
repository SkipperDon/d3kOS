# d3kOS Changelog

All notable changes to d3kOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.3] - 2026-02-18

### Added

**Installation ID System** - File-based persistent installation tracking
- 16-character hex installation ID (SHA-256 hash of MAC address + timestamp)
- Stored in `/opt/d3kos/config/license.json` (survives browser cache clears)
- Generated on first boot (before Initial Setup wizard)
- License API service (port 8091) - GET `/license/info`, GET `/license/full`
- QR code simplified to plain text (16 chars) for better mobile scanning

**Tier System** - 4-tier licensing with feature restrictions
- Tier 0 (FREE): Base system, dashboard, boat log (30 days), 10 resets max
- Tier 1 (FREE): Mobile app pairing, data export, config restore
- Tier 2 ($9.99/month): Voice assistant, camera, unlimited resets, historical graphs (90 days)
- Tier 3 ($99.99/year): Cloud sync, multi-boat support, unlimited features
- Auto-upgrade to Tier 2 when OpenCPN detected (FREE)
- Tier detection service (port 8093) - Checks OpenCPN installation every 24 hours
- Tier management service (boot-time tier detection)

**Data Export System** - Central database sync with queue and retry
- Export manager service (port 8094) - POST `/export/generate`, GET `/export/status`
- 8 export categories: benchmark, boatlog, marine vision metadata, QR code, settings, alerts, onboarding, snapshots
- JSON format with installation_id, timestamp, tier, format_version
- Queue system with 3 retry attempts (immediate, 5min, 15min)
- Boot-time automatic export (checks queue and uploads pending)
- Tier 1+ requirement (Tier 0 has NO export capability)

**Marine Vision Telegram Notifications** - Instant fish capture alerts
- Notification manager service (port 8088) - POST `/notify/send`, POST `/notify/test`, GET `/notify/failed`
- Telegram bot integration with photo uploads (up to 10MB)
- Auto-formatted messages with species, confidence, GPS, regulations, Google Maps links
- Queue and retry system (3 attempts, 5-second delay)
- Failed notification tracking
- Settings UI page (settings-telegram.html) for bot configuration

**Voice/AI Performance Optimization** - 132× faster cached responses
- Signal K data caching (3-second TTL) - reduces response time from 18s to 0.17s
- Persistent AI query handler (cache survives across requests)
- Expanded rule-based patterns (13 instant-response queries: rpm, oil, temp, fuel, battery, speed, heading, boost, hours, location, time, help, status)
- Removed Phi-2 LLM (60-180s response time too slow, 1.7GB storage recovered)
- Smart data fetching (time/help queries skip boat data fetch)

**GPS Configuration Fix** - gpsd and Signal K integration
- gpsd now configured with `/dev/ttyACM0` device
- Signal K uses gpsd protocol (localhost:2947) instead of direct serial
- Eliminates gpsd/Signal K conflict (both trying to read same serial device)
- Zero latitude errors (was 100+ errors/minute)

**Session Coordination** - Multi-session parallel development
- `.session-status.md` - Active sessions registry
- `.domain-ownership.md` - File/directory ownership map
- `multi-session-protocol.md` - Coordination rules for parallel Claude Code sessions

**Documentation** - Comprehensive user and developer guides
- AI_ASSISTANT_USER_GUIDE.md (20KB, 663 lines) - End-user guide for text and voice AI
- MARINE_VISION_API.md (32KB, 1,228 lines) - Developer API reference with code examples
- MARINE_VISION_NOTIFICATION_INTEGRATION.md (12KB) - Telegram notification integration guide
- MARINE_VISION_NOTIFICATION_TESTING.md (16KB, 25 tests) - Testing procedures

### Changed

**Initial Setup Wizard**:
- Step 18 QR code simplified from 170-char JSON to 16-char plain text
- QR code colors changed to standard black-on-white (was green-on-black)
- QR code size increased to 400×400px (was 300×300)
- Error correction level changed to Medium (was High)
- Installation ID now read from license API (not generated in browser)
- Auto-focus added to first input field (fixes on-screen keyboard not appearing)

**AI Assistant**:
- OpenRouter now receives real-time sensor data in context (no more placeholder responses)
- Query handler v5: Removed Phi-2 LLM, rule-based only for onboard mode
- Onboard complex queries now show helpful message: "Connect to internet for complex questions"
- Response metadata includes provider, model, response time

**Web UI**:
- Navigation page WebSocket URL fixed (localhost → window.location.hostname for nginx proxy)
- Weather radar default GPS position added (Lake Simcoe: 44.4167, -79.3333) when no GPS fix
- Weather data panel null handling for inland locations (marine API returns null for lakes)
- Helm Assistant auto-focus added (500ms delay)
- Export manager proxy port fixed (8090 → 8094)
- Added `/export/status` endpoint to export manager

**Services**:
- Export manager (Python Flask, port 8094) - Replaces planned Node.js implementation
- Notification manager (Python Flask, port 8088) - New service
- License API (Python Flask, port 8091) - New service
- Tier API (Python Flask, port 8093) - New service
- vcan0 simulator disabled in Signal K (was causing continuous errors)
- Signal K log level changed to "warn" (reduces GPS error spam)

**Storage**:
- System freed 1.7GB by removing Phi-2 model
- Before: 96-97% full (456-537MB free)
- After: 85% full (2.2GB free)
- `/opt/d3kos/models/` now 141MB (was 1.9GB)

### Fixed

**Voice Assistant**:
- PipeWire audio interference identified (17× signal reduction)
- Attempted direct hardware access (`-adcdev plughw:3,0`) - partial success
- **KNOWN ISSUE**: Wake word detection still not working reliably
- Workaround: Use text-based AI Assistant

**GPS**:
- gpsd configuration fixed (`DEVICES="/dev/ttyACM0"`)
- Signal K GPS provider changed to gpsd protocol
- GPS position now flowing to Signal K correctly
- Zero latitude errors (was continuous errors)

**System**:
- Keyring double password entry (disabled keyring)
- Footer showing at bottom of screen (removed Chromium flags)
- On-screen keyboard appearing but not inputting text (AI Assistant page fixed)
- vcan0 simulator error spam (disabled provider)
- APT cache cleanup (freed 131MB)

**Web UI**:
- AI Assistant page fullscreen toggle removed (broke keyboard input) - restored from Feb 13 backup
- Weather radar map shows default GPS when no fix (was blank)
- Weather data panel handles null values for inland locations
- Navigation page GPS data now displays correctly

### Security

- Default credentials documented (CHANGE IMMEDIATELY after first login):
  - System user: d3kos / d3kos2026
  - SSH access: d3kos / d3kos2026
  - WiFi AP: d3kOS / d3kos-2026
- Password change instructions in README.md and INSTALLATION_GUIDE.md

### Known Issues

1. **CRITICAL: Voice Assistant Wake Word Detection Not Working**
   - Status: Under investigation
   - Root cause: PipeWire interference + PocketSphinx subprocess integration issues
   - Workaround: Use text-based AI Assistant (http://d3kos.local/ai-assistant.html)
   - Affected: All Tier 2+ users
   - ETA: Unknown (requires 2-3 hour debugging session)

2. **Boatlog Export Button Crash**
   - Status: Known issue
   - Workaround: Use Settings → Data Management → Export All Data Now
   - Fix: Scheduled for v1.0.4

3. **Charts Page Missing o-charts Addon**
   - Status: Known limitation
   - Workaround: Manually install o-charts plugin via OpenCPN
   - Fix: Auto-install planned for v1.0.5

4. **GPS Drift Indoors**
   - Status: Expected behavior (weak satellite signals)
   - Cause: Indoor GPS accuracy ±10-30m, position "wanders"
   - Expected outdoors: 8+ satellites, HDOP <2.0, stable position

5. **Small SD Card Storage Warnings**
   - Status: User configuration issue
   - Recommendation: Use 128GB SD card (not 16GB)
   - Workaround: Automatic media cleanup after 7 days

### Upgrade Notes

**BREAKING CHANGES** from v1.0.2:
- Installation ID format changed (12-char → 16-char hex)
- Old installation IDs discarded, new ID generated on upgrade
- Mobile app must be re-paired (scan new QR code)
- Tier system enforced (voice/camera disabled for Tier 0/1)
- Upgrade from Tier 0 to Tier 2: Install OpenCPN (FREE auto-upgrade)

**Migration Steps**:
1. See UPGRADE_GUIDE.md for detailed instructions
2. Use Method 1 (SD Card Swap) or Method 2 (In-Place, Tier 2/3 only)
3. After upgrade: Navigate to Settings → License Information
4. Verify tier, install OpenCPN if needed
5. Re-pair mobile app with new QR code

---

## [1.0.2] - 2026-02-14

### Added

**Marine Vision System - Phase 1** - Camera streaming and recording
- Camera stream manager service (port 8084) - Live RTSP feed from Reolink RLC-810A
- Flask API with 6 endpoints: status, frame, record/start, record/stop, recordings, capture
- Background frame grabber (30 FPS, ONNX Runtime)
- VLC recording support (H.264 MP4 output)
- Storage: `/home/d3kos/camera-recordings/` (SD card)
- DHCP reservation: 10.42.0.100 for camera (MAC: ec:71:db:f9:7c:7c)
- Web UI: `/marine-vision.html` (12KB) - Live feed (8 FPS), start/stop recording, capture photo, status panel

**Marine Vision System - Phase 2.1** - Fish detection with YOLOv8
- Fish detector service (port 8086) - Object detection using YOLOv8n ONNX model
- ONNX Runtime 1.24.1 (60MB RAM, 13MB model)
- API endpoints: GET `/detect/status`, POST `/detect/frame`, GET `/captures`, GET `/captures/{id}`
- Auto-capture: Triggers when person + fish detected
- Performance: 2-3 seconds per detection on Pi 4B
- Database: SQLite at `/opt/d3kos/data/marine-vision/captures.db`
- **Known Limitation**: Fish detection uses "bird" class proxy (no custom fish model yet)

**Camera Integration**:
- Main menu button added (after Weather button)
- Settings page: Camera Management section - Camera 1 status, "Add New Camera", "View All Cameras"
- Auto-updates every 10 seconds

**Weather Radar - Large Touch Controls**:
- Custom overlay buttons (80×80px) for touchscreen: Zoom In/Out, Recenter on Position
- Green d3kOS theme (#00CC00 border)
- Dark semi-transparent background for visibility
- Touch event support (click + touchend with preventDefault)
- 4× larger than standard Windy.com controls

**Onboarding Wizard Keyboard Fix**:
- Rebuilt wizard using minimal test page structure
- All 20 steps working with physical and on-screen keyboards
- Step 17: Configuration review (displays all 16 answers)
- Step 18: DIP switch diagram (visual █/░ based on config)
- Step 19: QR code generation (QRCode.js, persistent ID)
- Step 20: Fullscreen toggle (restores kiosk mode)
- Main Menu button on ALL pages

**NMEA2000 Simulator** - Testing without real engine
- Virtual CAN interface: `vcan0`
- Simulator script: `/opt/d3kos/simulator/nmea2000-simulator.sh`
- Systemd service: `d3kos-simulator.service` (manual start/stop)
- Data: PGN 127488 (RPM 800-2400, Boost 1.5 bar, 1 Hz update rate)
- Node-RED dashboard toggle

### Changed

**Signal K Configuration**:
- Log level set to "warn" (reduces GPS error spam)
- vcan0-simulator provider disabled by default
- Access: http://192.168.1.237/sk-admin/ (nginx proxy)

**Web Interface**:
- Dashboard: All pages use standalone HTML (not Node-RED Dashboard 2.0)
- Design system: 22-24px fonts, black background, green accents, 60px buttons
- Touch-friendly: 60px min button height, 20px scrollbars
- Signal K WebSocket: ws://localhost:3000/signalk/v1/stream

**Documentation**:
- MARINE_VISION.md (48KB, 1091 lines) - Complete system specification
- MARINE_VISION_PHASE1_COMPLETE.md (14KB) - Phase 1 implementation summary
- MARINE_VISION_PHASE1_FINAL.md (12KB) - Final configuration
- MARINE_VISION_PHASE2.1_COMPLETE.md (11KB) - Phase 2.1 implementation summary
- MARINE_VISION_PHASE2_PLAN.md (19KB) - Phase 2+ roadmap
- WEATHER_2026-02-13.md - Large touch controls documentation
- UPDATES_2026-02-13_PM.md - Session documentation

### Fixed

- Camera firewall blocking Pi (disabled in Reolink app)
- RTSP not enabled by default (factory reset enabled it)
- Camera credentials changed (d3kos:d3kos2026 → admin:d3kos2026 after reset)
- WiFi disconnected during network changes (reconnected and rebooted)
- Main menu button navigation (added onclick handler)
- Camera feed stability (switched to sub-stream)
- Frame rate optimization (0.5 FPS → 8 FPS)
- AtMyBoat.com logo fullscreen toggle

### Storage

- Before: 97% full (456MB free)
- Cleanup: +131MB (journal logs, temp files)
- After: 96% full (537MB free)
- **Critical**: 16GB SD card very limited storage

---

## [1.0.1] - 2026-02-13

### Added

**Hybrid AI Assistant System - Phase 1-3**:
- OpenRouter integration (gpt-3.5-turbo) - 6-8 second response
- Onboard AI: Rule-based responses for simple queries (5-6 seconds)
- Onboard AI: Phi-2 LLM for complex queries (60-180 seconds - too slow)
- Context: skills.md knowledge base (boat system info, capabilities, web URLs)
- Memory: SQLite conversation history (`/opt/d3kos/data/conversation-history.db`)
- Config: `/opt/d3kos/config/ai-config.json` (OpenRouter API key)

**Wake Words - Three Options**:
- **helm** → Auto-select (online if available, onboard if not) → "Aye Aye Captain"
- **advisor** → Force onboard (rule-based if simple, Phi-2 if complex) → "Aye Aye Captain"
- **counsel** → Force online (OpenRouter) → "Aye Aye Captain"

**Signal K Integration (Phase 4.1)**:
- SignalKClient module: `/opt/d3kos/services/ai/signalk_client.py`
- Rule-based responses use real sensor data from NMEA2000
- RPM reading working (engine off = 0, engine on = actual RPM)
- Graceful fallback to simulated values for missing sensors
- Response time: ~23 seconds (includes Signal K fetch)

**Web Text Interface (Phase 5)**:
- Chat page: `/var/www/html/ai-assistant.html`
- AI API server: `/opt/d3kos/services/ai/ai_api.py` (port 8080)
- Systemd service: `d3kos-ai-api.service` (auto-start enabled)
- Nginx proxy: `/ai/` → `localhost:8080/ai/`
- Features: Chat UI, provider selector (auto/online/onboard), response metadata
- Button added to main menu (after Helm button)
- Fullscreen toggles OFF on page load (enables keyboard), ON when returning to main menu
- Chat layout: Newest messages at top, scrolls downward for history, input field at bottom

**Chartplotter Integration**:
- Step 4 of Initial Setup wizard: Chartplotter detection via WebSocket
- Listens for navigation PGNs (129025, 129026, 129029) for 5 seconds
- Auto-selects "I have a chartplotter" if navigation PGNs detected
- Auto-selects "I don't have a chartplotter" if only engine PGNs
- Fullscreen toggle before redirect (restores kiosk mode)

**Nginx Proxy for Signal K**:
- WebSocket proxy: port 80 → port 3000 (IPv4/IPv6 bridge)
- Required for browser WebSocket connections
- URL: `ws://window.location.hostname/signalk/v1/stream?subscribe=none`

### Changed

**Voice Assistant**:
- Hybrid system: PocketSphinx wake word + Vosk STT + Piper TTS
- Wake word threshold: 1e-3 (conservative, reduces false positives)
- Listening duration: 3 seconds (reduced from 5 for faster response)
- Microphone: Auto-detected "S330" or "Anker" (plughw:3,0)
- Response times: 8-12s (simple), 60-80s (complex AI)
- Query classification: Simple patterns vs. Phi-2 LLM
- Dashboard integration: Voice toggle button (top-right, 240×60px, green ON/gray OFF)
- Node-RED endpoints: GET `/voice/status`, POST `/voice/toggle`

**Auto-Start Configuration**:
- Voice service: **DISABLED** (due to touchscreen conflict)
- Manual control: Dashboard toggle or `sudo systemctl start d3kos-voice`

### Fixed

- Touchscreen stops working after voice service stop (requires reboot to restore)
- User group: d3kos added to "input" group
- VNC mouse pointer continues to work when touchscreen fails

### Known Issues

1. **CRITICAL: Touchscreen-Voice Conflict**
   - Touchscreen stops responding after d3kos-voice service is stopped
   - Works fine on boot and while voice service is running
   - Requires reboot or USB replug to restore after voice service stop
   - **Workaround**: Keep voice disabled, only start when needed, avoid stopping
   - **See**: `touchscreen-voice-conflict.md` for investigation details

2. **Voice Wake Word False Positives**
   - Background noise triggers wake word (threshold 1e-3 helps but not perfect)
   - **Mitigation**: Threshold tuning, noise filtering

3. **Phi-2 LLM Too Slow**
   - 60-180 seconds response time on Raspberry Pi 4B
   - Impractical for helm use
   - **Recommendation**: Use "Helm" or "Counsel" wake words, avoid "Advisor" for complex queries

### Documentation

- UPDATES_2026-02-12.md - Hybrid AI system Phase 1
- PHASE_2_COMPLETE.md - Wake words and voice integration
- PHASE_3_COMPLETE.md - Hybrid onboard AI
- MASTER_SYSTEM_SPEC.md v2.4 Section 4.5 - AI Assistant specification
- CLAUDE.md v2.6 - Development guidelines
- SKILLS_MD_SPECIFICATION.md v1.0 - skills.md format
- touchscreen-voice-conflict.md - Detailed issue investigation

---

## [1.0.0] - 2026-02-09

### Added

**Core System**:
- Debian 13 (Trixie) base OS
- Raspberry Pi 4B support (4GB/8GB RAM)
- Wayland display server (labwc compositor) with Xwayland
- Custom d3kOS boot splash (AtMyBoat.com logo)
- Fullscreen kiosk mode (Chromium browser)
- WiFi Access Point: SSID `d3kOS`, Password `d3kos-2026`, Network `10.42.0.0/24`

**Web Interface**:
- Nginx v1.26.3 web server
- Main menu: `/var/www/html/index.html` (20KB) - 9 navigation buttons + AtMyBoat.com logo
- Engine Dashboard: `/var/www/html/dashboard.html` (21KB) - 4 rows (Engine Metrics, Tank Levels, System Status, Network Status)
- Onboarding wizard: `/var/www/html/onboarding.html` (58KB) - 20 steps with QR code generation
- Boatlog: `/var/www/html/boatlog.html` (27KB)
- Navigation: `/var/www/html/navigation.html` (28KB)
- Helm: `/var/www/html/helm.html` (31KB)
- Logo: `/var/www/html/atmyboat.png` (1.5MB) - AtMyBoat.com branding
- Access: http://d3kos.local or http://10.42.0.1

**Initial Setup Wizard (Onboarding)**:
- 20 steps: Welcome → Boat info (4) → Engine info (10) → Regional (2) → Completion (4)
- Step 4: Chartplotter detection (WebSocket-based)
- Step 18: DIP switch configuration (CX5106 setup)
- Step 19: QR code generation (installation ID + system info)
- Step 20: Fullscreen toggle (restores kiosk mode)
- Data saved: `/opt/d3kos/config/onboarding.json`

**QR Code Generation**:
- Library: QRCode.js (https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js)
- Installation ID: XXXX-XXXX-XXXX format (localStorage as 'd3kos-installation-id')
- QR Data: JSON with type, version, host, installationId, urls (web, signalk, nodered, ws), name, timestamp
- Size: 300×300px, High error correction

**Engine Monitoring**:
- Signal K Server - NMEA2000 data aggregation
- Node-RED v4.1.4 - Automation and API services
- Node-RED Dashboard 2.0 (@flowfuse/node-red-dashboard v1.30.2)
- Node.js v20.20.0
- PiCAN-M HAT support (CAN bus interface)
- CX5106 Engine Gateway integration (analog sensors to NMEA2000)
- Real-time dashboard: RPM, oil pressure, temperature, fuel, battery, speed, heading
- Dashboard update frequency: 1 Hz (1 second intervals)

**Navigation**:
- gpsd - GPS daemon
- OpenCPN - Chart plotting (auto-installed if needed)
- GPS/AIS data integration
- Signal K WebSocket stream: ws://localhost:3000/signalk/v1/stream

**Fullscreen Toggle**:
- Script: `/usr/local/bin/toggle-fullscreen.sh` (uses wtype for Wayland)
- Endpoint: POST http://localhost:1880/toggle-fullscreen
- Used by: Engine Setup and Helm buttons (to show on-screen keyboard)

### Design System

- Fonts: 22-24px base, 24px headings, 48px gauge values
- Colors: Black (#000000) background, Green (#00CC00) accents, White (#FFFFFF) text
- Touch-friendly: 60px min button height, 20px scrollbars
- Top navigation bar with "← Main Menu" button standard on all pages
- Standalone HTML files (NOT Node-RED Dashboard 2.0 for main UI)

### Default Credentials

- System User: `d3kos` / `d3kos2026`
- SSH Access: `d3kos` / `d3kos2026`
- Desktop Login: `d3kos` / `d3kos2026`
- WiFi AP: SSID `d3kOS` / `d3kos-2026`
- Web Interface: http://d3kos.local or http://10.42.0.1 (no auth)

### Services

- Signal K: Port 3000 (IPv6 :::3000)
- Node-RED: Port 1880
- Node-RED Dashboard: Port 1880/dashboard
- Nginx: Port 80
- gpsd: Port 2947

### File System Layout

```
/opt/d3kos/
├── config/
│   ├── onboarding.json
│   ├── benchmark-results.json
│   └── engine-manufacturers.json
├── state/
│   └── onboarding-reset-count.json
├── data/
│   ├── boat-log.txt
│   └── historical.db
├── services/
│   ├── onboarding/
│   └── health/
├── scripts/
│   ├── install-*.sh
│   └── configure-*.sh
└── logs/
    ├── onboarding.log
    └── health.log

/var/www/html/
├── index.html (main menu)
├── dashboard.html
├── onboarding.html
├── boatlog.html
├── navigation.html
├── helm.html
└── atmyboat.png
```

### Documentation

- INSTALLATION.md (19KB) - Installation guide
- API_REFERENCE.md (25KB) - API documentation
- CX5106_CONFIGURATION_GUIDE.md (14KB) - CX5106 setup
- CX5106_USER_MANUAL.md (25KB) - CX5106 user manual
- ONBOARDING.md (33KB) - Initial Setup wizard specification
- MASTER_SYSTEM_SPEC.md v2.0 - System specification

### Performance Metrics

- Boot time: 60-90 seconds (first boot with filesystem expansion)
- Boot time: 30-45 seconds (subsequent boots)
- Dashboard update frequency: 1 Hz
- Voice response time: N/A (voice not implemented in v1.0.0)

### Known Issues

1. **Browser Cache**: After HTML updates, users may see old cached pages (Ctrl+Shift+R to refresh)
2. **Node-RED Dashboard 2.0**: Requires ui-theme node, all ui-page nodes must reference theme, all ui-group nodes require showTitle/className/visible/disabled/groupType properties
3. **Touchscreen**: ILITEK ILITEK-TP (USB ID 222a:0001), hid-multitouch driver

---

## Version History Summary

| Version | Release Date | Key Features | Status |
|---------|--------------|--------------|--------|
| **1.0.3** | 2026-02-18 | Installation ID system, tier system, data export, Telegram notifications, GPS fix, voice optimization | Current |
| **1.0.2** | 2026-02-14 | Marine Vision Phase 1 & 2.1, camera streaming, fish detection, weather touch controls | Stable |
| **1.0.1** | 2026-02-13 | Hybrid AI assistant, wake words, Signal K integration, web text interface | Stable |
| **1.0.0** | 2026-02-09 | Initial release, core system, web interface, onboarding wizard, engine monitoring | Stable |

---

## Upgrade Path

- **1.0.0 → 1.0.1**: Standard upgrade (no breaking changes)
- **1.0.1 → 1.0.2**: Standard upgrade (no breaking changes)
- **1.0.2 → 1.0.3**: ⚠️ BREAKING CHANGES (installation ID format, tier system enforced)
- **1.x → 2.x**: Major version upgrade (TBD - expect breaking changes)

See UPGRADE_GUIDE.md for detailed upgrade instructions.

---

## Semantic Versioning

d3kOS follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (1.x → 2.x): Incompatible API changes, breaking changes
- **MINOR** (1.0.x → 1.1.x): New features, backwards-compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backwards-compatible

---

**Document Version**: 1.0.3
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
**Repository**: https://github.com/SkipperDon/d3kOS
