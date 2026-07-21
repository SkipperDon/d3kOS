# CX5106 Wire Identification — Boat Field Procedure

**Boat:** 1994 Monterey 265 SEL
**Gauges to wire:** Fuel · Tach · Oil Pressure · Temperature · Trim
**Relates to:** BUG-14 (CX5106) and BUG-17 (battery voltage)

---

## ⚠️ GOLDEN RULE

- **Do NOT identify wires by colour.** Monterey did not follow the standard colour code on this boat.
  Identify each wire by **what the meter reads** and by the **letter (I / S / G / L) molded into the back of the gauge**.
- **NEVER unplug the tachometer / ignition harness.** Ignition power runs through it — disconnecting it
  stalls the engine. You only **tap alongside** wires, never cut or unplug them.

---

## 1. Tools to bring

- Your analog multimeter
- A short jumper wire to reach a known ground (engine block / battery negative)
- Masking tape + pen for labelling wires
- This sheet + a pen to fill in the results table at the bottom

---

## 2. Setting the OLD-STYLE (analog) multimeter

### To find the SENDER wire ("S") — measuring resistance
- Set the dial to **Ohms → Rx1**
- **Zero it first, every time:** touch the two probes together and turn the **ZERO OHMS / Ω ADJ** knob
  until the needle sits exactly on **0**.
- Read the **OHMS scale** — it runs **backwards** (0 on the RIGHT, infinity on the LEFT).
- On Rx1 the reading is direct (needle on 100 = 100 Ω). Look straight on to avoid parallax error.

### To find the 12V wire ("I") — measuring voltage
- Set the dial to **DC Volts → 50V range**
- Read on the **0–50 scale** — 12V lands about a quarter of the way across (13–14V with engine running).
- **Do NOT use a 10V or 15V range** — the charging system hits ~14V and will peg the needle.

---

## 3. What each wire reads (this is how you tell them apart)

| Wire's real job | Key **OFF** — Ohms (Rx1) to ground | Key **ON** — DC Volts (50V) to ground |
|---|---|---|
| **I — Ignition (+12V in)** | nothing / no reading | **~12–14 V** |
| **⭐ S — Sender / Signal (TAP HERE)** | **a resistance in range (~33–240 Ω)** | small, varying voltage |
| **G — Ground** | **~0 Ω** (needle swings full right) | 0 V |
| **L — Light** | nothing / no reading | 0 V (→ 12V only when panel lights ON) |

> ⭐ **The S wire is the only one that reads a resistance (ohms) to ground with the key OFF.
> That is the wire the CX5106 taps.**

---

## 4. Step by step (at each gauge)

- [ ] **1. Key OFF.** Meter on **Ohms Rx1**, zeroed. Back-probe each wire to a known ground.
  The **~0 Ω** wire = **Ground (G)**. The wire that reads a **resistance** = **Sender (S) — your target.**
- [ ] **2. Key ON.** Meter on **DC Volts 50V**. The wire that jumps to **~12–14V** = **Ignition (I)**.
  The wire that is 12V only with panel lights ON = **Light (L)**.
- [ ] **3. Confirm the S wire** using the proof for that gauge (Section 5).
- [ ] **4. Label the wire with tape** the moment you confirm it. Do this once — never re-guess.
- [ ] **5. Tap the CX5106 input to the confirmed S wire, IN PARALLEL** (T-tap / posi-tap). Leave the gauge wire connected.
- [ ] **6. Record it** in the results table at the bottom of this sheet.

---

## 5. Proof for each gauge — make the value move so you are 100% sure

| Gauge | How to prove you found S | What you should see |
|---|---|---|
| **Trim** ← do this FIRST | Move the trim up, then down | Ohms **sweep** smoothly. Unmistakable — teaches you the method. |
| **Temperature** | Cold engine vs. warmed up | Ohms **high when cold, low when hot** (~30–122 Ω) |
| **Oil pressure** | Engine off vs. running | Value **changes with pressure** (~10–184 Ω) |
| **Fuel** | Level can't be changed easily | Steady ohms **in the 33–240 Ω** range; dash fuel gauge agrees |
| **Tach / RPM** | Signal only exists while running | Find by **elimination** (the wire that is NOT I/G/L and NOT a resistive sender). **Better:** take RPM from the **alternator AC / "W" tap** — lower risk near the ignition. |

---

## 6. Safety

- **Ohms tests: key OFF.** Voltage tests: key ON — do not let the probe short 12V to ground.
- **Never unplug the tach / ignition harness** — it carries ignition power and will stall the engine.
- Engine-running tests (oil, tach): keep hands, probes and leads clear of belts and pulleys.
- Switch the CX5106's dedicated 12V line **ON only when the key is ON** — otherwise it reads false/zero values.

---

## 7. Results — fill this in on the boat (bring it back)

| Gauge | Wire COLOUR on the S post | Confirmed by (trim sweep / temp change / etc.) | Ohms measured |
|---|---|---|---|
| **Fuel** | | | |
| **Oil pressure** | | | |
| **Temperature** | | | |
| **Trim** | | | |
| **Tach / RPM** (source used) | | | |

---

*AtMyBoat.com — d3kOS field reference. Method is meter-based by design: it does not rely on any
wire-colour claim. Verify every wire before tapping.*
