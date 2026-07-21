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

- Your AstroAI digital multimeter
- A short jumper wire to reach a known ground (engine block / battery negative)
- Masking tape + pen for labelling wires
- This sheet + a pen to fill in the results table at the bottom

---

## 2. Setting the digital multimeter (AstroAI 2000 Counts)

### To find the SENDER wire ("S") — measuring resistance
- Set the dial to **Ω → 2kΩ range**
- No zeroing needed — digital meters self-zero automatically.
- The display shows the actual resistance in ohms. A reading of "OL" means the wire is open (no path to ground) — not the S wire.
- Use 2kΩ (not 200Ω) because a cold temperature sender can read above 200Ω; 2kΩ covers the full 33–240Ω range without overloading.

### To find the 12V wire ("I") — measuring voltage
- Set the dial to **DC V → 20V range**
- The display shows the actual voltage. 12–14V with the engine running.
- **Do NOT use the 2V range** — it will show "OL" on a 12V circuit.

---

## 3. What each wire reads (this is how you tell them apart)

| Wire's real job | Key **OFF** — Ω (2kΩ range) to ground | Key **ON** — DC V (20V range) to ground |
|---|---|---|
| **I — Ignition (+12V in)** | OL / no reading | **~12–14 V** |
| **⭐ S — Sender / Signal (TAP HERE)** | **a resistance in range (~33–240 Ω)** | small, varying voltage |
| **G — Ground** | **~0 Ω** (display reads near zero) | 0 V |
| **L — Light** | OL / no reading | 0 V (→ 12V only when panel lights ON) |

> ⭐ **The S wire is the only one that reads a resistance (ohms) to ground with the key OFF.
> That is the wire the CX5106 taps.**

---

## 4. Step by step (at each gauge)

- [ ] **1. Key OFF.** Meter on **Ω → 2kΩ**. Back-probe each wire to a known ground.
  The **~0 Ω** wire = **Ground (G)**. The wire that reads a **resistance** = **Sender (S) — your target.**
- [ ] **2. Key ON.** Meter on **DC V → 20V**. The wire that jumps to **~12–14V** = **Ignition (I)**.
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
