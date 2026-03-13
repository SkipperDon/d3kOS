# AvNav Installation & API Reference
**Project:** Helm-OS / d3kOS Marine Dashboard
**Document:** `docs/AVNAV_INSTALL_AND_API.md`
**Version:** 1.0.0
**Created:** 2026-03-13
**Status:** READY TO EXECUTE — complete before Phase 5 begins

---

## ⚠️ CRITICAL WARNINGS — READ BEFORE TOUCHING ANYTHING

**WARNING 1 — Wrong installer will break OpenPlotter:**
Do NOT download or install `avnav-raspi_xxx.deb` directly.
That standalone package conflicts with OpenPlotter's network configuration.
**The only safe installation path on this Pi is through OpenPlotter Settings → AvNav Installer.**

**WARNING 2 — Signal K port must be verified before Phase 5:**
OpenPlotter default Signal K port is **3000**.
This Pi has Signal K on **8099** — someone changed it at some point.
Run the verification command in Section 2 before any Phase 5 code references that port.
If it has moved, every URL in D3KOS_PLAN.md and D3KOS_PHASE5 must be updated.

**WARNING 3 — AvNav API uses POST, not GET:**
Confirmed from live test on this Pi — `GET` returns HTTP 501.
All API calls in Phase 5 code must use `curl -X POST` or `requests.post()`.

**WARNING 4 — Port 8085 conflict: RESOLVED 2026-03-13**
AvNav updater process uses port **8085**.
`d3kos-keyboard-api.service` moved to port **8087** (8086 was taken by fish_detector). Port 8085 is now free.
Pi deploy required before AvNav install — Session 1 deploys updated keyboard-api.py and nginx.

---

## MASTER SEQUENCE — COMPLETE THIS IN ORDER BEFORE PHASE 5

Every step below must be ✅ before any Phase 5 code is written.
Each step references the section in this document where the full details live.

```
STAGE A — BEFORE INSTALLING AVNAV
──────────────────────────────────
[ ] A1. Run all pre-install checks → Section 2
        Confirm: port 8080 free, port 8085 free (keyboard-api moved to 8087), Signal K port known, disk space OK
[ ] A2. Record Signal K port in SESSION_LOG.md (8099 or 3000?)
        If NOT 8099, update D3KOS_PLAN.md master URL table before continuing
[x] A3. Port 8085 conflict RESOLVED (2026-03-13) — keyboard-api moved to 8087, port 8085 free for AvNav updater
        (Verify Pi deploy before install: ss -tlnp | grep :8087 should show keyboard-api)

STAGE B — INSTALL AVNAV
────────────────────────
[ ] B1. Open OpenPlotter Settings → Apps → AvNav Installer → Install
        → DO NOT use standalone .deb package (see Warning 1)
[ ] B2. Enable Autostart in OpenPlotter → Apps → AvNav Installer → Autostart ON
[ ] B3. Start AvNav from OpenPlotter or: sudo systemctl start avnav

STAGE C — VERIFY INSTALLATION
──────────────────────────────
[ ] C1. Run the full verification script → Section 5
        All items must show ✓ before continuing
[ ] C2. Open http://localhost:8080 in Chromium — chart plotter must load
[ ] C3. Confirm AvNav is connected to Signal K at correct port → Section 3 Step 4

STAGE D — FIND AND RECORD DATA PATHS
──────────────────────────────────────
[ ] D1. Run: find /home /var /opt -name "avnav_server.xml" 2>/dev/null
        Record actual AvNav data root in SESSION_LOG.md
[ ] D2. Update AVNAV_DATA path in:
        - docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md
        - ai-bridge/config/ai-bridge.env (AVNAV_DATA_DIR=)

STAGE E — VERIFY API AND FILE ACCESS
──────────────────────────────────────
[ ] E1. Run all POST API commands from Section 4
        Confirm keys return real data (gps.lat, gps.lon, gps.speed, etc.)
[ ] E2. Load a test 2-waypoint route in AvNav, activate it
[ ] E3. Confirm currentLeg.json is created and readable:
        cat $(find /home /var /opt -name "currentLeg.json" 2>/dev/null | head -1)
[ ] E4. Create a short test track in AvNav, then check:
        ls $(find /home /var /opt -path "*/avnav/data/tracks" -type d 2>/dev/null)
[ ] E5. Create AVNAV_API_REFERENCE.md with real JSON responses → Section 6

STAGE F — FINAL GATE CHECK BEFORE PHASE 5
───────────────────────────────────────────
[ ] F1. AvNav loads at http://localhost:8080 ✓
[ ] F2. GPS position showing in AvNav from Signal K ✓
[ ] F3. currentLeg.json path is known and confirmed readable ✓
[ ] F4. Track GPX path is known and confirmed readable ✓
[ ] F5. API POST returns valid gps.lat and gps.lon ✓
[ ] F6. Signal K port confirmed and all plan documents updated ✓
[ ] F7. AVNAV_API_REFERENCE.md exists with real responses ✓
[x] F8. Port 8085 conflict resolved — keyboard-api at 8087, port 8085 free ✓
[ ] F9. SESSION_LOG.md updated with all findings ✓

→ ALL F items checked? Phase 5 implementation may begin.
```

---

## SECTION 1 — WHAT AVNAV IS AND HOW IT FITS d3kOS

AvNav is a web-based chart plotter — the entire UI runs in a browser at `http://localhost:8080`.
It is touch-optimised, runs as a background service, and handles:

- Chart display (raster + o-charts vector)
- GPS position tracking and route navigation
- Waypoints, routes, tracks (GPX files)
- AIS overlay
- Anchor watch alarm (built-in)
- Voyage log recording

**When installed via OpenPlotter**, AvNav receives ALL NMEA data from Signal K automatically.
It does NOT scan for USB GPS/AIS devices itself — OpenPlotter and Signal K handle that.
This means: install AvNav → point it at Signal K → everything works. No serial port config needed.

**Note on AvNav's built-in anchor watch:** AvNav has its own anchor watch alarm at the UI level.
Phase 5 adds a second AI-enhanced anchor watch that reads Signal K paths and adds AI advisory.
During Phase 5 P5.2 (Node-RED flow audit), confirm AvNav's alarm and Phase 5's alarm will not
fire conflicting alerts simultaneously. The Phase 5 anchor watch is additive — never replace
AvNav's built-in alarm.

### Port Map After Installation

| Service | Port | Notes |
|---|---|---|
| AvNav web interface | **8080** | Primary chart viewer — d3kOS iframe |
| AvNav o-charts process | **8082** | Auto-started by AvNav when needed |
| AvNav updater | **8085** | keyboard-api moved to **8087** — port 8085 free ✓ |
| Signal K (this Pi) | **8099** | Verify with command in Section 2 |

---

## SECTION 2 — PRE-INSTALL CHECKS

Run all of these before installing. Do not skip.

```bash
# 1. Confirm Signal K is actually on 8099 (not moved to default 3000)
curl -s --max-time 5 http://localhost:8099/signalk | python3 -m json.tool | head -10
# Expected: JSON with "version" and "endpoints" keys
# If this fails, try port 3000:
curl -s --max-time 5 http://localhost:3000/signalk | python3 -m json.tool | head -10
# Document which port responds and update D3KOS_PLAN.md if needed

# 2. Confirm port 8080 is free for AvNav
ss -tlnp | grep :8080
# Must return nothing — if something is on 8080, stop and report before proceeding

# 3. Confirm port 8082 is free (AvNav o-charts process)
ss -tlnp | grep :8082
# Must return nothing

# 4. Check OpenPlotter version — needed to confirm which AvNav installer to use
cat /etc/openplotter-version 2>/dev/null \
  || cat /usr/lib/openplotter-settings/version 2>/dev/null \
  || dpkg -l | grep openplotter-settings | awk '{print $3}'

# 5. Check available disk space — AvNav + charts need headroom
df -h /
# Need at least 2GB free before charts; 500MB minimum for the install itself

# 6. Check if openplotter-avnav package is already available in apt
apt-cache search openplotter-avnav
# If nothing returned, the OpenPlotter repo may need updating (Section 3, step 1)

# 7. Port 8085 conflict — RESOLVED 2026-03-13
# keyboard-api.service moved to port 8087 — port 8085 is free for AvNav updater
# Verify Pi deploy is complete before AvNav install:
ss -tlnp | grep :8087 && echo "keyboard-api on 8087 — OK" || echo "WARN: Session 1 deploy not yet done"
ss -tlnp | grep :8085 && echo "WARN: port 8085 still occupied" || echo "Port 8085 free — OK"
```

**Stop and resolve before continuing if:**
- Port 8080 is already in use
- Signal K is not responding on 8099 (or 3000)
- Disk space is under 500MB free
- OpenPlotter version is unclear
- Port 8085 is still occupied (keyboard-api must be deployed to Pi on 8087 before install)

---

## SECTION 3 — INSTALLATION PROCEDURE

### Step 1 — Update OpenPlotter package lists

```bash
sudo apt update
```

If you get a GPG error for the OpenPlotter repository:
```bash
# Re-add OpenPlotter signing key
curl -fsSL https://dl.openplotter.cloud/public.gpg | sudo gpg --dearmor \
  -o /usr/share/keyrings/openplotter-archive-keyring.gpg
sudo apt update
```

### Step 2 — Install via OpenPlotter Settings GUI (recommended path)

This is the safest method — it handles all dependencies and Signal K wiring automatically.

1. Open **OpenPlotter Settings** from the Pi menu → Main → OpenPlotter
2. Click the **Apps** tab
3. Find **AvNav Installer** in the list
4. Click **Install**
5. Wait for installation to complete — it will download AvNav and configure Signal K integration
6. Click **Autostart ON** to enable AvNav at boot
7. Click **Start** to launch AvNav immediately

### Step 2 (alternative) — Install via terminal if GUI unavailable

```bash
# Install the OpenPlotter AvNav integration package
sudo apt install openplotter-avnav

# Enable and start the AvNav service
sudo systemctl enable avnav
sudo systemctl start avnav

# Verify it's running
sudo systemctl status avnav
```

### Step 3 — Verify installation

```bash
# Service must be active
sudo systemctl status avnav | head -15

# Port 8080 must now be listening
ss -tlnp | grep :8080
# Expected: something like: LISTEN 0 5 0.0.0.0:8080 ... avnav

# AvNav web interface must respond
curl -s --max-time 10 http://localhost:8080 | head -5
# Expected: HTML starting with <!DOCTYPE html>

# Check AvNav data directory location
sudo systemctl cat avnav | grep -i workingdirectory
find /home -name "avnav_server.xml" 2>/dev/null
find /home -name "currentLeg.json" 2>/dev/null
# Document the actual data directory — needed for Phase 5 file access
```

### Step 4 — Connect AvNav to Signal K

When installed via OpenPlotter, this connection is made automatically.
Verify it is working:

1. Open `http://localhost:8080` in Chromium
2. Go to Settings (top right gear icon)
3. Navigate to **Server** → **SignalK**
4. Confirm the Signal K URL shows `http://localhost:8099` (or whichever port is confirmed active)
5. Confirm status shows **connected**

If not automatically connected:
```
In AvNav UI → Settings → Server → SignalK:
  URL: http://localhost:8099/signalk
  Enable: ON
  Save and restart AvNav
```

### Step 5 — Record actual data directory

After installation, find and record the exact paths:

```bash
# Find data directory
find /home /var /opt -name "avnav_server.xml" 2>/dev/null

# List the data subdirectories
AVNAV_DATA=$(dirname $(find /home /var /opt -name "avnav_server.xml" 2>/dev/null | head -1))
echo "AvNav data root: $AVNAV_DATA"
ls -la $AVNAV_DATA/

# Expected structure (actual path TBD from above):
# .../avnav/data/
#   routes/     ← route GPX files + currentLeg.json
#   tracks/     ← daily track GPX files (YYYY-MM-DD.gpx)
#   charts/     ← chart files
#   log/        ← AvNav log files
```

**Record the actual path in SESSION_LOG.md** — Phase 5 file access depends on it.

---

## SECTION 4 — AVNAV HTTP API REFERENCE

### Critical: API Uses POST, Not GET

Confirmed on this Pi — GET requests return HTTP 501 "Unsupported method".
**All API calls must use POST.**

### Base URL

```
http://localhost:8080/viewer/avnav_navi.php
```

### Known Endpoints

All requests are POST to the base URL with a JSON body or form data.

#### GPS — Get Live Navigation Data

⚠️ **UPDATED 2026-03-13:** `request=navigate` does NOT exist in AvNav v20250822.
Use `request=gps`. Key names use Signal K path notation (see below).
Full verified response: `docs/AVNAV_API_REFERENCE.md`

```bash
# POST request — get current GPS and navigation state
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=gps"
```

Expected response shape (verified on Pi 2026-03-13, AvNav 20250822):
```json
{
  "version": "20250822",
  "signalk": {
    "navigation": {
      "position": {
        "latitude": 43.68619666666667,
        "longitude": -79.52087666666667
      },
      "courseOverGroundTrue": 0,
      "speedOverGround": 0,
      "datetime": "2026-03-13T15:54:42.000Z",
      "gnss": {
        "satellitesInView": { "count": 16, "gnss": "GPS" }
      }
    },
    "propulsion": { "port": { "revolutions": 0 } }
  }
}
```

**Actual key names (verified on Pi — NOT the original spec values):**

| Data | Actual Key Path | Unit |
|---|---|---|
| GPS latitude | `signalk.navigation.position.latitude` | decimal degrees |
| GPS longitude | `signalk.navigation.position.longitude` | decimal degrees |
| Speed over ground | `signalk.navigation.speedOverGround` | m/s — multiply × 1.944 for knots |
| Course over ground | `signalk.navigation.courseOverGroundTrue` | radians (convert to degrees) |
| GPS datetime | `signalk.navigation.datetime` | ISO-8601 string |
| Satellites in view | `signalk.navigation.gnss.satellitesInView.count` | integer |
| Engine RPM | `signalk.propulsion.port.revolutions` | rev/s |

**NOTE:** Route/waypoint keys (`nav.wp.*`, `nav.route.*`, `nav.anchor.*`) were not present
in live response — these likely appear only when a route is active in AvNav.
Verify by loading a route in AvNav and repeating `request=gps`.

#### Status Check

```bash
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=status"
```

#### List Routes

```bash
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=list&type=route"
```

#### Download a Route GPX

```bash
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=download&name=MyRoute.gpx&type=route" \
  -o /tmp/myroute.gpx
```

#### List Tracks

```bash
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=list&type=track"
```

#### Download Today's Track GPX

```bash
TODAY=$(date +%Y-%m-%d)
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=download&name=${TODAY}.gpx&type=track" \
  -o /tmp/today_track.gpx
cat /tmp/today_track.gpx | head -20
```

### ⚠️ API vs File Access — Use Files Where Possible

For routes and tracks, reading files directly is faster, more reliable, and
fully offline. Only use the HTTP API for **live navigation data** (GPS, speed, heading,
active waypoint) where you need the current real-time state.

```python
import json
from pathlib import Path

# ── File-based access (preferred for routes and tracks) ──

# Read active navigation leg
AVNAV_DATA = Path("/var/lib/avnav")  # confirmed path on this Pi (2026-03-13)

def get_current_leg() -> dict:
    """Read active route/waypoint from AvNav currentLeg.json."""
    leg_file = AVNAV_DATA / "routes" / "currentLeg.json"
    if leg_file.exists():
        return json.loads(leg_file.read_text())
    return {}

def get_latest_track_gpx() -> str:
    """Return GPX text of today's track file."""
    from datetime import date
    today = date.today().isoformat()  # YYYY-MM-DD
    track_file = AVNAV_DATA / "tracks" / f"{today}.gpx"
    if track_file.exists():
        return track_file.read_text()
    return ""

def list_track_files() -> list:
    """List all track GPX files, newest first."""
    tracks = sorted(
        (AVNAV_DATA / "tracks").glob("*.gpx"),
        reverse=True
    )
    return [str(t) for t in tracks]

# ── HTTP API access (use for live GPS/nav data only) ──

import requests

AVNAV_API = "http://localhost:8080/viewer/avnav_navi.php"

NAV_KEYS = ",".join([
    "gps.lat", "gps.lon", "gps.speed", "gps.track",
    "nav.wp.name", "nav.wp.lat", "nav.wp.lon", "nav.wp.distance",
    "nav.route.name", "nav.route.numpoints",
    "nav.anchor.distance", "nav.anchor.heading"
])

def get_nav_data() -> dict:
    """Get live navigation state from AvNav API."""
    try:
        r = requests.post(
            AVNAV_API,
            data={"request": "navigate", "keys": NAV_KEYS},
            timeout=3
        )
        result = r.json()
        if result.get("status") == "OK":
            return result.get("data", {})
    except Exception:
        pass
    return {}
```

---

## SECTION 5 — POST-INSTALL VERIFICATION CHECKLIST

Run after completing Section 3. All items must pass before Phase 5 work begins.

```bash
# Full post-install verification script
echo "=== AvNav Installation Verification ==="

echo ""
echo "--- Service Status ---"
systemctl is-active avnav && echo "✓ avnav service ACTIVE" || echo "✗ avnav NOT active"

echo ""
echo "--- Port Check ---"
ss -tlnp | grep :8080 && echo "✓ Port 8080 listening" || echo "✗ Port 8080 NOT listening"

echo ""
echo "--- HTTP Response ---"
STATUS=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" http://localhost:8080)
[ "$STATUS" = "200" ] && echo "✓ HTTP 200 OK at localhost:8080" || echo "✗ HTTP $STATUS at localhost:8080"

echo ""
echo "--- API POST Test ---"
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -d "request=status" | python3 -m json.tool | head -10

echo ""
echo "--- Data Directory ---"
find /home /var /opt -name "currentLeg.json" 2>/dev/null \
  && echo "✓ currentLeg.json found" \
  || echo "ℹ currentLeg.json not yet created (normal if no route is active)"

find /home /var /opt -name "avnav_server.xml" 2>/dev/null \
  && echo "✓ avnav_server.xml found" \
  || echo "✗ avnav_server.xml NOT found — check installation"

echo ""
echo "--- Signal K Connection ---"
curl -s --max-time 3 http://localhost:8099/signalk \
  && echo "✓ Signal K responding on 8099" \
  || echo "⚠ Signal K NOT on 8099 — check port"

echo ""
echo "--- Port 8085 / 8087 Check ---"
ss -tlnp | grep :8087 && echo "✓ keyboard-api on 8087" || echo "⚠ keyboard-api NOT on 8087 — Session 1 deploy needed"
ss -tlnp | grep :8085 && echo "⚠ Port 8085 occupied — check before AvNav install" || echo "✓ Port 8085 clear"

echo ""
echo "=== Done ==="
```

---

## SECTION 6 — THINGS TO DO AFTER VERIFICATION

In order, before Phase 5 coding starts:

**1. Record the actual AvNav data path**
Find it with `find /home /var /opt -name "avnav_server.xml"` then update:
- `docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` — `AVNAV_DATA` constant
- `ai-bridge/config/ai-bridge.env` — `AVNAV_DATA_DIR=` line

**2. Verify the exact API key names**
Run the navigate POST with all keys and look at the actual response.
Key names like `gps.speed` may differ across AvNav versions.
Document exact working keys in this file under Section 4.

**3. Confirm Signal K port**
If Signal K is on 3000 and not 8099 — update every reference in:
- `D3KOS_PLAN.md` (Master URL table)
- `docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` (all Signal K WebSocket URLs)
- `dashboard/config/d3kos-config.env` (SIGNALK_PORT)
- `gemini-nav/config/gemini.env`

**4. Create AVNAV_API_REFERENCE.md**
After running all the POST API commands with live data, create:
`/home/boatiq/Helm-OS/deployment/d3kOS/docs/AVNAV_API_REFERENCE.md`
Paste actual JSON responses from the Pi with real keys and values.
This is the ground truth for Phase 5 implementation.

**5. Load a test route in AvNav**
Create a simple 2-waypoint route in AvNav, activate it, then verify:
```bash
cat $(find /home /var /opt -name "currentLeg.json" 2>/dev/null | head -1)
```
This confirms the file is created and readable — essential for the route widget feature.

**6. Port 8085 conflict — RESOLVED 2026-03-13**
keyboard-api.service moved to port 8087 (8086 was taken by fish_detector). Port 8085 is free for AvNav updater.
Session 1 deploys updated keyboard-api.py and nginx to Pi — verify before AvNav install.

---

## SECTION 7 — ROLLBACK

If AvNav causes any problems with OpenPlotter, GPS, or Signal K:

```bash
sudo systemctl stop avnav
sudo systemctl disable avnav
sudo apt remove openplotter-avnav
sudo systemctl restart signalk  # restore Signal K to clean state
```

OpenCPN and all existing OpenPlotter functionality is completely unaffected.
AvNav is an additive install — it does not touch OpenCPN, Signal K config,
NMEA routing, or any existing OpenPlotter plugins.

---

*Document version 1.0.0 — Written 2026-03-13*
*Deployed to: `/home/boatiq/Helm-OS/deployment/d3kOS/docs/AVNAV_INSTALL_AND_API.md`*
*Source: `/mnt/c/Users/donmo/Downloads/AVNAV_INSTALL_AND_API.md` + Warning 4 (port 8085 conflict) added by Claude Code 2026-03-13*
