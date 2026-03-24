# d3kOS User Manual
## Version 0.9.2.2 — Release Candidate

**System:** d3kOS — AI-powered marine navigation hub
**Hardware:** Raspberry Pi 4, 10.1" touchscreen, 1280×800
**Document version:** 1.0.0 — March 23, 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Initial Setup Wizard](#2-initial-setup-wizard)
3. [Main Dashboard](#3-main-dashboard)
4. [Weather Panel](#4-weather-panel)
5. [Marine Vision — Camera System](#5-marine-vision--camera-system)
6. [Engine Dashboard](#6-engine-dashboard)
7. [Helm Assistant — AI Chat](#7-helm-assistant--ai-chat)
8. [Boat Log](#8-boat-log)
9. [Settings](#9-settings)
10. [Remote Access](#10-remote-access)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Introduction

d3kOS is a marine navigation hub that runs on a Raspberry Pi mounted at your helm. It integrates chart navigation (AvNav), engine monitoring (NMEA 2000 via Signal K), AI-powered vessel assistance (Helm), camera monitoring (Marine Vision), weather overlays, and a boat log — all accessible from a single touchscreen interface.

**What d3kOS is not:** it is not a standalone chartplotter. It works alongside your existing MFD and VHF radio. It adds an AI intelligence layer and centralized monitoring that your MFD does not provide.

### First Boot

On first power-up, d3kOS launches the **Setup Wizard** automatically. Complete all 8 steps before the main dashboard becomes accessible. The wizard saves your vessel, engine, and electronics configuration — the AI uses this information to provide accurate diagnostics and advice specific to your boat.

The wizard can be re-run at any time from **Settings → System → Initial Setup Reset** (requires triple confirmation — contact support).

---

## 2. Initial Setup Wizard

The wizard runs once at first boot. It has 8 steps indicated by dots at the top of the card. Your progress is saved automatically — if you close the browser, it resumes where you left off.

A **← Back** button appears on every step from Step 2 onward. Use it to review and correct previous entries before moving forward.

---

### Step 1 — Welcome

**Screen title:** Your marine navigation hub

This screen introduces d3kOS. No data entry required.

**Button:** `GET STARTED ›` — advances to Step 2.

---

### Step 2 — Vessel Information

**Screen title:** Tell us about your vessel

This step captures your vessel identity. The Vessel Name field is required (marked with a red asterisk). All other fields are optional but improve AI accuracy.

| Field | What to enter | Example |
|-------|---------------|---------|
| **Vessel Name** *(required)* | Your boat's registered name | `MV Serenity` |
| **Home Port** | Marina or harbour you return to | `Kingston, ON` |
| **Dashboard Language** | UI language for the dashboard | English (Canada), English (US), French, etc. |
| **Manufacturer** | Boat builder name | `Regal`, `Sea Ray`, `Bayliner` |
| **Year** | Model year of your vessel | `2019` |
| **Model** | Specific model name or number | `2600`, `3260 XO` |
| **Length (ft)** | Vessel length overall | `26` |
| **Boat Type** | Type selector | Bowrider, Cruiser, Sailboat, etc. |
| **Region Sold** | Where the boat was sold | Canada, USA, Europe |

At the bottom of Step 2 you will see a **Free Charts Configured** indicator. This confirms that open-source chart streaming (OpenStreetMap marine tiles via AvNav) is ready. Charts stream live when internet is connected; previously-viewed areas are cached for offline use.

**Button:** `NEXT ›` — validates that Vessel Name is filled in, then advances to Step 3.

---

### Step 3 — Engine Configuration

**Screen title:** Engine configuration

Enter your engine details. The AI uses make, model, and RPM range to interpret engine data from your NMEA 2000 gateway accurately.

**Single engine fields:**

| Field | What to enter | Example |
|-------|---------------|---------|
| **Make** | Engine manufacturer | Mercruiser, Volvo Penta, Yanmar, Yamaha |
| **Year** | Engine model year | `2018` |
| **Model / Spec** | Full model designation | `5.0L MPI Alpha`, `4JH4-HTE` |
| **Horsepower** | Rated HP | `220` |
| **Cylinders** | Number of cylinders | 4, 6, 8 |
| **Fuel Type** | Gasoline or Diesel | Gasoline |
| **Induction** | How air enters the engine | Naturally Aspirated, Turbocharged, Supercharged |
| **Idle RPM** | Normal warm idle speed | `700` |
| **Max RPM (WOT)** | Wide-open throttle limit | `4800` |

**Twin engine:** A toggle switch enables a second engine block with the same fields. Port and starboard engines can have different makes and specs if needed.

**Button:** `NEXT ›` — advances to Step 4.

---

### Step 4 — Nav Gear & NMEA Gateway

**Screen title:** Nav gear & NMEA gateway

This step records your electronics and the NMEA gateway model. d3kOS reads engine and instrument data through your gateway — knowing the exact model ensures DIP switch instructions in Step 5 are correct.

| Field | What to enter | Example |
|-------|---------------|---------|
| **Chart Plotter / MFD** | Your existing chartplotter | `Garmin GPSMAP 1242xsv` |
| **VHF Radio** | Your VHF | `Standard Horizon GX2400` |
| **Gateway Model** | NMEA 2000 to NMEA 0183 gateway | `Actisense NGT-1`, `Yacht Devices YDNG` |
| **Fuel / Level Sender Standard** | Resistance standard for your tank senders | US Standard (240–33Ω), European (0–190Ω) |

**Button:** `NEXT ›` — advances to Step 5.

---

### Step 5 — NMEA Gateway DIP Switches

**Screen title:** NMEA Gateway DIP Switches

This step generates a custom DIP switch configuration diagram for your CX5106 NMEA gateway based on what you entered in Step 4. The diagram shows the exact switch positions for your specific engine setup.

**How to read the diagram:**

The CX5106 has two rows of switches:
- **Row 1** — 8 switches (left to right: 1 through 8) — controls NMEA sentence output, baud rate, and data routing
- **Row 2** — 2 switches — controls engine channel assignment for twin-engine installations

Each switch is shown as either **ON** (raised/up) or **OFF** (lowered/down).

**For twin-engine setups:** port and starboard switch positions are shown separately. Set Row 2 switches exactly as shown — incorrect positions will cause engine data to be assigned to the wrong engine slot in d3kOS.

**Why text:** Below the diagram, the "WHY THESE SETTINGS" section explains in plain language what each active switch does. Read this before setting switches so you understand the purpose of each position.

**Installation warning:** The gateway must be powered off before changing DIP switches. Changes take effect on next power-up.

**Gateway notices:** If your gateway model is not CX5106, a notice appears explaining that the diagram is a reference — consult your gateway manual for the equivalent settings.

**Button:** `NEXT ›` — advances to Step 6.

---

### Step 6 — Connect Your Mobile Phone

**Screen title:** Connect your mobile phone

This step pairs your phone with d3kOS for the companion mobile app (d3kOS Mobile — v0.9.4, coming soon).

A QR code is displayed on screen. Scan it with your phone camera to complete pairing. The QR code encodes your vessel's unique device token — this token links your phone to your specific d3kOS installation.

If you do not have the mobile app yet, tap **SKIP THIS STEP** — you can pair your phone later from Settings → Mobile.

**Button:** `NEXT ›` — advances to Step 7.

---

### Step 7 — Gemini API Key

**Screen title:** Gemini API Key

d3kOS uses Google Gemini AI for the Helm Assistant, engine diagnostics, and document analysis. A free API key is required.

**How to get your key:**
1. On a phone or computer, open a browser and go to `aistudio.google.com`
2. Sign in with a Google account
3. Click **Get API Key** → **Create API key**
4. Copy the key (it starts with `AIza`)

| Field | What to enter |
|-------|---------------|
| **Gemini API Key** | Paste your key from Google AI Studio |

The key is stored locally on your Pi — it never leaves your network except when making AI queries directly to Google's servers.

If you do not have a key yet, tap **SKIP THIS STEP** — Helm Assistant will be disabled until the key is added in Settings → AI Configuration.

**Button:** `NEXT ›` — advances to Step 8.

---

### Step 8 — Ready to Set Sail

**Screen title:** Ready to set sail

All configuration is complete. This screen summarises what was set up and confirms the system is ready.

**Button:** `LAUNCH d3kOS ›` — saves all wizard data to your vessel configuration file and loads the main dashboard.

---

## 3. Main Dashboard

The main dashboard is the primary screen you use underway. It shows live instrument data, navigation, and provides access to all features.

### Instrument Grid

The dashboard displays real-time data in instrument cells arranged in a grid. Each cell shows a primary value, a unit label, and status colour coding.

| Cell | Data source | What it shows |
|------|-------------|---------------|
| **Speed** | Signal K / NMEA 2000 | Speed over ground in knots |
| **Course** | Signal K / NMEA 2000 | Course over ground, true degrees |
| **Position** | Signal K / NMEA 2000 | Lat/Lon in degrees and decimal minutes |
| **Depth** | Signal K / NMEA 2000 | Depth below keel in metres |
| **Coolant Temp** | Signal K / NMEA 2000 | Engine coolant temperature in °C |
| **Oil Pressure** | Signal K / NMEA 2000 | Engine oil pressure in PSI |
| **Next Waypoint** | AvNav | Distance (nm), bearing (°T), and ETA to active waypoint |
| **Wind** | Signal K / NMEA 2000 | Wind speed and direction (if transducer connected) |
| **Fuel** | Signal K / NMEA 2000 | Fuel level percentage (if sender connected) |
| **Voltage** | Signal K / NMEA 2000 | House bank voltage |

**Cell colour states:**
- **Normal** — white/grey — within acceptable range
- **Advisory** — amber — approaching a threshold — monitor closely
- **Alert** — orange — threshold exceeded — take action
- **Critical** — red — critical limit reached — stop and investigate

When a critical alert fires, a red banner appears at the bottom of the screen with a plain-language message (e.g. `⛔ CRITICAL — COOLANT 108°C — REDUCE RPM NOW`).

Tapping a coolant or oil pressure cell while in alert state opens the **AI Engine Diagnostic** overlay — Helm analyses the sensor readings and provides a specific recommendation for your engine.

---

### Navigation Bar (Bottom)

Six buttons run across the bottom of the screen:

| Button | Action |
|--------|--------|
| **Dashboard** (house icon) | Returns to instrument grid from any sub-screen |
| **Weather** | Opens the Weather panel (Windy wind/wave map + Radar) |
| **Marine Vision** | Opens the camera grid |
| **HELM** | Opens the Helm AI listening overlay |
| **Boat Log** | Opens the Boat Log |
| **More ⋮⋮** | Opens the secondary menu |

**HELM** is the large centre button — it protrudes above the navigation bar. Tap it once to start a voice conversation with your AI First Mate. Tap again to stop listening.

---

### More Menu

The More menu provides access to secondary features:

| Item | Opens |
|------|-------|
| **Engine** | Engine Dashboard (full engine instrument panel) |
| **AvNav** | Chart navigation (AvNav embedded) |
| **Settings** | System settings page |
| **Documents** | Upload and manage vessel manuals and documents |
| **Remote Access** | Remote monitoring status |

---

### Weather Conditions Panel

A slide-out panel on the left edge of the dashboard shows current conditions:
- Wind speed and direction
- Temperature and barometric pressure
- Sea state summary

Tap the **WX** button (or swipe from the left edge) to open/close it. This panel reads from Signal K when underway. When the vessel is docked and internet is available, it pulls from online weather services.

---

## 4. Weather Panel

The Weather panel provides two full-screen weather views:

### Windy (Wind & Wave Map)

An embedded Windy.com map showing wind speed, direction, and wave height overlays for your region. The map is centred on your current GPS position when a fix is available.

- **Zoom:** pinch to zoom, drag to pan
- **Overlay:** defaults to wave height — tap the map menu to switch to wind, pressure, rain, etc.
- **Units:** wind in knots, temperature in °C

Requires internet connection. Displays "Offline — internet not available" when offline.

### Radar

An embedded RainViewer radar map showing precipitation in your area. Animated — shows the last 2 hours of radar frames.

Requires internet connection.

### Switching Tabs

Two tabs at the top of the weather screen: **WINDY** and **RADAR**. Tap to switch. Both maps are lazy-loaded — they download only when first opened.

---

## 5. Marine Vision — Camera System

Marine Vision manages your onboard cameras. It provides live feeds, recording, and AI-powered fish detection.

### Camera Grid

The main Marine Vision screen shows a grid of all configured camera slots. Each cell displays:
- **Live feed** (if camera is connected and streaming)
- **Camera name** (as assigned in Settings → Cameras)
- **Status indicator** — green dot (live), amber (connecting), red (offline)

Tap any camera cell to open it full-screen. In full-screen view:
- Pinch to zoom
- **Record** button starts/stops clip recording for that camera
- **Back** returns to the grid

### Camera Slots

Cameras are assigned to named slots (e.g. Bow, Stern, Port, Starboard, Helm). Slot names are set in Settings → Cameras. Up to 8 slots are supported.

Slots without a physical camera assigned show a placeholder with the slot name.

### Fish Detection

When a camera is active, d3kOS runs an AI model (YOLOv8-based) in the background looking for fish in the frame. When a fish is detected:
1. A **FISH DETECTED** banner appears over the camera feed
2. The species identification system queries the AI with a frame capture
3. Species name, common name, and habitat notes appear in the detection panel
4. The detection is logged with timestamp, species, and confidence level

Fish detection runs at low priority — it does not affect camera stream performance.

### Recordings

Camera clips are stored on the Pi's SD card at `/home/d3kos/camera-recordings/`. Each clip is named with camera slot and timestamp. Manage storage from Settings → Cameras → Storage.

---

## 6. Engine Dashboard

The Engine Dashboard provides a full-screen instrument panel dedicated to engine monitoring.

### Engine Gauges

All values are read live from your NMEA 2000 network via Signal K:

| Gauge | Units | Normal range |
|-------|-------|-------------|
| **RPM** | Revolutions per minute | Varies by engine (see your manual) |
| **Coolant Temperature** | °C | 75–95°C typical inboard |
| **Oil Pressure** | PSI | 40–80 PSI at operating temp (varies by engine) |
| **Alternator Voltage** | V | 13.8–14.4V when charging |
| **Fuel Flow** | L/hr or GPH | Varies by throttle |
| **Hours** | Total engine hours | Cumulative |
| **Trim** | Degrees | 0° = full down |

For twin-engine setups, port and starboard gauges are displayed side by side.

### Alert Thresholds

Colour coding follows the same system as the main dashboard (normal / advisory / alert / critical). Thresholds are set in Settings → Engine Alerts.

### AI Engine Diagnostic

Tap the **AI DIAGNOSTIC** button to send current engine readings to Helm for analysis. Helm will assess the data against your engine's specification (entered in the Setup Wizard) and provide a plain-language status report or recommended action.

This is most useful when you see an unusual reading and want a second opinion before deciding whether to head in.

---

## 7. Helm Assistant — AI Chat

Helm is your AI First Mate. It understands your vessel, your engine, your location, and the current state of your instruments.

### Starting a Conversation

**Voice:** Tap the **HELM** button on the navigation bar. The "HELM IS LISTENING" overlay appears. Speak naturally — Helm uses Vosk for speech recognition (runs locally, no internet required for transcription). Piper TTS reads the response aloud through the Pi's audio output.

**Text:** In the Helm Assistant page (accessible from More menu), type your question in the input field and tap **Send**.

### What You Can Ask

Helm has context about:
- Your vessel name, type, engine, and specifications
- Current GPS position, speed, and course
- Current engine readings (coolant, oil pressure, RPM, etc.)
- Active navigation route and next waypoint
- Your boat log entries

**Example questions:**
- *"What's my ETA to the next waypoint at current speed?"*
- *"My coolant is running at 98°C — is that normal for my engine?"*
- *"How far have I travelled today?"*
- *"Summarise my engine hours since last service."*
- *"What should I check if my oil pressure drops below 40 PSI?"*
- *"Tell me about this morning's boat log entries."*

### Mute / Pause

Tap the **mute** button (speaker icon, top-right of Helm screen) to toggle TTS voice response on or off. When muted, Helm still responds — text only, no audio.

Helm automatically pauses when you are recording a voice note in the Boat Log — it resumes after the recording completes.

### Documents

Helm can answer questions about documents you have uploaded (vessel manuals, engine manuals, coast guard guides). See Settings → Documents for how to upload.

---

## 8. Boat Log

The Boat Log is your onboard journal. It records engine data snapshots, voice notes, text entries, and exports to CSV or JSON for your records.

### Adding a Voice Note

1. Tap **Boat Log** in the navigation bar
2. Tap the **microphone** button
3. Speak your note — the recording stops automatically after a pause, or tap the button again to stop manually
4. Helm transcribes the note using Vosk (runs locally — no internet required)
5. The transcribed text appears and is saved automatically

Voice notes are saved with a timestamp. The transcription is stored in the database and appears in exports.

### Adding an Engine Entry

Engine data is captured automatically every 30 minutes when the engine is running. A snapshot includes: RPM, coolant temperature, oil pressure, voltage, and fuel flow at the time of capture.

Engine entries also trigger on significant events — if coolant exceeds the advisory threshold, an entry is written automatically with the sensor readings and a flag.

### Viewing Entries

Entries appear in reverse chronological order. Each entry shows:
- Timestamp
- Entry type (voice note / engine snapshot / manual entry / alert)
- Content (transcription text or data values)

Tap any entry to expand it and see full details.

### Exporting

Tap **Export** to download your log:
- **CSV** — spreadsheet-compatible, includes all entry types and unit metadata
- **JSON** — full structured data for archiving or importing into other systems

Exports include your unit preferences (metric or imperial) in the metadata header so data is always interpretable.

---

## 9. Settings

Settings is a full-page screen accessible from the **More** menu. It is organised into sections.

### Engine Settings

| Control | Function |
|---------|----------|
| **Service Interval** | Hours between scheduled service events |
| **Oil Change Interval** | Hours between oil changes |
| **Total Engine Hours** | Cumulative hours (editable for initial setup) |
| **Hours Since Last Service** | Resets when service is performed |
| **Save Engine Settings** | Writes values to configuration |
| **Reset Service Counter** | Zeros the hours-since-service counter |

### Display & Units

| Control | Function |
|---------|----------|
| **Distance** | Nautical miles or kilometres |
| **Speed** | Knots or km/h |
| **Temperature** | Celsius or Fahrenheit |
| **Pressure** | PSI, kPa, or bar |
| **Save Display Settings** | Applies unit preferences across all screens |

### Alert Thresholds

Set advisory, alert, and critical limits for:
- Coolant temperature
- Oil pressure
- Depth below keel
- Voltage (low)

Default values are set from your engine specification. Adjust only if your engine manual specifies different operating limits.

### Vessel Profile

| Control | Function |
|---------|----------|
| **Vessel Name** | Updates the displayed vessel name |
| **Home Port** | Updates home port |
| **Save Vessel Settings** | Writes to vessel configuration file |

### AI Configuration (Gemini)

| Control | Function |
|---------|----------|
| **Gemini API Key** | Enter or update your Google AI Studio key |
| **Voice Responses** | Toggle TTS on/off globally |
| **Auto-Diagnose Alerts** | Toggle automatic AI analysis when alert fires |
| **Save Configuration** | Writes API key and settings |

### Data Management

| Button | Function |
|--------|----------|
| **Export All Data** | Downloads complete boat log, engine data, and trip history as ZIP |
| **Clear Trip Data** | Deletes all trip/voyage records (requires confirmation) |
| **Clear Benchmarks** | Deletes engine benchmark history (requires confirmation) |

### Cameras

Camera slot management:
- **Add Slot** — define a named camera position (Bow, Stern, Port, Starboard, etc.)
- **Assign Camera** — link a discovered hardware camera to a slot
- **Unassign** — remove a camera from a slot without deleting the slot
- **Storage** — view recording storage usage, set maximum storage limit

Camera list is fetched live from the camera service — never shows stale/hardcoded data.

### Remote Access

Shows current status of the remote monitoring connection. See Section 10.

### System

| Button | Function |
|--------|----------|
| **Reboot System** | Restarts the Pi (requires confirmation) |
| **Initial Setup Reset** | Clears all wizard configuration and relaunches the wizard (requires triple confirmation — contact support before using) |
| **Visit AtMyBoat.com** | Opens AtMyBoat.com in a new tab (requires internet) |

---

## 10. Remote Access

The Remote Access page shows the status of d3kOS's connection to the AtMyBoat.com monitoring service.

When connected, AtMyBoat.com receives:
- Vessel name and last known GPS position
- System health status (services running/stopped)
- Periodic engine data summaries (no raw readings — summaries only)

**Status indicators:**
- **Connected** — green — data is flowing to AtMyBoat.com
- **Offline** — amber — Pi has no internet, data queued for next connection
- **Disconnected** — red — connection error, check network settings

The status updates in real time via a server-sent events (SSE) stream — no page refresh required.

**Privacy:** GPS coordinates are sent as last-known position only, not a live track. You control what data is shared in Settings → Remote Access.

---

## 11. Troubleshooting

### Dashboard doesn't load / shows blank screen

1. On the Pi, check that the d3kOS dashboard service is running
2. The dashboard runs at `http://localhost:3000` — Chromium connects directly to Flask
3. If you changed a template file and restarted, allow 30 seconds for Flask to start

### Instrument cells show "---"

Signal K is not receiving data from your NMEA gateway:
1. Check that the gateway is powered on and connected to the Pi via USB or serial
2. Check Signal K server status at `http://[pi-ip]:8099/admin`
3. Verify baud rate matches your gateway DIP switch setting (Step 5 of wizard)

### Next Waypoint shows "No active route"

No route is active in AvNav:
1. Open AvNav from the More menu
2. Load a route and tap Activate
3. Return to the dashboard — the waypoint cell updates within 15 seconds

### GPS position not showing

1. Ensure your GPS source is connected and transmitting to Signal K
2. If indoors, GPS will not get a fix — this is normal. Go outside or to an area with sky view
3. Check Signal K data browser for `navigation.position` — if it shows `null`, the GPS source is not connected

### Helm Assistant not responding / no voice

1. Check that the Gemini API key is set in Settings → AI Configuration
2. Check the microphone — tap Helm and say something. If the waveform shows no input, check the USB microphone is plugged in and not muted
3. For TTS silence, check that the Pi audio output is not muted (Settings → AI Configuration → Voice Responses)

### Camera shows "Connecting" / offline

1. Check that the camera USB or RTSP source is connected
2. Restart the camera service: Settings → System → Reboot, or contact support
3. Check camera slot assignment in Settings → Cameras — the slot may not have a camera assigned

### Fish detector not activating

Fish detection requires an active camera stream. If the camera is connecting or offline, detection is suspended. Once the camera stream is live, detection resumes automatically.

### Touch keyboard not appearing

The on-screen keyboard (Squeekboard) appears automatically when you tap any text input field. If it does not appear:
1. Tap the text field again — sometimes a second tap is needed on first load
2. The keyboard may be behind the main window — check if it appears at the bottom of the screen

### System time is wrong after reboot

The Pi has no hardware clock. Time is set by NTP when internet is available (usually within 1–2 minutes of network connection). If you are offline, `fake-hwclock` keeps time approximate between reboots.

---

## Quick Reference Card

| Feature | How to access | Requires internet |
|---------|--------------|-------------------|
| Instrument data | Main dashboard | No |
| Chart navigation | More → AvNav | No (cached charts) |
| Wind/wave map (Windy) | Weather → Windy tab | Yes |
| Radar | Weather → Radar tab | Yes |
| Camera feeds | Marine Vision | No |
| Fish detection | Automatic when cameras active | No |
| AI Helm | HELM button (voice or text) | Yes (Gemini API) |
| Engine diagnostics | Engine cell tap or Engine Dashboard | Yes (Gemini API) |
| Boat log voice note | Boat Log → microphone | No |
| Data export | Boat Log → Export | No |
| Settings | More → Settings | No |

---

*d3kOS v0.9.2.2 — AtMyBoat.com — For support: atmyboat.com*
