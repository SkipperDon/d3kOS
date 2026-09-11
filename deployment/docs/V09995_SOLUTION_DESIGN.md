# v0.9.9.5 — Solution Design
**Document:** V09995-SOL-001  
**Version:** 1.0  
**Date:** 2026-09-11  
**Author:** SkipperDon / Claude Sonnet 4.6 (S159)  
**Status:** APPROVED — all operator decisions locked (S159)

---

## Locked Decisions (S159 — do not re-open)

| # | Question | Decision |
|---|---|---|
| D02-1 | SafeHelm phase scope | Phase 1 + Advisory (voice + AvNav widget overlay). NOT shadow-only. |
| D02-2 | SH-15 gate | Does NOT block v0.9.9.5. Phase Feature Flag pattern. SH-15 enforced only at Phase 2+ Signal K write path. |
| D16-1 | go2rtc vs camera_stream_manager | **Option A — Alongside.** go2rtc on port 8554. camera_stream_manager stays on port 8084, untouched. |
| D05-1 | YOLOv8n model hosting | **Option C — npm asset.** Bundled in npm tarball at `assets/models/yolov8n.onnx`. No external download at runtime. |
| D05-2 | OpenPlotter test (SK-FW-2) | Tested on lab Pi Signal K via `npm link`. Functionally equivalent. README notes: "tested on Signal K Node Server 2.x." |

---

## Build Sequence

```
D17 (Hardware Probe + Feature Gate)   ← no dependencies, foundation layer
  ↓
D05 (signalk-forward-watch v0.2.4)   ← independent npm work, quick ship
  ↓
D16 (3D Surround View Phase 1)       ← requires cameras working (existing)
  ↓
D02 (SafeHelm Advisory Mode)         ← requires Signal K live data, most complex
```

**Rationale:** D17 provides the feature gate library that D02 and D16 use to auto-enable/disable. D05 is independent and ships quickly to npm. D16 is camera-only with no AI dependencies. D02 is the largest and requires all infrastructure to be confirmed first.

---

## D17 — Hardware Capability Detection

**Build tasks:** HCD-1 through HCD-5  
**Spec:** `deployment/docs/HARDWARE_CAPABILITY_DETECTION_REQUIREMENTS.md` (HCD-REQ-001 v1.0)

### File Structure

```
deployment/v0.9.9.5/
  scripts/
    hardware-probe.sh               ← HCD-1: probe script + CLI (d3kos-probe)
  services/
    d3kos_feature_gate.py           ← HCD-3: shared Python library
  config/
    hardware-profile.json           ← default empty profile (overwritten by probe)
    capabilities-manifest.json      ← HCD-3: feature definitions
  etc/
    udev/rules.d/
      99-d3kos-accelerator.rules    ← HCD-2: Coral USB hot-plug rules
    systemd/system/
      d3kos-hardware-probe.service  ← HCD-1: boot-time oneshot service
  opt/d3kos/services/dashboard/
    templates/hardware.html         ← HCD-4: Hardware page template
    templates/setup.html            ← HCD-5: modified — adds final Setup Description screen
```

### HCD-1 — hardware-probe.sh

**Logic:**
```bash
#!/usr/bin/env bash
# /opt/d3kos/scripts/hardware-probe.sh
# Reads hardware state → writes /opt/d3kos/config/hardware-profile.json atomically

PROFILE=/opt/d3kos/config/hardware-profile.json
TMP=${PROFILE}.tmp

# --- Platform ---
pi_model=$(cat /proc/device-tree/model 2>/dev/null | tr -d '\0' || echo "unknown")
if [[ "$pi_model" =~ Raspberry\ Pi\ ([0-9]+) ]]; then
    pi_gen="${BASH_REMATCH[1]}"
else
    pi_gen=0
fi
ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
ram_gb=$(( ram_kb / 1048576 ))

# --- HAT ---
hat_present=false
hat_product="null"
hat_vendor="null"
hat_product_id="null"
hat_product_ver="null"
hat_class="null"
if [ -d /proc/device-tree/hat ]; then
    hat_present=true
    hat_product=$(cat /proc/device-tree/hat/product 2>/dev/null | tr -d '\0' | jq -Rs '.' || echo '"unknown"')
    hat_vendor=$(cat /proc/device-tree/hat/vendor 2>/dev/null | tr -d '\0' | jq -Rs '.' || echo '"unknown"')
    hat_product_id=$(cat /proc/device-tree/hat/product_id 2>/dev/null | tr -d '\0' | jq -Rs '.' || echo '"unknown"')
    hat_product_ver=$(cat /proc/device-tree/hat/product_ver 2>/dev/null | tr -d '\0' | jq -Rs '.' || echo '"unknown"')
    # Normalise hat_class
    raw_product=$(cat /proc/device-tree/hat/product 2>/dev/null | tr -d '\0')
    case "$raw_product" in
        *"AI HAT+"*)    hat_class='"hailo-ai-hat"' ;;
        *"PiCAN-M"*)    hat_class='"pican-m"' ;;
        *"PiCAN2"*)     hat_class='"pican2"' ;;
        *"Waveshare"*)  hat_class='"waveshare-can"' ;;
        *)              hat_class='"unknown-hat"' ;;
    esac
fi

# --- Accelerators ---
accel_present=false
accel_class="[]"
accel_devices="[]"
declare -a classes=()
declare -a devices=()

if [ -c /dev/hailo0 ]; then
    accel_present=true
    classes+=("\"hailo-8l\"")
    devices+=("{\"type\":\"hailo-8l\",\"node\":\"/dev/hailo0\",\"bus\":\"pcie\"}")
fi
if lsusb 2>/dev/null | grep -q "18d1:9302"; then
    accel_present=true
    classes+=("\"coral-usb\"")
    devices+=("{\"type\":\"coral-usb\",\"node\":\"usb\",\"bus\":\"usb\"}")
fi
if lsusb 2>/dev/null | grep -q "18d1:9303"; then
    accel_present=true
    classes+=("\"coral-usb-mini\"")
    devices+=("{\"type\":\"coral-usb-mini\",\"node\":\"usb\",\"bus\":\"usb\"}")
fi
# Hailo-8 full (PCIe)
if find /sys/bus/pci/devices/ -name "vendor" -exec grep -l "0x1e60" {} \; 2>/dev/null | grep -q .; then
    accel_present=true
    classes+=("\"hailo-8\"")
    devices+=("{\"type\":\"hailo-8\",\"node\":\"pcie\",\"bus\":\"pcie\"}")
fi
if [ ${#classes[@]} -gt 0 ]; then
    accel_class="[$(IFS=','; echo "${classes[*]}")]"
    accel_devices="[$(IFS=','; echo "${devices[*]}")]"
fi

# --- Read current probe_version ---
current_version=0
if [ -f "$PROFILE" ]; then
    current_version=$(jq -r '.probe_version // 0' "$PROFILE" 2>/dev/null || echo 0)
fi
new_version=$(( current_version + 1 ))

# --- Write atomically ---
cat > "$TMP" << EOF
{
  "probe_version": $new_version,
  "probed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platform": {
    "pi_model": "$pi_model",
    "pi_gen": $pi_gen,
    "ram_gb": $ram_gb
  },
  "hat": {
    "present": $hat_present,
    "product": $hat_product,
    "vendor": $hat_vendor,
    "product_id": $hat_product_id,
    "product_ver": $hat_product_ver,
    "hat_class": $hat_class
  },
  "accelerator": {
    "present": $accel_present,
    "accelerator_class": $accel_class,
    "devices": $accel_devices
  }
}
EOF
mv "$TMP" "$PROFILE"
chmod 644 "$PROFILE"
```

**Systemd service:** `d3kos-hardware-probe.service`
```ini
[Unit]
Description=d3kOS Hardware Probe
Before=d3kos-dashboard.service
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/opt/d3kos/scripts/hardware-probe.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**CLI alias:** `sudo ln -sf /opt/d3kos/scripts/hardware-probe.sh /usr/local/bin/d3kos-probe`

### HCD-2 — udev rules

```udev
# /etc/udev/rules.d/99-d3kos-accelerator.rules
# Google Coral USB Accelerator
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", ATTR{idProduct}=="9302", \
    RUN+="/opt/d3kos/scripts/hardware-probe.sh", \
    RUN+="/opt/d3kos/scripts/notify-hardware-change.sh"
ACTION=="remove", SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", ATTR{idProduct}=="9302", \
    RUN+="/opt/d3kos/scripts/hardware-probe.sh", \
    RUN+="/opt/d3kos/scripts/notify-hardware-change.sh"
# Google Coral USB Mini
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", ATTR{idProduct}=="9303", \
    RUN+="/opt/d3kos/scripts/hardware-probe.sh", \
    RUN+="/opt/d3kos/scripts/notify-hardware-change.sh"
ACTION=="remove", SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", ATTR{idProduct}=="9303", \
    RUN+="/opt/d3kos/scripts/hardware-probe.sh", \
    RUN+="/opt/d3kos/scripts/notify-hardware-change.sh"
```

**notify-hardware-change.sh:** posts `POST http://localhost:3000/api/hardware/profile-updated` to the dashboard webhook. Uses a lockfile (`/tmp/d3kos-hw-notify.lock`) so overlapping events queue safely.

### HCD-3 — d3kos_feature_gate.py

```python
# /opt/d3kos/services/d3kos_feature_gate.py
import json, os, time

_PROFILE_PATH  = '/opt/d3kos/config/hardware-profile.json'
_MANIFEST_PATH = '/opt/d3kos/config/capabilities-manifest.json'

_profile_cache   = None
_manifest_cache  = None
_cached_version  = -1

def _load():
    global _profile_cache, _manifest_cache, _cached_version
    with open(_PROFILE_PATH) as f:
        p = json.load(f)
    if p['probe_version'] != _cached_version:
        _profile_cache  = p
        _cached_version = p['probe_version']
        with open(_MANIFEST_PATH) as f:
            _manifest_cache = json.load(f)

def feature_available(key: str) -> bool:
    _load()
    feat = _manifest_cache['features'].get(key)
    if not feat:
        return False
    if feat.get('operator_override'):
        return True
    req  = feat['requires']
    p    = _profile_cache['platform']
    accel = _profile_cache['accelerator']
    if p['pi_gen'] < req.get('pi_gen_min', 0):
        return False
    if p['ram_gb'] < req.get('ram_gb_min', 0):
        return False
    if req.get('accelerator_any') and not accel['present']:
        allowed = req.get('accelerator_class_any', [])
        if allowed and not any(c in accel['accelerator_class'] for c in allowed):
            return False
        elif not allowed:
            return False
    return True

def feature_reason(key: str) -> str:
    _load()
    feat = _manifest_cache['features'].get(key)
    if not feat:
        return 'Feature not defined.'
    req = feat['requires']
    p   = _profile_cache['platform']
    accel = _profile_cache['accelerator']
    reasons = []
    if p['pi_gen'] < req.get('pi_gen_min', 0):
        reasons.append(f"Requires Pi {req['pi_gen_min']} (detected: Pi {p['pi_gen']})")
    if p['ram_gb'] < req.get('ram_gb_min', 0):
        reasons.append(f"Requires {req['ram_gb_min']} GB RAM (detected: {p['ram_gb']} GB)")
    if req.get('accelerator_any') and not accel['present']:
        reasons.append('Requires an AI accelerator (Hailo-8L or Coral USB)')
    return '. '.join(reasons) or 'Hardware requirements met.'

def feature_upgrade_path(key: str) -> list:
    _load()
    feat = _manifest_cache['features'].get(key)
    if not feat:
        return []
    req = feat['requires']
    p   = _profile_cache['platform']
    accel = _profile_cache['accelerator']
    items = []
    if p['pi_gen'] < req.get('pi_gen_min', 0):
        items.append(f'Upgrade to Raspberry Pi {req["pi_gen_min"]}')
    if p['ram_gb'] < req.get('ram_gb_min', 0):
        items.append(f'Install at least {req["ram_gb_min"]} GB RAM')
    if req.get('accelerator_any') and not accel['present']:
        items.append('Add a Hailo-8L AI HAT+ or Google Coral USB Accelerator')
    return items
```

### HCD-4 — Dashboard Hardware Page

**New Flask route** added to `app.py`:
```python
@app.route('/hardware')
def hardware_page():
    profile  = load_hardware_profile()   # reads config/hardware-profile.json
    manifest = load_capabilities_manifest()
    features_on  = [k for k in manifest['features'] if feature_gate.feature_available(k)]
    features_off = [k for k in manifest['features'] if not feature_gate.feature_available(k)]
    return render_template('hardware.html',
        profile=profile, manifest=manifest,
        features_on=features_on, features_off=features_off,
        feature_gate=feature_gate)

@app.route('/api/hardware/profile-updated', methods=['POST'])
def hardware_profile_updated():
    # Re-invalidate cache, push SSE event to any open browser connections
    feature_gate._cached_version = -1   # force cache refresh on next call
    _push_hardware_sse_event()
    return jsonify({'ok': True})
```

**Toast notifications:** delivered via Server-Sent Events (SSE) to the dashboard page. The dashboard's existing WebSocket or a new `/api/hardware/events` SSE endpoint pushes `hardware_changed` events. Browser JS intercepts and renders the toast.

### HCD-5 — Wizard Final Screen

Modify `setup.html` to add a final step "Your d3kOS Hardware Profile" before the Finish button. Renders the same Setup Description format as the Hardware page. Re-probe button triggers a client-side fetch to `POST /api/hardware/profile-updated` followed by a page refresh.

---

## D05 — signalk-forward-watch v0.2.4

**Repository:** `signalk-forward-watch/`  
**Tasks:** SK-FW-1, SK-FW-2 (lab Pi), SK-FW-3

### SK-FW-1 — Bundle YOLOv8n ONNX (npm asset)

**Changes to `package.json`:**
```json
{
  "version": "0.2.4",
  "files": ["index.js", "assets/"],
  "scripts": {
    "postinstall": "node scripts/install-model.js"
  }
}
```

**`scripts/install-model.js`:**
```javascript
// Downloads yolov8n.onnx from the GitHub release asset at npm install time
// (install time = developer environment, not runtime on the boat)
// At runtime, loads from local path — never makes external requests.
const fs   = require('fs');
const path = require('path');
const https = require('https');

const MODEL_DIR  = path.join(__dirname, '..', 'assets', 'models');
const MODEL_PATH = path.join(MODEL_DIR, 'yolov8n.onnx');
const MODEL_URL  = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx';

if (fs.existsSync(MODEL_PATH)) {
  console.log('[signalk-forward-watch] Model already present — skipping download.');
  process.exit(0);
}
fs.mkdirSync(MODEL_DIR, { recursive: true });
console.log('[signalk-forward-watch] Downloading YOLOv8n model...');
// ... (standard https.get + write stream)
```

**At runtime, plugin loads model from:**
```javascript
const MODEL_PATH = path.join(__dirname, 'assets', 'models', 'yolov8n.onnx');
// No external URL references — no fallback to network
```

**`.npmignore`** must NOT exclude `assets/`. Add `!assets/` if a `.npmignore` exists.

**Package size impact:** +6 MB (YOLOv8n ONNX). Acceptable — eliminates offline install failures.

### SK-FW-2 — OpenPlotter Compatibility Test (lab Pi Signal K)

**Procedure (lab Pi):**
```bash
cd /home/boatiq/signalk-forward-watch
npm pack                         # build the tarball
cd ~/.signalk
npm install /home/boatiq/signalk-forward-watch/signalk-forward-watch-0.2.4.tgz
# Restart Signal K
sudo systemctl restart signalk
# Verify in Signal K admin UI → Server → Plugin Config → signalk-forward-watch → Enabled
# Check journal:
journalctl -u signalk -f | grep forward-watch
```

**Pass criteria:** Plugin appears in Signal K admin UI, enables without error, and begins processing frames when a camera feed is active.

**README note (added):** "Tested on Signal K Node Server 2.x running on Raspberry Pi OS. Compatible with OpenPlotter installations using the same Signal K version."

### SK-FW-3 — README Update

Remove Section "Step 2 — Download the YOLO model" entirely. Update Step 1 to read: "Install the plugin — the YOLO model downloads automatically during `npm install`." Bump version reference to v0.2.4.

---

## D16 — 3D Surround View (Phase 1)

**Spec:** `deployment/docs/D16_3D_SURROUND_VIEW_SPEC.md`  
**Decision locked:** go2rtc runs alongside `camera_stream_manager.py` (Option A)

### File Structure

```
deployment/v0.9.9.5/
  etc/
    go2rtc/
      go2rtc-d16.yaml                 ← go2rtc config (port 8554 API)
    systemd/system/
      d3kos-go2rtc.service            ← systemd unit
  scripts/
    install-go2rtc.sh                 ← download ARM64 binary
    configure-go2rtc.sh               ← reads slots.json, writes go2rtc-d16.yaml bow camera URL
  opt/d3kos/services/
    marine-vision/
      bird_eye_stitch.py              ← new module: OpenCV homography stitch → MJPEG endpoint
    dashboard/
      templates/3d-view.html          ← three-zone layout
      templates/base.html             ← modified: add AvNav ↔ 3D toggle button
      static/js/safehelm-overlay.js   ← SafeHelm widget injection (also used by D02)
```

### go2rtc Config

```yaml
# /etc/go2rtc/go2rtc-d16.yaml
api:
  listen: ":8554"   # HTTP API for WebRTC signaling + MJPEG server

streams:
  d16_forward: rtsp://{BOW_CAMERA_RTSP_URL}   # filled by configure-go2rtc.sh from slots.json
```

`configure-go2rtc.sh` reads `/opt/d3kos/config/slots.json`, finds the slot with `roles` containing `forward_watch`, reads `hw_id`, looks up `rtsp_url` in `hardware.json`, writes the YAML with the real URL. Runs once at post-install and again if camera slots change.

### Bird's Eye Stitch Module

**New endpoint added to `camera_stream_manager.py`:** `GET /camera/surround-view/bird-eye`

Returns a MJPEG stream. The stitch thread runs in the background pulling frames from the 4 hardware grabbers already active in `camera_stream_manager.py` and producing a 640×480 bird's eye image at ~5 FPS.

**Stitch algorithm:**
```python
# bird_eye_stitch.py — imported by camera_stream_manager.py
import cv2, numpy as np

# Homography matrices per camera (computed once from calibration points)
# Operator enters 4 reference points per camera via a calibration UI at first use
# Stored in /opt/d3kos/config/surround-calibration.json

def stitch_frame(bow_frame, port_frame, starboard_frame, stern_frame,
                 transforms: dict) -> np.ndarray:
    output = np.zeros((640, 640, 3), dtype=np.uint8)
    for cam_id, frame, T in [
        ('bow',       bow_frame,       transforms['bow']),
        ('port',      port_frame,      transforms['port']),
        ('starboard', starboard_frame, transforms['starboard']),
        ('stern',     stern_frame,     transforms['stern']),
    ]:
        if frame is None or T is None:
            continue
        warped = cv2.warpPerspective(frame, T, (640, 640))
        mask = (warped > 0).any(axis=2)
        output[mask] = warped[mask]
    return output
```

**First-run calibration:** if `surround-calibration.json` is absent, the bird's eye endpoint returns a 640×640 grid of the 4 raw camera thumbnails (no stitch). The Hardware page shows a "Calibrate Surround View" button that launches a guided calibration flow.

### 3D View Template — Three-Zone Layout

```
┌─────────────────────────┬──────────────────────┐
│  FORWARD PANEL          │  BIRD'S EYE STITCH   │
│  go2rtc WebRTC stream   │  /camera/surround-   │
│  (bow camera)           │   view/bird-eye MJPEG│
│  SVG range rings        │  (port 8084)         │
│  (calibrated to height) │                      │
│  65% width              │  35% width           │
├─────────────────────────┴──────────────────────┤
│  MARINE VISION (existing — unchanged)          │
│  Camera grids · fish detection · controls      │
└────────────────────────────────────────────────┘
```

**Forward panel range rings (SVG):**
```
ring_y = frame_height × (0.5 - arctan(h/d) / θ_v)
```
Where `h` = operator-configured bow camera height (metres), `d` = ring distance (10 / 25 / 50 m), `θ_v` = vertical FOV (RLC-810A = 48°). Camera height input stored in `/opt/d3kos/config/surround-calibration.json`. Default: 1.35 m (midpoint of typical bow rail range).

**AvNav ↔ 3D toggle:** single JS call in the dashboard. One button outside the row-pill zone:
```javascript
function toggleAvNav3D() {
    const frame = document.getElementById('avnav-frame');
    if (frame.src.includes('3d-view')) {
        frame.src = 'http://localhost:8080';   // AvNav
    } else {
        frame.src = '/3d-view';               // 3D view
    }
}
```
No interaction with `showRow()`, engine ribbon, or nav ribbon.

### go2rtc systemd unit

```ini
[Unit]
Description=d3kOS go2rtc — D16 3D Surround View streaming
After=network.target

[Service]
ExecStart=/opt/d3kos/bin/go2rtc -config /etc/go2rtc/go2rtc-d16.yaml
Restart=always
RestartSec=5
User=d3kos

[Install]
WantedBy=multi-user.target
```

---

## D02 — SafeHelm Advisory Mode

**Port:** 8095  
**Phase scope:** Phase 1 (CPA/TCPA engine + COLREGs classifier) + Advisory output (voice + AvNav widget overlay)  
**SH-15:** enforced via Phase Feature Flag — Signal K write paths are hard-disabled in this phase  
**AIS data source:** Signal K WebSocket `ws://localhost:<SK_PORT>/signalk/v1/stream`  
**Voice API:** `POST http://localhost:3002/webhook/alert` (ai_bridge `speak_urgent`)

### File Structure

```
deployment/v0.9.9.5/
  opt/d3kos/services/safehelm/
    safehelm.py              ← Flask app (port 8095) + main orchestration loop
    cpa_engine.py            ← CPA/TCPA vector geometry
    colregs_classifier.py    ← Rules 13/14/15 classifier
    alert_manager.py         ← SafeHelmAlertManager state machine (operator spec)
    signalk_client.py        ← WebSocket consumer (AIS + own-vessel data)
    voice_client.py          ← ai_bridge POST /webhook/alert wrapper
    shadow_logger.py         ← structured log to /opt/d3kos/data/safehelm/shadow.log
    static/
      safehelm-widget.js     ← AvNav overlay widget (injected into dashboard)
      safehelm-widget.css    ← widget styles: ACTIVE_UNACKED flash, ACKNOWLEDGED_MUTED static
  etc/systemd/system/
    d3kos-safehelm.service
```

### Alert Severity and COLREGs Classification

**CPA/TCPA thresholds (operator-defined):**
| Class | Condition | Behaviour |
|---|---|---|
| CRITICAL | CPA < 200 m AND TCPA < 5 min | Immediate voice + full widget takeover (Red #FF0000, 2Hz flash) |
| COLREGs Rule 14 | Head-On detected | Voice + Amber widget |
| COLREGs Rule 15 | Crossing detected | Voice + Amber widget |
| COLREGs Rule 13 | Overtaking detected | Voice + Amber widget |

**Voice formulas (fixed strings — no dynamic prose generation):**
```python
VOICE_PHRASES = {
    'rule14':          'Danger. Head-on situation. Alter course to starboard.',
    'rule15_giveway':  'Warning. Crossing target to starboard. You are Give-Way.',
    'rule15_standon':  'Alert. Crossing target to port. You are Stand-On. Monitor.',
    'rule13_overtake': 'Alert. Overtaking situation. You do not have right-of-way.',
    'critical':        'Critical Collision Risk. Target {bearing}. CPA {cpa_m} metres.',
}
```

### SafeHelmAlertManager (operator-provided — implement as-is)

```python
# alert_manager.py
import time
from enum import Enum

class AlertState(Enum):
    ACTIVE_UNACKED    = 1
    ACKNOWLEDGED_MUTED = 2
    CLEARED           = 3

class SafeHelmAlertManager:
    def __init__(self, target_id, cpa, tcpa, bearing, rule_id):
        self.target_id         = target_id
        self.cpa               = cpa
        self.tcpa              = tcpa
        self.bearing           = bearing
        self.rule_id           = rule_id
        self.state             = AlertState.ACTIVE_UNACKED
        self.ack_time          = None
        self.last_audio_played = 0
        self.snooze_timeout    = 120   # seconds

    def update_metrics(self, current_cpa, current_tcpa):
        previous_cpa = self.cpa
        self.cpa     = current_cpa
        self.tcpa    = current_tcpa
        if self.cpa > 500 and self.tcpa < 0:
            self.state = AlertState.CLEARED
            return
        if self.state == AlertState.ACKNOWLEDGED_MUTED:
            time_since_ack = time.time() - self.ack_time
            if time_since_ack > self.snooze_timeout or (self.cpa < previous_cpa * 0.80):
                self.state = AlertState.ACTIVE_UNACKED

    def execute_ui_acknowledgement(self):
        self.state    = AlertState.ACKNOWLEDGED_MUTED
        self.ack_time = time.time()

    def check_audio_broadcast_trigger(self) -> bool:
        if self.state == AlertState.ACTIVE_UNACKED:
            if time.time() - self.last_audio_played > 15:
                self.last_audio_played = time.time()
                return True
        return False
```

### voice_client.py

```python
# voice_client.py
import requests

AI_BRIDGE_ALERT = 'http://localhost:3002/webhook/alert'

def speak(message: str, repeat: int = 1) -> bool:
    try:
        r = requests.post(AI_BRIDGE_ALERT,
                          json={'message': message, 'repeat': repeat},
                          timeout=3)
        return r.status_code == 200
    except Exception:
        return False   # ai_bridge unavailable — alert logged, not fatal
```

### Phase Feature Flag (SH-15 enforcement)

```python
# safehelm.py — initialization
SAFEHELM_PHASE = int(os.environ.get('SAFEHELM_PHASE', '1'))

def initialize_system():
    boot_cpa_engine()
    boot_colregs_classifier()
    boot_signalk_consumer()
    boot_alert_manager()
    initialize_shadow_logger()
    boot_voice_client()         # Phase 1.5 — voice active
    boot_avnav_widget_server()  # Phase 1.5 — overlay active

    if SAFEHELM_PHASE >= 2:
        # Phase 2+ — Signal K write path (synthetic AIS injection)
        # SH-15 must be verified before this block is entered
        if not verify_signalk_transmit_whitelist():
            raise SystemExit('[SAFEHELM CRITICAL] SH-15 violation: transmitPGNs whitelist missing.')
        boot_synthetic_ais_injector()
    else:
        # Phase 1 — no outbound Signal K writes
        logger.info('SafeHelm Phase 1 boot — SH-15 write path disabled.')
```

### AvNav Widget Overlay

The SafeHelm widget is a floating overlay div injected into the d3kOS dashboard page alongside the AvNav iframe. It does NOT modify AvNav internals. SafeHelm exposes a status SSE endpoint at `GET http://localhost:8095/widget/events` that the dashboard JS subscribes to.

**safehelm-widget.js** — subscribes to SSE, renders overlay:
```javascript
// State machine rendering
const states = {
  ACTIVE_UNACKED: {
    borderColor: '#FF0000',
    flash: true,
    expanded: true
  },
  ACKNOWLEDGED_MUTED: {
    borderColor: '#FFBF00',
    flash: false,
    expanded: false
  }
};
```

**safehelm-widget.css** — 2Hz flash animation via CSS keyframes on `.sh-widget--active-unacked`.

**Widget layout (operator wireframe — implemented as CSS popup):**
```
+======================================================+
| 🚨 [severity label] (COLREG RULE XX: [situation])    |
+------------------------------------------------------+
| Target: #ID | CPA: Xm      | Bearing: XXX° [DIR]    |
| Status: [role] | TCPA: Xm Xs | SOG: X.X kts          |
+------------------------------------------------------+
| SYSTEM RECOMMENDATION: [action text]                 |
+------------------------------------------------------+
| [ ACKNOWLEDGE & SILENCE (120s) ] | [ DISMISS ]       |
+======================================================+
```

ACK button → `POST http://localhost:8095/alert/{target_id}/ack`  
Dismiss button → `POST http://localhost:8095/alert/{target_id}/dismiss`

### CPA Engine — Key Geometry

```python
# cpa_engine.py — core CPA/TCPA calculation
import math

def compute_cpa_tcpa(own_lat, own_lon, own_sog, own_cog,
                     tgt_lat, tgt_lon, tgt_sog, tgt_cog) -> tuple:
    """Returns (cpa_metres, tcpa_seconds). tcpa < 0 means target has passed."""
    # Convert to Cartesian (flat Earth approximation, valid < 50 NM)
    lat_ref  = math.radians(own_lat)
    m_per_deg_lat = 111320
    m_per_deg_lon = 111320 * math.cos(lat_ref)

    dx = (tgt_lon - own_lon) * m_per_deg_lon   # metres east
    dy = (tgt_lat - own_lat) * m_per_deg_lat   # metres north

    own_vx = own_sog * 0.5144 * math.sin(math.radians(own_cog))
    own_vy = own_sog * 0.5144 * math.cos(math.radians(own_cog))
    tgt_vx = tgt_sog * 0.5144 * math.sin(math.radians(tgt_cog))
    tgt_vy = tgt_sog * 0.5144 * math.cos(math.radians(tgt_cog))

    rel_vx = tgt_vx - own_vx
    rel_vy = tgt_vy - own_vy
    v2     = rel_vx**2 + rel_vy**2

    if v2 < 1e-6:          # essentially stationary relative motion
        return (math.hypot(dx, dy), float('inf'))

    tcpa = -(dx * rel_vx + dy * rel_vy) / v2
    cpa  = math.hypot(dx + rel_vx * tcpa, dy + rel_vy * tcpa)
    return (cpa, tcpa)
```

### COLREGs Classifier (Rules 13, 14, 15)

```python
# colregs_classifier.py
def classify(own_cog, tgt_cog, relative_bearing_deg) -> str:
    """Returns 'rule13_overtake', 'rule14_headon', 'rule15_giveway',
               'rule15_standon', or 'no_conflict'."""
    # Rule 14 — Head-On: reciprocal courses ±15°
    course_diff = abs((tgt_cog - own_cog + 180) % 360 - 180)
    if course_diff < 15:
        return 'rule14_headon'

    # Rule 13 — Overtaking: target approaching from >112.5° abaft own beam
    if 112.5 < relative_bearing_deg < 247.5:
        return 'rule13_overtake'

    # Rule 15 — Crossing: target within 0–112.5° either side
    if 0 <= relative_bearing_deg < 112.5:
        return 'rule15_giveway'   # target to starboard = give-way
    if 247.5 < relative_bearing_deg <= 360:
        return 'rule15_standon'   # target to port = stand-on

    return 'no_conflict'
```

### SafeHelm systemd unit

```ini
[Unit]
Description=d3kOS SafeHelm — Collision Avoidance Advisory
After=network.target signalk.service d3kos-ai-bridge.service

[Service]
WorkingDirectory=/opt/d3kos/services/safehelm
ExecStart=/opt/d3kos/venv/bin/python safehelm.py
Environment=SAFEHELM_PHASE=1
Restart=always
RestartSec=10
User=d3kos

[Install]
WantedBy=multi-user.target
```

---

## Inter-Item Dependencies

```
D17 hardware-profile.json  ←─ consumed by D02 (feature gate: SafeHelm on Pi4+ ✓)
                           ←─ consumed by D16 (feature gate: Surround View on Pi4 ✓)
D16 go2rtc on :8554        ─→ forward panel video source in 3d-view.html
D02 SafeHelm SSE on :8095  ─→ safehelm-widget.js overlay in dashboard
ai_bridge on :3002          ←─ consumed by D02 voice_client.py (existing, unchanged)
camera_stream_manager :8084 ←─ consumed by D16 bird's eye MJPEG (existing, extended)
```

---

## Test Plan Summary

| Item | Gate | Method |
|---|---|---|
| HCD-1 | `hardware-profile.json` written correctly on lab Pi | `d3kos-probe && cat /opt/d3kos/config/hardware-profile.json` |
| HCD-2 | Profile updates within 5s of Coral USB plug | Plug test USB device matching vendor ID, watch journal |
| HCD-3 | `feature_available('safehelm_d02')` returns True on Pi 4 | Python unit test |
| HCD-4 | Hardware page renders Setup Description | Browser: `http://localhost:3000/hardware` |
| HCD-5 | Setup Description appears as wizard final screen | Lab Pi first-boot walkthrough |
| SK-FW-1 | `assets/models/yolov8n.onnx` present after `npm install` | `ls -lh` check |
| SK-FW-2 | Plugin loads in Signal K admin UI on lab Pi | `journalctl -u signalk -f` |
| SK-FW-3 | README has no Step 2 model download instruction | Manual review |
| D16 Phase 1 | 3D view page renders forward panel video and bird's eye | Browser on Pi |
| D16 toggle | AvNav ↔ 3D toggle switches iframe, nav/engine ribbon unaffected | Browser on Pi |
| D02 CPA | `compute_cpa_tcpa()` returns correct geometry for known scenario | Python unit test |
| D02 voice | `speak()` triggers audible voice alert via Jabra S330 | Live test on Pi |
| D02 ACK | ACK button mutes audio, shifts widget to amber static border | Browser on Pi |
| D02 snooze | Re-trigger fires after 120s if CPA degrades | Simulated CPA feed test |
| D02 SH-15 | `SAFEHELM_PHASE=2` boot fails cleanly without whitelist | Unit test |

---

## Open Items (Require On-Boat Measurement Before Implementation)

| Item | Required For | What Is Needed |
|---|---|---|
| Bow camera RTSP sub-stream URL | D16 go2rtc config | Already in `hardware.json` — `configure-go2rtc.sh` reads it automatically |
| Bow camera height above waterline | D16 SVG ring pixel positions | Tape measure: bow rail top to waterline at next boat visit. Default 1.35 m used until measured. |
| Signal K port on this installation | D02 SignalK WebSocket URL | Confirm SK port from `~/.signalk/settings.json` on lab Pi |

---

*End of V09995-SOL-001 v1.0*  
*Next step: implement in build sequence order — D17 → D05 → D16 → D02*
