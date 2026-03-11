# Signal K Upgrade — v2.20.3 to v2.22.1

**Date:** 2026-03-08/09
**Status:** RESOLVED — stable at ~265MB, AIS confirmed working
**Problem:** Signal K at v2.20.3 had a memory leak in the AIS TCP NMEA0183 handler. With AIS enabled, SK heap grew continuously, reaching OOM within hours.

---

## What Changed in v2.22.1

The AIS TCP NMEA0183 memory leak was fixed upstream. At v2.22.1 with full stack (AIS, GPS, engine data, NMEA0183 output):
- Heap stable at ~265MB
- AIS data flowing correctly
- No memory growth observed over multi-hour sessions

---

## Upgrade Steps (performed on Pi)

```bash
cd ~/.signalk
npm install signalk-server@2.22.1
sudo systemctl restart signalk
```

---

## SK Heap Limit

Set in `/etc/systemd/system/signalk.service`:
```
ExecStart=/usr/bin/node --max-old-space-size=2048 ...
```

2048MB limit allows full operation while preventing unbounded growth from consuming all Pi RAM.

**Note:** `WatchdogSec` must NOT be set on signalk.service — SK does not implement `sd_notify`, so any watchdog setting kills the service every N seconds.

---

## AIS Pipeline (confirmed working post-upgrade)

```
GPS/AIS NMEA → Signal K v2.22.1 → signalk-to-nmea0183 plugin → TCP port 10110 → OpenCPN
```

Plugin config: `~/.signalk/plugin-config-data/sk-to-nmea0183.json`
- `VDM` (AIS): `true`
- `VDM_throttle`: `0`

Signal K mDNS must be `false` in `~/.signalk/settings.json` — mDNS causes 5300ms response time on queries.

---

## cx5106 Bus Issue (resolved separately)

The Navico cx5106 N2K adapter was physically removed by Don. It was flooding the N2K bus at 100+ frames/sec with PGN 127488 (tachometer + tilt/trim). Bus is clean without it. If N2K data is needed in future, the cx5106 is not suitable for this setup.
