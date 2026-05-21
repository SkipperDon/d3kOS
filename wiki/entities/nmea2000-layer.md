# Entity: NMEA 2000 Layer

*Last updated: S85 2026-05-20 | Sources: pi-system.md, MEMORY.md S85 correction*

---

## Critical Distinction (read first)

**PiCAN-M** and **CX5106** are two different devices that are often confused. They must not be conflated.

| Device | What It Is | Where It Lives |
|--------|-----------|----------------|
| **PiCAN-M** | CAN bus HAT — the Pi's own hardware interface to the N2K bus. Sits on RPi 5 GPIO header. Provides `can0`. | On the d3kOS RPi 5 |
| **CX5106** | Analogue-to-digital converter — reads engine sensor signals (RPM, oil pressure, coolant temp) and outputs them as NMEA 2000 PGNs. A device ON the N2K bus, not the Pi's interface to it. | On the NMEA 2000 backbone |

**Before any session involving N2K hardware: name the specific device. Never say "CX5106" when you mean the Pi's N2K interface.**

---

## Pi's N2K Connection

```
RPi 5 GPIO → PiCAN-M HAT → can0 → NMEA 2000 backbone
```

Signal K reads the entire N2K bus via `canbus-canboatjs` on `can0`. This includes all devices on the backbone: CX5106 engine data, GPS from chartplotter, AIS transponder, depth sounder, etc.

## CX5106

- Converts analogue engine signals to NMEA 2000 PGNs
- PGN 127488 (engine RPM) — was flooding bus at 100+ frames/sec on bench setup; removed from bench
- **WILL be installed on the boat** — this is the primary engine data source
- DIP switch configuration: Signal K setup wizard Step 5
- Connects to N2K backbone, NOT directly to Pi

## Signal K Data Sources

| Source | Path | Detail |
|--------|------|--------|
| N2K bus (all devices) | `can0` via canbus-canboatjs | PiCAN-M HAT |
| GPS | gpsd port 2947 | Separate from N2K |
| AIS | TCP 10110 | NMEA 0183 input |

## AIS Isolation (mandatory for SafeHelm)

SafeHelm injects synthetic vessel targets into Signal K. These must NEVER reach the N2K bus and be re-broadcast by the AIS transponder (ITU violation).

**transmitPGNs whitelist** — in Signal K `settings.json`, canboat-js output provider must be an explicit whitelist of own-vessel sensor PGNs only:

```json
{
  "type": "@signalk/signalk-to-nmea2000",
  "options": {
    "transmitPGNs": [127250, 128267, 129025, 129026, 127245, 128259, 130306]
  }
}
```

AIS vessel PGNs (129038, 129039, 129040, 129041) must NOT appear. See [[concepts/ais-isolation]] for full 4-layer isolation spec.

## PGN 126983 — Alert to Axiom MFD

Raymarine Lighthouse 4.8.164 added support for receiving PGN 126983.

When Axiom receives PGN 126983:
- Alert appears in Alarm Manager
- Emergency Alarm / Alarm types fire internal buzzer
- Captain acknowledges → Axiom sends PGN 126984 back on N2K bus
- SafeHelm can listen for 126984 to confirm acknowledgment

Sending path: Pi Python → Signal K notification → canboat-n2k plugin → PiCAN-M → N2K → Axiom

## Related

- [[entities/safehelm]] — uses N2K output for PGN 126983 collision alerts
- [[entities/pi-system]] — PiCAN-M is on the d3kOS RPi 5
- [[concepts/ais-isolation]] — mandatory before synthetic AIS ships
