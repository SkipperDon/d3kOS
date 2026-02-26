# Forward Watch - Technical Specification
## Marine Collision Avoidance System for d3kOS

**Version:** 1.0
**Date:** 2026-02-26
**Status:** Specification Complete
**Project Type:** d3kOS Sub-Project / Signal K Plugin

---

## 1. Overview

**Forward Watch** is a camera-based collision avoidance system that detects marine hazards in real-time and displays them on chartplotters. Using AI-powered computer vision, it identifies objects in the boat's forward path, estimates their distance, calculates GPS coordinates, and transmits this data via Signal K to NMEA2000-compatible chartplotters.

### 1.1 Purpose

Provide **visual collision avoidance** capability for recreational and commercial vessels, enhancing safety by detecting hazards that traditional radar might miss (swimmers, kayakers, floating debris) and displaying them as targets on existing chartplotter displays.

### 1.2 Key Features

- **Real-time object detection:** People, boats, kayaks, buoys, logs, debris, docks, ice/icebergs
- **Distance estimation:** Monocular depth using AI (MiDaS)
- **GPS coordinate mapping:** Converts camera detections to chartplotter overlays
- **Signal K integration:** Outputs via standard marine protocols
- **NMEA2000 compatibility:** Works with all major chartplotter brands
- **Open source:** Signal K plugin, community-driven development

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FORWARD WATCH SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────────────────────┐    │
│  │   Camera     │──────│  Object Detection (YOLOv8)   │    │
│  │  (RTSP/HTTP) │      │  - People, boats, buoys      │    │
│  └──────────────┘      │  - Kayaks, debris, docks     │    │
│                        └──────────────┬───────────────┘    │
│                                       │                     │
│                        ┌──────────────▼───────────────┐    │
│                        │  Depth Estimation (MiDaS)    │    │
│                        │  - Monocular depth inference │    │
│                        │  - Distance in meters        │    │
│                        └──────────────┬───────────────┘    │
│                                       │                     │
│  ┌──────────────┐      ┌──────────────▼───────────────┐    │
│  │  Signal K    │◄─────│  GPS Coordinate Calculator   │    │
│  │  (Heading,   │      │  - Bearing from camera FOV   │    │
│  │   Position)  │      │  - Destination point (lat/lon)│   │
│  └──────┬───────┘      └──────────────────────────────┘    │
│         │                                                    │
│         │              ┌──────────────────────────────┐    │
│         └──────────────►  Signal K Output            │    │
│                        │  - Delta messages            │    │
│                        │  - NMEA2000 PGN conversion   │    │
│                        └──────────────┬───────────────┘    │
│                                       │                     │
│                        ┌──────────────▼───────────────┐    │
│                        │     Chartplotter Display      │    │
│                        │  - AIS-like target overlay   │    │
│                        │  - Distance and bearing      │    │
│                        └──────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Input:** Camera RTSP/HTTP stream (10 FPS)
2. **Detection:** YOLOv8 identifies objects (people, boats, etc.)
3. **Depth:** MiDaS estimates distance to each object
4. **Bearing:** Calculate angle from camera field of view + object position in frame
5. **Position:** Get boat GPS and heading from Signal K
6. **Calculation:** Compute object GPS coordinates using geodesy math
7. **Output:** Send Signal K delta messages (vessels.urn:mrn:signalk:uuid:xxx)
8. **Conversion:** Signal K converts to NMEA2000 PGN 129038 (AIS-like target)
9. **Display:** Chartplotter shows targets on navigation chart

---

## 3. Object Detection

### 3.1 Detected Object Classes

| Class | Description | Priority | Typical Use Case |
|-------|-------------|----------|------------------|
| **People** | Swimmers, man overboard, people on paddleboards | Critical | Safety, rescue |
| **Boats** | Vessels, ships, sailboats, motorboats | High | Collision avoidance |
| **Kayaks** | Kayaks, canoes, small watercraft | High | Collision avoidance |
| **Buoys** | Navigation markers, mooring buoys | Medium | Navigation aid |
| **Logs** | Large floating logs, timber | High | Collision avoidance |
| **Debris** | Floating trash, containers, wreckage | Medium | Hazard awareness |
| **Docks** | Piers, marinas, fixed structures | Medium | Navigation aid |
| **Ice/Icebergs** | Floating ice, icebergs, sea ice, growlers, bergy bits | Critical | Collision avoidance (Arctic/northern waters) |

**⚠️ CRITICAL NOTE ON ICE DETECTION:**

Ice and icebergs are **highly variable** - no two are the same. The AI model must learn **general ice characteristics** rather than specific shapes:

- **Color variations:** White, blue-white, translucent, with dirt/debris
- **Shape variations:** Irregular, angular, rounded, tabular, pinnacled
- **Size range:** Small growlers (< 5m) to large icebergs (> 75m)
- **Surface conditions:** Smooth, jagged, melted, fractured
- **Water level:** Partially submerged (only 10-20% visible above water)
- **Lighting conditions:** Bright sun, overcast, fog, low light

**Training Strategy:** Use diverse ice imagery from multiple regions, seasons, and conditions. Focus on training the model to recognize **"ice-like"** characteristics (color, texture, context) rather than memorizing specific iceberg shapes.

### 3.2 AI Model: YOLOv8-Marine

**Base Model:** YOLOv8n (Nano) - 6MB
**Custom Training:** Required for marine-specific objects
**Format:** ONNX (for ONNX Runtime on Raspberry Pi)
**Input Size:** 640×640 pixels
**Output:** Bounding boxes with class labels and confidence scores
**Performance:** 10+ FPS on Raspberry Pi 4B

### 3.3 Training Requirements

**Dataset Needed:**
- **People in water:** 1,000+ images (swimmers, man overboard scenarios)
- **Boats:** 5,000+ images (various vessel types, sizes, angles)
- **Kayaks:** 1,000+ images (kayaks, canoes, paddleboards)
- **Buoys:** 500+ images (navigation markers, different colors)
- **Floating debris:** 1,000+ images (logs, containers, trash)
- **Docks:** 500+ images (piers, marinas)
- **Ice/Icebergs:** 2,000+ images (**CRITICAL:** Maximum diversity - Arctic, Antarctic, Greenland, Alaska; various sizes, colors, shapes, lighting conditions)

**Available Datasets:**
- [SeaShips Dataset](https://github.com/jiaming-wang/SeaShips) - 31,455 ship images, 6 vessel types
- [Marine Surveillance Dataset (Roboflow)](https://universe.roboflow.com/marine-cv6x4/seaships-zhqhn) - Pre-annotated vessels
- [Floating Debris Dataset](https://www.nature.com/articles/s41597-025-04594-9) - 3,000 inland water floater images
- [SeaDronesSee Dataset](https://www.nature.com/articles/s41598-024-75807-1) - UAV maritime rescue objects
- [YOLO-MRS Dataset](https://www.sciencedirect.com/science/article/abs/pii/S0141118724003614) - 9,000+ maritime objects, 13 classes
- [Statoil Iceberg Classifier (Kaggle)](https://www.kaggle.com/c/statoil-iceberg-classifier-challenge) - 1,604 SAR images (radar - supplemental)
- [Roboflow Universe Iceberg Datasets](https://universe.roboflow.com/search?q=class:iceberg) - Optical iceberg images (YOLOv8 format)
- [Sentinel-2 Iceberg Dataset](https://www.mdpi.com/2072-4292/12/15/2353) - 350 ships/icebergs, Greenland waters, multispectral imagery

**Training Process:**
1. Combine multiple datasets (SeaShips + custom captures)
2. Annotate 8 classes (people, boats, kayaks, buoys, logs, debris, docks, ice/icebergs)
3. Train YOLOv8n for 50-100 epochs (~12-16 hours on RTX 3060 Ti)
4. Export to ONNX format
5. Validate on test set (target: >85% mAP@0.5)

---

## 4. Distance Estimation

### 4.1 AI Model: MiDaS v3.0

**Purpose:** Monocular depth estimation (single camera distance measurement)
**Model:** MiDaS v3.0 (Intel) - Pre-trained, no custom training needed
**Format:** ONNX
**Input Size:** 384×384 pixels
**Output:** Depth map (relative depth values)
**Performance:** 5+ FPS on Raspberry Pi 4B

### 4.2 Depth Calibration

**Calibration Parameters:**
- Camera height above waterline (meters)
- Camera tilt angle (degrees from horizon)
- Focal length (from camera specs)
- Field of view (horizontal, degrees)

**Conversion to Absolute Distance:**
```
distance_meters = (camera_height / tan(pixel_angle + tilt_angle)) * depth_scale_factor
```

**Accuracy:**
- **10-50m range:** ±20% error
- **50-100m range:** ±40% error
- **>100m range:** ±60% error (unreliable)

**Validation:** Compare against known reference objects (buoys at known distances)

---

## 5. GPS Coordinate Calculation

### 5.1 Required Inputs

From **Signal K:**
- `navigation.position` → Boat GPS (latitude, longitude)
- `navigation.headingTrue` → Boat heading (degrees true north)

From **Camera Detection:**
- Object position in frame (X, Y pixel coordinates)
- Estimated distance to object (meters)

### 5.2 Bearing Calculation

```javascript
// Camera field of view (FOV)
const cameraFOV = 107; // degrees (Reolink RLC-810A)

// Object position in frame (normalized -0.5 to +0.5)
const objectX = (pixelX - frameWidth/2) / frameWidth;

// Relative bearing from camera center
const relativeBearing = objectX * cameraFOV;

// Absolute bearing (true north)
const boatHeading = signalk.navigation.headingTrue;
const absoluteBearing = (boatHeading + relativeBearing + 360) % 360;
```

### 5.3 Destination Point Calculation

Uses **Geodesy library** (Haversine formula):

```javascript
const LatLon = require('geodesy/latlon-spherical.js');

function calculateObjectGPS(boatLat, boatLon, bearing, distance) {
  const boatPos = new LatLon(boatLat, boatLon);
  const objectPos = boatPos.destinationPoint(distance, bearing);

  return {
    latitude: objectPos.lat,
    longitude: objectPos.lon
  };
}
```

**Formula:**
```
lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(θ))
lon2 = lon1 + atan2(sin(θ) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))

Where:
  lat1, lon1 = boat position
  θ = bearing (radians)
  d = distance (meters)
  R = Earth radius (6,371,000 meters)
```

---

## 6. Signal K Integration

### 6.1 Plugin Structure

**Plugin Name:** `signalk-forward-watch`

**Package.json:**
```json
{
  "name": "signalk-forward-watch",
  "version": "1.0.0",
  "description": "Camera-based collision avoidance system - detects marine hazards and displays on chartplotters",
  "main": "index.js",
  "keywords": [
    "signalk-node-server-plugin",
    "signalk-category-safety",
    "signalk-category-navigation"
  ],
  "author": "d3kOS Team",
  "license": "Apache-2.0",
  "repository": {
    "type": "git",
    "url": "https://github.com/d3kOS/signalk-forward-watch"
  }
}
```

### 6.2 Delta Message Format

```json
{
  "context": "vessels.urn:mrn:signalk:uuid:forward-watch-001",
  "updates": [
    {
      "source": {
        "label": "forward-watch-camera",
        "type": "camera",
        "src": "forward-watch-plugin"
      },
      "timestamp": "2026-02-26T14:35:22.789Z",
      "values": [
        {
          "path": "navigation.position",
          "value": {
            "latitude": 44.4175,
            "longitude": -79.3342
          }
        },
        {
          "path": "sensors.camera.objectType",
          "value": "person"
        },
        {
          "path": "sensors.camera.distance",
          "value": 42.5
        },
        {
          "path": "sensors.camera.bearing",
          "value": 315
        },
        {
          "path": "sensors.camera.confidence",
          "value": 0.89
        },
        {
          "path": "navigation.courseOverGroundTrue",
          "value": null
        },
        {
          "path": "navigation.speedOverGround",
          "value": 0
        }
      ]
    }
  ]
}
```

### 6.3 NMEA2000 PGN Conversion

**Option A: AIS-like Targets (Recommended)**

**PGN 129038** - AIS Class A Position Report

```
PGN: 129038
Priority: 4
Length: 27 bytes
Fields:
  - Message ID: 1 (Position Report)
  - Repeat Indicator: 0
  - User ID: Generated UUID (camera-detection-XXX)
  - Longitude: Calculated object position
  - Latitude: Calculated object position
  - Position Accuracy: Low (monocular depth)
  - COG: 0 (stationary objects)
  - SOG: 0
  - Name: "FWD-PERSON-001" (type + ID)
```

**Option B: Waypoint/Mark**

**PGN 129285** - Route/WP Information

```
PGN: 129285
Fields:
  - Start RPS#: 0
  - nItems: 1
  - Database ID: 1
  - Route ID: Forward Watch detections
  - WP ID: Object UUID
  - WP Name: "HAZARD-PERSON-42m"
  - WP Latitude: Calculated
  - WP Longitude: Calculated
```

---

## 7. Chartplotter Display

### 7.1 Compatible Chartplotters

| Brand | Model Examples | AIS Support | Signal K Support | Status |
|-------|----------------|-------------|------------------|--------|
| **Garmin** | GPSMAP 8600, Echomap Ultra | Yes | No | Via NMEA2000 |
| **Raymarine** | Axiom+, Element | Yes | Partial | Via NMEA2000 |
| **Simrad** | NSS evo3, GO Series | Yes | No | Via NMEA2000 |
| **Lowrance** | HDS Live, Elite FS | Yes | No | Via NMEA2000 |
| **Furuno** | NavNet TZtouch3, GP Series | Yes | No | Via NMEA2000 |
| **OpenCPN** | All versions | Yes | **Full** | Native Signal K ✅ |
| **Navionics** | Boating App | No | No | Not compatible |

### 7.2 Display Characteristics

**Target Icons:**
- **People:** Red ⚠️ triangle with "PERSON" label
- **Boats:** Blue ⛵ with vessel name
- **Kayaks:** Green 🛶 with "KAYAK" label
- **Buoys:** Yellow ⚫ with buoy ID
- **Debris:** Orange ⚠️ with "HAZARD" label
- **Docks:** Gray ▬ with "DOCK" label

**Information Displayed:**
- Distance (meters or nautical miles)
- Bearing (degrees true)
- Time since detection
- Confidence score (if chartplotter supports)

**Update Rate:**
- Detection: 10 FPS (camera)
- Signal K: 1-2 Hz (updates per second)
- Chartplotter refresh: 1-5 seconds (varies by model)

---

## 8. Performance Requirements

### 8.1 Hardware Specifications

**Minimum:**
- Raspberry Pi 4B (4GB RAM)
- Camera: 1080p, RTSP/HTTP stream
- Network: 100 Mbps Ethernet

**Recommended:**
- Raspberry Pi 4B (8GB RAM) or Pi 5
- Camera: 4K, night vision, IP67 rated (Reolink RLC-810A)
- Network: Gigabit Ethernet

### 8.2 Performance Targets

| Metric | Target | Acceptable | Notes |
|--------|--------|------------|-------|
| Object Detection FPS | 10+ | 5+ | YOLOv8n inference |
| Depth Estimation FPS | 5+ | 3+ | MiDaS inference |
| Detection Latency | <200ms | <500ms | Camera → Signal K |
| GPS Accuracy | ±10m | ±30m | Combined error |
| Distance Accuracy (10-50m) | ±20% | ±40% | Monocular depth |
| Update Rate to Chartplotter | 1-2 Hz | 0.5 Hz | NMEA2000 |
| CPU Usage | <60% | <80% | Sustained load |
| Memory Usage | <2GB | <3GB | Running services |

### 8.3 Scalability

**Single Camera:** 10 FPS, 5-10 objects tracked
**Multiple Cameras:** Reduce FPS per camera (e.g., 3 cameras @ 3 FPS each)
**Processing Optimization:** Use hardware acceleration if available (Coral TPU, Intel NCS2)

---

## 9. Configuration

### 9.1 Plugin Settings (Web UI)

**Camera Configuration:**
- Camera URL (RTSP/HTTP)
- Resolution (1080p/4K)
- FPS limit (1-30)
- Enable/disable

**Detection Settings:**
- Object classes to detect (checkboxes for 8 classes)
- Confidence threshold (0.1-0.9, default: 0.5)
- Minimum object size (pixels)
- Maximum detection range (meters)

**Calibration:**
- Camera height above waterline (meters)
- Camera tilt angle (degrees)
- Field of view (degrees, auto-detect if possible)
- Depth scale factor (calibration multiplier)

**Output Settings:**
- Signal K update rate (0.5-5 Hz)
- NMEA2000 PGN format (AIS-like or Waypoint)
- Target naming convention
- Enable/disable specific chartplotters

**Alert Settings:**
- Audible alerts (enable/disable)
- Alert distance threshold (meters)
- Alert types (person, boat, debris, etc.)

### 9.2 Example Configuration File

```json
{
  "enabled": true,
  "camera": {
    "url": "rtsp://admin:password@10.42.0.100:554/h264Preview_01_main",
    "resolution": "1920x1080",
    "fps": 10
  },
  "detection": {
    "classes": {
      "people": true,
      "boats": true,
      "kayaks": true,
      "buoys": true,
      "logs": true,
      "debris": true,
      "docks": false
    },
    "confidenceThreshold": 0.5,
    "minObjectSize": 50,
    "maxRange": 200
  },
  "calibration": {
    "cameraHeight": 2.5,
    "cameraTilt": -5,
    "fieldOfView": 107,
    "depthScaleFactor": 1.0
  },
  "output": {
    "updateRate": 1.0,
    "pgnFormat": "ais",
    "targetPrefix": "FWD-"
  },
  "alerts": {
    "audible": true,
    "distanceThreshold": 50,
    "alertClasses": ["people", "boats"]
  }
}
```

---

## 10. Installation

### 10.1 Prerequisites

- Signal K server installed (Node.js 18+)
- Camera accessible via RTSP or HTTP
- NMEA2000 network (if using chartplotter integration)

### 10.2 Install via Signal K AppStore

1. Open Signal K server web interface (http://localhost:3000)
2. Navigate to **Appstore** → **Available**
3. Search for "forward-watch"
4. Click **Install**
5. Restart Signal K server
6. Configure plugin in **Server** → **Plugin Config** → **Forward Watch**

### 10.3 Install via npm

```bash
cd ~/.signalk
npm install signalk-forward-watch
sudo systemctl restart signalk
```

### 10.4 Manual Installation (Development)

```bash
git clone https://github.com/d3kOS/signalk-forward-watch.git
cd signalk-forward-watch
npm install
npm link
cd ~/.signalk
npm link signalk-forward-watch
sudo systemctl restart signalk
```

---

## 11. Testing & Validation

### 11.1 Test Procedure

**Phase 1: Camera Connection**
1. Verify camera stream accessible (VLC test)
2. Check frame rate and resolution
3. Confirm network latency <50ms

**Phase 2: Object Detection**
1. Place test objects at known distances (5m, 10m, 25m, 50m)
2. Verify detection accuracy (>80% confidence)
3. Measure false positive rate (<10%)
4. Test in various lighting conditions

**Phase 3: Distance Estimation**
1. Compare estimated distance vs actual measured distance
2. Calculate error percentage
3. Adjust depth scale factor if needed
4. Validate at multiple ranges (10m, 25m, 50m, 100m)

**Phase 4: GPS Mapping**
1. Place known object at measured GPS coordinates
2. Run Forward Watch detection
3. Compare calculated GPS vs actual GPS
4. Verify error <30m

**Phase 5: Signal K Output**
1. Monitor Signal K delta messages
2. Verify data format correct
3. Check update rate matches configuration

**Phase 6: Chartplotter Display**
1. Verify targets appear on chartplotter
2. Check icon types and labels
3. Confirm distance and bearing accurate
4. Test with moving boat (heading changes)

### 11.2 Validation Scenarios

**Scenario 1: Man Overboard**
- Deploy mannequin or test object in water
- Verify detection within 10 seconds
- Confirm GPS coordinates accurate
- Check chartplotter displays alert

**Scenario 2: Approaching Vessel**
- Approach another boat at 5 knots
- Verify continuous tracking
- Confirm distance updates correctly
- Check collision warning if <50m

**Scenario 3: Floating Debris**
- Navigate near floating logs or debris
- Verify detection at 50-100m range
- Confirm debris classification
- Check hazard icon on chartplotter

**Scenario 4: Night Operation**
- Test with camera night vision mode
- Verify detection in low light
- Check IR illumination range
- Confirm no false positives from reflections

---

## 12. Troubleshooting

### 12.1 Common Issues

**Issue: No objects detected**
- Check camera URL and credentials
- Verify camera stream is active (test with VLC)
- Lower confidence threshold in settings
- Ensure objects within camera field of view

**Issue: Inaccurate distance estimates**
- Calibrate camera height and tilt angle
- Adjust depth scale factor
- Verify camera mounted correctly (level, forward-facing)
- Test against known reference distances

**Issue: GPS coordinates incorrect**
- Check Signal K heading data (navigation.headingTrue)
- Verify boat GPS is accurate
- Confirm camera field of view setting correct
- Recalibrate bearing offset if needed

**Issue: No chartplotter display**
- Verify NMEA2000 network connected
- Check Signal K NMEA2000 plugin enabled
- Confirm chartplotter supports AIS targets
- Try waypoint PGN format instead

**Issue: Low performance (FPS drops)**
- Reduce camera resolution (4K → 1080p)
- Lower detection FPS in settings
- Disable unused object classes
- Consider hardware acceleration (Coral TPU)

### 12.2 Debug Mode

Enable debug logging in Signal K plugin settings:

```json
{
  "debug": {
    "enabled": true,
    "logLevel": "verbose",
    "saveFrames": true,
    "frameInterval": 10
  }
}
```

Debug output location: `~/.signalk/logs/forward-watch-debug.log`

---

## 13. Future Enhancements

### 13.1 Planned Features (v2.0)

- **Object tracking:** Persistent IDs for moving objects
- **Collision prediction:** ETA to intercept
- **Multi-camera support:** Panoramic 360° coverage
- **Object classification:** Vessel type identification
- **Wake detection:** Detect wakes to identify hidden boats
- **Integration with AIS:** Merge camera targets with AIS data
- **Replay mode:** Record and playback detection sessions

### 13.2 Hardware Acceleration

- **Coral TPU:** 10× faster inference (30+ FPS possible)
- **Intel NCS2:** 5× faster inference
- **NVIDIA Jetson:** GPU acceleration for depth + detection

### 13.3 Advanced Calibration

- **Automatic calibration:** Use known reference objects (buoys)
- **Stereo camera support:** Accurate depth without AI estimation
- **LiDAR integration:** Precise distance measurement
- **IMU integration:** Compensate for boat pitch/roll

---

## 14. References

### 14.1 Research Papers

- [Marine Vessel Tracking using Monocular Camera (2021)](https://www.scitepress.org/PublishedPapers/2021/105160/105160.pdf)
- [Distance Estimation for Maritime Traffic (2024)](https://www.mdpi.com/2077-1312/12/1/78)
- [YOLOv8 Maritime Object Detection (2024)](https://www.nature.com/articles/s41598-024-75807-1)

### 14.2 Datasets

- [SeaShips Dataset](https://github.com/jiaming-wang/SeaShips) - 31,455 ship images
- [Floating Debris Dataset](https://www.nature.com/articles/s41597-025-04594-9) - 3,000 images
- [Marine Surveillance (Roboflow)](https://universe.roboflow.com/marine-cv6x4/seaships-zhqhn)

### 14.3 Libraries

- [Geodesy.js](https://www.npmjs.com/package/geodesy) - GPS coordinate calculations
- [ONNX Runtime](https://onnxruntime.ai/) - AI model inference
- [Signal K Node Server](https://github.com/SignalK/signalk-server)

### 14.4 Standards

- [NMEA2000 Standard](https://www.nmea.org/nmea-2000.html)
- [Signal K Specification](https://signalk.org/specification/)
- [PGN 129038 - AIS Position Report](https://www.nmea.org/Assets/20190613%20nmea%202000%20pgn%20field%20list%202019%20v2.pdf)

---

## 15. License & Support

**License:** Apache 2.0 (Open Source)

**Repository:** https://github.com/d3kOS/signalk-forward-watch

**Issues:** https://github.com/d3kOS/signalk-forward-watch/issues

**Documentation:** https://d3kos.org/forward-watch

**Community:** Signal K Slack #forward-watch channel

---

**Document Version:** 1.0
**Last Updated:** 2026-02-26
**Authors:** d3kOS Development Team
