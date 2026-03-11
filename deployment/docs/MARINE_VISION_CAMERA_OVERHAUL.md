# Marine Vision — Camera Management Overhaul
## Dynamic Slot/Hardware Architecture (1–20 Cameras)

**Version:** v1.0 | **Date:** 2026-03-11 | **Status:** Specification
**Supersedes:** `MARINE_VISION_CAMERA_SYSTEM.md` (v0.9.2)
**Builds on:** `deployment/v0.9.2-multicam/`

---

## Problem Statement

The current system hardcodes camera positions (`bow`, `stern`) at config time inside `cameras.json`. This breaks in every real-world lifecycle scenario:

- No cameras exist at initial install
- Cameras are added one at a time over weeks or months
- A camera dies — the position still exists, the hardware doesn't
- A camera gets moved to a different position
- The owner installs cameras in locations no spec anticipated (bait tank, underwater hull, engine room, helm overhead)
- 1 to 20 cameras must all be supported without code changes

The fix is a clean separation: **positions are slots the owner defines, hardware is what fills them**.

---

## Core Mental Model

```
SLOT  =  A named position on the boat (owner creates, names, roles)
          Lives forever. Not tied to hardware.

HARDWARE  =  A physical camera discovered on the network
              Comes and goes. Has an IP and MAC.

ASSIGNMENT  =  The link between a slot and a piece of hardware
                Owner controls. Can be changed at any time.
```

Marine Vision, the fish detector, and the notification system **only talk to slots**. They never reference hardware IDs directly. When hardware changes, the slot stays. Nothing downstream needs to know.

---

## Data Files

### Replace `cameras.json` with two files:

#### `/opt/d3kos/config/slots.json`
Owner-defined positions. Persists forever.

```json
[
  {
    "slot_id": "bow",
    "label": "Bow",
    "display_order": 1,
    "roles": {
      "forward_watch": true,
      "fish_detection": true,
      "active_default": true,
      "display_in_grid": true
    },
    "hardware_id": "hw_aa_bb_cc_dd_ee_ff",
    "assigned": true,
    "created": "2026-03-11T10:00:00"
  },
  {
    "slot_id": "engine_room",
    "label": "Engine Room",
    "display_order": 2,
    "roles": {
      "forward_watch": false,
      "fish_detection": false,
      "active_default": false,
      "display_in_grid": true
    },
    "hardware_id": null,
    "assigned": false,
    "created": "2026-03-11T10:05:00"
  }
]
```

**Rules:**
- `slot_id` is a URL-safe slug generated from the label on creation (e.g. "Bait Tank" → `bait_tank`)
- Labels are free text — owner types whatever makes sense for their boat
- No preset list. No suggestions.
- `forward_watch`: exactly one slot may hold this role at a time
- `active_default`: exactly one slot may hold this at a time; falls back to `forward_watch` slot if unset
- `fish_detection`: any number of slots, no constraint
- `display_in_grid`: any number of slots; controls what appears in Marine Vision

---

#### `/opt/d3kos/config/hardware.json`
Discovered physical cameras. Managed by the system, not the owner.

```json
[
  {
    "hardware_id": "hw_aa_bb_cc_dd_ee_ff",
    "mac": "AA:BB:CC:DD:EE:FF",
    "ip": "10.42.0.100",
    "model": "Reolink RLC-820A",
    "rtsp_url": "rtsp://admin:d3kos2026%24@10.42.0.100:554/h264Preview_01_sub",
    "last_seen": "2026-03-11T14:22:00",
    "status": "online",
    "assigned_to_slot": "bow"
  },
  {
    "hardware_id": "hw_11_22_33_44_55_66",
    "mac": "11:22:33:44:55:66",
    "ip": "10.42.0.112",
    "model": "Reolink RLC-820A",
    "rtsp_url": "rtsp://admin:d3kos2026%24@10.42.0.112:554/h264Preview_01_sub",
    "last_seen": "2026-03-11T14:20:00",
    "status": "online",
    "assigned_to_slot": null
  }
]
```

**Rules:**
- `hardware_id` is derived from MAC: `hw_` + MAC with colons replaced by underscores (lowercase)
- This gives hardware a stable identity even if its IP changes
- System writes this file — owner never edits it directly
- `status` values: `online`, `offline`, `unassigned`

---

## Migration from cameras.json

One-time migration script runs on first deploy. It reads `cameras.json`, creates `slots.json` and `hardware.json` from the existing data, and renames `cameras.json` to `cameras.json.bak`.

**Migration mapping:**
- Each entry in `cameras.json` → one slot + one hardware entry
- Existing `position` field → `slot_id` and `label`
- `detection_enabled: true` → `roles.fish_detection: true`
- The camera with `position: "bow"` gets `roles.forward_watch: true` and `roles.active_default: true`
- All existing cameras get `assigned: true`
- All existing cameras get `status: online`

No manual re-entry. The system keeps working through the transition without any visible change.

---

## camera_stream_manager.py Changes (Port 8084)

### Frame Buffer — Critical for Scaling

**Current problem:** Each browser client that requests a frame causes a fresh RTSP decode. At 20 cameras with 3 browser tabs open, that's 60 simultaneous RTSP decoders. The Pi dies.

**Fix:** One background thread per hardware entry decodes RTSP continuously and writes to a frame buffer. Any number of `/camera/frame/<slot_id>` requests read from the buffer — zero additional RTSP load.

```python
# Conceptual structure
frame_buffers = {}  # hardware_id → latest JPEG bytes
decode_threads = {} # hardware_id → background thread

def frame_grabber_thread(hardware_id, rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        ret, frame = cap.read()
        if ret:
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_buffers[hardware_id] = jpeg.tobytes()
        else:
            # reconnect logic
            time.sleep(5)
            cap = cv2.VideoCapture(rtsp_url)
```

### New API Endpoints

All existing endpoints are preserved unchanged for backwards compatibility.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/camera/slots` | All slots + assigned hardware status |
| GET | `/camera/hardware` | All discovered hardware (assigned + unassigned) |
| POST | `/camera/slots` | Create new slot |
| PATCH | `/camera/slots/<slot_id>` | Update label, display_order, or roles |
| POST | `/camera/slots/<slot_id>/assign` | Assign hardware_id to slot |
| POST | `/camera/slots/<slot_id>/unassign` | Remove hardware assignment from slot |
| DELETE | `/camera/slots/<slot_id>` | Delete slot (hardware returned to unassigned pool) |
| POST | `/camera/scan` | Trigger network discovery scan |
| GET | `/camera/frame/<slot_id>` | Single frame by slot (resolves slot→hardware→buffer) |
| GET | `/camera/status` | Active camera status (backwards compat — returns forward_watch slot) |
| GET | `/camera/frame` | Active camera frame (backwards compat — returns forward_watch slot frame) |

**Removed:** `/camera/grid` (server-side stitched JPEG). The browser now handles grid layout.

### Role Constraint Enforcement

When `PATCH /camera/slots/<slot_id>` sets `forward_watch: true`:
1. Find any other slot currently holding `forward_watch: true`
2. Set it to `false` on that slot
3. Set it to `true` on the requested slot
4. Write both changes atomically

Same logic for `active_default`.

### Discovery Scan

Runs at:
1. Service startup (once, non-blocking — happens in background thread)
2. `POST /camera/scan` from UI
3. Never on a background timer (avoids false positives from phones/tablets on the hotspot)

**Algorithm:**
```
For each IP in 10.42.0.50 – 10.42.0.200:
    If TCP port 554 responds within 300ms:
        Read MAC from ARP table
        Derive hardware_id from MAC
        If hardware_id not in hardware.json:
            Add as unassigned entry
        Else if status was 'offline':
            Update status to 'online', update IP (handles DHCP changes)
```

Scan is threaded — all IPs probed concurrently with a 300ms timeout. Full scan of 150 IPs completes in under 2 seconds.

---

## Settings Page — Camera Setup Tab

### Layout

Three-column layout on desktop, stacked on mobile (d3kOS touch targets apply — 80px minimum button height):

```
┌──────────────────────────────────────────────────────────────────┐
│  CAMERA SETUP                                   [Scan for Cameras]│
├────────────────────┬──────────────────────┬──────────────────────┤
│  POSITIONS         │  SLOT DETAIL         │  UNASSIGNED CAMERAS  │
│  [+ New Position]  │                      │                      │
│                    │  (select a slot      │  No unassigned       │
│  ● Bow        ✅  │   to edit it)        │  cameras detected.   │
│  ● Engine Rm  ⚠️  │                      │                      │
│  ○ Helm       ❌  │                      │  [Scan for Cameras]  │
│                    │                      │                      │
└────────────────────┴──────────────────────┴──────────────────────┘
```

**Slot status indicators:**
- ✅ green — slot has a camera and it's online
- ⚠️ amber — slot has a camera but it's offline (needs replacement)
- ❌ red — slot exists, no camera assigned

### Slot Detail Panel (when a slot is selected)

```
┌──────────────────────────┐
│  Bow                [✎]  │   ← label, tap to rename
│                          │
│  [live thumbnail]        │   ← JPEG from /camera/frame/bow, refreshed 1/sec
│                          │
│  ─── Roles ───           │
│  ○ Forward Watch     [●] │   ← radio, only one slot can hold this
│  ○ Fish Detection    [●] │   ← toggle, any number of slots
│  ○ Active Default    [●] │   ← radio, only one slot can hold this
│  ○ Show in Grid      [●] │   ← toggle, any number of slots
│                          │
│  ─── Hardware ───        │
│  Reolink RLC-820A        │
│  10.42.0.100  ● online   │
│                          │
│  [Reassign Camera]       │
│  [Unassign Camera]       │
│                          │
│  ─── ─────────── ───     │
│  [Delete Position]       │   ← red, requires confirmation
└──────────────────────────┘
```

**Reassign flow:** Opens a modal showing all unassigned hardware as thumbnail cards. Owner taps one to assign it. Modal closes, detail panel updates.

### New Position Flow

Owner taps **+ New Position**:

```
┌─────────────────────────────────┐
│  New Position                   │
│                                 │
│  Name: [________________]       │   ← free text, any name
│                                 │
│  Roles:                         │
│  [ ] Forward Watch              │
│  [ ] Fish Detection             │
│  [x] Show in Grid               │   ← on by default
│                                 │
│  [Save]  [Cancel]               │
└─────────────────────────────────┘
```

On save, slot is created with `hardware_id: null`. It immediately appears in the slot list with ❌ status. Owner then assigns hardware from the unassigned panel or waits until a camera is physically connected.

### Unassigned Hardware Panel

Each unassigned camera shows:
- Live thumbnail (or grey placeholder if frame unavailable)
- IP address
- Model (if detectable)
- Last seen timestamp
- **[Assign to Position]** button — opens slot picker

### Role Summary Bar (bottom of page)

Always visible, single-line status check:

```
Forward Watch: Bow ✅   |   Fish Detection: Bow, Stern ✅   |   Active Default: Bow ✅
```

Turns amber with a warning message if Forward Watch is unassigned.

---

## Marine Vision UI Changes (marine-vision.html)

### Replace stitched grid JPEG with dynamic tile renderer

**Current:** One `<img>` tag refreshed on a timer, src pointing to `/camera/grid`
**New:** One `<div class="camera-grid">` containing one tile per slot with `display_in_grid: true`

### Adaptive Grid Layout

On page load and whenever slot count changes:
```javascript
function computeGridLayout(activeCount) {
    const cols = Math.ceil(Math.sqrt(activeCount));
    const rows = Math.ceil(activeCount / cols);
    grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
}
```

| Active slots | Columns | Rows |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 1 |
| 3–4 | 2 | 2 |
| 5–6 | 3 | 2 |
| 7–9 | 3 | 3 |
| 10–12 | 4 | 3 |
| 13–16 | 4 | 4 |
| 17–20 | 5 | 4 |

At 17+ slots, tiles become small. Scrolling is enabled. Alternatively, the owner should consider whether all 20 cameras truly need `display_in_grid: true` — most monitoring use cases have 2–6 active in the grid with the rest accessible via the slot list.

### Focus Mode (Primary + Filmstrip)

Default view loads in **Focus Mode**:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│          PRIMARY FEED (forward_watch slot)          │
│          + fish detection overlay if active         │
│          + slot label top-left                      │
│          + online/offline indicator                 │
│                                                     │
├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┤
│  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  ← filmstrip
└──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
```

Clicking any filmstrip tile swaps it into the primary view. Tapping the primary view switches to **Grid Mode** (all tiles equal size). Toggle button in top-right corner switches between modes.

### Staggered Polling — Critical for Pi CPU

Never fire all frame requests simultaneously. Stagger by priority tier:

```javascript
const POLL_TIERS = {
    primary: 500,       // ms — forward_watch slot, smooth enough to watch
    grid_active: 2000,  // ms — all other display_in_grid slots
    offline: 0          // no polling — skip entirely
};

// Stagger grid tile requests so they never fire at the same time
function scheduleGridRefresh(tiles) {
    tiles.forEach((tile, index) => {
        setTimeout(() => {
            startPolling(tile, POLL_TIERS.grid_active);
        }, index * 200); // 200ms between each tile's first request
    });
}
```

At 16 grid tiles refreshing every 2000ms, staggered 200ms apart: maximum of 1 request in flight at any time. Pi handles this trivially.

### Empty and Offline States

**No slots configured:**
```
No cameras configured.
Visit Settings → Camera Setup to add your first camera.
[Go to Settings]
```

**Slot has no hardware:**
Grey tile with slot label and ❌ — still visible in grid so owner knows the position exists.

**Slot hardware offline:**
Last known frame shown with amber border + "Camera offline" overlay. Slot label still shown.

### Fish Detection Overlay

Fish detection currently assumes one forward-watch camera. With the slot model, `fish_detector.py` reads `slots.json` and processes frames from all slots with `roles.fish_detection: true`. Detection results are tagged with `slot_id`.

Marine Vision displays detection bounding boxes only on the primary view (too small to see on filmstrip tiles). If a fish is detected on a non-primary slot, that slot's filmstrip tile gets a green pulsing border.

---

## fish_detector.py Changes (Port 8086)

Currently hardcoded to pull from `http://localhost:8084/camera/frame` (the single active camera). Must change to:

1. Read `slots.json` on startup and whenever `POST /detect/reload` is called
2. Build a list of slots with `roles.fish_detection: true`
3. For each such slot, pull from `/camera/frame/<slot_id>` at the detection interval
4. Tag all detection results and capture records with `slot_id`
5. Expose `slot_id` in the `/captures` API response

No other changes needed. The frame buffer in `camera_stream_manager.py` means the fish detector fetching from multiple slots adds zero RTSP load.

---

## Lifecycle Scenarios — How Each One Works

### Fresh install, no cameras

`slots.json` = `[]`, `hardware.json` = `[]`

Settings shows empty state + **+ New Position** button. Marine Vision shows "No cameras configured." No errors.

Owner can pre-create slots (name positions, assign roles) before any cameras arrive. Slots sit at ❌ status until hardware is assigned.

### New camera physically connected to hotspot

Camera appears on `10.42.0.x`. Next scan (triggered by owner hitting **Scan for Cameras** or by service restart) finds it, adds it to `hardware.json` with `assigned_to_slot: null`.

Settings shows the unassigned camera panel: live thumbnail, IP, **[Assign to Position]** button.

Owner taps Assign, picks an existing slot or creates a new one. Done. Camera is live in Marine Vision immediately.

### Camera goes bad

Old camera drops off network. `hardware.json` marks it `status: offline`. Slot still exists, shows ⚠️ in settings. Marine Vision shows last known frame with amber "Camera offline" overlay.

Owner installs replacement camera. It appears in unassigned hardware. Owner opens the ⚠️ slot, taps **Reassign Camera**, picks new hardware. Slot roles (forward watch, fish detection, etc.) are unchanged. Marine Vision goes back to ✅. Total owner actions: 2 taps.

### Camera moved to different position

Owner physically relocates a camera. In Settings:
1. Open old slot → **Unassign Camera** → slot goes to ❌
2. Open new slot (or create it) → **Assign Camera** → pick the hardware from unassigned list
3. Done. Old slot's roles preserved for when a new camera arrives for that position.

### Owner changes their mind about a slot name

Tap the slot label (✎ edit icon). Type new name. Save. `slot_id` stays the same (stable for API references). Label updates everywhere immediately.

### Adding camera 5 through 20

Identical to "new camera physically connected." No code changes. No config file restructuring. The Settings UI and Marine Vision grid scale automatically.

---

## Files to Create / Modify

| File | Action | What Changes |
|------|--------|-------------|
| `/opt/d3kos/config/slots.json` | **Create** | New file (from migration) |
| `/opt/d3kos/config/hardware.json` | **Create** | New file (from migration) |
| `/opt/d3kos/config/cameras.json` | **Rename to .bak** | Replaced by above two files |
| `camera_stream_manager.py` | **Major rewrite** | Frame buffer, slot/hardware API, discovery scan, remove stitched grid |
| `marine-vision.html` | **Major rewrite** | Dynamic tile grid, focus mode, staggered polling, slot-aware rendering |
| `settings.html` | **Add tab** | Camera Setup tab (three-panel layout) |
| `fish_detector.py` | **Minor update** | Read slots.json, tag captures with slot_id, multi-slot support |
| `migrate_cameras.py` | **Create** | One-time migration script, runs once then stays for reference |

---

## Build Order

### Step 1 — Data Layer (no visible change to users)
- Write `migrate_cameras.py`
- Run migration on Pi: produces `slots.json` and `hardware.json` from existing `cameras.json`
- Verify existing camera feed still works (camera_stream_manager still reads cameras.json during transition)

### Step 2 — Backend (camera_stream_manager.py)
- Implement frame buffer (highest priority — required for >4 cameras)
- Add slot/hardware data loading (replaces cameras.json reads)
- Add new API endpoints
- Add discovery scan
- Keep all existing endpoints working
- Deploy and verify existing Marine Vision still functions

### Step 3 — Settings UI (settings.html)
- Add Camera Setup tab
- Three-panel layout: slot list, slot detail, unassigned hardware
- New Position flow
- Assign/Unassign/Reassign flows
- Role toggles with constraint enforcement
- Scan for Cameras button

### Step 4 — Marine Vision UI (marine-vision.html)
- Dynamic tile grid renderer
- Adaptive column layout
- Focus mode + filmstrip
- Staggered polling
- Empty / offline state handling
- Fish detection overlay on primary view

### Step 5 — Fish Detector (fish_detector.py)
- Read slots.json for fish_detection role
- Multi-slot frame fetching
- Tag captures with slot_id

---

## Performance Targets (unchanged from v0.9.2)

| Metric | Target | Notes |
|--------|--------|-------|
| CPU (all cameras streaming) | <35% | Frame buffer decode-once model |
| Memory (all cameras) | <970MB total | ~50MB per active RTSP stream |
| Grid bandwidth (16 cameras) | <12Mbps | Staggered 2s refresh at 85% JPEG quality |
| Primary feed bandwidth | <4Mbps | 500ms refresh, sub-stream |
| Settings scan time | <3 seconds | 150-IP concurrent probe |

---

## What Does NOT Change

- Port 8084 for camera_stream_manager
- Port 8086 for fish_detector
- Port 8088 for notification_manager
- Nginx proxy configuration
- Systemd service names and unit files
- RTSP credential format (percent-encoded in hardware.json)
- DHCP reservation process (setup_dhcp_reservations.py reads from hardware.json instead of cameras.json — one-line change)
- d3kOS black/green theme, touch target sizes, font sizes
- Offline detection: "Camera offline — not on boat network" message still appears when `10.42.0.x` network is unreachable

---

*Document created: 2026-03-11 | Next: migrate_cameras.py + camera_stream_manager.py rewrite*
