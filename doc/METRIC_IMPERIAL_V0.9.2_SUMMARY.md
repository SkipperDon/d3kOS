# Metric/Imperial Support - v0.9.2 Implementation Summary

**Date:** March 1, 2026 **Version:** v0.9.1.2 → v0.9.2 **Priority:** HIGH - "American boaters vs the world" **Timeline:** 3 weeks development + 1 week testing = 4 weeks total


## QUICK SUMMARY

**What:** Simple Imperial/Metric toggle affecting entire system **Where:** Settings → Measurement System (toggle switch) **Default:** Auto-set based on boat origin during onboarding **User Control:** Can change anytime in Settings


## AUTO-DEFAULT LOGIC

**During Onboarding (Step 15 - Boat Origin):**

| Region Selected | Default System |
| - | - |
| **United States** | Imperial |
| **Canada** | Imperial |
| **Europe** | Metric |
| **Asia** | Metric |
| **Oceania** | Metric |
| **Africa** | Metric |
| **South America** | Metric |


**User can always change in Settings later**


## WHAT CHANGES

### Displays Affected:

- ✅ Dashboard (engine temp, oil pressure, fuel, etc.)

- ✅ Onboarding wizard (engine size, power inputs)

- ✅ Voice assistant responses

- ✅ Navigation page (speed, altitude)

- ✅ Weather page (temperature, wind)

- ✅ Boatlog entries (display only)

- ✅ Export data (includes unit metadata)

### Conversions:

| Measurement | Imperial | Metric |
| - | - | - |
| Temperature | °F | °C |
| Pressure | PSI | Bar |
| Speed | Knots (+ MPH) | Knots (+ km/h) |
| Distance | Nautical miles | Kilometers |
| Depth | Feet | Meters |
| Fuel | Gallons | Liters |
| Length | Feet | Meters |
| Weight | Pounds | Kilograms |
| Displacement | Cubic inches | Liters |



## IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (Week 1)

- [ ] Create `/var/www/html/js/units.js` (conversion utility)

- [ ] Create `/opt/d3kos/services/config/preferences-api.py` (Port 8107)

- [ ] Create `/etc/systemd/system/d3kos-preferences-api.service`

- [ ] Add nginx proxy: `/api/preferences` → `localhost:8107`

- [ ] Add Settings UI toggle (simple green/grey switch)

- [ ] Test all conversion formulas (accuracy verification)

### Phase 2: Dashboard & Forms (Week 2)

- [ ] Update `/var/www/html/index.html` (dashboard gauges)

- [ ] Update `/var/www/html/onboarding.html` (Step 15 auto-default logic)

- [ ] Update `/var/www/html/onboarding.html` (Steps 9, 10 - engine size/power)

- [ ] Update `/var/www/html/navigation.html` (speed, altitude)

- [ ] Update `/var/www/html/weather.html` (temperature, wind)

- [ ] Add event listener for preference changes (live updates)

- [ ] Test all forms and displays

### Phase 3: Voice & Data (Week 3)

- [ ] Update `/opt/d3kos/services/ai/query\_handler.py` (unit conversions)

- [ ] Update all response types (rpm, oil, temp, fuel, speed, etc.)

- [ ] Update boatlog display (convert on retrieval)

- [ ] Update export system (include unit metadata)

- [ ] Integration testing (voice → display → export consistency)

### Phase 4: Testing & Deployment (Week 4)

- [ ] Beta test with 5 metric users + 5 imperial users

- [ ] Test onboarding auto-default logic

- [ ] Test Settings toggle (live updates)

- [ ] Accuracy verification (all conversions)

- [ ] Performance testing (\< 1ms conversion time)

- [ ] Package as v0.9.2 update

- [ ] Deploy to production


## KEY FILES

### New Files:

1. `/var/www/html/js/units.js` - Conversion utility module

2. `/opt/d3kos/services/config/preferences-api.py` - Backend API (Port 8107)

3. `/opt/d3kos/config/user-preferences.json` - Preference storage

4. `/etc/systemd/system/d3kos-preferences-api.service` - Service file

### Modified Files:

1. `/var/www/html/settings.html` - Add toggle switch

2. `/var/www/html/index.html` - Dashboard conversions

3. `/var/www/html/onboarding.html` - Auto-default logic + unit dropdowns

4. `/var/www/html/navigation.html` - Speed/altitude conversions

5. `/var/www/html/weather.html` - Temperature/wind conversions

6. `/opt/d3kos/services/ai/query\_handler.py` - Voice response conversions

7. `/opt/d3kos/services/export/export-manager.py` - Unit metadata

8. `/etc/nginx/sites-enabled/default` - Add `/api/preferences` proxy


## CODE EXAMPLES

### 1. Auto-Default (Onboarding Step 15)

```
// In onboarding.html, after boat origin selection  
document.getElementById('boat-origin').addEventListener('change', function() \{  
  const origin = this.value;  
  const metricRegions = \['Europe', 'Asia', 'Oceania', 'Africa', 'South America'\];  
  const measurementSystem = metricRegions.includes(origin) ? 'metric' : 'imperial';  
  
  Units.setPreference(measurementSystem);  
  localStorage.setItem('d3kos-measurement-system', measurementSystem);  
\});
```

### 2. Dashboard Display (index.html)

```
// Before (hardcoded imperial)  
document.getElementById('engine-temp').textContent = temp + '°F';  
  
// After (user preference)  
document.getElementById('engine-temp').textContent = Units.temperature.toDisplay(temp);
```

### 3. Voice Assistant (query\_handler.py)

```
\# Before (hardcoded imperial)  
return f"Oil pressure is currently \{psi\} PSI."  
  
\# After (user preference)  
prefs = self.load\_user\_preferences()  
if prefs.get('measurement\_system') == 'metric':  
    bar = float(psi) \* 0.0689476  
    return f"Oil pressure is currently \{bar:.2f\} bar."  
return f"Oil pressure is currently \{psi\} PSI."
```

### 4. Settings Toggle (settings.html)

```
\<div class="settings-section"\>  
  \<h2\>Measurement System\</h2\>  
  \<div class="setting-row"\>  
    \<label class="toggle-switch"\>  
      \<input type="checkbox" id="measurement-system-toggle" onchange="changeMeasurementSystem()"\>  
      \<span class="toggle-slider"\>\</span\>  
    \</label\>  
    \<span id="measurement-system-label"\>Imperial\</span\>  
  \</div\>  
  \<p\>Default set based on boat origin. Affects all displays and voice responses.\</p\>  
\</div\>
```


## TESTING CRITERIA

### Must Pass:

- [ ] Temperature: 185°F = 85°C (±0.1°C)

- [ ] Pressure: 45 PSI = 3.10 bar (±0.01 bar)

- [ ] Speed: 10 knots = 18.52 km/h (±0.1 km/h)

- [ ] Fuel: 50 gal = 189.3 L (±0.1 L)

- [ ] Dashboard updates instantly when preference changed

- [ ] Voice responses use correct units

- [ ] Onboarding auto-defaults correctly for all regions

- [ ] Settings toggle switches between Imperial/Metric

- [ ] No performance degradation (\< 1ms conversion)

- [ ] Stored data unchanged (always in imperial)


## USER EXPERIENCE

### Example 1: European User (Auto-Default Metric)

**Onboarding:**

- Step 15: Select "Europe" as boat origin

- System auto-sets: Metric

- Engine size input: "5.7 L" (dropdown shows Liters)

- No additional setup needed

**Usage:**

- Dashboard: "Engine Temp: 85°C, Oil Pressure: 3.1 bar"

- Voice: "Helm, what's the fuel level?" → "Fuel level is 189 liters"

- Settings: Can change to Imperial anytime

### Example 2: American User (Auto-Default Imperial)

**Onboarding:**

- Step 15: Select "United States" as boat origin

- System auto-sets: Imperial

- Engine size input: "350 ci" (dropdown shows Cubic Inches)

- No additional setup needed

**Usage:**

- Dashboard: "Engine Temp: 185°F, Oil Pressure: 45 PSI"

- Voice: "Helm, what's the fuel level?" → "Fuel level is 50 gallons"

- Settings: Can change to Metric anytime

### Example 3: Changing Preference

**Steps:**

1. Navigate to Settings

2. Find "Measurement System" section

3. Toggle switch: Imperial → Metric (green light)

4. Page refreshes

5. All displays now show metric units

6. Voice assistant uses metric in next query


## COST & TIMELINE

**Development:** 120 hours = 3 weeks

- Phase 1: 40 hours (conversion utilities, API, Settings UI)

- Phase 2: 40 hours (dashboard, forms, navigation, weather)

- Phase 3: 40 hours (voice assistant, boatlog, export)

**Testing:** 24 hours = 1 week

- Unit testing: 8 hours

- Integration testing: 8 hours

- Beta testing: 8 hours

**Total:** 144 hours = 4 weeks **Cost:** $7,200 - $21,600 (at $50-150/hour)


## DEPLOYMENT

**Version:** v0.9.1.2 → **v0.9.2**

**Release Notes:**

> d3kOS v0.9.2 - Metric/Imperial Support

> New Features:

> - Measurement system preference (Imperial or Metric)

> - Auto-default based on boat origin

> - Affects all displays, forms, and voice responses

> - User can change anytime in Settings

> For international users: d3kOS now supports metric units! For American users: No change - defaults to imperial as before.

**Rollout:**

1. Package v0.9.2 update

2. Deploy to beta testers (10 users, 1 week)

3. Deploy to production (all installations)

4. Monitor for issues (2 weeks)

5. Hotfix v0.9.2.1 if needed


## SUCCESS METRICS

**Technical:**

- ✅ All conversions accurate (\< 0.1% error)

- ✅ Performance impact negligible (\< 1ms)

- ✅ Zero data corruption

**User:**

- ✅ Auto-default works 100% of time

- ✅ Settings toggle works reliably

- ✅ User satisfaction \> 4.5/5 stars

- ✅ Zero confusion about units

**Business:**

- ✅ Enables European distribution

- ✅ Enables Canadian distribution

- ✅ Enables Australian distribution

- ✅ "American boaters vs the world" - solved!


## NEXT STEPS

1. **Approve this plan** - Review implementation approach

2. **Allocate budget** - $7K-22K for 4 weeks work

3. **Begin Phase 1** - Create conversion utilities and API

4. **Recruit beta testers** - 5 metric + 5 imperial users

5. **Target completion** - April 1, 2026 (4 weeks from now)

After v0.9.2 completion → v0.9.3 (Gemini API + Three-Tier AI)


**Full Details:** See `METRIC\_IMPERIAL\_IMPLEMENTATION\_PLAN.md` (42KB)

**Questions?** Contact Donald Moskaluk - [skipperdon@atmyboat.com](mailto:skipperdon@atmyboat.com)


**© 2026 AtMyBoat.com | d3kOS v0.9.2 - International Marine Electronics**

