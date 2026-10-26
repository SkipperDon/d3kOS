# d3kOS User Manual
## Version 0.9.9.5

**System:** d3kOS — AI-powered marine navigation hub
**Hardware:** Raspberry Pi 4B (8 GB RAM minimum), 128 GB microSD card, 10.1" touchscreen, 1280×800
**Document version:** 2.9.0 — October 26, 2026 — covers d3kOS v0.9.9.5 and the v0.9.9.5.1 update

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Initial Setup Wizard](#2-initial-setup-wizard)
    - [First-Boot Password Setup](#first-boot-password-setup)
3. [Main Dashboard](#3-main-dashboard)
    - [Instrument Row Ribbon (BOTH/ENGINE/NAV/WX)](#instrument-row-ribbon)
4. [Weather Panel](#4-weather-panel)
5. [Marine Vision — Camera System](#5-marine-vision--camera-system)
6. [Engine Dashboard & Predictive Maintenance](#6-engine-dashboard--predictive-maintenance)
7. [Helm Assistant — AI Chat](#7-helm-assistant--ai-chat)
8. [Boat Log](#8-boat-log)
9. [Mobile Companion App](#9-mobile-companion-app)
10. [Fix My Pi & OTA Updates](#10-fix-my-pi--ota-updates)
    - [OTA Software Updates (D23)](#ota-software-updates-d23)
    - [Automatic Rollback](#automatic-rollback)
    - [Config Backup & Recovery (T1+)](#config-backup--recovery-t1)
11. [Fleet Management (T3)](#11-fleet-management-t3)
12. [Settings](#12-settings)
    - [Security — Change Password](#security--change-password)
13. [Remote Access](#13-remote-access)
14. [Autonomous Health System](#14-autonomous-health-system)
15. [Troubleshooting](#15-troubleshooting)
16. [Quick Reference Card](#16-quick-reference-card)
17. [AtMyBoat.com Account](#17-atmyboatcom-account)
18. [AI-SafeHelm — Collision Advisory System](#18-ai-safehelm--collision-advisory-system)

---

## 1. Introduction

d3kOS is a marine navigation hub that runs on a Raspberry Pi mounted at your helm. It integrates chart navigation (AvNav), engine monitoring (NMEA 2000 via Signal K), AI-powered vessel assistance (Helm), camera monitoring (Marine Vision), weather overlays, predictive maintenance, and a boat log — all accessible from a single touchscreen interface.

**What d3kOS is not:** it is not a standalone chartplotter. It works alongside your existing MFD and VHF radio. It adds an AI intelligence layer and centralised monitoring that your MFD does not provide.

### What You Need

| Required | What to look for |
|----------|------------------|
| Raspberry Pi 4B | 8 GB RAM minimum |
| microSD card | 128 GB minimum, Class 10 A2 or better |
| Touchscreen | 10.1 inch, 1280×800, HDMI + USB touch |
| Power supply | 12 V to 5 V DC-DC converter, 5 A minimum, marine-grade isolated |

| Optional | What it adds |
|----------|--------------|
| NMEA 2000 adapter — PiCAN-M or USB-CAN-A | Engine, GPS and AIS data from your NMEA 2000 network. Detected automatically at boot — no setup needed. |
| USB GPS receiver | GPS position — only needed if your NMEA 2000 network has no GPS |
| AIS receiver — RTL-SDR USB dongle, or AIS on your NMEA 2000 network | AIS targets on the chart and AI-SafeHelm collision advisory |
| USB speakerphone | Helm voice assistant |
| IP cameras (PoE, RTSP) | Marine Vision and Forward Watch |

The CX5106 engine gateway used by earlier versions is no longer supported. Engine data now comes only from your NMEA 2000 network.

### Service Tiers

d3kOS has four service tiers. Your tier decides which features are active. This table describes d3kOS v0.9.9.5 as it ships:

| Tier | Cost | What it adds |
|------|------|-------------|
| **T0 — Base** | Free, no account | Main dashboard, AvNav charts, engine and navigation instruments, weather, Helm Assistant text chat (with your own Gemini key), boat log, anchor watch, AI-SafeHelm. |
| **T1 — First Mate** | Free with an approved AtMyBoat.com registration | T0 + cameras (Marine Vision, Forward Watch), Helm voice assistant, over-the-air (OTA) updates, mobile companion app, community map, cloud sync, engine and anchor alerts, predictive alerts. Fix My Pi at $29.99 per use. |
| **T2 — Premium** | $9.99/month | T1 + PDF reports, SMS alerts, multiple phones, maintenance schedule, Fix My Pi 3 times per month. |
| **T3 — Professional** | $99.99/year | T2 + fleet management (multiple boats), unlimited Fix My Pi. |

**Note:** in this release, cameras and the Helm voice assistant need Tier 1 (free registration). We intend to make them available without an account in a future update.

Your tier is shown in **Settings → License & Tier**. Plans are listed at **atmyboat.com/pricing**.

### First Boot

On first power-up, d3kOS shows a **legal disclaimer** — tap **I Agree** to continue (the disclaimer appears at the start of every new session). If your Pi still has the factory password, you must set a new one first. Then the **Setup Wizard** starts automatically. Only the vessel name is required — every other step can be skipped and completed later. The AI uses what you enter to give advice specific to your boat.

---

## 2. Initial Setup Wizard

The wizard runs once, at first boot. A password screen comes first (only if your Pi still has the factory password). The wizard itself has 9 screens: **Welcome** (Step 1), Steps 2–8, and a final **Hardware** screen (Step 9). Only the vessel name is required; every other step has a **Skip** option, and you can fill the details in later from Settings.

A **← Back** button appears on every step from Step 2 onward.

On Tier 0 the wizard can be re-run a limited number of times; the Welcome screen shows how many runs remain.

---

### First-Boot Password Setup

**This screen appears before the Welcome screen if your Pi still has the factory password.** It does not appear again once a new password is set.

Every d3kOS image ships with the same factory password. The wizard cannot run until you replace it.

**Why this matters:** your Pi is reachable by any device on your boat's network. Leaving the factory password in place means anyone on that network could access your system settings.

**What to do:**

1. Enter a new password — minimum 8 characters
2. Confirm the password
3. Tap **SET PASSWORD & CONTINUE ›**

**Rules:** minimum 8 characters; cannot be the factory password; both fields must match.

**Changing your password later:** go to **Settings → Security — Change Password**.

---

### Step 1 — Welcome

**Screen title:** Welcome to d3kOS — Your marine navigation hub

Introduces d3kOS. No data entry required.

**Buttons:**
- `GET STARTED ›` — starts the wizard
- `RECOVER EXISTING Pi ›` — restores a Pi you have set up before, using its **Recovery Key** (a 36-character code). See Section 10.

---

### Step 2 — Vessel Identity

The **Vessel Name** is required (shown in the status bar and used in AI prompts). All other fields are optional but improve AI accuracy.

| Field | What to enter |
|-------|---------------|
| **Vessel Name** *(required)* | Your boat's name |
| **Home Port** | Marina or harbour you return to |
| **Dashboard Language** | Language for the dashboard — also sets the Helm voice recognition language |
| **Manufacturer**, **Year**, **Model** | Your boat's builder, model year and model |
| **Length (ft)** | Length overall |
| **Boat Type** | Power — Single Engine, Power — Twin Engine, Sail, Catamaran — Power, Catamaran — Sail, Inflatable (RIB), Other |
| **Region Sold** | North America, Europe, Australia / NZ, Other |

Step 2 also shows a **Free Charts Configured** indicator — open-source chart streaming through AvNav is ready to use.

---

### Step 3 — Engine & Drive

Enter your engine details. The AI uses them to interpret engine data from your NMEA 2000 network and to search your manuals.

| Field | What to enter |
|-------|---------------|
| **Make** | Choose from the list (Mercury Marine, MerCruiser, Yamaha Marine, Volvo Penta, Yanmar, Cummins Marine, and others) or Other |
| **Year** | Engine model year |
| **Model / Spec** | Include displacement and series if known — used for manual search |
| **Horsepower** | Rated HP |
| **Cylinders** | 1, 2, 3, 4, 6, 8 or 12 |
| **Fuel Type** | Gasoline (4-stroke), Diesel (4-stroke), Outboard (4-stroke), Outboard (2-stroke) |
| **Induction** | Naturally Aspirated, Turbocharged, Supercharged |
| **Idle RPM** / **Max RPM (WOT)** | Normal idle and wide-open-throttle limit |

**Twin engines:** a second engine block (Make, Year, Model / Spec) can be filled in.

**Skip:** `Skip — I'll add engine details later ›`

---

### Step 4 — Electronics & NMEA

| Field | What to enter |
|-------|---------------|
| **Chart Plotter / MFD** | Your existing chartplotter |
| **VHF Radio** | Your VHF |
| **Gateway Model** | The device that connects your engine to NMEA 2000: None / Not installed, Actisense EMU-1, Yacht Devices YDAB-01, NMEA 2000, Other |
| **Fuel / Level Sender Standard** | North America — 240–33 Ω, or Europe / International — 0–190 Ω |

**Skip:** `Skip — No gateway yet ›`

**Note:** your NMEA 2000 adapter for the Pi itself (PiCAN-M or USB-CAN-A) is not chosen here — d3kOS detects it automatically at every boot.

---

### Step 5 — Gateway Configuration

Shows configuration guidance for the engine gateway you chose in Step 4:

- **Actisense EMU-1** — configured with Actisense NMEA Reader software on a Windows PC (see the EMU-1 Quick Reference Card). Key settings: cylinder count (from Step 3), engine instance (0 for single or port, 1 for starboard), tank sender standard (from Step 4).
- **Other NMEA 2000 gateways** — refer to the guide included with your gateway. Key settings: engine instance (0 for single or port, 1 for starboard), cylinder count, and the fuel/level sender range for your region.
- **None** — nothing to configure. You can add a gateway later from **Settings → Engine Configuration**.

**Skip:** `Skip ›`

---

### Step 6 — Mobile Pairing (AtMyBoat.com Registration)

Registration is **optional** — but in this release it is needed for cameras, the Helm voice assistant, OTA updates and the mobile app (see Service Tiers).

The screen explains that connecting is free, and that connecting shares information about your Pi with AtMyBoat.com. If you skip, your Pi stays anonymous.

To register:
1. Scan the QR code with your phone camera — it opens AtMyBoat.com, where you create your free account and link this Pi in one step
2. Or type the code shown on screen at **atmyboat.com/register** (the code expires — the screen shows when)
3. After registration your Pi waits for approval. You receive an email when it is approved; Tier 1 features then switch on

**No internet?** Registration needs an internet connection. Skip the step and register later from **Settings → AtMyBoat Community & Mobile Pairing**.

**Skip:** `Skip this to continue ›`

---

### Step 7 — AI Key

d3kOS uses Google Gemini for the Helm Assistant, engine diagnostics and document questions. You need your own free API key.

**How to get your key:**
1. On a phone or computer, go to `aistudio.google.com`
2. Sign in with a Google account
3. Click **Get API Key** → **Create API key**
4. Copy the key (it starts with `AIza`)

Paste it into **Gemini API Key**. The key is stored on your Pi.

No key yet? Tap **Skip for now** and add it later in **Settings → AI Assistant — Gemini & Vessel Settings**.

---

### Step 8 — All done

Shows **Camera RTSP URL format** help, with common defaults for Hikvision, Dahua and Reolink cameras, and a **Set Up Cameras (new tab) ›** button.

**Button:** `NEXT ›`

---

### Step 9 — Hardware

Shows the hardware d3kOS detected on your Pi, with a **Re-probe Hardware** button. Features are matched to what your hardware can run.

**Button:** `LAUNCH d3kOS ›` — saves your settings and opens the main dashboard.

---

## 3. Main Dashboard

The main dashboard is the primary screen you use underway. It shows live instrument data, navigation, and provides access to all features.

### Instrument Grid

The dashboard displays real-time data in instrument cells arranged in a grid. Each cell shows a primary value, a unit label, and status colour coding.

| Cell | What it shows |
|------|---------------|
| **Speed** | Speed over ground |
| **Course** | Course over ground |
| **Position** | Latitude and longitude |
| **Depth** | Depth (if a depth sounder is on your network) |
| **RPM** | Engine RPM |
| **Coolant Temp** | Engine coolant temperature |
| **Oil Pressure** | Engine oil pressure |
| **Trim** | Drive trim |
| **Fuel** | Fuel level (if a sender is connected) |
| **Next Waypoint** | Distance, bearing and ETA to the active AvNav waypoint |

Values come from Signal K (your NMEA 2000 network and GPS) and are shown in the units you choose in **Settings → Units & Display**.

**Cell colour states:**
- **Normal** — white/grey — within acceptable range
- **Advisory** — amber — approaching a threshold — monitor closely
- **Alert** — orange — threshold exceeded — take action
- **Critical** — red — critical limit reached — stop and investigate

When a critical alert fires, a red ticker banner appears at the bottom of the screen with a plain-language message (e.g. `⛔ CRITICAL — COOLANT 108°C — REDUCE RPM NOW`). Helm speaks the alert aloud through the Pi's speakers.

Tapping an engine gauge on the main dashboard opens the **AI Engine Diagnostic** panel — Helm analyses the live readings and gives a recommendation for your engine model.

---

### Instrument Row Ribbon

A row of tab buttons runs across the dashboard below the status bar. These switch which instrument data rows are visible and what fills the chart area beneath them:

| Button | What it shows |
|--------|--------------|
| **⚙ + 🧭 BOTH** | Engine row + Navigation row — standard underway view |
| **🔧 ENGINE** | Engine instruments only (coolant, oil, RPM, voltage) |
| **🧭 NAV** | Navigation instruments only (speed, course, depth, waypoint) |
| **🌤 WX** | Full-screen weather view (Windy wind/wave + radar overlay) |

The ribbon stays visible in every mode — including WX — so you can switch between views with a single tap at any time.

### Status Bar Pills

Small pills in the status bar show system state (the AI-SafeHelm widget sits at the bottom of the screen — see Section 18):

| Pill | Meaning |
|------|---------|
| **Pi: OK / Pi: WARN / Pi: CRITICAL** (green / amber / red) | Health of the Pi's monitoring agents. Tap it to see each agent's status and when it last reported. |
| **Update Available** (amber) | A new d3kOS version is ready to install (Tier 1). See Section 10. |


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

**HELM** is the large centre button — it opens the Helm Assistant page. To talk to Helm by voice, say "Helm" (see Section 7).

---

### More Menu

The More menu provides access to secondary features:

| Item | Opens |
|------|-------|
| **AI Navigation** | Marine AI assistant |
| **Engine Dashboard** | Full engine instrument panel |
| **Helm Assistant** | Engine diagnostics & AI chat |
| **Anchor Watch** | Anchor drag alarm and drift monitor |
| **Initial Setup** | Vessel configuration wizard |
| **Upload Documents** | Add manuals & PDFs for Helm to reference |
| **Manage Documents** | View & delete uploaded files |
| **Settings** | System settings page |
| **Help / Manual** | This user guide — all 18 chapters |

---

### Weather Conditions Panel

A slide-out panel on the left edge of the dashboard shows current conditions:
- Wind speed and direction
- Temperature and barometric pressure
- Sea state summary

Tap the **WX** button (or swipe from the left edge) to open/close it. This panel reads from Signal K when underway. When the vessel is docked and internet is available, it pulls from online weather services.

---

### Anchor Watch

Anchor Watch monitors your anchored position and sounds an alarm if your boat drifts outside a defined radius. The on-screen alarm works on all tiers; anchor alerts to your phone need Tier 1.

**Accessing Anchor Watch:** More menu → **Anchor Watch**

**Setting your anchor:**
1. Motor to your anchoring spot and drop the hook
2. Open Anchor Watch — your current GPS position is captured automatically as the anchor reference point
3. Set your **Watch Radius** — the acceptable drift distance in metres. Default is 25 m. Adjust for scope, tide, and conditions.
4. Tap **Set Anchor** — the alarm activates

**What you see on screen:**
- A canvas mini-map showing your anchor point (⚓) and current vessel position (▲)
- **Distance** — current distance from your anchor reference in metres
- **Drift Dir** — compass direction of drift from the anchor point
- Status: **Holding** (green) or **DRAGGING** (red)

**When the alarm fires:**
- The screen turns red and displays **ANCHOR DRAGGING**
- Helm speaks an audible alarm through the Pi speakers
- Tap **DISMISS** to silence the alarm (this does not reset the watch — monitoring continues)

**Stopping Anchor Watch:** Tap **Clear Anchor** to disarm the alarm and return to standby.

**Important:** Anchor Watch uses your Pi's GPS. GPS accuracy on a Pi is typically ±3–5 m. Set your radius to at least 15 m to avoid false alarms from GPS position drift while stationary.

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

Marine Vision manages your onboard cameras: live feeds and Forward Watch. Cameras need Tier 1 (free registration) in this release. Fish species identification is in development.

### View Mode Bar

The View Mode Bar runs across the top of the Marine Vision screen. It is divided into two groups:

**Left group — Camera Slots**
Each connected camera appears as a labelled button (e.g. Bow, Helm, Port, Stbd). Tap a button to switch to that camera's live feed. The active camera button is highlighted. An offline camera is dimmed and cannot be selected. A reconnecting camera is shown at reduced opacity but remains tappable.

**Right group — View Modes**

| Button | What it does |
|--------|-------------|
| **⊞ GRID** | Shows all cameras simultaneously in a 2×2 tile layout. Tap GRID again to return to single-camera view. |

### Camera Slots

Cameras are assigned to named slots (e.g. Bow, Stern, Port, Starboard, Helm). Cameras are found and assigned in **Settings → Camera Setup**.

Slots without a physical camera assigned show a placeholder with the slot name.

### Fish Species Identification

In development — not available in this release.

### Forward Watch — Bow Camera Hazard Detection

A bow-mounted camera can be used as a **Forward Watch** camera. d3kOS analyses the forward video with an AI model trained on marine objects: boats, ships, kayaks, logs and floating debris. (Buoys are part of the training set, but buoy and channel-marker detection is still being tuned — do not rely on it.)

- Alerts are suppressed below 1 knot, so the system stays quiet while moored
- An alarm is raised when an object is seen in 3 detection cycles in a row, or straight away when it is within about 75 m
- An alarm clears automatically when the object is no longer detected
- Detected objects are published to Signal K, so they can appear on the AvNav chart

Forward Watch is a Signal K plugin (signalk-forward-watch); its settings are in the Signal K admin under **Server → Plugin Config**. It is a safety aid — it does not replace a proper watch or VHF radio.

### Recordings

Camera clips are stored on the Pi's SD card.

---

## 6. Engine Dashboard & Predictive Maintenance

The Engine Dashboard provides a full-screen instrument panel dedicated to engine monitoring, combined with AI-powered predictive maintenance that watches your engine trends over time.

### Engine Gauges

Values are read live from your NMEA 2000 network via Signal K. The Engine Monitor page shows **RPM**, **Coolant Temp**, **Oil Pressure**, **Fuel**, **Battery**, and tank levels (**Fuel Level**, **Fresh Water**, **Black Water**) when those readings are present on your network.

### Alert Thresholds

Colour coding follows the same system as the main dashboard (normal / advisory / alert / critical). Thresholds are set in **Settings → Alerts & Notifications**.

### AI Engine Diagnostic

On the main dashboard, tap any engine gauge to open the **AI Engine Diagnostic** panel. Helm reads your live sensor values, compares them with the engine details from the Setup Wizard, and gives a plain-language status and recommended action. Useful when you see an unusual reading and want a second opinion before deciding whether to head in.

### Predictive Maintenance

d3kOS logs engine readings to a local database, and the predictive maintenance service compares recent readings with your engine's own baseline. When it sees a developing pattern — for example coolant temperature trending upward over several sessions — it can raise a predictive alert before a reading reaches its threshold. Predictive alerts need Tier 1.

---

## 7. Helm Assistant — AI Chat

Helm is your AI First Mate. It understands your vessel, your engine, your location, and the current state of your instruments.

### Starting a Conversation

**Voice (needs Tier 1 in this release):** say **"Helm"** — d3kOS listens for the wake word all the time — then ask your question. You can also open the Helm Assistant page with the **HELM** button and type. Speech is recognised on the Pi with Vosk (no internet needed for transcription) and the answer is spoken with Piper through the Pi's speaker. Answers come from Gemini using your boat details and your uploaded manuals; with no internet or no API key, Helm still answers from the manuals stored on the Pi.

If an urgent alert (for example AI-SafeHelm or anchor drag) needs the speaker while Helm is talking, the alert goes first and Helm asks you to repeat your question.

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

Helm can answer questions about documents you have uploaded (vessel manuals, engine manuals, coast guard guides, fishing regulations). Use **Upload Documents** in the More menu to add them.

---

## 8. Boat Log

The Boat Log is your onboard journal. It records engine data snapshots, voice notes and text entries, and exports to CSV for your records.

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

Tap **📥 Export CSV** to download your log as a spreadsheet-compatible CSV file, including your unit preferences (metric or imperial).

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
1. Go to **Settings → AtMyBoat Community & Mobile Pairing**
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
| **Chart Room** | Voyage summaries and engine trend graphs (T1); PDF diagnostic reports (T2) | T1 / T2 |
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
- Requires a paired Pi (Tier 1) that is online

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
- **T1:** $29.99 per incident
- **T2:** 3 requests per month included
- **T3:** unlimited

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

Over-the-air (OTA) updates keep your Pi current without removing the SD card or connecting a keyboard.

**Available for:** Tier 1 and above — your Pi must be registered (free) and approved at AtMyBoat.com. Install v0.9.9.5 from the SD card image once; after that, updates arrive over the air.

**Installing an update:**
1. When an update is ready for your Pi, an amber **Update Available** pill appears on the dashboard
2. Tap the pill, then confirm — the update installs in the background
3. d3kOS restarts its services automatically; the pill shows the result when done

**What an update keeps:** your configuration (`/opt/d3kos/config`), your data (`/opt/d3kos/data`) and logs are never overwritten.

**Safety checks built in:**
- Every update package is digitally signed. Your Pi installs only packages signed by the d3kOS release key and checks each package's SHA-256 checksum
- Your Pi refuses to install a version older than the one it is running
- If an installation fails, d3kOS rolls back to the previous version automatically

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
- On your Pi screen: **More → Settings → License & Tier → Recovery Key** — Copy button included
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
7. Re-enter your Gemini API key in **More → Settings → AI Assistant — Gemini & Vessel Settings**

**Option 2 — Restore using your Recovery Key (no app required)**

1. On the setup wizard welcome screen, tap **Recover Existing Pi**
2. Enter your Recovery Key (the 36-character code from your Pi label or Settings page)
3. Your configuration is downloaded from AtMyBoat's cloud
4. Dashboard loads with all your settings restored
5. Re-enter your Gemini API key in **More → Settings → AI Assistant — Gemini & Vessel Settings**

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

Each boat in a fleet needs a registered d3kOS installation. Fleet membership is managed from your AtMyBoat.com account.

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

A boat can be removed from a fleet from the AtMyBoat.com account.

---

## 12. Settings

Settings is a full-page screen opened from the **More** menu. It is organised into these sections:

| Section | What it is for |
|---------|----------------|
| **System Status — Live** | Live status of d3kOS services |
| **Engine Configuration** | Engine details and gateway |
| **Units & Display** | Metric or imperial units and display options |
| **Alerts & Notifications** | Alert thresholds and notification options |
| **AI Assistant — Gemini & Vessel Settings** | Your Gemini API key and vessel details used by the AI |
| **Camera Setup** | Find and assign cameras (Tier 1) |
| **Data Management** | Export and clear stored data |
| **Network & Connectivity** | Network settings |
| **Chart Setup & Documentation** | Charts and chart documentation |
| **OpenPlotter & System Infrastructure** | Underlying system components |
| **Getting Started — How to Use d3kOS** | Quick introduction |
| **d3kOS Phase Roadmap** | What is planned |
| **System Actions** | Reboot and other system actions |
| **System Information** | Version and hardware details |
| **License & Tier** | Your current tier |
| **Security — Change Password** | Change the system password (see below) |
| **About d3kOS** | Version and credits |
| **AtMyBoat Community & Mobile Pairing** | Register this Pi and pair your phone |
| **Updates** | Over-the-air updates (Tier 1) |

### Security — Change Password

Enter a new password (minimum 8 characters), confirm it, and tap **Change Password**. The change takes effect immediately. Change it periodically, after giving a guest access, or if you think someone has learned it.

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

**Privacy:** what your Pi sends depends on your tier and registration. See the AtMyBoat.com Privacy Policy for details.

**Version heartbeat:** d3kOS sends your current software version to AtMyBoat.com on each sync. This is used to notify you of available updates and to generate fleet analytics for T3 users. No identifying hardware information is included.

---

## 14. Autonomous Health System

d3kOS includes a background health management system (v0.9.8+) that monitors the Pi's own services and attempts to recover from problems automatically — before they affect your navigation session.

### What It Does

Five background agents watch the Pi, plus a separate service watchdog:

| Agent | Watches |
|-------|---------|
| **Health** | Overall system health — the source of the **Pi: OK / WARN / CRITICAL** pill |
| **Storage** | SD card space |
| **Performance** | CPU load and system performance |
| **Backup** | Configuration backups |
| **Update** | Software update status |

A separate **service watchdog** checks the critical d3kOS services and restarts any that have stopped.

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
3. Check your NMEA 2000 adapter is connected. PiCAN-M and USB-CAN-A are detected automatically at boot; unplugging and re-plugging a USB-CAN-A runs detection again

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

1. Helm voice needs Tier 1 in this release — check **Settings → License & Tier**
2. Check that the Gemini API key is set in **Settings → AI Assistant — Gemini & Vessel Settings** (Helm can still answer from your stored manuals without it)
3. Check the microphone — tap Helm and say something. If the waveform shows no input, check the USB microphone is plugged in and not muted
4. For no spoken reply, check that Helm is not muted
5. Note: if Helm was muted before the last reboot, it stays muted after reboot. Check the mute state first.

### Camera shows "Connecting" / offline

1. Cameras need Tier 1 in this release — check **Settings → License & Tier**
2. Check that the camera RTSP source is connected
3. Reboot from **Settings → System Actions**, or contact support
4. Check camera slot assignment in Settings → Camera Setup — the slot may not have a camera assigned

### Mobile app not connecting to Pi

1. Confirm the Pi is paired — go to Settings → AtMyBoat Community & Mobile Pairing on the Pi and check the paired devices list
2. Check that the Pi has an internet connection — the app communicates through AtMyBoat.com when you are away from the boat
3. If the Pi is online but showing as offline in the app, wait 15 minutes for the next sync cycle
4. If pairing is lost, re-pair from Settings → AtMyBoat Community & Mobile Pairing on the Pi

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

The Pi has no hardware clock. Time is set from the internet when a connection is available (usually within 1–2 minutes). If the Pi starts without internet after being powered off, the clock can be wrong until it gets internet time.

### Health score is below 80

Open the mobile app and tap **Health Score** to see which component is failing. Common causes:
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
| Camera feeds | Marine Vision (Tier 1) | No |
| Fish species identification | In development | — |
| Forward Watch (bow camera hazards) | Signal K admin → Server → Plugin Config (cameras need Tier 1) | No |
| Helm voice | Say "Helm" or tap HELM (Tier 1) | No for manuals; Yes for Gemini answers |
| Helm Assistant text chat | More → Helm Assistant | Yes (Gemini API) |
| Engine diagnostics (AI) | Tap an engine gauge on the main dashboard | Yes (Gemini API) |
| Predictive maintenance | Automatic background analysis | No |
| Boat log voice note | Boat Log → microphone | No |
| Data export | Boat Log → Export | No |
| Mobile app | atmyboat.com/app | Yes (for pairing and cloud sync) |
| Find My Boat | App → home screen | Yes |
| Fix My Pi | App → Fix My Pi, or atmyboat.com | Yes |
| Config backup | Automatic on every sync (T1+) | Yes |
| Restore Pi after reflash | App → Settings → Restore Pi, or setup wizard → Recover Existing Pi (T1+) | Yes (or LAN only) |
| Your Recovery Key | More → Settings → License & Tier → Recovery Key | No |
| OTA update | Update Available pill, or Settings → Updates (Tier 1) | Yes |
| Fleet map | atmyboat.com → Community (T3) | Yes |
| Restart Pi services | App → Settings → Restart Pi | Yes (via cloud) |
| Settings | More → Settings | No |
| Help / Manual | More → Help / Manual | No (served locally on Pi) |

---

## 17. AtMyBoat.com Account

AtMyBoat.com is the web platform that hosts the community forum, your account, and the cloud services that support the d3kOS mobile app. This section explains what you can do on the site, how to create an account, and how to manage it.

---

### What You Can Do Without an Account

Most of the website is fully public. No registration or login is required to:

| Page | What you can do |
|------|----------------|
| Homepage, /products, /hardware | Browse all content |
| /download | Download the d3kOS image |
| /app | Read PWA install instructions |
| /blog | Read all posts |
| /forum | Read all threads, ask the AI assistant |
| /features | Vote on feature requests |
| /directory | Browse the business directory |
| /marketplace | Browse buy/sell listings |
| /hall-of-fame, /challenges | View community content |

You only need an account to **participate** (post in the forum, create a listing, submit a feature request) or to use **cloud-connected features** (mobile app, community map, Chart Room).

---

### Creating an Account

Go to **atmyboat.com/register**.

**Registration fields:**

| Field | Required | Notes |
|-------|----------|-------|
| First name | Yes | |
| Last name | Yes | |
| Email address | Yes | Used as your login — must be a valid address |
| Password | Yes | Minimum 8 characters |
| Confirm password | Yes | Must match |
| I agree to the Terms of Service and Privacy Policy | Yes | Required — cannot submit without this |
| Send me product updates and community news | No | Optional — you can unsubscribe at any time |

After submitting, AtMyBoat sends a verification email to the address you entered. **Your account is not active until you click the link in that email.** The link expires after 24 hours — request a new one from the login page if needed.

Once verified, you are redirected to the login page.

**You do not need a d3kOS Pi to register.** The website is open to anyone interested in the d3kOS platform — boaters researching the system, community members, and forum participants who have not yet built a Pi are all welcome.

---

### Logging In

Go to **atmyboat.com/login**.

Enter your email address and password. Tick **Remember me** to stay logged in on that device.

**Links on the login page:**
- **Forgot your password?** — sends a reset link to your email address
- **Don't have an account?** — takes you to /register

After login you are taken to your account dashboard.

---

### Managing Your Account

Go to **atmyboat.com/my-account** (you must be logged in).

#### Change Password

1. Enter your new password (minimum 8 characters)
2. Confirm the new password
3. Click **Change Password**

Your session remains active. Any other devices logged in with your account will need to log in again with the new password.

#### Change Email Address

1. Enter your new email address
2. Enter your current password to confirm the change
3. Click **Update Email**

A verification email is sent to the new address. Your email does not change until you click the verification link. Until then, your old email address continues to work for login.

#### Delete Account

1. Click **Delete My Account**
2. Enter your current password to confirm
3. Click **Permanently Delete**

Deleting your account removes all personal data from AtMyBoat's servers in compliance with GDPR Article 17 and PIPEDA. This includes:
- Your profile and account details
- Forum posts (anonymised — content is kept, your name is removed)
- Paired Pi associations
- Billing history

**This action is permanent and cannot be undone.** Your Pi continues to function after account deletion at T0 (in this release, without cameras or Helm voice). Cloud features (mobile app, Fix My Pi, OTA updates) stop working until the Pi is paired with a new account.

#### Download Your Data

Click **Download My Data** to receive a ZIP file containing all personal data AtMyBoat holds about you — account details, paired device information, and any stored records. This complies with GDPR Article 15 (right of access).

---

### Forgot Password

On the login page, click **Forgot your password?** and enter your email address. A password reset link is sent immediately. The link expires after 1 hour. Check your spam folder if it does not arrive within a few minutes.

---

### Access Levels by Tier

Your account tier determines which website features are available after login:

| Feature | No account | Free account (T0/T1) | T1 (Pi paired) | T2 | T3 |
|---------|-----------|---------------------|-----------------|----|----|
| Read forum | Yes | Yes | Yes | Yes | Yes |
| Post in forum | No | Yes | Yes | Yes | Yes |
| AI assistant widget | Yes | Yes | Yes | Yes | Yes |
| Vote on feature requests | Yes | Yes | Yes | Yes | Yes |
| Submit feature requests | No | No | T1+ | T1+ | Yes |
| Community map (/community) | No | No | Yes | Yes | Yes |
| Chart Room (/dashboard) | No | No | Yes | Yes | Yes |
| Fleet management | No | No | No | No | Yes |

---

### 17.4 Creating Your AtMyBoat.com Account (Device-Gated Registration)

To protect the community from spam and bots, registration at **atmyboat.com/register/** requires proof that you have a real d3kOS installation. The process takes about 60 seconds.

#### Step 1 — Get your registration code from the Pi

1. Open the d3kOS dashboard in any browser on your home network
   - On the same device: go to `http://localhost:3000`
   - On a phone or tablet on the same Wi-Fi: go to `http://[your-Pi's-IP]:3000`
2. Tap **Settings** (gear icon)
3. Scroll to the **AtMyBoat Community & Mobile Pairing** section
4. Tap **Get Registration Code**
5. The dashboard contacts AtMyBoat.com and displays:
   - A **QR code** — scan it with your phone camera to go directly to the registration form
   - A **clickable link** — tap it if you are viewing the dashboard on the device you want to register with
   - A **short code** — type it manually at atmyboat.com/register/ if needed

> The code is valid for **30 minutes** and can only be used once.

#### Step 2 — Register at AtMyBoat.com

Using the QR code, link, or code from Step 1:

1. Go to **atmyboat.com/register/**
2. The page will show a green **"d3kOS Pi verified"** badge confirming your code is active
3. Fill in your first name, last name, email address, and password
4. Accept the Terms of Service
5. Tap **Create Account**

#### Step 3 — Verify your email

A verification email is sent to the address you provided. Click the link in that email to activate your account. The link is valid for 24 hours.

#### Step 4 — Pair your Pi

After verifying your email and logging in, go to **atmyboat.com/pair-device/** to pair your Pi with your account. Once your Pi is approved (you receive an email), it moves from T0 to T1 (First Mate) — enabling cameras, Helm voice, OTA updates and cloud features including the Chart Room, community map and voyage history.

#### Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid registration code" | The code expired (30 min limit) or was already used. Go back to the Pi dashboard and get a new code. |
| "Too many requests" | More than 5 codes were requested in 1 hour. Wait and try again. |
| Did not receive verification email | Check your spam folder. The email comes from hello@atmyboat.com. |
| Badge not showing on register page | Make sure you followed the link from your Pi dashboard, or type the code into the URL: `atmyboat.com/register/?rt=YOURCODE` |

---

---

## 18. AI-SafeHelm — Collision Advisory System

> **⚠ EXPERIMENTAL SYSTEM — READ THIS CHAPTER IN FULL BEFORE USE**
>
> AI-SafeHelm is a decision-support tool. It does not replace the watch, the radar, the VHF, or the judgment of a qualified mariner. The captain remains solely and completely responsible for the safe navigation of the vessel at all times. SafeHelm provides information — it does not give orders.

---

### What AI-SafeHelm Does

AI-SafeHelm monitors vessels in your area using AIS (Automatic Identification System) data received by your onboard AIS receiver. For each tracked vessel it continuously calculates:

- **CPA** — Closest Point of Approach (metres): how close the vessel will pass if both ships hold their current course and speed
- **TCPA** — Time to Closest Point of Approach (seconds): how long until that closest point is reached
- **COLREGs classification** — which International Regulations for Preventing Collisions at Sea rule applies to your situation with that vessel

When a developing situation reaches a defined threshold — CPA below your configured limit, TCPA within your configured window — SafeHelm raises an advisory alert on the SafeHelm widget shown on every operational d3kOS page.

SafeHelm does **not** take control of the helm or transmit any signal to any other vessel. It observes and advises, nothing more. Alerts are shown on the SafeHelm widget and spoken through the Pi's speaker.

---

### The SafeHelm Pill

On every operational d3kOS page, a small SafeHelm widget is fixed at the bottom of the screen:

```
  ⛵ SafeHelm
```

This pill is always visible while SafeHelm is active. Its colour and label change to reflect the current situation:

| Pill appearance | Meaning |
|---|---|
| `⛵ SafeHelm` — green border, white text | Connected — no qualifying traffic in the alert zone |
| `⛵ 1 !` — amber border | One vessel at Warning level — monitor the situation |
| `⛵ 2 ⚠` — red border, flashing | One or more vessels at Critical level — immediate attention required |
| `⛵` — grey border, grey text | SafeHelm disabled for this session |
| `⚠ SafeHelm` — orange border | SafeHelm service offline — attempting to reconnect |

**The pill itself is silent.** SafeHelm also speaks its alerts through the Pi's speaker in Helm's voice; urgent alerts begin with "Captain, standby." There is a 15-second gap between spoken announcements.

**Known issue (v0.9.9.5.1):** on the Pi's own touchscreen, the SafeHelm pill on the Engine Monitor and Anchor Watch pages may not update live. Spoken alerts are not affected. A fix is planned.

---

### Tapping the Pill — Expand Panel

Tap the widget at any time to open the **Alert Panel**. The panel is divided into three areas:

**1 — Alert rows (one per vessel)**

Each tracked vessel in alert state appears as a row:

```
  123456789   Head-On   CPA 420m   [ ACK ]  [ ✕ ]
```

| Column | What it means |
|---|---|
| MMSI number | The vessel's unique Maritime Mobile Service Identity |
| Rule label | The COLREGs rule governing the encounter (see table below) |
| CPA | Closest Point of Approach in metres at current courses and speeds |
| ACK button | Acknowledge — you have seen this alert; voice repetition is suppressed |
| ✕ button | Dismiss this vessel from the current alert episode |

**2 — Advisory line**

> *Advisory only — captain remains responsible*

This line is always shown. It cannot be removed. It is a permanent reminder of the system's advisory-only status.

**3 — Disable button**

> *Disable SafeHelm (this session)*

Tap this to shut SafeHelm off completely for the current session. See the Disabling section below.

---

### COLREGs Rules Displayed

SafeHelm classifies each encounter using the International Regulations for Preventing Collisions at Sea (COLREGs — COLREG 1972, as amended). The following rule labels may appear:

| Label shown | COLREGs Rule | Situation |
|---|---|---|
| **Head-On** | Rule 14 | Both vessels approaching head-on or nearly so — both must alter course to starboard |
| **Give-Way →** | Rule 15 | You are the give-way vessel in a crossing situation — you must keep clear |
| **Stand-On ←** | Rule 15 | You are the stand-on vessel in a crossing situation — maintain course and speed; give-way vessel should be altering |
| **Stand-On? ←** | Rule 15 | You appear to be the stand-on vessel but the give-way vessel's intentions are unconfirmed — maintain course but watch closely |
| **Overtaken** | Rule 13 | Another vessel is overtaking you from astern — the overtaking vessel is give-way |
| **Overtaking** | Rule 13 | You are overtaking another vessel — you are give-way and must keep clear |
| **Overtaken?** | Rule 13 | An overtaking situation is developing but not yet confirmed |
| **R18 Give-Way** | Rule 18 | A power-driven vessel must keep clear of sailing vessels, vessels not under command, or vessels restricted in their ability to manoeuvre |

**Important:** SafeHelm classifies based on AIS-reported course and speed only. It has no knowledge of vessel type, length, draught, or local traffic separation schemes. Rule 18 classification may be incorrect if AIS vessel-type data is absent or wrong.

---

### Alert Tiers

SafeHelm uses three alert tiers. Thresholds are set based on your vessel's speed and the calculated TCPA:

| Tier | Pill colour | Condition |
|---|---|---|
| **Advisory** | No change to pill | CPA below limit but TCPA is long — situation to watch |
| **Warning** | Amber border | CPA below limit, TCPA closing — action may be needed soon |
| **Critical** | Red border, flashing | CPA very close, TCPA short — immediate attention required |

The pill always shows the **highest tier** across all active alerts. Open the panel to see the individual tier for each vessel.

---

### ACK and Dismiss

**ACK — Acknowledge**

Tapping ACK tells SafeHelm that you have seen this alert and are aware of the vessel. The alert remains active in the display (the pill does not change) but voice repetition — if voice advisory is enabled — is suppressed. If the CPA worsens significantly after acknowledgement, the alert may escalate back to unacknowledged.

**✕ — Dismiss**

Tapping ✕ removes this vessel from the current alert episode. SafeHelm stops tracking this vessel for alerts until the vessel's CPA clears the alert zone and subsequently re-enters it. Use dismiss when you have assessed the situation and determined there is no collision risk — for example, because you have already altered course or because the other vessel's AIS data is known to be erratic.

Neither ACK nor Dismiss alters your course, signals the other vessel, or changes anything outside the d3kOS display.

---

### Disabling SafeHelm

To disable SafeHelm completely for the current session:

1. Tap the `⛵ SafeHelm` widget
2. In the panel that opens, tap **Disable SafeHelm (this session)**
3. The pill turns grey and shows `⛵` only
4. The SSE connection to the SafeHelm service closes
5. No further alerts are shown for the remainder of the session

**This setting is session-only.** It resets automatically when you close the browser or restart the Pi. SafeHelm will be fully active again on the next session. There is no permanent disable switch.

To re-enable during the same session:

1. Tap the grey `⛵` pill
2. Tap **Re-enable SafeHelm**
3. The connection reopens and alerts resume immediately

---

### Technical Requirements

SafeHelm requires the following to operate:

| Requirement | Notes |
|---|---|
| AIS receiver | An RTL-SDR USB dongle (decoded on the Pi), or AIS from your NMEA 2000 network through a PiCAN-M or USB-CAN-A adapter. SafeHelm reads AIS from Signal K. |
| Signal K server | Must be running (`d3kos-signalk` service). SafeHelm subscribes to the Signal K WebSocket stream. |
| Own vessel GPS | Your own position is required to compute CPA. SafeHelm uses the GPS position that Signal K receives from your GPS receiver. |
| Own vessel COG/SOG | Your own course and speed are required for COLREGs classification. These also come from Signal K. |
| Internet | Not required. SafeHelm runs entirely on the Pi. No data leaves your vessel. |

If any of these requirements are not met, the pill shows `⚠ SafeHelm` in orange and attempts to reconnect every 5 seconds.

---

### What SafeHelm Cannot See

AIS coverage has fundamental limitations that every operator must understand:

- **Vessels without AIS are invisible.** Fishing vessels under 15 metres, recreational vessels, military vessels, and many small commercial craft are not required to carry AIS and many do not. A clear SafeHelm display does not mean the water ahead is clear.
- **AIS data may be delayed.** AIS updates depend on the transmitting vessel's update rate (typically 2–10 seconds for vessels underway) and your receiver's ability to decode the signal. In congested areas, receiver overload can cause missed updates.
- **AIS data may be wrong.** Vessels sometimes transmit incorrect COG, SOG, or position due to equipment faults. SafeHelm cannot verify the accuracy of AIS data it receives.
- **SafeHelm does not know about bridges, shoals, traffic separation schemes, or local regulations.** It computes open-water CPA only.
- **SafeHelm does not account for vessel manoeuvring lag.** CPA calculations assume both vessels maintain current course and speed until the closest point. Real vessels take time to respond to helm input.
- **At anchor or slow speed, classifications may be unreliable.** COLREGs rules apply to vessels underway and making way. SafeHelm may misclassify situations when your own speed is very low or when COG is undefined.

---

### ⚠ Critical Safety Cautions

Read and understand these cautions before relying on SafeHelm in any way.

**CAUTION 1 — EXPERIMENTAL SYSTEM**
AI-SafeHelm is an experimental feature under active development. It has not been certified, type-approved, or approved by any maritime authority including Transport Canada, USCG, MCA, or IMO. It must not be used as a primary collision-avoidance tool.

**CAUTION 2 — ADVISORY ONLY**
Every alert SafeHelm produces is advisory. The system recommends nothing and commands nothing. The decision to alter course, reduce speed, sound a signal, or take any other action rests entirely with the officer of the watch. SafeHelm's classification of a COLREGs rule does not constitute legal or navigational advice.

**CAUTION 3 — PROPER LOOKOUT IS YOUR LEGAL OBLIGATION**
COLREGs Rule 5 requires every vessel to maintain a proper lookout by sight and hearing at all times. A glowing green pill does not satisfy this obligation. Do not reduce your watchkeeping because SafeHelm shows no alerts.

**CAUTION 4 — AIS IS NOT RADAR**
SafeHelm sees only AIS-equipped vessels. It does not detect vessels by radar return. In poor visibility, restricted waterways, or areas with high small-craft traffic, the majority of collision risk may come from vessels SafeHelm cannot see at all.

**CAUTION 5 — DO NOT DELEGATE THE WATCH TO SOFTWARE**
SafeHelm is a supplementary awareness tool. It is appropriate to glance at the pill as part of a broader scan. It is not appropriate to reduce watch frequency, reduce speed less cautiously in fog, or make manoeuvring decisions based solely on what SafeHelm shows.

**CAUTION 6 — PHASE 1 LIMITATIONS**
The current version (Phase 1) uses COLREGs rules based on geometry and relative motion only. It does not implement Rule 19 (restricted visibility) in full, does not account for vessel characteristics reported in AIS Type 21 (aids to navigation) messages, and does not handle traffic separation schemes. These limitations will be addressed in future versions.

---

### SafeHelm and COLREGs — A Note for the Captain

The COLREGs rules that SafeHelm references are international law, enacted in Canada under the *Collision Regulations* (CRC, c 1416) and applicable in all Canadian waters. Familiarity with Rules 5 (Lookout), 7 (Risk of Collision), 8 (Action to Avoid Collision), 13 (Overtaking), 14 (Head-on Situation), 15 (Crossing Situation), 16 (Action by Give-way Vessel), 17 (Action by Stand-on Vessel), and 18 (Responsibilities Between Vessels) is assumed for any operator using this feature.

SafeHelm is designed to reduce cognitive load during a busy watch — not to substitute for the trained seamanship that those rules require.

---

### Service Status and Reconnection

The SafeHelm service (`d3kos-safehelm`) runs continuously in the background on the Pi. The widget connects to it automatically when any d3kOS page loads. If the service is temporarily unavailable:

- The pill shows `⚠ SafeHelm` in orange
- The system attempts to reconnect every 5 seconds automatically
- No action is required from the operator — connection restores when the service recovers
- If the service remains offline, check **Settings → System Status** or use **Fix My Pi** to diagnose

To restart SafeHelm manually via the Pi terminal:

```
sudo systemctl restart d3kos-safehelm
```

---

*d3kOS User Manual — d3kOS v0.9.9.5 — Document version 2.9.0 — October 26, 2026*
*AtMyBoat.com — Open-source marine intelligence*
