# 	d3kOS Alerts & Notifications Reference

**Version:** v0.9.9.5 · **Created:** 2026-11-25 · **Source:** alert\_watcher.py, ai-bridge services, notification\_manager.py, app.js, rss\_feed.py

This document catalogues every alert and notification in d3kOS: what triggers it, every channel it uses, timing from trigger to delivery, and — for the AtMyBoat.com app — whether it is a push notification, an in-app message, or a sound.


## Delivery Channel Definitions

| Symbol | Channel | What it is |
| - | - | - |
| 🖥 | **On-Screen (dashboard)** | Visible overlay, card, pill, banner, or instrument change on the d3kOS Pi display |
| 🔊 | **Voice (TTS)** | Audio spoken through the vessel speaker (Anker S330 or any USB audio) via espeak-ng |
| 📱 | **AtMyBoat.com / App** | Action taken in or by the mobile PWA at atmyboat.com/app |
| 📡 | **RSS Feed** | Appears as an item in the `/rss` XML feed (last 50 events, entries pruned after 1 hour) |
| 📓 | **Boat Log** | Written as an entry to the digital captain's log |
| 📨 | **Telegram** | Sent via Telegram Bot API (marine-vision only) |


### App Channel Sub-Types (📱)

The AtMyBoat.com PWA does **not** send OS-level push notifications to the phone. The app must be open and polling to receive updates. All app delivery types are:

| App Sub-Type | What it means |
| - | - |
| **In-app — badge** | A red number badge on the Alerts screen tab increments. Only visible when the app is open. |
| **In-app — alert list** | The alert appears on the Alerts screen (tappable list). Only when app is open. |
| **In-app — vessel card** | The vessel status card on the home screen shows latest 3 alerts inline. Only when app is open. |
| **In-app — status dot** | The vessel's online/offline dot changes. Only when app is open. |
| **In-app — firmware banner** | An "Update available" banner appears on the vessel card. Only when app is open. |
| **Email** | An email is sent by HostPapa `alert-notify.php` to the account holder's email address. This arrives even when the app is closed. Server-side rate limit: 1 email per alert type per device per 15 minutes. |


> **Summary:** Only emails break through when the app is closed. All other app channels are passive — they update when the user opens the app.


## Alert & Notification Matrix

### 1. Anchor Drag

**Trigger:** Vessel has moved beyond the set watch radius (10–100 m, default 25 m) for 3 consecutive position checks.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Two locations: (a) **Anchor Drag Widget** — floating card with drift distance, bearing, speed, AI advice button, dismiss button; (b) **Anchor Watch page** — full-screen red flashing alarm overlay with animated ring and drift figure. |
| 🔊 Voice | ✅ Yes — URGENT | Immediate: *"Anchor drag detected. Anchor drag detected. Vessel has moved \[X\] metres from anchor position. Check your position immediately."* Pre-written — fires with zero AI wait. Prefaced with *"Captain, standby."* Repeats every 60 seconds (up to 10 repetitions) until operator dismisses. |
| 📱 App — Email | ✅ Yes | Email to account holder's email address. Rate limited: 1 per 15 min. Configurable via quiet hours and per-type toggle in user-preferences.json. |
| 📱 App — Alert List | ✅ Yes | Appears in the Alerts screen list once logged to issues.db and exported. |
| 📱 App — Vessel Card | ✅ Yes | Latest alert shows inline on vessel home card (up to 3 shown). |
| 📡 RSS Feed | ✅ Yes | Appears as RSS item at `/rss` from issues.db. Pruned after 1 hour. |
| 📓 Boat Log | ⬜ Not direct | Not auto-written to boat log. The drag event is logged to `/opt/d3kos/logs/anchor-events/` JSON files only. |


**Timing:**

- Drag confirmation: 3 polls × 15-second interval = **~45 seconds** from actual drag until alarm fires.

- Voice fires within 1 second of confirmation.

- Screen alert fires within 1 second of confirmation (via SSE push).

- Email: alert\_watcher.py polls issues.db every **30 seconds** → HostPapa API call → email delivered in **30–90 seconds** from alarm.

- RSS: same 30-second poll cycle.


### 2. Collision Risk (SafeHelm / COLREGs)

**Trigger:** AIS target detected that meets a COLREGs give-way, stand-on, head-on, overtaking, or Rule 18 obligation. CPA (Closest Point of Approach) is computed live against each AIS vessel. Three tiers: advisory, warning, critical.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **SafeHelm pill** in every page header updates continuously. Advisory = green count. Warning = yellow/orange pill with `!`. Critical = flashing red pill with `⚠`. Tap to expand panel showing each vessel's MMSI, COLREGs rule label (Head-On, Give-Way, Stand-On, Overtaken, Overtaking, R18 Give-Way), CPA in metres, ACK and dismiss buttons. |
| 🔊 Voice | ✅ Yes — URGENT | Fires when Node-RED or SafeHelm posts to `/webhook/alert`. Urgent sequence: *"Captain, standby."* → 4-second pause → alert message (repeated 2× for critical severity). |
| 📱 App — Email | ✅ Yes | Category `collision\_risk`. Email on critical/warning alerts per alert\_watcher.py rules. Rate limited 15 min. |
| 📱 App — Alert List | ✅ Yes | Via issues.db export. |
| 📡 RSS Feed | ✅ Yes | Via issues.db. |
| 📓 Boat Log | ⬜ No | Not written to boat log. |


**Timing:**

- SafeHelm SSE stream is live: pill updates within **2–5 seconds** of an AIS target entering a COLREGs zone.

- Voice: dependent on Node-RED webhook firing — typically **2–10 seconds** after SafeHelm detects the condition.

- Email: **30–90 seconds** via alert\_watcher.py → HostPapa.


### 3. Engine Oil Pressure — Critical

**Trigger:** Oil pressure reading from Signal K falls below the critical threshold (default: 20 PSI; configurable in Settings).

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Critical Engine Screen** — full-screen red takeover with current value, safe range (45–65 PSI), immediate action text ("Reduce to idle immediately"), and two buttons: ACKNOWLEDGE and ENGINE IS OFF — STOP ALERTING. |
| 🔊 Voice | ✅ Yes — URGENT | Via `/webhook/alert` or Node-RED. Urgent TTS with "Captain, standby." prefix. |
| 📱 App — Email | ✅ Yes | Category `engine\_oil\_pressure`. Email on critical/warning. |
| 📱 App — Alert List | ✅ Yes | Via issues.db export. |
| 📡 RSS Feed | ✅ Yes | Via issues.db. |
| 📓 Boat Log | ✅ Yes | `boatlog\_capture.py` logs engine readings (RPM, oil pressure, coolant, fuel) on a timed schedule. The current reading at the time of capture will appear in the boat log. |


**Timing:**

- Signal K WebSocket delivers readings in real time. `instruments.js` threshold check runs on every incoming message: **\< 2 seconds** from actual engine event to on-screen critical alert.

- Boat log capture: written on the boatlog\_capture.py schedule (interval-based, not event-driven).

- Email: **30–90 seconds** via alert\_watcher.py.


### 4. Engine Overtemperature

**Trigger:** Coolant temperature exceeds the warning threshold (configurable in Settings).

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **AI Engine Diagnostic Card** (right-click coolant cell) or **Critical Engine Screen** at critical threshold. Instrument cell changes colour. |
| 🔊 Voice | ✅ Yes — URGENT | Via `/webhook/alert`. Urgent TTS. |
| 📱 App — Email | ✅ Yes | Category `engine\_overtemp`. Rate limited 15 min. |
| 📱 App — Alert List | ✅ Yes | Via issues.db. |
| 📡 RSS Feed | ✅ Yes | Via issues.db. |
| 📓 Boat Log | ✅ Yes | Via boatlog\_capture.py scheduled engine snapshot. |


**Timing:** Same as oil pressure — \< 2 seconds on-screen, 30–90 seconds for email.


### 5. Low Fuel

**Trigger:** Fuel tank level falls below the alert threshold (configurable in Settings → Alerts).

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Fuel cell in Engine ribbon changes colour. Alert card may appear via AI bridge. |
| 🔊 Voice | ✅ Yes — URGENT | Via `/webhook/alert`. |
| 📱 App — Email | ✅ Yes | Category `low\_fuel`. Rate limited 15 min. |
| 📱 App — Alert List | ✅ Yes | Via issues.db. |
| 📡 RSS Feed | ✅ Yes | Via issues.db. |
| 📓 Boat Log | ✅ Yes | Via boatlog\_capture.py engine snapshot includes fuel level. |


**Timing:** \< 2 seconds on-screen. 30–90 seconds email.


### 6. GPS Lost

**Trigger:** Signal K stops reporting a valid GPS position (navigation.position path goes null or stale).

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Nav ribbon cells show `---`. Route AI Strip shows "Waiting for GPS". Windy weather embed stops updating position. Anchor Watch cannot set anchor. |
| 🔊 Voice | ✅ Yes — URGENT | Via `/webhook/alert` from self-healing agent. |
| 📱 App — Email | ✅ Yes | Category `gps\_lost`. Rate limited 15 min. |
| 📱 App — Alert List | ✅ Yes | Via issues.db. |
| 📡 RSS Feed | ✅ Yes | Via issues.db. |
| 📓 Boat Log | ⬜ Not direct | Boat log captures engine data, not GPS state. |


**Timing:** On-screen: immediate (Signal K WebSocket stream dies or returns null — instruments.js detects within 1–5 seconds). Email: 30–90 seconds.


### 7. Port Arrival Briefing

**Trigger:** Vessel is within 2.0 nautical miles of the active AvNav destination waypoint AND Speed Over Ground \> 0.5 knots. (Also manually triggerable via Node-RED `/webhook/arrival`.) Fires only once per unique destination per session.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Port Arrival Banner** — floating card with destination name, ETA/distance, structured briefing (fuel dock, marina contact, customs, anchorage, provisioning, approach hazards). "Full Briefing in AI" button opens split pane. |
| 🔊 Voice | ✅ Yes — Normal | Immediate stage-1 audio (no AI wait): *"Approaching \[destination\]. \[X\] nautical miles. Port arrival briefing ready on screen."* The full AI briefing is displayed on screen only. |
| 📱 App | ⬜ No | Not sent to the app. Briefing is an on-vessel advisory only. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not auto-logged. |


**Timing:**

- Port arrival monitor polls every **60 seconds**.

- Stage-1 voice fires within 1 second of detection.

- AI briefing (Gemini API call): **5–30 seconds** after trigger, then displayed on screen.

- Worst case from crossing the 2 nm threshold to full on-screen briefing: **60–90 seconds** (60s poll + 30s Gemini response).


### 8. Route Analysis Update (AI First Officer)

**Trigger:** Background service analyses the active AvNav route every 5 minutes automatically. Also triggerable manually by tapping the GEMINI badge on the Route AI Strip.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Route AI Strip** (above chart on main dashboard) updates with AI-generated route advisory text. State indicator shows ANALYZING → ACTIVE/OFFLINE AI. |
| 🔊 Voice | ⬜ No | No voice for routine route updates. |
| 📱 App | ⬜ No | Not sent to the app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not logged. |


**Timing:** Auto-trigger every **5 minutes**. Manual trigger is near-instant to start. AI response (Gemini): **5–30 seconds**. Update appears on screen as soon as the response arrives.


### 9. AI First Officer Situational Alert (AIS / COLREGs triggered by AI Bridge)

**Trigger:** AI bridge pushes a custom alert via `/webhook/alert` from Node-RED, SafeHelm, or the self-healing agent. This is the general-purpose urgent alert path.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **AI Alert Card** modal — shows alert title, full advisory paragraph (e.g. "AIS target MV ONTARIO SPIRIT converging bearing 047° — CPA 0.18nm in 4 minutes"), three buttons: ACKNOWLEDGE, ASK AI MORE, Dismiss. Also updates **ticker tape** at top of dashboard with the alert message. |
| 🔊 Voice | ✅ Yes — URGENT | Full urgent sequence: *"Captain, standby."* → 4-second pause → alert text (repeated 2× for critical severity, 1× for info/warning). |
| 📱 App | ⬜ No | Not directly sent to app unless the alert also logs to issues.db. |
| 📡 RSS Feed | ⬜ No | Not in RSS unless logged to issues.db. |
| 📓 Boat Log | ⬜ No | Not auto-logged. |


**Timing:** Voice and screen alert fire within **1–2 seconds** of the webhook POST.


### 10. OTA Firmware Update Available

**Trigger:** The OTA agent detects a newer d3kOS version on atmyboat.com. Also shows when an OTA install has failed.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Update Notice Bar** — amber bar between the status bar and instrument panel. Shows version number and "visit atmyboat.com to upgrade". Changes red on install failure. Dismissible per session. |
| 🔊 Voice | ⬜ No | No voice for OTA updates. |
| 📱 App — Firmware Banner | ✅ Yes | **In-app only** — a "Firmware update available" banner appears on the vessel status card when the app is open and polling. No push notification or email. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not logged. |


**Timing:** Dashboard polls `/update/status` on a timed interval (periodic). App shows the banner when it next polls the vessel heartbeat/status endpoint. No real-time push.


### 11. Fish / Marine Object Detection (Marine Vision)

**Trigger:** Operator taps "Run Detection Now" on the Marine Vision page, OR automatic detection when the camera service has a configured detection schedule. Fish capture recorded with species, confidence, GPS location, and applicable regulations.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Marine Vision page** — detection results panel shows species name, confidence %, each detected class and score. |
| 🔊 Voice | ⬜ No | No voice alert for fish detection. |
| 📱 App | ⬜ Not direct | Not pushed to the AtMyBoat.com PWA. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not auto-written to boat log. |
| 📨 Telegram | ✅ Yes | **Telegram Bot message** via `notification\_manager.py`. Message includes: 🎣 Fish capture header, capture ID, timestamp, species + confidence %, GPS coordinates with Google Maps link, applicable fishing regulations (size limit, bag limit, season, legal status). Optional: photo attached if a still was captured. Retry on failure (up to 3 attempts, 5-second retry delay). |


**Timing:** Manual: immediate on tap. Telegram delivery: **1–10 seconds** after detection (3-retry queue with 5s delay on failure, up to 30 seconds timeout per attempt).


### 12. Voyage Summary Ready

**Trigger:** The VoyageLogger background service completes a voyage GPX track summarisation (auto, or via `/summarize-voyage` API). This generates a Gemini-powered narrative summary of the trip.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Voyage Notice banner** appears in the AI Nav tab split pane: *"New voyage summary ready — see Settings \> Voyage Summaries."* |
| 🔊 Voice | ⬜ No | No voice for voyage summaries. |
| 📱 App | ⬜ No | Not sent to the app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not written to boat log. |


**Timing:** Triggered after voyage end is detected (vessel stops making way). AI summary generation (Gemini API): **5–30 seconds**. Screen notice appears within 1 second of summary arriving via SSE.


### 13. Self-Healing System Health Alert

**Trigger:** The self-healing agent (`self-healing/` service) detects a system-level issue: service crash, resource exhaustion, failed health check, etc. Issues are written to `issues.db` with severity (critical or warning) and category.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ⬜ Not direct | Not pushed to the dashboard directly. Engine Monitor page → Network Status section shows service state (running/stopped). Settings → System Status shows all service indicators. |
| 🔊 Voice | ✅ Conditional | If the self-healing agent posts to `/webhook/alert`, TTS fires. Not all issues trigger voice. |
| 📱 App — Email | ✅ Yes | All critical issues and high-priority warning categories email the account holder via `alert-notify.php`. Rate limited 15 min per type. |
| 📱 App — Alert List | ✅ Yes | All issues appear in the Alerts screen in the app via the export pipeline. |
| 📡 RSS Feed | ✅ Yes | The `/rss` feed is sourced directly from `issues.db`. Every new issue appears as an RSS item. Pruned after 1 hour. |
| 📓 Boat Log | ⬜ No | Not written to boat log. |


**Timing:**

- alert\_watcher.py polls `issues.db` every **30 seconds**.

- When a new critical/priority-warning alert is found: immediate export triggered to `export-manager` (`:8094`), then cloud email via HostPapa.

- Export cooldown: 2-minute minimum between consecutive export triggers (prevents alert storms).

- Email delivery: **30–90 seconds** from issue appearing in DB.

- RSS: **30 seconds** (next poll cycle by any RSS reader).

**Alert categories that trigger immediate export + email:** `anchor\_drag` · `engine\_overtemp` · `engine\_oil\_pressure` · `low\_fuel` · `gps\_lost` · `collision\_risk`

All other categories: appear in RSS and app alert list via scheduled export (no immediate email).


### 14. Vessel Online / Offline Status

**Trigger:** The d3kos-heartbeat service pings atmyboat.com every 5 minutes with the device token and API key. If `last\_seen\_at` is not updated, the vessel shows as offline on the app after a timeout period.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ⬜ No | Not shown on the Pi dashboard. |
| 🔊 Voice | ⬜ No | No voice. |
| 📱 App — Status Dot | ✅ Yes | **In-app only** — green online dot or grey offline dot on the vessel home card. Updates when app polls the vessel status endpoint. |
| 📱 App — Vessel Card | ✅ Yes | "Last seen" timestamp shown on vessel card. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not in boat log. |


**Timing:** Heartbeat fires every **5 minutes**. App status dot updates on the next poll when the app is open.


### 15. Anchor Watch Activated / Cleared

**Trigger:** Operator taps SET ANCHOR or CLEAR on the Anchor Watch page.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Status pill in Anchor Watch page header changes from INACTIVE → WATCHING or back. Canvas map activates. |
| 🔊 Voice | ✅ Yes — Normal | On set: *"Anchor set. Watching within \[X\] metres."* On activate via API: *"Anchor watch active. Radius: \[X\] metres."* Normal priority (queued after any in-progress speech). |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not in boat log. |


**Timing:** Immediate — voice fires within 1 second of the SET ANCHOR tap.


### 16. Engine State Change (ON / OFF / UNKNOWN) \[eng:on pill\]

**Trigger:** RPM data from Signal K or manual POST to `/engine/state`. When RPM is detected, the state is set to RUNNING and persisted to `engine-state.json`. On startup, if Signal K shows no propulsion namespace after 30 seconds, state auto-clears to UNKNOWN (BUG-349 fix).

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Engine State Chip** in the row toggle bar beside the ENGINE button shows RUNNING (green) or ON. |
| 🔊 Voice | ⬜ No | No voice for engine state changes. |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ✅ Yes | `boatlog\_capture.py` logs engine readings that include RPM. Engine on/off transitions are implicit in the log entries. |



### 17. AI Engine Diagnostic (Operator-Requested)

**Trigger:** Operator right-clicks any instrument cell and selects an action, OR taps "Run Diagnostics" on the Helm Assistant page.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **AI Engine Diagnostic card** — full overlay with engine data grid + Gemini analysis paragraph. Action buttons: REDUCE TO 1800 RPM, FULL AI BRIEF, MONITOR & DISMISS. |
| 🔊 Voice | ⬜ No | No voice — text response only. |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Not auto-logged. |


**Timing:** Gemini API call: **5–30 seconds**. Card appears immediately (loading state) and fills when AI responds.


### 18. Helm Voice Listening (Wake Word / Mic Tap)

**Trigger:** Wake word detected by the voice assistant, OR operator taps the HELM button or mic icon.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | **Helm Listening Overlay** — full-screen animated ring, audio-level bars, "HELM IS LISTENING" title, hint text, mute toggle, cancel button. |
| 🔊 Voice | ✅ Yes | Helm speaks responses aloud (normal priority). If an urgent alert fires mid-answer, Helm is interrupted by "Captain, standby." then the alert, then "Captain, ask the question again. We were interrupted." |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ⬜ No | Helm queries are not auto-logged ("QUERIES NOT STORED" label shown in UI). |


**Timing:** Wake word detection latency: **\< 1 second** (on-device wake word model). Full AI response latency: **1–15 seconds** depending on query type (local engine lookup vs. RAG vs. Gemini).


### 19. Boatlog Voice Entry (Operator-Recorded)

**Trigger:** Operator taps "TAP TO RECORD" on the Boat Log page, speaks, then stops recording.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Recording timer and transcript preview shown in real-time. Entry appears in log list after save. |
| 🔊 Voice | ⬜ No | No TTS response (operator is speaking, not receiving). |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ✅ Yes | The voice transcript and timestamp are written as a log entry. |


**Timing:** Transcription is performed server-side via the boatlog API after recording stops. Entry appears in the log within **2–5 seconds** of stopping.


### 20. Boatlog Engine Auto-Capture

**Trigger:** `boatlog\_capture.py` runs on a timed schedule and writes engine readings to the log automatically whenever the vessel is operating.

| Channel | Delivery | Detail |
| - | - | - |
| 🖥 On-Screen | ✅ Yes | Auto-captured engine entries appear in the Boat Log entry list. |
| 🔊 Voice | ⬜ No | No voice. |
| 📱 App | ⬜ No | Not sent to app. |
| 📡 RSS Feed | ⬜ No | Not in RSS. |
| 📓 Boat Log | ✅ Yes | RPM, oil pressure, coolant temperature, fuel level written as a timestamped engine entry. |


**Timing:** Schedule-based (interval configurable in service config). Not event-driven.


## Summary Table — All Alerts at a Glance

| Alert | 🖥 Screen | 🔊 Voice | 📱 App Email | 📱 App In-App | 📡 RSS | 📓 Boat Log | 📨 Telegram | Latency (worst case) |
| - | - | - | - | - | - | - | - | - |
| Anchor Drag | ✅ Widget + full-screen | ✅ Urgent — repeats every 60s | ✅ Email | ✅ Alert list | ✅ | ⬜ | ⬜ | Screen/Voice: 45s. Email: 90s |
| Collision Risk (SafeHelm) | ✅ Pill flashing | ✅ Urgent — via webhook | ✅ Email | ✅ Alert list | ✅ | ⬜ | ⬜ | Screen: 2–5s. Voice/Email: 90s |
| Engine Oil Pressure Critical | ✅ Full-screen takeover | ✅ Urgent | ✅ Email | ✅ Alert list | ✅ | ✅ Capture | ⬜ | Screen: \<2s. Email: 90s |
| Engine Overtemperature | ✅ Diagnostic card | ✅ Urgent | ✅ Email | ✅ Alert list | ✅ | ✅ Capture | ⬜ | Screen: \<2s. Email: 90s |
| Low Fuel | ✅ Cell colour + card | ✅ Urgent | ✅ Email | ✅ Alert list | ✅ | ✅ Capture | ⬜ | Screen: \<2s. Email: 90s |
| GPS Lost | ✅ Nav cells blank | ✅ Urgent | ✅ Email | ✅ Alert list | ✅ | ⬜ | ⬜ | Screen: 1–5s. Email: 90s |
| Port Arrival Briefing | ✅ Arrival banner | ✅ Normal — stage 1 immediate | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | Screen stage 1: 60–90s. Full briefing: +30s |
| Route Analysis Update | ✅ Route AI strip | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 5–10 min (5-min cycle + AI) |
| AI First Officer Alert | ✅ Alert card + ticker | ✅ Urgent | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 1–2s |
| OTA Update Available | ✅ Update bar | ⬜ | ⬜ | ✅ Firmware banner | ⬜ | ⬜ | ⬜ | App: next poll |
| Fish Detection | ✅ Results panel | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ✅ Photo + data | Telegram: 1–30s |
| Voyage Summary Ready | ✅ Notice in AI tab | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 1s after AI returns |
| System Health Alert | ⬜ | ✅ Conditional | ✅ Email | ✅ Alert list | ✅ | ⬜ | ⬜ | Email: 30–90s |
| Vessel Online / Offline | ⬜ | ⬜ | ⬜ | ✅ Status dot | ⬜ | ⬜ | ⬜ | App: next poll |
| Anchor Watch Set / Clear | ✅ Status pill | ✅ Normal — confirmation | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | Immediate |
| Engine State (eng:on pill) | ✅ State chip | ⬜ | ⬜ | ⬜ | ⬜ | ✅ Capture | ⬜ | Immediate |
| AI Engine Diagnostic | ✅ Diagnostic card | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 5–30s (AI response) |
| Helm Listening | ✅ Listening overlay | ✅ Normal — Helm responds | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | Wake word: \<1s. AI: 1–15s |
| Boatlog Voice Entry | ✅ Entry in log | ⬜ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | 2–5s (transcription) |
| Boatlog Engine Capture | ✅ Entry in log | ⬜ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | Schedule-based |



## Voice Alert Priority Reference

The speech queue has two priority lanes. Urgent alerts interrupt normal speech.

| Priority | Used for | Sequence |
| - | - | - |
| **Urgent** | Anchor drag, collision risk, engine critical, GPS lost, any critical webhook alert | *"Captain, standby."* → 4-second pause → alert text. Repeated 2× for critical severity. If Helm was answering, adds: *"Captain, ask the question again. We were interrupted."* |
| **Normal** | Anchor set confirmation, port arrival stage 1, Helm responses, anchor watch activated | Queued behind any in-progress speech. Plays when queue reaches it. |


**Mute state:** If the operator has muted Helm (via the HELM listening overlay mute button), all TTS is suppressed. Mute state persists to `tts-mute.json` and survives service restarts.


## App Email Alert Configuration

Operators can configure email alerts per device via `/opt/d3kos/config/user-preferences.json`:

| Setting | Effect |
| - | - |
| `alert\_prefs.email: false` | Disables all email alerts for this device |
| `alert\_prefs.enabled\_types: \[...\]` | Per-category whitelist — only listed categories send email |
| `alert\_prefs.quiet\_hours.start/end/tz` | No emails during quiet hours (except critical severity — bypasses quiet hours) |


**Server-side rate limit:** 1 email per alert type per device per 15 minutes (enforced at HostPapa `alert-notify.php`). This prevents email floods during sustained conditions.


*Document generated from live service source. Update when new alert types are added or delivery channels change.*

