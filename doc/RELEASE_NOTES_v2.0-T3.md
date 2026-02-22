# d3kOS v2.0-T3 Release Notes

**Version**: 2.0-T3 (Testing/Pre-release)
**Release Date**: February 22, 2026
**Status**: Testing Build - Tier 3 Enabled
**Image Size**: 9.2 GB (compressed)

---

## ⚠️ Pre-Release Notice

This is a **testing build** (T3) with Tier 3 features enabled for evaluation purposes. This release is intended for:
- Testing and validation
- Feature evaluation
- Development and debugging
- Early adopter feedback

**NOT recommended for production use yet.**

---

## Download

**Full Image (Tier 3 Testing):**
- Filename: `d3kOS-v2.0-tier3-full.zip`
- Size: 9.2 GB
- SHA256: `51f5a3115c24f77b0998d06d7e4b31ca8b54418cb3791531d8e18538e53ec368`
- Download: [Google Drive](https://drive.google.com/file/d/1pGdv_EGTI4CZ5JDrbiIRJYr09Dz5dvIS/view?usp=sharing)

**System Requirements:**
- Raspberry Pi 4B (8GB RAM recommended)
- 16GB+ microSD card (32GB+ recommended)
- PiCAN-M HAT or compatible NMEA2000 interface
- 7" touchscreen (1024×600 minimum)
- Anker S330 speakerphone (for voice features)

---

## What's New in v2.0-T3

### Major Features

#### 1. Emergency Voice Reboot ✅
- **Voice-triggered system reboot** for touchscreen recovery
- Industry-standard D-Bus + Polkit implementation
- Say "HELM" → "reboot" to restart system hands-free
- Use case: When touchscreen becomes unresponsive
- Response time: ~12 seconds from wake word to reboot
- **Commands supported:**
  - "reboot"
  - "restart"
  - "shutdown"
  - "reboot system"
  - "power cycle"

#### 2. Voice Assistant Improvements ✅
- **Vosk wake word detection** (100% offline)
- Three wake words: "helm" (auto), "advisor" (onboard), "counsel" (online)
- Single-word command recognition (simplified from multi-word)
- Real-time sensor data integration via Signal K
- ~0.17s response time for simple queries (cached)
- OpenRouter AI integration for complex queries (6-8s)

#### 3. Marine Vision System (Phase 1-2.1) ✅
- **Reolink RLC-810A camera integration** (4K, IP67, night vision)
- Live camera feed at 8 FPS (720p/1080p sub-stream)
- Video recording with VLC backend
- Photo capture (high-resolution JPEG)
- **YOLOv8n object detection** (ONNX Runtime)
- Person detection working (fish detection requires custom model)
- Storage management: Auto-cleanup after 7 days
- API: Port 8084 (camera), 8086 (detection), 8089 (unified)

#### 4. Network Management UI ✅
- **Touch-optimized WiFi settings** page
- WiFi network scan and connect
- Password entry via on-screen keyboard
- Status monitoring with auto-refresh
- PolicyKit authorization (no sudo required)
- API: Port 8101
- **Note:** Built-in WiFi is client-only (no AP/hotspot mode)

#### 5. Self-Healing System ✅
- **Automated issue detection:**
  - CPU temperature monitoring (>75°C alert, >80°C critical)
  - Memory usage tracking (>80% warning, >90% critical)
  - Disk space monitoring (>90% alert, >95% critical)
  - Service health checks (all d3kos services)
- **Auto-remediation:**
  - Automatic service restarts
  - Temp file cleanup
  - Log rotation
- **UI Dashboard:** Real-time status and issue history
- API: Port 8099

#### 6. Data Export & Backup System ✅
- **Export queue with retry logic** (3 attempts, 5s delay)
- Boatlog CSV export (download as spreadsheet)
- Automated backup system (36MB compressed)
- Backup API: Port 8100
- Export categories:
  - Engine benchmark data
  - Boatlog entries
  - Marine vision metadata
  - QR code data
  - Settings configuration
  - System alerts
  - Onboarding configuration

#### 7. Installation ID & License System ✅
- **16-character hex installation ID** (SHA-256 based)
- File-based storage: `/opt/d3kos/config/license.json`
- Tier detection (auto-upgrade to Tier 2 when OpenCPN installed)
- Feature restrictions by tier
- Reset counter tracking
- QR code generation with simplified format
- License API: Port 8091
- Tier API: Port 8093

#### 8. System Improvements ✅
- **Chromium session reset** (prevents "Restore pages?" prompt)
- **Timezone auto-detection** (GPS → Internet → UTC fallback)
- **Logo update:** Transparent background AtMyBoat.com logo
- **AI Assistant caching:** Signal K data cached (3s TTL) for instant responses
- **Pattern matching expansion:** 13 instant-answer query types

---

## System Architecture

### Core Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| nginx | 80 | Web server | ✅ Running |
| Signal K | 3000 | NMEA2000 data hub | ✅ Running |
| Node-RED | 1880 | Dashboard backend | ✅ Running |
| d3kos-voice | - | Voice assistant | ✅ Running |
| d3kos-ai-api | 8080 | AI text interface | ✅ Running |
| d3kos-camera-stream | 8084 | Camera feed | ✅ Running |
| d3kos-fish-detector | 8086 | Object detection | ✅ Running |
| d3kos-license-api | 8091 | License management | ✅ Running |
| d3kos-tier-api | 8093 | Tier detection | ✅ Running |
| d3kos-export-manager | 8094 | Data export | ✅ Running |
| d3kos-self-healing | 8099 | System monitoring | ✅ Running |
| d3kos-backup-api | 8100 | Backup management | ✅ Running |
| d3kos-network-api | 8101 | WiFi management | ✅ Running |

### AI Models

| Model | Size | Purpose | Format |
|-------|------|---------|--------|
| Vosk (small-en-us) | 50MB | Speech-to-text | Offline |
| PocketSphinx | 10MB | Wake word detection | Offline |
| Piper (en_US-amy) | 20MB | Text-to-speech | Offline |
| YOLOv8n | 13MB | Object detection | ONNX |

**Note:** Phi-2 LLM removed (too slow on Pi 4B - 60-180s response time)

---

## Installation

### Quick Start

1. **Download image:**
   - Get `d3kOS-v2.0-tier3-full.zip` from Google Drive
   - Verify SHA256 checksum

2. **Extract and flash:**
   ```bash
   # Extract
   unzip d3kOS-v2.0-tier3-full.zip

   # Flash to SD card (Linux/macOS)
   sudo dd if=d3kOS-v2.0-tier3-full.img of=/dev/sdX bs=4M status=progress conv=fsync

   # Or use Win32DiskImager (Windows)
   # Or Balena Etcher (cross-platform)
   ```

3. **Hardware setup:**
   - Insert SD card into Pi 4B
   - Attach PiCAN-M HAT
   - Connect 7" touchscreen
   - Connect NMEA2000 bus (12V, GND, CAN-H, CAN-L)
   - Power on

4. **First boot:**
   - Wait ~60 seconds for boot
   - Default credentials: `d3kos` / `d3kos2026`
   - Change password: `passwd`
   - Connect WiFi: Settings → Network Settings

5. **Complete onboarding:**
   - 13-question engine wizard
   - CX5106 DIP switch configuration
   - QR code for mobile app pairing
   - Time: 10-20 minutes

---

## What's NOT Included Yet

### Phase 2.2+ Marine Vision Features
- ❌ Custom fish detection model (requires training)
- ❌ Species identification (no pretrained model)
- ❌ Fishing regulations database
- ❌ Telegram/Signal notifications (backend ready, needs config)
- ❌ Forward watch mode (marine object detection)
- ❌ Distance estimation (depth perception)

### Phase 3 Data Export Features
- ❌ Boot-time export queue processing
- ❌ Daily scheduled exports (Tier 2+)
- ❌ Cloud sync (Tier 3)
- ❌ Multi-boat support (Tier 3)

### E-Commerce & Subscriptions
- ❌ Stripe billing integration (40-60 hours development)
- ❌ Apple IAP / Google Play billing
- ❌ Central database backend
- ❌ Mobile app (iOS/Android)
- ❌ Subscription management UI

### Charts & Navigation
- ❌ o-charts addon for OpenCPN
- ❌ S-57/S-63 chart support
- ❌ Route planning integration
- ❌ Waypoint management

---

## Known Issues

### Critical
1. **Voice Service → Touchscreen Conflict**
   - Stopping voice service breaks touchscreen
   - Mitigation: Emergency voice reboot ("HELM" → "reboot")
   - Do NOT stop voice service manually

2. **Built-in WiFi Limitations**
   - BCM4345/6 firmware error -52 (EOPNOTSUPP)
   - Cannot act as WiFi hotspot/AP
   - Client mode only (connect to existing WiFi)
   - Workaround: Use phone hotspot, Starlink, or marina WiFi

### Medium Priority
3. **Camera Stream Stability**
   - 4K main stream causes frame drops
   - Use sub-stream (720p/1080p) for stability
   - Optimized for 8 FPS refresh rate

4. **GPS Drift Indoors**
   - 3 satellites, HDOP 3.57 (weak signal)
   - Position "wanders" ±10-30m
   - Speed shows 0-2 knots when stationary
   - Normal outdoors with 8+ satellites

5. **Storage Space Limited**
   - 11GB used / 15GB total (80% full)
   - Camera recordings auto-delete after 7 days
   - Recommend 32GB+ SD card for production

### Low Priority
6. **Boatlog Export Button**
   - CSV export button occasionally crashes
   - Workaround: Use export API directly
   - Fix pending in next release

7. **Network Status Labels**
   - Some labels not white color
   - Minor cosmetic issue
   - Fix pending

---

## Testing Notes

### What to Test

1. **Emergency Voice Reboot:**
   - Say "HELM" → "reboot"
   - Verify system reboots cleanly
   - Check all services auto-start

2. **Voice Assistant:**
   - Test all 13 instant-answer queries
   - Verify wake word detection reliability
   - Check response times

3. **Marine Vision:**
   - Live camera feed stability
   - Video recording (start/stop)
   - Photo capture
   - Object detection accuracy

4. **Network Management:**
   - WiFi scan
   - Connect to new network
   - Password entry via on-screen keyboard
   - Status display accuracy

5. **Self-Healing System:**
   - Trigger CPU alert (stress test)
   - Verify auto-remediation
   - Check issue history logging

6. **Installation ID:**
   - Verify 16-char hex format
   - Check license.json persistence
   - Test QR code scanning

---

## Upgrade Notes

### From v0.9.x to v2.0-T3

**NOT RECOMMENDED** - Clean install recommended due to major changes:
- New license system (installation ID format changed)
- Voice assistant architecture updated
- Camera system added (new hardware)
- Network management UI added
- Self-healing system added

**To upgrade:**
1. Backup your data (Boatlog, settings)
2. Export onboarding configuration
3. Flash new v2.0-T3 image
4. Re-run onboarding wizard
5. Restore boatlog/settings if needed

---

## Support

### Documentation
- **README.md** - Main documentation
- **MASTER_SYSTEM_SPEC.md** - Complete system specification
- **AI_ASSISTANT_USER_GUIDE.md** - Voice/text AI usage
- **MARINE_VISION_API.md** - Camera system API reference
- **SESSION_VOICE_EMERGENCY_REBOOT_COMPLETE.md** - Emergency reboot guide

### Community
- **GitHub Issues:** Report bugs and request features
- **Email:** support@atmyboat.com
- **Website:** https://atmyboat.com

### Reporting Issues

When reporting issues, include:
1. Installation ID (from Settings)
2. d3kOS version (v2.0-T3)
3. Hardware specs (Pi model, RAM, SD card size)
4. Steps to reproduce
5. Log output: `journalctl -u <service-name> -n 100`

---

## Changelog

### v2.0-T3 (February 22, 2026)

**Major Features:**
- Emergency voice reboot via D-Bus + Polkit
- Marine Vision system (camera integration, object detection)
- Network management UI (WiFi settings)
- Self-healing system (monitoring + auto-remediation)
- Installation ID & license system
- Data export & backup system
- Voice assistant improvements (caching, pattern expansion)

**System Updates:**
- Chromium session reset (no more "Restore pages?" prompt)
- Timezone auto-detection (GPS → Internet → UTC)
- Logo update (transparent background)
- AI response caching (3s TTL, 100× faster)
- Pattern matching expansion (8 → 13 queries)

**Bug Fixes:**
- Fixed voice reboot command execution (D-Bus implementation)
- Fixed cache-busting for logo updates
- Fixed GPS drift display (documented as expected behavior)
- Fixed network API port conflicts

**Security:**
- Replaced NOPASSWD: ALL with fine-grained polkit rules
- Removed Claude SSH credentials from image
- Cleared WiFi passwords from image
- Bash history cleared
- SSH known_hosts cleared

**Performance:**
- AI response: 0.17-0.22s (cached queries, 100× faster)
- Camera stream: 8 FPS stable (optimized from initial issues)
- Voice detection: <500ms wake word, ~6s total response
- Disk usage: 11GB/15GB (80% full, 300-400MB freed via cleanup)

---

## Credits

**Developed by:** Skipper Don (donmo) @ AtMyBoat.com
**AI Assistant:** Claude Sonnet 4.5 (Anthropic)
**Testing:** d3kOS Community

**Open Source Components:**
- Debian GNU/Linux 13 (Trixie)
- Raspberry Pi OS
- Signal K Server
- Node-RED
- Vosk (speech recognition)
- Piper (text-to-speech)
- YOLOv8 (object detection)
- OpenCPN (navigation)

---

## License

**d3kOS Core:** Open Source (See LICENSE)
**d3kOS Tier 2/3 Features:** Proprietary (subscription required)

See README.md for tier comparison and licensing details.

---

**Release Status:** 🟡 Testing/Pre-release (T3)
**Next Release:** v2.0-RC1 (Release Candidate)
**Production Release:** v2.0.0 (TBD)
