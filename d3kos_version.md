# d3kOS System Applications & Versions

**System:** d3kOS v2.0
**Hardware:** Raspberry Pi 4 Model B (8GB RAM)
**IP Address:** 192.168.1.237
**Last Updated:** 2026-02-11

---

## Installed Applications & Components

| Category | Application/Component | Version | Notes |
|----------|----------------------|---------|-------|
| **System** | Debian GNU/Linux | 13 (trixie) | Operating System |
| | Linux Kernel | 6.12.62+rpt-rpi-v8 | Raspberry Pi optimized |
| | Raspberry Pi | 4 Model B | 8GB RAM |
| **Web & Network** | Nginx | 1.26.3 | Web server |
| | Chromium Browser | 144.0.7559.109 | Kiosk mode UI |
| | Signal K Server | (via Node-RED) | Marine data server |
| **Node.js Stack** | Node.js | v20.20.0 | JavaScript runtime |
| | npm | 10.8.2 | Package manager |
| | Node-RED | v4.1.4 | Flow-based programming |
| | Dashboard 2.0 | @flowfuse/node-red-dashboard v1.30.2 | UI framework |
| **Python** | Python | 3.13.5 | Programming language |
| | pip | 25.1.1 | Python package installer |
| **Voice Assistant** | PocketSphinx | (installed) | Wake word detection |
| | Vosk | (Python library) | Speech-to-text |
| | Piper TTS | 1.2.0 | Text-to-speech |
| **Audio** | ALSA | 1.2.14 | Audio subsystem |
| | aplay/arecord | 1.2.14 | Audio playback/recording |
| **Display** | Wayland (labwc) | 0.9.2 | Window compositor |
| | Xwayland | (included) | X11 compatibility |
| | wtype | (installed) | Wayland keyboard input |
| **Development** | git | 2.47.3 | Version control |
| | curl | 8.14.1 | HTTP client |
| **Marine Data** | NMEA2000 | CAN0 interface | Engine/sensor data |
| | GPS/AIS | Signal K integration | Navigation data |

---

## Custom d3kOS Components

### Web Interface
- **Main Menu:** `/var/www/html/index.html` (20KB) - With AtMyBoat.com logo
- **Engine Dashboard:** `/var/www/html/dashboard.html` (21KB) - Standalone HTML
- **Onboarding Wizard:** `/var/www/html/onboarding.html` (58KB) - With QR code generation
- **Boatlog:** `/var/www/html/boatlog.html` (27KB)
- **Navigation:** `/var/www/html/navigation.html` (28KB)
- **Helm:** `/var/www/html/helm.html` (31KB)
- **Logo:** `/var/www/html/atmyboat.png` (1.5MB) - AtMyBoat.com branding
- **Boot Splash:** `/usr/share/plymouth/themes/pix/splash.png` (1.5MB) - Custom d3kOS splash

### Voice Assistant
- **Script:** `/opt/d3kos/services/voice/voice-assistant-hybrid.py`
- **Service:** `d3kos-voice.service` (disabled by default)
- **Wake Word:** "helm" (threshold: 1e-3)
- **Hybrid AI:** Fast rule-based + Phi-2 LLM for complex queries
- **Status:** ⚠️ Disabled by default (touchscreen conflict)

### Services
- **Chromium Cleanup:** `/etc/systemd/system/chromium-cleanup.service`
- **Fullscreen Toggle:** `/usr/local/bin/toggle-fullscreen.sh`

---

## Service Status

| Service | Status | Port/Access |
|---------|--------|-------------|
| Nginx Web Server | ✅ Running | http://192.168.1.237/ |
| Node-RED | ✅ Running | http://192.168.1.237:1880/ |
| Signal K Server | ✅ Running | http://192.168.1.237:3000/ |
| Voice Assistant | ⚠️ Disabled | Toggle via dashboard |
| Chromium Kiosk | ✅ Auto-start | Fullscreen on boot |

---

## Design System

- **Fonts:** 22-24px base, 24px headings, 48px gauge values
- **Colors:** Black (#000000) background, Green (#00CC00) accents, White (#FFFFFF) text
- **Touch Targets:** 60px minimum button height, 20px scrollbars
- **Navigation:** Top bar with "← Main Menu" button standard on all pages
- **Architecture:** Standalone HTML files (NOT Node-RED Dashboard 2.0)

---

## Network Configuration

- **WebSocket:** `ws://192.168.1.237/signalk/v1/stream`
- **Signal K REST API:** `http://192.168.1.237:3000/signalk/v1/api/`
- **Node-RED Dashboard:** `http://192.168.1.237:1880/dashboard`
- **Nginx Proxy:** Port 80 → Signal K WebSocket bridge (IPv4/IPv6)

---

## Known Issues

### Touchscreen/Voice Conflict (Critical)
- **Status:** Documented, unresolved
- **Issue:** Stopping d3kos-voice service causes ILITEK touchscreen to stop responding
- **Workaround:** Keep voice disabled at boot, avoid turning OFF via dashboard
- **Details:** See `/home/boatiq/.claude/projects/-home-boatiq/memory/touchscreen-voice-conflict.md`

---

## Access Information

- **SSH:** `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- **Web Interface:** http://192.168.1.237/
- **VNC:** RealVNC (mouse pointer works when touchscreen fails)

---

**Document generated:** 2026-02-11
**d3kOS Version:** 2.0
**Build Status:** Deployed and working ✓
