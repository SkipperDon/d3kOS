# HELM-OS API REFERENCE

**Version**: 2.0
**Last Updated**: February 6, 2026

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Signal K Integration](#signal-k-integration)
4. [WebSocket API](#websocket-api)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Code Examples](#code-examples)

---

## OVERVIEW

d3kOS provides multiple APIs for integration and automation:

1. **d3kOS REST API**: System control and configuration
2. **Signal K REST API**: Marine data access (standardized)
3. **Signal K WebSocket**: Real-time data streaming
4. **d3kOS WebSocket**: System events and commands

### Base URLs

| API | URL | Protocol |
|-----|-----|----------|
| d3kOS REST | `http://10.42.0.1/api` | HTTP/1.1 |
| Signal K REST | `http://10.42.0.1:3000/signalk/v1/api` | HTTP/1.1 |
| Signal K WebSocket | `ws://10.42.0.1:3000/signalk/v1/stream` | WebSocket |
| d3kOS WebSocket | `ws://10.42.0.1:3000/d3kos` | WebSocket |

### Response Format

All API responses use JSON format:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-06T14:30:00Z",
  "version": "2.0.0"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "ENGINE_NOT_FOUND",
    "message": "Engine baseline data not found",
    "details": "Run engine benchmark first"
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

---

## API ENDPOINTS

### System Health

#### GET /api/health

Get overall system health status.

**Request:**
```
GET /api/health HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "cpu_temp": 65.3,
      "cpu_usage": 45.2,
      "memory_usage": 62.1,
      "disk_free": 42.3,
      "gpu_temp": 58.0,
      "throttled": false,
      "uptime_seconds": 312480
    },
    "services": {
      "signalk": "running",
      "nodered": "running",
      "gpsd": "running",
      "helm_voice": "stopped",
      "helm_camera": "stopped",
      "helm_health": "running"
    },
    "network": {
      "wifi_clients": 2,
      "ethernet_connected": false,
      "internet_available": false
    }
  },
  "timestamp": "2026-02-06T14:30:00Z",
  "version": "2.0.0"
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: System error

---

### Engine Baseline

#### GET /api/engine/baseline

Get engine baseline data.

**Request:**
```
GET /api/engine/baseline HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-06T10:00:00Z",
    "engine_hours": 245.5,
    "samples": 1800,
    "metrics": {
      "rpm_idle": {
        "mean": 720,
        "stddev": 15,
        "min": 690,
        "max": 750
      },
      "rpm_cruise": {
        "mean": 3200,
        "stddev": 50,
        "min": 3100,
        "max": 3300
      },
      "temp_steady_state": 180,
      "oil_pressure_idle": 12,
      "oil_pressure_cruise": 45,
      "fuel_rate_cruise": 4.2,
      "voltage_charging": 14.2
    },
    "engine_info": {
      "manufacturer": "Mercury Marine",
      "model": "5.0L MPI Alpha",
      "year": 2018,
      "cylinders": 8,
      "displacement_l": 5.0
    }
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Baseline not established
- `500 Internal Server Error`: System error

---

#### GET /api/engine/current

Get current engine metrics.

**Request:**
```
GET /api/engine/current HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-06T14:30:15Z",
    "engine_hours": 247.2,
    "metrics": {
      "rpm": 3250,
      "oil_pressure": 43,
      "coolant_temp": 182,
      "fuel_rate": 4.5,
      "voltage": 14.1,
      "throttle_position": 75
    },
    "status": {
      "running": true,
      "anomalies": [
        {
          "level": "INFO",
          "metric": "coolant_temp",
          "message": "Coolant temperature slightly elevated",
          "deviation": 2.0,
          "sigma": 1.2
        }
      ],
      "health": "NORMAL"
    }
  },
  "timestamp": "2026-02-06T14:30:15Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: No current data available
- `500 Internal Server Error`: System error

---

#### POST /api/engine/benchmark/start

Start engine benchmarking process.

**Request:**
```
POST /api/engine/benchmark/start HTTP/1.1
Host: 10.42.0.1
Content-Type: application/json

{
  "duration_minutes": 30,
  "overwrite_existing": false
}
```

**Parameters:**
- `duration_minutes` (integer, optional): Benchmark duration (default: 30, min: 10, max: 60)
- `overwrite_existing` (boolean, optional): Replace existing baseline (default: false)

**Response:**
```json
{
  "success": true,
  "data": {
    "benchmark_id": "bench_a3f7c91e",
    "started_at": "2026-02-06T14:30:00Z",
    "duration_minutes": 30,
    "expected_completion": "2026-02-06T15:00:00Z",
    "status": "in_progress"
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `201 Created`: Benchmark started
- `400 Bad Request`: Invalid parameters
- `409 Conflict`: Benchmark already running or baseline exists
- `500 Internal Server Error`: System error

---

#### GET /api/engine/benchmark/status

Get benchmarking process status.

**Request:**
```
GET /api/engine/benchmark/status HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "benchmark_id": "bench_a3f7c91e",
    "status": "in_progress",
    "started_at": "2026-02-06T14:30:00Z",
    "progress": 45.3,
    "samples_collected": 815,
    "samples_target": 1800,
    "estimated_completion": "2026-02-06T14:46:30Z"
  },
  "timestamp": "2026-02-06T14:43:38Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: No benchmark in progress
- `500 Internal Server Error`: System error

---

### Voice Assistant

#### POST /api/voice/enable

Enable voice assistant.

**Request:**
```
POST /api/voice/enable HTTP/1.1
Host: 10.42.0.1
Content-Type: application/json

{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "voice_enabled": true,
    "service_status": "starting",
    "tier": 2,
    "wake_word": "Helm"
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `403 Forbidden`: Tier 0 (upgrade required)
- `500 Internal Server Error`: Service failed to start

---

#### GET /api/voice/status

Get voice assistant status.

**Request:**
```
GET /api/voice/status HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "service_status": "running",
    "listening": true,
    "last_command": {
      "timestamp": "2026-02-06T14:28:45Z",
      "transcription": "what's the engine status",
      "response": "Engine is running normally at 3200 RPM, all systems green.",
      "duration_ms": 1850
    },
    "statistics": {
      "total_commands": 47,
      "success_rate": 95.7,
      "avg_response_time_ms": 1920
    }
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Voice assistant not enabled
- `500 Internal Server Error`: System error

---

### Camera

#### GET /api/camera/status

Get camera connection status.

**Request:**
```
GET /api/camera/status HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "camera_url": "rtsp://192.168.1.100:554/h264Preview_01_main",
    "recording": false,
    "storage": {
      "total_gb": 64,
      "used_gb": 27,
      "free_gb": 37,
      "free_percent": 57.8
    },
    "recordings": {
      "count": 23,
      "oldest": "2026-01-15T08:30:00Z",
      "newest": "2026-02-06T12:15:00Z"
    }
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `403 Forbidden`: Tier 0 (upgrade required)
- `404 Not Found`: Camera not configured
- `500 Internal Server Error`: System error

---

#### POST /api/camera/recording/start

Start camera recording.

**Request:**
```
POST /api/camera/recording/start HTTP/1.1
Host: 10.42.0.1
Content-Type: application/json

{
  "quality": "high",
  "segment_minutes": 10
}
```

**Parameters:**
- `quality` (string, optional): "low", "medium", "high" (default: "high")
- `segment_minutes` (integer, optional): Recording segment duration (default: 10, min: 5, max: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "recording_id": "rec_20260206_143000",
    "started_at": "2026-02-06T14:30:00Z",
    "quality": "high",
    "segment_minutes": 10,
    "file_path": "/opt/d3kos/data/camera/20260206_143000_camera.mp4"
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `201 Created`: Recording started
- `400 Bad Request`: Invalid parameters
- `403 Forbidden`: Tier 0 or insufficient disk space
- `409 Conflict`: Recording already in progress
- `500 Internal Server Error`: System error

---

#### POST /api/camera/recording/stop

Stop camera recording.

**Request:**
```
POST /api/camera/recording/stop HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recording_id": "rec_20260206_143000",
    "stopped_at": "2026-02-06T14:45:30Z",
    "duration_seconds": 930,
    "file_size_mb": 124.5,
    "file_path": "/opt/d3kos/data/camera/20260206_143000_camera.mp4"
  },
  "timestamp": "2026-02-06T14:45:30Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: No recording in progress
- `500 Internal Server Error`: System error

---

### Onboarding

#### POST /api/onboarding/reset

Reset onboarding wizard.

**Request:**
```
POST /api/onboarding/reset HTTP/1.1
Host: 10.42.0.1
Content-Type: application/json

{
  "confirm": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "reset_count": 8,
    "max_resets": 10,
    "remaining_resets": 2,
    "tier": 0,
    "warning": "Only 2 resets remaining. Consider upgrading to Tier 2 for unlimited resets."
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Confirmation not provided
- `403 Forbidden`: Reset limit reached (Tier 0)
- `500 Internal Server Error`: System error

---

### License

#### GET /api/license

Get license information.

**Request:**
```
GET /api/license HTTP/1.1
Host: 10.42.0.1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tier": 2,
    "installation_id": "a3f7c91e8d2b4f60",
    "installed_apps": ["opencpn"],
    "reset_count": 7,
    "max_resets": "unlimited",
    "version": "2.0.0",
    "last_update_check": "2026-02-06T14:30:00Z",
    "features": {
      "voice_assistant": true,
      "camera": true,
      "unlimited_resets": true,
      "cloud_sync": false,
      "remote_monitoring": false
    },
    "update_available": false
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: System error

---

### Historical Data

#### GET /api/historical/engine

Get historical engine data.

**Request:**
```
GET /api/historical/engine?start=2026-02-01T00:00:00Z&end=2026-02-06T23:59:59Z&interval=1h HTTP/1.1
Host: 10.42.0.1
```

**Query Parameters:**
- `start` (ISO8601 datetime, required): Start time
- `end` (ISO8601 datetime, required): End time
- `interval` (string, optional): Data aggregation interval (1m, 5m, 1h, 1d) (default: 5m)
- `metrics` (string, optional): Comma-separated metrics (default: all)

**Response:**
```json
{
  "success": true,
  "data": {
    "start": "2026-02-01T00:00:00Z",
    "end": "2026-02-06T23:59:59Z",
    "interval": "1h",
    "points": [
      {
        "timestamp": "2026-02-01T00:00:00Z",
        "rpm": 3215,
        "oil_pressure": 44,
        "coolant_temp": 181,
        "fuel_rate": 4.3,
        "voltage": 14.2
      },
      {
        "timestamp": "2026-02-01T01:00:00Z",
        "rpm": 3198,
        "oil_pressure": 45,
        "coolant_temp": 180,
        "fuel_rate": 4.2,
        "voltage": 14.1
      }
    ],
    "total_points": 144
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: No data for time range
- `500 Internal Server Error`: System error

---

## SIGNAL K INTEGRATION

Signal K is the standardized marine data format. d3kOS fully implements Signal K v1.x.

### Base URL

```
http://10.42.0.1:3000/signalk/v1/api
```

### Common Endpoints

#### GET /vessels/self

Get all vessel data.

**Request:**
```
GET /signalk/v1/api/vessels/self HTTP/1.1
Host: 10.42.0.1:3000
```

**Response:**
```json
{
  "uuid": "urn:mrn:signalk:uuid:a3f7c91e-8d2b-4f60-9c1a-3e7f8d2b4f60",
  "propulsion": {
    "main": {
      "revolutions": {
        "value": 53.33,
        "timestamp": "2026-02-06T14:30:15.000Z",
        "$source": "can0.127488",
        "_attr": {
          "rpm": 3200
        }
      },
      "oilPressure": {
        "value": 296527.5,
        "timestamp": "2026-02-06T14:30:15.000Z",
        "$source": "can0.127489"
      },
      "temperature": {
        "value": 355.37,
        "timestamp": "2026-02-06T14:30:15.000Z",
        "$source": "can0.127489"
      }
    }
  },
  "navigation": {
    "position": {
      "latitude": 43.6532,
      "longitude": -79.3832,
      "timestamp": "2026-02-06T14:30:15.000Z",
      "$source": "gpsd.GPS"
    },
    "speedOverGround": {
      "value": 5.14,
      "timestamp": "2026-02-06T14:30:15.000Z",
      "$source": "can0.129026"
    },
    "courseOverGroundTrue": {
      "value": 1.5708,
      "timestamp": "2026-02-06T14:30:15.000Z",
      "$source": "can0.129026"
    }
  },
  "electrical": {
    "batteries": {
      "0": {
        "voltage": {
          "value": 14.2,
          "timestamp": "2026-02-06T14:30:15.000Z",
          "$source": "can0.127508"
        }
      }
    }
  }
}
```

---

#### GET /vessels/self/{path}

Get specific data path.

**Example - Engine RPM:**
```
GET /signalk/v1/api/vessels/self/propulsion/main/revolutions HTTP/1.1
Host: 10.42.0.1:3000
```

**Response:**
```json
{
  "path": "propulsion.main.revolutions",
  "value": 53.33,
  "timestamp": "2026-02-06T14:30:15.000Z",
  "$source": "can0.127488",
  "_attr": {
    "rpm": 3200
  }
}
```

---

### Signal K Data Paths

| Parameter | Signal K Path | Unit | PGN |
|-----------|---------------|------|-----|
| Engine RPM | `propulsion.main.revolutions` | rev/s (×60 for RPM) | 127488 |
| Oil Pressure | `propulsion.main.oilPressure` | Pa (÷6895 for PSI) | 127489 |
| Coolant Temp | `propulsion.main.temperature` | K (−273.15 for °C) | 127489 |
| Fuel Rate | `propulsion.main.fuelRate` | m³/s (×3600000 for L/h) | 127489 |
| Battery Voltage | `electrical.batteries.0.voltage` | V | 127508 |
| Fuel Level | `tanks.fuel.0.currentLevel` | ratio (×100 for %) | 127505 |
| Water Depth | `environment.depth.belowTransducer` | m | 128267 |
| Water Speed | `navigation.speedThroughWater` | m/s (×1.944 for knots) | 128259 |
| Position (Lat) | `navigation.position.latitude` | radians (×180/π for °) | 129025 |
| Position (Lon) | `navigation.position.longitude` | radians (×180/π for °) | 129025 |
| COG | `navigation.courseOverGroundTrue` | radians (×180/π for °) | 129026 |
| SOG | `navigation.speedOverGround` | m/s (×1.944 for knots) | 129026 |

---

## WEBSOCKET API

### Signal K WebSocket

Real-time streaming of all Signal K data.

**Connection:**
```javascript
const ws = new WebSocket('ws://10.42.0.1:3000/signalk/v1/stream');

ws.onopen = () => {
  console.log('Connected to Signal K');

  // Subscribe to specific paths
  ws.send(JSON.stringify({
    context: 'vessels.self',
    subscribe: [
      {
        path: 'propulsion.main.revolutions',
        period: 1000,
        format: 'delta',
        policy: 'instant'
      },
      {
        path: 'navigation.position',
        period: 1000,
        format: 'delta',
        policy: 'instant'
      }
    ]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Signal K update:', data);
};
```

**Delta Message Format:**
```json
{
  "context": "vessels.urn:mrn:signalk:uuid:a3f7c91e-8d2b-4f60-9c1a-3e7f8d2b4f60",
  "updates": [
    {
      "source": {
        "label": "can0",
        "type": "NMEA2000",
        "pgn": 127488
      },
      "timestamp": "2026-02-06T14:30:15.000Z",
      "values": [
        {
          "path": "propulsion.main.revolutions",
          "value": 53.33
        }
      ]
    }
  ]
}
```

---

### d3kOS WebSocket

System events and commands.

**Connection:**
```javascript
const ws = new WebSocket('ws://10.42.0.1:3000/d3kos');

ws.onopen = () => {
  console.log('Connected to d3kOS');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'anomaly':
      handleAnomaly(message.data);
      break;
    case 'voice_command':
      handleVoiceCommand(message.data);
      break;
    case 'system_alert':
      handleSystemAlert(message.data);
      break;
  }
};

// Send command to backend
function sendCommand(cmd, params) {
  ws.send(JSON.stringify({
    command: cmd,
    params: params,
    timestamp: new Date().toISOString()
  }));
}
```

**Event Types:**

1. **Anomaly Detection**
```json
{
  "type": "anomaly",
  "data": {
    "level": "WARNING",
    "metric": "oil_pressure",
    "message": "Oil pressure is 10 PSI below baseline",
    "current_value": 35,
    "baseline_value": 45,
    "deviation": -10,
    "sigma": 2.3,
    "timestamp": "2026-02-06T14:30:15.000Z"
  }
}
```

2. **Voice Command**
```json
{
  "type": "voice_command",
  "data": {
    "transcription": "what's the engine status",
    "response": "Engine is running normally at 3200 RPM",
    "duration_ms": 1850,
    "timestamp": "2026-02-06T14:30:15.000Z"
  }
}
```

3. **System Alert**
```json
{
  "type": "system_alert",
  "data": {
    "level": "WARNING",
    "component": "raspberry_pi",
    "message": "CPU temperature high (78°C)",
    "value": 78.0,
    "threshold": 75.0,
    "timestamp": "2026-02-06T14:30:15.000Z"
  }
}
```

---

## AUTHENTICATION

### Tier 0 & Tier 2 (Local Access)

No authentication required for local WiFi access (10.42.0.x network).

### Tier 3 (Remote Access)

Remote access requires authentication (future feature).

**Authorization Header:**
```
Authorization: Bearer <api_token>
```

**Example:**
```
GET /api/health HTTP/1.1
Host: d3kos.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ERROR HANDLING

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context or debugging information"
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request or invalid parameters |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Tier upgrade required |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., benchmark running) |
| `RATE_LIMIT` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Tier Restriction Errors

When accessing Tier 2+ features from Tier 0:

```json
{
  "success": false,
  "error": {
    "code": "TIER_UPGRADE_REQUIRED",
    "message": "This feature requires Tier 2 or higher",
    "details": "Install OpenCPN or subscribe to unlock voice assistant and camera features",
    "current_tier": 0,
    "required_tier": 2,
    "upgrade_options": [
      "Install OpenCPN (free, unlocks Tier 2)",
      "Subscribe to Tier 3 (cloud features)"
    ]
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

---

## RATE LIMITING

### Limits

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| GET /api/* | 100 requests | 1 minute |
| POST /api/* | 20 requests | 1 minute |
| WebSocket connections | 5 connections | per client IP |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1675702800
```

### Rate Limit Exceeded

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": "Rate limit: 100 requests per minute",
    "retry_after_seconds": 42
  },
  "timestamp": "2026-02-06T14:30:00Z"
}
```

---

## CODE EXAMPLES

### JavaScript/Node.js

**Get Engine Status:**
```javascript
const axios = require('axios');

async function getEngineStatus() {
  try {
    const response = await axios.get('http://10.42.0.1/api/engine/current');

    if (response.data.success) {
      const metrics = response.data.data.metrics;
      console.log(`Engine RPM: ${metrics.rpm}`);
      console.log(`Oil Pressure: ${metrics.oil_pressure} PSI`);
      console.log(`Coolant Temp: ${metrics.coolant_temp}°F`);

      // Check for anomalies
      const anomalies = response.data.data.status.anomalies;
      if (anomalies.length > 0) {
        console.log('Anomalies detected:');
        anomalies.forEach(a => console.log(`  - ${a.message}`));
      }
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

getEngineStatus();
```

**WebSocket Real-Time Updates:**
```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://10.42.0.1:3000/signalk/v1/stream');

ws.on('open', () => {
  // Subscribe to engine RPM
  ws.send(JSON.stringify({
    context: 'vessels.self',
    subscribe: [
      {
        path: 'propulsion.main.revolutions',
        period: 1000
      }
    ]
  }));
});

ws.on('message', (data) => {
  const message = JSON.parse(data);

  if (message.updates) {
    message.updates.forEach(update => {
      update.values.forEach(value => {
        if (value.path === 'propulsion.main.revolutions') {
          const rpm = Math.round(value.value * 60);
          console.log(`Engine RPM: ${rpm}`);
        }
      });
    });
  }
});
```

---

### Python

**Get System Health:**
```python
import requests
import json

def get_system_health():
    url = 'http://10.42.0.1/api/health'

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if data['success']:
            system = data['data']['system']
            print(f"CPU Temp: {system['cpu_temp']}°C")
            print(f"CPU Usage: {system['cpu_usage']}%")
            print(f"Memory Usage: {system['memory_usage']}%")
            print(f"Disk Free: {system['disk_free']}%")

            if system['throttled']:
                print("WARNING: System is throttled!")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

get_system_health()
```

**Start Engine Benchmark:**
```python
import requests
import time

def start_benchmark(duration_minutes=30):
    url = 'http://10.42.0.1/api/engine/benchmark/start'
    payload = {'duration_minutes': duration_minutes}

    response = requests.post(url, json=payload)
    data = response.json()

    if data['success']:
        benchmark_id = data['data']['benchmark_id']
        print(f"Benchmark started: {benchmark_id}")

        # Monitor progress
        while True:
            status_response = requests.get('http://10.42.0.1/api/engine/benchmark/status')
            status_data = status_response.json()

            if status_data['success']:
                progress = status_data['data']['progress']
                print(f"Progress: {progress:.1f}%")

                if status_data['data']['status'] == 'completed':
                    print("Benchmark complete!")
                    break

            time.sleep(10)
    else:
        print(f"Error: {data['error']['message']}")

start_benchmark()
```

---

### cURL

**Get Engine Baseline:**
```bash
curl -X GET http://10.42.0.1/api/engine/baseline \
  -H "Accept: application/json" | jq
```

**Start Camera Recording:**
```bash
curl -X POST http://10.42.0.1/api/camera/recording/start \
  -H "Content-Type: application/json" \
  -d '{"quality": "high", "segment_minutes": 10}' | jq
```

**Get Historical Data:**
```bash
curl -X GET "http://10.42.0.1/api/historical/engine?start=2026-02-01T00:00:00Z&end=2026-02-06T23:59:59Z&interval=1h" \
  -H "Accept: application/json" | jq
```

---

## ADDITIONAL RESOURCES

- **Signal K Documentation**: https://signalk.org/specification/latest/
- **Signal K GitHub**: https://github.com/SignalK
- **d3kOS GitHub**: https://github.com/SkipperDon/d3kOS
- **WebSocket RFC**: https://tools.ietf.org/html/rfc6455

---

**API Version**: 2.0.0
**Last Updated**: February 6, 2026
