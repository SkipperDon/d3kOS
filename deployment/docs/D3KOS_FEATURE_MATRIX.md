# d3kOS Feature Matrix
**Version:** v0.9.9.5 · **Created:** 2026-11-25 · **Source:** dashboard templates + service code

This document catalogues every menu item, dashboard ribbon, panel, overlay, and page in the d3kOS interface. Each entry lists capabilities, function description, and hardware dependencies.

---

## Table of Contents
1. [Status Bar (Top)](#1-status-bar-top)
2. [Instrument Panel Ribbons](#2-instrument-panel-ribbons)
3. [Chart / Main Area](#3-chart--main-area)
4. [Split Pane (AI · Weather · Cameras)](#4-split-pane-ai--weather--cameras)
5. [Bottom Navigation Bar](#5-bottom-navigation-bar)
6. [More Menu (Slide-Up Sheet)](#6-more-menu-slide-up-sheet)
7. [Overlay Cards & Alert Widgets](#7-overlay-cards--alert-widgets)
8. [Pages — Full-Screen Views](#8-pages--full-screen-views)

---

## 1. Status Bar (Top)

| Element | Capabilities | Description | Hardware |
|---|---|---|---|
| **AtMyBoat Logo / Vessel Name** | Display only | Shows the d3kOS brand mark and the vessel name set in AI Settings. Tapping the vessel name does nothing — it is a label. | None |
| **Ticker Tape** | Scrolling alerts, arrival notices, AI status messages | Animated horizontal ticker that carries real-time AI First Officer status messages, AIS-based situational advisories, anchor drag warnings, and port arrival briefings from the AI bridge. Updates dynamically via `ai-bridge.js`. | AI bridge service (port 3000); AIS via Signal K |
| **AI Nav Pill** (`hPill`) | Opens AI navigation split pane | Green pill button labelled "AI Nav" with a live status dot. Tapping it slides open the right-side split pane to the AI navigation chat tab. | Gemini AI service (port 3001) |
| **Day / Night Toggle** | Two-mode display theme | Switches the entire dashboard between Day (light nautical green) and Night (deep red-black) colour modes. Mode persists across sessions via `localStorage`. | None |
| **Clock** | Real-time clock display | Shows current local time, updated every second by `instruments.js`. | Pi system clock / NTP |
| **Update Notice Bar** | OTA update alerts | Hidden amber bar that appears when a new d3kOS version is available on atmyboat.com, or in red when an OTA install has failed. Shows version number and status. Can be dismissed per session. | OTA agent (`/update/status` endpoint); Internet |

---

## 2. Instrument Panel Ribbons

The row toggle bar at the top of the instrument panel lets the operator select which data rows are visible.

### 2a. Row Toggle Bar

| Toggle | Description | Hardware |
|---|---|---|
| **BOTH** | Shows Engine row and Nav row simultaneously (default) | N2K bus + GPS |
| **ENGINE** | Shows Engine row only; hides Nav row. Displays engine alert badge and engine state chip (ON/OFF/UNKNOWN). | N2K bus / PiCAN-M |
| **NAV** | Shows Nav row only; hides Engine row. Displays nav alert badge. | GPS / depth sounder |
| **WX** | Hides both instrument rows and loads the full-screen Weather iframe view. | Internet (Windy) + GPS |

### 2b. Engine Ribbon

| Cell | Capabilities | Description | Hardware |
|---|---|---|---|
| **RPM** | Live reading; right-click context menu (change source, alert thresholds, priority, schedule position report, hide) | Engine revolutions per minute. Sourced from Signal K via N2K engine PGNs. Colour-coded at alert thresholds. | PiCAN-M HAT → Signal K → N2K bus / engine tachometer |
| **Trim** | Live reading; context menu | Engine trim angle in degrees. Positive = trimmed up. | PiCAN-M HAT → Signal K → N2K trim sensor |
| **Oil Pressure** | Live reading; alert threshold; critical alert trigger; context menu | Engine oil pressure in PSI. Triggers the AI Critical Engine Screen when it falls below the minimum safe threshold. | PiCAN-M HAT → Signal K → N2K oil pressure sender |
| **Coolant Temperature** | Live reading; alert threshold; AI diagnostic trigger; context menu | Engine coolant temperature in °C (or °F based on unit settings). Right-click opens the AI Engine Diagnostic card for Gemini-powered analysis. | PiCAN-M HAT → Signal K → N2K coolant temp sender |
| **Fuel** | Live reading; range estimate; context menu | Fuel tank level as a percentage, estimated litres remaining, and estimated range at current consumption rate. | PiCAN-M HAT → Signal K → N2K fuel tank sender |

### 2c. Nav Ribbon

| Cell | Capabilities | Description | Hardware |
|---|---|---|---|
| **Speed (SOG)** | Live reading; context menu | Speed Over Ground in knots. GPS-derived via Signal K. | GPS module → Signal K |
| **Depth** | Live reading; context menu | Water depth in metres below the transducer. | Depth sounder → N2K → PiCAN-M → Signal K |
| **Course (COG)** | Live reading; context menu | Course Over Ground in degrees true. GPS-derived via Signal K. | GPS module → Signal K |
| **GPS Position** | Live reading; lat/lon display; context menu | Current vessel position in degrees and decimal minutes. Updates continuously from GPS. Used as the anchor point for Anchor Watch and the Windy weather embed. | GPS module → Signal K |
| **Next Waypoint** | Destination name, distance (nm), ETA, bearing | Active waypoint from AvNav route planning. Shows destination name, distance in nautical miles, ETA, and true bearing. Only populated when a route is active in AvNav. | GPS → Signal K + AvNav chart plotter |

---

## 3. Chart / Main Area

| Element | Capabilities | Description | Hardware |
|---|---|---|---|
| **AvNav Chart Iframe** | Full interactive chart plotter; panning, zooming, waypoints, routes, AIS overlay, tide data | Embeds the AvNav chart navigation server as a full-width iframe. Host is resolved client-side (not server-side) so the chart works from any device on the LAN — not just the Pi's own screen. Port is supplied by Flask via `data-port`. | GPS → Signal K → AvNav (port 8080); AIS via Signal K; optional o-charts paid chart data |
| **Route AI Strip** (`rw`) | AI route briefing; tap "GEMINI" badge to trigger | Collapsible banner above the chart that displays AI-generated route analysis text from the Gemini AI bridge. Triggered manually via the GEMINI badge or automatically by the AI bridge on route change. Shows state label (ANALYZING / READY), main route text, and metadata line. | Gemini AI bridge (port 3000); GPS; AvNav active route |

---

## 4. Split Pane (AI · Weather · Cameras)

Opened by the AI Nav pill, Weather bottom nav button, or programmatically by the AI bridge. Slides in from the right, covering part of the chart area.

### 4a. AI Nav Tab

| Element | Capabilities | Description | Hardware |
|---|---|---|---|
| **Voyage Notice** | Arrival briefings, automated advisories | Auto-populated by the AI bridge with voyage-related notices (port arrival info, waypoint alerts). | AI bridge; GPS; Gemini AI |
| **AI Status Dot + Label** | Live connection indicator | Shows whether the Gemini AI service is reachable. Green dot = connected; grey = offline. | Gemini AI service (port 3001) |
| **Chat Body** | Full conversation history; Gemini responses; source citations | Displays the running conversation between the operator and the AI navigation assistant. Responses are sanitized (no raw HTML injected) and include markdown formatting. | Gemini AI (port 3001); Internet |
| **Text Input Field** | Natural language query input | Accepts typed navigation questions: routes, tides, weather routing, anchoring, fuel, customs, COLREGs, local info. Submitted via Enter or the Send button. | Gemini AI (port 3001) |
| **Mic Button** (`spMic`) | Voice input; starts Helm listening overlay | Tapping opens the Helm Listening Overlay for voice query input. Query text is returned to the AI input after Helm processes it. | Microphone (USB / built-in); Helm voice service |

### 4b. Weather Tab

| Sub-Tab | Capabilities | Description | Hardware |
|---|---|---|---|
| **Sea State** | Live wave height, swell direction, period (Windy) | Windy.com wave/swell layer centred on current GPS position. Auto-updates when GPS position changes. | GPS → Signal K; Internet (Windy embed) |
| **Radar** | Live rain radar overlay | Windy.com precipitation radar centred on vessel position. | GPS → Signal K; Internet |
| **Wind** | Live wind speed/direction map | Windy.com wind layer centred on vessel position. Shows wind barbs and speed contours. | GPS → Signal K; Internet |

### 4c. Cameras Tab (in-pane)

| Element | Capabilities | Description | Hardware |
|---|---|---|---|
| **Forward Watch Primary** | Live JPEG feed; full-width primary view | Displays the camera assigned to the `forward_watch` role as a full-width image refreshing every 2 seconds (configurable). Only visible when a forward_watch slot is assigned. | IP camera or USB camera via go2rtc (port 8084) |
| **Camera Grid** | Multi-camera live tiles | Shows all cameras with `display_in_grid` role as a 2-column thumbnail grid. Each tile refreshes independently at ~1500 ms intervals to keep Pi CPU load sustainable. | go2rtc (port 8084); IP or USB cameras |

---

## 5. Bottom Navigation Bar

Six fixed buttons at the bottom of every screen. The centre HELM button protrudes 24 px above the bar.

| Button | Capabilities | Description | Hardware |
|---|---|---|---|
| **Dashboard** | Returns to main dashboard view | Closes split pane and sets the dashboard nav item as active. This is the default home screen. | None (UI navigation) |
| **Weather** | Opens split pane to Weather tab | Opens the split pane and switches directly to the Weather sub-panel showing the Windy embed. | GPS → Signal K; Internet |
| **Marine Vision** | Full-page camera and AI detection view | Navigates to `/marine-vision` — the dedicated camera management, live feed, and fish/object detection page. | IP/USB cameras via go2rtc; ML detection model |
| **HELM** (centre) | Voice assistant; AI troubleshooting chat | Navigates to `/helm-assistant` — the Helm voice assistant and AI engine diagnostic page. Central raised button for quick access. | Microphone; Gemini AI; Signal K; onboard RAG manuals |
| **Boat Log** | Voyage record; voice notes; engine log | Navigates to `/boat-log` — the digital captain's log with voice recording, automatic engine data capture, and CSV export. | Microphone; Signal K engine data |
| **More** | Opens the full app menu | Opens the slide-up sheet with 8 additional pages: AI Navigation, Engine Dashboard, Helm Assistant, Initial Setup, Upload Documents, Manage Documents, Settings, Anchor Watch, Help / Manual. | None |

---

## 6. More Menu (Slide-Up Sheet)

Accessed via the "More" bottom nav button. Slides up from the bottom edge.

| Menu Item | Capabilities | Description | Hardware |
|---|---|---|---|
| **AI Navigation** | Full-screen navigation chat; COLREGs lookups; tide/weather routing; port and anchorage queries | Dedicated full-screen chat with the Gemini AI navigation assistant. Shows service status pill. Accepts any marine navigation question. Includes SafeHelm global script (COLREGs alert integration). | Gemini AI service (port 3001); Internet |
| **Engine Dashboard** | Full engine + tank + system + network status page | Dedicated full-page engine monitor with live Signal K WebSocket feed. Sections: Engine (RPM, oil, coolant, trim, battery), Tank Levels (fuel, water), System Status (CPU temp, memory, disk, uptime, IP), Network Status (Signal K, AvNav, Gemini AI, Ollama). | PiCAN-M HAT → Signal K (port 8099); N2K engine bus; system monitoring |
| **Helm Assistant** | AI engine diagnostics; RAG manual search; chat | AI-powered troubleshooting assistant. Combines live Signal K engine data with onboard PDF manual RAG and Gemini AI. Quick-action buttons for Engine Status and Run Diagnostics. Chat resolves queries against manuals first, then escalates to Gemini. | Microphone (optional); Signal K; Gemini AI (port 3001); PDF RAG service (port 8083) |
| **Initial Setup** | 8-step configuration wizard; NMEA DIP switch guide; mobile pairing | First-run wizard that configures vessel name, engine type/region, N2K DIP switches (CX5106 gateway diagram generated), mobile companion QR pairing, and AI First Officer. Tier 0 has a limited run count; Tier 1+ unlimited. | CX5106 NMEA 2000 gateway; PiCAN-M HAT; mobile device (PWA pairing via QR) |
| **Upload Documents** | PDF upload; document type classification; RAG indexing | Upload PDF manuals for engine, electronics, safety equipment, or charts. Documents are processed and indexed into the onboard Chroma vector store for use by Helm Assistant RAG queries. Progress shown with a live progress bar. | No hardware; manuals service (port 8083); Gemini embeddings |
| **Manage Documents** | List uploaded manuals; delete documents | View all indexed PDF manuals with file names and sizes. Permanently delete documents from the RAG index. Calls the manuals service at port 8083. | No hardware; manuals service (port 8083) |
| **Settings** | Full system configuration | Multi-section settings page (see §8 — Settings below). | All hardware indirectly |
| **Anchor Watch** | Anchor position set/clear; drag alarm; AI advice | Dedicated anchor watch page (see §8 — Anchor Watch below). | GPS → Signal K |
| **Help / Manual** | User guide and feature reference | In-app user manual for d3kOS. Static reference page. | None |

---

## 7. Overlay Cards & Alert Widgets

These appear over the main UI in response to system events, AI bridge triggers, or operator actions.

| Overlay | Capabilities | Description | Trigger | Hardware |
|---|---|---|---|---|
| **Helm Listening Overlay** | Voice query capture; mute toggle; cancel | Full-screen listening UI with animated ring, audio-level bars, and "HELM IS LISTENING" prompt. Mute button toggles the voice assistant between talking and muted. | Helm button tap or mic button in split pane | USB microphone; Helm voice service |
| **AI Alert Card** | Situational awareness alerts; AIS CPA warnings; acknowledge; escalate to AI | Modal card pushed by the AI bridge for AI First Officer situational alerts. Shows alert title, full advisory text, and three action buttons: Acknowledge, Ask AI More, Dismiss. | AI bridge event (AIS target, COLREGs trigger) | AIS via Signal K; Gemini AI bridge |
| **AI Engine Diagnostic Card** | Live engine data grid; Gemini AI analysis text; action recommendations | Full-panel diagnostic overlay. Shows a grid of current engine readings alongside a Gemini-generated analysis paragraph. Action buttons offer RPM reduction, full AI brief, or dismiss. | Right-click on any engine instrument cell | Signal K engine data; Gemini AI service (port 3001) |
| **Critical Engine Alert Screen** | Full-screen critical warning; engine-off confirmation | Red full-screen takeover for engine readings below the critical threshold (e.g. oil pressure < 20 PSI). Shows current value, safe range, and immediate action instructions. "Engine is off — stop alerting" button clears the alarm. | Signal K engine threshold breach via instruments.js | PiCAN-M HAT → Signal K → N2K |
| **Anchor Drag Widget** | Drift alert; AI advice button; dismiss | Compact floating card that appears when the Anchor Watch service detects the vessel has moved beyond the set radius. Shows drift distance and bearing, and offers an AI advice button. | Anchor Watch service event | GPS → Signal K |
| **Port Arrival Banner** | Arrival briefing; fuel/marina/approach/customs; full AI brief link | Sliding card that appears when the AI bridge detects the vessel is approaching the active waypoint destination. Shows ETA, distance, and a structured arrival briefing with fuel, marina, approach, and customs information. | AI bridge arrival event; GPS proximity to active waypoint | GPS → Signal K; Gemini AI bridge; Internet |
| **Position Report Overlay** | Full-screen speed/course/position display with auto-dismiss countdown bar | Full-screen position flash card intended for scheduled position reports. Shows speed, course, and lat/lon with a progress bar that auto-dismisses. | Right-click cell → "Schedule full-screen report" | GPS → Signal K |
| **Weather Conditions Panel** | Current conditions slide-over; wind map link | Left-side panel that slides over the chart area showing parsed weather conditions data. Has a "WIND MAP" button to open the full Windy split pane. | AI bridge weather event or operator trigger | GPS → Signal K; Internet (weather service) |
| **Cell Context Menu** | Change data source; set alert thresholds; mark priority; schedule position report; hide cell | Right-click (long-press) on any instrument cell opens a 5-item context menu for per-cell configuration. | Right-click / `oncontextmenu` on any `.ic` cell | None (UI action) |
| **Toast Notification** | Brief status confirmations | 2-second toast messages confirming actions (e.g. "Acknowledged — AI monitoring CPA"). Non-blocking. | Various UI actions | None |

---

## 8. Pages — Full-Screen Views

### Dashboard (`/` or `/dashboard`)
> Described fully in sections 1–7 above.

---

### Marine Vision (`/marine-vision`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Camera Selector** | Switch between configured camera slots; select active camera | Dynamically populated from `/camera/slots` API. Buttons for each assigned slot; "All Cameras" grid toggle. | go2rtc camera service (port 8084); IP or USB cameras |
| **Live Feed** | Real-time JPEG stream from active camera; 16:9 aspect ratio | Full-width live image feed from the selected camera slot. Refreshes at the go2rtc JPEG endpoint. Shows "Connecting to camera…" while establishing. | go2rtc (port 8084); IP camera (RTSP) or USB/Pi camera (V4L2) |
| **Recording Controls** | Start/stop recording; capture still photo; refresh feed | Three control buttons below the live feed. Recording saves a timestamped MP4 clip via the camera service API. Photo capture saves a JPEG. | go2rtc; camera; Pi local storage |
| **Active Camera Status Panel** | Connection state; camera name; IP address; recording status | Live status rows showing the current camera's connection health, friendly name, IP address, and whether a recording is in progress. | go2rtc (port 8084) |
| **All Cameras Grid** | 2-column thumbnail grid; all assigned slots | Overview grid showing JPEG thumbnails from every configured camera at ~0.67 fps. Sustainable Pi load design: 4 cameras × 1500 ms polling. | go2rtc (port 8084); all configured cameras |
| **Fish Detection** | AI object detection run on current frame; model info; class list; detection results | Runs the onboard ML detection model against the current camera frame. Shows model name, detection classes (fish species, marine life, vessel types), and per-class confidence results. | ML model service (port 8084 or separate detection service); camera feed; optional GPU/NPU (Hailo on Pi 5) |
| **Recent Recordings** | List of saved video clips; playback / download | Lists video files saved by the recording feature. | Pi local storage |

---

### Engine Monitor (`/engine-monitor`)

| Section | Capabilities | Description | Hardware |
|---|---|---|---|
| **Engine Section** | RPM, Oil Pressure, Coolant Temp, Trim, Battery Percentage | Live Signal K WebSocket readings for engine parameters with colour-coded status bars. Connection banner shows Signal K state. | PiCAN-M HAT → Signal K (port 8099 WS) → N2K engine bus; voltage/battery sender |
| **Tank Levels** | Fuel, Water, and additional tank percentages with visual bars | Tank level gauges from N2K tank PGNs. Visual progress bars with percentage readouts. | N2K tank sender → PiCAN-M → Signal K |
| **System Status** | CPU temp (°C), memory usage (%), disk usage (%), uptime, IP address | Raspberry Pi system health metrics polled from the d3kOS system info endpoint. Bar visualisations for CPU/memory/disk. | Pi hardware (CPU temp sensor, /proc filesystem) |
| **Network Status** | Signal K, AvNav, Gemini AI, Ollama — live dot indicators | Four service health cards showing running/stopped/available/offline state. Polled periodically. | All Pi services; LAN (Ollama at 192.168.1.36) |

---

### Helm Assistant (`/helm-assistant`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Quick Actions** | Engine Status; Run Diagnostics | Two one-tap buttons that pre-populate common queries. Engine Status fetches live Signal K readings and formats a natural-language report. Run Diagnostics generates a full engine health check with Gemini AI analysis. | Signal K (port 8099); Gemini AI (port 3001) |
| **RAG Chat** | Manual-grounded Q&A; Gemini fallback; engine/system query intercept | Chat interface that routes queries through three layers: (1) local engine/system query intercept (RPM, diagnostics — answered directly from Signal K data); (2) PDF RAG search against indexed manuals; (3) Gemini AI for anything not answered by the above. Sources shown in responses. | Gemini AI (port 3001); PDF RAG / manuals service (port 8083); Signal K (port 8099) |
| **Alert Thresholds** | Local alert evaluation (oil, coolant, RPM) | Helm evaluates engine readings against configured thresholds and can include a warning summary in the response without calling the cloud API. | Signal K (port 8099) |
| **Signal K Status Dot** | Live connection indicator in header | Shows Signal K WebSocket connection state in the page header. | Signal K (port 8099) |

---

### AI Navigation (`/ai-navigation`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Navigation Chat** | Routes; tides; weather routing; anchorages; fuel planning; customs; COLREGs references; local port info | Full-screen dedicated navigation assistant. Sends queries directly to the Gemini AI navigation service. Response sanitization prevents XSS. 60-second timeout. Includes SafeHelm global script for COLREGs alert integration. | Gemini AI service (port 3001); Internet; GPS via Signal K (position context) |
| **Service Status Pill** | READY / OFFLINE indicator | Shows whether the Gemini navigation AI is reachable. | Gemini AI service (port 3001) |

---

### Anchor Watch (`/anchor-watch`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Canvas Position Map** | Animated vessel position relative to anchor drop point; drift arc visualization | Circular canvas plot showing the vessel's current position relative to the anchor point. Drift arc drawn when outside the radius. Updates live from GPS. | GPS → Signal K |
| **Status Pill** | INACTIVE / WATCHING / ALARM states | Header pill showing current anchor watch state with colour coding (grey/green/red). | Signal K |
| **Drift Statistics** | Distance from anchor (m); current bearing (°); set radius (m) | Three stat cells below the map showing real-time drift distance, bearing from anchor, and the configured watch radius. | GPS → Signal K |
| **Radius Slider** | 10–100 m in 5 m increments | Adjustable alarm radius. Set before dropping anchor or while watching. Visual tick marks at 10 m, 50 m, 100 m. | None (configuration) |
| **Set / Clear Buttons** | Drop anchor at current position; cancel anchor watch | SET ANCHOR records the current GPS position as the anchor point and activates the watch. CLEAR cancels the watch and resets the display. | GPS → Signal K |
| **Full-Screen Drag Alarm** | Audio-visual alarm; drift distance; AI advice text; dismiss | Full-screen red alarm overlay with pulsing animation when drift exceeds the radius. Shows metres drifted and AI-generated advice on action to take. | GPS → Signal K; Gemini AI (advice text) |

---

### Boat Log (`/boat-log`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Voice Recording** | Tap-to-record voice notes; live timer; automatic transcription; transcript preview | Records a voice note via the browser microphone API. Transcription is performed server-side via the boatlog API and the transcript is displayed before submission. Entry is timestamped and stored. | USB or Pi microphone; boatlog service (port 3000) |
| **Engine Data Auto-Capture** | Automatic engine log entries from Signal K | Background service (`boatlog_capture.py`) writes engine readings (RPM, oil pressure, coolant, fuel) as periodic log entries without operator action. These appear in the entry list alongside voice notes. | Signal K (port 8099); N2K engine bus |
| **Entry List** | Chronological log; voice + engine entry types; session grouping | Scrollable list of all log entries with timestamps. Voice entries show transcript text. Engine entries show key readings at capture time. Grouped by session. | None (display) |
| **Export CSV** | Download full log as CSV | Exports all log entries to a downloadable CSV file for offline record-keeping. | Boatlog service (port 3000) |
| **Status Bar** | API health; total entry count; session count | Shows whether the boatlog API is reachable, total number of entries stored, and entries in the current session. | None (service status) |

---

### Settings (`/settings`)

| Section | Capabilities | Description | Hardware |
|---|---|---|---|
| **System Status** | Live status of all d3kOS services | Indicators for AvNav Charts, Signal K, GPS, AIS Receiver, Gemini AI, Ollama (LAN), and Internet connectivity. Test Signal K button opens a WebSocket test. | All Pi services; GPS; AIS receiver; LAN |
| **Engine Configuration** | Service interval hours; oil change interval; total engine hours; hours since last service | Fields for configuring engine maintenance thresholds. Used by the AI engine diagnostic to calculate time-to-service. | Signal K (engine hours source) |
| **Units & Display** | Distance (nm/km/mi); speed (kts/km·h/mph); temperature (°F/°C); pressure (PSI/kPa/bar); metric/imperial toggle | Per-unit selectors for all displayed values. Affects every instrument cell and engine monitor page. | None |
| **Alerts & Notifications** | Per-parameter alert thresholds | Configure warning and critical thresholds for RPM, oil pressure, coolant temperature, fuel level, and depth. Values used by both the dashboard and Helm Assistant. | None (configuration) |
| **AI Assistant — Vessel Settings** | Vessel name; home port; Gemini API key; Gemini model selection; system prompt preview | Vessel identity and AI configuration. Gemini API key is stored on the Pi only — never transmitted in queries. Model selector (flash / pro). System prompt preview shows the exact prompt sent to Gemini. | Gemini AI service (port 3001); Internet |
| **Camera Management** | Slot wizard; RTSP IP/port entry; role assignment; test connection | Camera slot configuration wizard. Discovers or manually enters camera RTSP endpoints. Assigns roles (`forward_watch`, `display_in_grid`, `stern`, etc.). Each slot tested on save. | go2rtc (port 8084); IP cameras (RTSP :554); USB/Pi cameras |
| **Data Management** | (Section present — exact controls in s-data section) | Storage and data management utilities. | Pi local storage |
| **Network & Connectivity** | (s-network section) | Network configuration and diagnostics. | LAN; Pi networking |
| **Chart Setup** | AvNav chart configuration documentation | Reference links and configuration notes for AvNav chart server setup and o-charts paid chart data. | AvNav (port 8080); SD card or USB storage for chart files |
| **OpenPlotter & System Infrastructure** | Infrastructure reference | Documentation links for OpenPlotter, SignalK, and Pi system infrastructure used as the foundation for d3kOS. | Pi OS; Signal K; OpenPlotter |
| **System Actions** | Restart services; reboot Pi | Buttons to restart d3kOS services or reboot the Pi from the UI. | Pi OS (systemd) |
| **System Information** | Software version; device UUID; tier; build date | Displays the installed d3kOS version, the Pi's device UUID (used for AtMyBoat.com pairing), and the active tier. | Pi identity files; license service |
| **License & Tier** | Current tier display; upgrade prompt | Shows the active tier (T0–T3) with feature unlock status. Links to atmyboat.com for upgrade. | AtMyBoat.com heartbeat / pairing; Internet |

---

### Initial Setup Wizard (`/setup`)

| Step | Capabilities | Description | Hardware |
|---|---|---|---|
| **Password Change** (Step 0, if factory default) | Forced password update before wizard proceeds | If the factory default password is detected, the wizard gates on a mandatory password change before any other step. | None |
| **Welcome & Overview** (Step 1) | Wizard introduction; run-count display (Tier 0 limited); recovery mode | Introduces the wizard, shows how many times it has been run (Tier 0 limited), and provides a restore-from-token panel for recovery scenarios. | Internet (recovery token check) |
| **Vessel Name & Home Port** (Step 2) | Vessel name entry; home port entry | Sets the vessel name and home port used in AI prompts and the status bar. | None |
| **Engine & Region** (Step 3) | Engine type selection; region selection | Determines the NMEA 2000 DIP switch configuration and AI response context (e.g. fuel/measurement units, local regulations). | None |
| **N2K DIP Switch Guide** (Step 4) | Auto-generated CX5106 wiring diagram | Generates a CX5106 NMEA 2000 gateway DIP switch configuration diagram based on the engine type and region selected in Step 3. | CX5106 NMEA 2000 gateway (physical hardware config) |
| **AI First Officer Setup** (Step 5) | Gemini API key entry; model selection | Configures the Gemini API key and selected model for the AI First Officer. Key is stored locally on the Pi. | Gemini AI service (port 3001); Internet |
| **Camera Setup** (Step 6) | RTSP camera entry; role assignment | Quick-entry for camera RTSP URLs and role assignment during first run. Full camera management available in Settings. | IP cameras (RTSP); go2rtc |
| **Mobile Companion Pairing** (Step 7) | QR code display; device UUID copy | Shows the Pi's device UUID as a QR code and copy-able text for pairing with the AtMyBoat.com mobile PWA. | Internet; atmyboat.com; mobile device (PWA) |
| **Complete** (Step 8) | Wizard summary; launch dashboard | Confirms setup is complete and redirects to the main dashboard. | None |

---

### Upload Documents (`/upload-documents`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **PDF Upload** | File picker; document type classification; upload to Pi | Uploads a PDF manual from the operator's device to the Pi. Document type (engine manual, electronics, safety, charts, general) is selected to provide AI context. | No physical hardware; manuals service (port 8083) |
| **RAG Indexing** | Vector embedding; Chroma vector store; progress bar | After upload, the document is chunked and embedded into the onboard Chroma vector database using Gemini embeddings. Progress bar shows indexing status. Used by Helm Assistant for grounded answers. | Gemini embeddings API; manuals service (port 8083); Pi storage |

---

### Manage Documents (`/manage-documents`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **Document List** | View all indexed PDFs; file name and size | Fetches the list of uploaded manuals from the manuals service. Displays each with its filename. | Manuals service (port 8083); Pi storage |
| **Delete Document** | Permanent deletion with confirmation modal | Removes a manual from the RAG index and Pi storage. Requires tap-through confirmation ("will be permanently deleted"). | Manuals service (port 8083) |

---

### 3D Surround View (`/3d`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **3D View** | Planned: 360° surround camera view | Reserved page. Currently shows "3D view — coming in a future release." Design calls for a multi-camera composite 360° view of the vessel's surroundings with AI detection overlay. | Planned: 3–4 IP/USB cameras; go2rtc; ML detection model; optional GPU/NPU (Hailo HAT+) |

---

### Help / Manual (`/manual`)

| Feature | Capabilities | Description | Hardware |
|---|---|---|---|
| **User Manual** | In-app reference documentation | Static d3kOS user guide covering features, setup, and troubleshooting steps. No external dependency. | None |

---

## Hardware Dependency Summary

| Hardware | Features That Use It |
|---|---|
| **Raspberry Pi 4 or Pi 5** | All features |
| **GPS module (via NMEA or Signal K)** | Nav ribbon (speed, depth, course, position, waypoint), Anchor Watch, Weather tab position, Port Arrival, AI Navigation context, Boat Log engine entries |
| **PiCAN-M HAT (CAN bus to Pi)** | Engine ribbon (RPM, trim, oil, coolant, fuel), Tank Levels, Engine Monitor, Boat Log engine capture, Engine Diagnostic, Critical Alert |
| **N2K Engine Bus (NMEA 2000)** | All engine data, tank levels, depth (if N2K depth sounder) |
| **Depth Sounder (N2K or NMEA 0183)** | Depth cell in Nav ribbon |
| **CX5106 NMEA 2000 Gateway** | Setup Wizard DIP switch guide; initial N2K bus configuration |
| **AIS Receiver (via Signal K port 10110)** | AI Alert Card (CPA warnings), AvNav AIS overlay, Ticker tape alerts |
| **IP Camera(s) — RTSP** | Marine Vision live feed, Forward Watch, Camera Grid, Fish Detection, Cameras tab |
| **USB or Pi Camera** | Marine Vision, Forward Watch, 3D Surround (future) |
| **go2rtc service (port 8084)** | All camera features |
| **USB Microphone** | Helm Listening Overlay, Voice query in AI Nav tab, Boat Log voice recording, Helm voice assistant |
| **Anker PowerConf S330 (or USB mic)** | Helm voice assistant audio I/O (voice assistant speaks back) |
| **Gemini API (cloud, port 3001 locally)** | Helm Assistant RAG fallback, AI Navigation, Engine Diagnostic AI, Route AI Strip, Anchor Watch advice, Port Arrival briefing, AI Alert Card, PDF embeddings |
| **Ollama LAN (192.168.1.36:11434)** | Helm Assistant offline fallback when Gemini is unavailable |
| **Internet connection** | Windy weather embed, Gemini AI, OTA updates, AtMyBoat.com heartbeat, AIS Hub (if community AIS enabled) |
| **AvNav (port 8080)** | Main chart area, waypoint/route data for Nav ribbon |
| **Signal K (port 8099)** | All instrument data (engine, nav, GPS, AIS, depth, tanks) |
| **Hailo AI HAT+ (Pi 5 only — optional)** | Fish Detection / Marine Vision ML inference acceleration (D30/D31 — not yet enabled) |
| **AtMyBoat.com / heartbeat** | Tier enforcement, mobile PWA pairing, OTA update delivery, License & Tier display |

---

*Document generated from live dashboard template source. Update when new pages or instrument cells are added.*
