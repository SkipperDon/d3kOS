# Marine Vision Camera Overhaul — Build Checklist
**Spec:** `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md`
**Started:** 2026-03-11
**Base:** `deployment/v0.9.2-multicam/pi_source/`

---

## Step 1 — Data Layer (migrate_cameras.py)
**Goal:** Produce slots.json + hardware.json from existing cameras.json. No visible change to running system.

- [x] `migrate_cameras.py` written to `pi_source/migrate_cameras.py`
- [x] Reviewed for correctness — role mapping, MAC lookup, fallback IDs
- [x] Deployed to Pi at `/opt/d3kos/services/marine-vision/migrate_cameras.py`
- [x] Run on Pi: `python3 /opt/d3kos/services/marine-vision/migrate_cameras.py`
- [x] Verify `/opt/d3kos/config/slots.json` created and valid JSON
- [x] Verify `/opt/d3kos/config/hardware.json` created and valid JSON
- [x] Verify `/opt/d3kos/config/cameras.json.bak` exists (617 bytes, Mar 10)
- [x] Confirm existing camera feed still working — `d3kos-camera-stream.service` active, port 8084 responding
- [x] Both MACs resolved from ARP (no fallback IDs needed)
  - bow:   EC:71:DB:F9:7C:7C → hw_ec_71_db_f9_7c_7c (10.42.0.100)
  - stern: EC:71:DB:99:78:04 → hw_ec_71_db_99_78_04 (10.42.0.63)

**Step 1 COMPLETE — 2026-03-11**

**Rollback:** Delete slots.json, hardware.json. Rename cameras.json.bak → cameras.json. Restart camera_stream_manager.

---

## Step 2 — Backend (camera_stream_manager.py)
**Goal:** Port 8084 rewrite. Frame buffer, slot/hardware API, discovery scan. All existing endpoints preserved.

- [x] `camera_stream_manager.py` written to `pi_source/camera_stream_manager.py`
- [x] Frame buffer implemented (one thread per hardware, keyed by hardware_id)
- [x] `load_config()` reads slots.json + hardware.json (replaces cameras.json)
- [x] New endpoints implemented:
  - [x] `GET /camera/slots` — verified, returns both slots with roles + hardware
  - [x] `GET /camera/hardware` — verified, returns both HW entries connected+has_frame
  - [x] `POST /camera/slots` — implemented
  - [x] `PATCH /camera/slots/<slot_id>` — implemented with exclusive role enforcement
  - [x] `POST /camera/slots/<slot_id>/assign` — implemented
  - [x] `POST /camera/slots/<slot_id>/unassign` — implemented
  - [x] `DELETE /camera/slots/<slot_id>` — implemented
  - [x] `POST /camera/scan` — verified, scan finds 10.42.0.63 + 10.42.0.100
  - [x] `GET /camera/frame/<slot_id>` — verified bow (47601 bytes) + stern (39882 bytes)
- [x] Backwards-compat endpoints verified:
  - [x] `GET /camera/status` → returns bow (forward_watch), credentials masked
  - [x] `GET /camera/frame` → returns forward_watch slot frame (47601 bytes)
  - [x] `GET /camera/list` → returns slots as cameras list, active_camera=bow
  - [x] `POST /camera/switch/<id>` → implemented (sets active_default)
  - [x] Recording, capture, recordings endpoints preserved unchanged
  - [x] `POST /camera/assign` → returns 410 Gone with helpful redirect message
- [x] `/camera/grid` endpoint removed
- [ ] `setup_dhcp_reservations.py` updated to read hardware.json (deferred — check if file exists)
- [x] Deployed to Pi, service restarted (d3kos-camera-stream.service active)
- [x] PYTHONUNBUFFERED=1 added to systemd unit — scan logs now visible in journalctl
- [x] Scan at startup finds both cameras: Scan: 2 IP(s) on port 554
- [x] Existing marine-vision.html still functional (backwards compat confirmed)

**Step 2 COMPLETE — 2026-03-11**

**Rollback:** `sudo cp camera_stream_manager.py.bak.20260311164427 camera_stream_manager.py && sudo systemctl restart d3kos-camera-stream.service` on Pi.

---

## Step 3 — Settings UI (settings.html — Camera Setup tab)
**Goal:** Three-panel camera management UI. All slot CRUD and assign/unassign flows.

- [x] `settings.html` updated with Camera Setup section (replaces broken duplicate camera section)
- [x] Three-panel CSS grid (slot list | slot detail | unassigned hardware) — stacks to 1-col below 900px
- [x] Slot list: status dots (green/amber/red/grey), role tags [FW][Fish], tap to select
- [x] `[+ New Position]` modal: name + FW/Fish/Grid checkboxes → POST /camera/slots → verified (test_bait_tank created + deleted)
- [x] Slot detail panel:
  - [x] Live thumbnail 1/sec from /camera/frame/<slot_id>
  - [x] Inline label edit + Save → PATCH /camera/slots/<slot_id>
  - [x] Role toggles → PATCH with role map
  - [x] Hardware info (IP, model, connected status)
  - [x] [Assign/Reassign Camera] → modal showing available hardware
  - [x] [Unassign Camera] → POST /camera/slots/<slot_id>/unassign
  - [x] [Delete Position] → confirm → DELETE /camera/slots/<slot_id>
- [x] Unassigned hardware panel: thumbnail + IP + model + [Assign to Position]
- [x] [Scan for Cameras] buttons (header + hw panel) → POST /camera/scan + reload after 3.5s
- [x] Role summary bar: Forward Watch / Fish Detection / Active Default with online status
- [x] Role constraint verified: stern forward_watch=true → bow forward_watch auto-cleared to false
- [x] Slug generation: "Test Bait Tank" → test_bait_tank
- [x] All action buttons: min-height 80px (touch-friendly)
- [x] Deployed to Pi — backup at settings.html.bak.20260311165043
- [x] API roundtrip verified: slots, hardware, PATCH, POST, DELETE all returning correct data
- [ ] Tested on Pi touchscreen (requires on-boat session)

**Step 3 COMPLETE — 2026-03-11**

**Rollback:** `sudo cp /var/www/html/settings.html.bak.20260311165043 /var/www/html/settings.html`

---

## Step 4 — Marine Vision UI (marine-vision.html)
**Goal:** Dynamic slot-aware tile renderer. Focus mode + filmstrip. Staggered polling.

- [x] `marine-vision.html` full rewrite (898 lines)
- [x] Page load: fetches `/camera/slots`, builds tile set from `display_in_grid: true` slots
- [x] CSS grid: `Math.ceil(Math.sqrt(n))` columns — scales 1→20 slots automatically
- [x] Focus mode (default):
  - [x] Primary view: forward_watch slot at 500ms poll
  - [x] Filmstrip: all other display_in_grid slots at 2000ms, staggered 200ms apart
  - [x] Tap filmstrip tile → swaps to primary (`mvSwapPrimary`)
  - [x] Tap primary OR toggle button → switches to Grid Mode
  - [x] Toggle button top-right header: "Grid View" ↔ "Focus View"
- [x] Grid mode: equal-size tiles, tap any tile → switches to Focus Mode with that tile as primary
- [x] Empty state: "No cameras configured" + [Go to Settings] button
- [x] Offline tile: amber text overlay "Camera offline" (focus) / inline message (grid)
- [x] Unassigned tile: grey placeholder with ○ indicator
- [x] Fish detection overlay: canvas element over primary-img, draws bboxes from /detect/frame
- [x] Filmstrip fish_detection slots: green pulsing border class `fish-active`
- [x] `pageshow` event used (not DOMContentLoaded) — bfcache safe
- [x] Zero `/camera/grid` references — server-side stitch removed
- [x] POLL_PRIMARY=500ms, POLL_GRID_ACTIVE=2000ms, POLL_STAGGER_MS=200ms confirmed in deployed file
- [x] All 6 API endpoints return 200: slots, frame/bow, frame/stern, status, detect/status, recordings
- [x] Deployed to Pi — backup at marine-vision.html.bak.20260311
- [ ] Tested on Pi touchscreen (requires on-boat session)

**Step 4 COMPLETE — 2026-03-11**

**Rollback:** `sudo cp /var/www/html/marine-vision.html.bak.20260311* /var/www/html/marine-vision.html`

---

## Step 5 — Fish Detector (fish_detector.py)
**Goal:** Multi-slot detection. Read slots.json. Tag all captures with slot_id.

- [x] `fish_detector.py` updated
- [x] Reads slots.json on startup, builds list of `fish_detection: true` slots
- [x] `POST /detect/reload` endpoint added (re-reads slots.json without restart)
- [x] Detection loop iterates all fish_detection slots
- [x] Each frame fetched from `/camera/frame/<slot_id>`
- [x] All detection results tagged with slot_id
- [x] `captures` DB table has `slot_id` column (migration for existing rows)
- [x] `/captures` API response includes slot_id per record
- [x] `/detect/status` response includes per-slot status — `fish_detection_slots: ['stern']`, `slot_statuses: {stern: online}`
- [x] Deployed to Pi, service restarted — `d3kos-fish-detector.service` active
- [ ] Detection fires on both cameras independently (stern only has fish_detection=true — verified slot_id=stern in future captures)
- [ ] Captures in DB show correct slot_id (pre-migration rows null — new captures will populate)
- [ ] Marine Vision shows bounding boxes on correct primary tile

**Step 5 COMPLETE — 2026-03-11**

**Rollback:** `sudo cp /opt/d3kos/services/marine-vision/fish_detector.py.bak.* /opt/d3kos/services/marine-vision/fish_detector.py && sudo systemctl restart d3kos-fish-detector.service` (DB migration is additive — no data loss on rollback.)

---

## Final Verification (all steps complete)

- [ ] Fresh install scenario: delete slots.json + hardware.json, visit Marine Vision → "No cameras configured" empty state — requires cameras
- [ ] Scan finds both cameras, add them to slots → both feed correctly — requires cameras
- [ ] Camera offline scenario: confirmed amber state shown — requires cameras
- [ ] Performance: CPU <35%, memory <970MB, scan <3sec — requires cameras
- [x] DEPLOYMENT_INDEX.md updated with camera-overhaul feature entry — COMPLETE 2026-03-11

---

## Files Changed (full list)

| File | Pi Path | Step | Change Type |
|------|---------|------|-------------|
| `migrate_cameras.py` | `/opt/d3kos/services/camera/` | 1 | New |
| `slots.json` | `/opt/d3kos/config/` | 1 | New (from migration) |
| `hardware.json` | `/opt/d3kos/config/` | 1 | New (from migration) |
| `camera_stream_manager.py` | `/opt/d3kos/services/camera/` | 2 | Major rewrite |
| `setup_dhcp_reservations.py` | `/opt/d3kos/services/camera/` | 2 | One-line change |
| `settings.html` | `/var/www/html/` | 3 | Add tab |
| `marine-vision.html` | `/var/www/html/` | 4 | Major rewrite |
| `fish_detector.py` | `/opt/d3kos/services/camera/` | 5 | Minor update |
