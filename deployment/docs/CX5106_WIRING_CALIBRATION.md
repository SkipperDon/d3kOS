# CX5106 Wiring & Calibration Guide — Monterey 265 SEL

**Version:** 3.0.0
**Created:** 2026-07-10 S95
**Updated:** 2026-07-10 S95
**Status:** RESEARCH COMPLETE — CX5106 installed, configuration in progress
**Relates to:** BUG-11 (third-party device compatibility), d3kOS engine monitoring via NMEA 2000

---

## Overview

The CX5106 is installed on the Monterey 265 SEL. It reads analog sender signals
(fuel, oil pressure, water temperature, trim) and converts them to NMEA 2000 PGNs,
which Signal K ingests and d3kOS displays on the engine monitor page.

The existing analog dash gauges are disconnected from the sender circuit. The CX5106
becomes the sole reader of each sender.

---

## Part 1 — Monterey 265 SEL Gauge Wires (Confirmed)

Each dash gauge has three wires: **black**, **purple**, and **blue**.

| Wire | Function |
|------|----------|
| **Black** | Ground (negative return) |
| **Purple** | 12V ignition power — gauge powers on with key |
| **Blue** | Sender signal — variable resistance from the sending unit |

**Blue is the sender wire.** Purple and black are accounted for by power and ground —
blue is the only role remaining in a 3-wire harness. Confirmed against ABYC standards
and North American boat wiring practice.

---

## Part 2 — CX5106 Wiring

Analog gauges are disconnected from the sender (blue wire). The CX5106 connects
directly to the sender and ground.

```
Sending unit (tank float / oil pressure sender / temp sender)
        │
        └──── Blue wire ──── CX5106 analog input terminal (one channel per sender)

Black wire ──────────────── CX5106 ground terminal

CX5106 power (its own leads):
  Red  ──── ignition-switched 12V (fused)
  Black ─── chassis ground
  N2K  ──── NMEA 2000 backbone drop cable → T-connector → PiCAN-M → Pi
```

**One channel per sender** — fuel to channel 1, oil pressure to channel 2,
water temp to channel 3, trim to channel 4 (or as labelled on the unit).

**Purple wire** — gauge power only. No connection to CX5106. Leave as-is or
cap it if the gauge is removed.

---

## Part 3 — Sender Resistance: US Standard (Confirmed)

Monterey is an American manufacturer. The Monterey 265 SEL uses US-standard senders.

| Sender | US Range | Empty | Full / Max |
|--------|----------|-------|------------|
| Fuel level | US | ~240 Ω | ~33 Ω |
| Oil pressure | US | ~10 Ω (0 PSI) | ~184 Ω (max) |
| Water temp | US | ~300 Ω (cold/40°C) | ~22 Ω (hot/120°C) |
| Trim / tilt | Universal | 0 Ω | ~190 Ω |

The CX5106 is factory-configured for 0–190 Ω (European standard). The fuel sender
runs 240–33 Ω (inverted and different scale). Verify fuel readings against a known
reference (dipstick measurement) after configuration and apply a Signal K correction
offset if needed.

---

## Part 4 — CX5106 Configuration

### DIP Switches

The only confirmed user-configurable parameter via DIP switches is the **tachometer
RPM ratio** — set to match the number of pulses per revolution your engine produces.
Consult the CX5106 label or manual for the switch positions.

All other channels (fuel, oil, temp) read at the factory resistance range. No software
interface or SD card configuration has been confirmed for this device.

### Verifying Readings in Signal K

After wiring and powering the CX5106:

1. SSH to Pi: `ssh d3kos@192.168.1.237`
2. Check Signal K is receiving data:
   ```
   curl http://localhost:3000/signalk/v1/api/vessels/self/propulsion/
   curl http://localhost:3000/signalk/v1/api/vessels/self/tanks/
   ```
3. Compare each value against a known reference:
   - Fuel: measure tank with a dipstick
   - Oil pressure: known idle pressure for your engine
   - Water temp: compare to engine operating spec

### Signal K Correction Offset (if readings are off)

For a consistent offset, apply a calibration correction in `~/.signalk/settings.json`:

```json
"tanks.fuel.0.currentLevel": {
  "calibration": { "offset": 0.05 }
}
```

Apply: `sudo systemctl restart signalk`

If fuel reads inverted (full shows empty or vice versa) the issue is the US/European
resistance range mismatch — an offset will not fix an inverted scale. In that case
the fuel channel reading cannot be corrected in software and will need a hardware workaround.

---

## Part 5 — Signal K Path Reference

| Sender | Signal K Path | NMEA 2000 PGN |
|--------|--------------|----------------|
| Fuel level | `tanks.fuel.0.currentLevel` | PGN 127505 |
| Oil pressure | `propulsion.0.oilPressure` | PGN 127489 |
| Water temperature | `propulsion.0.temperature` | PGN 127489 |
| Trim / tilt | `propulsion.0.trimPosition` | PGN 127245 |

---

## Open Items

- [x] Wire colours confirmed: black = ground, purple = 12V ignition, blue = sender signal
- [x] Monterey = US manufacturer — US sender standard confirmed (240–33 Ω fuel)
- [x] CX5106 installed
- [ ] Set DIP switches for RPM ratio to match engine
- [ ] Verify Signal K receiving data on all channels after wiring
- [ ] Verify fuel level reading against dipstick measurement — check for US/European range inversion
- [ ] Apply Signal K offset corrections if needed
- [ ] Confirm d3kOS engine monitor page displays all values correctly

---

## Sources

- [ABYC Cable & Wire Color Codes — Electrical Technology](https://www.electricaltechnology.org/2020/07/marine-boat-cable-wire-color-codes.html)
- [Engine Instrument Wiring Made Easy — boats.com](https://www.boats.com/how-to/engine-instrument-wiring-made-easy/)
- [Standard Boat Wiring Color Codes — CP Performance](https://www.cpperformance.com/t-boat_wiring_colors.aspx)
- [CX-5106 NMEA 2000 Converter — iMarinex](https://www.imarinex.com/product/cx-5106-nmea-2000-converter-up-to-13-sensors/)
- [N2K Engine Monitor User Experiences — YBW Forum](https://forums.ybw.com/threads/anyone-tried-the-cheap-n2k-engine-monitor-on-ebay.557725/)
- [Analog to NMEA 2000 using the CX5003 — Trawler Forum](https://www.trawlerforum.com/threads/analog-to-nema-2000-using-the-cx5003.75442/)
- [Actisense EMU-1 Review — Panbo](https://panbo.com/actisense-emu-1-analog-engine-gauges-to-nmea-2000-happiness/)
- [ABYC Color Codes Explained — Pacer Group](https://www.pacergroup.net/pacer-news/abyc-color-codes-explained/)
