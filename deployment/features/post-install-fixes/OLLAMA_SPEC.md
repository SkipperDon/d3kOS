# d3kOS Post-Install Bug Fix Specification
**Version:** 1.0 | **Date:** 2026-03-04 | **Target:** Ollama `qwen3-coder:30b` on workstation `192.168.1.36`
**Pi:** `d3kos@192.168.1.237` | **Web root:** `/var/www/html/` | **Services:** `/opt/d3kos/services/`

---

## Purpose

This specification defines 13 bug fixes and UI improvements identified after first full functional test of d3kOS v0.9.5. Claude Code is planner/reviewer. Ollama is implementer. Each fix is self-contained with exact file paths, current behaviour, required behaviour, and acceptance criteria.

---

## Engineering Standards (apply to every fix)

- Python services: Flask, systemd-managed, `User=d3kos`, `Restart=on-failure`
- HTML/JS: no frameworks, vanilla JS, touch-friendly (minimum 48px tap targets)
- Error handling: never crash on missing data — show user-friendly fallback
- Sudoers changes: add `NOPASSWD` only for specific commands, never `ALL`
- All new API endpoints: return `{ "success": bool, ... }` JSON
- Test with `curl` before declaring done

---

## Fix 1 — Dashboard: SignalK Disconnected Banner

**File:** `/var/www/html/dashboard.html`
**Current behaviour:** When SignalK is offline, dashboard shows blank engine data with no explanation.
**Required behaviour:** Yellow banner appears at top of page with message and link to Settings.

### Implementation

In `dashboard.html`, add to `<head>` CSS:
```css
#signalk-banner {
  display: none;
  background: #FF8C00;
  color: #000;
  padding: 16px 20px;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 999;
}
#signalk-banner a {
  color: #000;
  text-decoration: underline;
  margin-left: 12px;
}
```

Add to top of `<body>`:
```html
<div id="signalk-banner">
  ⚠️ Signal K is offline — engine data unavailable.
  <a href="/settings.html#system-actions">Go to Settings → Restart Signal K</a>
</div>
```

Add JS function (runs every 5s):
```javascript
function checkSignalK() {
  fetch('/signalk/v1/api/', { signal: AbortSignal.timeout(3000) })
    .then(r => {
      document.getElementById('signalk-banner').style.display = r.ok ? 'none' : 'block';
    })
    .catch(() => {
      document.getElementById('signalk-banner').style.display = 'block';
    });
}
checkSignalK();
setInterval(checkSignalK, 5000);
```

**Acceptance:** Disconnect SignalK (`sudo systemctl stop signalk`), reload dashboard — banner appears. Restart SignalK — banner disappears within 5s.

---

## Fix 2 — Engine Benchmark: Diagnose and Fix

**Files to investigate:** `/var/www/html/` (benchmark page), `/opt/d3kos/services/` (benchmark API)
**Current behaviour:** Engine Benchmark page is non-functional.
**Required behaviour:** Benchmark displays engine data baseline comparison.

### Investigation steps (run on Pi)
```bash
# Find benchmark page and API
ls /var/www/html/ | grep -i bench
systemctl status d3kos-health --no-pager
curl -s http://localhost:8085/health/status | python3 -m json.tool
# Check what port benchmark uses
grep -r 'benchmark\|8085\|8086' /opt/d3kos/services/ --include="*.py" -l
```

### Fix
1. Identify the broken API call or service
2. Fix the root cause (missing service, wrong port, wrong endpoint)
3. If service is stopped, start it and ensure it's enabled
4. If data is missing, verify SignalK is feeding health service

**Acceptance:** Benchmark page loads with data. No console errors.

---

## Fix 3 — Export: Race Condition at Boot

**Files:**
- `/opt/d3kos/scripts/export-daily.sh`
- `/opt/d3kos/scripts/export-on-boot.sh`
- `/etc/systemd/system/d3kos-export-daily.service`

**Current behaviour:** `export-daily.sh` exits with code 7 (curl ECONNREFUSED) at boot because tier API (port 8093) isn't listening yet when the script runs.

**Required behaviour:** Scripts wait for APIs to be ready before proceeding.

### Fix `export-daily.sh` — add retry before tier check

Replace the tier check block:
```bash
# OLD (fails if tier API not ready)
TIER_STATUS=$(curl -s http://localhost:8093/tier/status)

# NEW — wait up to 30s for tier API
wait_for_api() {
  local url="$1" max=10 i=0
  while [ $i -lt $max ]; do
    if curl -sf "$url" > /dev/null 2>&1; then return 0; fi
    i=$((i+1)); sleep 3
  done
  return 1
}

if ! wait_for_api "http://localhost:8093/tier/status"; then
  log "⚠ Tier API not available after 30s — skipping export"
  exit 0
fi
TIER_STATUS=$(curl -s http://localhost:8093/tier/status)
```

### Fix `d3kos-export-daily.service` — add ordering

In `[Unit]` section, add:
```ini
After=network-online.target d3kos-export-manager.service d3kos-tier-api.service
```

**Acceptance:** Reboot Pi. `systemctl status d3kos-export-daily` shows `active (exited)` not `failed`.

---

## Fix 4 — Navigation: GPS Readings Not Showing

**File:** `/var/www/html/navigation.html`
**Current behaviour:** GPS fields blank even when GPS has a fix.
**Required behaviour:** Speed, heading, COG, SOG, position all display when GPS fix available.

### Investigation
```bash
# Check SignalK has GPS data
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/speedOverGround
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/headingTrue
```

### Required data paths (in navigation.html JS)
| Display field | SignalK path |
|---|---|
| Latitude | `navigation/position` → `.value.latitude` |
| Longitude | `navigation/position` → `.value.longitude` |
| Speed Over Ground | `navigation/speedOverGround` → `.value` (m/s → knots: × 1.944) |
| Heading True | `navigation/headingTrue` → `.value` (radians → degrees: × 180/π) |
| Course Over Ground | `navigation/courseOverGroundTrue` → `.value` (radians → degrees) |
| Depth | `environment/depth/belowKeel` → `.value` |

### Fix
1. Verify JS fetch URLs match the paths above
2. Fix any path mismatches
3. Add "No GPS" placeholder text when position is null (instead of blank)
4. Add satellite count display from gpsd `SKY` class if available

**Acceptance:** With GPS connected and active: all fields populate. With no GPS fix: fields show `--` not blank.

---

## Fix 5 — Boatlog: Voice Note Feature

**Files:**
- `/var/www/html/boatlog.html`
- `/opt/d3kos/services/boatlog-api.py` (or equivalent)

**Current behaviour:** No voice note capability in boatlog.
**Required behaviour:** User can tap mic icon, record voice note, it transcribes and saves with the log entry.

### Backend: Add to boatlog API

```python
import os, wave, datetime
from flask import request, jsonify

VOICE_NOTE_DIR = '/opt/d3kos/data/boatlog-audio'
os.makedirs(VOICE_NOTE_DIR, exist_ok=True)

@app.route('/boatlog/voice-note', methods=['POST'])
def save_voice_note():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400
    audio = request.files['audio']
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'voice_note_{ts}.webm'
    path = os.path.join(VOICE_NOTE_DIR, filename)
    audio.save(path)
    # Transcription via Vosk (best-effort — return empty if Vosk unavailable)
    transcript = ''
    try:
        transcript = transcribe_audio(path)
    except Exception:
        pass
    return jsonify({'success': True, 'filename': filename, 'transcript': transcript, 'timestamp': ts})
```

### Frontend: Add mic button to boatlog.html

Add microphone button near the Add Entry form:
```html
<button id="voice-note-btn" onclick="startVoiceNote()" style="font-size:32px; padding:16px; min-width:64px;">🎤</button>
<span id="voice-note-status" style="font-size:16px;"></span>
```

```javascript
let mediaRecorder = null;
let audioChunks = [];

async function startVoiceNote() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    document.getElementById('voice-note-btn').textContent = '🎤';
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const fd = new FormData();
    fd.append('audio', blob, 'voice_note.webm');
    const res = await fetch('/boatlog/voice-note', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.transcript) {
      document.getElementById('log-notes').value += (document.getElementById('log-notes').value ? '\n' : '') + data.transcript;
      document.getElementById('voice-note-status').textContent = '✓ Transcribed';
    } else {
      document.getElementById('voice-note-status').textContent = '✓ Saved (no transcript)';
    }
    stream.getTracks().forEach(t => t.stop());
  };
  mediaRecorder.start();
  document.getElementById('voice-note-btn').textContent = '⏹';
  document.getElementById('voice-note-status').textContent = 'Recording...';
}
```

**Acceptance:** Tap mic → tap stop → note appears in text field → save entry → audio file exists in `/opt/d3kos/data/boatlog-audio/`.

---

## Fix 6 — Weather: GPS Centering & Wind/Clouds Overlay

**File:** `/var/www/html/weather.html`

**Current behaviour:**
- Map hardcoded fallback `{ lat: 44.4167, lon: -79.3333 }` (Lake Simcoe) — always opens there
- Wind and cloud overlays not rendering

**Required behaviour:**
- Map opens at actual vessel GPS position on startup
- Wind and cloud layers visible when API key is configured

### Fix A — GPS position on init

Replace the hardcoded init block:
```javascript
// REMOVE THIS:
// let currentPosition = { lat: 44.4167, lon: -79.3333 };

// ADD THIS:
let currentPosition = { lat: 44.4167, lon: -79.3333 }; // fallback
let gpsResolved = false;

async function initPosition() {
  try {
    const r = await fetch('/signalk/v1/api/vessels/self/navigation/position', { signal: AbortSignal.timeout(4000) });
    const d = await r.json();
    if (d.value && d.value.latitude && d.value.longitude) {
      currentPosition = { lat: d.value.latitude, lon: d.value.longitude };
      gpsResolved = true;
    }
  } catch (e) { /* fallback to Lake Simcoe */ }
  initMap(); // call map init after position resolved
}

// Call initPosition() instead of initMap() on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPosition);
```

### Fix B — Wind/Clouds overlay

1. Find where OpenWeatherMap tile layers are defined in weather.html
2. Verify the API key is being read from the Gemini/settings config or a dedicated weather config
3. Check the tile URL format — current OWM API v3.0 tile URL:
   ```
   https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={API_KEY}
   ```
   Valid layer names: `wind_new`, `clouds_new`, `precipitation_new`, `temp_new`
4. If API key is missing or wrong, show "Weather overlays unavailable — configure API key in Settings"
5. Add error handler on tile layer: if 401/403 response, hide layer and show notice

**Acceptance:** With GPS: map opens at vessel position. Recenter button uses live GPS. Wind/cloud layers visible when API key is set.

---

## Fix 7 — Marine Vision: Graceful Offline Handling

**Files:**
- `/var/www/html/marine-vision.html`
- `/opt/d3kos/services/marine-vision/camera_stream_manager.py`
- `/opt/d3kos/services/marine-vision/fish_detector.py`

**Current behaviour:** Camera errors show as broken images or unhandled exceptions. Fish detector may crash when camera offline.

**Required behaviour:** When cameras are unreachable (boat network 10.42.0.x not available), show clean placeholder UI.

### Backend fixes

In `camera_stream_manager.py`, ensure camera status field exists:
```python
# Each camera dict must include 'status' key
camera['status'] = 'online' if connected else 'offline'
camera['offline_reason'] = 'Camera unreachable — connect to boat network' if not connected else ''
```

In `fish_detector.py`, wrap camera access:
```python
try:
    frame = get_camera_frame()
except Exception:
    return {'status': 'offline', 'reason': 'camera unavailable', 'detections': []}
```

### Frontend fixes

In `marine-vision.html`, for each camera feed `<img>`:
```javascript
img.onerror = function() {
  this.style.display = 'none';
  const placeholder = document.createElement('div');
  placeholder.className = 'camera-offline-placeholder';
  placeholder.innerHTML = '<div style="text-align:center;padding:40px;font-size:20px;color:#888;">📷<br>' + cameraName + '<br><small>Offline — Connect to boat network</small></div>';
  this.parentNode.appendChild(placeholder);
};
```

Add CSS:
```css
.camera-offline-placeholder {
  background: #1a1a1a;
  border: 2px dashed #444;
  border-radius: 8px;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

**Acceptance:** With cameras unreachable: placeholder shown, no JS errors, fish detector returns `offline` status cleanly.

---

## Fix 8 — OpenCPN: Flatpak Migration

**Platform:** Raspberry Pi 4B, Debian Trixie (13), ARM64
**Current:** `opencpn 5.10.2+dfsg-1` via apt (native)
**Target:** `org.opencpn.OpenCPN` via Flatpak from Flathub (supports plugins)

### Step-by-step commands (run on Pi as root or with sudo)

```bash
# 1. Backup current OpenCPN settings
cp -r ~/.opencpn ~/.opencpn.backup.$(date +%Y%m%d)

# 2. Install Flatpak runtime
sudo apt install -y flatpak

# 3. Add Flathub repo
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# 4. Remove native OpenCPN (keep config backup)
sudo apt remove -y opencpn

# 5. Install OpenCPN via Flatpak
flatpak install -y flathub org.opencpn.OpenCPN

# 6. Migrate settings
mkdir -p ~/.var/app/org.opencpn.OpenCPN/config/opencpn/
cp ~/.opencpn/opencpn.conf ~/.var/app/org.opencpn.OpenCPN/config/opencpn/

# 7. Test launch
flatpak run org.opencpn.OpenCPN
```

### Update d3kOS menu launcher

In the main menu HTML or launcher script, find the OpenCPN launch call and update:
```bash
# OLD
opencpn

# NEW
flatpak run org.opencpn.OpenCPN
```

If the menu is configured in `/var/www/html/index.html`, find the OpenCPN button and update `onclick` or the iframe/launch target.

### Touchscreen verification

After migration, verify in OpenCPN Preferences:
- Display → Touch screen mode: enabled
- Toolbar icon size: large
- Chart bar: visible

### Plugin installer

Once Flatpak OpenCPN is running:
1. Menu → Tools → Plugin Manager
2. Install: Dashboard, AIS, Radar Overlay (OpenCPN Pi Radar)
3. Enable each plugin after install

**Acceptance:** `flatpak run org.opencpn.OpenCPN` launches. Charts load. Touchscreen works. Plugin manager available.

---

## Fix 9 — Boat Setup Wizard: Gemini API Key Step

**File:** `/var/www/html/onboarding.html`
**Current:** No Gemini configuration step. AI assistant not configured during setup.
**Required:** Add Step 17 "AI Assistant Setup" with optional Gemini API key.

### Implementation

Find the last step in `onboarding.html` (likely Step 16 or 17 completion screen).

Insert new step before the completion screen:

```html
<!-- Step 17: AI Assistant Setup (Optional) -->
<div class="wizard-step" id="step-17" style="display:none;">
  <h2>🤖 AI Assistant Setup</h2>
  <p style="font-size:18px;">d3kOS includes an AI assistant. Add a free Gemini API key for the best experience.</p>

  <div class="setting-card" style="margin: 20px 0;">
    <label style="font-size:18px; display:block; margin-bottom:8px;">Gemini API Key (optional)</label>
    <input type="password" id="gemini-key-input" placeholder="AIza..." style="width:100%; font-size:18px; padding:12px; border-radius:8px; border:2px solid #555; background:#222; color:#fff;">
    <small style="color:#aaa; margin-top:8px; display:block;">Free API key from <strong>aistudio.google.com</strong></small>
  </div>

  <button onclick="testGeminiKey()" style="font-size:20px; padding:16px 32px; background:#4CAF50; color:#fff; border:none; border-radius:8px; margin:8px;">🔌 Test Connection</button>
  <div id="gemini-test-result" style="font-size:18px; margin-top:12px;"></div>

  <div style="display:flex; gap:16px; margin-top:24px; justify-content:center;">
    <button onclick="saveGeminiAndContinue()" style="font-size:20px; padding:16px 32px; background:#2196F3; color:#fff; border:none; border-radius:8px;">✓ Save & Continue</button>
    <button onclick="skipGemini()" style="font-size:20px; padding:16px 32px; background:#555; color:#fff; border:none; border-radius:8px;">Skip for Now</button>
  </div>
</div>
```

```javascript
async function testGeminiKey() {
  const key = document.getElementById('gemini-key-input').value.trim();
  if (!key) { document.getElementById('gemini-test-result').textContent = '⚠️ Enter an API key first'; return; }
  document.getElementById('gemini-test-result').textContent = 'Testing...';
  const r = await fetch('/gemini/test', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({api_key: key}) });
  const d = await r.json();
  document.getElementById('gemini-test-result').textContent = d.success ? '✅ Connected! AI assistant ready.' : '❌ ' + (d.error || 'Connection failed');
}

async function saveGeminiAndContinue() {
  const key = document.getElementById('gemini-key-input').value.trim();
  if (key) {
    await fetch('/gemini/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({api_key: key}) });
  }
  showStep(18); // next step (completion)
}

function skipGemini() {
  showStep(18);
}
```

**Acceptance:** Wizard shows AI setup step. Key can be entered + tested. Skip works. Key is saved to Gemini config.

---

## Fix 10 — AI Assistant: RAG Precision Improvement

**File:** `/opt/d3kos/services/ai/query_handler.py`

### Changes

**1. Increase retrieval count**
```python
# Find: n_results=4 in RAG query
# Change to:
n_results=6
```

**2. Filter weak results**
```python
# After RAG query, filter by distance
MAX_DISTANCE = 0.40
results = [r for r in rag_results if r.get('distance', 1.0) < MAX_DISTANCE]
if not results:
    # No strong matches — fall through to Gemini
    return self._query_gemini(query)
```

**3. Add source context to prompt**
```python
# When building RAG context, include source info
context_parts = []
for r in results:
    source = r.get('metadata', {}).get('source', 'unknown')
    context_parts.append(f"[Source: {source}]\n{r['document']}")
rag_context = '\n\n'.join(context_parts)
```

**4. Re-ingest source collection after this deployment**
```bash
# Run on laptop after deploying Pi changes:
cd /home/boatiq/rag-stack
.venv/bin/python3 helm_os_ingest.py --collection source
```

**Acceptance:** Ask voice assistant a technical question. Response cites source file. Weak/off-topic RAG results don't appear in answers.

---

## Fix 11 — Boot: Keyring Auto-Unlock & Auto-Login

**Files:**
- `/etc/lightdm/lightdm.conf`
- `/etc/pam.d/lightdm-autologin`

### Step 1 — Configure LightDM auto-login

Edit `/etc/lightdm/lightdm.conf`. Find or add `[Seat:*]` section:
```ini
[Seat:*]
autologin-user=d3kos
autologin-user-timeout=0
autologin-session=labwc
```

Note: The window manager is `labwc` (Wayland, Debian Trixie — confirmed from MASTER_SYSTEM_SPEC.md v3.7).

### Step 2 — Configure PAM to auto-unlock keyring

Add to `/etc/pam.d/lightdm-autologin` (append after existing lines):
```
auth     optional    pam_gnome_keyring.so
session  optional    pam_gnome_keyring.so auto_start
```

### Step 3 — Set keyring to empty password

Run once interactively (on Pi desktop):
```bash
# Remove existing keyring password
echo "" | /usr/bin/gnome-keyring-daemon --unlock
# Or use seahorse GUI: change login keyring password to empty string
```

### Step 4 — Verify

After reboot:
- Desktop appears without any login prompt
- No keyring password dialog
- All services running
- SSH still requires password (untouched)

**Acceptance:** Reboot → desktop auto-starts → d3kOS UI accessible within 60s → no password prompts anywhere.

---

## Fix 12 — Settings: Measurement System Section Formatting

**File:** `/var/www/html/settings.html`

**Current (line ~627):**
```html
<h2>Measurement System</h2>
```

**Required:**
```html
<h2 class="section-header">📏 Measurement System</h2>
```

Also check and fix (line ~691):
```html
<!-- Current: -->
<h2>🤖 AI Assistant — Gemini API</h2>
<!-- Required: -->
<h2 class="section-header">🤖 AI Assistant — Gemini API</h2>
```

**Acceptance:** All `<h2>` section headers in settings.html have `class="section-header"` and match visual style of Engine Configuration, Units & Display, etc.

---

## Fix 13 — Settings: System Actions Actually Execute

**New file:** `/opt/d3kos/services/settings-api.py`
**New service:** `/etc/systemd/system/d3kos-settings-api.service`
**Port:** 8101
**Nginx proxy:** `/settings/action/` → `localhost:8101`

### Settings API service

```python
#!/usr/bin/env python3
"""d3kOS Settings Action API — port 8101"""
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_COMMANDS = {
    'restart-signalk':  ['sudo', 'systemctl', 'restart', 'signalk'],
    'restart-nodered':  ['sudo', 'systemctl', 'restart', 'nodered'],
    'reboot':           ['sudo', 'reboot'],
}

@app.route('/settings/action/<action>', methods=['POST'])
def run_action(action):
    if action not in ALLOWED_COMMANDS:
        return jsonify({'success': False, 'error': 'Unknown action'}), 400
    try:
        result = subprocess.run(ALLOWED_COMMANDS[action], capture_output=True, text=True, timeout=15)
        return jsonify({'success': True, 'message': f'{action} triggered', 'output': result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({'success': True, 'message': f'{action} triggered (no response expected)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/settings/action/initial-setup-reset', methods=['POST'])
def initial_setup_reset():
    # Call existing reset logic
    try:
        subprocess.run(['/opt/d3kos/scripts/sanitize.sh'], timeout=30)
        return jsonify({'success': True, 'message': 'Initial setup reset complete'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8101)
```

### Systemd service file

```ini
[Unit]
Description=d3kOS Settings Action API
After=network.target

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services
ExecStart=/usr/bin/python3 /opt/d3kos/services/settings-api.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Sudoers rule

Create `/etc/sudoers.d/d3kos-settings-api`:
```
d3kos ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart signalk
d3kos ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nodered
d3kos ALL=(ALL) NOPASSWD: /usr/bin/reboot
```

### Nginx proxy (add to d3kOS nginx config)

```nginx
location /settings/action/ {
    proxy_pass http://127.0.0.1:8101;
    proxy_set_header Host $host;
}
```

### Update settings.html JS

```javascript
// Replace alert-based functions with real API calls:

function restartSignalK() {
  if (!confirm('Restart Signal K? Engine data will pause briefly.')) return;
  fetch('/settings/action/restart-signalk', {method:'POST'})
    .then(r => r.json())
    .then(d => showToast(d.success ? '✓ Signal K restarting...' : '✗ ' + d.error));
}

function restartNodered() {
  if (!confirm('Restart Node-RED? Dashboard will reload.')) return;
  fetch('/settings/action/restart-nodered', {method:'POST'})
    .then(r => r.json())
    .then(d => showToast(d.success ? '✓ Node-RED restarting...' : '✗ ' + d.error));
}

function rebootSystem() {
  if (!confirm('Reboot the system now?')) return;
  fetch('/settings/action/reboot', {method:'POST'})
    .then(() => { showToast('🔄 Rebooting...'); setTimeout(() => location.reload(), 15000); });
}
```

**Acceptance:**
- Tap "Restart Signal K" → confirmation → button performs restart → toast message appears
- Tap "Reboot System" → confirmation dialog → system reboots
- No SSH instructions appear anywhere

---

## Fix 14 — All Pages: Touch-Friendly Scrollbar Size

**Files:** All HTML pages with scrollable content (applies globally)
**Current behaviour:** Browser default scrollbar (~10px wide) — cannot be reliably grabbed on touchscreen.
**Required behaviour:** Scrollbar minimum 56px wide, high contrast, grabbable with a finger.

### Check for shared CSS file first

```bash
# On Pi:
ls /var/www/html/css/ 2>/dev/null
ls /var/www/html/*.css 2>/dev/null
```

### If shared CSS file exists — add once there

Add to the shared CSS file:
```css
/* Touch-friendly scrollbars — minimum 56px for touchscreen use */
::-webkit-scrollbar { width: 56px; }
::-webkit-scrollbar-track { background: #1a1a1a; border-radius: 8px; }
::-webkit-scrollbar-thumb { background: #555; border-radius: 8px; min-height: 80px; }
::-webkit-scrollbar-thumb:active { background: #FFD700; }
/* Firefox */
* { scrollbar-width: thick; scrollbar-color: #555 #1a1a1a; }
```

### If no shared CSS — add to EVERY page's `<style>` block

Pages to update:
- `/var/www/html/dashboard.html`
- `/var/www/html/navigation.html`
- `/var/www/html/weather.html`
- `/var/www/html/marine-vision.html`
- `/var/www/html/boatlog.html`
- `/var/www/html/settings.html`
- `/var/www/html/onboarding.html`
- `/var/www/html/index.html`
- Any other `.html` files in `/var/www/html/`

### Implementation note

The `active` state uses gold (`#FFD700`) — matches d3kOS brand colour and provides clear visual feedback that the scrollbar is being touched.

**Acceptance:** Open any page with a scrollbar on the touchscreen. The scrollbar is clearly visible and easy to grab and drag with a fingertip without precision.

---

## Deployment Order

Run fixes in this order (dependencies):

1. Fix 13 (Settings API) — other fixes may test using it
2. Fix 11 (Auto-login/Keyring) — affects all testing
3. Fix 3 (Export race condition) — test with reboot
4. Fix 1 (Dashboard banner)
5. Fix 2 (Benchmark investigation)
6. Fix 4 (Navigation GPS)
7. Fix 6 (Weather GPS centering)
8. Fix 7 (Marine Vision offline)
9. Fix 5 (Boatlog voice note)
10. Fix 9 (Wizard Gemini step)
11. Fix 12 (Settings formatting)
12. Fix 10 (RAG precision)
13. Fix 8 (OpenCPN Flatpak) — last, requires most manual testing
14. Fix 14 (Scrollbars) — apply to all pages, verify on touchscreen

---

## Files to Deploy to Pi

| Source | Destination |
|--------|-------------|
| `opt/d3kos/scripts/export-daily.sh` | `/opt/d3kos/scripts/export-daily.sh` |
| `opt/d3kos/scripts/export-on-boot.sh` | `/opt/d3kos/scripts/export-on-boot.sh` |
| `opt/d3kos/services/settings-api.py` | `/opt/d3kos/services/settings-api.py` |
| `etc/systemd/system/d3kos-settings-api.service` | `/etc/systemd/system/d3kos-settings-api.service` |
| `etc/sudoers.d/d3kos-settings-api` | `/etc/sudoers.d/d3kos-settings-api` |
| `var/www/html/dashboard.html` | `/var/www/html/dashboard.html` |
| `var/www/html/navigation.html` | `/var/www/html/navigation.html` |
| `var/www/html/weather.html` | `/var/www/html/weather.html` |
| `var/www/html/marine-vision.html` | `/var/www/html/marine-vision.html` |
| `var/www/html/boatlog.html` | `/var/www/html/boatlog.html` |
| `var/www/html/settings.html` | `/var/www/html/settings.html` |
| `var/www/html/onboarding.html` | `/var/www/html/onboarding.html` |
| `opt/d3kos/services/ai/query_handler.py` | `/opt/d3kos/services/ai/query_handler.py` |

---

*Spec generated by Claude Code (Orchestrator) 2026-03-04. Implemented by Ollama qwen3-coder:30b.*
