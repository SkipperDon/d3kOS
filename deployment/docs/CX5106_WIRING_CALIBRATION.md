# CX5106 Wiring & Calibration Guide — Monterey 265 SEL

**Version:** 1.1.0
**Created:** 2026-07-10 S95
**Updated:** 2026-07-10 S95
**Status:** RESEARCH COMPLETE — awaiting on-boat verification
**Relates to:** BUG-11 (third-party device compatibility), d3kOS engine monitoring via NMEA 2000

---

## Overview

This document covers how to wire the CX5106 analog-to-NMEA 2000 converter to the
Monterey 265 SEL dash gauge harness, and how to calibrate it so readings are accurate
in d3kOS and Signal K. Research compiled from ABYC standards, marine electronics
forums, and CX5106 product documentation.

The CX5106 reads existing analog sender signals (fuel, oil pressure, water temperature,
trim) and converts them to NMEA 2000 PGNs, which Signal K ingests and d3kOS displays.

---

## Part 1 — Understanding the Monterey 265 SEL Gauge Wires

Each dash gauge on the Monterey 265 SEL has three wires: **black**, **purple**, and **blue**.

### Wire Functions

| Wire | Function | Standard |
|------|----------|----------|
| **Black** | Ground (negative return) | Universal — ABYC and all manufacturers |
| **Purple** | 12V ignition power — energises the gauge when key is ON | ABYC standard |
| **Blue** | Sender signal input — variable resistance from the sending unit | Manufacturer-simplified harness (see note below) |

### Why Blue is the Sender Wire

ABYC defines sender-specific colors at the *engine* end of the circuit:
light blue for oil pressure, pink for fuel, tan for water temperature. However, when a
manufacturer runs a unified 3-wire harness to all dash gauges using the same three colors,
power (purple) and ground (black) are already assigned — the only remaining role for
the third wire is the sender signal input. This 3-wire pattern (purple/black/blue) is
confirmed across multiple marine boat manufacturers.

**The blue wire carries a variable resistance signal** from the sending unit (inside
your tank, on your engine) back to the gauge. This is exactly what the CX5106 reads.

### What Each Wire Does in the Circuit

```
Sender unit (tank float, oil pressure sender, temp sender)
        │
        │  Variable resistance (e.g. 240 Ω empty → 33 Ω full for US fuel)
        │
Blue wire ─────────────────────────────────────────────── Gauge sender terminal
Purple wire (12V ignition) ────────────────────────────── Gauge B+ terminal
Black wire (ground) ───────────────────────────────────── Gauge ground terminal
```

---

## Part 2 — CX5106 Connection

The CX5106 wires **in parallel with your existing gauges**. It uses a high-impedance
input — it listens to the same sender signal the gauge already reads. Your analog
gauges continue to work normally after the CX5106 is added.

### Wiring Diagram

```
Sender unit (in tank / on engine)
        │
        └──── Blue wire ──────┬──── to gauge sender terminal (existing)
                              └──── to CX5106 analog input terminal (that channel)

Black wire (ground) ──────────┬──── to gauge ground terminal (existing)
                              └──── to CX5106 ground terminal

Purple wire (12V ignition) ────────  to gauge B+ terminal ONLY
                                      do NOT connect to CX5106

CX5106 own power supply (separate wires from the CX5106 itself):
  Red lead  ──── ignition-switched 12V source (clean, fused)
  Black lead ─── chassis ground
  N2K port  ──── NMEA 2000 backbone (via drop cable to backbone T-connector)
                  This connects through PiCAN-M to the Pi
```

### Key Rules

- **Purple does NOT connect to the CX5106.** That is gauge power only.
- **CX5106 needs its own 12V supply** (red/black leads) — do not power it from the gauge circuit.
- **One CX5106 channel per sender** — fuel sender to channel 1, oil pressure sender to channel 2, etc.
- **N2K port connects to the NMEA 2000 backbone** — same bus the PiCAN-M is on.

### Parallel Operation Warning

Most installations work correctly in parallel. However, at least one user reported that
the CX5003 (same device family) did not work correctly in parallel with existing gauges
on some engine types, possibly due to impedance loading affecting gauge accuracy.

**Test:** After wiring in the CX5106, verify your analog gauge still reads correctly.
If the gauge reading shifts, disconnect the CX5106 sender terminal — the gauge should
immediately return to normal. This confirms the CX5106 is loading the circuit. In this
case, consult the CX5106 manufacturer about impedance matching.

---

## Part 3 — Sender Resistance Ranges

This is the most critical step for accuracy. The CX5106 must be configured for the
resistance range your senders produce.

### US vs. European Standard — Know Which You Have

| Sender Type | US Standard (most North American boats) | European / Metric Standard |
|-------------|----------------------------------------|---------------------------|
| Fuel level | 240 Ω (empty) → 33 Ω (full) | 0 Ω (empty) → 190 Ω (full) |
| Oil pressure | 10 Ω → 184 Ω (0–10 bar) | Similar |
| Water temp | ~300 Ω (cold/40°C) → 22 Ω (hot/120°C) | Similar |
| Trim / tilt | 0–190 Ω | 0–190 Ω |

The CX5106 is marketed as **0–190 Ω** (European standard).

**Monterey Boats is an American manufacturer. The Monterey 265 SEL uses US-standard
senders (240 Ω empty → 33 Ω full for fuel).** The CX5106's default 0–190 Ω range
does NOT match. If used without reconfiguration, fuel readings in d3kOS will be
inverted and wrong — empty will display as partial or full, full will read as
over-range or zero.

**The CX5106 must be reconfigured for the US sender resistance range before
calibration will produce accurate results.** This is a required step, not optional.

### Sender Resistance — Confirmed Values for Monterey 265 SEL

| Sender Type | Confirmed Standard | Empty | Full / Max |
|-------------|-------------------|-------|------------|
| Fuel level | US | ~240 Ω | ~33 Ω |
| Oil pressure | US | ~10 Ω (0 PSI) | ~184 Ω (max pressure) |
| Water temp | US | ~300 Ω (cold/40°C) | ~22 Ω (hot/120°C) |
| Trim / tilt | 0–190 Ω (widely universal) | 0 Ω | ~190 Ω |

Verify the exact fuel sender resistance with a multimeter at known empty and known
full if precise calibration is needed. The values above are US standard; individual
sending units can vary slightly.

---

## Part 4 — Calibration Procedure

Calibration is performed at the CX5106 level (via its SD card configuration interface
or Windows software if provided). Signal K and d3kOS receive the already-calibrated
values — get the CX5106 right first.

### Stage 1 — Key On, Engine Off (Low Reference Point)

1. Turn ignition to ON position (engine not running).
2. Note the reading on each analog gauge (fuel level, oil pressure = 0, water temp = ambient).
3. In the CX5106 configuration, enter the low reference value for each channel.
   - Fuel: note gauge position (e.g. half tank)
   - Oil pressure: 0 PSI / 0 bar
   - Water temp: ambient temperature (e.g. 20°C / 68°F)

### Stage 2 — Engine Running at Known Values

1. Start engine and run until fully at operating temperature.
2. Read each analog gauge and record the values.
3. In the CX5106 configuration, enter the high reference value for each channel.
   - Oil pressure: read from gauge (e.g. 40 PSI)
   - Water temp: read from gauge (e.g. 85°C / 185°F)
   - Fuel: should match Stage 1 reading (level unchanged during a short run)

The CX5106 uses these two reference points to interpolate resistance → engineering value
across the full sender range.

### Stage 3 — Verify in Signal K and d3kOS

After CX5106 calibration:

1. SSH to Pi: `ssh d3kos@192.168.1.237`
2. Check Signal K is receiving the values:
   ```
   curl http://localhost:3000/signalk/v1/api/vessels/self/propulsion/
   curl http://localhost:3000/signalk/v1/api/vessels/self/tanks/
   ```
3. Compare Signal K values to your analog gauges.
4. Open d3kOS engine monitor page — values should match analog gauges.

### Fine-Tuning in Signal K (if needed)

If d3kOS shows a consistent offset from the analog gauge (e.g. always reads 5°C high),
Signal K can apply a correction factor. In `~/.signalk/settings.json`, under the
relevant path, add a `calibration` offset:

```json
"propulsion.0.temperature": {
  "calibration": {
    "offset": -5
  }
}
```

Apply with: `sudo systemctl restart signalk`

This is a last-resort fine-tune. If the offset is large, re-do the CX5106 hardware
calibration — a Signal K offset only masks an underlying calibration error.

---

## Part 5 — Resistance Quick Reference

| Gauge Type | Signal K Path | NMEA 2000 PGN | US Sender Range |
|-----------|--------------|----------------|-----------------|
| Fuel level | `tanks.fuel.0.currentLevel` | PGN 127505 | 240 Ω (E) → 33 Ω (F) |
| Oil pressure | `propulsion.0.oilPressure` | PGN 127489 | 10 → 184 Ω |
| Water temperature | `propulsion.0.temperature` | PGN 127489 | ~300 → 22 Ω |
| Trim / tilt | `propulsion.0.trimPosition` | PGN 127245 | 0 → 190 Ω |

---

## Open Items Before On-Boat Verification

- [x] Confirmed: Monterey 265 SEL is US-manufactured — US sender standard applies (240–33 Ω fuel)
- [ ] Reconfigure CX5106 channels from default 0–190 Ω (European) to US resistance ranges — REQUIRED before calibration
- [ ] Perform Stage 1 and Stage 2 calibration on the boat
- [ ] Verify Signal K paths are populating after calibration
- [ ] Confirm d3kOS engine monitor displays match analog gauges

---

## Sources

- [ABYC Cable & Wire Color Codes — Electrical Technology](https://www.electricaltechnology.org/2020/07/marine-boat-cable-wire-color-codes.html)
- [Engine Instrument Wiring Made Easy — boats.com](https://www.boats.com/how-to/engine-instrument-wiring-made-easy/)
- [Standard Boat Wiring Color Codes — CP Performance](https://www.cpperformance.com/t-boat_wiring_colors.aspx)
- [CX-5106 NMEA 2000 Converter — iMarinex](https://www.imarinex.com/product/cx-5106-nmea-2000-converter-up-to-13-sensors/)
- [N2K Engine Monitor User Experiences — YBW Forum](https://forums.ybw.com/threads/anyone-tried-the-cheap-n2k-engine-monitor-on-ebay.557725/page-2)
- [Analog to NMEA 2000 using the CX5003 — Trawler Forum](https://www.trawlerforum.com/threads/analog-to-nema-2000-using-the-cx5003.75442/)
- [ABYC Color Codes Explained — Pacer Group](https://www.pacergroup.net/pacer-news/abyc-color-codes-explained/)
