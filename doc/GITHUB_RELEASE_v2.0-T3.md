# d3kOS v2.0-T3 - Testing Build

**Marine Intelligence Operating System for Raspberry Pi**

---

## ⚠️ Pre-Release Notice

This is a **TESTING BUILD** (T3) with Tier 3 features enabled for evaluation. **NOT recommended for production use.**

**Purpose:**
- Testing and validation
- Feature evaluation
- Early adopter feedback
- Development and debugging

---

## 📥 Download

**Image File:** `d3kOS-v2.0-tier3-full.zip`
- **Size:** 9.2 GB (compressed)
- **Download:** [Google Drive](https://drive.google.com/file/d/1pGdv_EGTI4CZ5JDrbiIRJYr09Dz5dvIS/view?usp=sharing)
- **SHA256:** `51f5a3115c24f77b0998d06d7e4b31ca8b54418cb3791531d8e18538e53ec368`

**Verify checksum after download:**
```bash
# Linux/macOS
sha256sum d3kOS-v2.0-tier3-full.zip

# Windows PowerShell
Get-FileHash d3kOS-v2.0-tier3-full.zip -Algorithm SHA256
```

---

## 🚀 What's New

### 🎙️ Emergency Voice Reboot
**Voice-triggered system recovery** when touchscreen fails
- Say "HELM" → "reboot" to restart hands-free
- Industry-standard D-Bus + Polkit implementation
- ~12 second response time
- Commands: "reboot", "restart", "shutdown", "power cycle"

### 📹 Marine Vision System (Phase 1-2.1)
**Camera integration and AI object detection**
- Reolink RLC-810A support (4K, IP67, night vision)
- Live feed: 8 FPS streaming (720p/1080p)
- Video recording + photo capture
- YOLOv8n object detection (person detection working)
- Auto-cleanup after 7 days

### 🔐 Installation ID & License System
**Persistent identification and tier management**
- 16-character hex installation ID (SHA-256 based)
- File-based storage: `/opt/d3kos/config/license.json`
- Auto-tier detection (Tier 2 when OpenCPN installed)
- Feature restrictions by tier
- QR code generation for mobile app pairing

### 📡 Network Management UI
**Touch-optimized WiFi settings**
- WiFi scan and connect
- Password entry via on-screen keyboard
- Real-time status monitoring
- PolicyKit authorization (no sudo required)
- **Note:** Client mode only (no AP/hotspot - hardware limitation)

### 🔧 Self-Healing System
**Automated monitoring and remediation**
- CPU temp, memory, disk space monitoring
- Service health checks (all d3kos services)
- Automatic service restarts
- Temp file cleanup and log rotation
- Real-time status dashboard (port 8099)

### 💾 Data Export & Backup
**Queue-based export with retry logic**
- 3 retry attempts with 5s delay
- Boatlog CSV export
- Automated 36MB compressed backups
- 8 export categories (engine data, boatlog, settings, etc.)

### 🤖 AI & Voice Improvements
**100× faster responses with caching**
- Signal K data cache (3s TTL): 0.17-0.22s response time
- Pattern expansion: 13 instant-answer query types
- Removed slow Phi-2 LLM (60-180s → removed)
- OpenRouter integration for complex queries (6-8s)
- Three wake words: "helm", "advisor", "counsel"

### 🛠️ System Improvements
- Chromium session reset (no more "Restore pages?" prompt)
- Timezone auto-detection (GPS → Internet → UTC)
- Logo update (transparent background)
- Enhanced pattern matching (single-word commands)

---

## 📋 System Requirements

**Hardware:**
- Raspberry Pi 4B (8GB RAM recommended)
- 16GB+ microSD card (32GB+ recommended)
- PiCAN-M HAT or compatible NMEA2000 interface
- 7" touchscreen (1024×600 minimum)
- Anker S330 speakerphone (for Tier 2+ voice features)

**Optional:**
- Reolink RLC-810A camera (Marine Vision)
- GPS/AIS receiver (navigation)

---

## 🔨 Installation

### Quick Start

1. **Download and verify:**
   ```bash
   unzip d3kOS-v2.0-tier3-full.zip
   sha256sum d3kOS-v2.0-tier3-full.img
   ```

2. **Flash to SD card:**
   ```bash
   # Linux/macOS
   sudo dd if=d3kOS-v2.0-tier3-full.img of=/dev/sdX bs=4M status=progress conv=fsync

   # Or use Win32DiskImager (Windows) / Balena Etcher (all platforms)
   ```

3. **Hardware setup:**
   - Insert SD card into Pi 4B
   - Attach PiCAN-M HAT
   - Connect 7" touchscreen
   - Connect NMEA2000 bus (12V, GND, CAN-H, CAN-L)
   - Power on

4. **First boot:**
   - Wait ~60 seconds
   - Default credentials: `d3kos` / `d3kos2026`
   - **Change password:** `passwd`
   - Connect WiFi: Settings → Network Settings

5. **Complete onboarding:**
   - 13-question engine wizard
   - CX5106 DIP switch configuration
   - QR code for mobile pairing
   - Time: 10-20 minutes

---

## ⚠️ Known Issues

### Critical
1. **Voice Service → Touchscreen Conflict**
   - Stopping voice service breaks touchscreen
   - **Mitigation:** Emergency voice reboot ("HELM" → "reboot")
   - Do NOT stop voice service manually

2. **WiFi Hotspot Not Supported**
   - BCM4345/6 firmware error -52 (EOPNOTSUPP)
   - Client mode only (connect to existing WiFi)
   - **Workaround:** Use phone hotspot, Starlink, or marina WiFi

### Medium Priority
3. **Camera Stream:** Use sub-stream (720p/1080p) for stability, not 4K main stream
4. **GPS Drift Indoors:** 3 satellites, position wanders ±10-30m (normal behavior)
5. **Storage Limited:** 11GB used / 15GB total (80% full) - recommend 32GB+ SD card
6. **Boatlog Export:** CSV export button occasionally crashes (use API instead)

---

## 🎯 What's NOT Included Yet

**Marine Vision (Phase 2.2+):**
- ❌ Custom fish detection model (requires training)
- ❌ Species identification
- ❌ Fishing regulations database
- ❌ Telegram/Signal notifications (backend ready, needs config)

**Data Export (Phase 3):**
- ❌ Boot-time export queue processing
- ❌ Daily scheduled exports
- ❌ Cloud sync (Tier 3)

**E-Commerce:**
- ❌ Stripe billing integration
- ❌ Mobile app (iOS/Android)
- ❌ Subscription management

**Charts:**
- ❌ o-charts addon for OpenCPN

---

## 📚 Documentation

**Complete Documentation:**
- **Full Release Notes:** [RELEASE_NOTES_v2.0-T3.md](https://github.com/SkipperDon/d3kOS/blob/main/doc/RELEASE_NOTES_v2.0-T3.md)
- **README:** [README.md](https://github.com/SkipperDon/d3kOS/blob/main/README.md)
- **AI Assistant Guide:** [AI_ASSISTANT_USER_GUIDE.md](https://github.com/SkipperDon/d3kOS/blob/main/doc/AI_ASSISTANT_USER_GUIDE.md)
- **Marine Vision API:** [MARINE_VISION_API.md](https://github.com/SkipperDon/d3kOS/blob/main/doc/MARINE_VISION_API.md)
- **Emergency Reboot:** [SESSION_VOICE_EMERGENCY_REBOOT_COMPLETE.md](https://github.com/SkipperDon/d3kOS/blob/main/doc/SESSION_VOICE_EMERGENCY_REBOOT_COMPLETE.md)

**Quick Reference:**
- **Release Info File:** [d3kOS-v2.0-T3-RELEASE-INFO.txt](https://github.com/SkipperDon/d3kOS/blob/main/d3kOS-v2.0-T3-RELEASE-INFO.txt)
- **System Spec:** [MASTER_SYSTEM_SPEC.md](https://github.com/SkipperDon/d3kOS/blob/main/MASTER_SYSTEM_SPEC.md)

---

## 🧪 Testing Focus Areas

Please test and report feedback on:

1. **Emergency Voice Reboot:** Say "HELM" → "reboot" - does it work reliably?
2. **Voice Assistant:** Test 13 instant-answer queries (RPM, oil, temp, fuel, etc.)
3. **Marine Vision:** Camera feed stability, video recording, object detection
4. **Network Management:** WiFi scan, connect, password entry via touchscreen
5. **Self-Healing:** Trigger alerts (CPU stress), verify auto-remediation
6. **Installation ID:** Check 16-char hex format, QR code scanning

**Report Issues:**
- **GitHub Issues:** https://github.com/SkipperDon/d3kOS/issues
- Include: Installation ID, version, hardware specs, steps to reproduce
- Log output: `journalctl -u <service-name> -n 100`

---

## 🆘 Support

- **GitHub:** https://github.com/SkipperDon/d3kOS
- **Email:** support@atmyboat.com
- **Website:** https://atmyboat.com

---

## 📊 Release Stats

**Development Time:** 40+ sessions over 12 days
**Lines of Code:** 15,000+ (Python, JavaScript, HTML/CSS)
**Services:** 12 microservices
**APIs:** 11 RESTful endpoints
**Documentation:** 50+ markdown files
**Commits:** 120+ since v0.9.1.2

---

## 🙏 Credits

**Developed by:** Skipper Don (donmo) @ AtMyBoat.com
**AI Assistant:** Claude Sonnet 4.5 (Anthropic)
**Testing:** d3kOS Community

**Open Source Components:**
- Debian GNU/Linux 13 (Trixie)
- Signal K Server
- Node-RED
- Vosk (speech recognition)
- Piper (text-to-speech)
- YOLOv8 (object detection)
- OpenCPN (navigation)

---

## 📝 License

**d3kOS Core:** Open Source (See LICENSE)
**Tier 2/3 Features:** Proprietary (subscription required)

See [README.md](https://github.com/SkipperDon/d3kOS/blob/main/README.md) for tier comparison.

---

## 🗓️ Release Timeline

- **v2.0-T3:** February 22, 2026 (This release - Testing)
- **v2.0-RC1:** TBD (Release Candidate)
- **v2.0.0:** TBD (Production Release)

---

**⚠️ TESTING BUILD - Use at your own risk**

This pre-release is for testing purposes only. Features may be unstable, incomplete, or change without notice. Always maintain backups of your data.

---

**Questions?** Open an issue on GitHub or email support@atmyboat.com
