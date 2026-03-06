# i18n Page Wiring — Feature Spec

## Overview

Add `data-i18n="<key>"` attributes to visible text elements on each page.
The shared `/js/i18n.js` loader is already injected into all pages — it reads
`data-i18n` attributes and replaces textContent with the correct translation.

## How it works
- `data-i18n="ui.dashboard"` → textContent set to translations["ui"]["dashboard"]
- `data-i18n="ui.back"` → textContent set to translations["ui"]["back"]
- `data-i18n="alerts.high_temp"` → textContent set to translations["alerts"]["high_temp"]
- English text stays in the HTML as fallback — NEVER remove the existing text
- ONLY add the `data-i18n` attribute to the existing element — do not change any other attributes

## Available ui keys (use EXACTLY these key names)
dashboard, navigation, weather, marine_vision, charts, helm, benchmark, voice_ai,
manuals, export_data, boat_log, settings, network, camera, language, engine_status,
back, confirm, save, cancel, connect, disconnect, scanning, loading, offline, no_data,
refresh, start, stop, open, close, no_gps, position, speed, heading, depth, course,
start_trip, stop_trip, pause_trip, resume_trip, new_entry, voice_note, export,
voice_wake, section_engine, section_camera, section_network, section_language,
section_units, section_system, section_ai, listening, processing, ready

## Rules — READ CAREFULLY
1. Add `data-i18n="ui.<key>"` attribute to the ELEMENT that contains the text
2. NEVER change the element's existing text — it stays as English fallback
3. NEVER change tag names, class names, ids, onclick, or any other attributes
4. NEVER add data-i18n to elements whose text is dynamic (loaded via JS fetch)
5. NEVER add data-i18n to script tags, style tags, or SVG elements
6. Only add data-i18n where the text EXACTLY MATCHES one of the available keys
7. If no key matches a text element, leave that element alone — do not invent keys
8. Output format: one FIND_LINE/ACTION/CODE block per element change
9. The FIND_LINE must be the EXACT current line from the file — single line only

---

## PHASE 1: index.html — i18n-index

Wire data-i18n onto the main menu tile button-label spans.

Target elements — `<span class="button-label">` elements only:
- "Dashboard" → data-i18n="ui.dashboard"
- "Navigation" → data-i18n="ui.navigation"
- "Weather" → data-i18n="ui.weather"
- "Boat Log" → data-i18n="ui.boat_log"
- "Marine Vision" → data-i18n="ui.marine_vision"
- "Charts" → data-i18n="ui.charts"
- "Settings" → data-i18n="ui.settings"
- "Helm" → data-i18n="ui.helm"
- "Benchmark" → data-i18n="ui.benchmark"
- "Network" → data-i18n="ui.network"

For each target, replace ONLY the `<span class="button-label">Text</span>` line
with `<span class="button-label" data-i18n="ui.key">Text</span>`.

---

## PHASE 2: dashboard.html — i18n-dashboard

Wire data-i18n onto section title h2 elements and the back/settings nav button.

Target elements:
- `<h2 class="section-title">⚙️ Engine Metrics</h2>` → add data-i18n="ui.section_engine" (keep emoji)
- `<h2 class="section-title">💧 Tank Levels</h2>` → no matching key, skip
- `<h2 class="section-title">🖥️ System Status</h2>` → no matching key, skip
- Any back button with text "Back" → data-i18n="ui.back"
- Any "Settings" nav button text span → data-i18n="ui.settings"
- "Loading..." text elements → data-i18n="ui.loading"

---

## PHASE 3: navigation.html — i18n-navigation

Wire data-i18n onto nav data label divs.

Target elements — `<div class="nav-label">` elements:
- "Speed Over Ground" → data-i18n="ui.speed"
- "Course Over Ground" → data-i18n="ui.course"
- "Heading (True)" → data-i18n="ui.heading"
- "Depth Below Surface" → data-i18n="ui.depth"
- "Position" → data-i18n="ui.position"
- Any "No GPS Fix" text → data-i18n="ui.no_gps"
- Any "Back" button text → data-i18n="ui.back"

---

## PHASE 4: weather.html — i18n-weather

Wire data-i18n onto weather page labels.

Target elements:
- "Loading..." text elements → data-i18n="ui.loading"
- "Back" button text → data-i18n="ui.back"
- Any "Offline" text elements → data-i18n="ui.offline"
- Any "No Data" text elements → data-i18n="ui.no_data"
- "Refresh" button text → data-i18n="ui.refresh"

---

## PHASE 5: marine-vision.html — i18n-marine-vision

Wire data-i18n onto marine vision labels.

Target elements:
- "Loading..." text elements → data-i18n="ui.loading"
- "Back" button text → data-i18n="ui.back"
- Any "Offline" text elements → data-i18n="ui.offline"
- Any "Camera" label text → data-i18n="ui.camera"

---

## PHASE 6: boatlog.html — i18n-boatlog

Wire data-i18n onto boatlog action buttons.

Target elements — button text spans or button text content:
- "Start Trip" button text → data-i18n="ui.start_trip"
- "Stop Trip" button text → data-i18n="ui.stop_trip"
- "Pause Trip" button text → data-i18n="ui.pause_trip"
- "🎤 Voice Note" button — keep emoji, add data-i18n="ui.voice_note" to inner text span if present
- "Export" button text → data-i18n="ui.export"
- "Back" button text → data-i18n="ui.back"
- "New Entry" button text → data-i18n="ui.new_entry"

---

## PHASE 7: settings.html — i18n-settings

Wire data-i18n onto settings section header h2 elements.

Target elements — `<h2 class="section-header">` elements:
- Any containing "Engine Configuration" → add data-i18n="ui.section_engine"
- Any containing "Camera Settings" → add data-i18n="ui.section_camera"
- Any containing "Network Settings" → add data-i18n="ui.section_network"
- Any containing "Language Settings" → add data-i18n="ui.section_language"
- Any containing "AI Assistant" → add data-i18n="ui.section_ai"
- Any containing "System Actions" → add data-i18n="ui.section_system"
- "Back" button text → data-i18n="ui.back"
- "Save" button text → data-i18n="ui.save"
- "Cancel" button text → data-i18n="ui.cancel"

---

## PHASE 8: onboarding.html — i18n-onboarding

Wire data-i18n onto onboarding wizard text elements.

Target elements:
- "Welcome to d3kOS" heading → data-i18n="onboarding.welcome"
- "Setup Complete" text → data-i18n="onboarding.wizard_complete"
- "Select Engine Manufacturer" label/text → data-i18n="onboarding.select_engine"
- "Engine Model" label/text → data-i18n="onboarding.engine_model"
- "Continue" or "Next" button text → data-i18n="ui.confirm"
- "Back" button text → data-i18n="ui.back"
- "Cancel" button text → data-i18n="ui.cancel"
- "Save" button text → data-i18n="ui.save"

---

## PHASE 9: helm.html — i18n-helm

Wire data-i18n onto helm assistant status text elements.

Target elements:
- Status text showing "Listening..." → data-i18n="ui.listening"
- Status text showing "Processing..." → data-i18n="ui.processing"
- Status text showing "Ready" or "Helm ready" → data-i18n="ui.ready"
- "Back" button text → data-i18n="ui.back"
- "Settings" nav text → data-i18n="ui.settings"
