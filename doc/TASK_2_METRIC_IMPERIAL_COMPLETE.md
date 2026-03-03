# Task 2: Metric/Imperial Conversion - COMPLETE Implementation

**Executor:** Ollama
**Timeline:** 3 weeks (120 hours)
**Status:** Ready to execute

## Week 1: Foundation (16 hours)

### Create units.js
File: `/var/www/html/js/units.js`

9 function pairs (18 functions total):
- temperatureToC/ToF, pressureToBar/ToPSI, knotsToKmh/ToMph
- distanceToKm/ToNm, depthToMeters/ToFeet, fuelToLiters/ToGallons
- lengthToMeters/ToFeet, weightToKg/ToLb, displacementToLiters/ToCi

### Extend Preferences API
File: `/opt/d3kos/services/preferences/preferences-api.py`
- Add measurement_system field ("imperial" or "metric")
- Update GET/POST endpoints
- Default: "imperial"

### Settings UI
File: `/var/www/html/settings.html`
- Add Measurement System toggle
- Live update (no reload)

## Week 2: UI Updates (24 hours)

Update 5 pages to use units.js:
1. `/var/www/html/index.html` - Dashboard (temp, pressure, fuel, speed)
2. `/var/www/html/onboarding.html` - Step 15 auto-default, Step 9/10 dropdowns
3. `/var/www/html/navigation.html` - Speed, altitude
4. `/var/www/html/weather.html` - Temp, wind speed
5. `/var/www/html/boatlog.html` - Display only (storage unchanged)

## Week 3: Voice & Testing (24 hours)

### Voice Assistant
File: `/opt/d3kos/services/ai/query_handler.py`
- Load user preference
- Convert all responses to preferred units

### Testing
- 47 unit tests (all conversions)
- Accuracy: ±0.1 tolerance
- Performance: < 1ms per conversion
- Integration: All pages update live
- Voice: Responses in correct units

## Deployment

```bash
# On Pi
cd /home/boatiq/Helm-OS
git add var/www/html/js/units.js
git add var/www/html/*.html
git add opt/d3kos/services/preferences/
git add opt/d3kos/services/ai/query_handler.py
git commit -m "feat(v0.9.2): Metric/Imperial conversion system

- units.js: 9 conversion types (18 functions)
- Preferences API: measurement_system field
- Settings: Live toggle switch
- Dashboard/Onboarding/Navigation/Weather/Boatlog: Unit display
- Voice: Responses in preferred units
- Auto-default: USA/Canada=Imperial, Rest=Metric
- Tests: 47 unit tests, 100% pass, <1ms performance"

git tag v0.9.2
```

## Acceptance Criteria
- ✅ All 9 conversions working
- ✅ All 5 pages updated
- ✅ Settings toggle works
- ✅ Voice responses correct
- ✅ 47 tests pass
- ✅ Git committed, tagged v0.9.2
- ✅ Nothing hanging
