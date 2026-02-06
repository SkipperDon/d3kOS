# HELM-OS NODE-RED FLOWS

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0
**Audience**: Developers

---

## TABLE OF CONTENTS

1. [Node-RED Overview](#node-red-overview)
2. [Dashboard Configuration](#dashboard-configuration)
3. [Flow Architecture](#flow-architecture)
4. [Core Flows](#core-flows)
5. [Gauge Implementations](#gauge-implementations)
6. [Data Processing](#data-processing)
7. [Alert System](#alert-system)
8. [WebSocket Communication](#websocket-communication)
9. [Custom Nodes](#custom-nodes)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 1. NODE-RED OVERVIEW

### 1.1 Node-RED in Helm-OS

Node-RED serves as the **automation and visualization engine** for Helm-OS:
- **Data Flow**: Processes Signal K data streams
- **Dashboard**: Provides real-time gauges and charts
- **Automation**: Triggers alerts and actions based on conditions
- **Integration**: Connects Signal K, SQLite, file system, and services

**Version**: Node-RED 3.x with Dashboard 2.0

### 1.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  NODE-RED RUNTIME                    │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Signal K  │→ │ Processing │→ │ Dashboard  │   │
│  │   Input    │  │   Flows    │  │  Output    │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│         ↓              ↓              ↓            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Storage   │  │   Alerts   │  │    API     │   │
│  │  (SQLite)  │  │  (Voice)   │  │(WebSocket) │   │
│  └────────────┘  └────────────┘  └────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 1.3 File Locations

```
/home/pi/.node-red/
├── settings.js              # Node-RED configuration
├── flows.json               # Main flow definitions
├── flows_cred.json          # Encrypted credentials
├── package.json             # Installed nodes
├── node_modules/            # Node.js dependencies
└── lib/                     # Custom function libraries
    ├── utils.js
    ├── conversions.js
    └── anomaly_detector.js
```

---

## 2. DASHBOARD CONFIGURATION

### 2.1 Dashboard 2.0 Setup

**Installation**:
```bash
cd ~/.node-red
npm install @flowfuse/node-red-dashboard
```

**Configuration** (in `settings.js`):
```javascript
module.exports = {
    uiPort: 1880,
    uiHost: "0.0.0.0",

    // Dashboard 2.0 settings
    ui: {
        path: "dashboard",
        middleware: function(req, res, next) {
            // Add custom middleware here
            next();
        }
    },

    // AODA compliance
    dashboardSettings: {
        theme: {
            name: "dark-helm",
            colors: {
                primary: "#00CC00",
                bgPage: "#000000",
                bgCard: "#1a1a1a",
                textPrimary: "#FFFFFF",
                textSecondary: "#CCCCCC"
            },
            sizes: {
                pagePadding: "16px",
                groupGap: "16px",
                widgetGap: "20px",
                density: "comfortable"
            }
        }
    }
}
```

### 2.2 Dashboard Layout

**Page Structure**:
```javascript
// Dashboard 2.0 page configuration
{
    "pages": [
        {
            "id": "page_engine",
            "name": "Engine & System",
            "path": "/dashboard/engine",
            "icon": "mdi-engine",
            "layout": "grid",
            "groups": [
                {
                    "id": "group_engine_gauges",
                    "name": "Engine Gauges",
                    "width": "12",
                    "widgets": ["rpm", "temp", "pressure", "voltage", "trim"]
                },
                {
                    "id": "group_tanks",
                    "name": "Tank Levels",
                    "width": "12",
                    "widgets": ["fuel", "fresh", "black", "battery"]
                },
                {
                    "id": "group_system",
                    "name": "System Status",
                    "width": "12",
                    "widgets": ["cpu", "memory", "storage", "gpu"]
                },
                {
                    "id": "group_network",
                    "name": "Network Status",
                    "width": "12",
                    "widgets": ["wifi", "ethernet", "nmea", "internet"]
                }
            ]
        },
        {
            "id": "page_log",
            "name": "Boat Log",
            "path": "/dashboard/log",
            "icon": "mdi-notebook"
        },
        {
            "id": "page_health",
            "name": "Health Reports",
            "path": "/dashboard/health",
            "icon": "mdi-heart-pulse"
        }
    ]
}
```

### 2.3 Widget Configuration

**Base Widget Properties**:
```javascript
{
    "id": "widget_rpm",
    "type": "ui-gauge",
    "name": "Engine RPM",
    "group": "group_engine_gauges",
    "width": 4,
    "height": 4,
    "min": 0,
    "max": 6000,
    "segments": [
        {"from": 0, "color": "#FF0000"},      // Red: 0-700 (too low)
        {"from": 700, "color": "#00CC00"},     // Green: 700-4500 (normal)
        {"from": 4500, "color": "#FFA500"},    // Amber: 4500-5500 (caution)
        {"from": 5500, "color": "#FF0000"}     // Red: 5500+ (critical)
    ],
    "units": "RPM",
    "label": "Engine",
    "style": {
        "fontSize": "24px",
        "fontWeight": "bold"
    }
}
```

---

## 3. FLOW ARCHITECTURE

### 3.1 Main Flow Structure

```
┌──────────────────────────────────────────────────────┐
│                    INPUT FLOWS                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ Signal K   │  │   GPSd     │  │  System    │    │
│  │ WebSocket  │  │   Input    │  │  Metrics   │    │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘    │
└─────────┼────────────────┼────────────────┼──────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼──────────┐
│                 PROCESSING FLOWS                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │   Unit     │  │ Threshold  │  │  Anomaly   │    │
│  │Conversion  │  │   Check    │  │ Detection  │    │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘    │
└─────────┼────────────────┼────────────────┼──────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼──────────┐
│                   OUTPUT FLOWS                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ Dashboard  │  │  Storage   │  │   Alerts   │    │
│  │  Gauges    │  │  (SQLite)  │  │  (Voice)   │    │
│  └────────────┘  └────────────┘  └────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 3.2 Flow Organization

**Tab Structure**:
1. **Input** - Signal K, GPS, system metrics collection
2. **Engine** - Engine data processing and gauges
3. **Tanks** - Tank level monitoring
4. **System** - Raspberry Pi health monitoring
5. **Network** - Network status monitoring
6. **Anomaly** - Anomaly detection and alerts
7. **Storage** - Database logging
8. **Dashboard** - UI elements and interactions

---

## 4. CORE FLOWS

### 4.1 Signal K Input Flow

**Purpose**: Subscribe to Signal K WebSocket and parse marine data

**Flow JSON**:
```json
[
    {
        "id": "signalk_input",
        "type": "websocket in",
        "name": "Signal K WS",
        "server": "signalk_server",
        "client": "",
        "x": 100,
        "y": 100,
        "wires": [["parse_signalk"]]
    },
    {
        "id": "signalk_server",
        "type": "websocket-client",
        "path": "ws://localhost:3000/signalk/v1/stream",
        "wholemsg": "true"
    },
    {
        "id": "parse_signalk",
        "type": "function",
        "name": "Parse Signal K Delta",
        "func": "// Parse Signal K delta format\nconst delta = JSON.parse(msg.payload);\n\nif (!delta.updates) {\n    return null;\n}\n\nconst results = [];\n\nfor (const update of delta.updates) {\n    for (const value of update.values) {\n        results.push({\n            payload: value.value,\n            topic: value.path,\n            timestamp: update.timestamp\n        });\n    }\n}\n\nreturn [results];",
        "outputs": 1,
        "x": 300,
        "y": 100,
        "wires": [["route_by_path"]]
    },
    {
        "id": "route_by_path",
        "type": "switch",
        "name": "Route by Path",
        "property": "topic",
        "rules": [
            {"t": "cont", "v": "propulsion.main.", "vt": "str"},
            {"t": "cont", "v": "electrical.batteries.", "vt": "str"},
            {"t": "cont", "v": "tanks.", "vt": "str"},
            {"t": "cont", "v": "navigation.", "vt": "str"}
        ],
        "x": 500,
        "y": 100,
        "wires": [
            ["engine_processing"],
            ["electrical_processing"],
            ["tank_processing"],
            ["navigation_processing"]
        ]
    }
]
```

### 4.2 Engine RPM Flow

**Purpose**: Process engine RPM, convert units, check thresholds, update gauge

**Flow Diagram**:
```
[Signal K: propulsion.main.revolutions]
         ↓
   [Convert units if needed]
         ↓
   [Threshold check]
    ↓       ↓
[Gauge]  [Anomaly detector]
    ↓       ↓
[SQLite] [Voice alert]
```

**Flow JSON**:
```json
[
    {
        "id": "rpm_input",
        "type": "link in",
        "name": "RPM Input",
        "links": ["engine_processing"],
        "x": 100,
        "y": 200,
        "wires": [["rpm_extract"]]
    },
    {
        "id": "rpm_extract",
        "type": "function",
        "name": "Extract RPM",
        "func": "// Extract RPM value\nif (msg.topic === 'propulsion.main.revolutions') {\n    msg.payload = Math.round(msg.payload);\n    msg.topic = 'rpm';\n    return msg;\n}\nreturn null;",
        "outputs": 1,
        "x": 300,
        "y": 200,
        "wires": [["rpm_threshold", "rpm_gauge", "rpm_store"]]
    },
    {
        "id": "rpm_threshold",
        "type": "function",
        "name": "Check Thresholds",
        "func": "const rpm = msg.payload;\nconst baseline = global.get('baseline') || {};\nconst rpmBaseline = baseline.rpm?.cruise?.mean || 3200;\nconst rpmStddev = baseline.rpm?.cruise?.stddev || 50;\n\nconst deviation = Math.abs(rpm - rpmBaseline);\nconst sigma = deviation / rpmStddev;\n\nif (sigma > 3) {\n    msg.level = 'CRITICAL';\n    msg.message = `RPM ${rpm} is ${deviation.toFixed(0)} above/below baseline (${sigma.toFixed(1)}σ)`;\n    return [msg, null, null];\n} else if (sigma > 2) {\n    msg.level = 'WARNING';\n    msg.message = `RPM ${rpm} is ${deviation.toFixed(0)} above/below baseline (${sigma.toFixed(1)}σ)`;\n    return [null, msg, null];\n} else {\n    msg.level = 'NORMAL';\n    return [null, null, msg];\n}",
        "outputs": 3,
        "x": 500,
        "y": 200,
        "wires": [
            ["critical_alert"],
            ["warning_log"],
            []
        ]
    },
    {
        "id": "rpm_gauge",
        "type": "ui-gauge",
        "name": "RPM Gauge",
        "group": "group_engine_gauges",
        "min": 0,
        "max": 6000,
        "segments": [
            {"from": 0, "color": "#FF0000"},
            {"from": 700, "color": "#00CC00"},
            {"from": 4500, "color": "#FFA500"},
            {"from": 5500, "color": "#FF0000"}
        ],
        "units": "RPM",
        "x": 500,
        "y": 250,
        "wires": []
    },
    {
        "id": "rpm_store",
        "type": "function",
        "name": "Store to DB",
        "func": "// Store RPM to SQLite\nconst timestamp = new Date().toISOString();\nconst rpm = msg.payload;\n\nmsg.topic = `INSERT INTO engine_metrics (timestamp, rpm) VALUES ('${timestamp}', ${rpm})`;\n\nreturn msg;",
        "outputs": 1,
        "x": 500,
        "y": 300,
        "wires": [["sqlite_insert"]]
    }
]
```

### 4.3 Temperature Conversion Flow

**Purpose**: Convert temperature from Kelvin (Signal K) to Fahrenheit (display)

**Function Node**:
```javascript
// Temperature conversion: K → °F
const tempK = msg.payload;

if (typeof tempK === 'number' && tempK > 0) {
    const tempF = (tempK - 273.15) * 9/5 + 32;
    msg.payload = Math.round(tempF);
    msg.topic = 'coolant_temp_f';
    msg.unit = '°F';
    return msg;
}

return null;
```

### 4.4 Oil Pressure Conversion Flow

**Purpose**: Convert pressure from Pascal (Signal K) to PSI (display)

**Function Node**:
```javascript
// Pressure conversion: Pa → PSI
const pressurePa = msg.payload;

if (typeof pressurePa === 'number' && pressurePa > 0) {
    const pressurePSI = pressurePa / 6894.76;
    msg.payload = Math.round(pressurePSI);
    msg.topic = 'oil_pressure_psi';
    msg.unit = 'PSI';
    return msg;
}

return null;
```

---

## 5. GAUGE IMPLEMENTATIONS

### 5.1 Circular Gauge (Tachometer)

**Configuration**:
```json
{
    "id": "gauge_rpm",
    "type": "ui-gauge",
    "name": "Tachometer",
    "group": "group_engine_gauges",
    "order": 1,
    "width": 4,
    "height": 4,
    "gaugetype": "donut",
    "min": 0,
    "max": 6000,
    "segments": [
        {"from": 0, "to": 700, "color": "#FF0000", "label": "Low"},
        {"from": 700, "to": 4500, "color": "#00CC00", "label": "Normal"},
        {"from": 4500, "to": 5500, "color": "#FFA500", "label": "High"},
        {"from": 5500, "to": 6000, "color": "#FF0000", "label": "Critical"}
    ],
    "units": "RPM",
    "label": "Engine",
    "style": {
        "arc": 270,
        "needle": true,
        "needleColor": "#FFFFFF",
        "fontSize": "32px",
        "fontWeight": "bold"
    }
}
```

### 5.2 Linear Gauge (Fuel Level)

**Configuration**:
```json
{
    "id": "gauge_fuel",
    "type": "ui-slider",
    "name": "Fuel Level",
    "group": "group_tanks",
    "order": 1,
    "width": 6,
    "height": 2,
    "min": 0,
    "max": 100,
    "step": 1,
    "orientation": "horizontal",
    "disabled": true,
    "showTicks": true,
    "thumbLabel": "always",
    "color": {
        "gradient": true,
        "stops": [
            {"value": 0, "color": "#FF0000"},
            {"value": 25, "color": "#FFA500"},
            {"value": 50, "color": "#FFFF00"},
            {"value": 100, "color": "#00CC00"}
        ]
    },
    "units": "%",
    "label": "Fuel"
}
```

**Processing Function**:
```javascript
// Convert fuel level from ratio (0-1) to percentage
const fuelRatio = msg.payload;

if (typeof fuelRatio === 'number') {
    msg.payload = Math.round(fuelRatio * 100);
    msg.topic = 'fuel_percent';

    // Calculate gallons if capacity known
    const tankCapacity = global.get('tank_capacity') || 50; // gallons
    msg.gallons = Math.round(fuelRatio * tankCapacity);

    return msg;
}

return null;
```

### 5.3 Status Indicator (Network)

**Configuration**:
```json
{
    "id": "status_wifi",
    "type": "ui-text",
    "name": "WiFi Status",
    "group": "group_network",
    "order": 1,
    "width": 3,
    "height": 1,
    "label": "WiFi",
    "format": "{{msg.payload}}",
    "style": {
        "color": "{{msg.color}}",
        "fontSize": "22px",
        "icon": "mdi-wifi"
    }
}
```

**Processing Function**:
```javascript
// WiFi status checker
const exec = require('child_process').exec;

exec('ip addr show wlan0 | grep "inet "', (error, stdout) => {
    if (stdout) {
        const ip = stdout.trim().split(' ')[1].split('/')[0];
        msg.payload = `Connected: ${ip}`;
        msg.color = '#00CC00'; // Green
    } else {
        msg.payload = 'Disconnected';
        msg.color = '#FF0000'; // Red
    }
    node.send(msg);
});
```

### 5.4 Chart Widget (Historical Trend)

**Configuration**:
```json
{
    "id": "chart_rpm",
    "type": "ui-chart",
    "name": "RPM History",
    "group": "group_engine_gauges",
    "order": 10,
    "width": 12,
    "height": 4,
    "chartType": "line",
    "xAxisType": "time",
    "yAxisType": "linear",
    "removeOlder": 3600,
    "removeOlderUnit": "s",
    "removeOlderPoints": "",
    "colors": ["#00CC00"],
    "textColor": ["#FFFFFF"],
    "textColorDefault": "#FFFFFF",
    "gridColor": "#333333",
    "tickColor": "#FFFFFF",
    "showLegend": true,
    "interpolate": "linear",
    "nodata": "No data",
    "ymin": 0,
    "ymax": 6000,
    "dot": false,
    "legend": "RPM"
}
```

---

## 6. DATA PROCESSING

### 6.1 Anomaly Detection Function

**File**: `/home/pi/.node-red/lib/anomaly_detector.js`

```javascript
/**
 * Anomaly Detector
 * Uses Statistical Process Control (SPC) with 3-sigma rule
 */

module.exports = function(RED) {
    "use strict";

    function AnomalyDetector(config) {
        RED.nodes.createNode(this, config);
        const node = this;

        // Load baseline from global context
        node.baseline = node.context().global.get('baseline') || {};

        node.on('input', function(msg) {
            const metric = config.metric || msg.metric;
            const value = msg.payload;
            const mode = msg.mode || 'cruise';

            if (!metric || typeof value !== 'number') {
                return;
            }

            // Get baseline stats
            const baselineData = node.baseline[metric]?.[mode];

            if (!baselineData) {
                node.warn(`No baseline for ${metric} in ${mode} mode`);
                return;
            }

            const mean = baselineData.mean;
            const stddev = baselineData.stddev;

            // Calculate deviation
            const deviation = Math.abs(value - mean);
            const sigma = stddev > 0 ? deviation / stddev : 0;

            // Classify
            let level, color;
            if (sigma > 3) {
                level = 'CRITICAL';
                color = '#FF0000';
            } else if (sigma > 2) {
                level = 'WARNING';
                color = '#FFA500';
            } else if (sigma > 1) {
                level = 'INFO';
                color = '#FFFF00';
            } else {
                level = 'NORMAL';
                color = '#00CC00';
            }

            // Build output message
            msg.anomaly = {
                level: level,
                metric: metric,
                value: value,
                baseline: mean,
                deviation: deviation,
                sigma: sigma,
                color: color,
                message: level !== 'NORMAL' ?
                    `${metric} is ${deviation.toFixed(1)} units from baseline (${sigma.toFixed(1)}σ)` :
                    null
            };

            node.send(msg);
        });
    }

    RED.nodes.registerType("anomaly-detector", AnomalyDetector);
}
```

### 6.2 Unit Conversion Library

**File**: `/home/pi/.node-red/lib/conversions.js`

```javascript
/**
 * Unit Conversions for Marine Data
 * Signal K uses SI units, we display in imperial/common units
 */

module.exports = {
    // Temperature: Kelvin → Fahrenheit
    kelvinToFahrenheit: function(K) {
        return (K - 273.15) * 9/5 + 32;
    },

    // Temperature: Kelvin → Celsius
    kelvinToCelsius: function(K) {
        return K - 273.15;
    },

    // Pressure: Pascal → PSI
    pascalToPSI: function(Pa) {
        return Pa / 6894.76;
    },

    // Pressure: Pascal → Bar
    pascalToBar: function(Pa) {
        return Pa / 100000;
    },

    // Speed: m/s → Knots
    msToKnots: function(ms) {
        return ms * 1.94384;
    },

    // Speed: m/s → MPH
    msToMPH: function(ms) {
        return ms * 2.23694;
    },

    // Angle: Radians → Degrees
    radiansToDegrees: function(rad) {
        return rad * 180 / Math.PI;
    },

    // Volume: Cubic meters → Gallons
    m3ToGallons: function(m3) {
        return m3 * 264.172;
    },

    // Volume rate: L/h → GPH
    lphToGPH: function(lph) {
        return lph * 0.264172;
    },

    // Distance: Meters → Nautical Miles
    metersToNM: function(m) {
        return m / 1852;
    },

    // Distance: Meters → Feet
    metersToFeet: function(m) {
        return m * 3.28084;
    }
};
```

### 6.3 Batch Data Processing

**Function Node**: Process multiple metrics at once

```javascript
// Batch process engine metrics
const conversions = global.get('conversions');

const signalkData = msg.payload;

// Extract and convert all engine metrics
const processed = {
    timestamp: new Date().toISOString(),
    rpm: signalkData.propulsion?.main?.revolutions || 0,
    coolantTemp: conversions.kelvinToFahrenheit(
        signalkData.propulsion?.main?.temperature || 0
    ),
    oilPressure: conversions.pascalToPSI(
        signalkData.propulsion?.main?.oilPressure || 0
    ),
    voltage: signalkData.electrical?.batteries?.[0]?.voltage || 0,
    fuelLevel: (signalkData.tanks?.fuel?.[0]?.currentLevel || 0) * 100
};

msg.payload = processed;

return msg;
```

---

## 7. ALERT SYSTEM

### 7.1 Alert Flow Structure

```
[Anomaly Detection]
        ↓
  [Filter by Level]
   ↓      ↓      ↓
[INFO] [WARN] [CRITICAL]
   ↓      ↓      ↓
[Log]  [Visual] [Voice + Visual]
```

### 7.2 Critical Alert Handler

**Function Node**:
```javascript
// Critical alert handler
const anomaly = msg.anomaly;

if (anomaly.level === 'CRITICAL') {
    // Build voice alert message
    const voiceMsg = {
        payload: {
            type: 'alert',
            priority: 'critical',
            message: `Helm alert: ${anomaly.message}. Please check immediately.`,
            metric: anomaly.metric,
            value: anomaly.value
        }
    };

    // Build visual alert
    const visualMsg = {
        payload: {
            type: 'notification',
            title: 'CRITICAL ALERT',
            body: anomaly.message,
            color: '#FF0000',
            icon: 'mdi-alert-circle',
            timeout: 0  // Don't auto-dismiss
        }
    };

    // Build database log
    const dbMsg = {
        topic: `INSERT INTO anomalies (
            timestamp, level, metric, value,
            baseline_value, deviation, sigma, message
        ) VALUES (
            '${new Date().toISOString()}',
            'CRITICAL',
            '${anomaly.metric}',
            ${anomaly.value},
            ${anomaly.baseline},
            ${anomaly.deviation},
            ${anomaly.sigma},
            '${anomaly.message}'
        )`
    };

    return [voiceMsg, visualMsg, dbMsg];
}

return [null, null, null];
```

### 7.3 Alert Throttling

**Purpose**: Prevent alert spam (e.g., don't alert every second)

**Function Node**:
```javascript
// Alert throttling: Only alert once per 5 minutes
const alertKey = `alert_${msg.anomaly.metric}_${msg.anomaly.level}`;
const lastAlert = context.get(alertKey) || 0;
const now = Date.now();

const throttleTime = 5 * 60 * 1000; // 5 minutes

if (now - lastAlert > throttleTime) {
    context.set(alertKey, now);
    return msg; // Allow alert
}

return null; // Suppress alert
```

---

## 8. WEBSOCKET COMMUNICATION

### 8.1 Dashboard WebSocket

**Dashboard 2.0 uses built-in WebSocket for real-time updates**

**Client-Side** (browser):
```html
<script>
// Dashboard automatically connects to WebSocket
// But you can also connect manually for custom UI

const ws = new WebSocket('ws://helm-os.local:1880/ws/dashboard');

ws.onopen = () => {
    console.log('Connected to Node-RED Dashboard');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    // Update custom UI element
    if (data.topic === 'rpm') {
        document.getElementById('rpm-display').innerText = data.payload;
    }
};

// Send command to Node-RED
function sendCommand(command) {
    ws.send(JSON.stringify({
        topic: 'command',
        payload: command
    }));
}
</script>
```

**Server-Side** (Node-RED):
```javascript
// WebSocket output node
msg.payload = {
    topic: 'rpm',
    value: 3200,
    timestamp: new Date().toISOString()
};

// Send to all connected clients
return msg;
```

### 8.2 Custom WebSocket Server

**For custom integrations outside Dashboard**

**Configuration Node**:
```json
{
    "id": "ws_server",
    "type": "websocket-listener",
    "path": "/ws/helm-os",
    "wholemsg": "true"
}
```

**Input Handler**:
```json
{
    "id": "ws_input",
    "type": "websocket in",
    "name": "WS Commands",
    "server": "ws_server",
    "client": "",
    "x": 100,
    "y": 400,
    "wires": [["ws_command_parser"]]
}
```

**Output Handler**:
```json
{
    "id": "ws_output",
    "type": "websocket out",
    "name": "WS Response",
    "server": "ws_server",
    "client": "",
    "x": 500,
    "y": 400,
    "wires": []
}
```

---

## 9. CUSTOM NODES

### 9.1 Creating a Custom Node

**Directory**: `/home/pi/.node-red/nodes/helm-signalk/`

**Package.json**:
```json
{
    "name": "node-red-contrib-helm-signalk",
    "version": "1.0.0",
    "description": "Helm-OS Signal K nodes",
    "node-red": {
        "nodes": {
            "signalk-subscribe": "signalk-subscribe.js",
            "signalk-path": "signalk-path.js"
        }
    },
    "keywords": ["node-red", "signalk", "helm-os"],
    "author": "Helm-OS Team",
    "license": "GPL-3.0"
}
```

**Node Implementation** (`signalk-path.js`):
```javascript
module.exports = function(RED) {
    "use strict";

    function SignalKPathNode(config) {
        RED.nodes.createNode(this, config);
        const node = this;

        node.path = config.path;
        node.server = RED.nodes.getNode(config.server);

        node.on('input', function(msg) {
            // Extract value from Signal K path
            const path = node.path.split('.');
            let value = msg.payload;

            for (const key of path) {
                if (value && typeof value === 'object') {
                    value = value[key];
                } else {
                    value = null;
                    break;
                }
            }

            if (value !== null) {
                msg.payload = value;
                msg.signalk_path = node.path;
                node.send(msg);
            }
        });
    }

    RED.nodes.registerType("signalk-path", SignalKPathNode);
}
```

**HTML Template** (`signalk-path.html`):
```html
<script type="text/javascript">
    RED.nodes.registerType('signalk-path',{
        category: 'helm-os',
        color: '#00CC00',
        defaults: {
            name: {value:""},
            path: {value:"", required:true}
        },
        inputs: 1,
        outputs: 1,
        icon: "signalk.png",
        label: function() {
            return this.name || "signalk-path";
        }
    });
</script>

<script type="text/html" data-template-name="signalk-path">
    <div class="form-row">
        <label for="node-input-name"><i class="fa fa-tag"></i> Name</label>
        <input type="text" id="node-input-name" placeholder="Name">
    </div>
    <div class="form-row">
        <label for="node-input-path"><i class="fa fa-road"></i> Path</label>
        <input type="text" id="node-input-path" placeholder="propulsion.main.revolutions">
    </div>
</script>

<script type="text/html" data-help-name="signalk-path">
    <p>Extracts a value from a Signal K path</p>
    <h3>Inputs</h3>
    <dl class="message-properties">
        <dt>payload <span class="property-type">object</span></dt>
        <dd>Signal K data object</dd>
    </dl>
    <h3>Outputs</h3>
    <dl class="message-properties">
        <dt>payload <span class="property-type">any</span></dt>
        <dd>Extracted value from specified path</dd>
    </dl>
</script>
```

**Install Custom Node**:
```bash
cd ~/.node-red/nodes/helm-signalk
npm link
cd ~/.node-red
npm link node-red-contrib-helm-signalk
# Restart Node-RED
sudo systemctl restart nodered
```

---

## 10. BEST PRACTICES

### 10.1 Flow Organization

**DO**:
- Group related nodes into tabs (Engine, Tanks, System, etc.)
- Use link nodes to connect across tabs (avoid spaghetti)
- Name all nodes descriptively ("Extract RPM" not "function")
- Use comments to explain complex logic
- Color-code critical paths (red for alerts)

**DON'T**:
- Put everything in one tab
- Use generic names ("function 1", "function 2")
- Create circular dependencies
- Forget to handle error cases

### 10.2 Error Handling

**Catch Node**:
```json
{
    "id": "catch_all",
    "type": "catch",
    "name": "Global Error Handler",
    "scope": null,
    "uncaught": true,
    "x": 100,
    "y": 800,
    "wires": [["log_error", "notify_error"]]
}
```

**Error Logging Function**:
```javascript
// Log error to file
const error = msg.error;
const timestamp = new Date().toISOString();

const logEntry = `${timestamp} | ${error.source?.name || 'unknown'} | ${error.message}\n`;

const fs = require('fs');
fs.appendFileSync('/opt/helm-os/logs/nodered.log', logEntry);

msg.payload = `Error logged: ${error.message}`;
return msg;
```

### 10.3 Performance Optimization

**Throttle High-Frequency Updates**:
```javascript
// Throttle to 1Hz (1000ms)
const now = Date.now();
const lastUpdate = context.get('lastUpdate') || 0;

if (now - lastUpdate < 1000) {
    return null; // Drop message
}

context.set('lastUpdate', now);
return msg; // Allow message
```

**Batch Database Writes**:
```javascript
// Batch writes every 10 seconds
const batch = context.get('batch') || [];
batch.push(msg.payload);

if (batch.length >= 10) {
    // Build multi-row INSERT
    const values = batch.map(row =>
        `('${row.timestamp}', ${row.rpm}, ${row.temp}, ${row.pressure})`
    ).join(',');

    msg.topic = `INSERT INTO engine_metrics (timestamp, rpm, temperature, oil_pressure) VALUES ${values}`;
    context.set('batch', []);
    return msg;
}

context.set('batch', batch);
return null;
```

### 10.4 Context Storage

**Use appropriate context scope**:

```javascript
// Flow context (shared across nodes in same tab)
const baseline = flow.get('baseline');
flow.set('lastRPM', msg.payload);

// Global context (shared across all flows)
const config = global.get('helm_config');
global.set('anomalyCount', count);

// Node context (private to this node)
const counter = context.get('counter') || 0;
context.set('counter', counter + 1);
```

---

## 11. TROUBLESHOOTING

### 11.1 Dashboard Not Loading

**Symptoms**:
- Dashboard shows blank page
- Gauges not appearing
- 404 error on /dashboard

**Diagnostic**:
```bash
# Check Node-RED status
sudo systemctl status nodered

# Check dashboard installed
cd ~/.node-red
npm list @flowfuse/node-red-dashboard

# View Node-RED logs
journalctl -u nodered -f

# Check dashboard URL
curl http://localhost:1880/dashboard
```

**Solutions**:
1. Install Dashboard 2.0: `npm install @flowfuse/node-red-dashboard`
2. Restart Node-RED: `sudo systemctl restart nodered`
3. Clear browser cache
4. Check firewall allows port 1880

### 11.2 Signal K Connection Failed

**Symptoms**:
- WebSocket shows "disconnected"
- No data in gauges
- "Connection refused" errors

**Diagnostic**:
```bash
# Check Signal K status
sudo systemctl status signalk

# Test WebSocket manually
curl http://localhost:3000/signalk/v1/api/

# Check firewall
sudo ufw status | grep 3000
```

**Solutions**:
1. Start Signal K: `sudo systemctl start signalk`
2. Verify URL in WebSocket node: `ws://localhost:3000/signalk/v1/stream`
3. Check Signal K security settings (authentication)

### 11.3 Gauges Not Updating

**Symptoms**:
- Gauges show old data
- Values frozen
- No real-time updates

**Diagnostic**:
1. Check Debug output (add debug nodes)
2. Verify data flow (Deploy with "Modified Flows" not "Full")
3. Check for JavaScript errors in function nodes
4. Verify msg.payload format

**Debug Node Example**:
```json
{
    "id": "debug_rpm",
    "type": "debug",
    "name": "Debug RPM",
    "active": true,
    "tosidebar": true,
    "console": false,
    "tostatus": true,
    "complete": "payload",
    "targetType": "msg",
    "statusVal": "payload",
    "statusType": "auto",
    "x": 500,
    "y": 200,
    "wires": []
}
```

### 11.4 High CPU Usage

**Symptoms**:
- Node-RED using >50% CPU
- Slow dashboard response
- System lag

**Diagnostic**:
```bash
# Check Node-RED CPU usage
top -p $(pgrep -f node-red)

# Profile Node-RED
node-red-admin profile
```

**Solutions**:
1. Add throttle nodes (limit update frequency)
2. Batch database writes
3. Remove unnecessary debug nodes
4. Optimize function node logic (avoid loops)
5. Use link nodes instead of multiple wires

### 11.5 Memory Leaks

**Symptoms**:
- RAM usage increasing over time
- Node-RED crashes after hours/days
- "Out of memory" errors

**Diagnostic**:
```bash
# Monitor memory
watch -n 1 'free -h'

# Check Node-RED memory
ps aux | grep node-red
```

**Solutions**:
1. Clear context periodically:
```javascript
// Clear old data from context
const keys = flow.keys();
keys.forEach(key => {
    if (key.startsWith('temp_')) {
        flow.set(key, undefined);
    }
});
```

2. Limit chart data retention (removeOlder setting)
3. Use proper garbage collection in function nodes
4. Restart Node-RED daily (cron job)

---

## APPENDIX A: Complete Example Flow

### A.1 Engine Monitoring Flow (Full)

**Export JSON**: `engine-monitoring-flow.json`

```json
[
    {
        "id": "tab_engine",
        "type": "tab",
        "label": "Engine Monitoring",
        "disabled": false,
        "info": "Complete engine monitoring with gauges, alerts, and storage"
    },
    {
        "id": "signalk_in",
        "type": "websocket in",
        "name": "Signal K Stream",
        "server": "signalk_server",
        "x": 100,
        "y": 100,
        "wires": [["parse_delta"]]
    },
    {
        "id": "parse_delta",
        "type": "json",
        "name": "Parse JSON",
        "x": 250,
        "y": 100,
        "wires": [["extract_engine"]]
    },
    {
        "id": "extract_engine",
        "type": "function",
        "name": "Extract Engine Data",
        "func": "// Extract engine metrics from Signal K\nconst conversions = global.get('conversions');\n\nif (!msg.payload.updates) return null;\n\nconst metrics = {};\n\nfor (const update of msg.payload.updates) {\n    for (const value of update.values) {\n        const path = value.path;\n        \n        if (path === 'propulsion.main.revolutions') {\n            metrics.rpm = Math.round(value.value);\n        }\n        else if (path === 'propulsion.main.temperature') {\n            metrics.coolantTemp = Math.round(conversions.kelvinToFahrenheit(value.value));\n        }\n        else if (path === 'propulsion.main.oilPressure') {\n            metrics.oilPressure = Math.round(conversions.pascalToPSI(value.value));\n        }\n        else if (path === 'electrical.batteries.0.voltage') {\n            metrics.voltage = value.value.toFixed(1);\n        }\n    }\n}\n\nif (Object.keys(metrics).length > 0) {\n    msg.payload = metrics;\n    return msg;\n}\n\nreturn null;",
        "x": 400,
        "y": 100,
        "wires": [["rpm_gauge", "temp_gauge", "pressure_gauge", "voltage_gauge", "check_anomalies", "store_db"]]
    },
    {
        "id": "rpm_gauge",
        "type": "ui-gauge",
        "name": "RPM",
        "group": "engine_group",
        "format": "{{msg.payload.rpm}}",
        "min": 0,
        "max": 6000,
        "x": 600,
        "y": 50,
        "wires": []
    },
    {
        "id": "temp_gauge",
        "type": "ui-gauge",
        "name": "Temp",
        "group": "engine_group",
        "format": "{{msg.payload.coolantTemp}}",
        "min": 100,
        "max": 250,
        "x": 600,
        "y": 100,
        "wires": []
    },
    {
        "id": "pressure_gauge",
        "type": "ui-gauge",
        "name": "Oil Pressure",
        "group": "engine_group",
        "format": "{{msg.payload.oilPressure}}",
        "min": 0,
        "max": 100,
        "x": 600,
        "y": 150,
        "wires": []
    },
    {
        "id": "voltage_gauge",
        "type": "ui-text",
        "name": "Voltage",
        "group": "engine_group",
        "format": "{{msg.payload.voltage}}V",
        "x": 600,
        "y": 200,
        "wires": []
    },
    {
        "id": "check_anomalies",
        "type": "function",
        "name": "Anomaly Detection",
        "func": "// Check each metric against baseline\nconst metrics = msg.payload;\nconst baseline = global.get('baseline') || {};\n\nconst anomalies = [];\n\nfor (const [key, value] of Object.entries(metrics)) {\n    const baselineData = baseline[key]?.cruise;\n    \n    if (!baselineData) continue;\n    \n    const deviation = Math.abs(value - baselineData.mean);\n    const sigma = deviation / baselineData.stddev;\n    \n    if (sigma > 2) {\n        anomalies.push({\n            metric: key,\n            value: value,\n            baseline: baselineData.mean,\n            deviation: deviation,\n            sigma: sigma,\n            level: sigma > 3 ? 'CRITICAL' : 'WARNING'\n        });\n    }\n}\n\nif (anomalies.length > 0) {\n    msg.anomalies = anomalies;\n    return msg;\n}\n\nreturn null;",
        "x": 600,
        "y": 250,
        "wires": [["alert_handler"]]
    },
    {
        "id": "alert_handler",
        "type": "function",
        "name": "Alert Handler",
        "func": "// Send alerts\nconst anomalies = msg.anomalies;\n\nfor (const anomaly of anomalies) {\n    if (anomaly.level === 'CRITICAL') {\n        // Voice alert\n        node.send([{\n            payload: {\n                message: `Critical: ${anomaly.metric} is ${anomaly.deviation.toFixed(1)} units from baseline`\n            }\n        }, null]);\n    } else {\n        // Visual alert only\n        node.send([null, {\n            payload: {\n                message: `Warning: ${anomaly.metric} elevated`\n            }\n        }]);\n    }\n}\n\nreturn null;",
        "outputs": 2,
        "x": 800,
        "y": 250,
        "wires": [["voice_alert"], ["visual_alert"]]
    },
    {
        "id": "store_db",
        "type": "sqlite",
        "name": "Store Metrics",
        "db": "/opt/helm-os/data/historical.db",
        "sqlquery": "prepared",
        "sql": "INSERT INTO engine_metrics (timestamp, rpm, coolant_temp, oil_pressure, voltage) VALUES (?, ?, ?, ?, ?)",
        "x": 600,
        "y": 300,
        "wires": [[]]
    }
]
```

---

## APPENDIX B: Dashboard Groups

### B.1 Group Definitions

```json
{
    "groups": [
        {
            "id": "engine_group",
            "name": "Engine Gauges",
            "tab": "tab_engine",
            "order": 1,
            "width": "12",
            "collapse": false
        },
        {
            "id": "tanks_group",
            "name": "Tank Levels",
            "tab": "tab_engine",
            "order": 2,
            "width": "12",
            "collapse": false
        },
        {
            "id": "system_group",
            "name": "System Status",
            "tab": "tab_system",
            "order": 1,
            "width": "12",
            "collapse": false
        }
    ]
}
```

---

**END OF NODE-RED FLOWS SPECIFICATION**
