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

---

## GAP ANALYSIS — Phases 1–9

### Phase 1 (index.html) — 3 missing button-labels
The following tiles exist in index.html and were not included in the Phase 1 target list:
- "Voice AI" → data-i18n="ui.voice_ai"
- "Manuals" → data-i18n="ui.manuals"
- "Export Data" → data-i18n="ui.export_data"

### Phase 8 (onboarding.html) — onboarding namespace
Phase 8 uses keys like onboarding.welcome, onboarding.wizard_complete, onboarding.select_engine,
onboarding.engine_model. These exist in the translations file under the "onboarding" namespace
(confirmed present in en.json). No action needed.

### Phases 2–7, 9 — no gaps found

---

## EMOJI + TRANSLATION PATTERN (applies to all phases)

Elements with emoji prefixes require the span-wrap pattern to preserve the emoji when
i18n.js sets textContent:

Before: `<h1>📱 QR Code Pairing</h1>`
After:  `<h1>📱 <span data-i18n="ui.qr_pairing">QR Code Pairing</span></h1>`

The emoji sits outside the span as a literal character. i18n.js only touches the span textContent.
Apply this pattern wherever an emoji precedes translatable text.

Back button arrow pattern (same principle):
Before: `<a class="nav-button">← Main Menu</a>`
After:  `<a class="nav-button">← <span data-i18n="ui.back">Back</span></a>`

---

## PLACEHOLDER NOTE — history.html search box

i18n.js already supports data-i18n-placeholder (confirmed in /var/www/html/js/i18n.js).
Use: `<input data-i18n-placeholder="ui.search_placeholder" ...>`
Key: ui.search_placeholder = "Search conversations..."

---

## ELEMENTS SKIPPED — REASON LOG

| File | Element / Text | Reason skipped |
|------|---------------|----------------|
| history.html | "View and search past AI conversations" | No matching key, do not invent |
| history.html | "No conversations found" | JS-generated innerHTML, rule 4 |
| history.html | "Failed to load conversations..." | JS-generated innerHTML, rule 4 |
| history.html | "📋 Copy", "🔄 Re-ask", "🗑️ Delete" | JS-generated innerHTML, rule 4 |
| history.html | "🌐 Online", "💻 Onboard" badges | JS-generated innerHTML, rule 4 |
| upload-manual.html | "Add manuals, regulations..." subtitle | No matching key, do not invent |
| upload-manual.html | "Regulations" option | No matching key, do not invent |
| upload-manual.html | "Upload and Process Manual" submit button | JS sets textContent dynamically, rule 4 |
| upload-manual.html | All li info-box items | No matching keys, do not invent |
| qrcode.html | `<p class="qr-description">Scan this QR code...` | Long description, no matching key |
| qrcode.html | `<div id="installation-id">Loading...</div>` | JS-populated, rule 4 |
| qrcode.html | `<li>System IP: <strong id="system-ip">...` | Contains dynamic JS-populated child, rule 4 |
| qrcode.html | `<li>Web Interface: ...` | Contains hardcoded IP, skip |
| qrcode.html | Manual step 3 IP address line | Contains inline HTML, rule 4 |
| qrcode.html | Manual step 4 Installation ID line | JS-populated child, rule 4 |

---

## PHASE 10: history.html — i18n-history

Wire data-i18n onto conversation history page static text elements.
Status: COMPLETE — deployed 2026-03-11

Elements wired (8 data-i18n + 1 data-i18n-placeholder):
- `<div class="page-title">` → data-i18n="ui.history"
- `<a class="nav-button">← ...` → span-wrap: `← <span data-i18n="ui.back">Back</span>`
- `<span>Total:</span>` → data-i18n="ui.total"
- `<span>Online:</span>` → data-i18n="ui.online_label"
- `<span>Onboard:</span>` → data-i18n="ui.onboard_label"
- filter-button All → data-i18n="ui.filter_all"
- filter-button Online Only → data-i18n="ui.filter_online"
- filter-button Onboard Only → data-i18n="ui.filter_onboard"
- search-box input → data-i18n-placeholder="ui.search_placeholder"
- `<div class="loading">` → data-i18n="ui.loading"
- Added `<script src="/js/i18n.js"></script>`

---

## PHASE 11: upload-manual.html — i18n-upload-manual

Wire data-i18n onto upload manual page static text elements.
Status: COMPLETE — deployed 2026-03-11

Elements wired (10):
- `<h1 class="page-title">📄 ...` → span-wrap: `📄 <span data-i18n="ui.manuals">Upload Manual</span>`
- `<a class="nav-button">← ...` → span-wrap: `← <span data-i18n="ui.back">Back</span>`
- `<label class="form-label">Manual Type` → data-i18n="ui.manual_type"
- option Boat Manual → data-i18n="ui.manual_boat"
- option Engine Manual → data-i18n="ui.manual_engine"
- option Electronics Manual → data-i18n="ui.manual_electronics"
- option Safety Equipment Manual → data-i18n="ui.manual_safety"
- `<label class="form-label">Select PDF File` → data-i18n="ui.select_file"
- file-input-button → data-i18n="ui.choose_file"
- info-box h3 → data-i18n="ui.upload_info_title"
- Added `<script src="/js/i18n.js"></script>`

---

## PHASE 12: qrcode.html — i18n-qrcode

Wire data-i18n onto QR code pairing page static text elements.
Status: COMPLETE — deployed 2026-03-11

Elements wired (20):
- `<h1>📱 ...` → span-wrap: `📱 <span data-i18n="ui.qr_pairing">QR Code Pairing</span>`
- `<p class="subtitle">` → data-i18n="ui.qr_subtitle"
- back button → span-wrap: `← <span data-i18n="ui.back">Back</span>`
- share config button → data-i18n="ui.share_config"
- `<h2 class="qr-title">` → data-i18n="ui.qr_scan_title"
- regenerate button → span-wrap with data-i18n="ui.qr_regenerate"
- download button → span-wrap with data-i18n="ui.qr_download"
- print button → span-wrap with data-i18n="ui.qr_print"
- Connection Details span → data-i18n="ui.connection_details"
- System Information span → data-i18n="ui.system_info"
- Direct Connection URL span → data-i18n="ui.direct_url"
- How to Connect h3 → span-wrap with data-i18n="ui.qr_how_to_connect"
- QR step 1–5 .step-text spans → data-i18n="ui.qr_step_1" through qr_step_5
- Manual Connection h3 → span-wrap with data-i18n="ui.qr_manual_connect"
- Manual step 1, 2, 5 .step-text spans → data-i18n="ui.qr_manual_step_1/2/5"
- Added `<script src="/js/i18n.js"></script>`

---

## PHASE 13: initial-setup.html — i18n-initial-setup

Status: BLOCKED — file not found in repo or on Pi. Phase cannot proceed until file is located.
