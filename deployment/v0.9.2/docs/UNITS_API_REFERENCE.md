# d3kOS Preferences API — v0.9.2
## Service: preferences-api.py | Port: 8107 | Nginx proxy: /api/preferences

---

## Endpoints

### GET /api/preferences
Returns current user preferences.

**Response:**
```json
{
  "measurement_system": "imperial",
  "language": "en",
  "timezone": "UTC",
  "theme": "dark"
}
```

---

### POST /api/preferences
Updates one or more preferences.

**Request body:**
```json
{ "measurement_system": "metric" }
```

**Valid values for measurement_system:** `"imperial"` | `"metric"`

**Response (success):**
```json
{
  "success": true,
  "preferences": {
    "measurement_system": "metric",
    "language": "en",
    "timezone": "UTC",
    "theme": "dark"
  }
}
```

**Response (invalid value):**
```json
{ "error": "measurement_system must be \"imperial\" or \"metric\"" }
```
HTTP 400

---

### GET /health
Health check endpoint (direct to port 8107, bypasses nginx).

```
curl http://192.168.1.237:8107/health
```

**Response:**
```json
{ "status": "ok", "service": "preferences-api", "version": "0.9.2" }
```

---

## Config File
Preferences persisted to: `/opt/d3kos/config/user-preferences.json`

Default values:
```json
{
  "measurement_system": "imperial",
  "language": "en",
  "timezone": "UTC",
  "theme": "dark"
}
```

---

## Service Management
```bash
sudo systemctl status d3kos-preferences-api
sudo systemctl restart d3kos-preferences-api
sudo journalctl -u d3kos-preferences-api -f
```

---

## JavaScript Usage (units.js)
```javascript
Units.getPreference()           // → 'imperial' or 'metric'
Units.setPreference('metric')   // saves to localStorage + POSTs to API

Units.temperature.toDisplay(212)  // → '100.0°C' or '212.0°F'
Units.pressure.toDisplay(45)      // → '3.10 bar' or '45.0 PSI'
Units.speed.toDisplay(10)         // → '10.0 kts (18.5 km/h)' or '10.0 kts (11.5 mph)'
Units.depth.toDisplay(30)         // → '9.1 m' or '30.0 ft'
Units.fuel.toDisplay(50)          // → '189.3 L' or '50.0 gal'
Units.distance.toDisplay(10)      // → '18.5 km' or '10.0 nm'
Units.length.toDisplay(25)        // → '7.6 m' or '25.0 ft'
Units.weight.toDisplay(1000)      // → '453.6 kg' or '1000.0 lb'
Units.displacement.toDisplay(350) // → '5.7 L' or '350 ci'
```
