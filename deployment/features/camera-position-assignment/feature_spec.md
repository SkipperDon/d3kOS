# Feature: Camera Position Assignment
# Files: camera_stream_manager.py, settings.html, marine-vision.html

## OLLAMA SELF-CHECK RULES (apply to every phase)

After writing your CODE block, do these checks before submitting:
1. Copy your FIND_LINE. Search for it verbatim in the CURRENT FILE CONTEXT above. If it is not there exactly, rewrite FIND_LINE with a line that IS there.
2. If ACTION is REPLACE, confirm the old code you are replacing exists in the file. If it does not, you have the wrong anchor — find the correct one.
3. If ACTION is INSERT_AFTER, confirm the line you insert after exists in the file.
4. Do not invent variable names, function names, or endpoints not shown in the spec or file context.
5. Re-read your CODE and confirm it matches exactly what the spec asks for — no extra features, no renamed variables.

## Problem

When a user physically mounts multiple cameras on the boat, the system discovers
them by IP address only. There is no automatic way to know which physical camera
is facing bow, stern, port, or starboard.

Currently `cameras.json` hardcodes `"id": "bow"` and `"id": "stern"` — but that
only works because it was configured manually at install time. When a user plugs
in 4 new cameras, the system sees `camera_a7b3` (10.42.0.100) and
`camera_f2c1` (10.42.0.63) — it has no idea which direction they face.

---

## Solution

### The Core Idea

Add a `position` field to `cameras.json`. Each camera has exactly one position:
`bow`, `stern`, `port`, `starboard`, or `unassigned`.

In settings.html, each camera card shows its current position and an **Assign**
button. Tapping "Assign" lets the user pick a direction from 4 buttons. The
assignment is saved to `cameras.json` via a new API endpoint.

In marine-vision.html, the camera selector buttons show the **position label**
(Bow / Stern / Port / Starboard) instead of the camera name, so users navigate
by boat direction — which is natural when helming.

### User Flow (first install)

1. User mounts 4 cameras on the boat.
2. All 4 cameras connect to Pi hotspot and appear in settings under
   "Camera Management" as cards labelled by IP.
3. Each card shows "Position: Unassigned" and an [Assign Position] button.
4. User taps [Assign Position] on the camera whose feed looks like the bow.
   Four buttons appear inline: [Bow] [Stern] [Port] [Starboard].
5. User taps [Bow]. Card updates to show "Position: Bow".
6. Repeat for remaining 3 cameras.
7. Marine Vision page now shows [Bow] [Stern] [Port] [Starboard] selector buttons.

### cameras.json schema change (backwards compatible)

Add `"position"` field. Cameras without it default to `"unassigned"`.

```json
{
  "cameras": [
    {
      "id": "bow",
      "name": "Bow Camera",
      "position": "bow",
      "ip": "10.42.0.100",
      "rtsp_url": "rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub",
      "model": "Reolink",
      "detection_enabled": true
    },
    {
      "id": "stern",
      "name": "Stern Camera",
      "position": "stern",
      "ip": "10.42.0.63",
      "rtsp_url": "rtsp://admin:d3kos2026%24@10.42.0.63:554/h264Preview_01_sub",
      "model": "Reolink RLC-820A",
      "detection_enabled": false
    }
  ],
  "active_camera": "bow"
}
```

### New API endpoint

`POST /camera/assign`

Request body: `{"camera_id": "bow", "position": "stern"}`

- Validates position is one of: `bow`, `stern`, `port`, `starboard`, `unassigned`
- Validates camera_id exists in cameras.json
- If another camera already holds that position, clears it (one camera per position)
- Updates cameras.json on disk
- Returns `{"ok": true, "camera_id": "bow", "position": "stern"}`

`/camera/list` response already includes all camera fields — add `position` to
what it returns (it already passes through all fields from cameras.json).

---

## PHASE 1: ADD /camera/assign ENDPOINT — camera-assign-api

**File:** `camera_stream_manager.py`
**Action:** `INSERT_BEFORE`
**FIND_LINE:** `@app.route('/camera/grid', methods=['GET'])`

Insert a new Flask route immediately before the `/camera/grid` route:

```python
@app.route('/camera/assign', methods=['POST'])
def assign_camera_position():
    data = request.get_json()
    cam_id = data.get('camera_id')
    position = data.get('position')
    valid_positions = ['bow', 'stern', 'port', 'starboard', 'unassigned']
    if position not in valid_positions:
        return jsonify({'ok': False, 'error': 'invalid position'}), 400
    with open(CAMERAS_CONFIG) as f:
        config = json.load(f)
    found = False
    for cam in config['cameras']:
        if cam['id'] == cam_id:
            found = True
        if cam.get('position') == position and position != 'unassigned':
            cam['position'] = 'unassigned'
    if not found:
        return jsonify({'ok': False, 'error': 'camera not found'}), 404
    for cam in config['cameras']:
        if cam['id'] == cam_id:
            cam['position'] = position
    with open(CAMERAS_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)
    return jsonify({'ok': True, 'camera_id': cam_id, 'position': position})

```

**Variables already in scope (exact names from the file):**
- `CAMERAS_CONFIG` — path constant `'/opt/d3kos/config/cameras.json'`
- `json` — already imported at top of file
- `request`, `jsonify` — already imported (Flask)

**Do NOT:**
- Add any new imports
- Modify any other route
- Add a global statement — none is needed

---

## PHASE 2: UPDATE SETTINGS CAMERA CARDS — camera-assign-ui

**File:** `settings.html`
**Action:** `REPLACE`
**FIND_LINE:** `    function updateCameraStatus() {`
**END_LINE:** `        .catch(function(err) { console.error('Switch failed:', err); });`

> **MANDATORY:** Use FIND_LINE and END_LINE exactly as shown above — both are in CURRENT FILE CONTEXT.
> This replaces the entire block from `updateCameraStatus` through the catch of `switchCamera`.
> Do not use `<link>` tags, CSS, or HTML — this phase modifies JavaScript only.

Replace the entire Camera Management Functions block (from `// Camera Management
Functions` through the closing `}` of `switchCamera`) with:

```javascript
    // Camera Management Functions
    var POSITIONS = ['bow', 'stern', 'port', 'starboard'];

    function positionLabel(pos) {
      if (!pos || pos === 'unassigned') return 'Unassigned';
      return pos.charAt(0).toUpperCase() + pos.slice(1);
    }

    function assignPosition(camId, position) {
      fetch('/camera/assign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({camera_id: camId, position: position})
      })
        .then(function(r) { return r.json(); })
        .then(function() { updateCameraStatus(); })
        .catch(function(err) { console.error('Assign failed:', err); });
    }

    function renderAssignButtons(camId) {
      return POSITIONS.map(function(pos) {
        return '<button onclick="assignPosition(\'' + camId + '\',\'' + pos + '\')" ' +
          'style="margin:4px;padding:8px 14px;background:#333;color:#fff;border:1px solid #555;' +
          'border-radius:6px;font-size:16px;cursor:pointer;">' +
          positionLabel(pos) + '</button>';
      }).join('') +
      '<button onclick="assignPosition(\'' + camId + '\',\'unassigned\')" ' +
        'style="margin:4px;padding:8px 14px;background:#333;color:#888;border:1px solid #444;' +
        'border-radius:6px;font-size:16px;cursor:pointer;">Clear</button>';
    }

    function updateCameraStatus() {
      fetch('/camera/list')
        .then(function(r) { return r.json(); })
        .then(function(data) {
          var container = document.getElementById('camera-cards-container');
          if (!data.cameras || data.cameras.length === 0) {
            container.innerHTML = '<div class="setting-card" style="color:rgba(255,255,255,0.5);text-align:center;padding:20px;">No cameras configured</div>';
            return;
          }
          var html = '';
          data.cameras.forEach(function(cam) {
            var connColor = cam.connected ? '#00CC00' : '#FF0000';
            var connText  = cam.connected ? '✓ Connected' : '✗ Offline';
            var activeLabel = cam.active ? ' <span style="color:#FFD700;font-size:18px;">(Active)</span>' : '';
            var posLabel = positionLabel(cam.position);
            var posColor = (!cam.position || cam.position === 'unassigned') ? '#FF8800' : '#00CC00';
            var switchBtn = cam.active ? '' :
              '<button onclick="switchCamera(\'' + cam.id + '\')" style="margin-top:8px;margin-right:8px;padding:10px 20px;background:#00CC00;color:#000;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer;">Set Active</button>';
            html += '<div class="setting-card" style="margin-bottom:12px;">' +
              '<div style="font-size:20px;font-weight:700;color:#00CC00;margin-bottom:8px;">' + cam.name + activeLabel + '</div>' +
              '<div style="font-size:17px;color:rgba(255,255,255,0.7);">Model: ' + (cam.model || 'Reolink') + '</div>' +
              '<div style="font-size:17px;color:rgba(255,255,255,0.7);">IP: ' + cam.ip + '</div>' +
              '<div style="font-size:17px;color:' + connColor + ';">' + connText + '</div>' +
              '<div style="font-size:17px;color:' + posColor + ';margin-top:8px;">Position: ' + posLabel + '</div>' +
              '<div style="margin-top:10px;">' + renderAssignButtons(cam.id) + '</div>' +
              switchBtn +
              '</div>';
          });
          container.innerHTML = html;
        })
        .catch(function(err) {
          console.error('Failed to get camera list:', err);
          document.getElementById('camera-cards-container').innerHTML =
            '<div class="setting-card" style="color:#FF0000;padding:20px;">Camera service unavailable</div>';
        });
    }

    function switchCamera(camId) {
      fetch('/camera/switch/' + camId, { method: 'POST' })
        .then(function(r) { return r.json(); })
        .then(function() { updateCameraStatus(); })
        .catch(function(err) { console.error('Switch failed:', err); });
    }
```

**Variables:**
- `POSITIONS` — `['bow','stern','port','starboard']`
- `cam.position` — comes from cameras.json via `/camera/list` (may be missing on old configs — treat as `'unassigned'`)
- `cam.id`, `cam.name`, `cam.ip`, `cam.model`, `cam.connected`, `cam.active` — same as before

**Do NOT:**
- Change anything outside the Camera Management Functions block
- Add imports or require statements
- Change the `window.addEventListener('load', ...)` wiring at the bottom

---

## PHASE 3: UPDATE MARINE VISION SELECTOR — camera-vision-buttons

**File:** `marine-vision.html`
**Action:** `REPLACE`
**FIND_LINE:** `    function renderSelector(cams, activeId) {`
**END_LINE:** `      sel.innerHTML = html;`

> **MANDATORY:** Use FIND_LINE and END_LINE exactly as shown. Both lines are in CURRENT FILE CONTEXT.
> This replaces everything from the opening of `renderSelector` through `sel.innerHTML = html;`.
> The closing `}` will remain — your CODE must NOT include it.

Replace the entire `renderSelector` function (from `function renderSelector(cams, activeId) {`
through its closing `}`) with a version that shows direction labels (Bow/Stern/Port/Starboard)
instead of camera names. The button label should come from `cam.position` if set,
falling back to `cam.name` if position is missing or unassigned.

```javascript
    function renderSelector(cams, activeId) {
      const sel = document.getElementById('cameraSelector');
      let html = '';
      const posOrder = ['bow', 'stern', 'port', 'starboard'];
      posOrder.forEach(function(pos) {
        const cam = cams.find(function(c) { return c.position === pos; });
        if (!cam) return;
        const isActive  = cam.id === activeId && !gridMode;
        const isOffline = !cam.connected;
        let cls = 'cam-btn';
        if (isActive)  cls += ' active';
        if (isOffline) cls += ' offline';
        const label = pos.charAt(0).toUpperCase() + pos.slice(1);
        html += `<button class="${cls}" onclick="switchCamera('${cam.id}')">${label}</button>`;
      });
      if (!html) {
        cams.forEach(function(cam) {
          const isActive  = cam.id === activeId && !gridMode;
          const isOffline = !cam.connected;
          let cls = 'cam-btn';
          if (isActive)  cls += ' active';
          if (isOffline) cls += ' offline';
          html += `<button class="${cls}" onclick="switchCamera('${cam.id}')">${cam.name}</button>`;
        });
      }
      if (cams.length > 1) {
        const gCls = 'grid-btn' + (gridMode ? ' active' : '');
        html += `<button class="${gCls}" onclick="toggleGrid()">Grid View</button>`;
      }
      sel.innerHTML = html;
```

**Variables (exact names from the file — use these only):**
- `sel` — `document.getElementById('cameraSelector')`
- `gridMode` — existing global boolean
- `cams` — array of camera objects passed as argument
- `activeId` — active camera id passed as argument
- `cam.position` — new field from cameras.json (may be missing — treat as unassigned)
- `cam.id`, `cam.name`, `cam.connected` — existing fields
- `switchCamera(camId)` — existing function, do not modify
- `toggleGrid()` — existing function, do not modify

**Do NOT:**
- Modify `loadCameraList()` or `switchCamera()`
- Remove the Grid View button logic
- Remove the fallback `if (!html)` block — needed when no cameras have positions set

---

## Deployment Notes

1. Run phases 1–3 via Ollama executor
2. SCP `camera_stream_manager.py` to `/opt/d3kos/services/marine-vision/`
3. SCP `settings.html` and `marine-vision.html` to `/var/www/html/`
4. Update `cameras.json` on Pi to add `"position": "bow"` and `"position": "stern"` to existing cameras
5. `sudo systemctl restart d3kos-camera-stream`
6. Verify: `curl -s http://localhost/camera/list` — should include `position` field
7. Verify: `curl -s -X POST http://localhost/camera/assign -H 'Content-Type: application/json' -d '{"camera_id":"bow","position":"stern"}'`

---

## Future: Camera Discovery (v0.9.x)

When camera discovery is implemented (scanning Pi subnet for RTSP streams),
newly discovered cameras will arrive as `"position": "unassigned"`. The assign
UI in settings.html will immediately show them with orange "Unassigned" label
and the 4 direction buttons. No additional UI work needed.
