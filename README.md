# d3kOS — AI Marine Intelligence Platform

**An open-source helm operating system for Raspberry Pi**

d3kOS transforms a Raspberry Pi 4 into a professional-grade marine helm system: real-time instrument dashboard, AI-powered vessel assistant, chart navigation, engine monitoring, IP camera system with fish detection, and a full boat log with voice notes — all running locally, no subscription required.

**Version**: v0.9.2.2 — Release Candidate
**Released**: March 23, 2026
**OS**: Debian GNU/Linux 13 (Trixie)
**Status**: Code complete — UAT in progress

---

## Download

**Latest Release: v0.9.2.2 — Release Candidate**

| | |
|---|---|
| **Archive.org page** | https://archive.org/details/d-3k-os-v-0.9.2 |
| **Direct download** | https://archive.org/download/d-3k-os-v-0.9.2/ |
| **Size** | ~28 GB (full Pi disk image) |
| **Format** | `.img.gz` — flash directly with Raspberry Pi Imager |
| **Hardware** | Raspberry Pi 4B, 4GB RAM minimum |

**Flash with Raspberry Pi Imager:**
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Choose OS → Use custom → select the `.img.gz` file
3. Choose Storage → select your SD card (32GB+ recommended)
4. Write

**Note:** Upload in progress — file will be available at the link above once complete.

---

## What is d3kOS?

d3kOS runs on a Raspberry Pi 4 mounted at your helm. It integrates:

- **AvNav** chart plotter (replaces or complements your MFD)
- **HELM** — voice-activated AI assistant powered by Gemini + local RAG
- **Signal K** — NMEA 2000 / 0183 data aggregation hub
- **Marine Vision** — up to 20 IP cameras with YOLOv8 fish detection and Gemini Vision species ID
- **Engine Dashboard** — real-time gauges and alert monitoring
- **Boat Log** — voice-to-text entries, engine auto-capture, CSV/JSON export
- **18-language i18n** framework (UI language selectable in Settings)

**d3kOS is not a standalone chartplotter.** It works alongside your existing MFD and VHF. It adds an AI intelligence layer and centralized monitoring that your MFD does not provide.

**Key characteristics:**
- 100% local operation — all core features work without internet
- Touch-optimized for 1m helm viewing distance (IEC 62288 / ISO 9241-303 compliant fonts)
- Offline-capable: Gemini AI with local RAG fallback
- Open architecture: Flask, Signal K, standard web technologies
- ~$500 hardware cost vs $5,000+ for traditional marine electronics

---

## What's New in v0.9.2.2

See [CHANGELOG.md](CHANGELOG.md) for the full release notes.

**Highlights:**
- Full marine-grade instrument dashboard (Bebas Neue / Chakra Petch design system)
- 8-step onboarding wizard with CX5106 DIP switch auto-configuration
- Helm AI assistant with RAG → Gemini fallback
- Engine Dashboard: 5 sections, full 1280px width, alert states
- Marine Vision: slot/hardware architecture, 1–20 cameras, fish detection + species ID
- Boat Log: voice-to-text (Vosk), engine auto-capture, CSV/JSON export
- Weather: fullscreen Windy embed (no API key required)
- Signal K v2.23.0
- NMEA2000 simulator removed
- User manual ingested into Pi RAG knowledge base

---

## Hardware Requirements

### Core (Required)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| Raspberry Pi 4B | 4GB RAM minimum, 8GB recommended | $55–75 |
| microSD Card | 32GB minimum, Class 10 A2 | $12–20 |
| Touchscreen | 10.1" 1280×800, capacitive touch, HDMI+USB | $80–120 |
| DC-DC Converter | 12V→5V, 5A, galvanic isolation (Victron Orion-Tr) | $35 |
| USB GPS Receiver | Any gpsd-compatible (VK-162 or equivalent) | $15 |

**Total Core System**: ~$350–450

### Optional

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| Anker PowerConf S330 | USB speakerphone for HELM voice assistant | $130 |
| Reolink RLC-810A | 4K IP camera, PoE, night vision (up to 20) | $90/each |
| CX5106 or compatible | NMEA 2000 engine gateway (PiCAN-M also supported) | $120–200 |

### Display

- **Tested**: 10.1" 1280×800, 150 PPI
- **Minimum**: 1024×600 (some layout degradation below 1280px)
- **Brightness**: 1000 nit recommended for sunlight readability
- **Touch**: Capacitive multi-touch (ILITEK controller confirmed working)

---

## Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Debian (Trixie) | GNU/Linux 13 | Base OS |
| Flask | 3.x | Dashboard server (:3000) |
| Signal K Server | 2.23.0 | NMEA 2000/0183 aggregation (:8099) |
| AvNav | 20250822 | Chart navigation (:8080) |
| Node-RED | 3.x | Engine data flows |
| Gemini 2.5 Flash | via API | AI assistant + fish species ID |
| Vosk | small-en-us | Offline speech-to-text (voice notes) |
| Piper | en_US-amy | Offline text-to-speech (HELM responses) |
| ChromaDB | local | RAG vector database (manuals + fish species) |
| YOLOv8n | ONNX | Fish and obstacle detection |
| OpenCPN | 5.12.4 Flatpak | Chart plotter (fallback / o-charts) |
| Chromium | Latest | Kiosk browser (Wayland, `--app` mode) |
| labwc | Latest | Wayland compositor |

---

## Quick Start

### Prerequisites

- Raspberry Pi 4 running Debian 13 (Trixie) with Wayland/labwc
- Signal K Server installed and running on port 8099
- Python 3.13, Node.js 20+, AvNav installed

### Clone and Deploy

```bash
# On your workstation
git clone https://github.com/SkipperDon/d3kOS.git
cd d3kOS

# Deploy to Pi (replace with your Pi IP)
scp -r deployment/d3kOS/dashboard/ d3kos@192.168.1.237:/opt/d3kos/services/
scp -r deployment/d3kOS/services/ d3kos@192.168.1.237:/opt/d3kos/services/
```

See `deployment/` for full deployment scripts and configuration.

### First Boot

1. Power on Pi — wait ~60 seconds
2. Chromium opens at `http://localhost:3000` in kiosk mode
3. First-run: Setup Wizard launches automatically (8 steps)
4. Complete vessel identity, engine type, NMEA gateway config, Gemini API key
5. Dashboard is live

### Services

| Service | Port | Purpose |
|---------|------|---------|
| `d3kos-dashboard` | 3000 | Flask dashboard (main UI) |
| `avnav` | 8080 | Chart navigation |
| `upload_api` | 8081 | Manual upload |
| `history_api` | 8082 | History data |
| `manuals_api` | 8083 | Manual serving |
| `camera` | 8084 | Camera stream manager |
| `fish_detector` | 8086 | YOLOv8 fish detection |
| `keyboard-api` | 8087 | On-screen keyboard control |
| `ai_api` | 8089 | HELM voice AI service |
| `boatlog-export-api` | 8095 | Boat log + voice notes |
| `signalk` | 8099 | Signal K server |
| `language_api` | 8101 | i18n language service |
| `preferences_api` | 8107 | Metric/imperial preferences |
| `remote_api` | 8111 | Remote access API |

---

## Features

### Dashboard

- Instrument rows: ENGINE (RPM, coolant, oil, battery, fuel) + NAV (SOG, COG, position, next waypoint)
- 3-way row toggle: ENGINE / NAV / BOTH
- AvNav chart iframe (full chart plotter integration)
- Day/Night theme — auto-schedule with manual override
- Status bar: internet, AvNav, Gemini AI, Signal K, Ollama
- 6-tab bottom nav: NAV, MARINE VISION, ENGINE, BOAT LOG, MORE + HELM button

### HELM — AI Voice Assistant

- Wake word: "Helm" (Vosk small-en-us, offline)
- TTS: Piper en_US-amy (offline)
- AI: Gemini 2.5 Flash (online) with local RAG fallback
- RAG knowledge base: d3kOS user manual + Ontario fish regulations + vessel manuals
- Software mute toggle (persists across reload)
- Helm Assistant page: 4 quick-action buttons + full chat UI

### Marine Vision — Camera System

- Slot/Hardware architecture: named positions decouple from physical cameras
- Up to 20 IP cameras, RTSP streams
- Focus+filmstrip default view; grid mode available
- Fish detection: YOLOv8n ONNX + EfficientNet-483 classifier
- Fish species ID: Gemini Vision on-demand (common name, scientific name, Ontario regulation note)
- 21 Ontario freshwater species in RAG knowledge base
- Settings: scan, live thumbnails, role assignment (forward watch, active default, fish detection, grid display)

### Engine Dashboard

- 5 sections: Engine, Electrical, Tanks, System Status, Network Status
- Progress bars, alert states (warning/critical), DAY/NGT toggle
- Full 1280px width on Pi display

### Boat Log

- Manual text and voice entries (voice: Vosk offline transcription)
- Engine auto-capture: start event, 30-min snapshots, stop event, alert crossings
- Export: CSV + JSON with unit metadata
- Metric and imperial configurations supported

### Settings (16 Sections)

Vessel identity, units (metric/imperial), display, audio, engine gateway, camera setup, language, Gemini API key, Signal K status, remote access, onboarding wizard, documentation viewer, and more.

### i18n — 18 Languages

All 13 UI pages wired with `data-i18n`. Language selectable in Settings → Language.

Supported: Arabic, Danish, German, Greek, English, Spanish, Finnish, French, Croatian, Italian, Japanese, Dutch, Norwegian, Portuguese, Swedish, Turkish, Ukrainian, Chinese.

---

## Documentation

| Document | Description |
|----------|-------------|
| [CHANGELOG.md](CHANGELOG.md) | Full release notes for all versions |
| [CLAUDE.md](CLAUDE.md) | AI development guidelines and project operating procedures |
| [deployment/docs/D3KOS_USER_MANUAL_v0922.md](deployment/docs/D3KOS_USER_MANUAL_v0922.md) | Full user manual — Setup Wizard, Dashboard, all features, Troubleshooting |
| [deployment/docs/DEPLOYMENT_INDEX.md](deployment/docs/DEPLOYMENT_INDEX.md) | Index of all solution docs, feature dirs, tools |
| [deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md](deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md) | Camera slot/hardware architecture |
| [deployment/docs/FISH_DETECTION_ARCHITECTURE.md](deployment/docs/FISH_DETECTION_ARCHITECTURE.md) | YOLOv8 + Gemini Vision fish detection design |
| [deployment/docs/OPENCPN_FLATPAK_OCHARTS.md](deployment/docs/OPENCPN_FLATPAK_OCHARTS.md) | OpenCPN + o-charts installation guide |
| [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) | Master task list — all versions |

---

## Roadmap

### v0.9.2.2 (Current — Release Candidate)
- [x] Full instrument dashboard
- [x] HELM AI assistant (Gemini + RAG)
- [x] Marine Vision (1–20 cameras, fish detection + species ID)
- [x] Boat Log with voice notes
- [x] Engine Dashboard
- [x] Signal K v2.23.0
- [x] 18-language i18n
- [x] 8-step onboarding wizard
- [ ] UAT (5 metric + 5 imperial users) — in progress

### v0.9.3 — AtMyBoat.com Community Platform
- WordPress + child theme on HostPapa
- bbPress forum at /forum/
- AI assistant widget (Gemini via PHP)
- AODA compliant

### v0.9.4 — d3kOS Mobile Companion App
- PWA on GitHub Pages (no App Store)
- WebRTC/STUN P2P live tunnel (Pi ↔ phone)
- Find My Boat, boat health dashboard
- Fix My Pi diagnostic + restore
- $0 ongoing infrastructure cost

### v1.0
- Multi-language voice (Whisper-small, 18-language Piper)
- Mobile app + signalk-forward-watch public release
- CJK keyboard support

---

## Project Structure

```
d3kOS/
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
├── CLAUDE.md                        # AI development guidelines
├── PROJECT_CHECKLIST.md             # Master task tracker
├── SESSION_LOG.md                   # Development session log
│
├── deployment/
│   ├── docs/                        # Solution documents and specs
│   │   ├── D3KOS_USER_MANUAL_v0922.md
│   │   ├── DEPLOYMENT_INDEX.md
│   │   ├── MARINE_VISION_CAMERA_OVERHAUL.md
│   │   └── ...
│   ├── d3kOS/
│   │   └── dashboard/               # Flask dashboard source
│   │       ├── app.py
│   │       ├── templates/           # Jinja2 HTML templates
│   │       └── static/              # CSS, JS modules
│   └── scripts/                     # Deploy and utility scripts
│
├── deployment/features/             # Feature build checklists
└── deployment/v0.9.3/               # AtMyBoat.com platform files
```

---

## Contributing

Contributions welcome. Please:

1. Fork the repository
2. Read [CLAUDE.md](CLAUDE.md) for development and coding standards
3. Create a feature branch
4. Follow the existing code style (Flask, vanilla JS, no frameworks in dashboard)
5. Add tests where applicable
6. Submit a pull request

**Note:** This project uses the AAO Autonomous Action Operating Methodology. All AI-assisted development follows the standards documented in `CLAUDE.md`.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/SkipperDon/d3kOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SkipperDon/d3kOS/discussions)
- **User Manual**: [D3KOS_USER_MANUAL_v0922.md](deployment/docs/D3KOS_USER_MANUAL_v0922.md)

---

## Acknowledgments

Built on exceptional open-source projects:

- **[Signal K](https://signalk.org/)** — Universal marine data standard
- **[AvNav](https://www.wellenvogel.net/software/avnav/docs/en_index.html)** — Marine chart navigation
- **[OpenCPN](https://opencpn.org/)** — Open-source chartplotter
- **[Vosk](https://alphacephei.com/vosk/)** — Offline speech recognition
- **[Piper](https://github.com/rhasspy/piper)** — Fast neural text-to-speech
- **[YOLOv8](https://github.com/ultralytics/ultralytics)** — Real-time object detection
- **[ChromaDB](https://www.trychroma.com/)** — Local vector database
- **[Node-RED](https://nodered.org/)** — Flow-based automation

---

## Licensing

d3kOS is dual licensed:

**Open Source — GPL v3**
Free to use, modify, and distribute under the GNU General Public License v3.0.
Any derivative works must also be released under GPL v3. See [LICENSE](./LICENSE).

**Commercial License**
Commercial use — including bundling with hardware for resale or distribution
in paid products — requires a separate commercial license agreement.
Contact: skipperdont@atmyboat.com | https://atmyboat.com

---

## Version History

| Version | Date | Status | Summary |
|---------|------|--------|---------|
| v0.9.2.2 | Mar 23, 2026 | **Release Candidate** | Full marine intelligence platform |
| v0.9.2.1 | Mar 13, 2026 | Closed | Flask dashboard architecture, all 6 phases |
| v0.9.2 | Mar 12, 2026 | Closed | Camera overhaul, i18n, Signal K upgrade |
| v0.9.1.2 | Feb 20, 2026 | Closed | Voice assistant, self-healing, data export |

---

*d3kOS v0.9.2.2 — Built by boaters, for boaters. Powered by open source.*
