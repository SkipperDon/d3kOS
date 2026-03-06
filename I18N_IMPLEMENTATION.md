# d3kOS Multi-Language (i18n) Implementation
## Instructions for Claude Code

> **Read this entire file before writing any code.**
> This feature was designed by Claude (claude.ai) with full knowledge of the
> d3kOS architecture from MASTER_SYSTEM_SPEC.md. Follow these instructions
> exactly to avoid common pitfalls.

---

## What Was Built & Why

A multi-language (i18n) system for d3kOS supporting **18 languages** targeted
at global pleasure boating markets. The language list was researched against
actual boating geography — NOT a generic language list. Do not change the
languages without reading `doc/I18N_MARKET_RESEARCH.md` first.

**Languages (in priority order):**
`en` `fr` `it` `es` `el` `hr` `tr` `de` `nl` `sv` `no` `da` `fi` `pt` `ar` `zh` `ja` `uk`

Arabic (`ar`) is the only RTL language — the HTML must set `dir="rtl"` on
`<html>` when Arabic is active.

---

## Architecture — Read This Before Touching Anything

### The Critical Rule: No Filesystem Fetches from Chromium

d3kOS uses Chromium to render all HTML UI pages. **Chromium running on the
Pi 4B cannot `fetch()` local filesystem paths.** This means:

```javascript
// ❌ THIS WILL FAIL — Chromium blocks filesystem access
fetch('/opt/d3kos/config/i18n/en.json')
fetch('file:///opt/d3kos/config/i18n/en.json')

// ✅ THIS IS CORRECT — go through Flask
fetch('http://localhost:8101/api/i18n/en')
```

Every translation lookup, language preference read, and language preference
write goes through the Flask settings service on **port 8101**. This is the
same pattern already used by the Network Settings UI (Session F in MASTER_SYSTEM_SPEC).

### Where Everything Lives

```
/opt/d3kos/
├── ui/
│   └── language-menu.html          ← The language selector page (provided)
├── config/
│   ├── onboarding.json             ← ADD "language" and "dir" fields here
│   └── i18n/
│       ├── en.json                 ← Create all 18 of these
│       ├── fr.json
│       ├── it.json
│       ├── es.json
│       ├── el.json
│       ├── hr.json
│       ├── tr.json
│       ├── de.json
│       ├── nl.json
│       ├── sv.json
│       ├── no.json
│       ├── da.json
│       ├── fi.json
│       ├── pt.json
│       ├── ar.json
│       ├── zh.json
│       ├── ja.json
│       └── uk.json
└── services/
    └── settings/
        └── language_api.py         ← ADD to the existing Flask settings service
```

### Existing Service to Extend

The Flask settings service already exists at port 8101 (Session F —
`d3kos-settings` systemd service). **Do not create a new service.**
Add the language endpoints to the existing Flask app file.

---

## Step-by-Step Implementation

### Step 1 — Create the i18n Directory

```bash
sudo mkdir -p /opt/d3kos/config/i18n
sudo chown d3kos:d3kos /opt/d3kos/config/i18n
```

### Step 2 — Create Translation JSON Files

Create one JSON file per language in `/opt/d3kos/config/i18n/`.

**Required schema — every file must follow this exact structure:**

```json
{
  "lang_code": "en",
  "lang_name": "English",
  "native_name": "English",
  "dir": "ltr",
  "ui": {
    "dashboard":     "Dashboard",
    "engine_status": "Engine Status",
    "boat_log":      "Boat Log",
    "settings":      "Settings",
    "network":       "Network",
    "camera":        "Camera",
    "voice_wake":    "Helm",
    "back":          "Back",
    "confirm":       "Confirm",
    "save":          "Save",
    "cancel":        "Cancel",
    "connect":       "Connect",
    "disconnect":    "Disconnect",
    "scanning":      "Scanning...",
    "loading":       "Loading..."
  },
  "alerts": {
    "high_temp":     "High Engine Temperature",
    "low_oil":       "Low Oil Pressure",
    "low_voltage":   "Low Battery Voltage",
    "gps_lost":      "GPS Signal Lost",
    "ais_offline":   "AIS Offline",
    "disk_low":      "Low Disk Space",
    "cpu_high":      "CPU Temperature Critical"
  },
  "onboarding": {
    "welcome":         "Welcome to d3kOS",
    "select_engine":   "Select Engine Manufacturer",
    "engine_model":    "Engine Model",
    "engine_year":     "Engine Year",
    "cylinders":       "Number of Cylinders",
    "wizard_complete": "Setup Complete"
  },
  "voice": {
    "listening":   "Listening...",
    "processing":  "Processing...",
    "ready":       "Helm ready"
  }
}
```

**Arabic ONLY — set `"dir": "rtl"`**. All other languages use `"ltr"`.

**Translation files to create:**

| Code | Language   | Notes |
|------|------------|-------|
| en   | English    | Default — must be complete and perfect |
| fr   | French     | |
| it   | Italian    | |
| es   | Spanish    | |
| el   | Greek      | Verify marine terminology with native speaker |
| hr   | Croatian   | |
| tr   | Turkish    | |
| de   | German     | Watch for compound word text overflow |
| nl   | Dutch      | |
| sv   | Swedish    | |
| no   | Norwegian  | |
| da   | Danish     | |
| fi   | Finnish    | Longest words — check UI layout |
| pt   | Portuguese | |
| ar   | Arabic     | RTL — dir must be "rtl" |
| zh   | Chinese    | Simplified (Mandarin) |
| ja   | Japanese   | |
| uk   | Ukrainian  | Cyrillic script |

> ⚠️ **Marine terminology warning:** Do not blindly machine-translate terms
> like "Boat Log", "AIS", "NMEA", "Helm", "Engine Gateway". These have
> specific nautical meanings. Flag any uncertain translations with a
> `// NEEDS_REVIEW` comment in the JSON so native speakers can verify.

### Step 3 — Add Language Fields to onboarding.json

The existing `/opt/d3kos/config/onboarding.json` needs two new fields.
Add them without removing existing fields:

```python
# Read existing config, add fields, write back
import json, os

config_path = '/opt/d3kos/config/onboarding.json'
with open(config_path, 'r') as f:
    config = json.load(f)

# Only add if not already present
if 'language' not in config:
    config['language'] = 'en'
if 'dir' not in config:
    config['dir'] = 'ltr'

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

### Step 4 — Add API Endpoints to Existing Flask Settings Service

Find the existing Flask settings service file (look for the file that handles
port 8101, likely in `/opt/d3kos/services/settings/`). Add these routes:

```python
import json
import os
from flask import jsonify, request, send_from_directory

# Directory where translation JSON files live
I18N_DIR      = '/opt/d3kos/config/i18n'
ONBOARDING    = '/opt/d3kos/config/onboarding.json'
UI_DIR        = '/opt/d3kos/ui'

# Supported language codes — update this list if adding new languages
SUPPORTED_LANGUAGES = [
    'en','fr','it','es','el','hr','tr','de','nl',
    'sv','no','da','fi','pt','ar','zh','ja','uk'
]

def load_onboarding():
    """Load onboarding.json — returns dict, never raises."""
    try:
        with open(ONBOARDING, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_onboarding(config):
    """Save onboarding.json atomically."""
    tmp = ONBOARDING + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ONBOARDING)


# ── SERVE THE LANGUAGE SELECTION PAGE ────────────────────────────────────
@app.route('/language')
def language_page():
    """Serve the language selection HTML page."""
    return send_from_directory(UI_DIR, 'language-menu.html')


# ── GET CURRENT LANGUAGE ─────────────────────────────────────────────────
@app.route('/api/language', methods=['GET'])
def get_language():
    """Return the currently selected language code and direction."""
    config = load_onboarding()
    return jsonify({
        'language': config.get('language', 'en'),
        'dir':      config.get('dir', 'ltr')
    })


# ── SET LANGUAGE ─────────────────────────────────────────────────────────
@app.route('/api/language', methods=['POST'])
def set_language():
    """
    Save language preference to onboarding.json.
    Body: { "language": "fr", "dir": "ltr" }
    """
    data = request.get_json(silent=True) or {}
    lang = data.get('language', 'en')

    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': f'Unsupported language: {lang}'}), 400

    # Determine RTL — only Arabic is RTL
    direction = 'rtl' if lang == 'ar' else 'ltr'

    config = load_onboarding()
    config['language'] = lang
    config['dir']      = direction
    save_onboarding(config)

    return jsonify({'status': 'ok', 'language': lang, 'dir': direction})


# ── SERVE TRANSLATION JSON FILE ───────────────────────────────────────────
@app.route('/api/i18n/<lang_code>')
def get_translation(lang_code):
    """
    Serve a translation JSON file from /opt/d3kos/config/i18n/<lang_code>.json
    Chromium cannot fetch files directly from disk, so Flask serves them.
    """
    if lang_code not in SUPPORTED_LANGUAGES:
        return jsonify({'error': f'Unsupported language: {lang_code}'}), 404

    filepath = os.path.join(I18N_DIR, f'{lang_code}.json')

    if not os.path.exists(filepath):
        # Fall back to English if the requested file doesn't exist yet
        filepath = os.path.join(I18N_DIR, 'en.json')
        if not os.path.exists(filepath):
            return jsonify({'error': 'Translation file not found'}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=3600'  # Cache 1hr on Pi
    return response


# ── LIST AVAILABLE LANGUAGES ──────────────────────────────────────────────
@app.route('/api/languages')
def list_languages():
    """Return list of languages that have translation files installed."""
    available = []
    for code in SUPPORTED_LANGUAGES:
        path = os.path.join(I18N_DIR, f'{code}.json')
        if os.path.exists(path):
            available.append(code)
    return jsonify({'languages': available, 'total': len(available)})
```

### Step 5 — Copy the UI File

```bash
sudo cp language-menu.html /opt/d3kos/ui/language-menu.html
sudo chown d3kos:d3kos /opt/d3kos/ui/language-menu.html
sudo chmod 644 /opt/d3kos/ui/language-menu.html
```

### Step 6 — Restart the Settings Service

```bash
sudo systemctl restart d3kos-settings
sudo systemctl status d3kos-settings   # verify it started cleanly
```

### Step 7 — Test the Endpoints

```bash
# Test API is alive
curl http://localhost:8101/api/language

# Expected: {"dir":"ltr","language":"en"}

# Test translation file serving
curl http://localhost:8101/api/i18n/en

# Expected: full JSON with ui/alerts/onboarding/voice objects

# Test setting a language
curl -X POST http://localhost:8101/api/language \
  -H "Content-Type: application/json" \
  -d '{"language": "fr"}'

# Expected: {"dir":"ltr","language":"fr","status":"ok"}

# Verify it persisted
curl http://localhost:8101/api/language
# Expected: {"dir":"ltr","language":"fr"}

# Test the page loads
curl -I http://localhost:8101/language
# Expected: HTTP/1.1 200 OK

# Test Arabic RTL
curl -X POST http://localhost:8101/api/language \
  -H "Content-Type: application/json" \
  -d '{"language": "ar"}'
curl http://localhost:8101/api/language
# Expected: {"dir":"rtl","language":"ar"}

# Reset to English
curl -X POST http://localhost:8101/api/language \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

### Step 8 — Add to Settings Navigation

Add a link to the language page from the existing d3kOS Settings menu.
The link should open: `http://localhost:8101/language`

In Node-RED Dashboard, add a UI Button or link node pointing to that URL.

### Step 9 — Verify Font Coverage on Pi 4B

```bash
# Check Noto fonts are installed (needed for Arabic, CJK, Greek, Cyrillic)
fc-list | grep -i noto | grep -E "(Arabic|CJK|Devanagari)" | head -10

# If missing, install:
sudo apt install fonts-noto fonts-noto-cjk fonts-noto-extra -y

# Verify Chromium will find them:
fc-match "Noto Sans Arabic"
fc-match "Noto Sans CJK SC"
```

---

## Adding a New Language Later

When a user requests a new language:

1. Add the language code to `SUPPORTED_LANGUAGES` in `language_api.py`
2. Create `/opt/d3kos/config/i18n/<code>.json` using the schema above
3. Add the language to the `languages` array in `language-menu.html`
4. Run `sudo systemctl restart d3kos-settings`
5. Test with `curl http://localhost:8101/api/i18n/<code>`

No reboot required. The page picks up new languages on next load.

---

## What NOT to Do

- **Do NOT** create a new systemd service for language. Use port 8101.
- **Do NOT** use `fetch()` with filesystem paths in any HTML file.
- **Do NOT** hardcode translations in HTML/JS — all strings come from JSON.
- **Do NOT** remove existing fields from `onboarding.json` when adding language fields.
- **Do NOT** use machine translation for marine-specific terms without review.
- **Do NOT** assume all languages fit in the same button width — Finnish and German produce very long strings. Test overflow.
- **Do NOT** forget `"ensure_ascii": False` when writing JSON files with non-Latin scripts.

---

## Files Provided in This PR

| File | Destination on Pi | Description |
|------|------------------|-------------|
| `ui/language-menu.html` | `/opt/d3kos/ui/language-menu.html` | Language selector page — do not modify fetch() calls |
| `services/settings/language_api.py` | Add to existing Flask settings service | API endpoints |
| `config/i18n/en.json` | `/opt/d3kos/config/i18n/en.json` | English translations (reference/template) |
| (remaining 17 .json files) | `/opt/d3kos/config/i18n/` | One per language |

---

## Verification Checklist

Before marking this feature complete, verify:

- [ ] `curl http://localhost:8101/api/language` returns current language
- [ ] `curl http://localhost:8101/api/i18n/en` returns full JSON
- [ ] `curl http://localhost:8101/api/i18n/ar` returns `"dir": "rtl"`
- [ ] Page loads in Chromium at `http://localhost:8101/language`
- [ ] Selecting a language and clicking Confirm saves to `onboarding.json`
- [ ] Language persists after `sudo systemctl restart d3kos-settings`
- [ ] Language persists after full Pi reboot
- [ ] Arabic switches page to RTL layout
- [ ] All 18 language flags and names display correctly
- [ ] Demo preview panel updates when switching languages
- [ ] Back button returns to `http://localhost:1880/dashboard`
- [ ] Noto fonts installed and rendering Arabic/CJK/Greek/Cyrillic correctly
- [ ] Error banner appears (not crash) if Flask service is stopped
- [ ] No console errors in Chromium DevTools

---

## Systemd Service Reference

The settings service that must be running:

```bash
# Service name (check actual name in your system):
systemctl status d3kos-settings
# or
systemctl status d3kos-network   # Session F name may differ

# Logs:
journalctl -u d3kos-settings -f

# Restart after code changes:
sudo systemctl restart d3kos-settings
```

---

*Designed by Claude (claude.ai) — March 2026*
*Architecture based on MASTER_SYSTEM_SPEC.md — SkipperDon/d3kOS*
