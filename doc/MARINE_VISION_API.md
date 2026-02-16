# Marine Vision System - API Documentation

**Version:** 2.1 (Phase 2.1 Complete)
**Last Updated:** February 16, 2026
**System:** d3kOS Marine Helm Control System
**Camera:** Reolink RLC-810A @ 10.42.0.100

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Camera Stream API](#camera-stream-api)
4. [Fish Detection API](#fish-detection-api)
5. [Captures API](#captures-api)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)
8. [Code Examples](#code-examples)
9. [WebSocket Streaming](#websocket-streaming)
10. [Performance Considerations](#performance-considerations)

---

## Overview

### What is the Marine Vision System?

The Marine Vision System provides AI-powered computer vision capabilities for recreational boating through a RESTful API architecture. The system consists of microservices that handle:

- **Camera streaming** from Reolink RLC-810A (4K/1080p)
- **Object detection** using YOLOv8 ONNX models
- **Photo/video capture** with automatic triggers
- **Fish identification** (Phase 2.1 complete)
- **Forward obstacle detection** (Phase 4 - planned)

### Base URLs

All API endpoints are accessible via nginx proxy:

```
Base URL: http://192.168.1.237
Camera Stream API: http://192.168.1.237/camera/
Fish Detection API: http://192.168.1.237/detect/
Captures API: http://192.168.1.237/captures
Web UI: http://192.168.1.237/marine-vision.html
```

### Current Status

**Phase 1 (Complete):** ✅ Camera Streaming
- RTSP connection management
- Frame grabbing (30 FPS background thread)
- Video recording (VLC)
- Photo capture (high-resolution JPEG)
- Web UI with live preview

**Phase 2.1 (Complete):** ✅ AI Model Setup & Fish Detection
- YOLOv8n ONNX model (13MB)
- Person detection (COCO class 0)
- Fish detection proxy (COCO class 14 "bird")
- Auto-capture on person+fish detection
- SQLite database logging
- Detection API endpoints

**Phase 2.2+ (Planned):** 🚧 Custom Fish Model, Species ID, Regulations

---

## Architecture

### Microservices Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (Port 80)                      │
│  Routes: /camera/ → 8084, /detect/ → 8086, /captures → 8086 │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Camera Stream │  │ Fish Detector │  │ (Future)      │
│  Port 8084    │  │  Port 8086    │  │ Forward Watch │
│               │  │               │  │  Port 8087    │
│ - RTSP Client │  │ - YOLOv8 ONNX │  │ - Marine Obj  │
│ - Frame Grab  │  │ - Detection   │  │ - Depth Est.  │
│ - Recording   │  │ - Capture     │  │ - Alerts      │
│ - HTTP API    │  │ - Database    │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │
        ▼                  ▼
┌───────────────┐  ┌───────────────┐
│ Reolink Camera│  │ SQLite DB     │
│ 10.42.0.100   │  │ captures.db   │
│ RTSP Stream   │  │               │
└───────────────┘  └───────────────┘
```

### Service Dependencies

```
d3kos-camera-stream.service (Port 8084)
  ├─ Requires: network-online.target
  ├─ Camera: Reolink @ 10.42.0.100:554
  └─ Provides: Frame API for other services

d3kos-fish-detector.service (Port 8086)
  ├─ Requires: d3kos-camera-stream.service
  ├─ Depends on: Camera Stream API
  └─ Provides: Detection & Captures API
```

### Data Flow

**Frame Capture:**
```
Reolink Camera → RTSP → Camera Stream Service → Background Thread (30 FPS)
                                                        │
                                                        ▼
                                         Latest Frame Buffer (in-memory)
                                                        │
                ┌───────────────────────────────────────┴──────────────┐
                ▼                                                      ▼
        GET /camera/frame                                    Fish Detector Service
        Returns JPEG                                         Fetches frame for AI
```

**Detection Flow:**
```
User → POST /detect/frame → Fish Detector → Fetches frame → YOLOv8 Inference
                                                                    │
                                                                    ▼
                                                            Detections (JSON)
                                                                    │
                                    ┌───────────────────────────────┴────────────┐
                                    ▼                                            ▼
                            Person + Fish?                                 Return Results
                                YES │                                              │
                                    ▼                                              │
                          Capture Photo → Save to DB → Return capture_id          │
                                                                    └──────────────┘
```

---

## Camera Stream API

### Service: `d3kos-camera-stream`
**Port:** 8084 (internal), proxied via `/camera/` (external)
**File:** `/opt/d3kos/services/marine-vision/camera_stream_manager.py`

### Endpoints

#### GET /camera/status

Get camera connection status and stream information.

**Request:**
```http
GET /camera/status HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "connected": true,
  "camera_ip": "10.42.0.100",
  "resolution": "4K (3840x2160)",
  "fps": 25,
  "recording": false,
  "frame_count": 45231,
  "uptime_seconds": 1507.7,
  "last_frame_time": "2026-02-16T14:32:15.123456"
}
```

**Status Codes:**
- `200 OK` - Camera connected and operational
- `503 Service Unavailable` - Camera disconnected or unreachable

---

#### GET /camera/frame

Fetch the latest frame from camera as JPEG image.

**Request:**
```http
GET /camera/frame HTTP/1.1
Host: 192.168.1.237
Accept: image/jpeg
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Length: 552341

[Binary JPEG data]
```

**Response Headers:**
- `Content-Type: image/jpeg`
- `Content-Length: [size in bytes]`

**Status Codes:**
- `200 OK` - Frame retrieved successfully
- `503 Service Unavailable` - No frame available (camera disconnected)

**Performance:**
- Frame size: 400-600KB (JPEG quality 95%)
- Refresh rate: 30 FPS (background thread)
- Latency: <100ms

**Usage Example:**
```bash
# Fetch latest frame
curl http://192.168.1.237/camera/frame --output latest_frame.jpg

# Display in browser
# Simply navigate to: http://192.168.1.237/camera/frame
```

---

#### POST /camera/record/start

Start recording video from camera stream.

**Request:**
```http
POST /camera/record/start HTTP/1.1
Host: 192.168.1.237
Content-Type: application/json

{
  "duration": 60,
  "filename": "optional_custom_name"
}
```

**Parameters:**
- `duration` (optional): Recording duration in seconds (default: unlimited)
- `filename` (optional): Custom filename (default: `recording_YYYYMMDD_HHMMSS.mp4`)

**Response:**
```json
{
  "status": "recording_started",
  "filename": "recording_20260216_143215.mp4",
  "path": "/home/d3kos/camera-recordings/recording_20260216_143215.mp4",
  "started_at": "2026-02-16T14:32:15.123456"
}
```

**Status Codes:**
- `200 OK` - Recording started successfully
- `400 Bad Request` - Invalid parameters
- `409 Conflict` - Recording already in progress
- `503 Service Unavailable` - Camera not connected

---

#### POST /camera/record/stop

Stop current video recording.

**Request:**
```http
POST /camera/record/stop HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "status": "recording_stopped",
  "filename": "recording_20260216_143215.mp4",
  "path": "/home/d3kos/camera-recordings/recording_20260216_143215.mp4",
  "duration_seconds": 127.4,
  "file_size_mb": 142.3,
  "stopped_at": "2026-02-16T14:34:22.567890"
}
```

**Status Codes:**
- `200 OK` - Recording stopped successfully
- `400 Bad Request` - No recording in progress

---

#### GET /camera/recordings

List all recorded videos.

**Request:**
```http
GET /camera/recordings HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "recordings": [
    {
      "filename": "recording_20260216_143215.mp4",
      "path": "/home/d3kos/camera-recordings/recording_20260216_143215.mp4",
      "size_mb": 142.3,
      "duration_seconds": 127.4,
      "created_at": "2026-02-16T14:32:15",
      "url": "/recordings/recording_20260216_143215.mp4"
    },
    {
      "filename": "recording_20260216_120031.mp4",
      "path": "/home/d3kos/camera-recordings/recording_20260216_120031.mp4",
      "size_mb": 87.1,
      "duration_seconds": 78.2,
      "created_at": "2026-02-16T12:00:31",
      "url": "/recordings/recording_20260216_120031.mp4"
    }
  ],
  "total_recordings": 2,
  "total_size_mb": 229.4
}
```

**Status Codes:**
- `200 OK` - List retrieved successfully

---

#### POST /camera/capture

Capture a single high-resolution photo.

**Request:**
```http
POST /camera/capture HTTP/1.1
Host: 192.168.1.237
Content-Type: application/json

{
  "filename": "optional_custom_name",
  "quality": 95
}
```

**Parameters:**
- `filename` (optional): Custom filename (default: `capture_YYYYMMDD_HHMMSS.jpg`)
- `quality` (optional): JPEG quality 1-100 (default: 95)

**Response:**
```json
{
  "status": "captured",
  "filename": "capture_20260216_143445.jpg",
  "path": "/home/d3kos/camera-recordings/capture_20260216_143445.jpg",
  "size_kb": 587,
  "resolution": "3840x2160",
  "timestamp": "2026-02-16T14:34:45.123456"
}
```

**Status Codes:**
- `200 OK` - Photo captured successfully
- `503 Service Unavailable` - Camera not connected

---

## Fish Detection API

### Service: `d3kos-fish-detector`
**Port:** 8086 (internal), proxied via `/detect/` (external)
**File:** `/opt/d3kos/services/marine-vision/fish_detector.py`
**Model:** YOLOv8n ONNX (13MB)

### Endpoints

#### GET /detect/status

Get fish detection service status.

**Request:**
```http
GET /detect/status HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "service": "fish_detector",
  "status": "running",
  "model": "yolov8n.onnx",
  "model_path": "/opt/d3kos/models/marine-vision/yolov8n.onnx",
  "model_loaded": true,
  "camera_connected": true,
  "total_captures": 47,
  "uptime_seconds": 3621.4,
  "version": "2.1"
}
```

**Status Codes:**
- `200 OK` - Service operational

---

#### POST /detect/frame

Run object detection on the latest camera frame.

**Request:**
```http
POST /detect/frame HTTP/1.1
Host: 192.168.1.237
Content-Type: application/json

{
  "auto_capture": true,
  "confidence_threshold": 0.5
}
```

**Parameters:**
- `auto_capture` (optional): Trigger photo capture if person+fish detected (default: `true`)
- `confidence_threshold` (optional): Minimum confidence for detections (default: `0.5`)

**Response:**
```json
{
  "timestamp": "2026-02-16T14:45:23.987654",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.87,
      "bbox": {
        "x_center": 320.5,
        "y_center": 240.3,
        "width": 180.2,
        "height": 350.8
      }
    },
    {
      "class_id": 14,
      "class_name": "bird",
      "confidence": 0.62,
      "bbox": {
        "x_center": 410.2,
        "y_center": 380.5,
        "width": 120.4,
        "height": 80.3
      }
    }
  ],
  "person_detected": true,
  "person_confidence": 0.87,
  "fish_detected": true,
  "fish_confidence": 0.62,
  "capture_triggered": true,
  "capture_id": 48,
  "processing_time_ms": 2347
}
```

**Response Fields:**
- `detections`: Array of all detected objects
- `person_detected`: Boolean - person found in frame
- `fish_detected`: Boolean - fish proxy (bird class) found
- `capture_triggered`: Boolean - photo was captured
- `capture_id`: Integer - database ID of capture (if triggered)
- `processing_time_ms`: Inference time in milliseconds

**Status Codes:**
- `200 OK` - Detection completed successfully
- `503 Service Unavailable` - Camera not connected or model not loaded
- `500 Internal Server Error` - Inference failed

**Performance:**
- Inference time: 2-3 seconds on Raspberry Pi 4B
- Frame preprocessing: ~100ms
- ONNX inference: ~1500-2000ms
- Post-processing: ~50ms

---

## Captures API

### Service: `d3kos-fish-detector`
**Database:** `/opt/d3kos/data/marine-vision/captures.db`
**Storage:** `/home/d3kos/camera-recordings/captures/`

### Endpoints

#### GET /captures

List all captured fish photos.

**Request:**
```http
GET /captures HTTP/1.1
Host: 192.168.1.237
```

**Query Parameters:**
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `date` (optional): Filter by date YYYY-MM-DD

**Response:**
```json
{
  "captures": [
    {
      "id": 48,
      "timestamp": "2026-02-16T14:45:24.012345",
      "image_path": "/home/d3kos/camera-recordings/captures/catch_20260216_144524.jpg",
      "person_detected": true,
      "fish_detected": true,
      "person_confidence": 0.87,
      "fish_confidence": 0.62,
      "species": null,
      "location": "44.4167° N, 79.3333° W",
      "url": "/captures/48/image"
    },
    {
      "id": 47,
      "timestamp": "2026-02-16T12:23:11.876543",
      "image_path": "/home/d3kos/camera-recordings/captures/catch_20260216_122311.jpg",
      "person_detected": true,
      "fish_detected": true,
      "person_confidence": 0.91,
      "fish_confidence": 0.58,
      "species": null,
      "location": "44.4201° N, 79.3298° W",
      "url": "/captures/47/image"
    }
  ],
  "total_captures": 48,
  "total_pages": 1,
  "current_page": 1
}
```

**Status Codes:**
- `200 OK` - List retrieved successfully

---

#### GET /captures/{id}

Get details of a specific capture.

**Request:**
```http
GET /captures/48 HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "id": 48,
  "timestamp": "2026-02-16T14:45:24.012345",
  "image_path": "/home/d3kos/camera-recordings/captures/catch_20260216_144524.jpg",
  "person_detected": true,
  "fish_detected": true,
  "person_confidence": 0.87,
  "fish_confidence": 0.62,
  "species": null,
  "location": "44.4167° N, 79.3333° W",
  "weather": null,
  "regulations": null,
  "image_url": "/captures/48/image",
  "image_size_kb": 587,
  "image_resolution": "3840x2160"
}
```

**Status Codes:**
- `200 OK` - Capture found
- `404 Not Found` - Capture ID does not exist

---

#### GET /captures/{id}/image

Retrieve the captured photo image.

**Request:**
```http
GET /captures/48/image HTTP/1.1
Host: 192.168.1.237
Accept: image/jpeg
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Length: 601234

[Binary JPEG data]
```

**Status Codes:**
- `200 OK` - Image retrieved successfully
- `404 Not Found` - Capture ID does not exist or image file missing

---

#### DELETE /captures/{id}

Delete a capture from database and remove photo file.

**Request:**
```http
DELETE /captures/48 HTTP/1.1
Host: 192.168.1.237
```

**Response:**
```json
{
  "status": "deleted",
  "id": 48,
  "timestamp": "2026-02-16T15:01:32.123456"
}
```

**Status Codes:**
- `200 OK` - Capture deleted successfully
- `404 Not Found` - Capture ID does not exist
- `500 Internal Server Error` - Failed to delete file

---

## Authentication

### Current Status

**Phase 2.1:** ❌ No authentication implemented

All API endpoints are currently **publicly accessible** on the local network (192.168.1.0/24). This is acceptable for a single-user boat system.

### Future Authentication (Phase 3+)

Planned authentication methods:
- API key authentication (header-based)
- JWT tokens for web UI sessions
- Role-based access control (admin vs viewer)

**Recommendation:** For production deployment on public networks, implement nginx basic auth:

```nginx
location /camera/ {
  auth_basic "Marine Vision";
  auth_basic_user_file /etc/nginx/.htpasswd;
  proxy_pass http://localhost:8084/camera/;
}
```

---

## Error Handling

### Standard Error Response Format

All errors return JSON with consistent structure:

```json
{
  "error": "service_unavailable",
  "message": "Camera not connected",
  "details": "RTSP connection failed to 10.42.0.100:554",
  "timestamp": "2026-02-16T15:15:32.123456",
  "request_id": "req_abc123"
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `bad_request` | Invalid request parameters |
| 404 | `not_found` | Resource not found |
| 409 | `conflict` | Resource state conflict (e.g., already recording) |
| 500 | `internal_error` | Server-side error |
| 503 | `service_unavailable` | Service not ready (camera disconnected, model not loaded) |
| 504 | `timeout` | Request timed out |

### Common Error Scenarios

**Camera Disconnected:**
```json
{
  "error": "service_unavailable",
  "message": "Camera not connected",
  "details": "RTSP stream unavailable at rtsp://admin:***@10.42.0.100:554"
}
```

**Model Not Loaded:**
```json
{
  "error": "service_unavailable",
  "message": "Detection model not loaded",
  "details": "YOLOv8 ONNX model failed to initialize"
}
```

**Inference Failure:**
```json
{
  "error": "internal_error",
  "message": "Object detection failed",
  "details": "ONNX Runtime inference error: Invalid input shape"
}
```

**Recording Already Active:**
```json
{
  "error": "conflict",
  "message": "Recording already in progress",
  "details": "Stop current recording before starting new one"
}
```

---

## Code Examples

### Python - Fetch Latest Frame

```python
import requests
from PIL import Image
from io import BytesIO

# Fetch frame
response = requests.get('http://192.168.1.237/camera/frame')
response.raise_for_status()

# Convert to PIL Image
image = Image.open(BytesIO(response.content))
print(f"Frame size: {image.size}, Mode: {image.mode}")

# Save locally
image.save('latest_frame.jpg')
```

### Python - Run Object Detection

```python
import requests
import json

# Run detection with auto-capture enabled
payload = {
    "auto_capture": True,
    "confidence_threshold": 0.5
}

response = requests.post(
    'http://192.168.1.237/detect/frame',
    json=payload
)

data = response.json()

print(f"Processing time: {data['processing_time_ms']}ms")
print(f"Person detected: {data['person_detected']}")
print(f"Fish detected: {data['fish_detected']}")

if data['capture_triggered']:
    capture_id = data['capture_id']
    print(f"Photo captured! ID: {capture_id}")

    # Fetch the captured image
    img_url = f"http://192.168.1.237/captures/{capture_id}/image"
    print(f"View at: {img_url}")
```

### Python - List All Captures

```python
import requests

response = requests.get('http://192.168.1.237/captures')
data = response.json()

print(f"Total captures: {data['total_captures']}")

for capture in data['captures']:
    print(f"\nCapture #{capture['id']}")
    print(f"  Time: {capture['timestamp']}")
    print(f"  Location: {capture['location']}")
    print(f"  Confidence: Person={capture['person_confidence']:.2f}, "
          f"Fish={capture['fish_confidence']:.2f}")
    print(f"  Image: {capture['url']}")
```

### Python - Start/Stop Recording

```python
import requests
import time

# Start recording
response = requests.post('http://192.168.1.237/camera/record/start', json={
    "duration": 60,  # 60 seconds
    "filename": "fishing_trip_2026"
})

data = response.json()
print(f"Recording started: {data['filename']}")

# Wait 60 seconds
time.sleep(60)

# Stop recording
response = requests.post('http://192.168.1.237/camera/record/stop')
data = response.json()
print(f"Recording stopped: {data['filename']}")
print(f"Duration: {data['duration_seconds']}s")
print(f"Size: {data['file_size_mb']}MB")
```

### JavaScript - Live Preview (MJPEG-style)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Marine Vision Live Feed</title>
</head>
<body>
  <h1>Live Camera Feed</h1>
  <img id="preview" style="width: 100%; max-width: 800px;">

  <script>
    const preview = document.getElementById('preview');

    // Refresh frame every 125ms (8 FPS)
    setInterval(() => {
      preview.src = `http://192.168.1.237/camera/frame?t=${Date.now()}`;
    }, 125);
  </script>
</body>
</html>
```

### JavaScript - Run Detection on Button Click

```html
<!DOCTYPE html>
<html>
<head>
  <title>Fish Detection</title>
</head>
<body>
  <h1>Fish Detection Test</h1>
  <button onclick="runDetection()">Run Detection</button>
  <div id="results"></div>

  <script>
    async function runDetection() {
      const resultsDiv = document.getElementById('results');
      resultsDiv.textContent = 'Running detection...';

      try {
        const response = await fetch('http://192.168.1.237/detect/frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ auto_capture: true })
        });

        const data = await response.json();

        resultsDiv.innerHTML = `
          <h3>Results (${data.processing_time_ms}ms):</h3>
          <p>Person detected: ${data.person_detected} (${data.person_confidence})</p>
          <p>Fish detected: ${data.fish_detected} (${data.fish_confidence})</p>
          <p>Capture triggered: ${data.capture_triggered}</p>
          ${data.capture_id ? `<p>Capture ID: ${data.capture_id}</p>` : ''}
          <h4>All Detections:</h4>
          <pre>${JSON.stringify(data.detections, null, 2)}</pre>
        `;
      } catch (error) {
        resultsDiv.textContent = `Error: ${error.message}`;
      }
    }
  </script>
</body>
</html>
```

### Curl - Command Line Examples

```bash
# Check camera status
curl http://192.168.1.237/camera/status

# Fetch latest frame
curl http://192.168.1.237/camera/frame --output frame.jpg

# Run detection
curl -X POST http://192.168.1.237/detect/frame \
  -H "Content-Type: application/json" \
  -d '{"auto_capture": true, "confidence_threshold": 0.5}'

# List captures
curl http://192.168.1.237/captures

# Get specific capture details
curl http://192.168.1.237/captures/48

# Download capture image
curl http://192.168.1.237/captures/48/image --output catch_48.jpg

# Start recording
curl -X POST http://192.168.1.237/camera/record/start \
  -H "Content-Type: application/json" \
  -d '{"duration": 60}'

# Stop recording
curl -X POST http://192.168.1.237/camera/record/stop

# List recordings
curl http://192.168.1.237/camera/recordings
```

---

## WebSocket Streaming

### Status: Not Implemented (Future Phase)

WebSocket streaming would enable:
- Real-time frame streaming to multiple clients
- Live detection results broadcast
- Lower latency than HTTP polling
- Bidirectional communication

**Planned Endpoint:**
```
ws://192.168.1.237/camera/stream
```

**Planned Message Format:**
```json
{
  "type": "frame",
  "timestamp": "2026-02-16T15:30:45.123456",
  "frame": "[base64 encoded JPEG]",
  "detections": []
}
```

**Alternative:** Current HTTP polling approach works well for 8 FPS refresh rate.

---

## Performance Considerations

### Camera Stream Service

**Frame Rate:**
- Background grabber: 30 FPS
- HTTP endpoint: On-demand (can serve 8 FPS to multiple clients)
- Recommendation: Poll at 8 FPS (125ms interval) for smooth preview

**Memory Usage:**
- Frame buffer: ~2MB (one 1080p frame in memory)
- VLC recording: Minimal (streams to disk)
- Service baseline: ~150MB RAM

**Network Bandwidth:**
- Frame size: 400-600KB JPEG
- 8 FPS streaming: ~4.8 MB/s (38 Mbps)
- Recording bitrate: ~1-2 Mbps (VLC H.264)

### Fish Detection Service

**Inference Performance:**
- YOLOv8n ONNX on Pi 4B: 2-3 seconds per frame
- Recommendation: On-demand detection only (don't poll continuously)
- Batch processing: Not currently supported

**Memory Usage:**
- ONNX Runtime: ~150MB
- YOLOv8n model: 13MB disk, ~50MB loaded in RAM
- Python process: ~200MB total
- Peak during inference: ~350MB

**CPU Usage:**
- Idle: <1%
- During inference: 60-80% (single core, spreads across cores)
- Multi-core benefit: Yes (ONNX Runtime uses 4 cores)

**Optimization Tips:**
1. **Reduce frame resolution before inference:**
   ```python
   # Resize 4K → 640×640 before sending to model
   img_resized = cv2.resize(img, (640, 640))
   ```

2. **Skip frames for continuous monitoring:**
   ```python
   # Process every 5th frame (6 FPS effective rate)
   if frame_count % 5 == 0:
       run_detection(frame)
   ```

3. **Use sub-stream for detection:**
   - Main stream (4K): High-res captures only
   - Sub-stream (1080p/720p): Live preview and detection

4. **Adjust confidence thresholds:**
   - Lower threshold (0.3): More detections, more false positives
   - Higher threshold (0.7): Fewer detections, fewer false positives
   - Default (0.5): Balanced

### Database Performance

**SQLite Captures Database:**
- Location: `/opt/d3kos/data/marine-vision/captures.db`
- Table: `captures` (10 columns)
- Write speed: ~100 inserts/second
- Read speed: ~1000 queries/second
- Index: Primary key on `id`, index on `timestamp`

**Storage Growth:**
- Each capture: ~600KB JPEG + 1KB database row
- 100 captures/day: ~60MB/day
- 32GB SD card: ~500 days of captures
- Recommendation: Periodic cleanup of old captures

### Network Considerations

**Local Network (192.168.1.0/24):**
- Latency: <1ms
- Bandwidth: 1000 Mbps (Gigabit Ethernet or WiFi 5)
- No internet required for core functionality

**Camera Network (10.42.0.0/24):**
- Pi ethernet shared connection
- Camera at 10.42.0.100
- DHCP reservation ensures stable IP
- Bandwidth: 100 Mbps (camera limitation)

**Port Forwarding (External Access):**
- NOT RECOMMENDED for security reasons
- Use VPN (Tailscale, WireGuard) for remote access
- Or nginx basic auth if exposing to internet

---

## Rate Limiting

### Current Status: No Rate Limiting

All endpoints are currently **unlimited**. For production deployment, consider implementing rate limits:

**Recommended Limits:**
- `/camera/frame`: 10 requests/second (prevents bandwidth abuse)
- `/detect/frame`: 1 request/5 seconds (prevents CPU overload)
- `/camera/record/start`: 1 request/minute (prevents storage abuse)

**Implementation:** Use nginx `limit_req` module:

```nginx
limit_req_zone $binary_remote_addr zone=detect:10m rate=1r/s;

location /detect/ {
  limit_req zone=detect burst=2;
  proxy_pass http://localhost:8086/detect/;
}
```

---

## Versioning

### Current Version: 2.1 (Phase 2.1)

**API Versioning:**
- No versioned endpoints yet (e.g., `/v1/camera/status`)
- All endpoints are considered **v2.1** implicitly
- Breaking changes will require version prefix

**Backward Compatibility:**
- Phase 2.1 API is stable and will not change
- Phase 2.2+ will add new endpoints (non-breaking)
- Future phases may deprecate endpoints (with warning period)

**Changelog:**

**v2.1 (February 16, 2026):**
- ✅ Fish detection API endpoints
- ✅ Captures database and API
- ✅ YOLOv8 ONNX integration

**v2.0 (February 14, 2026):**
- ✅ Camera stream API endpoints
- ✅ Video recording support
- ✅ Photo capture support

---

## Troubleshooting

### Camera Connection Issues

**Problem:** `GET /camera/status` returns `"connected": false`

**Solutions:**
1. Check camera power and network cable
2. Verify camera IP: `ping 10.42.0.100`
3. Test RTSP stream: `ffplay rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub`
4. Restart camera stream service: `sudo systemctl restart d3kos-camera-stream`
5. Check service logs: `sudo journalctl -u d3kos-camera-stream -f`

### Detection Service Issues

**Problem:** `POST /detect/frame` returns 503 error

**Solutions:**
1. Check if camera stream is running: `GET /camera/status`
2. Verify model file exists: `ls -lh /opt/d3kos/models/marine-vision/yolov8n.onnx`
3. Restart detection service: `sudo systemctl restart d3kos-fish-detector`
4. Check logs: `sudo journalctl -u d3kos-fish-detector -f`

### Performance Issues

**Problem:** Detection taking >5 seconds

**Solutions:**
1. Check CPU usage: `htop`
2. Verify using sub-stream (not main 4K stream)
3. Reduce confidence threshold (less post-processing)
4. Restart service to clear memory: `sudo systemctl restart d3kos-fish-detector`

### Storage Issues

**Problem:** Recording fails with "No space left on device"

**Solutions:**
1. Check SD card space: `df -h`
2. Delete old recordings: `rm /home/d3kos/camera-recordings/*.mp4`
3. Delete old captures: `rm /home/d3kos/camera-recordings/captures/*.jpg`
4. Upgrade to 32GB or 128GB SD card

---

## Future Enhancements (Roadmap)

### Phase 2.2: Custom Fish Detection Model
- Fine-tune YOLOv8 on fish dataset
- Replace "bird" proxy with actual fish class
- Improved accuracy for marine fish species

### Phase 2.3: Continuous Monitoring
- Background detection thread
- Frame skipping for real-time performance
- WebSocket streaming for live results

### Phase 2.4: Species Identification
- ResNet50/MobileNetV2 classifier
- FishBase API integration
- Ontario fish species database

### Phase 2.5: Fishing Regulations
- Ontario MNR regulations database
- Size and bag limit checking
- Automatic compliance alerts

### Phase 2.6: Notifications
- Telegram bot integration
- Signal notifications
- Email alerts with photos

### Phase 4: Forward Watch Mode
- Marine object detection (boats, kayaks, buoys, debris)
- MiDaS/ZoeDepth monocular depth estimation
- Distance alerts for collision avoidance
- Integration with chartplotter

### Phase 5: Mode Switching
- Searchlight orientation detection
- Automatic mode selection
- Manual override controls

---

## Support & Resources

### Documentation
- **Marine Vision Specification:** `/home/boatiq/Helm-OS/doc/MARINE_VISION.md`
- **Phase 1 Complete:** `/home/boatiq/Helm-OS/doc/MARINE_VISION_PHASE1_COMPLETE.md`
- **Phase 2.1 Complete:** `/home/boatiq/Helm-OS/doc/MARINE_VISION_PHASE2.1_COMPLETE.md`
- **Master System Spec:** `/home/boatiq/Helm-OS/doc/MASTER_SYSTEM_SPEC.md`

### Service Files
- Camera Stream: `/opt/d3kos/services/marine-vision/camera_stream_manager.py`
- Fish Detector: `/opt/d3kos/services/marine-vision/fish_detector.py`
- Systemd Services: `/etc/systemd/system/d3kos-*.service`

### Web Interface
- Live Preview: http://192.168.1.237/marine-vision.html
- Settings: http://192.168.1.237/settings.html

### Community
- GitHub: https://github.com/boatiq/Helm-OS
- AtMyBoat.com: https://atmyboat.com

---

**Document Version:** 1.0
**Created:** February 16, 2026
**For:** d3kOS Marine Vision System v2.1
**Author:** d3kOS Documentation Team
