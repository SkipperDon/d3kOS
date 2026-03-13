# d3kOS — AvNav Plugins Guide
**Version:** 1.0.0 | **Phase:** 4 | **Updated:** 2026-03-13
**Applies to:** AvNav installed via OpenPlotter on Raspberry Pi 4B

---

## Overview

AvNav plugins extend chart functionality with AIS targets, anchor alarms, NMEA data display, voyage logging, and chart management. This guide covers the plugins most relevant to d3kOS.

**AvNav URL:** `http://localhost:8080`
**Signal K (data source):** `http://localhost:8099`
**Signal K WebSocket:** `ws://localhost:8099/signalk/v1/stream`

---

## Key Plugins

### 1. ochartsng — Commercial Charts

**Purpose:** Load purchased o-charts licensed charts (CHS, Admiralty, etc.)

**Install:**
1. AvNav Plugin Manager → Available → **ochartsng** → Install
2. Restart AvNav after install
3. Activate licence (see AVNAV_OCHARTS_INSTALL.md)

**Config:** AvNav Settings → ochartsng → enter o-charts credentials or import licence file

---

### 2. AvNav SignalK Plugin

**Purpose:** Reads live vessel data (GPS position, SOG, COG, depth, AIS) from Signal K and displays it on charts.

**Install:** Usually pre-installed with OpenPlotter's AvNav. Verify at Plugin Manager.

**Config:**
- Signal K URL: `http://localhost:8099`
- Signal K WebSocket: `ws://localhost:8099/signalk/v1/stream`

> **Critical:** The Signal K WebSocket address is `ws://localhost:8099` — NOT `ws://localhost:3000`.
> Port 3000 is the d3kOS Flask dashboard. This is a common misconfiguration.

**Verify:** In AvNav, open the status bar — GPS position should update live when Signal K is connected.

---

### 3. Anchor Alarm Plugin

**Purpose:** Sounds an alarm if the vessel drifts beyond a set radius from the anchor position.

**Note:** AvNav has a built-in anchor alarm. Phase 5 adds an AI-enhanced version (d3kOS Anchor Watch AI) that provides contextual advice and SMS/voice alerts.

**Setup:**
1. Drop anchor → go to AvNav → Anchor Alarm → Set Anchor Here
2. Set radius in meters (15–50m typical)
3. AvNav sounds alarm if position drifts beyond radius

**Coordination with d3kOS Phase 5:**
- Phase 5 anchor watch reads the same GPS position from Signal K (:8099)
- Both alarms can run simultaneously — d3kOS provides AI advice, AvNav provides the primary alarm sound
- See `D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` §P5.2 for Node-RED flow audit

---

### 4. Voyage Log / GPX Export

**Purpose:** Records your route as a GPX track file for navigation and sharing.

**Location of track files (Pi):** Check AvNav data root — typically `/home/d3kos/.avnav/tracks/`

**Phase 5 integration:** d3kOS Voyage Logger (Phase 5 Feature 3) reads these GPX files and generates AI-written voyage summaries. Only summary statistics are sent to AI — raw coordinates are never transmitted.

**Export:** AvNav → Tracks → select track → Export GPX

---

### 5. NMEA Display Plugin

**Purpose:** Shows raw NMEA 0183 or NMEA 2000 sentence data for diagnostics.

**Data path on d3kOS:** NMEA hardware → OpenPlotter (:8081) → Signal K (:8099) → AvNav (:8080)

**Troubleshoot:** If GPS shows in OpenPlotter but not AvNav, verify the Signal K AvNav plugin is connected to `:8099`.

---

## AvNav REST API Reference

AvNav uses a POST-only REST API for data queries.

> **Important:** All AvNav API calls must use **POST** — GET returns HTTP 501.

| Action | Method | URL | Body |
|--------|--------|-----|------|
| Get GPS position | POST | `http://localhost:8080/viewer/avnav_navi.php` | `{"request":"getStatus"}` |
| Get route info | POST | `http://localhost:8080/viewer/avnav_navi.php` | `{"request":"getCurrentLeg"}` |
| Get track list | POST | `http://localhost:8080/viewer/avnav_navi.php` | `{"request":"getTrackList"}` |

Full API reference (with real Pi responses) is created in Phase 5 Stage E: `deployment/d3kOS/docs/AVNAV_API_REFERENCE.md`

---

## Signal K Data Paths Used by AvNav

| Data | Signal K Path |
|------|---------------|
| GPS position | `vessels.self.navigation.position` |
| Speed over ground | `vessels.self.navigation.speedOverGround` |
| Course over ground | `vessels.self.navigation.courseOverGroundTrue` |
| Heading | `vessels.self.navigation.headingTrue` |
| Depth | `vessels.self.environment.depth.belowKeel` |
| AIS targets | `vessels` (all entries except self) |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No GPS in AvNav | Check SK plugin: AvNav → Plugins → SignalK → verify URL is `http://localhost:8099` |
| AIS targets missing | Ensure OpenPlotter AIS plugin is enabled and sending to SK |
| Anchor alarm not sounding | Check Pi audio output; AvNav audio uses system speaker |
| Plugin install fails | Check disk space and internet connection |
| Track files missing | Check AvNav data root path in AvNav settings |

---

*d3kOS v2.0 — deployment/d3kOS/docs/AVNAV_PLUGINS.md*
