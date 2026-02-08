# HELM-OS DATA MODEL

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0
**Audience**: Developers

---

## TABLE OF CONTENTS

1. [Data Architecture Overview](#data-architecture-overview)
2. [Signal K Data Model](#signal-k-data-model)
3. [Configuration Data](#configuration-data)
4. [State Management](#state-management)
5. [Historical Data](#historical-data)
6. [File Storage](#file-storage)
7. [Data Flow](#data-flow)
8. [API Data Formats](#api-data-formats)
9. [Data Retention Policies](#data-retention-policies)
10. [Database Schemas](#database-schemas)

---

## 1. DATA ARCHITECTURE OVERVIEW

### 1.1 Data Layers

```
┌─────────────────────────────────────────────────┐
│           PRESENTATION LAYER                    │
│  Dashboard UI, Gauges, Charts, Voice Interface  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           APPLICATION LAYER                     │
│  Node-RED Flows, Health Monitor, Voice Engine  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           DATA AGGREGATION LAYER                │
│  Signal K Server, GPSd, Data Processors        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           DATA PERSISTENCE LAYER                │
│  Files (JSON), SQLite DB, Logs, Recordings     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           HARDWARE/SENSOR LAYER                 │
│  NMEA2000, GPS, AIS, Camera, Microphone        │
└─────────────────────────────────────────────────┘
```

### 1.2 Data Categories

| Category | Storage | Format | Persistence | Update Frequency |
|----------|---------|--------|-------------|------------------|
| **Configuration** | JSON files | JSON | Permanent | Manual (user) |
| **State** | JSON files | JSON | Session/permanent | Real-time |
| **Real-time Data** | Memory + WebSocket | JSON | Volatile | 1Hz - 10Hz |
| **Historical Data** | SQLite | Structured | 90 days | 1Hz |
| **Logs** | Text files | Plain text | 30-90 days | Event-driven |
| **Media** | Binary files | MP4, WAV | Until disk full | Continuous (recording) |

### 1.3 Data Storage Locations

```
/opt/d3kos/
├── config/                      # Configuration (permanent)
│   ├── onboarding.json         # User onboarding responses
│   ├── benchmark-results.json  # Engine baseline data
│   ├── license.json            # Tier & entitlements
│   └── engine-manufacturers.json # Manufacturer database
│
├── state/                       # Runtime state
│   ├── onboarding-reset-count.json # Reset tracking
│   └── pi-health-status.json   # System health metrics
│
├── data/                        # User data & logs
│   ├── boat-log.txt            # Boat log entries (text)
│   ├── historical.db           # SQLite database
│   ├── camera/                 # Camera recordings (MP4)
│   │   └── YYYYMMDD_HHMMSS_camera.mp4
│   ├── voice/                  # Voice recordings (temp)
│   │   └── recording_*.wav
│   └── exports/                # Exported data (CSV/JSON)
│       ├── engine_data_*.csv
│       └── d3kos-config.json
│
├── models/                      # AI models (static)
│   ├── vosk/                   # STT model (50MB)
│   ├── piper/                  # TTS voice (20MB)
│   └── phi2/                   # LLM model (5GB)
│
└── logs/                        # Application logs
    ├── onboarding.log
    ├── voice.log
    ├── health.log
    └── camera.log
```

---

## 2. SIGNAL K DATA MODEL

### 2.1 Signal K Overview

Signal K is the marine data standard used by d3kOS. All NMEA2000 and NMEA0183 data is converted to Signal K format.

**Signal K Specification**: https://signalk.org/specification/

### 2.2 Signal K Data Structure

**Root Object**:
```json
{
  "vessels": {
    "urn:mrn:signalk:uuid:<uuid>": {
      "name": "My Boat",
      "navigation": { ... },
      "propulsion": { ... },
      "electrical": { ... },
      "environment": { ... },
      "tanks": { ... }
    }
  },
  "sources": { ... },
  "version": "1.7.0"
}
```

### 2.3 Signal K Paths (d3kOS Core)

#### Navigation Data

| Path | Type | Unit | Source | Description |
|------|------|------|--------|-------------|
| `navigation.position` | Object | deg | GPS | Latitude/longitude |
| `navigation.position.latitude` | Number | rad | GPS | Latitude in radians |
| `navigation.position.longitude` | Number | rad | GPS | Longitude in radians |
| `navigation.speedOverGround` | Number | m/s | GPS | Speed over ground |
| `navigation.courseOverGroundTrue` | Number | rad | GPS | Course over ground (true) |
| `navigation.speedThroughWater` | Number | m/s | NMEA2000 | Speed through water |
| `navigation.headingTrue` | Number | rad | NMEA2000 | True heading |
| `navigation.headingMagnetic` | Number | rad | NMEA2000 | Magnetic heading |

#### Propulsion (Engine) Data

| Path | Type | Unit | Source | Description |
|------|------|------|--------|-------------|
| `propulsion.main.revolutions` | Number | RPM | NMEA2000 | Engine RPM |
| `propulsion.main.temperature` | Number | K | NMEA2000 | Coolant temperature |
| `propulsion.main.oilPressure` | Number | Pa | NMEA2000 | Oil pressure |
| `propulsion.main.oilTemperature` | Number | K | NMEA2000 | Oil temperature |
| `propulsion.main.alternatorVoltage` | Number | V | NMEA2000 | Alternator voltage |
| `propulsion.main.engineHours` | Number | s | NMEA2000 | Engine running hours |
| `propulsion.main.coolantPressure` | Number | Pa | NMEA2000 | Coolant pressure |
| `propulsion.main.fuelRate` | Number | L/h | NMEA2000 | Fuel consumption rate |
| `propulsion.main.boost` | Number | Pa | NMEA2000 | Turbo boost pressure |
| `propulsion.main.exhaustTemperature` | Number | K | NMEA2000 | Exhaust gas temperature |

#### Electrical Data

| Path | Type | Unit | Source | Description |
|------|------|------|--------|-------------|
| `electrical.batteries.0.voltage` | Number | V | NMEA2000 | House battery voltage |
| `electrical.batteries.0.current` | Number | A | NMEA2000 | House battery current |
| `electrical.batteries.0.temperature` | Number | K | NMEA2000 | Battery temperature |
| `electrical.batteries.0.capacity.stateOfCharge` | Number | % | NMEA2000 | State of charge |
| `electrical.batteries.1.voltage` | Number | V | NMEA2000 | Starter battery voltage |

#### Tank Data

| Path | Type | Unit | Source | Description |
|------|------|------|--------|-------------|
| `tanks.fuel.0.currentLevel` | Number | ratio | NMEA2000 | Fuel tank level (0-1) |
| `tanks.fuel.0.capacity` | Number | m³ | Config | Fuel tank capacity |
| `tanks.freshWater.0.currentLevel` | Number | ratio | NMEA2000 | Fresh water level |
| `tanks.freshWater.0.capacity` | Number | m³ | Config | Fresh water capacity |
| `tanks.blackWater.0.currentLevel` | Number | ratio | NMEA2000 | Black water level |
| `tanks.blackWater.0.capacity` | Number | m³ | Config | Black water capacity |

#### Environment Data

| Path | Type | Unit | Source | Description |
|------|------|------|--------|-------------|
| `environment.depth.belowTransducer` | Number | m | NMEA2000 | Water depth |
| `environment.water.temperature` | Number | K | NMEA2000 | Water temperature |
| `environment.wind.speedApparent` | Number | m/s | NMEA2000 | Apparent wind speed |
| `environment.wind.angleApparent` | Number | rad | NMEA2000 | Apparent wind angle |
| `environment.outside.temperature` | Number | K | NMEA2000 | Outside air temperature |
| `environment.outside.pressure` | Number | Pa | NMEA2000 | Barometric pressure |

### 2.4 NMEA2000 PGN to Signal K Mapping

| PGN | Name | Signal K Path | Update Rate |
|-----|------|---------------|-------------|
| 127488 | Engine Parameters, Rapid | `propulsion.*.revolutions` | 100ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.*.temperature` | 500ms |
| 127489 | Engine Parameters, Dynamic | `propulsion.*.oilPressure` | 500ms |
| 127505 | Fluid Level | `tanks.*.currentLevel` | 2500ms |
| 127508 | Battery Status | `electrical.batteries.*.voltage` | 1500ms |
| 128259 | Speed (Water Referenced) | `navigation.speedThroughWater` | 1000ms |
| 128267 | Water Depth | `environment.depth.belowTransducer` | 1000ms |
| 129025 | Position, Rapid Update | `navigation.position` | 100ms |
| 129026 | COG & SOG, Rapid Update | `navigation.courseOverGroundTrue` | 100ms |
| 129026 | COG & SOG, Rapid Update | `navigation.speedOverGround` | 100ms |
| 129029 | GNSS Position Data | `navigation.gnss.*` | 1000ms |
| 130311 | Environmental Parameters | `environment.water.temperature` | 500ms |

### 2.5 Signal K Data Types

**Value Object**:
```json
{
  "path": "propulsion.main.revolutions",
  "value": 3200,
  "timestamp": "2026-02-06T14:30:00.000Z",
  "source": {
    "label": "NMEA2000-1",
    "type": "NMEA2000",
    "pgn": 127488,
    "src": "17"
  },
  "$source": "nmea2000-can0.17"
}
```

**Meta Object** (units, description, zones):
```json
{
  "path": "propulsion.main.revolutions",
  "value": 3200,
  "meta": {
    "units": "rpm",
    "description": "Engine revolutions per minute",
    "displayName": "Engine RPM",
    "shortName": "RPM",
    "zones": [
      {
        "lower": 0,
        "upper": 700,
        "state": "alarm",
        "message": "Engine idle too low"
      },
      {
        "lower": 700,
        "upper": 4500,
        "state": "normal"
      },
      {
        "lower": 4500,
        "upper": 5500,
        "state": "warn",
        "message": "Engine RPM high"
      },
      {
        "lower": 5500,
        "upper": 6500,
        "state": "alarm",
        "message": "Engine RPM critical - reduce throttle"
      }
    ]
  }
}
```

### 2.6 Signal K Delta Format (WebSocket)

**Delta Update**:
```json
{
  "context": "vessels.urn:mrn:signalk:uuid:abc123",
  "updates": [
    {
      "source": {
        "label": "NMEA2000-1",
        "type": "NMEA2000",
        "pgn": 127488,
        "src": "17"
      },
      "timestamp": "2026-02-06T14:30:00.000Z",
      "values": [
        {
          "path": "propulsion.main.revolutions",
          "value": 3200
        },
        {
          "path": "propulsion.main.temperature",
          "value": 353.15
        }
      ]
    }
  ]
}
```

---

## 3. CONFIGURATION DATA

### 3.1 Onboarding Configuration

**File**: `/opt/d3kos/config/onboarding.json`

```json
{
  "version": "2.0",
  "completed": true,
  "timestamp": "2026-02-06T14:30:00.000Z",
  "operator": {
    "name": "Captain John Doe",
    "email": "john@example.com",
    "phone": "+1-555-1234"
  },
  "vessel": {
    "name": "My Boat",
    "type": "powerboat",
    "hullMaterial": "fiberglass",
    "length": 35,
    "lengthUnit": "feet",
    "beam": 12,
    "draft": 3,
    "year": 2015
  },
  "engine": {
    "manufacturer": "Mercury Marine",
    "model": "MerCruiser 5.0L",
    "year": 2015,
    "serialNumber": "ABC123456",
    "cylinders": 8,
    "displacement": 5.0,
    "displacementUnit": "liters",
    "compressionRatio": 9.5,
    "strokeLength": 89,
    "strokeLengthUnit": "mm",
    "inductionType": "naturally_aspirated",
    "ratedPower": 220,
    "ratedPowerUnit": "hp",
    "idleRPM": 700,
    "wotRPMMin": 4800,
    "wotRPMMax": 5200,
    "maxCoolantTemp": 180,
    "maxCoolantTempUnit": "F",
    "minOilPressureIdle": 10,
    "minOilPressureCruise": 40,
    "oilPressureUnit": "psi",
    "fuelType": "gasoline",
    "strokeType": "4-stroke",
    "gearRatio": 1.5,
    "propellerDiameter": 15,
    "propellerPitch": 17
  },
  "cx5106": {
    "instance": 0,
    "dipSwitches": {
      "sw1": "OFF",
      "sw2": "OFF",
      "sw3": "ON",
      "sw4": "OFF",
      "sw5": "OFF",
      "sw6": "OFF",
      "sw7": "OFF",
      "sw8": "ON"
    },
    "explanation": "SW1-2: Instance 0, SW3-4: Alternator RPM, SW5-6: 8 cylinders, SW7: 4-stroke, SW8: Custom ratio (1.5:1)"
  },
  "chartplotter": {
    "present": false,
    "manufacturer": null,
    "model": null,
    "autoInstallOpenCPN": true
  },
  "installationID": "abc123def456",
  "qrCode": "d3kos://pair?id=abc123def456&version=2.0&tier=2"
}
```

### 3.2 Engine Baseline

**File**: `/opt/d3kos/config/benchmark-results.json`

```json
{
  "version": "1.0",
  "timestamp": "2026-02-06T15:00:00.000Z",
  "engineHours": 245.5,
  "duration": 1800,
  "samples": 1800,
  "conditions": {
    "airTemp": 20,
    "waterTemp": 15,
    "humidity": 65,
    "barometer": 1013.25,
    "weather": "clear"
  },
  "baseline": {
    "rpm": {
      "idle": {
        "mean": 720,
        "stddev": 15,
        "min": 690,
        "max": 750,
        "samples": 600
      },
      "cruise": {
        "mean": 3200,
        "stddev": 50,
        "min": 3100,
        "max": 3300,
        "samples": 1200
      }
    },
    "temperature": {
      "warmup": {
        "curve": [120, 130, 145, 160, 170, 175, 178, 180],
        "timeToSteadyState": 480
      },
      "steadyState": {
        "mean": 180,
        "stddev": 2,
        "min": 178,
        "max": 182,
        "unit": "F"
      }
    },
    "oilPressure": {
      "idle": {
        "mean": 12,
        "stddev": 1,
        "min": 11,
        "max": 14,
        "unit": "psi"
      },
      "cruise": {
        "mean": 45,
        "stddev": 2,
        "min": 42,
        "max": 48,
        "unit": "psi"
      }
    },
    "fuelRate": {
      "cruise": {
        "mean": 4.2,
        "stddev": 0.3,
        "min": 3.8,
        "max": 4.5,
        "unit": "gph"
      }
    },
    "voltage": {
      "charging": {
        "mean": 14.2,
        "stddev": 0.1,
        "min": 14.0,
        "max": 14.4,
        "unit": "V"
      }
    }
  },
  "notes": "Baseline established under calm sea conditions, light load"
}
```

### 3.3 License Configuration

**File**: `/opt/d3kos/config/license.json`

```json
{
  "version": "2.0",
  "tier": 2,
  "tierName": "App-Based",
  "installationID": "abc123def456",
  "installedApps": ["opencpn"],
  "resetCount": 3,
  "maxResets": -1,
  "features": {
    "voiceAssistant": true,
    "camera": true,
    "unlimitedResets": true,
    "cloudSync": false,
    "remoteAccess": false,
    "prioritySupport": false
  },
  "version": "2.0.0",
  "lastUpdateCheck": "2026-02-06T14:30:00.000Z",
  "expirationDate": null,
  "registrationDate": "2026-02-06T10:00:00.000Z"
}
```

### 3.4 Manufacturer Database

**File**: `/opt/d3kos/config/engine-manufacturers.json`

```json
{
  "manufacturers": [
    {
      "name": "Mercury Marine",
      "country": "USA",
      "models": [
        {
          "name": "MerCruiser 4.5L V6",
          "cylinders": 6,
          "displacement": 4.5,
          "displacementUnit": "L",
          "power": 250,
          "powerUnit": "hp",
          "fuelType": "gasoline",
          "strokeType": "4-stroke",
          "years": [2005, 2006, 2007, 2008, 2009, 2010]
        },
        {
          "name": "MerCruiser 5.0L V8",
          "cylinders": 8,
          "displacement": 5.0,
          "displacementUnit": "L",
          "power": 220,
          "powerUnit": "hp",
          "fuelType": "gasoline",
          "strokeType": "4-stroke",
          "years": [1995, 2000, 2005, 2010, 2015, 2020]
        }
      ]
    },
    {
      "name": "Volvo Penta",
      "country": "Sweden",
      "models": [
        {
          "name": "D4-300",
          "cylinders": 4,
          "displacement": 3.7,
          "displacementUnit": "L",
          "power": 300,
          "powerUnit": "hp",
          "fuelType": "diesel",
          "strokeType": "4-stroke",
          "inductionType": "turbocharged"
        }
      ]
    }
  ]
}
```

---

## 4. STATE MANAGEMENT

### 4.1 Reset Counter

**File**: `/opt/d3kos/state/onboarding-reset-count.json`

```json
{
  "resetCount": 7,
  "maxResets": 10,
  "lastReset": "2026-02-06T10:30:00.000Z",
  "warningsShown": [8, 9],
  "tier": 0,
  "history": [
    {
      "timestamp": "2026-02-01T09:00:00.000Z",
      "reason": "initial_setup"
    },
    {
      "timestamp": "2026-02-03T14:20:00.000Z",
      "reason": "configuration_error"
    },
    {
      "timestamp": "2026-02-06T10:30:00.000Z",
      "reason": "engine_change"
    }
  ]
}
```

### 4.2 System Health Status

**File**: `/opt/d3kos/state/pi-health-status.json`

```json
{
  "timestamp": "2026-02-06T14:30:00.000Z",
  "uptime": 259200,
  "cpu": {
    "temperature": 65.3,
    "temperatureUnit": "C",
    "usage": 45.2,
    "usageUnit": "%",
    "frequency": 1500,
    "frequencyUnit": "MHz",
    "throttled": false
  },
  "memory": {
    "total": 4096,
    "used": 2560,
    "free": 1536,
    "unit": "MB",
    "usage": 62.5,
    "usageUnit": "%"
  },
  "storage": {
    "total": 64,
    "used": 27,
    "free": 37,
    "unit": "GB",
    "usage": 42.2,
    "usageUnit": "%"
  },
  "gpu": {
    "temperature": 58.0,
    "temperatureUnit": "C"
  },
  "network": {
    "wlan0": {
      "status": "up",
      "ipAddress": "10.42.0.1",
      "clients": 3
    },
    "eth0": {
      "status": "up",
      "ipAddress": "192.168.1.100",
      "internet": true
    },
    "can0": {
      "status": "up",
      "bitrate": 250000,
      "devices": 5
    }
  },
  "services": {
    "signalk": "active",
    "nodered": "active",
    "gpsd": "active",
    "helm-voice": "active",
    "helm-camera": "inactive",
    "d3kos-health": "active"
  }
}
```

---

## 5. HISTORICAL DATA

### 5.1 SQLite Database Schema

**Database**: `/opt/d3kos/data/historical.db`

#### Table: engine_metrics

```sql
CREATE TABLE engine_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    engine_hours REAL,
    rpm INTEGER,
    oil_pressure REAL,
    oil_pressure_unit TEXT DEFAULT 'psi',
    coolant_temp REAL,
    coolant_temp_unit TEXT DEFAULT 'F',
    fuel_rate REAL,
    fuel_rate_unit TEXT DEFAULT 'gph',
    voltage REAL,
    voltage_unit TEXT DEFAULT 'V',
    boost_pressure REAL,
    exhaust_temp REAL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_engine_hours (engine_hours)
);
```

#### Table: anomalies

```sql
CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT CHECK(level IN ('INFO', 'WARNING', 'CRITICAL')),
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    baseline_value REAL,
    deviation REAL,
    sigma REAL,
    message TEXT,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at DATETIME,
    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level),
    INDEX idx_metric (metric)
);
```

#### Table: boat_log

```sql
CREATE TABLE boat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entry TEXT NOT NULL,
    audio_file TEXT,
    transcription TEXT,
    location_lat REAL,
    location_lon REAL,
    engine_hours REAL,
    tags TEXT,
    INDEX idx_timestamp (timestamp)
);
```

#### Table: system_metrics

```sql
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_temp REAL,
    cpu_usage REAL,
    memory_usage REAL,
    storage_free REAL,
    gpu_temp REAL,
    throttled BOOLEAN,
    uptime INTEGER,
    INDEX idx_timestamp (timestamp)
);
```

#### Table: navigation_log

```sql
CREATE TABLE navigation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    latitude REAL,
    longitude REAL,
    speed_over_ground REAL,
    course_over_ground REAL,
    heading REAL,
    depth REAL,
    INDEX idx_timestamp (timestamp)
);
```

### 5.2 Data Insertion Examples

**Insert Engine Metric**:
```sql
INSERT INTO engine_metrics (
    timestamp, engine_hours, rpm, oil_pressure,
    coolant_temp, fuel_rate, voltage
) VALUES (
    '2026-02-06 14:30:00', 245.5, 3200, 45,
    180, 4.2, 14.2
);
```

**Insert Anomaly**:
```sql
INSERT INTO anomalies (
    timestamp, level, metric, value,
    baseline_value, deviation, sigma, message
) VALUES (
    '2026-02-06 14:30:00', 'WARNING', 'oil_pressure', 35,
    45, -10, 2.5, 'Oil pressure 10 PSI below baseline (2.5σ)'
);
```

**Insert Boat Log Entry**:
```sql
INSERT INTO boat_log (
    timestamp, entry, transcription,
    location_lat, location_lon, engine_hours
) VALUES (
    '2026-02-06 14:30:00',
    'Noticed slight vibration at 3000 RPM',
    'Noticed slight vibration at 3000 RPM',
    45.5231, -122.6765, 245.5
);
```

### 5.3 Query Examples

**Get Last 24 Hours of Engine Data**:
```sql
SELECT
    timestamp,
    rpm,
    oil_pressure,
    coolant_temp,
    fuel_rate
FROM engine_metrics
WHERE timestamp >= datetime('now', '-24 hours')
ORDER BY timestamp DESC;
```

**Get All Critical Anomalies (Unacknowledged)**:
```sql
SELECT
    timestamp,
    metric,
    value,
    baseline_value,
    message
FROM anomalies
WHERE level = 'CRITICAL'
  AND acknowledged = 0
ORDER BY timestamp DESC;
```

**Get Average RPM by Hour (Last 7 Days)**:
```sql
SELECT
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    AVG(rpm) as avg_rpm,
    MIN(rpm) as min_rpm,
    MAX(rpm) as max_rpm,
    COUNT(*) as samples
FROM engine_metrics
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY hour
ORDER BY hour DESC;
```

---

## 6. FILE STORAGE

### 6.1 Boat Log (Text Format)

**File**: `/opt/d3kos/data/boat-log.txt`

**Format**: Plain text, one entry per line

```
2026-02-06 10:00:00 | Engine Hours: 245.0 | Pos: 45.5231,-122.6765 | Starting engine for morning run
2026-02-06 10:15:00 | Engine Hours: 245.1 | Pos: 45.5245,-122.6780 | Reached cruising speed, 3200 RPM
2026-02-06 11:30:00 | Engine Hours: 246.3 | Pos: 45.5890,-122.7120 | Noticed slight vibration at 3000 RPM
2026-02-06 12:00:00 | Engine Hours: 246.8 | Pos: 45.5231,-122.6765 | Returned to dock, engine running smoothly
```

**Entry Format**:
```
YYYY-MM-DD HH:MM:SS | Engine Hours: <hours> | Pos: <lat>,<lon> | <entry text>
```

### 6.2 Camera Recordings

**Directory**: `/opt/d3kos/data/camera/`

**File Naming**: `YYYYMMDD_HHMMSS_camera.mp4`

**Examples**:
```
20260206_100000_camera.mp4  (10:00:00 AM)
20260206_101000_camera.mp4  (10:10:00 AM, 10-minute segment)
20260206_102000_camera.mp4  (10:20:00 AM)
```

**Metadata** (sidecar JSON):
```json
{
  "filename": "20260206_100000_camera.mp4",
  "startTime": "2026-02-06T10:00:00.000Z",
  "endTime": "2026-02-06T10:10:00.000Z",
  "duration": 600,
  "size": 52428800,
  "resolution": "1920x1080",
  "fps": 30,
  "codec": "H.264",
  "location": {
    "latitude": 45.5231,
    "longitude": -122.6765
  }
}
```

### 6.3 Voice Recordings (Temporary)

**Directory**: `/opt/d3kos/data/voice/`

**File Naming**: `recording_<timestamp>.wav`

**Format**: WAV, 16kHz, 16-bit, mono

**Lifecycle**:
1. Recorded during voice assistant interaction
2. Transcribed by Vosk STT
3. Deleted immediately after transcription
4. Never persisted (privacy)

### 6.4 Exported Data

**Directory**: `/opt/d3kos/data/exports/`

**CSV Export Example** (`engine_data_202602.csv`):
```csv
timestamp,engine_hours,rpm,oil_pressure,coolant_temp,fuel_rate,voltage
2026-02-06 10:00:00,245.0,700,12,120,0.8,14.2
2026-02-06 10:00:01,245.0,720,12,121,0.8,14.2
2026-02-06 10:00:02,245.0,740,13,122,0.9,14.2
...
```

**JSON Configuration Export** (`d3kos-config.json`):
```json
{
  "exported": "2026-02-06T14:30:00.000Z",
  "version": "2.0",
  "onboarding": { ... },
  "baseline": { ... },
  "license": { ... }
}
```

---

## 7. DATA FLOW

### 7.1 Real-Time Engine Data Flow

```
NMEA2000 Bus (PGN 127488, RPM=3200)
         ↓
  PiCAN-M HAT (CAN frame decode)
         ↓
  SocketCAN (can0 interface)
         ↓
  Signal K Server (actisense plugin)
         ↓ Convert to Signal K format
  WebSocket (ws://localhost:3000)
         ↓ Broadcast delta update
  Node-RED (signalk-in node)
         ↓ Process & threshold check
  [Function Node: Anomaly Detection]
         ↓
  ┌──────┴──────┐
  ▼             ▼
Dashboard   SQLite DB
Gauge       (historical.db)
(1Hz)       (1Hz insert)
```

### 7.2 Voice Assistant Data Flow

```
Microphone (16kHz audio)
         ↓
  [Wake Word Detection: PocketSphinx]
         ↓ "Helm" detected
  [STT: Vosk]
         ↓ Transcription
  "What's the engine status?"
         ↓
  [Command Parser]
         ↓
  ┌──────┴──────┐
  ▼             ▼
[Phi-2 LLM]   [Direct Query]
(general Q)   (specific command)
  │             │
  └──────┬──────┘
         ▼
  [Response Generator]
         ↓
  "Engine running at 3200 RPM, all systems normal"
         ↓
  [TTS: Piper]
         ↓
  Speaker (audio output)
```

### 7.3 Camera Recording Data Flow

```
Reolink Camera (RTSP stream)
         ↓
  rtsp://192.168.1.100:554/h264Preview_01_main
         ↓
  [VLC libvlc: Stream Capture]
         ↓ H.264 video
  [Storage Check: > 18% free?]
         ↓ YES
  [Segmenter: 10-minute chunks]
         ↓
  /opt/d3kos/data/camera/YYYYMMDD_HHMMSS_camera.mp4
         ↓
  [FIFO Cleanup: if disk < 18%]
         ↓
  Delete oldest recordings
```

### 7.4 Anomaly Detection Flow

```
Current Engine Metrics (from Signal K)
         ↓
  {rpm: 3200, oilPressure: 35, temp: 180}
         ↓
  [Load Baseline]
         ↓
  baseline-results.json
  {rpm: {mean: 3200, stddev: 50}, oilPressure: {mean: 45, stddev: 2}}
         ↓
  [Calculate Deviation]
         ↓
  oilPressure: 35 vs 45 baseline → -10 PSI deviation
  sigma = deviation / stddev = 10 / 2 = 5σ
         ↓
  [Classify]
         ↓
  σ > 3 → CRITICAL
         ↓
  [Insert Anomaly Record]
         ↓
  SQLite: anomalies table
         ↓
  [Trigger Alert]
         ├─ Visual: Dashboard red gauge
         └─ Voice: "Oil pressure critical, 10 PSI below normal"
```

---

## 8. API DATA FORMATS

### 8.1 Signal K REST API

**Base URL**: `http://localhost:3000/signalk/v1/api/`

**Get Single Value**:
```
GET /signalk/v1/api/vessels/self/propulsion/main/revolutions

Response:
{
  "path": "propulsion.main.revolutions",
  "value": 3200,
  "timestamp": "2026-02-06T14:30:00.000Z",
  "$source": "nmea2000-can0.17",
  "source": {
    "label": "NMEA2000-1",
    "type": "NMEA2000",
    "pgn": 127488,
    "src": "17"
  }
}
```

**Get Multiple Values**:
```
GET /signalk/v1/api/vessels/self/propulsion/main

Response:
{
  "revolutions": {
    "value": 3200,
    "timestamp": "2026-02-06T14:30:00.000Z"
  },
  "temperature": {
    "value": 353.15,
    "timestamp": "2026-02-06T14:30:00.000Z"
  },
  "oilPressure": {
    "value": 310264,
    "timestamp": "2026-02-06T14:30:00.000Z"
  }
}
```

### 8.2 d3kOS Custom API

**Base URL**: `http://localhost/api/`

**Get System Health**:
```
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "2026-02-06T14:30:00.000Z",
  "cpu": {
    "temperature": 65.3,
    "usage": 45.2,
    "throttled": false
  },
  "memory": {
    "total": 4096,
    "used": 2560,
    "free": 1536,
    "usage": 62.5
  },
  "storage": {
    "total": 64,
    "used": 27,
    "free": 37,
    "usage": 42.2
  }
}
```

**Get Engine Baseline**:
```
GET /api/engine/baseline

Response:
{
  "version": "1.0",
  "timestamp": "2026-02-06T15:00:00.000Z",
  "engineHours": 245.5,
  "baseline": { ... }
}
```

**Get Current Engine Status**:
```
GET /api/engine/current

Response:
{
  "timestamp": "2026-02-06T14:30:00.000Z",
  "engineHours": 245.5,
  "metrics": {
    "rpm": 3200,
    "oilPressure": 45,
    "coolantTemp": 180,
    "fuelRate": 4.2,
    "voltage": 14.2
  },
  "status": "normal",
  "anomalies": []
}
```

**Start Engine Benchmark**:
```
POST /api/engine/benchmark/start

Request Body:
{
  "duration": 1800
}

Response:
{
  "status": "started",
  "startTime": "2026-02-06T14:30:00.000Z",
  "estimatedCompletion": "2026-02-06T15:00:00.000Z",
  "duration": 1800
}
```

### 8.3 WebSocket Data Format

**Node-RED Dashboard WebSocket**:

```javascript
// Connect
const ws = new WebSocket('ws://localhost:1880/ws/dashboard');

// Receive gauge update
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  // {
  //   "topic": "rpm",
  //   "payload": 3200,
  //   "timestamp": "2026-02-06T14:30:00.000Z"
  // }
};

// Send command
ws.send(JSON.stringify({
  topic: "command",
  payload: "start_recording"
}));
```

---

## 9. DATA RETENTION POLICIES

### 9.1 Retention by Data Type

| Data Type | Tier 0 | Tier 2 | Tier 3 | Auto-Delete |
|-----------|--------|--------|--------|-------------|
| **Configuration** | Permanent | Permanent | Permanent | Never |
| **Engine Baseline** | Permanent | Permanent | Permanent | Never |
| **Boat Log** | 30 days | Unlimited | Unlimited | After limit |
| **Historical Metrics** | 30 days | 90 days | 90 days | After limit |
| **Anomaly Log** | 90 days | Unlimited | Unlimited | After limit |
| **System Metrics** | 7 days | 30 days | 30 days | After limit |
| **Camera Recordings** | Until disk full | Until disk full | Until disk full | FIFO at 18% |
| **Voice Recordings** | Immediate | Immediate | Immediate | After STT |
| **Application Logs** | 7 days | 30 days | 30 days | Rotated |

### 9.2 Auto-Cleanup Implementation

**Cleanup Script** (`/opt/d3kos/scripts/data-cleanup.sh`):

```bash
#!/bin/bash
# Run daily via cron: 0 2 * * * /opt/d3kos/scripts/data-cleanup.sh

TIER=$(jq -r '.tier' /opt/d3kos/config/license.json)

# Cleanup boat log
if [ "$TIER" -eq 0 ]; then
    # Tier 0: Keep 30 days
    find /opt/d3kos/data -name "boat-log.txt" -mtime +30 -exec truncate -s 0 {} \;
fi

# Cleanup historical metrics
if [ "$TIER" -eq 0 ]; then
    # Tier 0: Delete > 30 days
    sqlite3 /opt/d3kos/data/historical.db \
        "DELETE FROM engine_metrics WHERE timestamp < datetime('now', '-30 days');"
    sqlite3 /opt/d3kos/data/historical.db \
        "DELETE FROM system_metrics WHERE timestamp < datetime('now', '-7 days');"
elif [ "$TIER" -ge 2 ]; then
    # Tier 2+: Delete > 90 days
    sqlite3 /opt/d3kos/data/historical.db \
        "DELETE FROM engine_metrics WHERE timestamp < datetime('now', '-90 days');"
    sqlite3 /opt/d3kos/data/historical.db \
        "DELETE FROM system_metrics WHERE timestamp < datetime('now', '-30 days');"
fi

# Cleanup camera recordings (all tiers: FIFO at 18% disk free)
DISK_FREE=$(df -h /opt/d3kos/data | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_FREE" -gt 82 ]; then  # 82% used = 18% free
    # Delete oldest 10 recordings
    ls -t /opt/d3kos/data/camera/*.mp4 | tail -10 | xargs rm -f
fi

# Cleanup voice recordings (immediate delete, should be none)
find /opt/d3kos/data/voice -name "*.wav" -mtime +0 -delete

# Cleanup application logs
find /opt/d3kos/logs -name "*.log" -mtime +30 -delete

# Vacuum SQLite database
sqlite3 /opt/d3kos/data/historical.db "VACUUM;"

echo "Cleanup completed: $(date)"
```

---

## 10. DATABASE SCHEMAS

### 10.1 Schema Version Management

**Migrations Directory**: `/opt/d3kos/db/migrations/`

**Migration 001** (`001_initial_schema.sql`):
```sql
-- Migration 001: Initial schema
-- Date: 2026-02-06
-- Author: d3kOS Team

CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description)
VALUES (1, 'Initial schema');

CREATE TABLE engine_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    engine_hours REAL,
    rpm INTEGER,
    oil_pressure REAL,
    coolant_temp REAL,
    fuel_rate REAL,
    voltage REAL,
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT CHECK(level IN ('INFO', 'WARNING', 'CRITICAL')),
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    baseline_value REAL,
    deviation REAL,
    sigma REAL,
    message TEXT,
    acknowledged BOOLEAN DEFAULT 0,
    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level)
);

CREATE TABLE boat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entry TEXT NOT NULL,
    audio_file TEXT,
    transcription TEXT,
    location_lat REAL,
    location_lon REAL,
    engine_hours REAL,
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_temp REAL,
    cpu_usage REAL,
    memory_usage REAL,
    storage_free REAL,
    INDEX idx_timestamp (timestamp)
);
```

**Apply Migration Script** (`/opt/d3kos/scripts/migrate.sh`):
```bash
#!/bin/bash
# Apply database migrations

DB="/opt/d3kos/data/historical.db"
MIGRATIONS_DIR="/opt/d3kos/db/migrations"

# Get current version
CURRENT_VERSION=$(sqlite3 $DB "SELECT MAX(version) FROM schema_version;" 2>/dev/null || echo 0)

echo "Current schema version: $CURRENT_VERSION"

# Apply migrations
for migration in $(ls $MIGRATIONS_DIR/*.sql | sort); do
    MIGRATION_VERSION=$(basename $migration | cut -d'_' -f1)

    if [ "$MIGRATION_VERSION" -gt "$CURRENT_VERSION" ]; then
        echo "Applying migration $MIGRATION_VERSION..."
        sqlite3 $DB < $migration
        echo "Migration $MIGRATION_VERSION applied successfully"
    fi
done

echo "Database up to date"
```

### 10.2 Database Indexes

**Performance Indexes**:
```sql
-- Engine metrics time-series queries
CREATE INDEX idx_engine_timestamp ON engine_metrics(timestamp DESC);
CREATE INDEX idx_engine_hours ON engine_metrics(engine_hours);

-- Anomaly filtering
CREATE INDEX idx_anomaly_timestamp ON anomalies(timestamp DESC);
CREATE INDEX idx_anomaly_level ON anomalies(level);
CREATE INDEX idx_anomaly_metric ON anomalies(metric);
CREATE INDEX idx_anomaly_acknowledged ON anomalies(acknowledged);

-- Boat log search
CREATE INDEX idx_boatlog_timestamp ON boat_log(timestamp DESC);
CREATE VIRTUAL TABLE boat_log_fts USING fts5(entry, transcription);

-- System metrics
CREATE INDEX idx_system_timestamp ON system_metrics(timestamp DESC);
```

### 10.3 Database Maintenance

**Optimize Database** (run weekly):
```sql
-- Analyze tables for query optimization
ANALYZE;

-- Rebuild indexes
REINDEX;

-- Reclaim unused space
VACUUM;

-- Update statistics
ANALYZE sqlite_master;
```

---

## APPENDIX A: Data Type Conversions

### A.1 Unit Conversions

| From | To | Formula | Example |
|------|----|---------| --------|
| Kelvin (K) | Fahrenheit (°F) | (K - 273.15) × 9/5 + 32 | 353.15 K = 176°F |
| Kelvin (K) | Celsius (°C) | K - 273.15 | 353.15 K = 80°C |
| Pascal (Pa) | PSI | Pa / 6894.76 | 310264 Pa = 45 PSI |
| Pascal (Pa) | Bar | Pa / 100000 | 310264 Pa = 3.1 bar |
| Radians (rad) | Degrees (°) | rad × 180 / π | 0.785 rad = 45° |
| m/s | Knots | m/s × 1.94384 | 5 m/s = 9.72 knots |
| m/s | MPH | m/s × 2.23694 | 5 m/s = 11.18 mph |
| Liters (L) | Gallons (gal) | L × 0.264172 | 20 L = 5.28 gal |
| Liters/hour | Gallons/hour | L/h × 0.264172 | 16 L/h = 4.23 gph |

### A.2 Signal K Unit Standards

All Signal K values use SI units:
- Temperature: Kelvin (K)
- Pressure: Pascal (Pa)
- Speed: meters/second (m/s)
- Angle: Radians (rad)
- Volume: Cubic meters (m³)
- Distance: Meters (m)

**Convert for Display**:
```javascript
// Temperature K → °F
const tempF = (tempK - 273.15) * 9/5 + 32;

// Pressure Pa → PSI
const pressurePSI = pressurePa / 6894.76;

// Speed m/s → knots
const speedKnots = speedMS * 1.94384;
```

---

## APPENDIX B: Sample Queries

### B.1 Performance Analysis

**Average RPM by Day**:
```sql
SELECT
    DATE(timestamp) as date,
    AVG(rpm) as avg_rpm,
    MIN(rpm) as min_rpm,
    MAX(rpm) as max_rpm,
    COUNT(*) as samples
FROM engine_metrics
WHERE timestamp >= datetime('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

**Fuel Consumption Trends**:
```sql
SELECT
    strftime('%Y-%m', timestamp) as month,
    SUM(fuel_rate * (1.0/3600)) as total_fuel_gallons,
    AVG(fuel_rate) as avg_fuel_rate
FROM engine_metrics
WHERE fuel_rate > 0
GROUP BY month
ORDER BY month DESC;
```

**Anomaly Frequency**:
```sql
SELECT
    metric,
    level,
    COUNT(*) as occurrences,
    MIN(timestamp) as first_occurrence,
    MAX(timestamp) as last_occurrence
FROM anomalies
WHERE timestamp >= datetime('now', '-30 days')
GROUP BY metric, level
ORDER BY occurrences DESC;
```

### B.2 Maintenance Reports

**Engine Hours Summary**:
```sql
SELECT
    MIN(engine_hours) as start_hours,
    MAX(engine_hours) as current_hours,
    MAX(engine_hours) - MIN(engine_hours) as hours_logged,
    COUNT(*) as data_points
FROM engine_metrics
WHERE timestamp >= datetime('now', '-30 days');
```

**Oil Pressure Degradation**:
```sql
SELECT
    DATE(timestamp) as date,
    AVG(oil_pressure) as avg_oil_pressure,
    MIN(oil_pressure) as min_oil_pressure
FROM engine_metrics
WHERE timestamp >= datetime('now', '-90 days')
  AND rpm BETWEEN 3000 AND 3400
GROUP BY DATE(timestamp)
ORDER BY date ASC;
```

---

**END OF DATA MODEL SPECIFICATION**
