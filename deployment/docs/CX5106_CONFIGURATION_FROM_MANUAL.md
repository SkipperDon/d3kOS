# CX5106 Engine Gateway — Configuration Guide (Manual-Derived)

**Version:** 1.0.0
**Created:** 2026-08-24 (S132)
**Status:** AUTHORITATIVE for DIP switch configuration — supersedes the DIP content of
`doc/CX5106_CONFIGURATION_GUIDE.md` and `doc/CX5106_USER_MANUAL.md` (see §8)
**Relates to:** BUG-14 (CX5106 not transmitting data PGNs), BUG-31 (false 0% fuel),
setup wizard Step 5 (`setup.html`)

---

## 1. Provenance — where this document's facts come from

Every fact in §2–§6 was read directly from the two-sided owner's leaflet that ships in the
CX5106 box. Nothing here is inferred from general marine-electronics knowledge.

| Source | Sheet code | Content | Resolution |
|---|---|---|---|
| `cx5106 manual 1.avif` (operator-supplied 2026-08-24) | **D2026-B** | §6 RPM speed ratio setting | 1200 × 1200 |
| `cx5106 manual 2.avif` (operator-supplied 2026-08-24) | **D2026-A** | §1–§4 spec, features, wiring diagram, terminal label | 1200 × 1200 |
| `assets/manuals/CX5106_10125_manual.pdf` (already in repo) | **D2026-A + D2026-B** | Same two sheets, scanned | 2544 × 3296 |

The operator-supplied AVIFs and the repo PDF are **the same two-page leaflet**, confirmed by the
sheet codes `D2026-A` / `D2026-B` printed in the top-right of each page. They were read
independently and cross-checked against each other. Where the degraded fax scan in the PDF and the
cleaner AVIF disagreed on a line of the terminal label, the AVIF at 7× magnification was taken as
authoritative.

**Device identity on the label plate:** `CX5106   08221`. The plate carries a CE mark and a
recycling mark. **It carries no manufacturer name and no brand.** See §8.4.

### 1.1 Internal consistency check (why this reading can be trusted)

The leaflet contains a self-checking fact. §2.2 states *"Up to 13 sensors can be collected."*
The terminal label independently lists **4 sensor inputs on the left** and **9 on the right** —
4 + 9 = **13**. The two statements were printed from different parts of the document and they
agree exactly. This confirms the terminal list in §4 is complete, correctly ordered, and that no
terminal was missed or double-counted.

---

## 2. What the device is

An analogue-sender to NMEA 2000 converter. It reads resistive and pulse senders from a
conventional engine harness and publishes them as NMEA 2000 PGNs.

| Property | Value | Source |
|---|---|---|
| Size | 100 mm × 68 mm × 50 mm | §1.1 |
| Sensor channels | Up to 13 | §2.2 |
| Operating voltage | 9–32 V DC | §3.1 |
| Voltage marked on the label plate | **VDC10~30V** | label |
| Power consumption | < 120 mA | §3.2 |
| Operating temperature | −30 to +75 °C | §3.3 |
| Storage temperature | −40 to +85 °C | §3.4 |
| Ingress protection | IP67 | §3.5 |
| Network connector | Micro-C NMEA 2000 | §4.1 |

> **Discrepancy in the manual itself:** §3.1 says 9–32 V; the label plate says 10–30 V.
> These are not the same. Use **10–30 V** as the design envelope — it is the narrower of the two
> and it is what is printed on the unit the installer is holding.

---

## 3. Sender ranges the device expects

Wiring a sender whose curve does not match one of these will produce a wrong reading, not a
missing one — the gauge will look alive and lie.

| Sender type | Range | Resistance |
|---|---|---|
| Pressure (oil, transmission oil) | 0–10 bar | 10–185 Ω |
| Temperature (coolant, transmission oil) | 40–120 °C | 301–22 Ω |
| Tank level — European standard | — | 0–190 Ω |
| Tank level — American standard | — | 240–33 Ω |

Note both temperature and pressure senders are **falling-resistance** (higher reading = lower
ohms). Tank level senders exist in both a rising (0–190 Ω) and a falling (240–33 Ω) form, which is
exactly why the device needs the selector switch described in §5.2.

---

## 4. Terminal map

Read from the label plate. Order is top to bottom as the plate is printed.

### Left-hand terminal block

| # | Terminal | Notes |
|---|---|---|
| 1 | `Tach(RPM)` | Pulse input — the tachometer signal |
| 2 | `Tilt/Trim` | Resistive |
| 3 | `Oil Pressure` | 10–185 Ω |
| 4 | `Coolant Temp.` | 301–22 Ω |
| 5 | `·····` | unused |
| 6 | `VDC10~30V` | supply positive |
| 7 | `GND` | supply negative |
| 8–10 | `·····` | unused |

### Right-hand terminal block

| # | Terminal | Notes |
|---|---|---|
| 1 | `Trans Oil Pressure` | 10–185 Ω |
| 2 | `Trans oil Temp.` | 301–22 Ω |
| 3 | `BlackWater` | level sender |
| 4 | `FreshWater` | level sender |
| 5 | `Fuel` | level sender |
| 6 | `LiveWell` | level sender |
| 7 | `Water in Fuel` | switch/sender |
| 8 | `Low Coolant Level` | switch/sender |
| 9 | `Over Temperature` | switch/sender |
| 10 | `GND` | sender common |

**Power:** the §4 diagram shows supply arriving through the ignition switch (marked `ING`) on a
two-pin connection, `2` = negative and `1` = positive, fed from the 9–32 V battery. The gateway is
therefore only powered with the ignition on — it is not a permanently live device.

---

## 5. The switches — the part that is most often got wrong

**The CX5106 has TWO physically separate switch blocks.** This is the single most important fact
in this document, and it is the fact that every previous d3kOS document and the setup wizard got
wrong (§8).

```
         ┌──────────────────────────────┐
         │                              │
         │   ┌────────────────┐         │   ← Block A: 7-position DIP
         │   │ ▮ ▮ ▮ ▮ ▮ ▮ ▮ │         │     ONE binary field = RPM speed ratio
         │   │ 1 2 3 4 5 6 7 │         │
         │   └────────────────┘         │
         │   ┌────┐                     │   ← Block B: 2-position switch
         │   │▮ ▮ │                     │     independent settings
         │   │1  2│                     │
         │   └────┘                     │
         └──────────────────────────────┘
```

Both blocks are on the PCB and are reached by opening the enclosure. In the leaflet diagram the
7-position block is called out to an enlarged graphic marked `ON` above positions `1 2 3 4 5 6 7`;
the 2-position block sits just below it and is called out by the two text boxes quoted in §5.2.

### 5.1 Block A — the 7-position DIP is ONE number, not seven settings

The seven positions do **not** each control a different feature. Together they encode a single
integer: the **RPM speed ratio**.

The leaflet heading is *"6.2 Toggle switch setting ratio (ratio range 1~127)"*, followed by a
lookup table of ratio values against switch pictures.

**The encoding, decoded from the printed table:**

> **Switch 1 is the least-significant bit. ON = 1, OFF = 0.**
> **ratio = 1 + (sw1×1) + (sw2×2) + (sw3×4) + (sw4×8) + (sw5×16) + (sw6×32) + (sw7×64)**

Equivalently: set the seven switches to the binary representation of `ratio − 1`, LSB first.

This was verified against every one of the 16 printed rows the leaflet shows in full:

| ratio | value = ratio−1 | sw1 | sw2 | sw3 | sw4 | sw5 | sw6 | sw7 |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | OFF | OFF | OFF | OFF | OFF | OFF | OFF |
| 2 | 1 | **ON** | OFF | OFF | OFF | OFF | OFF | OFF |
| 3 | 2 | OFF | **ON** | OFF | OFF | OFF | OFF | OFF |
| 4 | 3 | **ON** | **ON** | OFF | OFF | OFF | OFF | OFF |
| 5 | 4 | OFF | OFF | **ON** | OFF | OFF | OFF | OFF |
| 6 | 5 | **ON** | OFF | **ON** | OFF | OFF | OFF | OFF |
| 7 | 6 | OFF | **ON** | **ON** | OFF | OFF | OFF | OFF |
| 8 | 7 | **ON** | **ON** | **ON** | OFF | OFF | OFF | OFF |
| 9 | 8 | OFF | OFF | OFF | **ON** | OFF | OFF | OFF |
| 10 | 9 | **ON** | OFF | OFF | **ON** | OFF | OFF | OFF |
| 11 | 10 | OFF | **ON** | OFF | **ON** | OFF | OFF | OFF |
| 12 | 11 | **ON** | **ON** | OFF | **ON** | OFF | OFF | OFF |
| 13 | 12 | OFF | OFF | **ON** | **ON** | OFF | OFF | OFF |
| 14 | 13 | **ON** | OFF | **ON** | **ON** | OFF | OFF | OFF |
| 15 | 14 | OFF | **ON** | **ON** | **ON** | OFF | OFF | OFF |
| 16 | 15 | **ON** | **ON** | **ON** | **ON** | OFF | OFF | OFF |

All 16 rows match the formula with no exceptions. The leaflet then shows `⋮` and resumes at the
top of the range with ratios 125–128, which also match.

> **Range discrepancy in the manual:** the heading says the range is `1~127`, but the table
> includes a cell for `128`, and 7 bits with `ratio = value + 1` does reach 128. Treat `1~127` as
> the supported range; do not rely on 128 (all seven switches ON) being honoured.

### 5.2 Block B — the 2-position switch

These two are genuine independent settings. In the leaflet they are quoted as switch `"1"` and
switch `"2"` **of this block** — not positions 1 and 2 of the 7-position DIP.

| Switch | OFF | ON |
|---|---|---|
| **1** — level sender standard | `0–190 Ω` (European) | `240–33 Ω` (American) |
| **2** — engine position | `PORT` | `STBD` |

Verbatim from the leaflet:

> *"Level sensor signal `1` switch OFF is 0-190Ω (European), and `1` switch ON is 240-33Ω
> (American)."*
>
> *"`2` switch OFF is PORT, and `2` switch ON is STBD."*

Switch 1 applies to **all** level inputs — `Fuel`, `FreshWater`, `BlackWater`, `LiveWell`. There
is no per-tank selection. Getting it wrong does not blank the gauge; it produces a wrong
percentage, and because the two standards run in opposite directions it can read near-empty on a
full tank.

---

## 6. Choosing the speed ratio for your engine

§6.1 gives three lookup tables. Pick the one that matches your engine, get the ratio, then encode
it with §5.1.

### Inboard gas engine

| Cylinders | Cycle | Speed ratio |
|---|---|---|
| 4 | 4 | 2 |
| 6 | 4 | 3 |
| 8 | 4 | **4** |
| 10 | 4 | 5 |
| 12 | 4 | 6 |

### Outboard

| Poles | Speed ratio |
|---|---|
| 4 | 2 |
| 6 | 3 |
| 8 | 4 |
| 10 | 5 |
| 12 | 6 |

### Diesel

> **Speed Ratio = Gear Number**

That is the entire diesel rule as printed. The leaflet does not define "Gear Number" further.

---

## 7. Worked configuration — Monterey 265 SEL / MerCruiser 454 MAG MPI

This is the d3kOS reference boat.

**Engine:** MerCruiser 454 MAG MPI — V8, 8 cylinders, 4-cycle, inboard gasoline.

**Step 1 — ratio.** Inboard gas table, 8 cylinders, 4 cycle → **speed ratio 4**.

**Step 2 — encode.** ratio 4 → value 3 → `sw1 ON, sw2 ON, sw3–sw7 OFF`.

This does not rely on the formula alone: **ratio 4 is one of the rows the leaflet prints in full,
and its picture shows exactly positions 1 and 2 set.** Formula and printed table agree.

**Step 3 — Block B.** American boat with American senders → switch 1 **ON** (240–33 Ω).
Single engine → switch 2 **OFF** (PORT).

### Target configuration

| Block | Switch | Setting |
|---|---|---|
| A (7-pos DIP) | 1 | **ON** |
| A | 2 | **ON** |
| A | 3 | OFF |
| A | 4 | OFF |
| A | 5 | OFF |
| A | 6 | OFF |
| A | 7 | OFF |
| B (2-pos) | 1 | **ON** — 240–33 Ω American senders |
| B | 2 | OFF — PORT |

### 7.1 This does not match what was recorded on the physical unit

`MEMORY.md` / `project_cx5106_status.md` records, from S101, the DIP switches on the fitted unit
as: `SW1=ON, SW2=OFF, SW3=ON, SW6=ON`.

If those four refer to Block A, they encode value `1 + 4 + 32 = 37`, i.e. **speed ratio 38** —
against a required ratio of 4.

`Uncertainty flag: I cannot tell from the S101 record whether those four switch names refer to
Block A, Block B, or a mix of the two, because the record predates the discovery that there are
two blocks. Verify against the physical unit before changing anything.`

`Assumption: I am assuming the S101 note refers to Block A, since it names switches up to 6 and
Block B has only two. If wrong, the ratio-38 calculation above does not apply.`

### 7.2 Hypothesis for BUG-14 — explicitly NOT a finding

BUG-14's live symptom (S119, engine running): the CX5106 is present on the bus at source 106 and
emits heartbeat PGN 126993 every 60 s, but **zero data PGNs**.

A wrong speed ratio is a plausible contributor and is cheap to correct while the enclosure is
open. But it is a hypothesis, and a weak one on its own:

- A wrong ratio would normally produce a **wrong RPM value**, not the **absence** of data PGNs.
- It would not explain the absence of the non-RPM PGNs (oil pressure, temperature, fuel level),
  which do not depend on the ratio at all.

`Uncertainty flag: I have not verified that speed ratio affects data-PGN emission at all. Do not
record "wrong DIP ratio" as the root cause of BUG-14 on the strength of this document.` The
correct next action is to set the switches per §7 and re-observe the bus for at least 130 s (per
the standing rule that the CX5106 must never be diagnosed with a candump shorter than ~130 s).

### 7.3 Possible bearing on the false 0% fuel reading

BUG-31 recorded a false 0% fuel level on a confirmed-full tank. That was attributed to the Pangoo
device at source 64 and the bug was closed without remediation. Separately, Block B switch 1
selects the level-sender standard, and an American sender read on the European curve reads
backwards.

`Uncertainty flag: these may be unrelated — BUG-31's frozen frames were traced to source 64, not
to the CX5106 at source 106. Flagging the mechanism only so that Block B switch 1 is checked
while the case is open, not asserting a link.`

---

## 8. Validation against the existing d3kOS artifacts

The operator asked for these findings to be validated against this directory. All three d3kOS
artifacts that describe CX5106 DIP switches were read and compared against the leaflet.

### 8.1 The artifacts

| Artifact | Lines | Role |
|---|---|---|
| `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html` | 1611 | Live setup wizard, Step 5 of 8 — computes and displays DIP settings |
| `doc/CX5106_CONFIGURATION_GUIDE.md` | 525 | Wizard design doc, README-linked |
| `doc/CX5106_USER_MANUAL.md` | 936 | Standalone user manual |
| `reference/CX5106_DIP_SWITCH.md` | 1 | Placeholder, contains only the word `hold` |

### 8.2 The core divergence

All three substantive artifacts share one model of the hardware, and it does not match the
leaflet. From `setup.html` lines 1237–1248:

```
/* Row 1 — 8 switches (Engine Configuration)
 *   SW1-2 : Engine instance  00=single/port  10=starboard
 *   SW3-4 : RPM sensor type  00=alternator W-terminal
 *   SW5-6 : Cylinder count   cylinderMap below
 *   SW7   : Stroke type      0=4-stroke  1=2-stroke
 *   SW8   : Gear ratio       0=1:1 direct drive
 *
 * Row 2 — 2 switches (Regional)
 *   SW1   : Tank sender  1=North America (240-33Ω)  0=Europe (0-190Ω)
 *   SW2   : Position     0=primary/port  1=starboard
 */
```

`CX5106_USER_MANUAL.md` line 53 states the same premise in prose: *"The CX5106 has 8 switches
arranged in a row."*

### 8.3 Field-by-field comparison

| Aspect | Leaflet (authoritative) | d3kOS artifacts | Verdict |
|---|---|---|---|
| Main block width | **7** positions | 8 switches | ✗ wrong |
| What the main block means | ONE binary integer = speed ratio, sw1 = LSB | 5 independent feature fields | ✗ wrong |
| Engine instance | Not on the main block — it is Block B switch 2 (PORT/STBD) | Row 1 SW1–2 **and** Row 2 SW2 | ✗ wrong, and duplicated |
| RPM sensor type | No such setting exists | Row 1 SW3–4 | ✗ invented |
| Cylinder count | Indirect — cylinders → ratio via §6.1 table → binary | Row 1 SW5–6 as a 2-bit `cylinderMap` | ✗ wrong |
| Stroke type | No such setting exists | Row 1 SW7 | ✗ invented |
| Gear ratio | Diesel only, and it *is* the ratio (whole main block) | Row 1 SW8, "1:1 direct drive" | ✗ wrong |
| Tank sender standard | Block B switch 1: OFF = 0–190 Ω EU, ON = 240–33 Ω US | Row 2 SW1: 1 = NA 240–33 Ω, 0 = EU 0–190 Ω | ✓ **correct** |
| Position PORT/STBD | Block B switch 2: OFF = PORT, ON = STBD | Row 2 SW2: 0 = port, 1 = starboard | ✓ **correct** |

**Result: the 2-switch block is right. Everything the artifacts say about the 7-position DIP is
wrong.** The wizard's `buildDIPRow1()` (line 1253) returns an 8-element array for a 7-position
switch and assigns meanings that do not exist in the hardware.

Consequence for the reference boat: the wizard, given 8 cylinders and 4-stroke, produces
`cylinderMap['8'] = [0,1]` on SW5–6 and emits `OFF OFF OFF OFF OFF ON OFF OFF`. The correct
setting is `ON ON OFF OFF OFF OFF OFF`. They agree on no position.

### 8.4 Brand attribution

`setup.html` line 796 offers `<option value="cx5106">Actisense CX5106</option>`, and line 1328
renders the heading `Actisense CX5106 — Complete Configuration`.

The label plate carries **no brand at all** — only `CX5106  08221`, CE, and a recycling mark. The
same wizard separately and correctly lists the Actisense **EMU-1** as a different gateway option
(line 888), so the two are being conflated.

`Uncertainty flag: I have not established who does manufacture the CX5106. A prior WebSearch
(recorded under BUG-31) failed to confirm the "Pangoo" branding found on a neighbouring N2K
device as the CX5106's maker. The correct statement today is "manufacturer unconfirmed", not
"Actisense".`

### 8.5 Why this went undetected

The leaflet is the only documentation that exists for this device — there is no manufacturer
website or downloadable manual (recorded in `project_cx5106_status.md`). The 8-switch model is
internally coherent and resembles how comparable gateways genuinely do work, so it reads as
plausible. It was written once and then carried forward into 1,461 lines of documentation and a
live wizard without ever being checked against the leaflet — even though a scan of that leaflet
has been sitting in the repo at `assets/manuals/CX5106_10125_manual.pdf` the whole time.

This is the same failure mode recorded for BUG-08 (five fixes built on an untested docstring
claim) and for BUG-78 (a bug logged from `MASTER_SYSTEM_SPEC` §12.1 describing a script that does
not exist): **a plausible written premise was trusted in place of the primary source.**

---

## 9. Installation procedure

1. **Confirm engine parameters** — cylinders, cycle, and fuel type. For an outboard, get the pole
   count, not the cylinder count.
2. **Look up the speed ratio** in the matching §6 table.
3. **Encode the ratio** onto Block A per §5.1. Cross-check against the printed table row in the
   leaflet if the ratio is ≤ 16 or ≥ 125.
4. **Set Block B switch 1** to match the tank senders actually fitted — American 240–33 Ω or
   European 0–190 Ω. Confirm by measuring a sender, not by assuming from the boat's country.
5. **Set Block B switch 2** — OFF for a single or port engine, ON for starboard.
6. **Wire the senders** per §4, observing the ranges in §3. Sender commons go to the `GND`
   terminal of the block they belong to.
7. **Wire power** through the ignition switch, 10–30 V.
8. **Connect NMEA 2000** via Micro-C. Confirm the backbone is terminated at both ends and
   powered.
9. **Verify on the bus.** Observe for at least 130 s — the heartbeat PGN 126993 is only sent every
   60 s, so a shorter capture cannot distinguish "absent" from "not yet due".
10. **Verify the values, not just their presence.** Compare displayed oil pressure and RPM against
    the boat's analogue gauges. A wrong ratio or a wrong sender standard produces a confident
    wrong number, which is more dangerous than a blank gauge.

---

## 10. What this document does not cover

Stated explicitly so no future session mistakes silence for completeness.

- **The leaflet has no §5, and nothing after §6.** It jumps §4 → §6. Whether a §5 exists on some
  other sheet is unknown. If the device has configuration beyond the ratio and the two Block B
  switches, it is not documented in what we hold.
- **No PGN list.** The leaflet never states which PGNs the device emits for which terminal. The
  mapping from `Oil Pressure` to PGN 127489, and from `Fuel` to PGN 127505, comes from d3kOS bus
  observation (BUG-31, BUG-14), not from the manual.
- **No instance/address configuration** beyond PORT/STBD. How the device picks its NMEA 2000
  source address is undocumented.
- **No calibration.** There is no documented way to trim a sender curve, set tank capacity, or
  apply an offset. Tank capacity in particular appears to be set on the display side, not here.
- **No mention of the `08221` number's meaning.** It may be a hardware or firmware revision. The
  repo PDF is filed as `CX5106_10125_manual.pdf`; whether `10125` is a different revision of the
  same device is unconfirmed.
- **The physical silkscreen next to each switch block is not legible** in either scan. §5's
  identification of which block is which rests on the leaflet's callout arrows, plus the fact that
  one block clearly has seven positions and the other two. Confirm visually with the enclosure
  open before setting anything.

---

## 11. Open actions arising

These are recommendations. None has been executed — this document is the only artifact produced.

| # | Action | Why |
|---|---|---|
| 1 | Log a BUG-XX for the wizard's incorrect DIP model | Standing holistic bug rule: no fix without an entry first. **Not logged** — awaiting operator instruction. |
| 2 | Correct `setup.html` Step 5 to the 7-position ratio model | It currently instructs every d3kOS user to set their gateway wrongly |
| 3 | Correct or retire `doc/CX5106_CONFIGURATION_GUIDE.md` and `doc/CX5106_USER_MANUAL.md` | 1,461 lines built on the 8-switch premise. `CONFIGURATION_GUIDE` is README-linked and was on the branch intended to go public |
| 4 | Remove the "Actisense" attribution | §8.4 — factually wrong and conflated with the EMU-1 |
| 5 | Verify the fitted unit's actual switch positions | §7.1 — the S101 record cannot be interpreted now that two blocks are known |
| 6 | Set the reference boat to ratio 4 and re-observe the bus ≥ 130 s | §7.2 — cheap to do while the enclosure is open; may or may not bear on BUG-14 |
| 7 | Fill `reference/CX5106_DIP_SWITCH.md` or delete it | It contains only the word `hold` |

---

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-08-24 (S132) | Created. DIP encoding decoded from leaflet sheets D2026-A/B and verified against 16 printed table rows. Audit of `setup.html`, `CX5106_CONFIGURATION_GUIDE.md`, `CX5106_USER_MANUAL.md` recorded in §8. |
