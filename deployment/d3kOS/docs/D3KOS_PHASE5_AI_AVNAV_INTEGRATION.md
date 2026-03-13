# d3kOS Phase 5 — AI + AvNav Integration Specification
**Project:** Helm-OS / d3kOS Marine Dashboard
**Operator:** Skipper Don / AtMyBoat.com
**Document:** `docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md`
**Version:** 1.1.0
**Status:** ACTIVE — implementation begins after Phase 4 is complete and stable
**Methodology:** AAO v1.1 | Master AI Engineering Standard
**Created:** 2026-03-13
**Amended:** 2026-03-13 — v1.0.0 anomalies corrected (see ANOMALY LOG at end of document)

---

## ANOMALY LOG — Changes from v1.0.0

The following errors were found during cross-check with AVNAV_INSTALL_AND_API.md and the
existing d3kOS plan. All are corrected in this document (v1.1.0):

| # | Section | v1.0.0 Error | Correction Applied |
|---|---|---|---|
| A1 | P5.0 pre-actions | All curl commands used `GET http://localhost:8080/api/...` — GET returns HTTP 501 | Replaced with `POST http://localhost:8080/viewer/avnav_navi.php` throughout |
| A2 | Architecture, ai-bridge.env, avnav_client.py | `AVNAV_API=http://localhost:8080/api` (wrong URL, wrong method) | Corrected to `AVNAV_API=http://localhost:8080/viewer/avnav_navi.php` (POST) |
| A3 | Port table | AvNav updater port 8085 not flagged as conflicting with keyboard-api.service | Conflict noted; RESOLVED 2026-03-13 — keyboard-api moved to 8087 (8086 taken by fish_detector) |
| A4 | Feature 4 | AvNav built-in anchor watch not acknowledged | Added coordination note — Phase 5 is additive, not replacement |

---

## PURPOSE OF THIS DOCUMENT

This document defines the complete specification for Phase 5 of d3kOS: deep integration
between the Gemini/Ollama AI proxy and the AvNav chart system. It was written from
Skipper Don's direct requirements and captures every design decision before a single
line of Phase 5 code is written.

**Do not implement Phase 5 until:**
- Phase 4 (Settings page + docs) is marked DONE in PROJECT_CHECKLIST.md
- AvNav installation is complete and verified (all Stages A-F in AVNAV_INSTALL_AND_API.md)
- AVNAV_API_REFERENCE.md exists with real responses from the live Pi
- The system has been stable through at least one real voyage
- This spec has been reviewed and approved by Don at session start

---

## REQUIREMENTS SUMMARY

All answers captured directly from Skipper Don — 2026-03-13.

| Requirement | Decision |
|---|---|
| Features to build | Route Widget, Port Arrival Briefing, Voyage Log Summary, Anchor Watch Alerts |
| Route widget trigger | Always-on dashboard widget — re-analyzes every **5 minutes** |
| Offline operation | **Critical** — full functionality required with Ollama only (no internet) |
| Port arrival info needed | Fuel dock, Marina/VHF, Customs, Anchorage, Provisioning, Tidal hazards |
| Port arrival trigger distance | **2 nautical miles** from destination waypoint (configurable) |
| AI response location | **Side panel** alongside AvNav chart + **audio TTS** on Pi speakers |
| Vessel data AI can read | GPS position, Active route & waypoints, SOG & heading, Engine data |
| Voyage log generation | **Both** — auto when track stops in AvNav + on-demand button |
| Anchor watch response | Screen alert + Audio TTS + Corrective action + Log drift event |
| AvNav REST API familiarity | Known but unexplored — must be researched in Phase 5 pre-actions |
| Existing Node-RED flows | **Significant custom integrations** — Phase 5 must integrate with, not replace |

---

## ARCHITECTURE OVERVIEW

### New Service: d3kOS AI Bridge

Phase 5 introduces one new service: `d3kos-ai-bridge` at **localhost:3002**.

This service is the central intelligence layer. It:
- Reads live vessel data from Signal K (`ws://localhost:8099/signalk/v1/stream`)
- Reads navigation data from AvNav REST API (`http://localhost:8080/viewer/avnav_navi.php` via POST)
- Calls the existing Gemini proxy (`http://localhost:3001/ask`) for all AI queries
- Outputs responses to the d3kOS side panel (via Server-Sent Events) and Pi audio (TTS)
- Exposes webhooks that Don's existing Node-RED flows can call

The Gemini proxy at port 3001 handles all online/offline routing (Gemini → Ollama).
The AI Bridge never calls Gemini or Ollama directly — it always goes through port 3001.

```
┌─────────────────────────────────────────────────────────────────┐
│                    d3kOS Phase 5 Data Flow                       │
│                                                                  │
│  Signal K :8099 ──WebSocket──┐                                   │
│                              │                                   │
│  AvNav :8080 ──POST API──────┼──► d3kOS AI Bridge :3002          │
│  (avnav_navi.php)            │         │                         │
│                              │                                   │
│  Node-RED flows ──Webhook────┘         │                         │
│                                        ▼                         │
│                              Gemini Proxy :3001                  │
│                                /ask endpoint                     │
│                                        │                         │
│                          ┌─────────────┴──────────────┐         │
│                          ▼                             ▼         │
│                   Gemini API                    Ollama :11434    │
│                (online path)                 (offline fallback)  │
│                                                                  │
│  AI Bridge :3002 outputs:                                        │
│    ├── SSE stream → Dashboard side panel (:3000)                 │
│    ├── TTS → Pi speakers (espeak-ng / piper)                     │
│    └── Event log → /home/boatiq/logs/ai-events/                  │
└─────────────────────────────────────────────────────────────────┘
```

### Port Assignment

| Service | Port | Notes |
|---|---|---|
| d3kOS Dashboard | **3000** | Existing — unchanged |
| Gemini AI Proxy | **3001** | Existing — unchanged |
| **d3kOS AI Bridge** | **3002** | NEW — Phase 5 |
| AvNav Charts | **8080** | Read-only — never modified |
| AvNav o-charts | **8082** | Auto-started by AvNav |
| AvNav updater | **8085** | keyboard-api moved to **8087** — port 8085 free ✓ (resolved 2026-03-13) |
| Signal K | **8099** | Read-only — never modified |
| OpenPlotter | **8081** | Infrastructure — never touched |
| Ollama (LAN) | **192.168.1.36:11434** | Via :3001 proxy only |

---

## PHASE 5 PRE-ACTIONS (MANDATORY BEFORE CODING)

These must be completed and documented **before any Phase 5 implementation begins**.

### P5.0 — AvNav REST API Exploration

**CRITICAL NOTE:** AvNav API uses POST only. GET returns HTTP 501. All commands below use POST.
Base URL: `http://localhost:8080/viewer/avnav_navi.php`
See `docs/AVNAV_INSTALL_AND_API.md` Section 4 for full API reference.

Before writing any code that depends on the API, verify actual key names and response shapes:

```bash
# 1. Check service status
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=status" | python3 -m json.tool

# 2. Get current GPS and navigation state
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=gps" \  # NOTE: request=navigate does not exist. Use request=gps. Keys use signalk.* notation. See AVNAV_API_REFERENCE.md
  | python3 -m json.tool

# 3. List all routes
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=list&type=route" | python3 -m json.tool

# 4. List all tracks
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=list&type=track" | python3 -m json.tool

# 5. Download today's track GPX (file-based access is preferred for tracks)
TODAY=$(date +%Y-%m-%d)
curl -s -X POST "http://localhost:8080/viewer/avnav_navi.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "request=download&name=${TODAY}.gpx&type=track" \
  -o /tmp/test_track.gpx
head -20 /tmp/test_track.gpx

# 6. Find and read currentLeg.json (route file — preferred over API for route data)
find /home /var /opt -name "currentLeg.json" 2>/dev/null
# If found:
cat $(find /home /var /opt -name "currentLeg.json" 2>/dev/null | head -1)
```

Document every key name and response shape in:
`/home/boatiq/Helm-OS/deployment/d3kOS/docs/AVNAV_API_REFERENCE.md`

This file must exist and be accurate before any feature implementation begins.

### P5.1 — Signal K Schema Audit

Confirm the exact Signal K paths for vessel data on Don's specific setup:

```bash
# Open Signal K data browser
# http://localhost:8099/signalk → browse live data tree

# Or via WebSocket — check what keys are actually present
python3 - << 'EOF'
import websocket, json

def on_message(ws, msg):
    d = json.loads(msg)
    if 'updates' in d:
        for u in d['updates']:
            for v in u.get('values', []):
                print(v['path'], '=', v['value'])

ws = websocket.WebSocketApp(
    'ws://localhost:8099/signalk/v1/stream?subscribe=all',
    on_message=on_message
)
ws.run_forever(ping_interval=20)
EOF
```

**Expected Signal K paths — verify each one is present:**

| Data | Expected SK Path | Unit |
|---|---|---|
| GPS position | `navigation.position` | lat/lon |
| Speed over ground | `navigation.speedOverGround` | m/s → convert to knots |
| Course over ground | `navigation.courseOverGroundTrue` | radians → convert to degrees |
| Heading magnetic | `navigation.headingMagnetic` | radians |
| Engine hours | `propulsion.0.runTime` | seconds |
| Engine temperature | `propulsion.0.coolantTemperature` | Kelvin |
| Oil pressure | `propulsion.0.oilPressure` | Pa |
| Anchor alarm radius | `navigation.anchor.maxRadius` | metres |
| Anchor position | `navigation.anchor.position` | lat/lon |
| Distance to anchor | `navigation.anchor.currentRadius` | metres |

**If a path is missing:** check OpenPlotter Signal K plugin configuration and
Node-RED flows that may be publishing to different paths. Document the actual
paths found on Don's system and update the code accordingly.

### P5.2 — Node-RED Flow Audit

Don has significant custom Node-RED flows. Before Phase 5:

```bash
# Find Node-RED flows directory
find /home/boatiq -name "flows*.json" 2>/dev/null
# or
find /home/boatiq/.node-red -name "*.json" 2>/dev/null

# Count flows and identify any that touch AvNav or Signal K
cat /home/boatiq/.node-red/flows.json | python3 -c \
  "import json,sys; flows=json.load(sys.stdin); \
   [print(f['id'],f.get('name',''),f.get('type','')) \
   for f in flows if any(k in str(f) for k in ['avnav','signalk','8080','8099'])]"
```

Document in `SESSION_LOG.md`:
- Which flows exist
- Which touch AvNav or Signal K
- Which output data that Phase 5 might duplicate or conflict with
- **Whether AvNav's built-in anchor watch alarm is wired into any flows** — if so, coordinate with Phase 5 anchor watch to avoid duplicate alerts firing simultaneously
- Any flows to preserve, wrap, or call from the AI Bridge

**Design rule:** Phase 5 adds capabilities alongside existing flows, never replaces them.
The AI Bridge exposes webhook endpoints that Node-RED flows can call if Don wants
to trigger AI features from within existing automations.

### P5.3 — TTS Engine Selection

The audio output requirement means a text-to-speech engine must be installed on the Pi.

```bash
# Option A: espeak-ng (lightweight, works offline, less natural voice)
sudo apt install espeak-ng
espeak-ng "d3kOS AI Bridge test. Anchor watch active." --stdout | aplay

# Option B: piper (neural TTS, better voice quality, still offline)
pip3 install piper-tts --break-system-packages
echo "d3kOS AI Bridge test" | piper --model en_US-lessac-medium --output_raw | aplay -r 22050 -f S16_LE -c 1

# Option C: festival
sudo apt install festival
echo "d3kOS AI Bridge test" | festival --tts
```

Evaluate voice quality on Pi speakers. Select one engine, document choice in
`ai-bridge/config/ai-bridge.env` as `TTS_ENGINE=espeak-ng` (or piper/festival).

**Priority:** Natural voice quality matters for underway alerts — piper is recommended
if Pi 4B has sufficient RAM headroom after all other services are running.

### P5.4 — Port Availability Check

```bash
# Port 3002 — must be free for AI Bridge
ss -tlnp | grep :3002 && echo "PORT 3002 IN USE — STOP" || echo "Port 3002 free"

# Port 8085 — RESOLVED 2026-03-13: keyboard-api moved to 8087, port 8085 free for AvNav
# Verify Pi deploy complete before AvNav install:
ss -tlnp | grep :8087 && echo "keyboard-api on 8087 — OK" || echo "WARN: keyboard-api not on 8087 yet"
ss -tlnp | grep :8085 && echo "WARN: something still on 8085" || echo "Port 8085 free — OK"
```

---

## FEATURE 1 — Always-On Route Analysis Widget

### What It Does

A persistent widget in the d3kOS dashboard (left panel, above the AvNav iframe) that
automatically queries the AI about the active AvNav route every **5 minutes**. Shows
a continuously updated passage brief: hazards, waypoint summary, estimated arrival,
conditions to watch.

### Data Inputs

```
AvNav POST API → active route waypoints (names, lat/lon, sequence) via nav.route.* keys
AvNav POST API → next waypoint ETA via nav.wp.* keys
Signal K :8099 → current GPS position
Signal K :8099 → speed over ground (converted to knots)
Signal K :8099 → course over ground (converted to degrees)
```

### AI Prompt Template

```
You are a marine navigation assistant for vessel {VESSEL_NAME},
home port {HOME_PORT}.

Current position: {lat:.4f}N, {lon:.4f}W
Speed: {sog:.1f} knots | Course: {cog:.0f}°
Active route: {route_name} — {waypoint_count} waypoints

Waypoints:
{waypoint_list}

Distance to next waypoint: {dtw:.1f} nm
Estimated arrival at destination: {eta}

Provide a brief passage analysis (4–6 sentences):
1. Next waypoint — any approach hazards or notes
2. Upcoming waypoints — anything to prepare for
3. One practical piece of local knowledge if relevant
4. Any timing or tidal considerations

Be concise. This is displayed on a chart tablet underway.
```

### Trigger Logic

```python
ROUTE_ANALYSIS_INTERVAL = 300  # 5 minutes in seconds

# Also re-trigger immediately if:
# - Active route changes (different route_name detected)
# - Next waypoint changes (skipped or arrived)
# - User taps "Analyze Now" button in widget
```

### Output

Brief text displayed in a collapsible panel above the AvNav iframe.
Updates silently in the background — no audio (only navigation events speak).

Widget states:
- `ACTIVE` — route loaded, analysis running every 5 min
- `NO ROUTE` — no active route in AvNav
- `UPDATING` — analysis in progress (spinner)
- `OFFLINE` — using Ollama, flagged with "OFFLINE AI" badge

---

## FEATURE 2 — Port Arrival Briefing

### What It Does

When the vessel reaches **2 nautical miles** from the **final destination waypoint**
of the active AvNav route, the AI Bridge automatically generates a full port arrival
briefing. Delivered via side panel AND audio TTS on Pi speakers.

Triggers once per destination — will not re-fire until a new destination is set.

### Data Inputs

```
AvNav POST API → final destination waypoint (name, lat/lon) via nav.wp.* keys
Signal K :8099 → current position
Signal K :8099 → speed over ground
```

### Trigger Detection

```python
ARRIVAL_TRIGGER_NM = 2.0  # nautical miles (configurable in ai-bridge.env)

def haversine_nm(lat1, lon1, lat2, lon2) -> float:
    """Returns distance in nautical miles between two lat/lon points."""
    # ... standard haversine calculation ...

# Polled every 60 seconds by AI Bridge
distance_to_dest = haversine_nm(
    current_lat, current_lon,
    dest_waypoint_lat, dest_waypoint_lon
)

if distance_to_dest <= ARRIVAL_TRIGGER_NM and not already_triggered_for_this_dest:
    fire_port_arrival_briefing(dest_waypoint_name)
    already_triggered_for_this_dest = True
```

### Port Arrival Briefing — Required Information

All six of the following must be included in the AI response:

| # | Category | Content |
|---|---|---|
| 1 | **Fuel Dock** | Location within marina, hours of operation, VHF channel for fuel |
| 2 | **Marina Contact** | Harbour master VHF channel, phone, berth availability, transient policy |
| 3 | **Customs / Entry** | Required procedures if crossing from another jurisdiction; pleasure craft decal; NEXUS/CBSA if Canadian |
| 4 | **Anchorage** | Best anchorage area, depth, bottom type, holding quality, any restrictions |
| 5 | **Provisioning** | Nearest grocery, chandlery, restaurants within walking or dinghy distance |
| 6 | **Approach Hazards** | Tidal timing, charted shoals, submerged hazards, speed restrictions, narrow channels |

### AI Prompt Template

```
You are a marine navigation assistant for vessel {VESSEL_NAME},
home port {HOME_PORT}. The vessel is approaching {destination_name}.

Current position: {lat:.4f}N, {lon:.4f}W
Speed: {sog:.1f} knots
Distance to {destination_name}: {distance:.1f} nautical miles

Provide a complete port arrival briefing covering ALL of the following:

1. FUEL DOCK — location, hours, VHF channel for fuel
2. MARINA CONTACT — harbour master VHF channel, phone, transient berths
3. CUSTOMS / ENTRY — any required procedures, documentation, or clearance
4. ANCHORAGE — best area, depth, bottom type, holding quality
5. PROVISIONING — grocery, chandlery, restaurants in walking/dinghy distance
6. APPROACH HAZARDS — tidal timing, shoals, speed limits, narrow channels

Format as numbered sections. Be specific and practical.
Note if any information may be outdated and should be verified on official charts.
```

### Audio Delivery

The full briefing is long — audio is delivered in two stages:

**Stage 1 — Spoken immediately (short):**
```
"Approaching {destination_name}. Two nautical miles.
Port arrival briefing ready on screen.
Key hazard: {first_hazard_sentence_extracted}."
```

**Stage 2 — Full briefing on screen only (too long for audio).**
User can tap any section heading to hear it read aloud.

---

## FEATURE 3 — Voyage Log Summarization

### What It Does

Reads the GPX track exported from AvNav and generates a plain-English voyage summary:
departure, arrival, route taken, notable waypoints, total distance, elapsed time,
average speed, and any observations. Saved as a log entry.

### Trigger Modes

**Auto-trigger:** When AvNav stops recording a track (record status changes from
`recording` to `stopped`). AI Bridge detects this via polling AvNav POST API.

**On-demand:** User taps "Summarize Voyage" button in the d3kOS dashboard.
A file picker (or most recent track selector) allows choosing which GPX to summarize.

### Data Inputs

```
AvNav data directory → GPX track file (read directly from disk — preferred over API)
AvNav POST API → track metadata (start time, end time, distance) if not in GPX
Signal K :8099 → engine hours at start vs end (if available)
```

### GPX Processing

```python
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_gpx_summary(gpx_text: str) -> dict:
    """
    Extract key statistics from GPX without sending raw GPS data to AI.
    Returns summary dict for prompt construction.
    """
    root = ET.fromstring(gpx_text)
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    points = root.findall('.//gpx:trkpt', ns)

    if not points:
        return {}

    first = points[0]
    last  = points[-1]

    # Extract start/end position names from nearest waypoints (AvNav metadata)
    # Calculate total distance using haversine between consecutive points
    # Extract start/end timestamps

    return {
        'start_lat':   float(first.get('lat')),
        'start_lon':   float(first.get('lon')),
        'end_lat':     float(last.get('lat')),
        'end_lon':     float(last.get('lon')),
        'start_time':  first.find('gpx:time', ns).text,
        'end_time':    last.find('gpx:time', ns).text,
        'point_count': len(points),
        'total_nm':    calculate_total_distance_nm(points),
    }
```

**Privacy rule:** Only the summary statistics are sent to the AI, not raw GPS coordinates.
The GPX file itself stays on the Pi.

### AI Prompt Template

```
You are a marine navigation assistant for vessel {VESSEL_NAME},
home port {HOME_PORT}.

Write a plain-English voyage log entry for the following passage:

Departure: approximately {start_lat:.3f}N, {start_lon:.3f}W at {start_time}
Arrival:   approximately {end_lat:.3f}N, {end_lon:.3f}W at {end_time}
Total distance: {total_nm:.1f} nautical miles
Elapsed time: {elapsed_hours:.1f} hours
Average speed: {avg_speed:.1f} knots
Track points recorded: {point_count}

Write a 3–5 sentence log entry as a skipper would write it in a paper log:
- Mention departure and arrival locations by approximate name if recognizable
- Include distance, time, and average speed
- Write in past tense, first person ("We departed..." or "Departed...")
- Keep it factual and nautical in tone
```

### Output Storage

```
/home/boatiq/logs/voyage-summaries/
  YYYY-MM-DD_HHmm_voyage_summary.txt    ← AI-generated text
  YYYY-MM-DD_HHmm_voyage_raw.gpx        ← original GPX track (kept locally)
```

Displayed in a "Voyage Summaries" panel in d3kOS settings (Phase 5 addition to settings page).
Most recent 5 summaries shown — tap to read full text.

---

## FEATURE 4 — Anchor Watch AI Alerts

### What It Does

Monitors anchor drag via Signal K. When the vessel drifts beyond the set anchor
radius, the AI Bridge fires four simultaneous responses:

1. **Screen alert** — plain-English description with current drift distance and direction
2. **Audio alarm** — spoken warning on Pi speakers (loud, repeated)
3. **Corrective action** — AI-generated suggestion for what to do
4. **Drift event log** — timestamped record with GPS coordinates saved to disk

**Note on AvNav's built-in anchor watch:** AvNav has its own anchor watch alarm at
the UI level. Phase 5's anchor watch reads the same Signal K paths and adds AI advisory.
Both may alert simultaneously when anchor drag is detected — this is intentional and
additive. Confirm during P5.2 (Node-RED audit) that existing Node-RED flows do not
create a third conflicting alarm path.

### Data Inputs

```
Signal K :8099 → navigation.anchor.maxRadius    (metres — set by skipper)
Signal K :8099 → navigation.anchor.currentRadius (metres — live distance from anchor)
Signal K :8099 → navigation.anchor.position     (lat/lon of set anchor point)
Signal K :8099 → navigation.position            (current vessel position)
Signal K :8099 → navigation.speedOverGround     (knots — used in alert context)
```

### Trigger Logic

```python
ANCHOR_POLL_INTERVAL = 15  # seconds — check every 15s when anchor watch active
DRAG_CONFIRMATION_COUNT = 3  # must exceed radius 3 consecutive polls before alert fires
                              # prevents false alarms from GPS jitter

def check_anchor_drag(anchor_data: dict) -> bool:
    """
    Returns True if vessel has genuinely dragged anchor.
    Filters out GPS jitter by requiring 3 consecutive exceedances.
    """
    max_radius   = anchor_data.get('maxRadius', 0)
    current_dist = anchor_data.get('currentRadius', 0)

    if max_radius <= 0:
        return False  # anchor watch not active

    return current_dist > max_radius
```

### Four-Part Alert Response

**Part 1 — Immediate audio alarm (fires first, no AI needed):**
```
"Anchor drag detected. Anchor drag detected.
Vessel has moved {drift_metres:.0f} metres from anchor position.
Check your position immediately."
```
This fires from pre-written text — does NOT wait for AI response.
Repeated every 60 seconds until dismissed.

**Part 2 — Screen alert (fires simultaneously with audio):**
```
ANCHOR DRAG ALERT
Drift: {current_radius:.0f}m (limit: {max_radius:.0f}m)
Direction: {drift_bearing:.0f} degrees from anchor
Time: {timestamp}
Speed: {sog:.1f} kts
[DISMISS]  [GET AI ADVICE]
```

**Part 3 — AI corrective action (generated after alert fires):**

```python
# AI prompt for corrective action
prompt = f"""
Marine emergency: vessel {VESSEL_NAME} anchor drag detected.

Anchor position: {anchor_lat:.4f}N, {anchor_lon:.4f}W
Current position: {current_lat:.4f}N, {current_lon:.4f}W
Drift distance: {drift_metres:.0f} metres
Current speed: {sog:.1f} knots
Time: {timestamp}
Conditions: {conditions_summary}

Provide a brief, calm, practical 3-4 step corrective action plan.
Steps should be in order of urgency. Be direct. This is an emergency.
"""
```

Result shown when user taps "GET AI ADVICE" — not spoken automatically
(skipper may already be on deck dealing with the situation).

**Part 4 — Drift event log entry:**

```
/home/boatiq/logs/anchor-events/
  YYYY-MM-DD_HHmm_anchor_drag.json
```

```json
{
  "timestamp":        "2026-07-15T03:42:17Z",
  "event_type":       "anchor_drag",
  "anchor_position":  {"lat": 43.8421, "lon": -76.3142},
  "vessel_position":  {"lat": 43.8406, "lon": -76.3128},
  "drift_metres":     47.3,
  "drift_bearing":    218,
  "max_radius_set":   30,
  "sog_at_event":     0.4,
  "ai_advice_requested": false
}
```

---

## AI BRIDGE SERVICE — IMPLEMENTATION SPEC

### File Location

```
/home/boatiq/Helm-OS/deployment/d3kOS/ai-bridge/
├── ai_bridge.py              ← main service (port 3002)
├── features/
│   ├── route_analyzer.py     ← Feature 1: route widget
│   ├── port_arrival.py       ← Feature 2: arrival briefing
│   ├── voyage_logger.py      ← Feature 3: log summarization
│   └── anchor_watch.py       ← Feature 4: anchor alerts
├── utils/
│   ├── signalk_client.py     ← WebSocket reader for ws://localhost:8099
│   ├── avnav_client.py       ← POST client for http://localhost:8080/viewer/avnav_navi.php
│   ├── tts.py                ← text-to-speech wrapper (espeak-ng / piper)
│   └── geo.py                ← haversine, bearing, unit conversions
├── logs/                     ← auto-created at runtime
│   ├── voyage-summaries/
│   └── anchor-events/
├── config/
│   └── ai-bridge.env         ← NEVER commit — verify gitignore covers **/*.env
└── tests/
    └── test_ai_bridge.py
```

### Config File

`ai-bridge/config/ai-bridge.env` (covered by `**/*.env` in Phase 0 .gitignore — verify before first commit):

```env
# d3kOS AI Bridge Configuration — DO NOT COMMIT
AI_BRIDGE_PORT=3002
GEMINI_PROXY_URL=http://localhost:3001
SIGNALK_WS=ws://localhost:8099/signalk/v1/stream
AVNAV_API=http://localhost:8080/viewer/avnav_navi.php
AVNAV_DATA_DIR=/home/boatiq/avnav/data
VESSEL_NAME=Your Vessel Name
HOME_PORT=Your Home Port

# Feature intervals
ROUTE_ANALYSIS_INTERVAL=300
ANCHOR_POLL_INTERVAL=15
ARRIVAL_POLL_INTERVAL=60
ARRIVAL_TRIGGER_NM=2.0
ANCHOR_DRAG_CONFIRM_COUNT=3

# TTS engine: espeak-ng | piper | festival
TTS_ENGINE=espeak-ng

# Audio device (find with: aplay -l)
AUDIO_DEVICE=default

# Log directories
LOG_DIR=/home/boatiq/logs
```

### Flask Endpoints

```python
# ai_bridge.py endpoints

GET  /status           → health check — all subsystem states
GET  /stream           → Server-Sent Events to dashboard (route widget updates, alerts)
POST /analyze-route    → trigger immediate route analysis (from "Analyze Now" button)
POST /summarize-voyage → trigger voyage summary from GPX file path or "latest"
POST /anchor/activate  → start anchor watch (radius in metres from request body)
POST /anchor/dismiss   → dismiss active anchor alarm

# Node-RED webhook endpoints (for Don's existing flows)
POST /webhook/arrival  → Node-RED can trigger a port briefing for a named destination
POST /webhook/alert    → Node-RED can push a custom alert through TTS + screen
POST /webhook/query    → Node-RED can send arbitrary marine queries to AI and get response
```

### Server-Sent Events Stream

The dashboard side panel subscribes to `GET /stream` and receives real-time events:

```javascript
// In dashboard index.html — Phase 5 addition
const bridge = new EventSource('http://localhost:3002/stream');

bridge.addEventListener('route_update', e => {
  const data = JSON.parse(e.data);
  document.getElementById('route-widget').innerHTML = data.html;
});

bridge.addEventListener('arrival_briefing', e => {
  const data = JSON.parse(e.data);
  showSidePanel('arrival', data);
  // Audio already firing from server side
});

bridge.addEventListener('anchor_alert', e => {
  const data = JSON.parse(e.data);
  showAnchorAlarm(data);
  // Audio already firing from server side
});

bridge.addEventListener('voyage_summary', e => {
  const data = JSON.parse(e.data);
  showSidePanel('voyage', data);
});
```

### Phase 2 Dashboard /status Update Required

When Phase 5 is deployed, update `dashboard/app.py` `/status` endpoint to also check AI Bridge:

```python
# Add to status() in app.py when Phase 5 goes live:
'ai_bridge': check_service('3002'),  # localhost:3002
```

And add a corresponding indicator to `index.html` status bar:
```html
<span id="indicator-ai-bridge" class="indicator" title="AI Bridge :3002">🧠</span>
```

---

## NODE-RED INTEGRATION GUIDE

Don's existing Node-RED flows are kept intact. Phase 5 integrates in two ways:

### Option A — Node-RED calls AI Bridge (recommended)

Node-RED flows can POST to AI Bridge webhook endpoints to trigger AI features:

```
POST http://localhost:3002/webhook/query
Body: { "query": "What is the VHF channel for Kingston Harbour Master?" }
Response: { "response": "...", "source": "gemini|ollama" }

POST http://localhost:3002/webhook/alert
Body: { "message": "Engine temperature high — 105 degrees C", "severity": "warning" }
→ Fires TTS + screen alert in d3kOS
```

### Option B — AI Bridge reads Signal K (passive, no Node-RED changes needed)

The AI Bridge reads from Signal K WebSocket (`ws://localhost:8099`).
If Node-RED is already publishing data to Signal K paths, the AI Bridge reads it
automatically without any flow changes.

### Mapping Don's Existing Flows

During Phase 5 pre-actions (P5.2), identify which of Don's flows:
- Already publish anchor/engine data to Signal K → AI Bridge reads automatically
- Need to be updated to use `/webhook/alert` instead of their own notification logic
- Should remain completely independent (no changes needed)

**Golden rule:** Never delete or modify an existing Node-RED flow in Phase 5.
Only add new flows that call AI Bridge endpoints.

---

## DASHBOARD CHANGES (Phase 5 additions to index.html)

### Side Panel

A new collapsible side panel (right side, similar to weather panel) is added to
the main dashboard for AI output. It sits between the AvNav iframe and the
weather panel position.

```
┌──────────────────────────────────────────────┐
│ STATUS BAR                                   │
├────────────────────────┬─────────────────────┤
│                        │  ← Route Widget     │
│                        │  ROUTE ANALYSIS     │
│   AvNav Chart          │  ─────────────────  │
│   Iframe               │  AI SIDE PANEL      │
│   localhost:8080       │  (SSE updates from  │
│                        │   localhost:3002)    │
│                        │                     │
├────────────────────────┴─────────────────────┤
│ BOTTOM BAR                                   │
└──────────────────────────────────────────────┘
```

### Route Widget (always visible when route active)

Compact display above or alongside the AvNav iframe:

```
┌─────────────────────────────────────────────────┐
│ ROUTE ANALYSIS  •  gemini-2.5-flash  •  3:42 PM │
│─────────────────────────────────────────────────│
│ Approaching Kingston via Main Duck Island.      │
│ Next wp (Duck Island, 8.3nm): deep water, no    │
│ hazards. Kingston: fuel at Portsmouth Olympic   │
│ Harbour, VHF 68. Approaching in ebb — enter     │
│ before 1800 for best depth at fuel dock.        │
│                          [Analyze Now]  [v]     │
└─────────────────────────────────────────────────┘
```

---

## SYSTEMD SERVICE

Create `/etc/systemd/system/d3kos-ai-bridge.service`:

```ini
[Unit]
Description=d3kOS AI Bridge — localhost:3002
After=network.target d3kos-dashboard.service d3kos-gemini.service
Wants=d3kos-dashboard.service d3kos-gemini.service

[Service]
Type=simple
User=boatiq
WorkingDirectory=/home/boatiq/Helm-OS/deployment/d3kOS/ai-bridge
ExecStart=/usr/bin/python3 ai_bridge.py
Restart=on-failure
RestartSec=5
EnvironmentFile=/home/boatiq/Helm-OS/deployment/d3kOS/ai-bridge/config/ai-bridge.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-ai-bridge
sudo systemctl start  d3kos-ai-bridge
```

---

## ROLLBACK PROCEDURE

Phase 5 is additive — existing services at :3000 and :3001 are never modified.

```bash
# Full Phase 5 rollback — stops AI Bridge, leaves everything else running
sudo systemctl stop    d3kos-ai-bridge
sudo systemctl disable d3kos-ai-bridge
sudo rm -f /etc/systemd/system/d3kos-ai-bridge.service
sudo systemctl daemon-reload

# Dashboard reverts to Phase 4 state automatically (SSE connection to :3002 will fail silently)
# index.html AI Bridge additions can be removed with git revert if needed
```

---

## TEST SUITE REQUIREMENTS

Create `/home/boatiq/Helm-OS/deployment/d3kOS/ai-bridge/tests/test_ai_bridge.py`

Tests must cover:

```python
# Unit tests
test_haversine_nm_calculation()          # geo.py — 2nm trigger accuracy
test_anchor_drag_confirmation_debounce() # 3-poll confirmation logic
test_gpx_summary_extraction()            # parse_gpx_summary() with sample GPX
test_signalk_path_parsing()              # correct unit conversions (m/s → kts, K → °C)
test_tts_generates_audio()               # espeak-ng/piper produces output file
test_avnav_client_uses_post()            # avnav_client.py must use POST not GET

# Integration tests (require live services)
test_avnav_api_reachable()               # POST to avnav_navi.php responds with status OK
test_signalk_ws_connects()               # ws://localhost:8099 stream receives data
test_gemini_proxy_reachable()            # http://localhost:3001/status responds

# Privacy tests
test_gpx_raw_data_not_in_prompt()        # raw GPS points never sent to AI
test_ai_bridge_cache_no_query_text()     # same rule as :3001 — no query storage

# Webhook tests
test_webhook_query_returns_response()    # POST /webhook/query returns JSON
test_webhook_alert_fires_tts()           # POST /webhook/alert triggers audio
```

All tests must pass before Phase 5 is marked DONE.

---

## PHASE 5 — DEFINITION OF DONE

- [ ] AvNav installed via OpenPlotter (not standalone .deb)
- [x] Port 8085 conflict RESOLVED — keyboard-api moved to 8087 (2026-03-13); Pi deploy pending
- [ ] AvNav REST API reference documented in `docs/AVNAV_API_REFERENCE.md` with real responses
- [ ] Signal K paths verified and documented for Don's exact setup
- [ ] Node-RED flows audited — no conflicts identified, anchor watch coordination confirmed
- [ ] TTS engine selected, installed, and tested on Pi speakers
- [ ] Port 3002 confirmed free and in use by `d3kos-ai-bridge`
- [ ] `ai-bridge.env` confirmed NOT in git (verify `**/*.env` .gitignore rule covers it)
- [ ] Route widget displays and updates every 5 minutes when route is active
- [ ] Route widget shows "NO ROUTE" state correctly when AvNav has no active route
- [ ] Route widget re-triggers immediately when route changes
- [ ] Port arrival briefing fires at exactly 2nm from destination waypoint
- [ ] Briefing covers all 6 required categories (fuel, marina, customs, anchorage, provisioning, hazards)
- [ ] Briefing audio plays Stage 1 spoken summary on Pi speakers
- [ ] Full briefing text visible in side panel
- [ ] Voyage summary auto-generates when AvNav track recording stops
- [ ] Voyage summary on-demand button works from dashboard
- [ ] Summaries saved to `/home/boatiq/logs/voyage-summaries/`
- [ ] Anchor watch alert fires screen notification on drag detection
- [ ] Anchor watch audio alert fires and repeats every 60s until dismissed
- [ ] AI corrective action available via "GET AI ADVICE" tap
- [ ] Drift event logged to `/home/boatiq/logs/anchor-events/`
- [ ] Node-RED webhook endpoints working: `/webhook/query`, `/webhook/alert`
- [ ] Existing Node-RED flows confirmed unmodified
- [ ] All pytest tests pass (including test_avnav_client_uses_post)
- [ ] Systemd service `d3kos-ai-bridge` starts on boot
- [ ] Phase 2 dashboard /status updated to include AI Bridge :3002 indicator
- [ ] Full offline test: disconnect internet, all features work via Ollama at 192.168.1.36:11434
- [ ] SESSION_LOG.md entry written
- [ ] PROJECT_CHECKLIST.md updated
- [ ] MEMORY.md updated with Phase 5 patterns

---

## OFFLINE-FIRST DESIGN RULES

Every feature in Phase 5 must function completely with Ollama at `192.168.1.36:11434`.

**Implementation consequences:**
- All AI queries go through Gemini proxy at `:3001` which handles routing automatically
- No feature should check internet connectivity directly — let `:3001` handle it
- Ollama model must have sufficient knowledge for marine use (mistral or llama3 recommended)
- If Ollama is also unreachable: features degrade gracefully — no crash, no hang
  - Route widget: shows "AI UNAVAILABLE — check Ollama at 192.168.1.36:11434"
  - Port arrival: fires audio "Approaching {port} — AI briefing unavailable" only
  - Anchor watch: audio/screen alarm fires immediately from pre-written text (never depends on AI)
  - Voyage log: queues for generation when AI next becomes available

**Anchor watch is the most safety-critical feature. It must never wait for AI.**
The alarm fires from hardcoded text the instant drag is confirmed.
The AI corrective action is advisory and on-demand only.

---

## OPEN QUESTIONS (resolve before implementation)

| # | Question | Impact |
|---|---|---|
| 1 | What Node-RED flows touch anchor/engine data? | May already have anchor alarm — coordinate, not duplicate |
| 2 | What is the exact Signal K path for anchor radius on Don's setup? | Core to anchor watch |
| 3 | Does AvNav track recording status appear in POST API response? | Core to auto voyage log trigger |
| 4 | Which TTS engine sounds best on the Pi's specific audio hardware? | Resolve in P5.3 |
| 5 | What Ollama model is currently installed and working at 192.168.1.36? | Needed for offline testing |
| 6 | Should port arrival briefings be cached? (offshore, approaching same port repeatedly) | UX improvement |
| 7 | What is the actual AvNav data directory path after installation? | Needed for AVNAV_DATA_DIR in ai-bridge.env |
| 8 | Does keyboard-api.service need to move from 8085 to 8086 before AvNav install? | **RESOLVED 2026-03-13** — moved to 8087 (8086 was taken by fish_detector). Port 8085 free for AvNav. |

Resolve all eight during Phase 5 pre-actions and document answers in SESSION_LOG.md.

---

*Document version 1.1.0 — Original written 2026-03-13. Anomalies corrected 2026-03-13.*
*See ANOMALY LOG section at top of document for all changes from v1.0.0.*
*Next review: start of Phase 5 implementation session.*
*Owner: Skipper Don / AtMyBoat.com*
