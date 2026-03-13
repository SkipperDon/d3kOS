# d3kOS — Claude Code Implementation Plan
**Project:** Helm-OS / d3kOS Marine Dashboard  
**Operator:** Skipper Don / AtMyBoat.com  
**Methodology:** AAO v1.1 | Master AI Engineering Standard  
**File:** `/home/boatiq/Helm-OS/deployment/d3kOS/D3KOS_PLAN.md`  
**Version:** 2.0.0 — Merged, URL-Audited & Phase-Structured  
**Updated:** 2026-03-12

---

## SESSION START — REQUIRED EVERY TIME

Before any tool call, Claude Code **MUST** state aloud:

> "I have read and will adhere to:
> 1. Master AI Engineering, Coding, and Testing Standard
> 2. Standard Test Case Creation Template
> 3. AI Engineering & Automated Testing Specification Template
> 4. AI Engineering Specification & Solution Design Template
> 5. AAO Autonomous Action Operating Methodology (v1.1)
>
> All work this session follows these standards."

Then read **in this order** before any implementation:

1. `/home/boatiq/CLAUDE.md` — governing rules (non-negotiable, every session)
2. This file — determine current phase and task state
3. `PROJECT_CHECKLIST.md` — exact done/pending task state
4. `SESSION_LOG.md` — last 3 entries for continuity context

**Do not begin implementation until all four files are read.**

---

## PHASE STATUS TRACKER

Update this table at the **start of every session**.

| Phase | Name | Status | Est. Sessions |
|---|---|---|---|
| 0 | Initial Setup & Directory Structure | ⬜ TODO | 0.5 |
| 1 | Pi Menu Restructure | ⬜ TODO | 1 |
| 2 | Dashboard Hub (Flask :3000) | 🔶 IN PROGRESS 2026-03-13 | 2 |
| 3 | Gemini Marine AI Proxy (:3001) | ⬜ TODO | 2–3 |
| 4 | Settings Page + Documentation | ⬜ TODO | 1–2 |
| 5 | AI + AvNav Integration | ⬜ TODO | 3–4 |

> ⬜ TODO → 🔄 IN PROGRESS → ✅ DONE

---

## MASTER URL & PORT REFERENCE

> **This table is the single source of truth for all URLs and ports.**  
> Every code file, template, config, and `.env` in this project must match exactly.  
> If a port differs from what is found on the Pi, stop and report before proceeding.

| Service | URL / Address | Protocol | Notes |
|---|---|---|---|
| **d3kOS Dashboard** | `http://localhost:3000` | HTTP | Flask app — Phase 2 |
| **d3kOS Settings** | `http://localhost:3000/settings` | HTTP | Served by same Flask app |
| **AvNav Charts** | `http://localhost:8080` | HTTP | Primary chart viewer |
| **Gemini AI Proxy** | `http://localhost:3001` | HTTP | Flask proxy — Phase 3 |
| **Signal K Server** | `http://localhost:8099` | HTTP | Read only — do NOT modify |
| **Signal K WebSocket** | `ws://localhost:8099/signalk/v1/stream` | WS | ⚠️ Port 8099, NOT 3000 |
| **OpenPlotter UI** | `http://localhost:8081` | HTTP | Infrastructure — do NOT touch |
| **Ollama (LAN)** | `http://192.168.1.36:11434` | HTTP | Offline AI fallback |
| **Ollama tags** | `http://192.168.1.36:11434/api/tags` | HTTP | Health check endpoint |
| **Ollama generate** | `http://192.168.1.36:11434/api/generate` | HTTP | Query endpoint |
| **Gemini API** | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={KEY}` | HTTPS | Current model: `gemini-2.5-flash` |
| **Gemini AI Studio** | `https://aistudio.google.com` | HTTPS | Where Don gets API key |
| **Internet check** | `http://captive.apple.com` | HTTP | Lightweight connectivity probe |
| **Windy embed** | `https://embed.windy.com/embed2.html` | HTTPS | Sea state weather panel |
| **Radar embed** | `https://www.rainviewer.com/map.html` | HTTPS | Weather radar panel |
| **d3kOS AI Bridge** | `http://localhost:3002` | HTTP | Phase 5 — AI+AvNav integration service |
| **AvNav REST API** | `http://localhost:8080/viewer/avnav_navi.php` | HTTP POST | Phase 5 — POST only, GET returns 501 |

### Known Bugs Fixed in This Plan

| # | Location | Bug | Fix Applied |
|---|---|---|---|
| 1 | `settings.html` line 1357 | `ws://localhost:3000/signalk/v1/stream` — port 3000 is the dashboard, not Signal K | Changed to `ws://localhost:8099/signalk/v1/stream` |
| 2 | `gemini_proxy.py` | `GEMINI_MODEL = 'gemini-1.5-flash'` — outdated model | Changed to `gemini-2.5-flash` |
| 3 | Phase 5 spec v1.0.0 P5.0 | All AvNav pre-action curl commands used GET to `/api/...` — returns HTTP 501 | Fixed in v1.1.0: use POST to `/viewer/avnav_navi.php` |
| 4 | Phase 5 spec v1.0.0 config | `AVNAV_API=http://localhost:8080/api` — wrong URL and method | Fixed in v1.1.0: `http://localhost:8080/viewer/avnav_navi.php` (POST) |

---

## PROJECT OVERVIEW

Restructure Helm-OS on the Raspberry Pi from an OpenCPN-centric layout to a  
**web-first, AI-assisted marine dashboard** branded as **d3kOS**.

### Core Principles

- OpenCPN stays installed — **fallback only**, zero code changes, menu entry only
- AvNav (`http://localhost:8080`) is the primary chart viewer
- Gemini AI Proxy (`http://localhost:3001`) replaces static Navigation menus
- Everything degrades gracefully when offline — no hard failures
- OpenPlotter runs silently at `http://localhost:8081` — hidden from all Pi menus
- Ollama (`http://192.168.1.36:11434`) is tried **before** any paid Gemini API call
- No API keys in any committed file — `.env` files only, always in `.gitignore`
- Never store user query text — token counts and timestamps only

---

## DIRECTORY STRUCTURE

Create this entire tree at Phase 0 before any other work begins.

```
/home/boatiq/Helm-OS/deployment/d3kOS/
├── D3KOS_PLAN.md                    ← this file — keep updated each session
├── PROJECT_CHECKLIST.md             ← task tracking — update every session
├── SESSION_LOG.md                   ← append-only — never delete entries
├── CHANGELOG.md                     ← milestone entries only
├── .gitignore                       ← must exist before first commit
│
├── pi-menu/
│   ├── BACKUP/                      ← originals captured before any edit
│   │   └── BACKUP_LOG.txt           ← timestamped backup record
│   ├── d3kOS.menu                   ← Phase 1
│   ├── navigation.menu              ← Phase 1
│   └── charts.menu                  ← Phase 1
│
├── dashboard/                       ← Phase 2 — Flask app at :3000
│   ├── app.py
│   ├── templates/
│   │   ├── index.html               ← main dashboard
│   │   ├── settings.html            ← Phase 4 — full settings page
│   │   └── offline.html             ← shown when AvNav unreachable
│   ├── static/
│   │   ├── css/d3kos.css
│   │   ├── js/panel-toggle.js
│   │   └── js/connectivity-check.js
│   └── config/
│       └── d3kos-config.env         ← NEVER commit — in .gitignore
│
├── gemini-nav/                      ← Phase 3 — AI proxy at :3001
│   ├── gemini_proxy.py
│   ├── cache/                       ← response_cache.json (auto-created)
│   ├── templates/
│   │   └── chat.html
│   ├── config/
│   │   └── gemini.env               ← NEVER commit — in .gitignore
│   └── tests/
│       └── test_gemini_proxy.py
│
├── ai-bridge/                       ← Phase 5 — AI Bridge at :3002
│   ├── ai_bridge.py
│   ├── features/
│   │   ├── route_analyzer.py        ← Feature 1: route widget
│   │   ├── port_arrival.py          ← Feature 2: arrival briefing
│   │   ├── voyage_logger.py         ← Feature 3: log summarization
│   │   └── anchor_watch.py          ← Feature 4: anchor alerts
│   ├── utils/
│   │   ├── signalk_client.py        ← WebSocket reader for ws://localhost:8099
│   │   ├── avnav_client.py          ← POST client for avnav_navi.php
│   │   ├── tts.py                   ← TTS wrapper (espeak-ng / piper)
│   │   └── geo.py                   ← haversine, bearing, unit conversions
│   ├── config/
│   │   └── ai-bridge.env            ← NEVER commit — covered by **/*.env gitignore
│   └── tests/
│       └── test_ai_bridge.py
│
└── docs/
    ├── MENU_STRUCTURE.md            ← Phase 1: before/after + rollback
    ├── AVNAV_OCHARTS_INSTALL.md     ← Phase 4
    ├── AVNAV_PLUGINS.md             ← Phase 4
    ├── OPENPLOTTER_REFERENCE.md     ← Phase 4
    ├── AVNAV_INSTALL_AND_API.md     ← Phase 5 pre-req: AvNav install + API reference
    ├── D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md  ← Phase 5 full spec (v1.1.0)
    └── AVNAV_API_REFERENCE.md       ← Phase 5 pre-req: real API responses from live Pi (create in P5.0)
```

---

## GOVERNANCE FILES — MANDATORY EVERY SESSION

Claude Code **must** update all of these at session end. No exceptions.

| File | Action | Location |
|---|---|---|
| `SESSION_LOG.md` | Append: date, goal, completed, decisions, pending | `d3kOS/` |
| `PROJECT_CHECKLIST.md` | Mark completed tasks ✅, add discovered tasks | `d3kOS/` |
| `DEPLOYMENT_INDEX.md` | Add every new file: path, description, version | `Helm-OS/deployment/docs/` |
| `CHANGELOG.md` | Entry only if a phase milestone is reached | `Helm-OS/` |
| `MEMORY.md` | Add stable patterns, corrections, key facts | `/home/boatiq/.claude/projects/` |

---

## HARD RULES — NEVER VIOLATE

1. **Never push to GitHub** — local commits only, always
2. **Never touch OpenPlotter config** — `http://localhost:8081` is read-only infrastructure
3. **Never modify AvNav core files** — config and plugin directories only
4. **Never commit `.env` files** — verify `.gitignore` before every `git commit`
5. **OpenCPN is frozen** — Pi menu entry only, zero code changes ever
6. **Windy / Gemini / Radar require internet** — every feature must degrade gracefully offline
7. **Ollama first** (`http://192.168.1.36:11434`) before any Gemini API call
8. **Never store user query text** — token counts and timestamps only in cache
9. **Backup before any menu file edit** — BACKUP directory must exist and be written first
10. **Signal K is port 8099** — never use port 3000 for Signal K references (3000 = dashboard)

---

## ROLLBACK PROCEDURES

### Rollback Phase 1 (Menu)
```bash
cp /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/*.desktop \
   /home/boatiq/.local/share/applications/
rm -f /home/boatiq/.config/menus/applications-merged/d3kOS.menu
lxpanelctl restart
```

### Rollback Phase 2 (Dashboard)
```bash
sudo systemctl stop    d3kos-dashboard
sudo systemctl disable d3kos-dashboard
sudo rm -f /etc/systemd/system/d3kos-dashboard.service
sudo systemctl daemon-reload
```

### Rollback Phase 3 (Gemini Proxy)
```bash
sudo systemctl stop    d3kos-gemini
sudo systemctl disable d3kos-gemini
sudo rm -f /etc/systemd/system/d3kos-gemini.service
sudo systemctl daemon-reload
```

### Rollback Phase 5 (AI Bridge)
```bash
sudo systemctl stop    d3kos-ai-bridge
sudo systemctl disable d3kos-ai-bridge
sudo rm -f /etc/systemd/system/d3kos-ai-bridge.service
sudo systemctl daemon-reload
# Dashboard reverts to Phase 4 state — SSE connection to :3002 fails silently
```

---

---

# PHASE 0 — Initial Setup & Directory Structure

**Risk Level:** NONE  
**Reversible:** YES  
**Internet Required:** NO  
**Estimated Sessions:** 0.5 (first half of Phase 1 session)  
**Depends on:** Nothing — always runs first

### Objective
Create all directories, `.gitignore`, and governance file stubs before any other work.

---

### 0.1 — Create Directory Tree

```bash
cd /home/boatiq/Helm-OS/deployment/d3kOS

mkdir -p pi-menu/BACKUP
mkdir -p dashboard/templates
mkdir -p dashboard/static/css
mkdir -p dashboard/static/js
mkdir -p dashboard/config
mkdir -p gemini-nav/templates
mkdir -p gemini-nav/cache
mkdir -p gemini-nav/config
mkdir -p gemini-nav/tests
mkdir -p docs

echo "Directories created: $(date)" >> pi-menu/BACKUP/BACKUP_LOG.txt
echo "All directories OK"
```

---

### 0.2 — Create .gitignore

Create `/home/boatiq/Helm-OS/deployment/d3kOS/.gitignore`:

```gitignore
# Secret config files — NEVER commit these
dashboard/config/d3kos-config.env
gemini-nav/config/gemini.env
ai-bridge/config/ai-bridge.env
**/*.env
.env

# Python cache
**/__pycache__/
*.pyc
*.pyo

# AI response cache — contains server data
gemini-nav/cache/
```

Verify after creating:
```bash
git -C /home/boatiq/Helm-OS check-ignore -v \
  deployment/d3kOS/dashboard/config/d3kos-config.env \
  deployment/d3kOS/gemini-nav/config/gemini.env
# Both lines must print — if not, fix .gitignore before continuing
```

---

### 0.3 — Create Governance File Stubs

```bash
# SESSION_LOG.md
cat > /home/boatiq/Helm-OS/deployment/d3kOS/SESSION_LOG.md << 'EOF'
# d3kOS Session Log
Append-only. Never delete entries. Format: date, goal, completed, decisions, pending.

---
EOF

# PROJECT_CHECKLIST.md
cat > /home/boatiq/Helm-OS/deployment/d3kOS/PROJECT_CHECKLIST.md << 'EOF'
# d3kOS Project Checklist

## Phase 0 — Initial Setup
- [ ] Directory tree created
- [ ] .gitignore in place and verified
- [ ] Governance file stubs created

## Phase 1 — Pi Menu Restructure
- [ ] BACKUP directory populated with originals
- [ ] d3kOS menu category created
- [ ] d3kOS Dashboard desktop entry created (localhost:3000)
- [ ] OpenCPN Fallback desktop entry created
- [ ] AvNav Charts entry created (localhost:8080)
- [ ] Gemini Marine Assistant entry created (localhost:3001)
- [ ] OpenCPN removed from standard Navigation menu
- [ ] MENU_STRUCTURE.md written
- [ ] All .desktop files pass desktop-file-validate
- [ ] SESSION_LOG.md updated

## Phase 2 — Dashboard Hub
- [ ] Flask installed and importable
- [ ] Port 3000 confirmed free
- [ ] app.py created and runs without error
- [ ] Dashboard loads at http://localhost:3000
- [ ] AvNav iframe loads (http://localhost:8080)
- [ ] Weather panel opens/closes
- [ ] Windy loads when online (https://embed.windy.com)
- [ ] Radar loads when online (https://www.rainviewer.com)
- [ ] Offline notice shown when internet down
- [ ] Status indicators update every 30s
- [ ] Systemd service d3kos-dashboard enabled and starts on boot
- [ ] d3kos-config.env NOT in git (verified)
- [ ] SESSION_LOG.md updated

## Phase 3 — Gemini AI Proxy

> **Decision 2026-03-12 — Option B: Retire old proxy, replace with :3001**
> The existing `d3kos-gemini-proxy.service` at port :8097 will be retired once Phase 3 is tested
> and stable. After Phase 3 is verified: (1) stop and disable `d3kos-gemini-proxy.service`,
> (2) update `voice-assistant-hybrid.py` and `query_handler.py` to call `http://localhost:3001/ask`
> instead of `http://localhost:8097/ask`, (3) remove the old service file from Pi.
> This consolidates all AI proxy calls through the new :3001 Flask proxy.

- [ ] Ollama reachable at http://192.168.1.36:11434
- [ ] Port 3001 confirmed free
- [ ] gemini_proxy.py created
- [ ] /ask returns Gemini response when online
- [ ] /ask falls back to Ollama when offline
- [ ] Source badge shows correct source
- [ ] Cache never exceeds 10 entries
- [ ] Query text NOT in cache (manually verified)
- [ ] All pytest tests pass
- [ ] gemini.env NOT in git (verified)
- [ ] Systemd service d3kos-gemini enabled and starts on boot
- [ ] SESSION_LOG.md updated

## Phase 4 — Settings Page + Docs
- [ ] /settings route added to app.py
- [ ] settings.html deployed at localhost:3000/settings
- [ ] Signal K WebSocket check uses port 8099 (NOT 3000)
- [ ] System status live indicators working
- [ ] AVNAV_OCHARTS_INSTALL.md written
- [ ] AVNAV_PLUGINS.md written
- [ ] OPENPLOTTER_REFERENCE.md written
- [ ] All doc links functional
- [ ] SESSION_LOG.md updated
EOF

echo "Governance stubs created"
```

---

### Phase 0 — Definition of Done

- [ ] All directories exist: `find . -type d | sort`
- [ ] `.gitignore` verified — both `.env` files are ignored
- [ ] `SESSION_LOG.md`, `PROJECT_CHECKLIST.md` stubs exist
- [ ] `BACKUP_LOG.txt` exists with timestamp

---

---

# PHASE 1 — Pi Menu Restructure

**Risk Level:** LOW  
**Reversible:** YES — backup first, every time  
**Internet Required:** NO  
**Estimated Sessions:** 1  
**Depends on:** Phase 0 complete

### Objective
Create the `d3kOS` Pi menu category. Reorganize all menu entries. Move OpenCPN  
to fallback-only. Add AvNav (`http://localhost:8080`) and Gemini Nav (`http://localhost:3001`)  
as proper Pi menu entries.

---

### 1.1 — Pre-Actions (MANDATORY BEFORE ANY FILE EDIT)

```bash
# Confirm menu file locations on this Pi build
find /etc/xdg/menus /usr/share/applications /home/boatiq/.local/share/applications \
  -name "*.menu" -o -name "*.desktop" 2>/dev/null | sort

# Confirm AvNav is installed and on port 8080
systemctl status avnav 2>/dev/null || echo "avnav not running as service"
curl -s --max-time 5 http://localhost:8080 | head -5
# Expected: HTML response from AvNav

# Confirm Signal K is on port 8099
curl -s --max-time 5 http://localhost:8099/signalk | head -5
# Expected: JSON with version info

# Confirm OpenPlotter on 8081 (do not touch)
curl -s --max-time 5 http://localhost:8081 | head -3

# Confirm port 3000 is free (our dashboard)
ss -tlnp | grep :3000 && echo "⚠️ PORT 3000 IN USE — STOP AND REPORT" || echo "✓ Port 3000 free"

# Confirm port 3001 is free (our Gemini proxy)
ss -tlnp | grep :3001 && echo "⚠️ PORT 3001 IN USE — STOP AND REPORT" || echo "✓ Port 3001 free"
```

**Stop and report to Don before proceeding if:**
- AvNav is NOT responding on port 8080
- Signal K is NOT on port 8099
- Port 3000 or 3001 is already in use
- Menu files are not in expected locations

---

### 1.2 — Backup Current Menu Files

```bash
# Backup directory must already exist (Phase 0)
ls /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/BACKUP_LOG.txt \
  || { echo "BACKUP_LOG.txt missing — run Phase 0 first"; exit 1; }

# Copy all current .menu and .desktop files
cp -v /etc/xdg/menus/*.menu \
  /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/ 2>/dev/null

# Backup OpenCPN desktop entry
find /usr/share/applications /home/boatiq/.local/share/applications \
  -name "*opencpn*" -exec cp -v {} \
  /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/ \;

# Record backup timestamp
echo "Backup captured: $(date)" >> \
  /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/BACKUP_LOG.txt

echo "Backup complete. Contents:"
ls -la /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/
```

---

### 1.3 — Create d3kOS Dashboard Desktop Entry

Create `/home/boatiq/.local/share/applications/d3kos-dashboard.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=d3kOS Dashboard
Comment=Marine Navigation Dashboard — http://localhost:3000
Exec=chromium-browser --app=http://localhost:3000 --start-fullscreen
Icon=applications-internet
Categories=d3kOS;
Terminal=false
```

---

### 1.4 — Create OpenCPN Fallback Entry

Create `/home/boatiq/.local/share/applications/d3kos-opencpn.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=OpenCPN (Fallback)
Comment=Traditional Chart Plotter — Emergency Use Only
Exec=opencpn
Icon=opencpn
Categories=d3kOS;
Terminal=false
```

---

### 1.5 — Create AvNav Charts Entry

Create `/home/boatiq/.local/share/applications/d3kos-avnav.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=AvNav Charts
Comment=Web-based Chart Viewer — http://localhost:8080
Exec=chromium-browser --app=http://localhost:8080 --start-maximized
Icon=applications-internet
Categories=d3kOS;Charts;
Terminal=false
```

---

### 1.6 — Create Gemini Marine Assistant Entry

Create `/home/boatiq/.local/share/applications/d3kos-gemini-nav.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Gemini Marine Assistant
Comment=AI Navigation Assistant — http://localhost:3001
Exec=chromium-browser --app=http://localhost:3001 --start-maximized
Icon=applications-internet
Categories=d3kOS;Navigation;
Terminal=false
```

---

### 1.7 — Register d3kOS as Pi Menu Category

Create `/home/boatiq/.config/menus/applications-merged/d3kOS.menu`:

```xml
<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
  "http://www.freedesktop.org/standards/menu-spec/menu-1.0.dtd">
<Menu>
  <Name>Applications</Name>
  <Menu>
    <Name>d3kOS</Name>
    <Directory>d3kOS.directory</Directory>
    <Include>
      <Category>d3kOS</Category>
    </Include>
  </Menu>
</Menu>
```

Create `/home/boatiq/.local/share/desktop-directories/d3kOS.directory`:

```ini
[Desktop Entry]
Version=1.0
Type=Directory
Name=d3kOS
Comment=Marine Navigation Dashboard System
Icon=applications-internet
```

---

### 1.8 — Hide OpenCPN from Standard Navigation Menu

```bash
# Find current OpenCPN system desktop entry
find /usr/share/applications /home/boatiq/.local/share/applications \
  -name "*opencpn*" 2>/dev/null

# Override with local copy — change Categories only, do NOT delete system file
mkdir -p /home/boatiq/.local/share/applications
cp /usr/share/applications/opencpn.desktop \
   /home/boatiq/.local/share/applications/opencpn.desktop
```

Edit `/home/boatiq/.local/share/applications/opencpn.desktop` — change **only** the Categories line:
```ini
Categories=d3kOS;
```
This removes OpenCPN from Navigation/Science while keeping it accessible in d3kOS.

---

### 1.9 — Write Menu Structure Documentation

Create `/home/boatiq/Helm-OS/deployment/d3kOS/docs/MENU_STRUCTURE.md`:

```markdown
# d3kOS Menu Structure
**Date:** [DATE]  
**Version:** 1.0  

## Before (Original Pi Menu)
- Navigation → OpenCPN
- Charts → (none or OpenCPN)

## After (d3kOS v2.0)
- d3kOS →
  - d3kOS Dashboard → http://localhost:3000 (Chromium fullscreen)
  - OpenCPN (Fallback) → opencpn binary
- Navigation →
  - Gemini Marine Assistant → http://localhost:3001
- Charts →
  - AvNav Charts → http://localhost:8080

## Infrastructure (hidden from all menus)
- OpenPlotter: http://localhost:8081 — GPS, AIS, NMEA, Signal K
- Signal K: http://localhost:8099 — data broker

## Rollback Instructions
```bash
cp /home/boatiq/Helm-OS/deployment/d3kOS/pi-menu/BACKUP/*.desktop \
   /home/boatiq/.local/share/applications/
rm -f /home/boatiq/.config/menus/applications-merged/d3kOS.menu
lxpanelctl restart
```
```

---

### 1.10 — Refresh Menu and Verify

```bash
# Refresh LXDE/Pi menu
lxpanelctl restart 2>/dev/null || (killall lxpanel && lxpanel &)

# Validate all d3kOS desktop files
for f in /home/boatiq/.local/share/applications/d3kos-*.desktop; do
  echo "--- $f ---"
  desktop-file-validate "$f" && echo "✓ OK" || echo "✗ VALIDATION ERROR"
done
```

**Manual verify:** Right-click Pi desktop → confirm d3kOS menu appears with correct entries.

---

### Phase 1 — Definition of Done

- [ ] BACKUP directory contains all original menu/desktop files with timestamp
- [ ] d3kOS menu category visible in Pi menu
- [ ] d3kOS Dashboard entry present → opens `http://localhost:3000` in Chromium
- [ ] OpenCPN Fallback entry present in d3kOS menu
- [ ] AvNav Charts entry present → opens `http://localhost:8080`
- [ ] Gemini Marine Assistant entry present → opens `http://localhost:3001`
- [ ] OpenCPN removed from standard Navigation menu
- [ ] MENU_STRUCTURE.md written with before/after and rollback
- [ ] All `.desktop` files pass `desktop-file-validate`
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated

---

---

# PHASE 2 — d3kOS Dashboard Hub

**Risk Level:** MEDIUM  
**Reversible:** YES — stop systemd service, remove files  
**Internet Required:** For Windy/Radar panels only  
**Estimated Sessions:** 2  
**Depends on:** Phase 1 complete

### Objective
Flask app at `http://localhost:3000`. Split-pane: AvNav iframe (`http://localhost:8080`)  
on the left, collapsible Windy/Radar weather panel on the right. Bottom nav bar.  
Live status indicators polling `/status` every 30 seconds.

---

### 2.1 — Pre-Actions

```bash
# Confirm Python 3 and pip
python3 --version   # need 3.9+
pip3 --version

# Confirm Flask available or installable
python3 -c "import flask; print('Flask', flask.__version__)" 2>/dev/null \
  || echo "Flask not installed — will install"

# Confirm port 3000 free
ss -tlnp | grep :3000 && echo "⚠️ PORT IN USE — STOP" || echo "✓ Port 3000 free"

# Check RAM — Flask + AvNav + Chromium must coexist
free -h
# Need at least 500MB free RAM
```

---

### 2.2 — Install Dependencies

```bash
pip3 install flask python-dotenv requests --break-system-packages

# Verify
python3 -c "import flask, dotenv, requests; print('✓ All deps OK')"
```

---

### 2.3 — Create Config File

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/config/d3kos-config.env`:

```env
# d3kOS Dashboard Configuration
# DO NOT COMMIT — verified in .gitignore
AVNAV_PORT=8080
GEMINI_PORT=3001
SIGNALK_PORT=8099
DASHBOARD_PORT=3000
VESSEL_NAME=Your Vessel Name
HOME_PORT=Your Home Port
```

Verify it is gitignored before continuing:
```bash
git -C /home/boatiq/Helm-OS check-ignore -v \
  deployment/d3kOS/dashboard/config/d3kos-config.env
# Must print the file path — if silent, fix .gitignore immediately
```

---

### 2.4 — Create Flask App

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/app.py`:

```python
"""
d3kOS Dashboard Server
Serves the main marine navigation hub at http://localhost:3000

Port assignments (from d3kos-config.env):
  Dashboard:   localhost:3000  (this app)
  AvNav:       localhost:8080
  Gemini Proxy: localhost:3001
  Signal K:    localhost:8099
  OpenPlotter: localhost:8081  (read-only, not referenced here)
"""
from flask import Flask, render_template, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'config', 'd3kos-config.env'))

app = Flask(__name__)

AVNAV_PORT    = os.getenv('AVNAV_PORT',    '8080')
GEMINI_PORT   = os.getenv('GEMINI_PORT',   '3001')
SIGNALK_PORT  = os.getenv('SIGNALK_PORT',  '8099')
VESSEL_NAME   = os.getenv('VESSEL_NAME',   'Vessel')
HOME_PORT_VAL = os.getenv('HOME_PORT',     'Home Port')


def check_internet() -> bool:
    """Lightweight connectivity check — no data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except requests.RequestException:
        return False


def check_service(port: str) -> bool:
    """Check if a local service is responding on given port."""
    try:
        requests.get(f'http://localhost:{port}', timeout=2)
        return True
    except requests.RequestException:
        return False


@app.route('/')
def index():
    return render_template('index.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        vessel_name=VESSEL_NAME,
    )


@app.route('/status')
def status():
    """
    Live system status endpoint — polled by frontend every 30s.
    Checks: internet, AvNav (:8080), Gemini proxy (:3001), Signal K (:8099)
    """
    return jsonify({
        'internet': check_internet(),
        'avnav':    check_service(AVNAV_PORT),    # localhost:8080
        'gemini':   check_service(GEMINI_PORT),   # localhost:3001
        'signalk':  check_service(SIGNALK_PORT),  # localhost:8099
    })


@app.route('/settings')
def settings():
    """Settings & Help page — Phase 4."""
    return render_template('settings.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        signalk_port=SIGNALK_PORT,
        vessel_name=VESSEL_NAME,
        home_port=HOME_PORT_VAL,
    )


@app.route('/offline')
def offline():
    return render_template('offline.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
```

---

### 2.5 — Create Dashboard HTML

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>d3kOS — Marine Dashboard</title>
  <link rel="stylesheet" href="/static/css/d3kos.css">
</head>
<body>

  <!-- STATUS BAR -->
  <div id="status-bar">
    <span class="brand">⚓ d3kOS — {{ vessel_name }}</span>
    <span id="indicator-internet" class="indicator" title="Internet">🌐</span>
    <span id="indicator-avnav"    class="indicator" title="AvNav :8080">🗺️</span>
    <span id="indicator-gemini"   class="indicator" title="AI Proxy :3001">🤖</span>
    <span id="indicator-signalk"  class="indicator" title="Signal K :8099">📡</span>
    <span id="clock"></span>
  </div>

  <!-- MAIN CONTENT -->
  <div id="main-area">

    <!-- LEFT: AvNav Chart Viewer — localhost:8080 -->
    <div id="chart-pane">
      <iframe
        id="avnav-frame"
        src="http://localhost:{{ avnav_port }}"
        title="AvNav Chart Viewer — localhost:{{ avnav_port }}"
        allowfullscreen>
      </iframe>
    </div>

    <!-- RIGHT: Collapsible Weather Panel (requires internet) -->
    <div id="weather-panel" class="panel-closed">
      <div id="panel-tabs">
        <button onclick="showPanel('windy')" class="tab-btn" id="tab-windy">🌊 Sea State</button>
        <button onclick="showPanel('radar')" class="tab-btn" id="tab-radar">🌧 Radar</button>
        <button onclick="closePanel()"       class="tab-btn" id="tab-close">✕</button>
      </div>
      <div id="panel-content">
        <div id="offline-notice" style="display:none">
          ⚠️ Internet required for weather panels
        </div>
        <!-- Lazy-loaded when first opened -->
        <iframe id="windy-frame" src="" title="Windy Sea State" style="display:none"></iframe>
        <iframe id="radar-frame" src="" title="Weather Radar"   style="display:none"></iframe>
      </div>
    </div>

  </div>

  <!-- BOTTOM NAV BAR -->
  <nav id="bottom-bar">
    <a href="http://localhost:{{ gemini_port }}" target="_blank" class="nav-btn">
      🤖 AI Nav
    </a>
    <a href="http://localhost:{{ avnav_port }}" target="_blank" class="nav-btn">
      🗺️ AvNav
    </a>
    <button onclick="togglePanel()" class="nav-btn">
      🌤 Weather
    </button>
    <a href="/settings" class="nav-btn">
      ⚙️ Settings
    </a>
    <a href="#" onclick="launchOpenCPN()" class="nav-btn nav-fallback">
      OpenCPN ↗
    </a>
  </nav>

  <script src="/static/js/connectivity-check.js"></script>
  <script src="/static/js/panel-toggle.js"></script>
  <script>
    function launchOpenCPN() {
      fetch('/launch/opencpn').catch(() => {});
    }
  </script>
</body>
</html>
```

---

### 2.6 — Create CSS

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/static/css/d3kos.css`:

```css
/* d3kOS Marine Dashboard — Dark nautical theme */
:root {
  --navy:    #0a1628;
  --ocean:   #1a3a5c;
  --accent:  #00CC00;
  --warn:    #FFA500;
  --success: #00CC00;
  --danger:  #FF3333;
  --text:    #FFFFFF;
  --bar-h:   48px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--navy);
  color: var(--text);
  font-family: 'Roboto', 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* STATUS BAR */
#status-bar {
  height: var(--bar-h);
  background: var(--ocean);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 14px;
  border-bottom: 2px solid var(--accent);
  flex-shrink: 0;
}
.brand { font-weight: 700; color: var(--accent); font-size: 1rem; }
.indicator { font-size: 1.1rem; opacity: 0.3; transition: opacity 0.3s; }
.indicator.active { opacity: 1; }
.indicator.error  { filter: grayscale(1) brightness(0.4); }
#clock { margin-left: auto; font-size: 0.9rem; color: var(--accent); font-family: monospace; }

/* MAIN AREA */
#main-area { display: flex; flex: 1; overflow: hidden; }

/* CHART PANE — AvNav */
#chart-pane { flex: 1; position: relative; }
#avnav-frame { width: 100%; height: 100%; border: none; }

/* WEATHER PANEL */
#weather-panel {
  width: 0; overflow: hidden;
  transition: width 0.3s ease;
  background: var(--ocean);
  display: flex; flex-direction: column;
  border-left: 2px solid var(--accent);
}
#weather-panel.panel-open   { width: 380px; }
#weather-panel.panel-closed { width: 0; }

#panel-tabs {
  display: flex; gap: 4px; padding: 8px;
  background: var(--navy); flex-shrink: 0;
}
.tab-btn {
  flex: 1; padding: 8px 4px;
  background: var(--ocean); color: var(--text);
  border: 1px solid var(--accent); border-radius: 4px;
  cursor: pointer; font-size: 0.8rem;
}
.tab-btn:hover, .tab-btn.active { background: var(--accent); color: var(--navy); }

#panel-content { flex: 1; position: relative; }
#panel-content iframe { width: 100%; height: 100%; border: none; }
#offline-notice { padding: 20px; color: var(--warn); text-align: center; font-size: 1rem; }

/* BOTTOM BAR */
#bottom-bar {
  height: var(--bar-h);
  background: var(--ocean);
  display: flex; align-items: center;
  padding: 0 10px; gap: 8px;
  border-top: 2px solid var(--accent);
  flex-shrink: 0;
}
.nav-btn {
  padding: 8px 16px;
  background: var(--navy); color: var(--text);
  border: 1px solid var(--accent); border-radius: 4px;
  text-decoration: none; font-size: 0.85rem;
  cursor: pointer; white-space: nowrap;
}
.nav-btn:hover { background: var(--accent); color: var(--navy); }
.nav-fallback  { border-color: var(--warn); color: var(--warn); margin-left: auto; }
.nav-fallback:hover { background: var(--warn); color: var(--navy); }
```

---

### 2.7 — Create JavaScript: connectivity-check.js

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/static/js/connectivity-check.js`:

```javascript
/**
 * connectivity-check.js
 * Polls /status every 30s and updates indicator icons.
 *
 * Status endpoint checks:
 *   internet  — http://captive.apple.com
 *   avnav     — http://localhost:8080
 *   gemini    — http://localhost:3001
 *   signalk   — http://localhost:8099
 */

const POLL_INTERVAL = 30000;

function updateIndicators(status) {
  const map = {
    'indicator-internet': status.internet,
    'indicator-avnav':    status.avnav,
    'indicator-gemini':   status.gemini,
    'indicator-signalk':  status.signalk,
  };
  for (const [id, alive] of Object.entries(map)) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.classList.toggle('active', alive);
    el.classList.toggle('error',  !alive);
    el.title = `${el.title.split(':')[0]}: ${alive ? 'Online' : 'Offline'}`;
  }
  // Expose internet state for panel-toggle.js
  window.d3kOnline = status.internet;
}

async function pollStatus() {
  try {
    const res  = await fetch('/status');
    const data = await res.json();
    updateIndicators(data);
  } catch {
    updateIndicators({ internet: false, avnav: false, gemini: false, signalk: false });
  }
}

function updateClock() {
  const el = document.getElementById('clock');
  if (el) el.textContent = new Date().toLocaleTimeString();
}

setInterval(pollStatus, POLL_INTERVAL);
setInterval(updateClock, 1000);
pollStatus();   // immediate first call
updateClock();
```

---

### 2.8 — Create JavaScript: panel-toggle.js

Create `/home/boatiq/Helm-OS/deployment/d3kOS/dashboard/static/js/panel-toggle.js`:

```javascript
/**
 * panel-toggle.js
 * Controls the collapsible Windy / Radar side panel.
 *
 * External URLs used:
 *   Windy:    https://embed.windy.com/embed2.html  (requires internet)
 *   Radar:    https://www.rainviewer.com/map.html   (requires internet)
 *
 * Coordinates default to Toronto area (43.7, -79.4).
 * Update lat/lon in d3kos-config.env — Phase 4 will wire these dynamically.
 */

const WINDY_URL =
  'https://embed.windy.com/embed2.html?lat=43.7&lon=-79.4' +
  '&zoom=5&level=surface&overlay=waves&menu=&message=&marker=' +
  '&calendar=now&pressure=&type=map&location=coordinates' +
  '&detail=&detailLat=43.7&detailLon=-79.4' +
  '&metricWind=kts&metricTemp=%C2%B0C&radarRange=-1';

const RADAR_URL =
  'https://www.rainviewer.com/map.html?loc=43.7,-79.4,6' +
  '&oFa=0&oC=1&oU=0&oCS=1&oF=0&oAP=0&rmt=4&animate=1' +
  '&snow=1&sm=1&sn=0&c=3';

let panelOpen = false;
let activeTab = null;

function openPanel() {
  document.getElementById('weather-panel')
    .classList.replace('panel-closed', 'panel-open');
  panelOpen = true;
}

function closePanel() {
  document.getElementById('weather-panel')
    .classList.replace('panel-open', 'panel-closed');
  panelOpen = false;
  activeTab = null;
  setActiveTab(null);
}

function togglePanel() {
  panelOpen ? closePanel() : showPanel('windy');
}

function showPanel(type) {
  const windyFrame = document.getElementById('windy-frame');
  const radarFrame = document.getElementById('radar-frame');

  if (!window.d3kOnline) {
    document.getElementById('offline-notice').style.display = 'block';
    windyFrame.style.display = 'none';
    radarFrame.style.display = 'none';
    openPanel();
    return;
  }

  document.getElementById('offline-notice').style.display = 'none';

  if (type === 'windy') {
    if (!windyFrame.src || windyFrame.src === window.location.href)
      windyFrame.src = WINDY_URL;           // lazy load on first open
    windyFrame.style.display = 'block';
    radarFrame.style.display  = 'none';
  } else if (type === 'radar') {
    if (!radarFrame.src || radarFrame.src === window.location.href)
      radarFrame.src = RADAR_URL;           // lazy load on first open
    radarFrame.style.display = 'block';
    windyFrame.style.display  = 'none';
  }

  openPanel();
  setActiveTab(type);
}

function setActiveTab(type) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  if (type === 'windy') document.getElementById('tab-windy').classList.add('active');
  if (type === 'radar') document.getElementById('tab-radar').classList.add('active');
}
```

---

### 2.9 — Create Systemd Service

Create `/etc/systemd/system/d3kos-dashboard.service`:

```ini
[Unit]
Description=d3kOS Marine Dashboard — localhost:3000
After=network.target avnav.service
Wants=avnav.service

[Service]
Type=simple
User=boatiq
WorkingDirectory=/home/boatiq/Helm-OS/deployment/d3kOS/dashboard
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-dashboard
sudo systemctl start  d3kos-dashboard

# Verify
sudo systemctl status d3kos-dashboard
curl -s http://localhost:3000 | head -10
```

---

### Phase 2 — Definition of Done

- [ ] `python3 app.py` runs without error
- [ ] Dashboard loads at `http://localhost:3000`
- [ ] AvNav iframe loads (`http://localhost:8080`)
- [ ] Weather panel opens and closes
- [ ] Windy loads from `https://embed.windy.com` when internet available
- [ ] Radar loads from `https://www.rainviewer.com` when internet available
- [ ] Offline notice appears when internet down (`sudo ip route del default` to test)
- [ ] All 4 status indicators update correctly (internet, AvNav, Gemini, Signal K)
- [ ] Clock displays and ticks in status bar
- [ ] Systemd service `d3kos-dashboard` starts on boot
- [ ] `d3kos-config.env` NOT tracked: `git status` must not show it
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated

---

---

# PHASE 3 — Gemini Marine AI Proxy

**Risk Level:** MEDIUM-HIGH  
**Reversible:** YES — stop systemd service  
**Internet Required:** YES (Gemini) / NO (Ollama fallback)  
**Estimated Sessions:** 2–3  
**Depends on:** Phase 2 complete

### Objective
Flask proxy at `http://localhost:3001`. Routes marine queries to Gemini API  
(`https://generativelanguage.googleapis.com`) when online, or Ollama  
(`http://192.168.1.36:11434`) when offline. Marine-locked system prompt.  
Response cache stores last 10 entries — **response text and metadata only, never query text**.

---

### 3.1 — Pre-Actions

```bash
# Confirm Ollama reachable at correct address
curl -s --max-time 5 http://192.168.1.36:11434/api/tags \
  | python3 -m json.tool | head -20
# Must return JSON with models list

# List available Ollama models
curl -s http://192.168.1.36:11434/api/tags \
  | python3 -c "import sys,json; [print(m['name']) \
    for m in json.load(sys.stdin)['models']]"

# Confirm Gemini API key exists (show first 8 chars only — NEVER print full key)
grep GEMINI_API_KEY /home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav/config/gemini.env \
  | cut -c1-28
# Should show: GEMINI_API_KEY=AIzaSy...

# Confirm port 3001 free
ss -tlnp | grep :3001 && echo "⚠️ PORT IN USE — STOP" || echo "✓ Port 3001 free"
```

**Stop if Ollama is unreachable** — report to Don. Gemini-only is a fallback, not the primary path.

---

### 3.2 — Create Gemini Config File

Create `/home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav/config/gemini.env`:

```env
# Gemini Marine AI Proxy Configuration
# DO NOT COMMIT — verified in .gitignore
GEMINI_API_KEY=your_key_here_from_aistudio.google.com
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_URL=http://192.168.1.36:11434
OLLAMA_MODEL=mistral
VESSEL_NAME=Your Vessel Name
HOME_PORT=Your Home Port
```

**Get API key at:** `https://aistudio.google.com` → Get API key → Create API key  
Key starts with `AIzaSy…` — free tier is sufficient.

Verify gitignored:
```bash
git -C /home/boatiq/Helm-OS check-ignore -v \
  deployment/d3kOS/gemini-nav/config/gemini.env
# Must print the path — if silent, fix .gitignore
```

---

### 3.3 — Create Gemini Proxy

Create `/home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav/gemini_proxy.py`:

```python
"""
d3kOS Gemini Marine AI Proxy — localhost:3001
Routes marine queries to:
  1. Gemini API (https://generativelanguage.googleapis.com) — when online
  2. Ollama (http://192.168.1.36:11434)                    — offline fallback

Privacy rules (from CLAUDE.md):
  - Never store user query text
  - Cache stores: timestamp, source, token count, response text only
  - Cache max: 10 entries (CACHE_MAX)
"""
from flask import Flask, request, jsonify, render_template
import requests
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / 'config' / 'gemini.env')

app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL   = os.getenv('GEMINI_MODEL',   'gemini-2.5-flash')
OLLAMA_URL     = os.getenv('OLLAMA_URL',     'http://192.168.1.36:11434')
OLLAMA_MODEL   = os.getenv('OLLAMA_MODEL',   'mistral')
VESSEL_NAME    = os.getenv('VESSEL_NAME',    'Your Vessel')
HOME_PORT      = os.getenv('HOME_PORT',      'Home Port')

CACHE_FILE = Path(__file__).parent / 'cache' / 'response_cache.json'
CACHE_MAX  = 10

SYSTEM_PROMPT = (
    f"You are a marine navigation assistant for a vessel named {VESSEL_NAME}, "
    f"home port {HOME_PORT}. You help with:\n"
    "- Port information: facilities, depth, fuel docks, customs, entry procedures\n"
    "- Destination planning: waypoints, anchorages, marina contacts, provisioning\n"
    "- Passage safety: weather windows, tidal timing, hazards\n"
    "- Local knowledge: points of interest, fuel prices, marine services\n"
    "- Emergency contacts: coast guard, tow services, medical\n\n"
    "Respond concisely and practically — this is used at sea.\n"
    "Politely refuse if a query is not marine-related.\n"
    "Always note if information may be outdated and should be verified on official charts."
)


def load_cache() -> list:
    try:
        if CACHE_FILE.exists():
            return json.loads(CACHE_FILE.read_text())
    except Exception:
        pass
    return []


def save_cache(entries: list) -> None:
    """Save last CACHE_MAX entries — never store query text."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(entries[-CACHE_MAX:], indent=2))


def check_internet() -> bool:
    """Lightweight check — no user data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except Exception:
        return False


def check_ollama() -> bool:
    """Confirm Ollama at http://192.168.1.36:11434 is responding."""
    try:
        r = requests.get(f'{OLLAMA_URL}/api/tags', timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def query_gemini(user_message: str) -> dict:
    """
    Send query to Gemini API.
    Endpoint: https://generativelanguage.googleapis.com/v1beta/models/
              gemini-2.5-flash:generateContent?key={KEY}
    Returns: {text, tokens, source}
    """
    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'
    )
    payload = {
        'contents': [{'parts': [{'text': user_message}]}],
        'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'generationConfig': {'maxOutputTokens': 800}
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data   = r.json()
    text   = data['candidates'][0]['content']['parts'][0]['text']
    tokens = data.get('usageMetadata', {}).get('totalTokenCount', 0)
    return {'text': text, 'tokens': tokens, 'source': 'gemini'}


def query_ollama(user_message: str) -> dict:
    """
    Send query to Ollama at http://192.168.1.36:11434/api/generate.
    Returns: {text, tokens, source}
    """
    url = f'{OLLAMA_URL}/api/generate'
    payload = {
        'model':  OLLAMA_MODEL,
        'prompt': f'{SYSTEM_PROMPT}\n\nUser: {user_message}\nAssistant:',
        'stream': False,
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return {
        'text':   data.get('response', ''),
        'tokens': data.get('eval_count', 0),
        'source': 'ollama'
    }


@app.route('/')
def chat_ui():
    return render_template('chat.html', vessel=VESSEL_NAME)


@app.route('/status')
def status():
    """Health check — used by dashboard connectivity-check.js."""
    return jsonify({
        'online':  check_internet(),
        'ollama':  check_ollama(),
        'gemini_key': bool(GEMINI_API_KEY),
        'model':   GEMINI_MODEL,
    })


@app.route('/ask', methods=['POST'])
def ask():
    """
    Handle a marine query.
    Route: Gemini (online + key) → Ollama (http://192.168.1.36:11434) → 503
    Log: token counts only — NEVER log query text (CLAUDE.md rule).
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    result = None
    error  = None

    if check_internet() and GEMINI_API_KEY:
        try:
            result = query_gemini(user_message)
        except Exception as e:
            error = f'Gemini error: {e}'

    if result is None and check_ollama():
        try:
            result = query_ollama(user_message)
        except Exception as e:
            error = f'Ollama error: {e}'

    if result is None:
        return jsonify({
            'error':  'No AI service available. Check internet or Ollama at 192.168.1.36:11434.',
            'detail': error
        }), 503

    # Cache: response text + metadata ONLY — never query text
    cache = load_cache()
    cache.append({
        'timestamp': int(time.time()),
        'source':    result['source'],
        'tokens':    result['tokens'],
        'response':  result['text'],
    })
    save_cache(cache)

    return jsonify({
        'response': result['text'],
        'source':   result['source'],
        'tokens':   result['tokens'],
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=False)
```

---

### 3.4 — Create Systemd Service

Create `/etc/systemd/system/d3kos-gemini.service`:

```ini
[Unit]
Description=d3kOS Gemini Marine AI Proxy — localhost:3001
After=network.target d3kos-dashboard.service

[Service]
Type=simple
User=boatiq
WorkingDirectory=/home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav
ExecStart=/usr/bin/python3 gemini_proxy.py
Restart=on-failure
RestartSec=5
EnvironmentFile=/home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav/config/gemini.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-gemini
sudo systemctl start  d3kos-gemini
sudo systemctl status d3kos-gemini
```

---

### 3.5 — Create Test Suite

Create `/home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav/tests/test_gemini_proxy.py`:

```python
"""
Test suite for d3kOS Gemini Marine AI Proxy
Run: cd gemini-nav && pytest tests/test_gemini_proxy.py -v
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import gemini_proxy as gp


@pytest.fixture
def client():
    gp.app.config['TESTING'] = True
    with gp.app.test_client() as c:
        yield c


def test_status_endpoint(client):
    """Status endpoint returns 200 with expected keys."""
    res = client.get('/status')
    assert res.status_code == 200
    data = res.get_json()
    assert 'online'     in data
    assert 'ollama'     in data
    assert 'gemini_key' in data
    assert 'model'      in data


def test_ask_empty_message(client):
    """Empty message string returns 400."""
    res = client.post('/ask', json={'message': ''})
    assert res.status_code == 400


def test_ask_missing_message(client):
    """Missing message key returns 400."""
    res = client.post('/ask', json={})
    assert res.status_code == 400


def test_cache_load_empty():
    """Cache load on non-existent file returns empty list."""
    import tempfile
    gp.CACHE_FILE = Path(tempfile.mktemp(suffix='.json'))
    result = gp.load_cache()
    assert result == []


def test_cache_save_and_load(tmp_path):
    """Cache round-trip: save then load returns identical data."""
    gp.CACHE_FILE = tmp_path / 'test_cache.json'
    entries = [{'timestamp': 1, 'source': 'test', 'tokens': 10, 'response': 'ok'}]
    gp.save_cache(entries)
    loaded = gp.load_cache()
    assert loaded == entries


def test_cache_max_enforced(tmp_path):
    """Cache never exceeds CACHE_MAX (10) entries."""
    gp.CACHE_FILE = tmp_path / 'cache.json'
    entries = [
        {'timestamp': i, 'source': 'test', 'tokens': i, 'response': f'r{i}'}
        for i in range(20)
    ]
    gp.save_cache(entries)
    loaded = gp.load_cache()
    assert len(loaded) <= gp.CACHE_MAX


def test_cache_contains_no_query_text(tmp_path):
    """Cache entries must not contain a 'query' or 'message' field."""
    gp.CACHE_FILE = tmp_path / 'cache.json'
    entry = {'timestamp': 1, 'source': 'gemini', 'tokens': 50, 'response': 'Port info here.'}
    gp.save_cache([entry])
    loaded = gp.load_cache()
    for item in loaded:
        assert 'query'   not in item, "Query text must never be stored"
        assert 'message' not in item, "User message must never be stored"
```

Run tests:
```bash
cd /home/boatiq/Helm-OS/deployment/d3kOS/gemini-nav
pytest tests/test_gemini_proxy.py -v
# All tests must pass before Phase 3 is marked complete
```

---

### Phase 3 — Definition of Done

- [ ] All pytest tests pass: `pytest tests/test_gemini_proxy.py -v`
- [ ] `/ask` returns Gemini response (`source: gemini`) when internet is on
- [ ] `/ask` returns Ollama response (`source: ollama`) when internet is off
- [ ] Source badge in chat UI shows correct source label
- [ ] Typing indicator appears while request is in-flight
- [ ] Cache file (`response_cache.json`) grows correctly — never exceeds 10 entries
- [ ] Query text is NOT in cache — manually open `gemini-nav/cache/response_cache.json` and verify
- [ ] `gemini.env` NOT tracked by git: `git status` must not show it
- [ ] Systemd service `d3kos-gemini` starts on boot
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated

---

---

# PHASE 4 — Settings Page + AvNav Documentation

**Risk Level:** LOW  
**Reversible:** YES  
**Internet Required:** NO  
**Estimated Sessions:** 1–2  
**Depends on:** Phase 2 complete (Phase 3 recommended but not required)

### Objective
Deploy the full Settings & Help page at `http://localhost:3000/settings`.  
Write all AvNav, o-charts, and OpenPlotter documentation files.  
The settings page is the combined live settings page with bookmark navigation sidebar.

> ⚠️ **Critical fix applied in this phase:**  
> The Signal K WebSocket health check MUST use `ws://localhost:8099`  
> NOT `ws://localhost:3000` (which is the dashboard, not Signal K).

---

### 4.1 — Add Settings Route

This was already added to `app.py` in Phase 2 (section 2.4). Confirm the route exists:

```bash
grep -n "def settings" \
  /home/boatiq/Helm-OS/deployment/d3kOS/dashboard/app.py
# Must print the function definition
```

---

### 4.2 — Settings Page Signal K Check (CORRECTED)

In `settings.html`, the Signal K WebSocket health check **must** use port **8099**:

```javascript
// CORRECT — Signal K is on port 8099
function checkSignalK() {
  try {
    const ws = new WebSocket('ws://localhost:8099/signalk/v1/stream?subscribe=none');
    ws.onopen = () => {
      signalKConnected = true;
      document.getElementById('sk-status-dot').textContent  = '● LIVE';
      document.getElementById('sk-status-dot').style.color  = 'var(--color-accent)';
      ws.close();
    };
    ws.onerror = () => {
      signalKConnected = false;
      document.getElementById('sk-status-dot').textContent = '● OFFLINE';
      document.getElementById('sk-status-dot').style.color = 'var(--color-critical)';
    };
  } catch (e) {
    signalKConnected = false;
  }
}
```

**Do NOT use `ws://localhost:3000`** — that is the d3kOS dashboard Flask app.

---

### 4.3 — Settings Page Sections (in order)

The settings page served at `http://localhost:3000/settings` must contain all of these sections, with a fixed right-side bookmark navigation bar that scrolls to each:

| # | Section | Content |
|---|---|---|
| ① | 📡 System Status | Live indicators: AvNav (:8080), Signal K (:8099), GPS, AIS, Gemini (:3001), Ollama (192.168.1.36:11434), OpenPlotter (:8081), Internet |
| ② | ⚓ Engine Configuration | Service interval, oil change interval, engine hours, hours since service |
| ③ | 📏 Units & Display | Distance, speed, temperature, pressure dropdowns + metric/imperial toggle |
| ④ | 🔔 Alerts & Notifications | Service due, overheat, low oil, battery voltage toggles |
| ⑤ | 🤖 AI Assistant | Vessel name, home port, Gemini model selector, AI routing mode, Gemini API key field, privacy toggles, system prompt preview |
| ⑥ | 📹 Camera Setup | Slot/hardware panel (existing camera system) |
| ⑦ | 💾 Data Management | Export, import, clear trip data, clear benchmark data |
| ⑧ | 🌐 Network & Connectivity | Port table + Ollama address + Windy/Radar toggles |
| ⑨ | 🗺️ Chart Setup & Docs | Doc buttons: o-charts install, AvNav plugins, free charts, how to use AvNav |
| ⑩ | 🔌 OpenPlotter & Infrastructure | Doc buttons: OpenPlotter reference, plugins guide, OpenCPN fallback guide |
| ⑪ | 🚀 Getting Started | Daily use steps + emergency procedures |
| ⑫ | 🗓️ Phase Roadmap | All 5 phases with status |
| ⑬ | 🔧 System Actions | Restart Signal K, restart Node-RED, reboot, factory reset |
| ⑭ | 💻 System Information | d3kOS version, Pi model, OS, Signal K status, IP, disk, memory, CPU temp, uptime |
| ⑮ | 🎫 License & Tier | Tier display, installation ID, features |
| ⑯ | ℹ️ About d3kOS | Version, platform, project, credits |

---

### 4.4 — Write Documentation Files

**File:** `docs/AVNAV_OCHARTS_INSTALL.md`

Content must include:
- How to access AvNav at `http://localhost:8080`
- Installing the ochartsng plugin in AvNav
- Activating your o-charts license (account at `https://www.o-charts.org`)
- Downloading chart sets (Canada CHS, UK, US Coast Guard, Australia)
- AvNav chart directory: `/home/boatiq/charts/`
- Note: OpenCPN and AvNav use the same o-charts account but require separate device activations

**File:** `docs/AVNAV_PLUGINS.md`

Content must include:
- AIS overlay plugin (feeds from OpenPlotter/Signal K at `localhost:8099`)
- Anchor alarm plugin — set radius, activate from toolbar
- NMEA data display — reads from Signal K at `ws://localhost:8099/signalk/v1/stream`
- Voyage log — GPX export path and how to download
- SignalK integration plugin — connects AvNav to `http://localhost:8099`

**File:** `docs/OPENPLOTTER_REFERENCE.md`

Content must include:
- OpenPlotter is infrastructure — access at `http://localhost:8081`
- What it manages: GPS, AIS, NMEA 0183 routing, Signal K server
- Signal K server URL: `http://localhost:8099` (data browser: `http://localhost:8099/signalk`)
- Why OpenPlotter is hidden from the d3kOS Pi menu
- Plugin list: NMEA 0183, Signal K, AIS, pypilot (optional), IMU (optional)
- Troubleshooting: no GPS → check NMEA plugin; no AIS → check AIS plugin; Signal K down → `sudo systemctl restart signalk`

---

### Phase 4 — Definition of Done

- [ ] Settings page loads at `http://localhost:3000/settings`
- [ ] All sections present and scrollable
- [ ] Bookmark sidebar scrolls to correct section on tap
- [ ] Signal K WebSocket check uses `ws://localhost:8099` — **not 3000**
- [ ] System status shows live state from `/status` endpoint
- [ ] Gemini API key field saves to `gemini.env` (not committed)
- [ ] All 3 documentation files written with accurate port references
- [ ] o-charts doc references `http://localhost:8080` (AvNav), not OpenCPN
- [ ] OpenPlotter doc references `http://localhost:8081` and Signal K at `:8099`
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated

---

---

# PHASE 5 — AI + AvNav Integration

**Risk Level:** MEDIUM-HIGH
**Reversible:** YES — Phase 5 is fully additive; rollback stops AI Bridge only
**Internet Required:** NO (Ollama fallback required for offline operation)
**Estimated Sessions:** 3–4
**Depends on:** Phase 4 complete + AvNav installed + AVNAV_API_REFERENCE.md exists

**Full spec:** `docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` (v1.1.0)
**AvNav install guide:** `docs/AVNAV_INSTALL_AND_API.md`

---

### Phase 5 Architecture Summary

New service `d3kos-ai-bridge` at **localhost:3002**. Reads Signal K + AvNav, calls Gemini
proxy (:3001) for all AI, streams results to dashboard side panel via SSE and Pi speakers via TTS.

```
Signal K :8099 ──WS──┐
AvNav :8080 ──POST───┼──► AI Bridge :3002 ──► Gemini Proxy :3001 ──► Gemini/Ollama
Node-RED ──Webhook───┘         │
                               ├── SSE → Dashboard :3000
                               └── TTS → Pi speakers
```

### Features Built in Phase 5

| Feature | Trigger | AI Source | Audio |
|---|---|---|---|
| Route Analysis Widget | Every 5 min (auto) + "Analyze Now" tap | :3001 → Gemini/Ollama | No |
| Port Arrival Briefing | 2nm from destination waypoint | :3001 → Gemini/Ollama | Yes — Stage 1 summary |
| Voyage Log Summary | AvNav track stops OR on-demand | :3001 → Gemini/Ollama | No |
| Anchor Watch Alerts | Signal K drag > maxRadius × 3 polls | Pre-written (no AI wait) + advisory | Yes — repeated alarm |

### CRITICAL: Phase 5 Pre-Actions (Complete Before Coding)

All 8 Stages in `docs/AVNAV_INSTALL_AND_API.md` must be DONE first:

| Stage | What | Gate Item |
|---|---|---|
| A | Pre-install checks | Ports 8080, 8082, 8085, Signal K port confirmed |
| B | Install AvNav via OpenPlotter GUI | Service active, port 8080 listening |
| C | Verify installation | All verification script items pass |
| D | Find data directory | AVNAV_DATA_DIR known and recorded |
| E | Verify API and file access | POST API returns gps.lat; currentLeg.json found |
| F | Final gate check | All 9 F-items checked before any Phase 5 code |
| P5.0 | AvNav API exploration | `docs/AVNAV_API_REFERENCE.md` created with real responses |
| P5.1–P5.4 | SK audit, Node-RED audit, TTS, port check | All documented in SESSION_LOG.md |

### CRITICAL: AvNav API Rules (Do Not Get Wrong)

> **API uses POST, not GET.** GET returns HTTP 501.
> **Base URL:** `http://localhost:8080/viewer/avnav_navi.php`
> **NOT:** `http://localhost:8080/api` (this URL does not exist)

All `avnav_client.py` code must use `requests.post()`. See Section 4 of `AVNAV_INSTALL_AND_API.md`.

### Port 8085 Conflict — Must Resolve Before AvNav Install

`d3kos-keyboard-api.service` runs on port 8085. AvNav updater also wants port 8085.
**Resolution required:** Move keyboard-api to port 8086 before installing AvNav.
Steps: update `keyboard-api.py` (PORT=8086) + nginx proxy_pass + service EnvironmentFile
→ reload nginx, restart `d3kos-keyboard-api.service`, verify toggle still works.

### Phase 5 — Definition of Done

See `docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` for the full 27-item definition of done.

Key non-negotiables:
- [ ] AvNav API reference doc exists (`docs/AVNAV_API_REFERENCE.md`) with real Pi responses
- [ ] Port 8085 conflict resolved before AvNav install
- [ ] All API calls in code use POST to `/viewer/avnav_navi.php`
- [ ] Anchor watch: alarm fires from pre-written text — never waits for AI
- [ ] Full offline test passes with Ollama at 192.168.1.36:11434
- [ ] Phase 2 `/status` endpoint updated to include AI Bridge :3002
- [ ] `ai-bridge.env` NOT in git
- [ ] All pytest tests pass including `test_avnav_client_uses_post`
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated

---

*Auto-loaded by Claude Code. Version 2.0.0 → updated 2026-03-13 with Phase 5 (was DEFERRED, now active). All URLs and ports verified 2026-03-12/13.*
