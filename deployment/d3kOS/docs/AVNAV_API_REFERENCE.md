# AvNav API Reference — Verified Live Responses
**Document:** `AVNAV_API_REFERENCE.md`
**Version:** 1.0.0
**Created:** 2026-03-13
**Source:** Live Pi 192.168.1.237, AvNav v20250822, Debian Trixie

---

## CRITICAL: Key Names Differ From Original Spec

The original `AVNAV_INSTALL_AND_API.md` spec listed keys like `gps.lat`, `gps.lon`, `gps.speed`.
**These are WRONG.** The actual AvNav v20250822 API uses Signal K path notation.

| Original Spec Key | Actual Key (verified) |
|---|---|
| `gps.lat` | `signalk.navigation.position.latitude` |
| `gps.lon` | `signalk.navigation.position.longitude` |
| `gps.speed` | `signalk.navigation.speedOverGround` |
| `gps.track` | `signalk.navigation.courseOverGroundTrue` |
| `request=navigate` | **NOT VALID** — use `request=gps` |

---

## Base URL

```
http://localhost:8080/viewer/avnav_navi.php
```

All requests use **POST**.

---

## request=gps — Live Navigation Data

### Request
```bash
curl -s -X POST http://localhost:8080/viewer/avnav_navi.php \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'request=gps'
```

### Actual Response (Pi, 2026-03-13)
```json
{
  "updatealarm": 75259.543743395,
  "updateleg": 75260.543768135,
  "updateroute": 75259.543780561,
  "updateconfig": 75259.543788857,
  "version": "20250822",
  "signalk": {
    "environment": {
      "rpi": {
        "gpu": { "temperature": 334.45 },
        "cpu": {
          "temperature": 335.96,
          "utilisation": 0.13,
          "core": {
            "1": { "utilisation": 0.15 },
            "2": { "utilisation": 0.11 },
            "3": { "utilisation": 0.14 },
            "4": { "utilisation": 0.10 }
          }
        },
        "memory": { "utilisation": 0.27 },
        "sd": { "utilisation": 0.32 }
      }
    },
    "propulsion": {
      "port": {
        "revolutions": 0,
        "drive": { "trimState": 0 },
        "boostPressure": 143000
      }
    },
    "navigation": {
      "position": {
        "latitude": 43.68619666666667,
        "longitude": -79.52087666666667
      },
      "courseOverGroundTrue": 0,
      "speedOverGround": 0,
      "magneticVariation": 0.18151424224885535,
      "magneticVariationAgeOfService": 1773417282,
      "datetime": "2026-03-13T15:54:42.000Z",
      "gnss": {
        "satellitesInView": {
          "count": 16,
          "gnss": "GPS",
          "satellites": []
        }
      }
    }
  }
}
```

### Key Access Pattern for Phase 5 Code

```python
import requests

AVNAV_API = "http://localhost:8080/viewer/avnav_navi.php"

def get_nav_data() -> dict:
    """Get live navigation state from AvNav API."""
    try:
        r = requests.post(AVNAV_API, data={"request": "gps"}, timeout=3)
        return r.json()
    except Exception:
        return {}

def get_gps_position(data: dict) -> tuple:
    """Extract (lat, lon) from AvNav gps response. Returns (None, None) if unavailable."""
    sk = data.get("signalk", {})
    nav = sk.get("navigation", {})
    pos = nav.get("position", {})
    return pos.get("latitude"), pos.get("longitude")

def get_speed_kts(data: dict) -> float | None:
    """Get speed over ground in knots. AvNav returns m/s."""
    sk = data.get("signalk", {})
    sog_ms = sk.get("navigation", {}).get("speedOverGround")
    return round(sog_ms * 1.94384, 1) if sog_ms is not None else None

def get_cog(data: dict) -> float | None:
    """Get course over ground in degrees true."""
    sk = data.get("signalk", {})
    return sk.get("navigation", {}).get("courseOverGroundTrue")

# Example usage
data = get_nav_data()
lat, lon = get_gps_position(data)
speed = get_speed_kts(data)
cog = get_cog(data)
```

---

## request=status — Handler Status

### Request
```bash
curl -s -X POST http://localhost:8080/viewer/avnav_navi.php \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'request=status'
```

Returns JSON with `handler` array containing all AvNav handler states.
Each handler has: `name`, `configname`, `config`, `info.items[].status`, `info.items[].info`.

**Signal K handler connected:**
```
SignalKHandler: NMEA connected at http://localhost:8099/signalk/v1/api/
```

---

## request=list&type=route — List Routes

```bash
curl -s -X POST http://localhost:8080/viewer/avnav_navi.php \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'request=list&type=route'
```

---

## request=list&type=track — List Tracks

```bash
curl -s -X POST http://localhost:8080/viewer/avnav_navi.php \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'request=list&type=track'
```

---

## File-Based Access (Preferred for Routes and Tracks)

```
AVNAV_DATA_DIR = /var/lib/avnav

Routes:        /var/lib/avnav/routes/          ← GPX route files
CurrentLeg:    /var/lib/avnav/routes/currentLeg.json
Tracks:        /var/lib/avnav/tracks/          ← daily GPX files (YYYY-MM-DD.gpx)
Charts:        /var/lib/avnav/charts/
```

```python
from pathlib import Path
import json

AVNAV_DATA = Path("/var/lib/avnav")

def get_current_leg() -> dict:
    """Read active route/waypoint from AvNav currentLeg.json."""
    leg_file = AVNAV_DATA / "routes" / "currentLeg.json"
    if leg_file.exists():
        return json.loads(leg_file.read_text())
    return {}

def get_latest_track_gpx() -> str:
    """Return GPX text of today's track file."""
    from datetime import date
    today = date.today().isoformat()  # YYYY-MM-DD
    track_file = AVNAV_DATA / "tracks" / f"{today}.gpx"
    if track_file.exists():
        return track_file.read_text()
    return ""
```

---

## Installation Notes (Pi-specific)

- **AvNav version:** 20250822
- **Installed from:** `http://www.free-x.de/debian trixie main` (with `[trusted=yes arch=arm64]`)
- **OS:** Debian GNU/Linux 13 (Trixie), Python 3.13.5
- **Patch applied:** `/usr/lib/avnav/server/handler/httphandler.py` line 108 — replaced `cgi.parse_qs()` with `urllib.parse.parse_qs()` (cgi.parse_qs removed in Python 3.13)
- **Signal K port:** 8099 (set in `/var/lib/avnav/avnav_server.xml` — `AVNSignalKHandler port="8099"`)
- **ai_api.py moved:** Port 8080 → 8089 to free port for AvNav. Nginx `/ai/` proxy updated to 8089.
- **Data dir:** `/var/lib/avnav/`
- **Service:** `avnav.service` (enabled, starts at boot)

---

*Version 1.0.0 — Written 2026-03-13*
*Verified on live Pi at 192.168.1.237*
