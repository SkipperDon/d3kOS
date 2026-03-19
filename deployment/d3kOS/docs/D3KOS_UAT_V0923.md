> ❌ CANCELLED — DO NOT USE
> v0.9.2.3 was abandoned 2026-03-18. This UAT document is void. Retained as historical record only.

# d3kOS v0.9.2.3 — User Acceptance Test (UAT)

**Version:** v0.9.2.3 | **Document:** UAT-001 **Created:** 2026-03-16 | **Owner:** Donald Moskaluk — AtMyBoat.com **Status:** DRAFT — awaiting execution


## Purpose

This document is a complete, self-contained UAT for d3kOS v0.9.2.3. It covers:

- How to access the system and start testing (onboarding)

- Every verification check for v0.9.2.3 (V-01 through V-16)

- Carryover items from v0.9.2.2 (INC-16, UAT metric/imperial, o-charts, Node-RED)

- How to record results

When complete, return this document. Each failed item will be investigated and a remediation plan produced.


## How to Use This Document

1. Work through each section in order

2. For every check: mark **PASS**, **FAIL**, or **SKIP** in the Result column

3. If FAIL: write exactly what you see in the Notes field (one sentence is enough)

4. If SKIP: write why (e.g. "engine not running", "no GPS lock")

5. Return the completed document when done


## Section 1 — Test Environment

### 1.1 Access Methods

**Option A — Pi Screen (preferred)** The 10.1" touchscreen at the helm. This is the primary display. All touch target tests must be done here.

**Option B — Windows Browser** Open any browser on your Windows machine and go to: `http://192.168.1.237:3000` Use this for reading text, checking fonts, and verifying layouts when not at the Pi.

### 1.2 Before You Start — System Check

On the Pi screen (or Windows browser), navigate to the dashboard home screen.

| \# | Check | Result | Notes |
| - | - | - | - |
| S-01 | Dashboard loads at home screen | PASS |  |
| S-02 | Status bar shows vessel name | PASS |  |
| S-03 | Clock is ticking | PASS |  |
| S-04 | AvNav iframe visible in chart pane | PASS |  |
| S-05 | Signal K connected (instrument cells show data, not `---`) | PASS |  |
| S-06 | All 6 bottom nav buttons visible: Dashboard / Weather / Marine Vision / HELM / Boat Log / More | FAIL  | All six buttons are visibile. If dashboard is active it should be highlighted only helm show its active but it is in dashboard mode. Further the expectation was that all icons on the button are not solid green unless they are active. Weather map has disappeared and it is not visible anymore. The vertical column does appear but again the fonts are too small.  |


**If S-01 or S-06 fail, stop — system is not ready for UAT. Note the error and return this document.**


## Section 2 — Onboarding (First-Run Wizard)

**Purpose:** Verify the setup wizard works for a new installation.

**How to trigger it:** The wizard appears automatically when `vessel.env` is absent. To test it manually without wiping your config, open a browser and go to: `http://192.168.1.237:3000/setup`

Work through each step. You do not need to submit — just verify each step displays correctly.

| \# | Step | What to Check | Result | Notes |
| - | - | - | - | - |
| OB-01 | Step 1 — Welcome | Title visible, progress dots show "STEP 1 OF 6", Next button present | PASS / FAIL / SKIP |  |
| OB-02 | Step 2 — Vessel Basics | Vessel Name, Home Port, Language fields present. All fields are large enough to tap. | PASS / FAIL / SKIP |  |
| OB-03 | Step 3 — Mobile Pairing | QR code displays. UUID text below QR is selectable. Skip button present. | PASS / FAIL / SKIP |  |
| OB-04 | Step 4 — Equipment | Engine model, chartplotter, VHF fields present. "Upload PDF Manuals" link opens `/upload-documents` in new tab. | PASS / FAIL / SKIP |  |
| OB-05 | Step 5 — Gemini Key | Password input field present. 3-step instruction text visible. "Skip for now" link present. | PASS / FAIL / SKIP |  |
| OB-06 | Step 6 — Done | Summary of what was configured vs skipped. LAUNCH button present. | PASS / FAIL / SKIP |  |
| OB-07 | All steps | Progress bar dots update as you move through steps | PASS / FAIL / SKIP |  |
| OB-08 | All steps | Text is readable — no text smaller than 18px visible | PASS / FAIL / SKIP |  |
| OB-09 | All steps | Tap targets — all buttons easy to tap with a finger (no tiny buttons) | PASS / FAIL / SKIP |  |



## Section 3 — Dashboard Home Screen

### 3.1 NAV Ribbon (Instrument Rows)

The instrument rows run across the top of the chart area. There are two rows: ENGINE row and NAV row.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-01 | Position label is top-aligned — sits at the top of its cell like SPEED, DEPTH, COURSE labels | Compare position cell label alignment with SOG cell label alignment | PASS / FAIL / SKIP |  |
| V-02 | Position numbers (lat/lon) are noticeably smaller than the SOG value | SOG shows a large number (e.g. "2.4"). Lat/lon should be roughly half that size. | PASS / FAIL / SKIP |  |
| V-03 | Next Waypoint label is top-aligned — same as other labels | Compare Next Waypoint cell label alignment with SPEED label | PASS / FAIL / SKIP |  |
| V-04 | Next Waypoint value (destination name or "NO ROUTE") is same size as lat/lon values | Compare text size visually | PASS / FAIL / SKIP |  |


### 3.2 Bottom Navigation Bar

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-05 | Tap Dashboard — only Dashboard button is highlighted. All others are not highlighted. | Tap each bottom nav button in turn. Only the one you tapped should be lit. | PASS / FAIL / SKIP |  |
| V-05b | HELM button is NOT highlighted by default when you first load the app | Load fresh. HELM should be dark, not highlighted. | PASS / FAIL / SKIP |  |
| V-06 | Weather button is the same width as the other 5 nav buttons | Eyeball all 6 buttons — should be evenly sized | PASS / FAIL / SKIP |  |


### 3.3 INC-16 — Font Size at Helm Distance (Carryover from v0.9.2.2)

Stand at normal helm position (approximately 1 metre from the screen).

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| INC-16a | Instrument labels (SOG, DEPTH, COURSE etc.) are readable at 1 metre | Stand back and read the labels without moving closer | PASS / FAIL / SKIP |  |
| INC-16b | Instrument values (numbers) are readable at 1 metre | Read the current SOG and DEPTH values from 1 metre | PASS / FAIL / SKIP |  |
| INC-16c | Bottom nav labels are readable at 1 metre | Read "Dashboard", "Weather", "Boat Log" etc. from 1 metre | PASS / FAIL / SKIP |  |
| INC-16d | Status bar text is readable at 1 metre | Read vessel name and clock from 1 metre | PASS / FAIL / SKIP |  |



## Section 4 — HELM Overlay

Tap the HELM button in the bottom nav.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-05c | HELM button is highlighted (lit) when HELM overlay is open | After tapping HELM, check that the HELM button is lit/highlighted | PASS / FAIL / SKIP |  |
| V-06a | HELM overlay opens — mic button and close button visible | Overlay should slide up or appear over the dashboard | PASS / FAIL / SKIP |  |
| V-07a | Close button (X) on HELM overlay is visible, dark, bold | X button should be easy to see — not light grey, not tiny | PASS / FAIL / SKIP |  |
| V-07b | Close button is not right at the screen edge — inset from the corner | X button should have clear space from the physical screen edge | PASS / FAIL / SKIP |  |
| V-07c | Close button tap target is large enough — easy to hit with a finger | Tap the X to close the overlay. Should close cleanly. | PASS / FAIL / SKIP |  |
| V-06b | After closing HELM overlay, HELM button is no longer highlighted | Close the overlay — HELM button should go back to dark/unlit | PASS / FAIL / SKIP |  |
| V-06c (Session C) | Mute button is visible inside HELM overlay | A speaker/mute icon or button is visible. Note: this is a Session C item — skip if not yet built. | PASS / FAIL / SKIP |  |
| V-06d (Session C) | Tap mute — HELM stops talking. Tap again — resumes. | Test mute toggle. Note: skip if Session C not yet built. | PASS / FAIL / SKIP |  |



## Section 5 — More Menu

Tap the More button in the bottom nav.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-08 | More popup icons are the same size as bottom nav icons | Compare the emoji/icons in the More popup with those in the bottom nav bar. They should match. | PASS / FAIL / SKIP |  |
| V-09 | More popup labels are the same size as bottom nav labels | Compare "AI Navigation" text size in More popup with "Dashboard" text in bottom nav. Should match. | PASS / FAIL / SKIP |  |
| V-07d | Close button (X) on More popup is visible, dark, bold, easy to tap | Same close button standard as HELM overlay | PASS / FAIL / SKIP |  |
| MO-01 | All 6 More menu items are present: AI Navigation, Engine Monitor, Initial Setup, Upload Documents, Manage Documents, Settings | Count the items | PASS / FAIL / SKIP |  |



## Section 6 — Weather Panel (Session C item)

**Note:** This is a Session C item. If Session C has not been built yet, mark all as SKIP.

Tap the Weather button in the bottom nav.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-10a | Weather panel slides in from the left side | Panel should appear on the LEFT, overlapping AvNav | PASS / FAIL / SKIP |  |
| V-10b | AvNav is still visible on the right side of the screen | The chart/AvNav should still be visible — panel is an overlay, not a replacement | PASS / FAIL / SKIP |  |
| V-10c | ENGINE and NAV instrument ribbons are still full width | The top instrument rows should not be narrowed or shifted | PASS / FAIL / SKIP |  |
| V-11a | Wind speed, direction, and gusts are displayed | Look for wind data in the panel | PASS / FAIL / SKIP |  |
| V-11b | Wave height, direction, and sea state are displayed | Look for wave/sea data in the panel | PASS / FAIL / SKIP |  |
| V-11c | Barometric pressure, temperature, humidity visible | Look for atmospheric data | PASS / FAIL / SKIP |  |
| V-11d | Weather alerts section present (may say "No active alerts" if clear) | Look for an alerts section at the top of the panel | PASS / FAIL / SKIP |  |
| V-13 | No "Leave app?" dialog when tapping Weather button | Tap Weather button. No browser "leave page?" popup should appear. | PASS / FAIL / SKIP |  |
| V-10d | Tap Weather button again — panel closes | Panel should slide back out | PASS / FAIL / SKIP |  |
| V-12 | (30-min test) After leaving panel open for 30 minutes, an entry appears in Boat Log | Check Boat Log after 30 min — should see a WEATHER entry | PASS / FAIL / SKIP |  |



## Section 7 — Marine Vision

Tap Marine Vision in the bottom nav.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| MV-01 | No "Leave app?" dialog when tapping Marine Vision from dashboard | Tap Marine Vision. No browser "leave page?" popup. | PASS / FAIL / SKIP |  |
| MV-02 | Page loads — camera grid or "no cameras" message visible | Page should display something, not a blank screen | PASS / FAIL / SKIP |  |
| MV-03 | Back button present and works — returns to dashboard | Tap back. Should return to dashboard without a dialog. | PASS / FAIL / SKIP |  |
| V-07e | Close/back button is visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 8 — Boat Log

Tap Boat Log in the bottom nav.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| V-13b | No "Leave app?" dialog when tapping Boat Log from dashboard | Tap Boat Log. No browser "leave page?" popup. | PASS / FAIL / SKIP |  |
| V-14a | Boat Log page uses same fonts as dashboard (Bebas Neue / Chakra Petch) | The headings and labels should look like the dashboard — not plain system font | PASS / FAIL / SKIP |  |
| V-14b | Text sizes on Boat Log match the dashboard — not smaller | Labels and values should be the same scale as the dashboard | PASS / FAIL / SKIP |  |
| BL-01 | Voice record button is present — large, easy to tap | The mic/record button should be prominent | PASS / FAIL / SKIP |  |
| BL-02 | Tap record — button turns red, timer starts | Recording indicator should be visible | PASS / FAIL / SKIP |  |
| BL-03 | Tap stop — entry appears in the log list | A new VOICE entry should appear | PASS / FAIL / SKIP |  |
| V-15 (Session D) | Engine entries appear in log (ENGINE badge) within 30 min of engine start | Note: Session D item — skip if not built. Start engine, wait, check log. | PASS / FAIL / SKIP |  |
| BL-04 | Entry type badges are distinct — VOICE / ENGINE / WEATHER / ALERT are different colours | Entries in the log should have visible type badges | PASS / FAIL / SKIP |  |
| V-07f | Back button is visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 9 — Settings Page

From More menu → tap Settings.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| ST-01 | Settings page loads — sections visible | Should see scrollable sections (System Status, Engine Config, Units, etc.) | PASS / FAIL / SKIP |  |
| ST-02 | Day/night theme from dashboard carries through to settings | If dashboard was in night mode, settings should also be in night mode | PASS / FAIL / SKIP |  |
| V-16a | All dropdowns on Settings page are large enough to tap with a finger | Tap any dropdown (e.g. Units, Language). Should open easily. No tiny selects. | PASS / FAIL / SKIP |  |
| V-16b | Dropdown height — options inside the dropdown are finger-friendly (not a tiny list) | Open a dropdown — the options should be easy to select | PASS / FAIL / SKIP |  |
| V-07g | Back/close button visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 10 — AI Navigation

From More menu → tap AI Navigation.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| AI-01 | Page loads — chat interface visible | Text input and send button should be present | PASS / FAIL / SKIP |  |
| AI-02 | Type a question and submit — response appears | Try: "What is a safe anchoring depth?" | PASS / FAIL / SKIP |  |
| AI-03 | Source badge visible on response (GEMINI or OLLAMA) | A badge or label should indicate which AI responded | PASS / FAIL / SKIP |  |
| V-16c | Text input field is large enough to tap | Tap the text input field — should be easy to hit | PASS / FAIL / SKIP |  |
| V-07h | Back button visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 11 — Engine Monitor

From More menu → tap Engine Monitor.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| EM-01 | Page loads — engine metrics visible (SOG, RPM, oil, coolant, battery, fuel) | 6 metric tiles should be visible | PASS / FAIL / SKIP |  |
| EM-02 | Values update — not static placeholder text | Values should change as Signal K data comes in (or show `---` if no engine data) | PASS / FAIL / SKIP |  |
| V-07i | Back button visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 12 — Upload Documents

From More menu → tap Upload Documents.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| UD-01 | Page loads — file upload form visible | Should see a file picker and submit button | PASS / FAIL / SKIP |  |
| V-16d | Any dropdowns or selects on this page are touch-friendly | Same dropdown check | PASS / FAIL / SKIP |  |
| V-07j | Back button visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 13 — Manage Documents

From More menu → tap Manage Documents.

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| MD-01 | Page loads — document list visible (or "no documents" message) | List or empty state should be shown | PASS / FAIL / SKIP |  |
| V-07k | Back button visible, dark, bold, easy to tap | Same close button standard | PASS / FAIL / SKIP |  |



## Section 14 — Metric vs Imperial (UAT — 10 users)

**Purpose:** Verify the system displays correctly in both unit systems.

**How to change units:** Settings → Units & Display → select Metric or Imperial → save.

### 14.1 Metric Configuration

Change units to **Metric**. Verify:

| \# | Check | Result | Notes |
| - | - | - | - |
| UAT-M01 | SOG shows knots or km/h (confirm which is selected) | PASS / FAIL / SKIP |  |
| UAT-M02 | DEPTH shows metres | PASS / FAIL / SKIP |  |
| UAT-M03 | Temperature shows °C (engine monitor) | PASS / FAIL / SKIP |  |
| UAT-M04 | Distance to waypoint shows km or nm | PASS / FAIL / SKIP |  |
| UAT-M05 | Data export includes `unit\_metadata` confirming metric | PASS / FAIL / SKIP |  |


### 14.2 Imperial Configuration

Change units to **Imperial**. Verify:

| \# | Check | Result | Notes |
| - | - | - | - |
| UAT-I01 | SOG shows knots | PASS / FAIL / SKIP |  |
| UAT-I02 | DEPTH shows feet | PASS / FAIL / SKIP |  |
| UAT-I03 | Temperature shows °F (engine monitor) | PASS / FAIL / SKIP |  |
| UAT-I04 | Distance to waypoint shows nm or miles | PASS / FAIL / SKIP |  |
| UAT-I05 | Data export includes `unit\_metadata` confirming imperial | PASS / FAIL / SKIP |  |



## Section 15 — o-charts (Don's task)

**Reference document:** `deployment/docs/OPENCPN\_FLATPAK\_OCHARTS.md` Access from Windows: `\\\\wsl.localhost\\Ubuntu\\home\\boatiq\\Helm-OS\\deployment\\docs\\OPENCPN\_FLATPAK\_OCHARTS.md`

| \# | Check | Result | Notes |
| - | - | - | - |
| OC-01 | OpenCPN launches from the Charts button on the dashboard | Tap Charts / More → OpenCPN. App should open. | PASS / FAIL / SKIP |
| OC-02 | o-charts plugin is visible in OpenCPN plugin manager | OpenCPN → Options → Plugins — look for oeSENC or o-charts | PASS / FAIL / SKIP |
| OC-03 | o-charts account connected — licensed charts visible | Charts for your area should be available | PASS / FAIL / SKIP |
| OC-04 | Chart renders on screen — no blank tiles | Navigate to your local area — tiles should load | PASS / FAIL / SKIP |



## Section 16 — Node-RED Status

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| NR-01 | Confirm whether Node-RED is intentionally inactive | Go to Settings → System Status. Is Node-RED listed as down? | PASS / FAIL / SKIP |  |
| NR-02 | If inactive is NOT intentional: note what error or status is shown | Write exact status message in Notes | PASS / FAIL / SKIP |  |



## Section 17 — AODA / Accessibility Spot Check

| \# | Check | How to Verify | Result | Notes |
| - | - | - | - | - |
| AO-01 | All buttons and tap targets feel comfortable to tap with a finger — no fumbling required | Work through all pages — note any button that requires precision tapping | PASS / FAIL / SKIP |  |
| AO-02 | No text on any page requires squinting or leaning closer than 1 metre | Work through all pages at arm's length | PASS / FAIL / SKIP |  |
| AO-03 | Night mode is readable in low light — green on black, no washed-out colours | Switch to night mode (N key or D/N button). Check all pages. | PASS / FAIL / SKIP |  |
| AO-04 | Day mode is readable in bright light — no glare or low-contrast text | Switch to day mode. Check all pages. | PASS / FAIL / SKIP |  |



## Section 18 — Issue Log

Use this table to record any issues found that do not have a specific check above, or to add extra detail to failed checks.

| \# | Page / Feature | What you saw | Severity (High / Med / Low) |
| - | - | - | - |
| ISS-01 |  |  |  |
| ISS-02 |  |  |  |
| ISS-03 |  |  |  |
| ISS-04 |  |  |  |
| ISS-05 |  |  |  |
| ISS-06 |  |  |  |
| ISS-07 |  |  |  |
| ISS-08 |  |  |  |


**Severity guide:**

- **High** — feature does not work or is unusable

- **Med** — feature works but has a visible problem

- **Low** — cosmetic issue, minor sizing or alignment


## Section 19 — Summary

When you have finished, fill in this summary and return the document.

| Field | Value |
| - | - |
| Test date |  |
| Tester |  |
| Unit configuration tested | Metric / Imperial / Both |
| Total checks | 74 |
| PASS |  |
| FAIL |  |
| SKIP |  |
| High severity issues |  |
| Med severity issues |  |
| Low severity issues |  |
| Overall verdict | READY FOR RELEASE / NEEDS FIXES |
| Comments |  |



## Appendix — Session C and D Items (Not Yet Built)

The following checks are marked "Session C" or "Session D" in this document. They cannot be tested until those sessions are implemented. They are included here so the full UAT can be run in one pass after all sessions are complete.

| Check | Session | Description |
| - | - | - |
| V-06c, V-06d | C | HELM mute button |
| V-10 through V-12 | C | Weather overlay panel |
| V-15 | D | Engine auto-capture in boat log |
| V-14 (full) | D | Boat log font overhaul |
| BL-04 | D | Entry type badges |



*UAT-001 · d3kOS v0.9.2.3 · Donald Moskaluk · AtMyBoat.com* *Return completed document to Claude Code for issue investigation and remediation planning.*

