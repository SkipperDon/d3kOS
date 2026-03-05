# Multi-Camera System Implementation Plan
## d3kOS Marine Vision - Multiple Camera Support

**Date:** March 1, 2026
**Status:** 📋 PLANNING
**Current State:** Single camera (Reolink RLC-810A) operational
**Target Version:** v0.9.6 or v0.10.2 (after Predictive Maintenance)
**Estimated Time:** 6-8 weeks
**Priority:** MEDIUM-HIGH (safety + security feature)

---

## EXECUTIVE SUMMARY

**What:** Expand from 1 camera to multiple cameras (up to 6) with:
- Camera switching UI (select which camera to view)
- Grid overview (see all cameras at once)
- Per-camera purposes (bow/stern/interior/engine room)
- Obstacle avoidance on bow camera (Forward Watch AI)
- Individual camera classification and detection

**Why:**
- **Safety:** Forward collision avoidance (boats, kayaks, logs, debris)
- **Docking:** Stern camera for backing up and docking assistance
- **Security:** Interior camera for passenger/crew monitoring
- **Maintenance:** Engine room camera for visual inspection
- **Comprehensive coverage:** 360° situational awareness

**Resource Impact:**
- **Bandwidth:** Manageable with sub-streams (2-4 Mbps per camera)
- **CPU:** Moderate (detection on ONE camera at a time)
- **Memory:** ~400 MB for 4 cameras (Pi 4B has 8GB - plenty)
- **Storage:** Motion-triggered recording (~10-20 GB/day for 4 cameras)

---

## PROPOSED CAMERA LAYOUT

### Typical 4-Camera Setup:
1. **Bow Camera** (Forward) - Obstacle avoidance, Forward Watch AI
2. **Stern Camera** (Aft) - Docking assistance, backing up
3. **Port Camera** (Left side) - Side collision avoidance
4. **Starboard Camera** (Right side) - Side collision avoidance

### Extended 6-Camera Setup:
5. **Interior Camera** - Cabin security, passenger monitoring
6. **Engine Room Camera** - Visual inspection, maintenance

### Camera Purposes:

| Camera | Location | Purpose | Detection |
|--------|----------|---------|-----------|
| **Bow** | Forward | Forward Watch (collision avoidance) | ✅ YOLOv8 Marine Objects |
| **Stern** | Aft | Docking, backing up | ❌ Visual only |
| **Port** | Left side | Side collision, docking | 🔶 Optional motion |
| **Starboard** | Right side | Side collision, docking | 🔶 Optional motion |
| **Interior** | Cabin | Security, passengers | 🔶 Optional motion |
| **Engine** | Engine room | Maintenance, inspection | ❌ Visual only |

---

## TECHNICAL ARCHITECTURE

### 1. Camera Registry

**File:** `/opt/d3kos/config/cameras.json`

```json
{
  "cameras": [
    {
      "id": "cam01",
      "name": "Bow Camera",
      "location": "bow",
      "purpose": "forward_watch",
      "position": {
        "x": 0,
        "y": 1,
        "z": 2,
        "heading": 0
      },
      "ip": "10.42.0.100",
      "mac": "ec:71:db:f9:7c:7c",
      "model": "Reolink RLC-810A",
      "rtsp": {
        "main": "rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_main",
        "sub": "rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub"
      },
      "resolution": {
        "main": "3840x2160",
        "sub": "1280x720"
      },
      "enabled": true,
      "detection_enabled": true,
      "detection_type": "forward_watch",
      "recording": {
        "enabled": true,
        "mode": "motion",
        "retention_days": 7
      }
    },
    {
      "id": "cam02",
      "name": "Stern Camera",
      "location": "stern",
      "purpose": "docking",
      "position": {
        "x": 0,
        "y": -1,
        "z": 1,
        "heading": 180
      },
      "ip": "10.42.0.101",
      "mac": "ec:71:db:aa:bb:cc",
      "model": "Reolink RLC-810A",
      "rtsp": {
        "main": "rtsp://admin:d3kos2026@10.42.0.101:554/h264Preview_01_main",
        "sub": "rtsp://admin:d3kos2026@10.42.0.101:554/h264Preview_01_sub"
      },
      "resolution": {
        "main": "3840x2160",
        "sub": "1280x720"
      },
      "enabled": true,
      "detection_enabled": false,
      "detection_type": null,
      "recording": {
        "enabled": true,
        "mode": "manual",
        "retention_days": 7
      }
    }
  ],
  "settings": {
    "max_cameras": 6,
    "auto_discovery": true,
    "default_stream": "sub",
    "grid_update_interval": 2000,
    "detection_simultaneous": 1
  }
}
```

### 2. Multi-Camera Stream Manager

**Extend existing:** `/opt/d3kos/services/marine-vision/camera_stream_manager.py`

**Changes:**
- Load camera registry from `cameras.json`
- Manage multiple VLC instances (one per camera)
- Per-camera API endpoints
- Automatic camera discovery (scan 10.42.0.100-109)
- Health monitoring (detect offline cameras)

**New API Endpoints:**

```python
# Existing (single camera)
GET  /camera/status
GET  /camera/frame
POST /camera/record/start
POST /camera/record/stop
GET  /camera/recordings
POST /camera/capture

# New (multi-camera)
GET  /cameras/list                  # List all cameras
GET  /cameras/{camera_id}/status    # Status of specific camera
GET  /cameras/{camera_id}/frame     # Frame from specific camera
POST /cameras/{camera_id}/record/start
POST /cameras/{camera_id}/record/stop
GET  /cameras/{camera_id}/recordings
POST /cameras/{camera_id}/capture
POST /cameras/discover              # Auto-discover cameras on network
POST /cameras/{camera_id}/enable    # Enable/disable camera
POST /cameras/{camera_id}/disable
GET  /cameras/active                # List only enabled cameras
```

**Example: Get frame from specific camera:**
```bash
curl http://192.168.1.237/cameras/cam01/frame
# Returns JPEG from bow camera
```

### 3. Detection Manager

**File:** `/opt/d3kos/services/marine-vision/detection_manager.py` (NEW)

**Purpose:** Coordinate detection across multiple cameras
- Only run detection on ONE camera at a time (resource limit)
- Priority system (bow camera = highest priority)
- Queue detection requests
- Per-camera detection types

**Detection Types:**
- `forward_watch` - Marine objects (boats, kayaks, logs, debris, buoys)
- `motion` - Simple motion detection (interior/engine room)
- `none` - No detection (visual only)

**API Endpoints:**

```python
POST /detection/start/{camera_id}   # Start detection on camera
POST /detection/stop/{camera_id}    # Stop detection on camera
GET  /detection/status/{camera_id}  # Get detection status
GET  /detection/results/{camera_id} # Get latest detection results
GET  /detection/active              # Which camera is currently detecting
```

**Resource Management:**
```python
# Only allow detection on ONE camera at a time
if detection_active:
    return {"error": "Detection already running on camera " + active_camera_id}

# Priority queue
priority = {
    "forward_watch": 1,  # Highest (bow camera)
    "motion": 2,         # Medium (interior/engine)
    "none": 3            # Lowest (never)
}
```

---

## USER INTERFACE OPTIONS

### Option A: Single View with Camera Switcher (Recommended)

**Layout:**
```
d3kOS Marine Vision
[Bow] [Stern] [Port] [Starboard] [Interior] [Engine] [Grid View]

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                  BOW CAMERA (FULL SIZE)                     │
│                      1920x1080                              │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Status: Online | Resolution: 1080p | FPS: 25 | Recording: ON
[Start Recording] [Stop Recording] [Capture Photo] [Run Detection]

Recent Recordings:
- recording_20260301_120000.mp4 (5 min, 120 MB)
- recording_20260301_115000.mp4 (3 min, 75 MB)
```

**Advantages:**
- ✅ Simple, clean interface
- ✅ Full resolution single view
- ✅ Easy camera switching
- ✅ Detection available on selected camera
- ✅ Low bandwidth (only one stream at a time)

**Disadvantages:**
- ❌ Can't see all cameras simultaneously
- ❌ Must switch to see other angles

---

### Option B: Grid View + Single View

**Grid View Page** (`/marine-vision-grid.html`):
```
d3kOS Marine Vision - Grid View
[Single View] [Grid View (active)]

┌──────────────────────────┬──────────────────────────┐
│      BOW CAMERA          │     STERN CAMERA         │
│       720p @ 1 FPS       │      720p @ 1 FPS        │
│   [Click to enlarge]     │   [Click to enlarge]     │
├──────────────────────────┼──────────────────────────┤
│    PORT CAMERA           │   STARBOARD CAMERA       │
│       720p @ 1 FPS       │      720p @ 1 FPS        │
│   [Click to enlarge]     │   [Click to enlarge]     │
└──────────────────────────┴──────────────────────────┘

Camera Status:
- Bow: Online, Detection: ON
- Stern: Online, Detection: OFF
- Port: Offline (check connection)
- Starboard: Online, Detection: OFF
```

**Advantages:**
- ✅ See all cameras at once
- ✅ Quick situational awareness
- ✅ Click to expand to full view
- ✅ Overview + detail capability

**Disadvantages:**
- ❌ Higher bandwidth (4 streams @ 720p = ~8 Mbps)
- ❌ Requires more screen space
- ❌ No detection in grid mode (too resource intensive)

---

### Option C: Picture-in-Picture (Advanced)

**Layout:**
```
d3kOS Marine Vision - PIP Mode

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                  BOW CAMERA (MAIN VIEW)                     │
│                      1920x1080                              │
│                                                             │
│  ┌────────┐  ┌────────┐  ┌────────┐                        │
│  │ Stern  │  │ Port   │  │ Stbd   │  (Small thumbnails)    │
│  │ 320x180│  │ 320x180│  │ 320x180│                        │
│  └────────┘  └────────┘  └────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

**Advantages:**
- ✅ Main view + thumbnails
- ✅ Moderate bandwidth
- ✅ Good situational awareness

**Disadvantages:**
- ❌ More complex UI
- ❌ Thumbnails may be too small on 10.1" screen
- ❌ Higher development complexity

---

### **RECOMMENDED: Hybrid Approach**

**Implement Both Option A + B:**
1. **Default:** Single View with Switcher (Option A)
2. **Secondary:** Grid View page (Option B)
3. **Toggle:** Button to switch between modes

**Navigation:**
- `[Single View]` button → marine-vision.html (current camera)
- `[Grid View]` button → marine-vision-grid.html (all cameras)
- Click camera in grid → Switch to single view of that camera

---

## RESOURCE ANALYSIS

### Bandwidth Requirements:

| Configuration | Streams | Resolution | FPS | Bandwidth |
|---------------|---------|------------|-----|-----------|
| **Single View** | 1 | 1080p | 25 | ~4 Mbps |
| **Grid View (4 cams)** | 4 | 720p | 1 | ~8 Mbps |
| **Grid View (6 cams)** | 6 | 720p | 1 | ~12 Mbps |
| **Detection Active** | +0 | N/A | N/A | No extra |

**Network:** Gigabit Ethernet (1000 Mbps) - More than sufficient
**WiFi:** 802.11ac (433 Mbps typical) - Sufficient for grid view

### CPU Load:

| Task | Load | Notes |
|------|------|-------|
| **Single stream decode** | ~5% per camera | H.264 hardware acceleration |
| **Grid 4 cams** | ~20% | 4 streams @ 1 FPS |
| **Grid 6 cams** | ~30% | 6 streams @ 1 FPS |
| **Detection (YOLOv8)** | ~50% | 2-3 seconds per inference |

**Total (worst case):** 30% (grid) + 50% (detection) = 80% CPU
**Pi 4B has 4 cores:** 80% of 1 core, plenty of headroom

### Memory Usage:

| Component | RAM per camera | Total (6 cams) |
|-----------|----------------|----------------|
| **VLC instance** | ~100 MB | ~600 MB |
| **Frame buffers** | ~20 MB | ~120 MB |
| **Detection model** | ~250 MB | ~250 MB (shared) |
| **Total** | | **~970 MB** |

**Pi 4B has 8GB RAM:** 970 MB / 8192 MB = 12% usage - No problem!

### Storage Requirements:

**Recording Modes:**
- **Continuous:** ~1 GB/hour per camera @ 1080p
  - 4 cameras × 24 hours = 96 GB/day
  - Impractical for long-term storage

- **Motion-triggered:** ~0.5-2 GB/day per camera
  - 4 cameras × 1 GB/day = 4 GB/day
  - 7-day retention = 28 GB
  - **Recommended approach**

- **Event-based (detection trigger):** ~0.1-0.5 GB/day per camera
  - Bow camera only (Forward Watch)
  - Records when objects detected
  - Minimal storage impact

**Recommendation:**
- Bow camera: Motion-triggered recording
- Other cameras: Manual recording only
- 7-day retention
- Auto-cleanup after 7 days

---

## CAMERA DISCOVERY

### Auto-Discovery Process:

**File:** `/opt/d3kos/services/marine-vision/camera_discovery.py` (UPDATE)

**Current:** Scans 10.42.0.100 only
**New:** Scans 10.42.0.100-109 (10 possible cameras)

```python
def discover_cameras(self):
    """Scan network for Reolink cameras"""
    cameras_found = []

    for i in range(100, 110):  # 10.42.0.100-109
        ip = f"10.42.0.{i}"

        # Try RTSP connection
        rtsp_url = f"rtsp://admin:d3kos2026@{ip}:554/h264Preview_01_main"
        if self.test_rtsp(rtsp_url):
            # Get camera info
            camera = {
                "ip": ip,
                "rtsp_main": rtsp_url,
                "rtsp_sub": rtsp_url.replace("_main", "_sub"),
                "online": True,
                "discovered_at": datetime.now().isoformat()
            }
            cameras_found.append(camera)

    return cameras_found
```

**DHCP Reservations:**

**File:** `/etc/NetworkManager/dnsmasq-shared.d/camera-reservation.conf`

```
# Camera DHCP reservations
dhcp-host=ec:71:db:f9:7c:7c,10.42.0.100,infinite  # Bow
dhcp-host=ec:71:db:aa:bb:cc,10.42.0.101,infinite  # Stern
dhcp-host=ec:71:db:aa:bb:dd,10.42.0.102,infinite  # Port
dhcp-host=ec:71:db:aa:bb:ee,10.42.0.103,infinite  # Starboard
dhcp-host=ec:71:db:aa:bb:ff,10.42.0.104,infinite  # Interior
dhcp-host=ec:71:db:aa:bb:00,10.42.0.105,infinite  # Engine Room
```

---

## FORWARD WATCH INTEGRATION

### Bow Camera = Forward Watch (Automatic)

**Detection Objects:**
- Boats (sailboats, motorboats, yachts)
- Kayaks and canoes
- Logs and debris
- Buoys (navigation markers)
- Docks and structures
- People in water

**Alert Levels:**
- **Critical:** Object < 50 meters, collision imminent (red alert + alarm)
- **Warning:** Object 50-100 meters, collision possible (yellow alert + voice)
- **Info:** Object > 100 meters, maintain awareness (green info)

**Integration with Dashboard:**
```
Dashboard → Forward Watch Widget
┌────────────────────────────────┐
│ Forward Watch: ACTIVE          │
│ Bow Camera: Online             │
│ Objects Detected: 2            │
│ - Kayak (75m, Warning)         │
│ - Buoy (150m, Info)            │
│ [View Camera] [View Map]       │
└────────────────────────────────┘
```

**Forward Watch runs automatically when:**
- Boat is moving (speed > 1 knot)
- Bow camera is enabled
- User hasn't manually disabled it

**See:** Forward Watch specification in Master Integration Reference

---

## IMPLEMENTATION PHASES

### Phase 1: Multi-Camera Infrastructure (2 weeks - 80 hours)

**Week 1:**
- [ ] Update `camera_stream_manager.py` for multiple cameras (16 hours)
- [ ] Create camera registry system (`cameras.json`) (8 hours)
- [ ] Implement per-camera API endpoints (12 hours)
- [ ] Update camera discovery for 10.42.0.100-109 range (4 hours)

**Week 2:**
- [ ] Create detection manager (`detection_manager.py`) (16 hours)
- [ ] Implement resource management (one detection at a time) (8 hours)
- [ ] Add camera health monitoring (8 hours)
- [ ] Testing: 2-4 cameras with multiple streams (8 hours)

**Deliverable:** Backend supports multiple cameras with detection coordination

---

### Phase 2: Single View UI with Switcher (1.5 weeks - 60 hours)

**Week 3:**
- [ ] Update `marine-vision.html` with camera switcher (12 hours)
- [ ] Add camera selection buttons/dropdown (8 hours)
- [ ] Implement JavaScript camera switching (8 hours)
- [ ] Per-camera status display (8 hours)

**Week 4 (partial):**
- [ ] Per-camera recording controls (8 hours)
- [ ] Per-camera detection controls (8 hours)
- [ ] Testing: Switch between 4-6 cameras (8 hours)

**Deliverable:** Single view page with camera switching working

---

### Phase 3: Grid View UI (1.5 weeks - 60 hours)

**Week 4 (continued):**
- [ ] Create `marine-vision-grid.html` page (12 hours)
- [ ] Implement 2x2 grid layout (8 hours)
- [ ] Implement 3x2 grid layout (6 cameras) (8 hours)

**Week 5:**
- [ ] Add grid view updates (1 FPS, sub-streams) (8 hours)
- [ ] Click-to-expand functionality (switch to single view) (8 hours)
- [ ] Camera status indicators in grid (8 hours)
- [ ] Testing: Grid view with 4-6 cameras (8 hours)

**Deliverable:** Grid view page showing all cameras, click to expand

---

### Phase 4: Forward Watch Integration (2 weeks - 80 hours)

**Week 6:**
- [ ] Integrate Forward Watch with bow camera (16 hours)
- [ ] Automatic detection on boat movement (8 hours)
- [ ] Object distance estimation (monocular depth) (16 hours)

**Week 7:**
- [ ] Alert system (critical/warning/info levels) (12 hours)
- [ ] Dashboard widget for Forward Watch status (12 hours)
- [ ] Voice alerts for collision warnings (8 hours)
- [ ] Testing: Forward Watch with real boat movement (8 hours)

**Deliverable:** Forward Watch operational on bow camera

---

### Phase 5: Settings & Management (1 week - 40 hours)

**Week 8:**
- [ ] Camera management UI in Settings (16 hours)
- [ ] Add/remove camera interface (8 hours)
- [ ] Per-camera configuration (name, location, purpose) (8 hours)
- [ ] Recording settings per camera (8 hours)

**Deliverable:** Complete camera management system

---

### Total Implementation Time:

**Development:** 320 hours = 8 weeks
- Phase 1: 80 hours (infrastructure)
- Phase 2: 60 hours (single view + switcher)
- Phase 3: 60 hours (grid view)
- Phase 4: 80 hours (Forward Watch)
- Phase 5: 40 hours (settings & management)

**Testing:** 40 hours = 1 week
**Total:** 360 hours = 9 weeks

---

## HARDWARE REQUIREMENTS

### Cameras:
- **Recommended:** Reolink RLC-810A (same as current)
- **Quantity:** 2-6 cameras
- **Cost:** ~$80-120 per camera
- **Total Cost:** $160-720 for 2-6 cameras

**Why Reolink RLC-810A:**
- ✅ IP67 waterproof (marine rated)
- ✅ 4K resolution (3840x2160)
- ✅ Night vision (IR LEDs, 30m range)
- ✅ RTSP support (standard protocol)
- ✅ Dual streams (main + sub)
- ✅ Proven working with d3kOS

### Mounting:
- **Bow:** Forward-facing, 2-3 meters above waterline
- **Stern:** Aft-facing, 1-2 meters above waterline
- **Port/Starboard:** Side-facing, 1-2 meters above waterline
- **Interior:** Ceiling mount, facing cabin
- **Engine Room:** Waterproof enclosure recommended

### Network:
- **Current:** Pi 4B eth0 shared connection (10.42.0.0/24)
- **Capacity:** 254 devices max (10.42.0.1-254)
- **Camera IPs:** 10.42.0.100-109 (10 cameras max)
- **Bandwidth:** Gigabit Ethernet (1000 Mbps) - sufficient

### Storage:
- **Current:** 16 GB SD card (97% full - tight!)
- **Recommended:** 128 GB SD card or 256 GB SSD
- **Recording:** 28 GB for 7-day retention (4 cameras, motion-triggered)
- **Models:** ~250 MB (YOLOv8 + MiDaS depth estimation)

---

## COST ESTIMATE

### Hardware:
- 2 additional cameras (bow + stern): $160-240
- 4 additional cameras (full setup): $320-480
- Camera mounts/cables: $50-100
- **Total Hardware:** $210-580

### Development:
- 320 hours × $50-150/hour = $16,000 - $48,000

### Testing:
- 40 hours × $50-150/hour = $2,000 - $6,000

### **Grand Total:** $18,210 - $54,580

---

## USER EXPERIENCE EXAMPLES

### Example 1: Forward Watch (Bow Camera)

**Scenario:** Boat cruising at 15 knots, Forward Watch enabled

**System:**
1. Bow camera streaming at 1080p @ 25 FPS
2. YOLOv8 detection running automatically (every 3 seconds)
3. Kayak detected 75 meters ahead

**Alert:**
- Dashboard: Yellow warning icon appears
- Voice: "Caution - kayak detected 75 meters ahead, port side"
- Screen: Bounding box around kayak on camera feed
- Action: Operator adjusts course to starboard

**Result:** Collision avoided, kayaker safe

---

### Example 2: Docking (Stern Camera)

**Scenario:** Backing into dock slip

**User Action:**
1. Navigate to Marine Vision
2. Click [Stern] button
3. View stern camera (full screen)

**Display:**
- Clear view of dock behind boat
- Distance markers overlay (5m, 10m, 15m)
- No AI detection (visual only)

**Result:** Smooth docking with rear visibility

---

### Example 3: Grid View Overview

**Scenario:** Operator wants 360° situational awareness

**User Action:**
1. Navigate to Marine Vision
2. Click [Grid View] button

**Display:**
```
┌────────────────┬────────────────┐
│   Bow          │   Stern        │
│   (Online)     │   (Online)     │
│   2 objects    │   Clear        │
├────────────────┼────────────────┤
│   Port         │   Starboard    │
│   (Online)     │   (Offline)    │
│   Clear        │   -            │
└────────────────┴────────────────┘
```

**Observation:**
- Bow: 2 objects detected (info level)
- Stern, Port: Clear
- Starboard: Offline (connection issue)

**Action:** Click [Bow] to investigate detected objects

**Result:** Comprehensive awareness of surroundings

---

## NEXT STEPS

### Decision Points:

1. **When to implement?**
   - Option A: v0.9.6 (before Predictive Maintenance)
   - Option B: v0.10.2 (after Predictive Maintenance) ⭐ **Recommended**
   - Option C: v0.11.x (after Diagnostic Console)

2. **How many cameras?**
   - Minimum: 2 (bow + stern) - $160-240
   - Recommended: 4 (bow + stern + port + starboard) - $320-480
   - Maximum: 6 (add interior + engine room) - $480-720

3. **Which UI approach?**
   - Option A: Single View + Switcher only (simpler, faster)
   - Option B: Single View + Grid View (recommended) ⭐
   - Option C: Picture-in-Picture (more complex)

4. **Forward Watch priority?**
   - High: Implement with multi-camera (safety critical)
   - Medium: Implement later (Phase 4 separate)

### Approval Needed:

1. **Budget:** $18K-55K (hardware + development)
2. **Timeline:** 9 weeks development + testing
3. **Hardware:** Purchase 2-6 Reolink cameras
4. **Storage:** Upgrade to 128 GB SD card or 256 GB SSD

---

## RECOMMENDATION

**Implement in v0.10.2 (after Predictive Maintenance):**
- Predictive Maintenance (v0.10.0) is higher priority
- Multi-camera is valuable but not critical
- Allows time to purchase and test additional cameras

**Start with 4-camera setup:**
- Bow (Forward Watch - automatic detection)
- Stern (Docking assistance)
- Port (Side view)
- Starboard (Side view)

**Implement Single View + Grid View (Option B):**
- Best balance of features and complexity
- Provides overview + detail capability
- Moderate resource usage

**Forward Watch integrated from start:**
- Safety-critical feature
- Automatic on bow camera
- Alert system with voice warnings

---

## RELATED DOCUMENTS

- **Master Integration Reference** - Section 4 (Microservices), Port assignments
- **MARINE_VISION.md** - Current single-camera specification
- **Version Roadmap 2026** - v0.10.2 target for multi-camera
- **Forward Watch Specification** - (referenced in Master Integration Reference)

---

**Questions?** Contact Donald Moskaluk - skipperdon@atmyboat.com

---

**© 2026 AtMyBoat.com | d3kOS Multi-Camera Marine Vision System**
