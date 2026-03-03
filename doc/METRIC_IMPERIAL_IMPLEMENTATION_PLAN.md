# Metric/Imperial Measurement System Implementation Plan
## d3kOS Internationalization Feature

**Date:** March 1, 2026
**Status:** 📋 PLANNING
**Target Version:** v0.9.1.2 → v0.9.2 (Current version hotfix)
**Estimated Time:** 2-3 weeks
**Priority:** HIGH (international distribution requirement - "American boaters vs the world")

---

## EXECUTIVE SUMMARY

**What:** Add a measurement system preference switch that affects all displays, forms, and voice responses throughout d3kOS.

**Why:**
- International market expansion (Canada uses metric, US uses imperial)
- User preference (some boaters prefer metric even in imperial countries)
- Regulatory compliance (some regions require metric displays)
- Professional standards (commercial vessels often use metric)

**How:**
- Single toggle in Settings → Preferences
- Stored in user preferences (persistent across sessions)
- Affects all displays, forms, voice responses, and exports
- Real-time conversion using JavaScript utility functions

---

## SCOPE

**Simple Two-System Approach:** Imperial (America) vs Metric (World)

### In Scope:
✅ Temperature (°F ↔ °C)
✅ Speed (Knots, MPH ↔ Knots, km/h)
✅ Distance (Nautical miles ↔ Kilometers)
✅ Depth (Feet ↔ Meters)
✅ Fuel volume (Gallons ↔ Liters)
✅ Pressure (PSI ↔ Bar/kPa)
✅ Length (Feet/Inches ↔ Meters/Centimeters)
✅ Weight (Pounds ↔ Kilograms)
✅ Engine displacement (Cubic inches ↔ Liters)
✅ Dashboard displays
✅ Onboarding wizard forms
✅ Voice assistant responses
✅ Boatlog entries
✅ Navigation page
✅ Weather page
✅ Export data
✅ **Auto-default based on boat origin (Onboarding Step 15)**

### Auto-Default Logic:
- **America (USA, Canada)** → Imperial (default)
- **Europe, Asia, Oceania** → Metric (default)
- User can change anytime in Settings

### Out of Scope (for this phase):
❌ Mixed units (e.g., Fahrenheit for temp but liters for fuel) - keep simple
❌ Regional presets beyond Imperial/Metric - not needed
❌ Currency conversion (USD vs CAD vs EUR) - not measurements
❌ Date format (MM/DD/YYYY vs DD/MM/YYYY) - separate feature
❌ Language translation (English only) - future feature
❌ Historical data conversion (existing logs stay in original units) - display only
❌ UI mockups - not required

---

## MARINE MEASUREMENT CONVERSIONS

### Temperature:
- **Imperial:** Fahrenheit (°F)
- **Metric:** Celsius (°C)
- **Formula:** °C = (°F - 32) × 5/9
- **Reverse:** °F = (°C × 9/5) + 32
- **Examples:**
  - 185°F → 85°C (engine temp)
  - 72°F → 22°C (water temp)

### Speed:
- **Universal:** Knots (nautical miles per hour) - used by both systems
- **Imperial Alternative:** Miles per hour (MPH)
- **Metric Alternative:** Kilometers per hour (km/h)
- **Formulas:**
  - 1 knot = 1.15078 MPH
  - 1 knot = 1.852 km/h
- **Display:** Always show knots as primary, optional secondary unit

### Distance:
- **Imperial:** Nautical miles (nm)
- **Metric:** Kilometers (km)
- **Formula:** 1 nm = 1.852 km
- **Examples:**
  - 10 nm → 18.52 km

### Depth:
- **Imperial:** Feet (ft)
- **Metric:** Meters (m)
- **Formula:** 1 ft = 0.3048 m
- **Examples:**
  - 20 ft → 6.1 m (water depth)

### Fuel Volume:
- **Imperial:** US Gallons (gal)
- **Metric:** Liters (L)
- **Formula:** 1 gal = 3.78541 L
- **Examples:**
  - 50 gal → 189.3 L (fuel tank)

### Pressure:
- **Imperial:** Pounds per square inch (PSI)
- **Metric:** Bar or Kilopascals (kPa)
- **Formulas:**
  - 1 PSI = 0.0689476 Bar
  - 1 PSI = 6.89476 kPa
- **Examples:**
  - 45 PSI → 3.1 Bar (oil pressure)
  - 14.7 PSI → 101.3 kPa (atmospheric pressure)

### Length (Boat/Object):
- **Imperial:** Feet and inches (ft, in)
- **Metric:** Meters and centimeters (m, cm)
- **Formulas:**
  - 1 ft = 0.3048 m
  - 1 in = 2.54 cm
- **Examples:**
  - 24 ft → 7.32 m (boat length)
  - 10.1 in → 25.7 cm (screen diagonal)

### Weight:
- **Imperial:** Pounds (lbs)
- **Metric:** Kilograms (kg)
- **Formula:** 1 lb = 0.453592 kg
- **Examples:**
  - 1000 lbs → 453.6 kg (boat weight)

### Engine Displacement:
- **Imperial:** Cubic inches (ci)
- **Metric:** Liters (L)
- **Formula:** 1 ci = 0.0163871 L
- **Examples:**
  - 350 ci → 5.7 L (V8 engine)

---

## IMPLEMENTATION ARCHITECTURE

### 1. Storage Layer

**User Preference Storage:**

**Option A: localStorage (client-side only)**
```javascript
// Stored in browser
localStorage.setItem('d3kos-measurement-system', 'metric'); // or 'imperial'
```
✅ Immediate persistence
✅ Simple implementation
❌ Lost if browser cache cleared
❌ Not synced across devices

**Option B: Config file (server-side, recommended)**
```javascript
// Stored at /opt/d3kos/config/user-preferences.json
{
  "measurement_system": "metric",  // or "imperial"
  "date_format": "YYYY-MM-DD",
  "time_format": "24h",
  "language": "en",
  "timezone": "America/Toronto"
}
```
✅ Persistent across browser resets
✅ Syncs to AtMyBoat.com cloud (future)
✅ Accessible to backend services
✅ Can be exported/imported
❌ Requires API endpoint

**Recommended: Hybrid approach**
- Store in localStorage for immediate UI updates
- Sync to `/opt/d3kos/config/user-preferences.json` via API
- Backend reads config file for voice/export operations

### 2. Conversion Utility Module

**File:** `/var/www/html/js/units.js`

```javascript
// units.js - Measurement conversion utilities
const Units = {
  // Get current preference
  getPreference: function() {
    return localStorage.getItem('d3kos-measurement-system') || 'imperial';
  },

  // Set preference
  setPreference: function(system) {
    if (system !== 'metric' && system !== 'imperial') {
      throw new Error('Invalid measurement system');
    }
    localStorage.setItem('d3kos-measurement-system', system);
    // Trigger update event
    window.dispatchEvent(new CustomEvent('measurementSystemChanged', {
      detail: { system }
    }));
  },

  // Temperature conversions
  temperature: {
    toDisplay: function(fahrenheit) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const celsius = (fahrenheit - 32) * 5 / 9;
        return celsius.toFixed(1) + '°C';
      }
      return fahrenheit.toFixed(1) + '°F';
    },
    toFahrenheit: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return (value * 9 / 5) + 32;
      }
      return value;
    }
  },

  // Speed conversions
  speed: {
    toDisplay: function(knots) {
      const system = Units.getPreference();
      const secondary = system === 'metric' ?
        (knots * 1.852).toFixed(1) + ' km/h' :
        (knots * 1.15078).toFixed(1) + ' mph';
      return knots.toFixed(1) + ' kts (' + secondary + ')';
    }
  },

  // Distance conversions
  distance: {
    toDisplay: function(nauticalMiles) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const km = nauticalMiles * 1.852;
        return km.toFixed(2) + ' km';
      }
      return nauticalMiles.toFixed(2) + ' nm';
    }
  },

  // Depth conversions
  depth: {
    toDisplay: function(feet) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const meters = feet * 0.3048;
        return meters.toFixed(1) + ' m';
      }
      return feet.toFixed(1) + ' ft';
    },
    toFeet: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 0.3048;
      }
      return value;
    }
  },

  // Fuel volume conversions
  fuelVolume: {
    toDisplay: function(gallons) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const liters = gallons * 3.78541;
        return liters.toFixed(1) + ' L';
      }
      return gallons.toFixed(1) + ' gal';
    },
    toGallons: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 3.78541;
      }
      return value;
    }
  },

  // Pressure conversions
  pressure: {
    toDisplay: function(psi) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const bar = psi * 0.0689476;
        return bar.toFixed(2) + ' bar';
      }
      return psi.toFixed(1) + ' PSI';
    },
    toPSI: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 0.0689476;
      }
      return value;
    }
  },

  // Length conversions
  length: {
    toDisplay: function(feet) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const meters = feet * 0.3048;
        return meters.toFixed(2) + ' m';
      }
      return feet.toFixed(1) + ' ft';
    },
    toFeet: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 0.3048;
      }
      return value;
    }
  },

  // Weight conversions
  weight: {
    toDisplay: function(pounds) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const kg = pounds * 0.453592;
        return kg.toFixed(1) + ' kg';
      }
      return pounds.toFixed(1) + ' lbs';
    },
    toPounds: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 0.453592;
      }
      return value;
    }
  },

  // Engine displacement conversions
  displacement: {
    toDisplay: function(cubicInches) {
      const system = Units.getPreference();
      if (system === 'metric') {
        const liters = cubicInches * 0.0163871;
        return liters.toFixed(1) + ' L';
      }
      return cubicInches.toFixed(0) + ' ci';
    },
    toCubicInches: function(value, fromSystem) {
      if (fromSystem === 'metric') {
        return value / 0.0163871;
      }
      return value;
    }
  }
};
```

### 3. Settings UI (Simple Toggle - No Mockup)

**File:** `/var/www/html/settings.html`

**Add Preferences Section (Simple Implementation):**

```html
<div class="settings-section">
  <h2>Measurement System</h2>

  <div class="setting-row">
    <div class="setting-label">
      <strong>Units</strong>
      <p class="setting-description">Imperial (°F, PSI, gal) or Metric (°C, bar, L)</p>
    </div>
    <div class="setting-control">
      <label class="toggle-switch">
        <input type="checkbox" id="measurement-system-toggle" onchange="changeMeasurementSystem()">
        <span class="toggle-slider"></span>
      </label>
      <span id="measurement-system-label" class="toggle-label">Imperial</span>
    </div>
  </div>

  <div class="setting-info">
    <p><strong>Affects:</strong> Dashboard, forms, voice, navigation, weather</p>
    <p><strong>Default:</strong> Set automatically based on boat origin during onboarding</p>
  </div>
</div>

<script>
// Load current preference
window.addEventListener('DOMContentLoaded', function() {
  const system = Units.getPreference();
  const toggle = document.getElementById('measurement-system-toggle');
  const label = document.getElementById('measurement-system-label');

  if (system === 'metric') {
    toggle.checked = true;
    label.textContent = 'Metric';
  } else {
    toggle.checked = false;
    label.textContent = 'Imperial';
  }
});

// Handle preference change
function changeMeasurementSystem() {
  const toggle = document.getElementById('measurement-system-toggle');
  const label = document.getElementById('measurement-system-label');
  const system = toggle.checked ? 'metric' : 'imperial';

  Units.setPreference(system);
  label.textContent = system === 'metric' ? 'Metric' : 'Imperial';

  // Save to backend
  fetch('/api/preferences', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ measurement_system: system })
  }).then(response => {
    if (response.ok) {
      alert('Measurement system updated to ' + system);
      location.reload(); // Refresh to update all displays
    }
  });
}
</script>
```

**CSS (Simple d3kOS Green Theme):**

```css
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #666;
  transition: .4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #00CC00; /* d3kOS green */
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  margin-left: 10px;
  font-weight: bold;
  color: #FFFFFF;
}

.setting-description {
  color: #CCCCCC;
  font-size: 14px;
  margin: 5px 0 0 0;
}

.setting-info {
  background: #222;
  border: 1px solid #00CC00;
  padding: 15px;
  margin-top: 15px;
  border-radius: 5px;
  font-size: 14px;
  color: #CCCCCC;
}
```

### 4. Backend API Endpoint

**File:** `/opt/d3kos/services/config/preferences-api.py` (NEW)

```python
#!/usr/bin/env python3
"""
User Preferences API
Manages user preferences including measurement system
Port: 8107
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

CONFIG_FILE = '/opt/d3kos/config/user-preferences.json'

# Default preferences
DEFAULT_PREFERENCES = {
    'measurement_system': 'imperial',
    'date_format': 'YYYY-MM-DD',
    'time_format': '24h',
    'language': 'en',
    'timezone': 'America/Toronto'
}

def load_preferences():
    """Load preferences from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return DEFAULT_PREFERENCES.copy()
    return DEFAULT_PREFERENCES.copy()

def save_preferences(prefs):
    """Save preferences to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(prefs, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """Get current preferences"""
    prefs = load_preferences()
    return jsonify(prefs)

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    """Update preferences"""
    try:
        data = request.get_json()
        prefs = load_preferences()

        # Update only provided fields
        for key in ['measurement_system', 'date_format', 'time_format', 'language', 'timezone']:
            if key in data:
                prefs[key] = data[key]

        # Validate measurement_system
        if prefs['measurement_system'] not in ['metric', 'imperial']:
            return jsonify({'error': 'Invalid measurement system'}), 400

        if save_preferences(prefs):
            return jsonify({'success': True, 'preferences': prefs})
        else:
            return jsonify({'error': 'Failed to save preferences'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences/measurement-system', methods=['GET'])
def get_measurement_system():
    """Get measurement system preference only"""
    prefs = load_preferences()
    return jsonify({'measurement_system': prefs['measurement_system']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8107)
```

**Systemd Service:**

**File:** `/etc/systemd/system/d3kos-preferences-api.service`

```ini
[Unit]
Description=d3kOS User Preferences API
After=network.target

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/config
ExecStart=/usr/bin/python3 /opt/d3kos/services/config/preferences-api.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Nginx proxy:**

Add to `/etc/nginx/sites-enabled/default`:

```nginx
location /api/preferences {
    proxy_pass http://localhost:8107/api/preferences;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## COMPONENT UPDATES

### 1. Dashboard (index.html)

**Current code (example):**
```javascript
document.getElementById('engine-temp').textContent = temp + '°F';
```

**Updated code:**
```javascript
// Include units.js
document.getElementById('engine-temp').textContent = Units.temperature.toDisplay(temp);

// Listen for preference changes
window.addEventListener('measurementSystemChanged', function() {
  updateAllDisplays();
});
```

**All gauges to update:**
- Engine temperature (°F → °C)
- Oil pressure (PSI → Bar)
- Coolant temperature (°F → °C)
- Fuel level (gallons → liters)
- Battery voltage (stays same)
- Engine RPM (stays same)
- Speed (knots → knots + km/h)
- Heading (degrees, stays same)

### 2. Onboarding Wizard (onboarding.html)

**Steps requiring updates:**

**Step 5: Engine Make**
- No change (text input)

**Step 6: Engine Model**
- No change (text input)

**Step 7: Engine Year**
- No change (numeric input)

**Step 8: Number of Cylinders**
- No change (dropdown)

**Step 9: Engine Size**
```javascript
// Add unit toggle
<label for="engine-size">Engine Size:</label>
<input type="number" id="engine-size" step="0.1">
<select id="engine-size-unit" onchange="convertEngineSize()">
  <option value="ci">Cubic Inches</option>
  <option value="L">Liters</option>
</select>

// Default based on preference
window.addEventListener('DOMContentLoaded', function() {
  const system = Units.getPreference();
  document.getElementById('engine-size-unit').value = system === 'metric' ? 'L' : 'ci';
});
```

**Step 10: Engine Power**
```javascript
<label for="engine-power">Engine Power:</label>
<input type="number" id="engine-power">
<select id="engine-power-unit">
  <option value="HP">Horsepower (HP)</option>
  <option value="kW">Kilowatts (kW)</option>
</select>
```

**Step 11: Compression Ratio**
- No change (ratio stays same)

**Step 12: Idle RPM**
- No change (RPM stays same)

**Step 13: Max RPM**
- No change (RPM stays same)

**Step 14: Engine Type**
- No change (dropdown)

**Step 15: Boat Origin** ⭐ **AUTO-DEFAULT TRIGGER**
```javascript
// When user selects boat origin, auto-set measurement preference
document.getElementById('boat-origin').addEventListener('change', function() {
  const origin = this.value;
  let measurementSystem = 'imperial'; // Default

  // Metric regions
  const metricRegions = [
    'Europe', 'Asia', 'Oceania', 'Africa', 'South America',
    'United Kingdom', 'Germany', 'France', 'Italy', 'Spain',
    'Netherlands', 'Australia', 'New Zealand', 'Japan', 'China'
  ];

  // Imperial regions
  const imperialRegions = [
    'United States', 'Canada' // Canada uses mixed but default to imperial for marine
  ];

  // Auto-set based on region
  if (metricRegions.includes(origin)) {
    measurementSystem = 'metric';
  } else if (imperialRegions.includes(origin)) {
    measurementSystem = 'imperial';
  }

  // Save preference (will be used throughout system)
  Units.setPreference(measurementSystem);
  localStorage.setItem('d3kos-measurement-system', measurementSystem);

  console.log(`Boat origin: ${origin} → Measurement system: ${measurementSystem}`);
});
```

**Note:** User can change this later in Settings → Measurement System

**Step 16: Engine Position**
- No change (dropdown)

**Note:** Store all values in standard units (imperial) in backend, convert for display only.

### 3. Voice Assistant Integration

**File:** `/opt/d3kos/services/ai/query_handler.py`

**Add unit conversion to responses:**

```python
def format_quick_answer(self, query_type, boat_status):
    """Format quick answer with user's preferred units"""

    # Get user preference
    prefs = self.load_user_preferences()
    system = prefs.get('measurement_system', 'imperial')

    if query_type == 'rpm':
        rpm = boat_status.get('rpm', 'N/A')
        return f"The current RPM is {rpm}."  # RPM same in both

    elif query_type == 'oil':
        psi = boat_status.get('oil_pressure', 'N/A')
        if system == 'metric':
            bar = float(psi) * 0.0689476
            return f"Oil pressure is currently {bar:.2f} bar."
        return f"Oil pressure is currently {psi} PSI."

    elif query_type == 'temperature':
        temp_f = boat_status.get('coolant_temp', 'N/A')
        if system == 'metric':
            temp_c = (float(temp_f) - 32) * 5 / 9
            return f"Coolant temperature is {temp_c:.1f} degrees Celsius, which is normal."
        return f"Coolant temperature is {temp_f} degrees Fahrenheit, which is normal."

    elif query_type == 'fuel':
        gallons = boat_status.get('fuel_level', 'N/A')
        if system == 'metric':
            liters = float(gallons) * 3.78541
            return f"Fuel level is at {liters:.1f} liters ({gallons}% capacity)."
        return f"Fuel level is at {gallons} gallons."

    elif query_type == 'speed':
        knots = boat_status.get('speed', 'N/A')
        if system == 'metric':
            kmh = float(knots) * 1.852
            return f"Current speed is {knots} knots, which is {kmh:.1f} kilometers per hour."
        mph = float(knots) * 1.15078
        return f"Current speed is {knots} knots, which is {mph:.1f} miles per hour."

    # ... other query types

def load_user_preferences(self):
    """Load user preferences from config file"""
    try:
        with open('/opt/d3kos/config/user-preferences.json', 'r') as f:
            return json.load(f)
    except:
        return {'measurement_system': 'imperial'}
```

**Gemini API Integration:**

When implementing v0.9.3, add system message:

```javascript
const systemMessage = `You are a marine assistant for d3kOS.
The user prefers ${measurementSystem} units.
Always use ${measurementSystem === 'metric' ? 'Celsius, meters, liters, bar' : 'Fahrenheit, feet, gallons, PSI'} in your responses.`;
```

### 4. Navigation Page (navigation.html)

**Current displays:**
- Position: Latitude/Longitude (stays same)
- Speed: Knots (add secondary unit)
- Heading: Degrees (stays same)
- Altitude: Feet → Meters

**Updates:**
```javascript
document.getElementById('speed').textContent = Units.speed.toDisplay(speedKnots);
document.getElementById('altitude').textContent = Units.length.toDisplay(altitudeFeet);
```

### 5. Weather Page (weather.html)

**Current displays:**
- Temperature: Fahrenheit → Celsius
- Wind speed: Knots (add secondary)
- Precipitation: Inches → mm

**Updates:**
```javascript
document.getElementById('current-temp').textContent = Units.temperature.toDisplay(tempF);
document.getElementById('wind-speed').textContent = Units.speed.toDisplay(windKnots);
```

### 6. Boatlog Entries

**Current storage:** All in imperial units (Fahrenheit, PSI, etc.)

**Display:** Convert on retrieval based on user preference

```javascript
// When displaying boatlog entry
function displayBoatlogEntry(entry) {
  const temp = Units.temperature.toDisplay(entry.temperature);
  const pressure = Units.pressure.toDisplay(entry.oil_pressure);
  // ... etc
}
```

**Note:** Do NOT convert stored data. Always store in standard units (imperial), convert only for display.

### 7. Data Export

**File:** `/opt/d3kos/services/export/export-manager.py`

**Add preference to export:**

```python
def export_all_data(self):
    """Export all data with unit preferences"""

    # Load preferences
    prefs = self.load_preferences()
    measurement_system = prefs.get('measurement_system', 'imperial')

    export_data = {
        'metadata': {
            'installation_id': self.installation_id,
            'export_timestamp': datetime.now().isoformat(),
            'measurement_system': measurement_system,
            'units': {
                'temperature': 'celsius' if measurement_system == 'metric' else 'fahrenheit',
                'pressure': 'bar' if measurement_system == 'metric' else 'psi',
                'volume': 'liters' if measurement_system == 'metric' else 'gallons',
                'distance': 'kilometers' if measurement_system == 'metric' else 'nautical_miles'
            }
        },
        'data': {
            # ... exported data
        }
    }
```

**Include conversion formulas in export:**
```json
{
  "conversion_info": {
    "note": "All values stored in imperial units, converted to metric for display",
    "formulas": {
      "temperature": "°C = (°F - 32) × 5/9",
      "pressure": "bar = PSI × 0.0689476",
      "volume": "L = gal × 3.78541"
    }
  }
}
```

---

## IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1 - 40 hours)

**Tasks:**
1. ✅ Create `units.js` conversion utility module (8 hours)
   - All conversion functions
   - Event system for preference changes
   - Testing with sample data

2. ✅ Create preferences API backend (8 hours)
   - Flask service (port 8107)
   - Config file storage
   - Systemd service
   - Nginx proxy

3. ✅ Add Settings UI toggle (4 hours)
   - Preferences section in Settings
   - Toggle switch component
   - Save/load functionality

4. ✅ Testing infrastructure (4 hours)
   - Unit tests for conversions
   - Accuracy verification
   - Edge case testing

5. ✅ Documentation (4 hours)
   - User guide
   - Developer documentation
   - API documentation

**Deliverable:** Working preferences system with API

---

### Phase 2: Dashboard & Forms (Week 2 - 40 hours)

**Tasks:**
1. ✅ Update Dashboard displays (12 hours)
   - All gauges (engine, tanks, system)
   - Real-time updates
   - Event listeners for preference changes

2. ✅ Update Onboarding Wizard (12 hours)
   - Engine size input with unit dropdown
   - Power input with unit dropdown
   - All 20 steps reviewed
   - Form validation updates

3. ✅ Update Navigation page (4 hours)
   - Speed display
   - Altitude display
   - Distance calculations

4. ✅ Update Weather page (4 hours)
   - Temperature display
   - Wind speed display

5. ✅ Testing (8 hours)
   - All forms tested
   - All displays tested
   - User acceptance testing

**Deliverable:** All UI components support unit preference

---

### Phase 3: Voice & Data (Week 3 - 40 hours)

**Tasks:**
1. ✅ Update Voice Assistant (16 hours)
   - query_handler.py unit conversions
   - All response types updated
   - Preference loading
   - Testing with real queries

2. ✅ Update Boatlog display (8 hours)
   - Entry display conversion
   - Historical data handling

3. ✅ Update Export system (8 hours)
   - Metadata with unit preference
   - Conversion formulas in export
   - Testing export/import

4. ✅ Integration testing (8 hours)
   - End-to-end user flow
   - Voice → Display → Export consistency
   - Performance testing

**Deliverable:** Complete system-wide unit preference support

---

## TESTING CHECKLIST

### Unit Conversion Tests:
- [ ] Temperature: 32°F = 0°C, 212°F = 100°C, 185°F = 85°C
- [ ] Pressure: 45 PSI = 3.1 bar, 14.7 PSI = 1 bar
- [ ] Speed: 10 knots = 18.52 km/h, 10 knots = 11.51 mph
- [ ] Distance: 10 nm = 18.52 km
- [ ] Depth: 20 ft = 6.1 m
- [ ] Fuel: 50 gal = 189.3 L
- [ ] Length: 24 ft = 7.32 m
- [ ] Weight: 1000 lbs = 453.6 kg
- [ ] Displacement: 350 ci = 5.7 L

### UI Tests:
- [ ] Settings toggle switches between metric/imperial
- [ ] Dashboard updates immediately on preference change
- [ ] Onboarding wizard shows correct units in dropdowns
- [ ] Voice responses use correct units
- [ ] Navigation page shows correct units
- [ ] Weather page shows correct units
- [ ] Boatlog entries display in correct units

### Data Integrity Tests:
- [ ] Stored data remains in imperial (standard format)
- [ ] Export includes unit preference metadata
- [ ] Import handles different unit preferences
- [ ] Historical data converts correctly

### Edge Cases:
- [ ] Preference change while viewing dashboard (live update)
- [ ] Preference change mid-conversation with voice assistant
- [ ] Multiple rapid preference changes
- [ ] Invalid preference values rejected
- [ ] Missing preference file defaults to imperial

---

## USER EXPERIENCE EXAMPLES

### Example 1: Canadian User (Metric Preference)

**Setup:**
1. During onboarding, user is prompted: "Choose measurement system"
2. User selects: Metric
3. System stores preference

**Usage:**
- Dashboard shows: "Engine Temp: 85°C" (instead of 185°F)
- Voice query: "Helm, what's the oil pressure?"
- Voice response: "Oil pressure is currently 3.1 bar." (instead of 45 PSI)
- Onboarding: Engine size entered as "5.7 L" (instead of 350 ci)

### Example 2: US User (Imperial Preference)

**Setup:**
1. Default system: Imperial (no change needed)
2. User skips preference setup

**Usage:**
- Dashboard shows: "Engine Temp: 185°F"
- Voice query: "Helm, what's the fuel level?"
- Voice response: "Fuel level is at 25 gallons."
- Onboarding: Engine size entered as "350 ci"

### Example 3: Switching Preferences

**Scenario:** User initially set up with imperial, wants to switch to metric

**Steps:**
1. Navigate to Settings → Preferences
2. Toggle "Measurement System" from Imperial → Metric
3. System shows notification: "Measurement system updated to metric"
4. Dashboard immediately updates all displays to metric units
5. Next voice query responds in metric

**Result:** Seamless transition, all components updated instantly

---

## BACKWARD COMPATIBILITY

### Historical Data:
- All existing boatlog entries stored in imperial units
- Displayed in user's preferred units (converted on retrieval)
- Export includes conversion formulas

### Existing Installations:
- Default to imperial if no preference set
- First Settings visit prompts user to set preference
- No data migration required

### API Compatibility:
- Signal K data remains in standard units (Kelvin for temp, meters per second for speed)
- Only d3kOS display layer converts units
- External integrations (OpenCPN, etc.) unaffected

---

## FUTURE ENHANCEMENTS (Keep Simple for Now)

### Phase 4 (Future - Optional):

1. **Unit Display Options:**
   - Show both units: "185°F (85°C)"
   - Primary + secondary: "85°C (185°F)" with metric as primary
   - Currently: Show only user's preferred unit (simpler)

2. **Voice Unit Specification:**
   - "Helm, what's the temperature in Celsius?" (override preference)
   - "Helm, convert 350 cubic inches to liters"
   - Currently: Always use user's preference (simpler)

3. **GPS-Based Suggestion:**
   - Detect user location via GPS
   - Suggest measurement system if boat origin not set
   - Currently: Use boat origin from onboarding (simpler)

**Note:** User wants to keep it simple - "American boaters vs the world"
- Just Imperial vs Metric
- No mixed units
- No complex regional presets
- Auto-default based on boat origin
- User can change anytime in Settings

---

## COST & TIME ESTIMATES

### Development Time:
- **Phase 1 (Foundation):** 40 hours (1 week)
- **Phase 2 (Dashboard & Forms):** 40 hours (1 week)
- **Phase 3 (Voice & Data):** 40 hours (1 week)
- **Total:** 120 hours (3 weeks)

### Development Cost:
- 120 hours × $50-150/hour = **$6,000 - $18,000**

### Testing Time:
- Unit testing: 8 hours
- Integration testing: 8 hours
- User acceptance testing: 8 hours
- **Total:** 24 hours

### Documentation Time:
- User guide: 4 hours
- Developer documentation: 4 hours
- API documentation: 2 hours
- **Total:** 10 hours

### Grand Total:
- **Time:** 154 hours (~4 weeks with one developer)
- **Cost:** $7,700 - $23,100

---

## RISKS & MITIGATIONS

### Risk 1: Conversion Accuracy
**Risk:** Floating point precision errors in conversions
**Impact:** Incorrect measurements displayed (safety concern)
**Mitigation:**
- Use established conversion constants (not rounded)
- Round only for display, not internal calculations
- Extensive unit testing with known values

### Risk 2: Performance Impact
**Risk:** Real-time conversion adds latency
**Impact:** Slower dashboard updates
**Mitigation:**
- Conversions are simple math (microseconds)
- Cache preference to avoid repeated lookups
- Update only changed values

### Risk 3: Historical Data Confusion
**Risk:** Users confused why old data shows different values after switching units
**Impact:** User thinks data was corrupted or lost
**Mitigation:**
- Clear messaging: "Historical data converted to your preferred units"
- Show unit preference at time of recording (optional metadata)
- Include note in export: "Data stored in imperial, displayed in metric"

### Risk 4: Voice Response Inconsistency
**Risk:** User switches preference mid-conversation, voice uses wrong units
**Impact:** Confusing responses
**Mitigation:**
- Load preference at start of each query (not cached across queries)
- Include unit in response: "3.1 bar" not just "3.1"

### Risk 5: Form Validation Errors
**Risk:** User enters value in wrong unit, system rejects
**Impact:** Onboarding blocked
**Mitigation:**
- Unit dropdown always visible next to input
- Validation checks unit before comparing ranges
- Clear error messages: "Engine size must be 2-10 L or 122-610 ci"

---

## SUCCESS CRITERIA

### Technical Success:
✅ All conversions accurate to 2 decimal places
✅ Settings toggle works on all pages
✅ Voice responses use correct units
✅ Dashboard updates in real-time on preference change
✅ No performance degradation (< 1ms conversion time)
✅ Zero data corruption (stored values unchanged)

### User Success:
✅ User can switch preference in < 30 seconds
✅ All displays consistent across system
✅ Voice responses natural and clear
✅ Forms accept input in preferred units
✅ Export includes unit metadata

### Business Success:
✅ Feature enables international distribution (Canada, Europe)
✅ Positive user feedback (> 4.5/5 stars)
✅ No support tickets related to unit confusion
✅ Zero safety incidents from incorrect measurements

---

## DEPLOYMENT PLAN

### Step 1: Development (3 weeks)
- Build all components per phases above
- Internal testing on development system
- Test with both imperial and metric throughout

### Step 2: Beta Testing (1 week)
- Deploy to 10 beta testers:
  - 5 metric users (Europe/Canada/Australia)
  - 5 imperial users (USA)
- Test onboarding auto-default logic
- Test Settings toggle
- Collect feedback on accuracy and usability

### Step 3: Production Deployment (v0.9.1.2 → v0.9.2)
- Package as version update: **v0.9.2**
- Release notes: "Metric/Imperial measurement system support"
- Deploy to all installations via update system
- **Existing users:** Default to imperial (no change)
- **New users:** Auto-default based on boat origin
- Announcement: "New feature - Choose Imperial or Metric units in Settings"

### Step 4: Monitoring (2 weeks post-launch)
- Monitor for conversion accuracy issues
- Track preference adoption (% metric vs imperial by region)
- Collect user feedback
- Quick fixes if needed (v0.9.2.1 hotfix if required)

**Version Notes:**
- v0.9.1.2 (current) → v0.9.2 (with metric/imperial support)
- Next: v0.9.3 (Gemini API + Three-Tier AI)

---

## RECOMMENDATION

**Priority:** HIGH - Essential for international distribution ("American boaters vs the world")

**Target Version:** v0.9.1.2 → v0.9.2 (Current version - immediate implementation)

**Approach:** Simple Imperial vs Metric toggle
- Auto-default based on boat origin (Step 15 in onboarding)
- User can change anytime in Settings
- No complex presets, no mixed units
- Keep it simple

**Why Now (v0.9.2):**
- Blocks international distribution currently
- Simple enough to implement quickly (3 weeks)
- No dependencies on future features
- Can deploy immediately after testing

**Approval Needed:**
1. Budget approval: $6K-18K development cost
2. Timeline approval: 3 weeks development + 1 week testing
3. Beta tester recruitment: 10 users (5 metric/Europe, 5 imperial/USA)

---

## NEXT STEPS

1. **Review this plan** - Approve approach and scope
2. **Allocate budget** - Confirm funding for 120 hours development
3. **Schedule implementation** - v0.9.2.1 standalone or v0.9.3 combined?
4. **Recruit beta testers** - 5 Canadian/European users (metric), 5 US users (imperial)
5. **Begin Phase 1** - Create conversion utilities and preferences API

---

## APPENDICES

### A. Conversion Formula Reference
See Section "MARINE MEASUREMENT CONVERSIONS" above

### B. Component File Locations
- `/var/www/html/js/units.js` - Conversion utility (NEW)
- `/opt/d3kos/services/config/preferences-api.py` - Backend API (NEW)
- `/etc/systemd/system/d3kos-preferences-api.service` - Service file (NEW)
- `/opt/d3kos/config/user-preferences.json` - Preference storage (NEW)
- `/var/www/html/settings.html` - Settings UI (UPDATE)
- `/var/www/html/index.html` - Dashboard (UPDATE)
- `/var/www/html/onboarding.html` - Onboarding wizard (UPDATE)
- `/opt/d3kos/services/ai/query_handler.py` - Voice assistant (UPDATE)

### C. Port Assignment
- **Port 8107:** Preferences API (NEW)

### D. Related Documents
- Master Integration Reference (Section 4 - Microservice Inventory)
- Three-Tier AI Architecture Proposal (Gemini API will need unit awareness)
- Version Roadmap 2026 (v0.9.3 target)

---

**© 2026 AtMyBoat.com | Donald Moskaluk | skipperdon@atmyboat.com**

*d3kOS - AI-Powered Marine Electronics Platform*
*"Smarter Boating, Simpler Systems"*

---

**END OF IMPLEMENTATION PLAN**
