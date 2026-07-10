# CX5106 Wiring & Calibration Guide — Monterey 265 SEL

**Version:** 2.0.0
**Created:** 2026-07-10 S95
**Updated:** 2026-07-10 S95 (major correction — parallel connection claim removed)
**Status:** RESEARCH COMPLETE — awaiting on-boat verification
**Relates to:** BUG-11 (third-party device compatibility), d3kOS engine monitoring via NMEA 2000

---

## ⚠️ CORRECTION — Previous Version Error

Version 1.x of this document stated the CX5106 connects **in parallel** with existing gauges.
**This was wrong.** Further research confirmed the CX5106/CX5003 family requires the original
analog gauge to be **disconnected**. See Part 2 for full explanation and device choice guidance.

---

## Part 1 — Monterey 265 SEL Gauge Wires (Confirmed)

Each dash gauge has three wires: **black**, **purple**, and **blue**.

### Wire Functions

| Wire | Function | Confidence |
|------|----------|------------|
| **Black** | Ground (negative return) | Confirmed — universal ABYC standard |
| **Purple** | 12V ignition power — gauge powers on with key | Confirmed — ABYC standard |
| **Blue** | Sender signal — variable resistance from the sending unit | Confirmed — only role left in a 3-wire harness |

### Why Blue is the Sender Wire

ABYC defines sender-specific colors at the *engine end* of the circuit (light blue = oil
pressure, pink = fuel, tan = water temp). When a manufacturer runs a unified 3-wire harness
to all dash gauges using the same three colors, power (purple) and ground (black) are already
accounted for — blue is the sender signal. This 3-wire pattern is confirmed across multiple
North American boat manufacturers including Monterey.

### Circuit Diagram

```
Sending unit (tank float / oil pressure sender / temp sender)
        │
        │  Variable resistance (US standard: 240 Ω empty → 33 Ω full for fuel)
        │
Blue wire ─────────── Gauge sender terminal
Purple wire ────────── Gauge B+ terminal  (12V ignition)
Black wire ─────────── Gauge ground terminal
```

---

## Part 2 — CX5106 Connection: Critical Decision Point

### Does the CX5106 Connect in Parallel With Existing Gauges?

**No — not confirmed. Evidence points to required gauge disconnection.**

Most budget analog-to-NMEA 2000 converters, including the CX5106/CX5003 family, do **not**
have the electrical isolation needed to share a sender with an existing analog gauge. Without
isolation, connecting the converter in parallel disrupts the voltage the gauge depends on —
both the converter and the gauge will read incorrectly.

A confirmed user report on the YBW Forum (CX5003, same device family):
> *"worked fine once I realized you have to disconnect original gauges"*

This means with the CX5106, you face a choice:

---

### Option A — Use CX5106, Remove Analog Gauges

Connect the CX5106 sender terminal directly to the blue (sender) wire and the ground terminal
to the black (ground) wire. The analog gauge is removed from the circuit (or left disconnected).
d3kOS becomes the only readout.

```
Sending unit
        │
        └──── Blue wire ──── CX5106 analog input terminal (channel for that sender)

Black wire ──────────────── CX5106 ground terminal

CX5106 own power (its own wiring harness):
  Red lead  ──── ignition-switched 12V (fused, separate from gauge circuit)
  Black lead ─── chassis ground
  N2K port  ──── NMEA 2000 backbone (drop cable → T-connector → PiCAN-M → Pi)

Analog gauge: disconnected or removed
```

**Suitable if:** You are replacing your analog gauges entirely with digital display via d3kOS.

---

### Option B — Keep Analog Gauges, Use Actisense EMU-1 Instead

If you want to **keep your Monterey analog gauges working** AND have digital readings in
d3kOS, the CX5106 is the wrong device. The **Actisense EMU-1** is specifically engineered
for parallel operation:

- Automatically detects the presence of an existing analog gauge on each channel
- Adjusts its calibration to account for the shared sender load
- Opto-isolation between N2K power and device power — no interference with gauge circuit
- Calibrates via Windows software (Actisense Config Tool) with dropdown sender profiles
- Supports US and European sender resistance standards

With the EMU-1, both the analog gauge and d3kOS digital display run simultaneously from
the same sender — no gauge removal required.

**Suitable if:** You want to keep the original Monterey dash gauges as a backup/primary
display and also see values in d3kOS.

---

### Summary — Which Device For Which Scenario

| Goal | Device | Analog Gauge |
|------|--------|-------------|
| Digital only — replace gauges with d3kOS | CX5106 | Removed |
| Both analog and digital simultaneously | Actisense EMU-1 | Kept and working |

---

## Part 3 — Sender Resistance: US Standard Confirmed

Monterey Boats is an American manufacturer. The Monterey 265 SEL uses **US-standard senders**.

### Confirmed Resistance Values

| Sender Type | US Standard | Empty | Full / Max |
|-------------|------------|-------|------------|
| Fuel level | US | ~240 Ω | ~33 Ω |
| Oil pressure | US | ~10 Ω (0 PSI) | ~184 Ω (max) |
| Water temp | US | ~300 Ω (cold/40°C) | ~22 Ω (hot/120°C) |
| Trim / tilt | Universal | 0 Ω | ~190 Ω |

### CX5106 Resistance Range Mismatch

The CX5106 is pre-configured for **0–190 Ω (European standard)**. Your fuel sender uses
240–33 Ω (US standard). These are inverted and scaled differently.

**No confirmed user-accessible resistance range calibration exists for the CX5106.**
The device has DIP switches for RPM ratio only. There is no documented software
interface, SD card config, or hardware adjustment to change the fuel sender resistance
range from European to US standard.

This is a **potential blocker** for accurate fuel level readings with the CX5106 on
a US-standard boat. Oil pressure and temperature resistance ranges are similar enough
between US and European standards that those readings may be usable; fuel level is not.

**With the Actisense EMU-1:** sender standard is selected in the Windows config software —
US and European profiles are both supported with a dropdown selection.

---

## Part 4 — CX5106 Calibration (What Actually Exists)

The CX5106 does **not** have a sophisticated calibration interface. Based on confirmed
user reports and product documentation:

| Feature | CX5106 | Actisense EMU-1 |
|---------|--------|-----------------|
| Configuration interface | DIP switches (RPM ratio only) | Windows USB software |
| Sender profile selection | None documented | Dropdown — US/EU/custom |
| Resistance range adjustment | None confirmed | Yes — per channel |
| Parallel gauge detection | No | Yes — automatic |
| Two-point calibration | Not documented | Yes — via software |

### What DIP Switches Control on CX5106

The only confirmed configurable parameter via DIP switches is the **tachometer RPM ratio**
(engine pulses per revolution — varies by engine type). This sets the correct RPM scaling.
All other channels (fuel, oil, temp) read at the fixed factory resistance range.

### Practical Calibration Approach for CX5106

If proceeding with Option A (gauge removed):

1. Wire as per Part 2 Option A diagram.
2. Connect N2K backbone to PiCAN-M and confirm Signal K is receiving PGNs.
3. Check Signal K values via SSH:
   ```
   curl http://localhost:3000/signalk/v1/api/vessels/self/propulsion/
   curl http://localhost:3000/signalk/v1/api/vessels/self/tanks/
   ```
4. Compare readings against a known reference (e.g. measure actual fuel with a dipstick;
   read oil pressure with a mechanical gauge temporarily installed).
5. If Signal K values are consistently offset, apply a correction in `~/.signalk/settings.json`:
   ```json
   "tanks.fuel.0.currentLevel": {
     "calibration": { "offset": 0.05 }
   }
   ```
   Apply: `sudo systemctl restart signalk`

**Important:** If the fuel reading is drastically wrong (e.g. reads full when empty), this
is the US/European resistance range mismatch — a Signal K offset cannot fix a scaled/inverted
reading. In that case, the CX5106 is not compatible with your fuel sender without hardware
modification, and the Actisense EMU-1 is the appropriate device.

---

## Part 5 — Signal K Path Reference

| Gauge Type | Signal K Path | NMEA 2000 PGN | US Sender Range |
|-----------|--------------|----------------|-----------------|
| Fuel level | `tanks.fuel.0.currentLevel` | PGN 127505 | 240 Ω (E) → 33 Ω (F) |
| Oil pressure | `propulsion.0.oilPressure` | PGN 127489 | 10 → 184 Ω |
| Water temperature | `propulsion.0.temperature` | PGN 127489 | ~300 → 22 Ω |
| Trim / tilt | `propulsion.0.trimPosition` | PGN 127245 | 0 → 190 Ω |

---

## Open Items Before On-Boat Work

- [x] Wire colours confirmed: black = ground, purple = 12V ignition, blue = sender signal
- [x] Monterey = US manufacturer — US sender standard applies (240–33 Ω fuel)
- [x] Parallel connection NOT supported by CX5106 — gauge must be disconnected (Option A) or switch to Actisense EMU-1 (Option B)
- [ ] **Decision required:** Option A (CX5106, remove gauges) or Option B (Actisense EMU-1, keep gauges)?
- [ ] If Option A: confirm fuel sender resistance with multimeter to verify US/European range before relying on fuel level reading
- [ ] If Option A: wire CX5106 per Part 2 diagram, confirm Signal K PGNs arriving
- [ ] If Option B: purchase Actisense EMU-1, install Actisense Config Tool, configure sender profiles

---

## Sources

- [ABYC Cable & Wire Color Codes — Electrical Technology](https://www.electricaltechnology.org/2020/07/marine-boat-cable-wire-color-codes.html)
- [Engine Instrument Wiring Made Easy — boats.com](https://www.boats.com/how-to/engine-instrument-wiring-made-easy/)
- [Standard Boat Wiring Color Codes — CP Performance](https://www.cpperformance.com/t-boat_wiring_colors.aspx)
- [CX-5106 NMEA 2000 Converter — iMarinex](https://www.imarinex.com/product/cx-5106-nmea-2000-converter-up-to-13-sensors/)
- [N2K Engine Monitor User Experiences — YBW Forum](https://forums.ybw.com/threads/anyone-tried-the-cheap-n2k-engine-monitor-on-ebay.557725/)
- [Analog to NMEA 2000 using the CX5003 — Trawler Forum](https://www.trawlerforum.com/threads/analog-to-nema-2000-using-the-cx5003.75442/)
- [Actisense EMU-1 Review — Panbo](https://panbo.com/actisense-emu-1-analog-engine-gauges-to-nmea-2000-happiness/)
- [Analog to NMEA 2000 Engine Instruments — Downeast Boat Forum](https://downeastboatforum.com/threads/analog-to-nmea-2000-engine-instruments.45321/)
- [ABYC Color Codes Explained — Pacer Group](https://www.pacergroup.net/pacer-news/abyc-color-codes-explained/)
