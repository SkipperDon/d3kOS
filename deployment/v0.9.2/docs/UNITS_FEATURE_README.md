# d3kOS Measurement System — v0.9.2

## Overview
d3kOS supports Imperial and Metric unit display. All sensor data is stored in imperial
units internally. Metric is display-only conversion — no data is altered.

## How to Switch Units
1. Open **Settings** → `http://<pi-ip>/settings.html`
2. Find the **Measurement System** section
3. Toggle the switch between **Imperial** and **Metric**
4. Page reloads automatically — all displays update immediately

## Unit Mappings

| Measurement        | Imperial | Metric |
|--------------------|----------|--------|
| Temperature        | °F       | °C     |
| Pressure           | PSI      | bar    |
| Speed (secondary)  | mph      | km/h   |
| Distance           | nm       | km     |
| Depth              | ft       | m      |
| Fuel volume        | gal      | L      |
| Length             | ft       | m      |
| Weight             | lb       | kg     |
| Engine displacement| ci       | L      |

Speed is always shown in knots as primary, with the secondary unit in brackets:
`10.0 kts (11.5 mph)` or `10.0 kts (18.5 km/h)`

## Automatic Default (Onboarding)
During the onboarding wizard, selecting a boat origin in Europe, Asia, Australia,
South America, or Africa automatically sets Metric as the default.
US/Canada origins default to Imperial.

## Affected Pages
- Dashboard (`dashboard.html`) — temperature and oil pressure gauges
- Helm AI (`helm.html`) — voice/chat responses for engine status
- Navigation (`navigation.html`) — speed over ground, depth
- Weather (`weather.html`) — temperature units in Windy map
- Settings (`settings.html`) — the toggle itself
- Onboarding (`onboarding.html`) — auto-detection by boat origin

## Technical Notes
- Preference stored in: `localStorage['d3kos-measurement-system']`
- Preference also saved to: `/opt/d3kos/config/user-preferences.json`
- API endpoint: `GET/POST http://<pi-ip>/api/preferences`
- JavaScript library: `/js/units.js` — loaded on all pages
- Default: **Imperial**
