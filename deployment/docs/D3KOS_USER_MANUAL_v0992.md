# d3kOS User Manual
## Version 0.9.9.3

**System:** d3kOS — AI-powered marine navigation hub
**Hardware:** Raspberry Pi 4, 10.1" touchscreen, 1280×800
**Document version:** 2.2.0 — April 12, 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Initial Setup Wizard](#2-initial-setup-wizard)
3. [Main Dashboard](#3-main-dashboard)
4. [Weather Panel](#4-weather-panel)
5. [Marine Vision — Camera System](#5-marine-vision--camera-system)
6. [Engine Dashboard & Predictive Maintenance](#6-engine-dashboard--predictive-maintenance)
7. [Helm Assistant — AI Chat](#7-helm-assistant--ai-chat)
8. [Boat Log](#8-boat-log)
9. [Mobile Companion App](#9-mobile-companion-app)
10. [Fix My Pi & OTA Updates](#10-fix-my-pi--ota-updates)
    - [Config Backup & Recovery (T1+)](#config-backup--recovery-t1)
11. [Fleet Management (T3)](#11-fleet-management-t3)
12. [Settings](#12-settings)
13. [Remote Access](#13-remote-access)
14. [Autonomous Health System](#14-autonomous-health-system)
15. [Troubleshooting](#15-troubleshooting)
16. [Quick Reference Card](#16-quick-reference-card)

---

## 1. Introduction

d3kOS is a marine navigation hub that runs on a Raspberry Pi mounted at your helm. It integrates chart navigation (AvNav), engine monitoring (NMEA 2000 via Signal K), AI-powered vessel assistance (Helm), camera monitoring (Marine Vision), weather overlays, predictive maintenance, and a boat log — all accessible from a single touchscreen interface.

**What d3kOS is not:** it is not a standalone chartplotter. It works alongside your existing MFD and VHF radio. It adds an AI intelligence layer and centralised monitoring that your MFD does not provide.

### Service Tiers

d3kOS has four service tiers. Your tier determines which features are active:

| Tier | Cost | What it adds |
|------|------|-------------|
| **T0 — Base** | Free forever | Full local dashboard — GPS, engine, voice, cameras, AI. No account required. 100% offline capable. |
| **T1 — Mobile** | Free with account | T0 + mobile companion app, QR pairing, cloud sync, remote monitoring |
| **T2 — Premium** | $9.99/month | T1 + AI performance analysis, predictive maintenance alerts, OTA software updates, PDF reports |
| **T3 — Professional** | $99.99/year | T2 + unlimited boats (fleet), fleet-wide analytics, priority support |

Tier is shown at the top of the Settings page. Upgrade at **atmyboat.com/pricing**.

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

### Step 6 — Pair Your Phone

**Screen title:** Connect your mobile phone

This step pairs your phone with d3kOS for the companion mobile app (available at **atmyboat.com/app**).

A QR code is displayed on screen. To pair:

1. On your phone, open **atmyboat.com/app** in a browser
2. Log in or create your free AtMyBoat account
3. Tap **Pair Device** and scan the QR code shown on your Pi screen
4. Pairing completes automatically — you will see a confirmation on both screens

The QR code encodes your vessel's unique device token — this token links your account to your specific d3kOS installation. Each Pi has one token, assigned for life.

**If you skip this step:** tap **SKIP THIS STEP** — you can pair later from **Settings → Mobile → Pair Device**. You will need internet access on both the Pi and your phone to pair.

**T0 users:** pairing requires an AtMyBoat account (free). T0 mode is fully offline without pairing — pairing is only needed if you want the mobile app or cloud sync.

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

When a critical alert fires, a red ticker banner appears at the bottom of the screen with a plain-language message (e.g. `⛔ CRITICAL — COOLANT 108°C — REDUCE RPM NOW`). Helm speaks the alert aloud through the Pi's speakers.

Tapping a coolant or oil pressure cell while in alert state opens the **AI Engine Diagnostic** overlay — Helm analyses the live sensor readings and provides a specific recommendation for your engine model.

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
| **AI Navigation** | Marine AI assistant |
| **Engine Dashboard** | Full engine instrument panel |
| **Helm Assistant** | Engine diagnostics & AI chat |
| **Initial Setup** | Vessel configuration wizard |
| **Upload Documents** | Add manuals & PDFs for Helm to reference |
| **Manage Documents** | View & delete uploaded files |
| **Settings** | System settings page |
| **Help / Manual** | This user guide — all 16 sections |

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

### Forward Watch — AI Collision Avoidance

A bow-mounted camera can be configured as a **Forward Watch** camera. When enabled, d3kOS analyses the forward video feed in real time using computer vision trained on marine objects.

When a hazard is detected ahead (approaching vessel, person in water, kayak, debris):
- A **HAZARD DETECTED** alert fires on the dashboard
- The object type and estimated distance are displayed
- GPS coordinates are pushed to your chartplotter as an AIS-like target

Forward Watch is a safety aid — it does not replace a proper watch or VHF radio.

### Recordings

Camera clips are stored on the Pi's SD card at `/home/d3kos/camera-recordings/`. Each clip is named with camera slot and timestamp. Manage storage from Settings → Cameras → Storage.

---

## 6. Engine Dashboard & Predictive Maintenance

The Engine Dashboard provides a full-screen instrument panel dedicated to engine monitoring, combined with AI-powered predictive maintenance that watches your engine trends over time.

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

**Available on T2 and T3 only.** Tap any engine cell (coolant, oil pressure, RPM, voltage, fuel) or tap the **AI DIAGNOSTIC** button on the Engine Dashboard to open the diagnostic panel. Helm reads your live sensor readings, compares them against your engine's specification from the Setup Wizard, and provides a plain-language status report and recommended action.

The panel shows:
- A card for each sensor reading with value and status colour
- A Gemini AI assessment with specific recommendations for your engine model

This is most useful when you see an unusual reading and want a second opinion before deciding whether to head in. T0 and T1 users see an upgrade prompt instead.

### Predictive Health Panel

The Predictive Health section (bottom of the Engine Dashboard) shows your engine's long-term trend data:

| Cell | What it shows |
|------|--------------|
| **Advisory Events** | Count of advisory-level threshold crossings this month |
| **Critical Events** | Count of critical-level events this month |
| **Last Event** | Type and timestamp of the most recent alert |
| **Trend** | AI assessment of your engine's health trend (Stable / Declining / Improving) |

**How predictive maintenance works:** d3kOS logs every engine data snapshot to a local database. The predictive maintenance service analyses these logs continuously. When it detects a pattern that suggests a developing problem — such as coolant temperature trending upward over multiple sessions, or oil pressure gradually declining — it fires a predictive alert before the reading reaches a threshold.

Predictive alerts appear on the dashboard ticker and are spoken by Helm. They are also sent to your phone via the mobile app (T1+) and logged in your AtMyBoat account.

**Example predictive alert:** *"Coolant temperature has averaged 4°C higher than your baseline over the last 3 sessions. Recommend checking coolant level and inspecting the raw water impeller before your next voyage."*

---

## 7. Helm Assistant — AI Chat

Helm is your AI First Mate. It understands your vessel, your engine, your location, and the current state of your instruments.

### Starting a Conversation

**Voice:** Tap the **HELM** button on the navigation bar. The "HELM IS LISTENING" overlay appears. Speak naturally — Helm uses Vosk for speech recognition (runs locally, no internet required for transcription). Piper TTS (Amy — female voice) reads the response aloud through the Pi's speakers.

**Text:** In the Helm Assistant page (accessible from More menu), type your question in the input field and tap **Send**.

### What You Can Ask

Helm has context about:
- Your vessel name, type, engine, and specifications
- Current GPS position, speed, and course
- Current engine readings (coolant, oil pressure, RPM, etc.)
- Active navigation route and next waypoint
- Your boat log entries
- Documents you have uploaded (vessel manuals, engine guides, regulations)

**Example questions:**
- *"What's my ETA to the next waypoint at current speed?"*
- *"My coolant is running at 98°C — is that normal for my engine?"*
- *"How far have I travelled today?"*
- *"Summarise my engine hours since last service."*
- *"What should I check if my oil pressure drops below 40 PSI?"*
- *"Tell me about this morning's boat log entries."*
- *"What is the legal minimum life jacket requirement in Ontario?"*
- *"What are the bag limits for walleye in Lake Erie?"*

### Mute / Pause

Tap the **mute** button (speaker icon, top-right of Helm screen) to toggle TTS voice response on or off. When muted, Helm still responds — text only, no audio. **Mute state is saved across reboots** — if you mute Helm, it stays muted after the Pi restarts.

Helm automatically pauses when you are recording a voice note in the Boat Log — it resumes after the recording completes.

### Documents

Helm can answer questions about documents you have uploaded (vessel manuals, engine manuals, coast guard guides, fishing regulations). See Settings → Documents for how to upload.

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

## 9. Mobile Companion App

The d3kOS companion app is a Progressive Web App (PWA) available at **atmyboat.com/app**. No App Store download required — install it from your phone's browser.

### Installing the App

**iPhone / iPad (Safari only):**
1. Open **Safari** and go to **atmyboat.com/app**
2. Log in to your AtMyBoat account
3. Tap the **Share** button (box with arrow) at the bottom of Safari
4. Tap **Add to Home Screen**
5. Tap **Add** — the d3kOS icon appears on your home screen

**Android (Chrome):**
1. Open **Chrome** and go to **atmyboat.com/app**
2. Log in to your AtMyBoat account
3. Tap the **⋮** menu → **Add to Home Screen** (or tap the install prompt if it appears)
4. Tap **Install**

### Pairing Your Phone to Your Pi

Pairing links your AtMyBoat account to your specific d3kOS installation. You only need to pair once.

**On your Pi:**
1. Go to **Settings → Mobile → Pair Device**
2. A QR code appears on the Pi screen

**On your phone:**
1. In the d3kOS app, tap **Pair New Device**
2. Point your phone camera at the QR code on the Pi screen
3. Pairing completes automatically — both screens confirm success

After pairing, your phone can communicate with your Pi through the AtMyBoat cloud — even when you are not on the same network.

### What the App Does

| Feature | What it shows | Tier required |
|---------|--------------|--------------|
| **Find My Boat** | Last known GPS position, system health, engine snapshot | T1 (free) |
| **Live Monitoring** | Real-time engine data and alerts via direct P2P connection | T1 (free) |
| **Alerts** | Push notifications for engine alerts, anchor drag, Pi offline | T1 (free) |
| **Chart Room** | Voyage summaries, engine trend graphs, PDF diagnostic reports | T1 (free) |
| **Fix My Pi** | Remote AI-guided diagnostic and repair | T1 (pay-per-use) or T2+ included |
| **OTA Update** | Update d3kOS software remotely | T1+ |
| **Fleet Map** | See all your boats on one map (T3) | T3 |

### Alerts on Your Phone

When your Pi sends an alert (engine threshold, anchor drag, offline), d3kOS pushes a notification to your phone within the next sync cycle (up to 15 minutes). The notification shows:

- Alert type and severity
- Vessel name
- Time of alert
- Brief action recommendation

Tap the notification to open the app directly to the alert detail. Configure which alert types trigger notifications in **Settings → Alert Preferences** (in the app).

### Chart Room — Reports

The Chart Room is the reporting section of the app. It shows:

- **Voyage summaries** — each trip: distance, duration, fuel used, max RPM
- **Engine trend** — graphs of coolant temperature, oil pressure, and voltage over time (last 30 days)
- **PDF Reports** — AI-generated diagnostic reports (T2+). Reports are generated when significant engine events occur or on request.

To view a PDF report: tap **Chart Room → Reports** → tap any report to open it. Reports can be shared or saved from within the app.

### Restart Pi Services

In the app, go to **Settings** → scroll to the **Restart Pi** card. Tap **Restart Services** to remotely restart core d3kOS services (voice assistant, AI bridge, Gemini proxy, engine monitor) without a full Pi reboot.

- A status line shows the command being queued and the Pi's response
- Takes approximately 30–60 seconds to complete
- Available on all tiers (requires the Pi to be online)

---

## 10. Fix My Pi & OTA Updates

### Fix My Pi

Fix My Pi is a remote diagnostic and repair service. When d3kOS is misbehaving and you cannot physically access the Pi, Fix My Pi sends repair commands to your Pi on the next sync.

**Accessing Fix My Pi:**
- From the **d3kOS mobile app** → Fix My Pi tab
- From **atmyboat.com/fix-my-pi** (logged in)

**How it works:**
1. Describe the problem in the Fix My Pi form (e.g. "Dashboard shows blank screen", "Engine data stopped updating", "Helm AI not responding")
2. Submit the request — it is queued in AtMyBoat's command queue
3. The next time your Pi syncs (within 15–30 minutes on a normal connection), it pulls the Fix My Pi command
4. d3kOS runs automated diagnostics across all services — checking each component, attempting to restart any that have stopped
5. A PDF report is generated with the full diagnosis and what was fixed or what needs physical attention
6. The report is delivered to your **Chart Room** in the app

**Fix My Pi pricing:**
- **T1:** $29.99 per incident (charged to your account)
- **T2 / T3:** included — unlimited Fix My Pi requests

**What Fix My Pi can fix remotely:**
- Stopped d3kOS services (dashboard, camera, Helm AI, Signal K, GPS)
- Configuration file corruption
- Disk space issues
- Network connectivity problems
- Software crashes and failed updates

**What Fix My Pi cannot fix:**
- Physical hardware failures
- Power supply problems
- GPS antenna disconnections
- Camera hardware faults

### OTA Software Updates

OTA (Over-the-Air) updates allow you to upgrade your d3kOS installation remotely without touching the Pi, removing the SD card, or connecting a keyboard.

**Available for:** T1, T2, and T3 subscribers.

**Triggering an OTA update:**
1. In the d3kOS app, go to **Settings → System → Check for Updates**
2. If an update is available, the version number and release notes are shown
3. Tap **Install Update**
4. The update is queued. On the Pi's next sync, it downloads and installs automatically
5. The Pi reboots once installation is complete — typically takes 5–10 minutes
6. Your app shows "Update complete" when the Pi is back online

**What OTA updates can change:** application code, dashboard templates, Python services, and configuration defaults. OTA updates never touch your personal data, vessel configuration, boat log, or API keys.

### Config Backup & Recovery (T1+)

**Available for:** T1, T2, and T3 subscribers. T0 (free tier) does not include config backup.

d3kOS automatically backs up your Pi's configuration to AtMyBoat's cloud on every sync cycle (approximately every 30 seconds when connected). Backups are only sent when your configuration has actually changed — unchanged config is never uploaded twice. If your SD card ever fails, is lost, or you need to start from scratch, you can restore your full configuration in under two minutes — no manual re-entry required.

**What is backed up:**
- Vessel name and preferences (units, language, timezone)
- Your tier assignment and feature access
- Camera slot assignments
- Alert preferences and quiet hours
- Fleet assignment (T3)
- Cloud connection credentials
- AI and system settings

**What is NOT backed up:**
- Your Gemini API key — you re-enter this once after recovery (30 seconds)
- Boat log entries — these are preserved in your AtMyBoat cloud account separately
- Engine history data

**Your Recovery Key**

Your Recovery Key is a unique code tied to your Pi. You will need it if you restore your Pi without your phone.

**Where to find it:**
- On your Pi screen: **More → Settings → System → Recovery Key** — Copy button included
- In the d3kOS app: **Settings → Recovery Key** — Copy button included

**Recommendation:** Write your Recovery Key on a small label and stick it inside your Pi enclosure. This gives you a backup of the backup.

---

#### Restoring Your Pi After a Reflash

**Before you start:** Flash a fresh d3kOS image to your new SD card. Insert it and power on the Pi.

**Option 1 — Restore using the d3kOS app (easiest)**

1. The setup wizard loads on your Pi screen
2. Open the **d3kOS app** on your phone
3. Tap **Settings → Restore Pi**
4. Select your vessel from the list
5. The app sends your configuration directly to the Pi
6. The wizard confirms "Config restored" and loads the dashboard
7. Re-enter your Gemini API key in **More → Settings → AI Configuration**

**Option 2 — Restore using your Recovery Key (no app required)**

1. On the setup wizard welcome screen, tap **Recover Existing Pi**
2. Enter your Recovery Key (the 36-character code from your Pi label or Settings page)
3. Your configuration is downloaded from AtMyBoat's cloud
4. Dashboard loads with all your settings restored
5. Re-enter your Gemini API key in **More → Settings → AI Configuration**

**Option 3 — Restore using the app when offline (no internet required)**

1. Open the **d3kOS app** on your phone
2. Tap **Settings → Restore Pi**
3. Choose **Restore from App Cache**
4. Both your Pi and phone must be on the same WiFi network
5. The app sends your last saved configuration directly to the Pi over WiFi — no internet needed

---

#### Backup Frequency

Your configuration is backed up automatically every time your Pi syncs with AtMyBoat's cloud (approximately every 30 seconds when connected). The backup is updated only when your configuration has actually changed — there is no noticeable performance impact.

You can also trigger a manual backup at any time by running **Fix My Pi** from the app — config backup is the first step of every Fix My Pi run.

---

## 11. Fleet Management (T3)

Fleet Management is a T3 feature that allows you to monitor multiple boats — your own fleet or a small commercial operation — from a single AtMyBoat account.

### Setting Up a Fleet

1. Log in to **atmyboat.com** with your T3 account
2. Go to **Account → Fleet → Create Fleet**
3. Give your fleet a name (e.g. "MV Fishing Charter Fleet")
4. Your fleet code is generated — share this code with other T3 users to let them join

### Adding Boats to Your Fleet

Each boat that joins your fleet must have a paired d3kOS installation. The boat owner:
1. Goes to **Settings → Fleet** on their Pi
2. Enters the fleet join code
3. Confirms — their boat is now visible on your fleet map

### Fleet Map

On **atmyboat.com**, go to **Community → Fleet** to see your fleet map. Each boat appears as a colour-coded dot:

| Colour | Meaning |
|--------|---------|
| **Green** | All systems healthy, synced within 30 minutes |
| **Amber** | Advisory alert active, or last sync 30–120 minutes ago |
| **Red** | Critical alert active, or last sync > 2 hours ago |
| **Grey** | Pi offline or not synced in > 24 hours |

Tap any boat dot to see its detail card:
- Vessel name
- Last sync time
- Active alerts (if any)
- Last known position
- Engine health summary

### Fleet Alerts

Fleet-wide alerts appear in your **Account → Alerts** view. Any alert from any boat in your fleet — engine critical, anchor drag, Pi offline — appears here sorted by severity and time.

### Leaving a Fleet

A boat owner can leave a fleet at any time from **Settings → Fleet → Leave Fleet** on their Pi. Their boat is removed from the fleet map immediately.

---

## 12. Settings

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

### Mobile App

| Control | Function |
|---------|----------|
| **Pair Device** | Displays the QR code to pair a new phone |
| **Paired Devices** | Lists all paired phones — tap to unpair |
| **Alert Preferences** | Which alert types send a push notification to your phone |
| **Sync Status** | Last sync time, next scheduled sync |

### Predictive Maintenance

| Control | Function |
|---------|----------|
| **Enable Predictive Analysis** | Toggle — when on, engine trends are analysed in the background |
| **Baseline Reset** | Clears stored baseline readings and starts fresh (use after major engine work) |
| **Alert Sensitivity** | Low / Medium / High — controls how early predictive alerts fire |

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

### Fleet (T3 only)

| Control | Function |
|---------|----------|
| **Create Fleet** | Creates a new fleet and generates a join code |
| **Join Fleet** | Enter a fleet join code to add this boat to an existing fleet |
| **Leave Fleet** | Removes this boat from the current fleet |
| **Fleet Status** | Shows current fleet assignment and sync status |

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

Shows current status of the remote monitoring connection. See Section 13.

### System

| Button | Function |
|--------|----------|
| **Reboot System** | Restarts the Pi (requires confirmation) |
| **Check for Updates** | Checks AtMyBoat.com for OTA update availability (T1+) |
| **Install Update** | Queues OTA update for next sync (appears when update is available) |
| **Initial Setup Reset** | Clears all wizard configuration and relaunches the wizard (requires triple confirmation — contact support before using) |
| **Visit AtMyBoat.com** | Opens AtMyBoat.com in a new tab (requires internet) |

---

## 13. Remote Access

The Remote Access page shows the status of d3kOS's connection to the AtMyBoat.com monitoring service.

When connected, AtMyBoat.com receives:
- Vessel name and approximate GPS position (last known, not a live track)
- System health status (services running/stopped) — sent as a summary, not raw data
- Engine data summaries (trend data, not raw readings)
- Alert events (type and timestamp — no raw sensor streams)

**Status indicators:**
- **Connected** — green — data is flowing to AtMyBoat.com
- **Offline** — amber — Pi has no internet, data queued for next connection
- **Disconnected** — red — connection error, check network settings

The status updates in real time via a server-sent events (SSE) stream — no page refresh required.

**Privacy:** GPS coordinates are sent as approximate position only (±500m). You control what data is shared in **Settings → Remote Access**. T0 users can disable cloud sync entirely — d3kOS will never contact AtMyBoat.com.

**Version heartbeat:** d3kOS sends your current software version to AtMyBoat.com on each sync. This is used to notify you of available updates and to generate fleet analytics for T3 users. No identifying hardware information is included.

---

## 14. Autonomous Health System

d3kOS includes a background health management system (v0.9.8+) that monitors the Pi's own services and attempts to recover from problems automatically — before they affect your navigation session.

### What It Does

Six autonomous agents run continuously in the background:

| Agent | Function |
|-------|----------|
| **AA1 — Service Watchdog** | Monitors all 10 critical d3kOS services every 5 minutes. Restarts any service that has stopped. Alerts AtMyBoat.com if a service cannot be restarted. |
| **AA2 — Log Rotation** | Prevents log files from filling the SD card. Rotates and compresses old logs automatically. |
| **AA3 — Health Reporter** | Sends system health summaries to AtMyBoat.com. Generates the health score you see in the mobile app. |
| **AA4 — Update Checker** | Checks for available OTA updates and notifies the mobile app. Does not install without your confirmation. |
| **AA5 — Network Resilience** | Monitors WiFi and cellular connections. Reconnects automatically on drop. Switches between connections if configured. |
| **AA6 — Backup Agent** | Backs up your vessel configuration, boat log, and engine history to a USB drive when one is inserted at `/mnt/usb-backup`. No USB drive = this agent is idle. |

### Failure Intelligence

When a service fails and the system cannot recover automatically, d3kOS generates a **Failure Report** and sends it to AtMyBoat.com. The report includes:

- Which service failed
- Error logs from the failure
- Actions the system attempted before escalating
- Recommended repair steps

Failure reports appear in your **Account → Diagnostics** on AtMyBoat.com and trigger a notification to your phone. If you have a T1+ account, you can initiate a Fix My Pi directly from the failure report.

### Health Score

The mobile app shows a **Health Score** (0–100) on the main app screen. This score reflects:
- Services running vs. stopped
- Recent failure events
- Disk space remaining
- Last successful sync
- Active alerts

A score of 100 means everything is running normally. Below 80 warrants investigation. Below 50 means at least one critical service has failed.

---

## 15. Troubleshooting

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
3. For TTS silence, check that voice responses are not muted (Settings → AI Configuration → Voice Responses)
4. Note: if Helm was muted before the last reboot, it stays muted after reboot. Check the mute state first.

### Camera shows "Connecting" / offline

1. Check that the camera USB or RTSP source is connected
2. Restart the camera service: Settings → System → Reboot, or contact support
3. Check camera slot assignment in Settings → Cameras — the slot may not have a camera assigned

### Fish detector not activating

Fish detection requires an active camera stream. If the camera is connecting or offline, detection is suspended. Once the camera stream is live, detection resumes automatically.

### Mobile app not connecting to Pi

1. Confirm the Pi is paired — go to Settings → Mobile on the Pi and check the paired devices list
2. Check that the Pi has an internet connection — the app communicates through AtMyBoat.com when you are away from the boat
3. If the Pi is online but showing as offline in the app, wait 15 minutes for the next sync cycle
4. If pairing is lost, re-pair from Settings → Mobile → Pair Device on the Pi

### SD card failed — need to restore Pi configuration

If your Pi's SD card has died or been wiped, use the Config Backup & Recovery feature (T1+).
See **Section 10 — Config Backup & Recovery** for full instructions. Summary:

1. Flash a fresh d3kOS image to a new SD card
2. Power on the Pi — the setup wizard loads
3. Use the **d3kOS app → Settings → Restore Pi** (easiest), OR
4. Tap **Recover Existing Pi** on the wizard and enter your Recovery Key
5. Re-enter your Gemini API key after recovery completes

If you are on T0 (free tier), config backup is not included. You will need to go through the
full setup wizard as if it were a new installation.

### Fix My Pi request not completing

1. Fix My Pi requires the Pi to sync with AtMyBoat.com — the Pi must have internet access
2. If the Pi is completely offline (no network), Fix My Pi cannot run until the network is restored
3. Check the **Remote Access** page to confirm the Pi is connected
4. If the fix completes but the problem persists, contact support through **atmyboat.com/contact**

### Touch keyboard not appearing

The on-screen keyboard (Squeekboard) appears automatically when you tap any text input field. If it does not appear:
1. Tap the text field again — sometimes a second tap is needed on first load
2. The keyboard may be behind the main window — check if it appears at the bottom of the screen

### System time is wrong after reboot

The Pi has no hardware clock. Time is set by NTP when internet is available (usually within 1–2 minutes of network connection). If you are offline, `fake-hwclock` keeps time approximate between reboots.

### Health score is below 80

Open the mobile app and tap **Health Score** to see which component is failing. Common causes:
- AA6 (Backup Agent) is amber if no USB drive is inserted — insert a USB drive or ignore this if you do not need local backups
- A service has stopped — the watchdog will attempt restart automatically, but if it cannot, a Fix My Pi request will resolve most service failures
- Disk space low — check Settings → Data Management and clear old trip data or export and clear the boat log

---

## 16. Quick Reference Card

| Feature | How to access | Requires internet |
|---------|--------------|-------------------|
| Instrument data | Main dashboard | No |
| Chart navigation | More → AvNav | No (cached charts) |
| Wind/wave map (Windy) | Weather → Windy tab | Yes |
| Radar | Weather → Radar tab | Yes |
| Camera feeds | Marine Vision | No |
| Fish detection | Automatic when cameras active | No |
| Forward Watch (collision avoidance) | Enabled via Settings → Cameras | No |
| AI Helm | HELM button (voice or text) | Yes (Gemini API) |
| Engine diagnostics (AI) | Engine cell tap or Engine Dashboard → AI Diagnostic (T2/T3) | Yes (Gemini API) |
| Predictive maintenance | Automatic background analysis | No |
| Boat log voice note | Boat Log → microphone | No |
| Data export | Boat Log → Export | No |
| Mobile app | atmyboat.com/app | Yes (for pairing and cloud sync) |
| Find My Boat | App → home screen | Yes |
| Fix My Pi | App → Fix My Pi, or atmyboat.com | Yes |
| Config backup | Automatic on every sync (T1+) | Yes |
| Restore Pi after reflash | App → Settings → Restore Pi, or setup wizard → Recover Existing Pi (T1+) | Yes (or LAN only) |
| Your Recovery Key | More → Settings → System → Recovery Key | No |
| OTA update | App or Settings → System → Check for Updates | Yes |
| Fleet map | atmyboat.com → Community (T3) | Yes |
| Restart Pi services | App → Settings → Restart Pi | Yes (via cloud) |
| Settings | More → Settings | No |
| Help / Manual | More → Help / Manual | No (served locally on Pi) |

---

*d3kOS User Manual v0.9.9.3 — Document version 2.2.0 — April 12, 2026*
*AtMyBoat.com — Open-source marine intelligence*
