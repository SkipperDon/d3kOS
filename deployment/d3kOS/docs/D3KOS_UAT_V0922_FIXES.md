# d3kOS v0.9.2.2 — UI Fix UAT
**Version:** 1.0.0
**Date:** 2026-03-18
**Owner:** Donald Moskaluk — AtMyBoat.com
**Purpose:** Verification checklist for the 8 UI fixes identified in the 2026-03-18 issue review.
**System:** Pi at 192.168.1.237:3000 — 10.1" touchscreen (primary), Windows browser (secondary)

---

## How to Use This Document

1. Work through each section in order on the Pi touchscreen
2. For every check: mark **PASS**, **FAIL**, or **SKIP**
3. If FAIL: write exactly what you see — one sentence is enough
4. If SKIP: write why (e.g. "engine not running")
5. Return the completed document when done — each FAIL gets investigated individually

---

## Pre-Test System Check

| # | Check | Result | Notes |
|---|-------|--------|-------|
| S-01 | Dashboard loads at home screen | | |
| S-02 | Status bar shows vessel name | | |
| S-03 | Clock is ticking | | |
| S-04 | AvNav iframe visible | | |
| S-05 | Signal K data showing (not `---`) | | |

**If S-01 fails — stop. Note the error and return this document.**

---

## Fix 1 — HELM Button Active State (I-05)

**What was wrong:** HELM button was always highlighted green — even when the overlay was closed.
**What should be true:** Only the currently active screen is highlighted. HELM only highlights when the HELM overlay is open.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F1-01 | Open dashboard (home screen) | Dashboard button highlighted. HELM button NOT highlighted. | | |
| F1-02 | Tap Weather | Weather button highlighted. All others not highlighted. | | |
| F1-03 | Tap Marine Vision | Marine Vision button highlighted. All others not highlighted. | | |
| F1-04 | Tap Boat Log | Boat Log button highlighted. All others not highlighted. | | |
| F1-05 | Return to Dashboard, tap HELM | HELM overlay opens AND HELM button highlights green. | | |
| F1-06 | Close HELM overlay | HELM button returns to inactive (not highlighted). Dashboard button highlights. | | |

---

## Fix 2 — HELM Software Mute (I-07)

**What was wrong:** No way to stop TTS mid-sentence.
**What should be true:** A mute toggle button inside the HELM overlay. Green speaker = talking active. Grey speaker = muted. Persists across page reload.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F2-01 | Open HELM overlay | Mute button visible inside overlay. Speaker icon shown. | | |
| F2-02 | Trigger a voice response (ask HELM something) | TTS speaks the response. | | |
| F2-03 | Tap mute button while TTS is speaking | TTS stops immediately. Speaker icon goes grey. | | |
| F2-04 | Trigger another voice response | HELM listens and processes but does NOT speak. | | |
| F2-05 | Tap mute button again | Speaker icon goes green. TTS resumes on next response. | | |
| F2-06 | Reload page, open HELM | Mute state is preserved from before reload. | | |

---

## Fix 3 — Close Buttons (I-08)

**What was wrong:** X buttons throughout app were too small, too light, too close to screen edges.
**What should be true:** All X buttons — 48×48px minimum, inset 24px from edges, dark background, white ✕, bold.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F3-01 | Open HELM overlay | X button is dark, large, clearly visible, inset from edge. Easy to tap. | | |
| F3-02 | Open More popup | X button meets same standard. | | |
| F3-03 | Open Settings | X / back button meets same standard. | | |
| F3-04 | Open Marine Vision | X / back button meets same standard. | | |
| F3-05 | Open Boat Log | X / back button meets same standard. | | |
| F3-06 | Any other overlay or modal | All X buttons consistent — dark, large, inset. | | |

---

## Fix 4 — Weather Page (I-11)

**What was wrong:** Weather conditions panel was lost in v0.9.2.2. Rebuild attempted incorrectly in v0.9.2.3.
**What should be true:** Full-screen weather page. Left side: radar image. Right side: conditions (wind, waves, pressure, temp, humidity, visibility). Day/night colour scheme. Countdown to next weather update. Back button returns to dashboard.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F4-01 | Tap Weather button | Full-screen weather page opens (not an overlay). | | |
| F4-02 | Left panel | Radar image displayed. | | |
| F4-03 | Right panel | Conditions visible: wind speed/direction/gusts, wave height, pressure, temperature, humidity, visibility. | | |
| F4-04 | Countdown | Timer shows time until next weather data refresh. Counting down. | | |
| F4-05 | Day/night | Colours match the dashboard day/night theme. | | |
| F4-06 | Back button | Visible, large, easy to tap. Returns to dashboard. | | |
| F4-07 | GPS | Weather data is for correct location (not default Lake Simcoe if GPS is locked). | | |

---

## Fix 5 — Leave App Dialog Removed (I-14 / I-15)

**What was wrong:** "Leave app? Changes you made may not be saved." dialog appeared on ALL page navigation and page reloads. Was never requested — introduced accidentally.
**What should be true:** No dialog appears — ever — when navigating between pages or reloading.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F5-01 | From Dashboard — tap Weather | No dialog. Page loads directly. | | |
| F5-02 | From Dashboard — tap Marine Vision | No dialog. Page loads directly. | | |
| F5-03 | From Dashboard — tap Boat Log | No dialog. Page loads directly. | | |
| F5-04 | From Dashboard — tap More → any item | No dialog. Page loads directly. | | |
| F5-05 | From any page — tap back/return | No dialog. Returns to dashboard directly. | | |
| F5-06 | Reload any page (browser refresh) | No dialog. Page reloads directly. | | |

---

## Fix 6 — Boat Log Fonts (I-16)

**What was wrong:** Boat Log page used different fonts inconsistent with the main dashboard.
**What should be true:** All Boat Log text uses Bebas Neue (headings/values) and Chakra Petch (labels/body), same as the main dashboard.

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F6-01 | Open Boat Log | Page heading uses Bebas Neue. | | |
| F6-02 | Log entry list | Entry titles and timestamps use Chakra Petch. | | |
| F6-03 | Buttons and labels | All buttons and labels use Chakra Petch. | | |
| F6-04 | Overall look | Boat Log visually matches the rest of the dashboard. | | |

---

## Fix 7 — Boat Log Auto Engine Capture (I-17)

**What was wrong:** Engine data was not automatically recorded in the Boat Log.
**What should be true:** When the engine is running, the Boat Log automatically records entries at: engine start, every 30 minutes while running, engine stop, and any alert threshold crossing (oil pressure low, coolant high, battery low).

| # | Step | What to Check | Result | Notes |
|---|------|---------------|--------|-------|
| F7-01 | Start engine | An ENGINE START entry appears in Boat Log automatically. Shows RPM, oil pressure, coolant temp, battery voltage, GPS. | | |
| F7-02 | Engine running 30 min | An ENGINE SNAPSHOT entry appears automatically. | | |
| F7-03 | Stop engine | An ENGINE STOP entry appears automatically. | | |
| F7-04 | Entry display | Engine entries show a distinct badge (ENGINE) vs voice entries (VOICE). | | |
| F7-05 | No engine | If engine is not running, no spurious entries appear. | | |

**SKIP acceptable if engine is not available for testing.**

---

## Fix 8 — Dropdowns Touch Size (I-18)

**What was wrong:** Select/dropdown fields too small to tap reliably on the 10.1" touchscreen.
**What should be true:** All dropdowns — minimum 52px height, 20px font size, proper padding. Easy to tap on first attempt.

| # | Page | Check | Result | Notes |
|---|------|-------|--------|-------|
| F8-01 | Settings | All dropdowns are large enough to tap easily on first attempt. | | |
| F8-02 | Setup/Onboarding | All dropdowns are large enough. | | |
| F8-03 | Boat Log | Any dropdowns (filter, type select) are large enough. | | |
| F8-04 | Any other page | No small dropdowns anywhere in the app. | | |

---

## Fix 9 — Font Consistency Across All Pages (I-19)

**What was wrong:** Not all pages used Bebas Neue / Chakra Petch. Some had fonts too large for the screen.
**What should be true:** All pages use Bebas Neue / Chakra Petch. Minimum sizes enforced: body 20px, labels 24px, instrument values 32px. No text below 20px.

| # | Page | Check | Result | Notes |
|---|------|-------|--------|-------|
| F9-01 | Settings | Fonts match dashboard — Bebas Neue / Chakra Petch. Nothing below 20px. | | |
| F9-02 | Upload Documents | Fonts match. | | |
| F9-03 | Manage Documents | Fonts match. | | |
| F9-04 | AI Navigation | Fonts match. | | |
| F9-05 | Engine Monitor | Fonts match. | | |
| F9-06 | Setup/Onboarding | Fonts match. | | |
| F9-07 | Boat Log | Fonts match (also covered by Fix 6). | | |
| F9-08 | Marine Vision | Fonts match. | | |

---

## Results Summary

Fill this in when all sections are complete.

| Fix | Issue | Result | Notes |
|-----|-------|--------|-------|
| Fix 1 | HELM button active state | | |
| Fix 2 | HELM software mute | | |
| Fix 3 | Close buttons | | |
| Fix 4 | Weather page | | |
| Fix 5 | Leave app dialog removed | | |
| Fix 6 | Boat Log fonts | | |
| Fix 7 | Boat Log engine capture | | |
| Fix 8 | Dropdowns touch size | | |
| Fix 9 | Font consistency all pages | | |

**Return this document when complete. Each FAIL will be investigated and fixed individually.**

---

*d3kOS v0.9.2.2 UI Fix UAT v1.0.0 — Donald Moskaluk / AtMyBoat.com — 2026-03-18*
