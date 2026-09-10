# D16 — 3D Surround Situational Awareness
## d3kOS Feature Specification

**Document:** `D16_3D_SURROUND_VIEW_SPEC.md`
**Version:** 1.0
**Created:** 2026-09-10 S156
**Status:** APPROVED FOR BUILD — v0.9.9.5
**Owner:** Donald Moskaluk — AtMyBoat.com / d3kOS
**Target Platform:** Raspberry Pi 4B · d3kOS v0.9.9.5
**Hardware required:** None — uses existing 4 cameras and existing Pi

---

## 1. Purpose

A surround situational awareness display rendered in Chromium at the helm. Uses the existing 4 cameras (bow, helm/stern, port, starboard — all Reolink RLC-810A/820A, confirmed installed S112). Accessible from the d3kOS dashboard via a single toggle that switches between AvNav (:8080) and this view.

This is Phase 1 of three phases:
- **Phase 1 (v0.9.9.5):** Base view — camera stitching, range rings, no AI. Builds independently.
- **Phase 2 (v0.9.9.6):** D11 AI overlays — detection boxes + bearing markers on the view.
- **Phase 3 (v0.9.9.6):** WiBoat range integration — positionally accurate range rings from measured distances.

---

## 2. Display Layout

Resolution: **1920×1200** landscape (confirmed from d3kOS Chromium flags).

```
┌─────────────────────────────┬──────────────────────┐
│  FORWARD PANEL              │  BIRD'S EYE STITCH   │
│  Bow cam — perspective view │  All 4 cameras        │
│  50m+ range rings (SVG)     │  Homography stitch    │
│  (Phase 2: D11 boxes)       │  Forward-emphasized   │
│  (Phase 3: WiBoat rings)    │  (Phase 2: D11 marks) │
│  (~65% of top section)      │  (~35% of top section)│
├─────────────────────────────┴──────────────────────┤
│  MARINE VISION — existing screens (unchanged)      │
│  Camera grids · fish detection · controls          │
└────────────────────────────────────────────────────┘
```

**Why forward panel + bird's eye (not pure bird's eye):**
Camera-only bird's eye loses useful resolution past ~15–20m — a camera at 1–2m above the waterline sees 50m objects at a very shallow angle and top-down projection compresses them to near-zero pixels. The forward perspective panel solves this: natural perspective projection shows 50m+ clearly with SVG range rings calibrated to the bow camera's FOV and mount height. The bird's eye handles close-quarters spatial awareness around the hull. This is the same approach used in Garmin Surround View (commercial marine reference).

---

## 3. Toggle — AvNav ↔ 3D View

**Hard constraint: the toggle must not touch the engine ribbon, nav ribbon, or row-pill controls.**

- AvNav runs as `#avnav-frame` iframe inside the d3kOS dashboard.
- Engine row (`#rowEngine`) and nav row (`#rowNav`) are fully independent — they stay full width at all times. This is existing behaviour.
- The toggle switches only the iframe `src` — AvNav URL ↔ `:3000/3d-view`. One JS call.
- The row-pill controls (BOTH / ENGINE / NAV / WX) that govern the ribbons are completely unaffected.
- Toggle button sits outside both ribbon rows — exact placement confirmed against live layout during build.

---

## 4. Technology Stack

All decisions confirmed S147 2026-09-05. No Three.js or Babylon.js required. The browser does layout only. All video processing is Python/go2rtc.

### 4.1 go2rtc
- **Repo:** `github.com/AlexxIT/go2rtc` — MIT licence
- Pre-built ARM64 binary, runs on Pi natively — no compilation
- All 4 Reolink RTSP sub-streams configured in one YAML file
- Forward panel: bow camera WebRTC stream in HTML `<video>` element

### 4.2 Bird's Eye Homography Stitch
- Implemented natively in d3kOS using **OpenCV** (`cv2.getPerspectiveTransform` + `cv2.warpPerspective`) — ~50 lines Python, Apache 2.0
- **Not** dependent on `dyfcalid/CameraCalibration` (GPL-3.0) — that project is the reference only, not a dependency
- Output: OpenCV MJPEG stream → served by existing Flask camera service at port 8084 → HTML `<img>` element in the 3D view page

### 4.3 SVG Range Rings
- Plain SVG overlay on the `<video>` element
- Rings at 10m / 25m / 50m
- Calibrated to bow camera mount height and vertical FOV
- **No hardcoded values** — user enters camera height once in Settings; ring pixel positions calculate automatically (formula in §6)
- No library required

### 4.4 Flask Route
- Python Flask serves `/3d-view` as a new route in `app.py`
- Fits the existing d3kOS service pattern exactly

---

## 5. Open Architecture Decision — go2rtc vs. camera_stream_manager.py

**⚠ This decision must be made before build begins.**

go2rtc overlaps with the existing `camera_stream_manager.py` at port 8084. Options:

| Option | Description | Impact |
|--------|-------------|--------|
| A | go2rtc serves D16 only; `camera_stream_manager.py` unchanged | Zero risk to existing Marine Vision. go2rtc runs as a separate service on a new port. |
| B | go2rtc runs alongside `camera_stream_manager.py` on the same streams | Both services pull RTSP sub-streams. Reolink cameras support multiple concurrent sub-stream clients — low risk, but doubles stream connections. |
| C | go2rtc replaces `camera_stream_manager.py` entirely | Eliminates duplication. High risk — Marine Vision, fish detection, and camera grid all depend on `camera_stream_manager.py`. Requires full regression test. |

**Recommendation: Option A** — lowest risk, no impact on existing features, aligns with d3kOS pattern of isolated services.

**Operator decision required before build.**

---

## 6. Range Ring Calibration Formula

For a range ring at ground distance `d` from the bow camera, with camera height `h` above waterline and vertical FOV `θ_v`:

```
pixel_y = image_height * (0.5 - arctan(h/d) / θ_v)
```

Where:
- `image_height` = camera stream height in pixels
- `arctan(h/d)` = depression angle to the target at distance d
- `θ_v` = vertical FOV of the camera in radians

User enters `h` once in a Settings field (metres or feet). All three ring positions recalculate on save. No boat-specific hardcoding — formula works for any installation meeting the minimum height standard.

**Minimum camera height standard:**

| Standard | Height | Reason |
|----------|--------|--------|
| Absolute minimum | 0.9m / 3 ft above waterline | Below this, wave interference is frequent |
| Recommended minimum | 1.2m / 4 ft above waterline | Typical bow rail — rings spread adequately |
| Ideal | 1.5m+ / 5 ft+ above waterline | Rings distribute cleanly across full frame height |

**Additional mounting requirements:**
- Forward-facing — no more than 15° downward tilt
- Clear sight line ahead (not blocked by windshield, bimini, or anchor hardware)
- Camera must support RTSP sub-stream at 640×360 or lower (all Reolink models do)

---

## 7. Open Questions — Operator Must Answer (boat visit required)

| # | Question | Why needed | Blocking? |
|---|----------|------------|-----------|
| Q1 | Exact bow camera height above waterline (tape measure: bow rail top → waterline) | Required for exact ring pixel positions | No — can ship with approximate; user sets in Settings |
| Q2 | Bow camera tilt angle — level or angled slightly downward? | Affects ring vertical distribution | No — can calibrate from Settings input |
| Q3 | Confirm horizontal FOV not obstructed by rail hardware (spec: 87°) | Affects bird's eye stitch homography | No — can adjust stitch matrix after install |

None of these questions block Phase 1 build — the Settings input for camera height makes the rings self-calibrating per installation.

---

## 8. Existing Camera Hardware (confirmed)

All four cameras confirmed installed and working S112:

| Camera | Position | Model |
|--------|----------|-------|
| Bow | Starboard bow rail top, forward-facing, bullet mount | Reolink RLC-810A |
| Helm/stern | Stern — confirms S112 | Reolink RLC-820A |
| Port | Port side | Reolink RLC-810A or 820A |
| Starboard | Starboard side | Reolink RLC-810A or 820A |

Bow camera mount detail (S147 photo):
- Position: starboard bow rail top, bullet-style mount, forward-facing
- Estimated height above waterline: ~1.2–1.5m (must be measured on next boat visit)
- Line of sight: 300m+ on open water confirmed from operator photo

---

## 9. Relationship to Other Features

| Feature | Relationship |
|---------|-------------|
| D11 360° Vision AI | Phase 2 dependency — D16 subscribes to MQTT `vessel/safety/vision_alerts`. Phase 1 builds independently. |
| WiBoat (D01) | Phase 3 dependency — WebSocket :8766 range data locks rings to measured distances. Phase 1 and 2 build independently. |
| AvNav | Not replaced — toggle keeps both available at the helm at all times. |
| Marine Vision (existing) | D16 integrates into the Marine Vision page as the top section. Existing camera grids and fish detection are unchanged below it. |

---

## 10. Build Estimate

**Phase 1 (v0.9.9.5):** ~6–10 hours

| Task | Est. |
|------|------|
| go2rtc install + YAML config for 4 cameras | 1h |
| Flask `/3d-view` route + HTML template (3-zone layout) | 1–2h |
| OpenCV homography stitch service (4 cameras → bird's eye MJPEG) | 2–3h |
| SVG range ring overlay with Settings calibration input | 1h |
| AvNav ↔ 3D toggle wired into dashboard | 0.5h |
| Testing on lab Pi | 1h |

**Phase 1 has no dependency on D11 or WiBoat and can start as soon as the go2rtc decision (§5) is made.**

---

## 11. Prior Art Reviewed

| Project | Relevance | Licence |
|---------|-----------|---------|
| Frigate NVR + go2rtc "Birdseye" | Closest open-source example. go2rtc for streaming + tiled composite. Not a true homography stitch. | MIT / Apache 2.0 |
| RPI_BEV (hichristensen) | OpenCV perspective transform on RPi — confirms Pi compute is sufficient. No browser output. | — |
| hanifizzudinrahman surround view | 4-camera OpenCV surround on RPi 3 with fisheye cameras — confirms approach works on Pi hardware. | — |
| Garmin Surround View | Only production marine multi-camera surround system. Six through-hull cameras. Closed commercial. Validates marine use case. | Commercial |
| dyfcalid/CameraCalibration | Python + OpenCV homography reference — used as design reference only. **GPL-3.0 — not included as dependency.** | GPL-3.0 ⚠ |
