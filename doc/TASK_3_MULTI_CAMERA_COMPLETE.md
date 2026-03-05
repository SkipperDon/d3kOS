# Task 3: Multi-Camera System - COMPLETE Implementation

**Executor:** Ollama
**Timeline:** 8-9 weeks (320-360 hours)
**Status:** Ready to execute after Task 1 & 2

## Week 1: Camera Registry (40 hours)

### Files
- `/opt/d3kos/config/cameras.json` - 4 camera configs
- `/etc/NetworkManager/dnsmasq-shared.d/camera-reservations.conf` - DHCP
- Camera auto-discovery script

### DHCP Reservations
- 10.42.0.100 - Bow (Forward Watch)
- 10.42.0.101 - Stern
- 10.42.0.102 - Interior
- 10.42.0.103 - Port/Starboard

## Week 2-3: Backend API (80 hours)

Extend `/opt/d3kos/services/marine-vision/camera_stream_manager.py`:
- `/camera/list` - All cameras
- `/camera/status/{id}` - Per-camera status
- `/camera/switch/{id}` - Switch active
- `/camera/grid` - All frames (2×2 grid)
- `/camera/frame/{id}` - Specific camera

Resource optimization:
- Grid: 720p @ 1 FPS (sub-stream)
- Single: 1080p @ 25 FPS (main stream)

## Week 4-5: UI (80 hours)

### Single View
File: `/var/www/html/marine-vision.html` (update)
- Camera dropdown (4 cameras)
- 1080p @ 25 FPS
- Grid View button

### Grid View
File: `/var/www/html/marine-vision-grid.html` (new)
- 2×2 grid
- 720p @ 1 FPS all cameras
- Click to jump to Single View

## Week 6-7: Forward Watch (80 hours)

- Bow camera: detection_enabled=true
- YOLOv8 marine model (from Task 1)
- Detection overlay (bounding boxes)
- Visual + audio alerts
- Priority queue (bow first)

## Week 8: Testing (40 hours)

- CPU < 35%
- Memory < 970 MB
- Bandwidth: Grid < 12 Mbps, Single < 4 Mbps
- 24-hour continuous test
- Motion-triggered recording
- 7-day retention, auto-cleanup

## Week 9: Deployment (40 hours)

### Hardware
- Purchase 3 Reolink RLC-810A ($800-1,200)
- Mount: Stern, Interior, Port/Starboard
- Configure: Static IP, admin password

### Git Commit
```bash
git add opt/d3kos/config/cameras.json
git add opt/d3kos/services/marine-vision/
git add var/www/html/marine-vision*.html
git commit -m "feat(v0.9.3): 4-camera system with Forward Watch

- Camera registry with auto-discovery
- Multi-camera backend API (6 endpoints)
- Single View + Grid View UI
- Forward Watch: Bow camera obstacle detection
- Resource optimized: <35% CPU, <970 MB RAM
- Hybrid streams: 1080p single, 720p grid
- Tested 24 hours continuous, verified all cameras"

git tag v0.9.3
```

## Acceptance Criteria
- ✅ 4 cameras registered
- ✅ Grid + Single views working
- ✅ Forward Watch detecting obstacles
- ✅ Performance within targets
- ✅ Hardware installed
- ✅ Git committed, tagged v0.9.3
- ✅ Nothing hanging
