# Marine Vision — Live IP Camera System (Bow + Stern)

> **SUPERSEDED — 2026-03-11**
> This document describes the original `cameras.json` two-camera system.
> It has been replaced by the Slot/Hardware architecture.
> **Active documentation:** `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md`
> **Active source:** `deployment/features/camera-overhaul/pi_source/`
> This file is retained as read-only history.

**Version:** v0.9.2 | **Date:** 2026-03-06 | **Status:** SUPERSEDED 2026-03-11
**Commits:** `be236c5`, `9478f1d`, `9e53dfa`, `dbff06e`
**Source:** `deployment/v0.9.2-multicam/` (superseded — read-only)

---

## What This Is

Live video feeds from two IP cameras mounted on the boat displayed in the d3kOS Marine Vision page. The system supports camera switching, side-by-side grid view, camera position labels (bow/stern/port/starboard), and fish species detection using YOLOv8n (483 species).

The cameras are on the boat's hotspot network (10.42.0.x). When not on the boat, the system shows a graceful "Camera offline — not on boat network" message instead of an error.

---

## Hardware

| Camera | Model | IP | Position | RTSP |
|--------|-------|----|----------|------|
| Camera 1 | Reolink (generic) | 10.42.0.100 | Bow | working |
| Camera 2 | Reolink RLC-820A | 10.42.0.63 | Stern | working |
| Camera 3 & 4 | RLC-820A (planned) | TBD | TBD | — |

RTSP credential for RLC-820A: `d3kos2026$` (stored percent-encoded in cameras.json)

---

## Architecture

```
IP Cameras (RTSP) → camera_stream_manager.py (port 8084) → marine-vision.html
                                                          → settings.html (camera cards)
                                                          → fish detector (YOLOv8n)
```

---

## Key Files on Pi

| File | Path |
|------|------|
| Camera config | `/opt/d3kos/config/cameras.json` |
| Stream manager | `/opt/d3kos/services/marine-vision/camera_stream_manager.py` |
| Marine Vision UI | `/var/www/html/marine-vision.html` |
| DHCP setup script | `/home/d3kos/setup_dhcp_reservations.py` |

---

## API Endpoints (Port 8084)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/camera/list` | All cameras + status + position |
| POST | `/camera/switch/<id>` | Switch active camera |
| GET | `/camera/grid` | Side-by-side JPEG of all cameras |
| GET | `/camera/frame/<id>` | Single frame from specific camera |
| GET | `/camera/status` | Active camera status (backwards compat) |
| GET | `/camera/frame` | Active camera frame (backwards compat) |

---

## cameras.json Schema

```json
[
  {
    "id": "bow",
    "name": "Bow Camera",
    "location": "bow",
    "position": "bow",
    "ip": "10.42.0.100",
    "rtsp_url": "rtsp://admin:password@10.42.0.100:554/...",
    "model": "Reolink",
    "detection_enabled": true
  }
]
```

---

## Adding Camera 3 or 4

When purchased:
1. Add camera entry to `/opt/d3kos/config/cameras.json` on the Pi
2. No code changes needed — the API and UI are dynamic
3. Run DHCP reservation script (on-boat task — see below)

---

## On-Boat Tasks

Tasks that require physical presence on the boat with cameras connected to the hotspot:

**DHCP Reservations** — run once per camera added:
```
In Windows Explorer: \\wsl.localhost\Ubuntu\home\boatiq\Helm-OS\...
```
Don opens the Pi via browser → Settings → System → run the DHCP script.

The script `setup_dhcp_reservations.py` reads MAC addresses from the dnsmasq lease file and writes static reservations to `dnsmasq.conf`, then restarts dnsmasq. This ensures cameras always get the same IP after reboot.

**Stability test:** Run both cameras for 24 hours continuous. Monitor CPU (target <35%), memory (target <970MB total), bandwidth (grid <12Mbps, single <4Mbps).

---

## Fish Detector

- Model: YOLOv8n (forward-watch ONNX, 12MB)
- Species: 483 marine fish species
- Runs as separate process consuming frames from camera_stream_manager
- Restarted 2026-03-06 after dependency failure (was down since camera stream error Feb 28)
