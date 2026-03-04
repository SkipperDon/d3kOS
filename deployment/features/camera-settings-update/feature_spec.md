# Feature: Camera Settings — Dynamic Multi-Camera Display
# File: settings.html (one phase, one file)

## Context

The Camera Management section in settings.html currently shows only "Camera 1"
with hardcoded IDs. The camera service now serves multiple cameras via
`GET /camera/list` which returns all cameras with status.

`/camera/list` response format:
```json
{
  "active_camera": "bow",
  "cameras": [
    {"id":"bow","name":"Bow Camera","ip":"10.42.0.100","connected":true,"has_frame":true,"active":true,"model":"Reolink"},
    {"id":"stern","name":"Stern Camera","ip":"10.42.0.63","connected":true,"has_frame":true,"active":false,"model":"Reolink RLC-820A"}
  ]
}
```

`POST /camera/switch/<id>` switches the active camera. Returns `{"ok":true,"active_camera":"<id>"}`.

---

## PHASE 1: UPDATE HTML — camera-html

**File:** `settings.html`
**Action:** `REPLACE`
**FIND_LINE:** `        <h2 class="section-header">📹 Camera Management</h2>`

Replace everything from the `<h2>` Camera Management header through the closing
`</div>` of the btn-group (the one with "Add New Camera" and "View All Cameras"
buttons) with the following new block:

```html
        <h2 class="section-header">📹 Camera Management</h2>
        <div id="camera-cards-container">
          <div class="setting-card" style="color:rgba(255,255,255,0.5);text-align:center;padding:20px;">Loading cameras...</div>
        </div>
        <div class="btn-group">
          <button class="btn btn-secondary" onclick="window.location.href='/marine-vision.html'">
            <span class="btn-icon">📹</span>
            Open Marine Vision
          </button>
        </div>
```

**The exact block to replace ends at this line (inclusive):**
`          </button>`  ← the closing button tag of "View All Cameras"

**IMPORTANT:** The FIND_LINE must be the `<h2>` line shown above.
The REPLACE code block must include everything from that `<h2>` through
the new `</div>` closing the btn-group.

**Variables:** none needed in HTML — the JS function will populate
`camera-cards-container`.

---

## PHASE 2: UPDATE JS — camera-js

**File:** `settings.html`
**Action:** `REPLACE`
**FIND_LINE:** `    // Camera Management Functions`

Replace the entire `updateCameraStatus()`, `discoverNewCamera()`, and
`viewCameraList()` functions (everything from `// Camera Management Functions`
through the closing `}` of `viewCameraList`) with:

```javascript
    // Camera Management Functions
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
            var switchBtn = cam.active ? '' :
              '<button onclick="switchCamera(\'' + cam.id + '\')" style="margin-top:12px;padding:10px 20px;background:#00CC00;color:#000;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer;">Set Active</button>';
            html += '<div class="setting-card" style="margin-bottom:12px;">' +
              '<div style="font-size:20px;font-weight:700;color:#00CC00;margin-bottom:8px;">' + cam.name + activeLabel + '</div>' +
              '<div style="font-size:17px;color:rgba(255,255,255,0.7);">Model: ' + (cam.model || 'Reolink') + '</div>' +
              '<div style="font-size:17px;color:rgba(255,255,255,0.7);">IP: ' + cam.ip + '</div>' +
              '<div style="font-size:17px;color:' + connColor + ';">' + connText + '</div>' +
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

**IMPORTANT RULES:**
- The FIND_LINE is exactly: `    // Camera Management Functions`
- Do NOT invent any variable names not shown in this spec
- Do NOT add imports or require statements
- The functions `discoverNewCamera` and `viewCameraList` are being removed entirely — do not keep them
- Use `fetch('/camera/list')` not `/camera/status`
- Use `fetch('/camera/switch/' + camId, { method: 'POST' })` for switching
