# d3kOS Helm-OS — Ollama Codebase Context
# Injected into every Ollama prompt. Prevents hallucination of variable names and return types.

---

## CRITICAL: units.js Return Types

`Units` is a global object loaded from `/js/units.js` on every page.

ALL `toDisplay()` methods return a **formatted string** — NOT an object.

```
Units.temperature.toDisplay(212)     → "212.0°F"    or "100.0°C"
Units.pressure.toDisplay(45)         → "45.0 PSI"   or "3.10 bar"
Units.speed.toDisplay(10)            → "10.0 kts (11.5 mph)"  or "10.0 kts (18.5 km/h)"
Units.depth.toDisplay(30)            → "30.0 ft"    or "9.1 m"
Units.fuel.toDisplay(50)             → "50.0 gal"   or "189.3 L"
Units.distance.toDisplay(10)         → "10.0 nm"    or "18.5 km"
Units.length.toDisplay(25)           → "25.0 ft"    or "7.6 m"
Units.weight.toDisplay(1000)         → "1000.0 lb"  or "453.6 kg"
Units.displacement.toDisplay(350)    → "350 ci"     or "5.7 L"
Units.getPreference()                → "imperial"   or "metric"
Units.temperature.unit()             → "°F"         or "°C"
Units.pressure.unit()                → "PSI"        or "bar"
Units.depth.unit()                   → "ft"         or "m"
Units.fuel.unit()                    → "gal"        or "L"
```

NEVER write: `Units.temperature.toDisplay(x).value` or `Units.temperature.toDisplay(x).unit`
ALWAYS write: `Units.temperature.toDisplay(x)` — the whole string is the display value.

---

## Internal Storage Convention

All sensor data is stored in **imperial units**. Metric is display-only conversion.

| Measurement | Internal unit | Signal K raw unit | Conversion required |
|-------------|--------------|-------------------|---------------------|
| Temperature | °F | Kelvin | `(K - 273.15) * 9/5 + 32` |
| Pressure | PSI | Pascals | `Pa / 6894.76` |
| Speed | knots | m/s | `m/s * 1.94384` |
| Depth | feet | metres | `m * 3.28084` |
| Fuel | gallons | ratio 0-1 | `* 100` for percent |
| Engine displacement | cubic inches (ci) | — | stored as ci |

By the time values reach `updateGauge()` or `toDisplay()`, they are **already in imperial**.
Do NOT convert again inside display functions.

---

## Variable Names: dashboard.html

```javascript
// Global state
let ws = null;
let signalKConnected = false;
let currentData = {
  rpm: 0, trim: 0, temp: 0, oil: 0,
  voltage: 0, fresh: 0, black: 0, fuel: 0, battery: 0
};

// All values in currentData are already in imperial (°F, PSI, %, V, RPM)
// Call pattern:
updateGauge('temp', currentData.temp, 0, 250);   // value is already °F
updateGauge('oil',  currentData.oil,  0, 100);   // value is already PSI

// Gauge names: 'rpm', 'trim', 'temp', 'oil', 'voltage', 'fresh', 'black', 'fuel', 'battery'
// Element IDs: '${name}-value', '${name}-bar', '${name}-unit' (if exists)
```

---

## Variable Names: navigation.html

```javascript
// Global state
let signalKSocket = null;
let signalKConnected = false;
let navData = {
  position: { latitude: null, longitude: null },
  speedOverGround: null,    // metres/second from Signal K — convert *1.94384 for knots
  courseOverGroundTrue: null, // radians
  heading: null,              // radians
  depth: null,                // metres from Signal K — convert *3.28084 for feet
  gnss: { satellites: null, horizontalDilution: null, methodQuality: null }
};
let aisTargets = {};
let lastDataTime = null;

// Key functions to modify for units:
function updateSOG() {
  const sog = navData.speedOverGround;   // m/s — convert to knots first
  // const knots = sog * 1.94384;
}
function updateDepth() {
  const depth = navData.depth;           // metres — convert to feet first
  // const depthFt = depth * 3.28084;
}
```

---

## Variable Names: helm.html

```javascript
// Global state
let chatHistory = [];
let signalKSocket = null;
let signalKConnected = false;
let currentEngineData = {};
// currentEngineData keys populated from Signal K:
//   .rpm           — integer RPM
//   .oilPressure   — float PSI (already converted from Pa)
//   .temperature   — float °F (already converted from K)
//   .voltage       — float volts
//   .engineHours   — float hours

function getEngineStatus() {
  const rpm  = currentEngineData.rpm || 0;
  const oil  = currentEngineData.oilPressure || 0;    // PSI
  const temp = currentEngineData.temperature || 0;    // °F
  const voltage = currentEngineData.voltage || 0;
  const hours   = currentEngineData.engineHours || 0;
  // returns a formatted string for chat display
}
```

---

## Variable Names: weather.html

```javascript
// Global state
let currentPosition = { lat: 44.4167, lon: -79.3333 };
let hasGPSFix = false;
let weatherData = null;         // set by fetchWeatherData()
let currentZoom = 9;
let currentOverlay = 'wind';    // 'wind', 'rain', 'temp', 'pressure', etc.
let lastRadarPosition = { lat: null, lon: null };
let signalkWS = null;

// Key function:
function updateRadar() {
  // Builds windyUrl using currentPosition, currentZoom, currentOverlay
  // The metricTemp parameter in the URL controls C vs F
  // Current URL uses: &metricTemp=%C2%B0C  (hardcoded Celsius)
  // Fix: make metricTemp dynamic based on Units.getPreference()
  // metricTemp param: "%C2%B0C" for Celsius, "%C2%B0F" for Fahrenheit
  document.getElementById('radarFrame').src = windyUrl;
}

// weatherData structure (from open-meteo API):
// weatherData.weather.current.temperature_2m  — already in °C (API default)
// weatherData.marine.current.wave_height       — metres
```

---

## Variable Names: onboarding.html

```javascript
// Global state
let step = 0;
const total = 20;
let config = {};

// config keys (populated as wizard progresses):
// config.q1  = Boat Manufacturer (string)
// config.q2  = Boat Year (number)
// config.q3  = Boat Model (string)
// config.q4  = Chartplotter (string)
// config.q5  = Engine Manufacturer (string)
// config.q6  = Engine Model (string)
// config.q7  = Engine Year (number)
// config.q8  = Cylinders (string/number)
// config.q9  = Engine Size (number — in liters or CID as entered by user)
// config.q10 = Engine Power (number HP or kW)
// config.q11 = Compression Ratio (number)
// config.q12 = Idle RPM (number)
// config.q13 = Max RPM Range (string)
// config.q14 = Engine Type (string: 'gasoline', 'diesel', etc.)
// config.q15 = Boat Origin (string: 'us', 'ca', 'eu', 'au', 'asia', 'sa', 'af')
// config.q16 = Engine Position (string)

// Boat origin values that should default to metric:
// 'eu' (Europe), 'au' (Australia/Oceania), 'asia' (Asia), 'sa' (South America), 'af' (Africa)
// Values that should default to imperial:
// 'us' (United States), 'ca' (Canada)
```

---

## Variable Names: query_handler.py

```python
class AIQueryHandler:
    def __init__(self):
        self.config = self.load_config()   # /opt/d3kos/config/user-preferences.json
        self.skills = self.load_skills()
        self.signalk = SignalKClient()

    def get_boat_status(self):
        # Returns dict with these keys (all already in imperial):
        # status['rpm']           — integer
        # status['oil_pressure']  — float PSI
        # status['coolant_temp']  — float °F
        # status['fuel_level']    — float percentage 0-100
        # status['speed']         — float knots
        # status['boost_pressure']— float PSI (optional, may be absent)
        # status['voltage']       — float volts (optional, may be absent)

    def simple_response(self, category):
        # category: 'rpm', 'oil', 'temperature', 'fuel', 'battery', 'speed', 'boost', 'status'
        status = self.get_boat_status()   # call this once, then use status dict
        # Build responses dict and return responses.get(category, fallback)

    def _load_units_preference(self):
        # Read /opt/d3kos/config/user-preferences.json
        # Returns 'imperial' or 'metric'

    def _format_temperature(self, fahrenheit: float, system: str) -> str:
        # Returns e.g. "180.0 degrees Fahrenheit" or "82.2 degrees Celsius"

    def _format_pressure(self, psi: float, system: str) -> str:
        # Returns e.g. "45.0 PSI" or "3.10 bar"

    def _format_speed(self, knots: float, system: str) -> str:
        # Returns e.g. "12.5 knots, which is 14.4 miles per hour"
        #         or  "12.5 knots, which is 23.2 kilometers per hour"
```

---

## AI Services: Ports and Endpoints

```
Port 8097 — Gemini API proxy (d3kos-gemini-proxy.service)
  POST http://localhost:8097/gemini/chat      — conversational AI
  GET  http://localhost:8097/gemini/health    — health check
  GET  http://localhost:8097/gemini/test      — connectivity test
  GET  http://localhost:8097/gemini/config    — read Gemini config
  POST http://localhost:8097/gemini/config    — save API key / model

Port 8099 — Self-healing / issue detector (d3kos-issue-detector.service)
  GET  http://localhost:8099/healing/status   — system health
  POST http://localhost:8099/healing/detect   — run detection

Port 8107 — Preferences API (d3kos-preferences-api.service)
  GET/POST http://localhost:8107/api/preferences — measurement units
```

IMPORTANT: Gemini proxy is port 8097 (NOT 8099).
In query_handler.py, use: requests.post('http://localhost:8097/gemini/chat', ...)
In nginx config, use:    proxy_pass http://127.0.0.1:8097/gemini/;

---

## Variable Names: gemini-proxy.py (query_handler.py Gemini integration)

```python
# In query_handler.py, the Gemini integration method:
def _query_gemini(self, text: str, boat_status: dict = None) -> str | None:
    """Query Gemini API proxy. Returns response text or None on failure."""
    import requests
    try:
        payload = {'message': text}
        if boat_status:
            payload['context'] = boat_status
        r = requests.post('http://localhost:8097/gemini/chat', json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data.get('response', '').strip()
    except Exception as e:
        print(f"  Gemini query failed: {e}", flush=True)
    return None

# In query() method, the ai_used field must be 'online' or 'onboard' (not 'gemini')
ai_used = 'online' if provider == 'gemini' else 'onboard'
```

---

## FIND_LINE / ACTION / CODE Format

Your output MUST use EXACTLY this format. No explanation outside these blocks.

```
FIND_LINE: <exact verbatim text of a line that exists in the file>
ACTION: INSERT_BEFORE | INSERT_AFTER | REPLACE
CODE:
<exact code to insert or use as replacement — preserve indentation>
END_CODE
```

Rules:
- `FIND_LINE` must exist verbatim in the file (will be verified)
- Avoid using a line that is just `}` or `{` — these are not unique
- Use the most specific/distinctive line near the insertion point
- Multiple FIND_LINE/ACTION/CODE blocks are allowed (one per change)
- Preserve the indentation style of the surrounding code
- Do NOT wrap output in markdown code fences — just the raw blocks

---

## Example of Correct Output

```
FIND_LINE:     function updateGauge(name, value, min, max) {
ACTION: REPLACE
CODE:
    function updateGauge(name, value, min, max) {
      const valueEl = document.getElementById(`${name}-value`);
      if (valueEl) {
        if (name === 'temp' && typeof Units !== 'undefined') {
          valueEl.textContent = Units.temperature.toDisplay(value);
        } else if (name === 'oil' && typeof Units !== 'undefined') {
          valueEl.textContent = Units.pressure.toDisplay(value);
        } else {
          valueEl.textContent = value;
        }
      }
    }
END_CODE

FIND_LINE: <head>
ACTION: INSERT_AFTER
CODE:
<script src="/js/units.js"></script>
END_CODE
```
