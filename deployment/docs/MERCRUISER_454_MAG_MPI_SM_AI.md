---
title: Mercury MerCruiser MCM 454 Mag MPI (7.4L) — Service Manual (AI-Friendly Edition)
source_document: mercruise engine manual99171d (1).pdf — Service Manual Number 23, 90-861326--1, MARCH 1999 (1056 pp)
engine: MerCruiser MCM 454 Mag MPI — 454 CID / 7.4L big-block V8 sterndrive (operator-confirmed 7.4L, S106)
owner_vessel: Monterey 265 (sterndrive → MCM column applies, not MIE inboard)
edition: AI-friendly conversion — exact specs + diagrams-as-text + query structure
status: IN PROGRESS — Specifications & Fluid Capacities done; scope of remainder pending operator decision
converted: 2026-07-24 S106
consumer: d3kOS RAG (ChromaDB via helm_os_ingest.py)
d3kOS_relevance: unblocks BUG-16 (gauge tolerance advice), BUG-17 (battery/alternator), BUG-14 (sender/tach wiring)
---

# MerCruiser MCM 454 Mag MPI (7.4L) — AI-Friendly Service Reference

## About this edition
Faithful conversion of the factory service manual for AI retrieval. **Facts are exact** (every
spec, pressure, temperature, RPM, capacity, and torque reproduced precisely); **diagrams are
described in text**; safety notices keep their signal word. This covers the **MCM (sterndrive)
454 Mag MPI**, which is the engine on the Monterey 265. The source manual also documents the
7.4L MPI, 502/8.2L Mag MPI, and MIE (inboard) variants — values below are the **454 Mag MPI
sterndrive** column unless noted.

> **Why this manual matters for d3kOS:** the Monterey boat manual deferred all engine ranges to
> "the engine manual" — *this* is that manual. The tolerances below are the source of truth for
> the BUG‑16 gauge-tap "compare live value to normal range" feature.

---

# 1. Tune-Up Specifications — MCM 454 Mag MPI (7.4L) `[source: p1B-8]`

| Parameter | Specification |
|---|---|
| Number of cylinders | 8 (V8) |
| Displacement | 454 C.I.D. (7.4 L) |
| Bore × stroke | 4.25 × 4.00 in (108 × 101.6 mm) |
| Compression ratio | 9.3 : 1 |
| Compression pressure | Minimum 100 psi (690 kPa); no cylinder < 70% of the highest cylinder |
| **Idle rpm (in forward gear)** | **600 rpm** (EFI idle is not adjustable) |
| **Max rpm (at W.O.T.)** | **4200–4600 rpm** |
| **Oil pressure at 2000 rpm** | **Minimum 30 psi (207 kPa)** |
| **Min oil pressure at idle** | **Minimum 4 psi (28 kPa)** |
| Electrical system | 12 V negative (−) ground |
| Fuel pressure (running) | 43 psi (248 kPa) |
| Min battery requirement | 650 CCA / 825 MCA / 150 Ah |
| Firing order | 1-8-4-3-6-5-7-2 |
| Spark plug type | AC MR43LTS / Champion RV12YC / NGK BPR6EFS |
| Spark plug gap | 0.045 in (1.1 mm) |
| Timing (at idle rpm) | 8° BTDC (set by special procedure) |
| **Thermostat** | **160 °F (71 °C)** |

*(RPM measured with an accurate service tachometer at normal operating temperature.)*

## 1.1 d3kOS Gauge-Tolerance Reference (BUG‑16 / BUG‑17)
Direct mapping from the specs above to the dashboard gauges — this is what "tap a gauge → is it
normal?" should compare against:

| Gauge | Normal / expected | Alert condition | Source |
|---|---|---|---|
| **Oil pressure** | ≥ **30 psi (207 kPa)** at ~2000 rpm; ≥ **4 psi (28 kPa)** at idle | below these minimums | p1B-8 |
| **Coolant/engine temp** | thermostat opens at **160 °F (71 °C)** → normal running ≈ 160 °F+ | sustained well above ~160 °F = overheat (see §Cooling troubleshooting) | p1B-8 |
| **Tachometer (RPM)** | idle **600 rpm**; wide-open-throttle **4200–4600 rpm** | above 4600 at WOT = over-rev / prop or trim issue; well below = load/fuel/prop issue | p1B-8 |
| **Voltmeter** | 12 V negative-ground system; running/charging voltage from alternator | (charging-voltage range is in the Electrical section — to be converted, p1C/p123–124) | p1B-8 + Electrical |
| **Fuel pressure** (if shown) | **43 psi (248 kPa)** running | significantly off = fuel pump/filter | p1B-8 |
| Battery (cranking) | ≥ **650 CCA / 825 MCA / 150 Ah** | undersized/weak battery = hard cranking | p1B-8 |

> `[UNVERIFIED — confirm drive type]` Values assume the **MCM sterndrive** engine (Monterey 265
> is a sterndrive). The MIE (inboard) 454 Mag MPI Horizon differs on WOT rpm (4000–4400) and
> some plug data — not applicable to your boat.

---

# 2. Fluid Capacities `[source: p1B-11/12]`

| System | Capacity (454 / 7.4L) | Notes |
|---|---|---|
| Crankcase oil (with filter) | 7 U.S. qt (6.6 L) | use dipstick for exact level |
| Seawater cooling system | 20 U.S. qt (19 L) | figure is for winterization use |
| Closed cooling system | 18 U.S. qt (17 L) | if equipped |

**Transmission / drive (as applicable to the installed unit):** Velvet Drive 72C In-Line 1.5 qt
(1.3 L); Velvet Drive 5000A/5000V 3 qt (2.75 L) Dexron III; Hurth 630V 4.25 qt (4.0 L); Walter
V-Drive RV-36 0.75 qt (0.71 L) SAE 30. **Sterndrive unit oil (with Gear Lube Monitor):** Bravo
One 88 fl oz (2603 mL), Bravo Two 104 fl oz (3076 mL), Bravo Three 96 fl oz (2839 mL), Blackhawk
80 fl oz (2365 mL).

## 2.1 Break-In (first 20 hours) `[source: p1B-12]`
- First 10 hours: don't run below 1500 rpm for extended periods; don't exceed ¾ throttle.
- Next 10 hours: occasional full throttle OK (max 5 minutes at a time).
- Don't hold one speed for long periods; avoid full-throttle acceleration from idle; don't run
  full throttle until the engine reaches normal operating temperature.

---

# 3. Charging System — Mando 65 Amp Alternator `[source: §4C, p386/396]`

| Description | Specification |
|---|---|
| Alternator | Mando, 65 Amp |
| **Voltage output (regulated)** | **13.9 – 14.7 V** (at 1500–2000 rpm, warm, battery charged) |
| Current output | 60 A minimum |
| Excitation circuit | 1.3 – 2.5 V |
| Min brush length | 1/4 in (6 mm) |

**Alternator wire colors:** output = **ORANGE**, excitation = **PURPLE**, sensing = **RED/PURPLE**, ground = black.

**Voltage-output test (how the voltmeter should read):** battery fully charged; run engine warm
at 1500–2000 rpm; a good DC voltmeter across the battery should read **13.9–14.7 V**. Above
~14.7 V → regulator/ground fault; below ~13.9 V → belt, connections, brushes, or alternator.

## 3.1 d3kOS Voltmeter Reference (BUG‑17)
- **Charging (engine running):** **13.9–14.7 V** is normal.
- **Key-on / not charging:** ~12–12.7 V (battery resting).
- **Below ~12 V running or not climbing to ~14 V:** charging fault (belt, alternator, regulator,
  connections) — matches "Charging System Inoperative" troubleshooting below.

# 4. MerCruiser Wiring Color Code (BIA standard) `[source: §4E p4E-2]`

> **CRITICAL CAVEAT (printed on the page):** *"Color codes listed below DO NOT apply to fuel
> injection system harnesses."* Your **454 Mag MPI is EFI (MPI)** — so the **engine-side EFI
> harness may not follow these colors.** The **instrument/gauge (helm) wiring** generally still
> uses this standard, BUT your Monterey 265 was found on-boat NOT to match it (S101/S102). For
> that boat, the **meter-based wire ID (S102 field procedure) remains the authority** — use this
> table as the expected default, not gospel. `[d3kOS cross-ref: BUG-14, CX5106 wire ID]`

| Wire color | Circuit / where used |
|---|---|
| **BLACK (BLK)** | All grounds |
| BROWN (BRN) | Reference electrode — MerCathode |
| ORANGE (ORN) | Anode electrode — MerCathode **and** Alternator output |
| LT. BLUE/WHITE | Trim "Up" switch |
| **GRAY (GRY)** | **Tachometer signal** |
| GREEN/WHITE | Trim "Down" switch |
| **TAN** | **Water-temperature sender → gauge** |
| **LIGHT BLUE (LT BLU)** | **Oil-pressure sender → gauge** |
| **PINK (PNK)** | **Fuel-gauge sender → gauge** |
| BROWN/WHITE | Trim sender → trim gauge |
| PURPLE/WHITE | Trim "Trailer" switch |
| RED | Unprotected wires from battery |
| RED/PURPLE | Protected (fused) wires from battery; protected (+12 V) to trim panel |
| **PURPLE (PUR)** | **Ignition switch (+12 V)** |
| PURPLE/YELLOW | Ballast bypass |
| YELLOW/RED | Starter switch → starter solenoid → neutral-start switch |

> **Why this matters for the CX5106 (BUG‑14):** the CX5106 taps the gauge sender lines. Standard
> = tach signal on **GRAY**, temp on **TAN**, oil on **LT BLUE**, fuel on **PINK**, ignition +12 V
> on **PURPLE**. Since the EFI/Monterey wiring deviates, identify by **gauge post letter (I / S /
> G / L) + multimeter**, per the S102 field procedure — this table tells you what to *expect*.

# 5. Instrument Wiring Diagram `[source: §4E p4E-20, art 72940]`

**DIAGRAM (72940) — "Dual Station Wiring":** two helm stations (**A = upper/primary**, **B =
lower/second**), each with a row of five round gauges (numbered 1–5) and a remote-control lever.
Gauge terminal legend (molded post letters): **I** = ignition (+12 V, PURPLE), **S / SIG /
SEND** = sender signal, **G / GND** = ground (BLACK), **L** = light; the **tachometer** adds
**SW / UNSW / 12V / SIG** posts.
- **Gauge 1/2 (tach & voltmeter group):** wires **PUR** (12 V), **GRY** (tach signal), **BLK**
  (ground), with a **YEL/RED** start lead and an inline fuse.
- **Gauges 3/4/5 (oil / temp / fuel etc.):** each has **BLK** (ground) + **PUR** (12 V) + its
  **sender wire** — **LT. BLU** (oil pressure), **TAN** (water temp), **PINK** (fuel).
- **Feeds/links:** **RED/PUR** protected +12 V supply, **YEL/RED** to starter/neutral-safety,
  **BRN/WHT** trim sender, battery **(+)/(−)**; harness connectors numbered 1/2/3.
- **d3kOS use (BUG‑14):** this confirms the gauge-post → wire mapping the on-boat procedure taps
  (tach = GRY on the SIG post; senders on the S/SEND post; ignition = PUR on the I post; ground =
  BLK on G). Tap the CX5106 in parallel at the **gauge S post** (per S102), not by wire color.

# 6. Senders — Resistance Specifications `[source: §4D p4D-9..13]`

These map sender resistance ↔ the value the gauge shows — useful for verifying a sender and for
interpreting a live reading.

**Oil-pressure sender** (dual-station sender stamped **353-AM**):
| Oil pressure (psi) | Ohms — single station | Ohms — dual station |
|---|---|---|
| 0 | 227–257 | 113.5–128.5 |
| 20 | 142–162.5 | 71–81.25 |
| 40 | 91.7–113.6 | 45.8–56.8 |
| 80 | 9–49 | 4.5–24.5 |

**Water-temperature sender** (stamped **362-BC**, **TAN** wire):
| Temperature | Ohms |
|---|---|
| 140 °F (60 °C) | 121–147 |
| 194 °F (90 °C) | 47–55 |
| 212 °F (100 °C) | 36–41 |

**Fuel-tank sender** (flange type): **FULL** (float arm horizontal) = **30 Ω (±5)**; **EMPTY**
(arm vertical) = **240 Ω (±5)**. (US-standard 240–33 Ω range — consistent with the on-boat
40–70 Ω reading = nearly full tank.)

# 7. Electrical & Instrumentation Troubleshooting `[source: §1C p1C-11/12, p1C-19/20]`

| Symptom | Cause / special information |
|---|---|
| Engine will not crank over | Control not in neutral; low battery / damaged wiring / loose connections; tripped breaker; blown fuse; ignition switch; slave solenoid; faulty neutral-start safety switch; open circuit; starter solenoid; starter motor; mechanical engine fault |
| Charging system inoperative | Loose/broken serpentine belt; engine rpm too low at start (rev to 1500); loose/corroded connections; faulty battery gauge; battery won't accept charge (low electrolyte/failed); faulty alternator or regulator (see §4C) |
| Noisy alternator | Loose mounting bolts; worn/frayed/loose belt; loose pulley; worn/dirty bearings; faulty diode trio or stator |
| Instrumentation malfunction | Faulty wiring / loose or corroded terminals; faulty key switch; faulty gauge; faulty sender (test per §4D) |
| Low oil pressure | Low oil level; defective gauge/sender (verify with automotive test gauge); thin/diluted oil; oil-pump fault; internal/external leak; excessive bearing clearance |
| High oil pressure | Oil too thick / sludged; defective gauge/sender; clogged passage; relief valve stuck closed |

> **Oil-pressure reading guidance (from the manual, relevant to BUG‑16):** don't rely on the
> boat's oil-pressure gauge for diagnosis — verify with an automotive test gauge. It's **normal**
> for oil pressure to read higher when cold and to **drop at idle when hot**; low idle pressure
> alone (without lifter clatter) isn't necessarily a fault. This is why the gauge-tap advice
> should treat idle vs. running (≥4 psi idle / ≥30 psi @ 2000 rpm) as the thresholds.

---

# 8. Maintenance Schedule — MCM Sterndrive (Non-Horizon) `[source: §1B p1B-3..5]`

> Applies to your **MCM 454 Mag MPI sterndrive** (non-Horizon). Intervals are averages —
> owner/dealer should adjust to actual use/environment. Disconnect battery cables before any
> electrical work.

**Owner/operator — Weekly:**
- Engine crankcase oil — check level
- Closed-cooling coolant — check level
- Power-steering fluid — check level
- Sterndrive-unit oil — check level
- Battery — check level and inspect for damage
- Power-trim pump oil — check level
- Anodes — inspect for erosion
- Gear-housing water pickups — check for marine growth/debris
- Serpentine drive belt — inspect condition

**Dealer — End of first season, then every 100 hours or yearly (whichever first):**
crankcase oil & filter change · ignition clean/inspect · flame arrestor & crankcase-vent hose
clean · PCV valve change (if equipped) · sterndrive-unit oil change · gimbal-ring screws
retorque **50–55 lb-ft (67–74 N·m)** · rear engine mounts torque **38 lb-ft (52 N·m)** · gimbal
bearing lubricate · cooling system clean/inspect · engine alignment check · U-joint shaft
splines lubricate · steering system + steering head + remote control lube/inspect · electrical
wiring check · cooling hoses/clamps inspect · closed-cooling pressure cap test · continuity
circuit check · shift/throttle cable & linkage lube · exhaust system inspect · ignition timing
check/adjust · throttle body inspect · **fuel filter replace** · Mercathode output test.

**Dealer — Yearly:** closed-cooling coolant alkalinity test · heat-exchanger seawater section
clean · drive-unit bellows & clamps inspect.
**Dealer — every 200 hours or yearly:** universal-joint cross bearings inspect.
**Closed-cooling coolant — replace** every 5 years / 1000 hours (Extended-Life 5/100 coolant);
otherwise every 2 years / 400 hours.
**Seawater pickup pump** — disassemble & inspect whenever seawater flow is insufficient / temp
above normal.

# 9. Wiring Diagram Index & Applicable Harnesses `[source: §4E p4E-4..24]`

The manual has three harness families. **For your MCM 454 Mag MPI sterndrive, the applicable
diagrams are the two described below** (plus the instrument wiring in §5). Others are listed so
the AI knows they exist but don't apply to your boat.

| Diagram | Page | Applies to your 454 Mag MPI sterndrive? |
|---|---|---|
| Starting/Charging — MCM (Sterndrive) 7.4L MPI | 4E-6 | **YES** (engine starting/charging harness) |
| Starting/Charging — MIE (Inboard) 454 MPI Horizon & 8.2L | 4E-8 | No (inboard) |
| Starting/Charging — MIE (Inboard) 7.4L MPI | 4E-10 | No (inboard) |
| Fuel Injection — MEFI 2 MCM 7.4L MPI (L-29) | 4E-14 | No (earlier MEFI-2 / L-29 variant) |
| **Fuel Injection — MEFI 3 MCM (Sterndrive) 454 / 502 Mag MPI** | 4E-16 | **YES** (your EFI engine harness) |
| Fuel Injection — MEFI 3 MCM 7.4L MPI Bravo / MIE 7.4L | 4E-18 | Only if MEFI-3 7.4L MPI (not 454 Mag) |
| Instrumentation — Dual Station (neutral safety in one control) | 4E-20 | **YES** (see §5 above) |
| Instrumentation — Dual Station (neutral safety in both) | 4E-22 | If both stations have neutral-safety |
| Instrumentation — Dual Station (neutral safety in engine harness) | 4E-24 | Variant |

**DIAGRAM (75467) — "MCM (Sterndrive) 7.4L MPI" starting/charging harness (p4E-6):** the
engine-to-instrument harness. A **10-pin engine connector** carries: **GRY (pin 2) = tach**,
**PUR (5) = ignition +12 V**, **TAN/BLU (4)**, **RED/PUR (6) = fused +12 V**, **BLK (1) =
ground**, **YEL/RED (7) = start**, **LT BLU (8) = oil-pressure sender**, **TAN (3) = temp
sender**, **BRN/WHT (10) = trim sender**. Zone **A** = alternator (**ORN** output), ground stud,
starter motor + slave solenoid, battery (+/−); zone **B** = trim sender (BLU/TAN); zone **C** =
oil-pressure sender (grounded) and water-temp sender (TAN). Confirms the color/pin mapping the
CX5106 taps (BUG-14).

**DIAGRAM (76001) — "MEFI 3 MCM 454/502 Mag MPI" EFI engine harness (p4E-16) — YOUR ENGINE:**
the fuel-injection engine harness. NOTE on the page: *all black ground-symbol wires are
interconnected within the EFI harness.* Numbered component legend (this is the engine-bay
location index):
1 Fuel Pump · 2 Distributor · 3 Coil · 4 Knock Sensor (KS) Module · 5 Data Link Connector (DLC)
· 6 Manifold Absolute Pressure (MAP) Sensor · 7 Idle Air Control (IAC) · 8 Throttle Position
(TP) Sensor · 9 Engine Coolant Temperature (ECT) Sensor · 10 Electronic Control Module (ECM) ·
11 Fuel Pump Relay · 12 Ignition/System Relay · 13 Fuses — **15 A Fuel Pump, 15 A ECM/DLC/
Battery, 10 A ECM/Injector/Ignition/Knock Module** · 14 Harness connector to Starting/Charging
harness · 15 Positive (+) power wire to engine circuit breaker · 16 **Oil Pressure (Audio
Warning System)** · 17 Load Anticipation Circuit · 18 **Water Temperature Sender** · 19 Gear
Lube Bottle (sterndrive only).

> **Key BUG‑14/16 insight from the EFI harness:** on this EFI engine there are **two temperature
> devices** — the **ECT sensor (#9, feeds the ECM)** and the separate **Water Temperature Sender
> (#18, feeds the dash gauge)** — and oil has both the gauge sender and a separate **oil-pressure
> switch for the audio warning (#16)**. The **CX5106 must tap the gauge senders (#18 temp, the
> oil-pressure gauge sender), NOT the ECM sensors.** This is why gauge-post + meter identification
> (S102) is the reliable method, and why the standard BIA colors don't apply to this EFI harness.

---

<!-- OPERATIONAL SET COMPLETE (S106 2026-07-24). Sections: 1 Specifications/tolerances (BUG-16),
     2 Fluid Capacities + Break-in, 3 Charging/alternator voltage (BUG-17), 4 MerCruiser wiring
     color code, 5 Instrument wiring diagram (BUG-14), 6 Sender resistance tables, 7 Electrical/
     instrumentation troubleshooting, 8 Maintenance schedule, 9 Wiring diagram index + the two
     applicable engine harnesses (charging + EFI). This is the d3kOS-relevant operational
     reference. OUT OF SCOPE per operator (option 1): shop-rebuild sections §2,3,5,6,7,8 (~800 pp:
     engine R&I, fuel service, powerhead teardown, cooling, sterndrive/transmission rebuild,
     exploded parts views). Engine-side EFI harness does NOT use BIA standard colors — meter-based
     wire ID (S102 field procedure) remains authority for the Monterey 265's CX5106 taps. -->


