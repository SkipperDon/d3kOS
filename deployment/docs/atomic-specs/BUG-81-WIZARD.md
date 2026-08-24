# ATOMIC SPEC — BUG-81 (P1 + P4): Setup Wizard CX5106 DIP Configuration

**Defect:** Wizard Step 5 computes and displays an 8-switch DIP layout that does not exist on the
hardware, and attributes the device to Actisense, which is unsupported.
**Severity:** HIGH — every d3kOS user with a CX5106 is instructed to configure their gateway wrongly.
**Scope:** the wizard (P1, P4) **plus the local guide that specifies it** (section 1.5 Step 0 — added after the
operator identified it). P2 (the **public** `docs/` guide) and P3 remain excluded — see section 8.
**Tier:** Step 2 is Tier 3 (exact replacements). Step 1 is operator/Tier 1 — **it is a hard gate.**
**Created:** 2026-08-24 (S132-cont) · **Bug record:** `V09994_BUG_FIXES.md` BUG-81

---

## 1. WHAT I VERIFIED MYSELF, AND WHAT I DID NOT

The Hardware Claim Protocol applies: this spec instructs a physical configuration, so the provenance of
every hardware claim matters.

### Verified directly from the device photograph (`assets/images/cx5106_10125.png`)

✅ **Block A has exactly 7 positions**, numbered `1 2 3 4 5 6 7` beneath an `ON` / `DIP` legend.
✅ **Block B is a physically separate 2-position switch**, numbered `1 2`, offset below and right of
Block A, with a green LED between them.
✅ **No manufacturer name appears anywhere on the enclosure.** The only label carries numerals and a CE
mark. **This confirms P4: the "Actisense" attribution has no basis.**

**This is direct visual confirmation that the wizard's "8 switches in a row" model is wrong.** The device
has 7 + 2, in two separate blocks.

### NOT independently verified — inherited from S132's reading of the leaflet

⚠ **The ratio-encoding formula** (`ratio = 1 + sw1×1 + sw2×2 + … + sw7×64`, sw1 = LSB).
⚠ **Block B semantics** (sw1 = sender standard, sw2 = PORT/STBD).

**Now resolved:** the engine-to-ratio lookup is transcribed in `docs/CX5106_DIP_SWITCH.md`
section 6 — see Step 1 below. It is no longer blocked.

**Why I could not verify them:** `assets/manuals/CX5106_10125_manual.pdf` is a **pure image scan** — two
CCITTFaxDecode images with no text layer — and `pdftoppm` is not installed on this workstation, so it
cannot be rendered for reading.

**→ ACTION: install `poppler-utils` on the workstation.** Until then the only authoritative CX5106
document in the repo is unreadable by any session, which is precisely how a fabricated model survived in
three artifacts for months. This is a tooling gap with a track record.

⚠ **Operator note:** you mentioned *"a new updated manual for CX5106 was published."* The only manual I
found is `assets/manuals/CX5106_10125_manual.pdf`, dated 2026-08-23, which is the same document S132
worked from. **If a newer revision exists, this spec must be re-checked against it before Step 2 runs** —
particularly section 3's ratio table, which is the part I could not read.

---

## 1.5 STEP 0 — CORRECT THE GUIDE FIRST. It is the wizard's specification.

**Added after the operator identified `doc/CX5106_CONFIGURATION_GUIDE.md` as "the guide".**

This is not merely another document carrying the wrong model. **It is the document the wizard was built
from**, and it contains a complete, numbered specification of Step 5:

```
Q1 Number of Engines        Q5 Engine Stroke Type   -> SW7
Q2 Engine Position          Q6 Gear Ratio           -> SW8
Q3 RPM Signal Source        Q7 Tank Sensor Standard -> row 2 SW1   (correct)
Q4 Number of Cylinders -> SW5|SW6      Q8 Engine Position row 2 SW2 (correct)
```

The wizard's `buildDIPRow1()`, `cylinderMap`, `buildRow1Key()` and `buildWhyText()` are a **faithful
implementation of Q1–Q6.** The code is not independently wrong; it correctly implements a wrong spec.

⚠ **Therefore: fixing the wizard without fixing this guide guarantees the defect is rebuilt.** The next
person to touch Step 5 will read the guide, find it contradicts the code, and "restore" the guide's
model. Correct the specification before the implementation.

### Good news — no GitHub approval needed for this one

| Path | Local | On `origin/main` |
|---|---|---|
| `doc/CX5106_CONFIGURATION_GUIDE.md` | **YES** | **no** |
| `docs/CX5106_CONFIGURATION_GUIDE.md` | no | **YES** ← this is BUG-81 P2, public |
| `docs/CX5106_DIP_SWITCH.md` | YES | YES |

**`doc/` (singular) is local-only.** It can be corrected immediately under the ordinary Pre-Change File
List rule. **`docs/` (plural) is the public one** and still requires explicit operator approval.

### The finding that explains why this survived so long

Three consecutive lines of the guide, verbatim:

```
23:  ![CX5106 DIP Switches](../assets/images/cx5106_10125.png)
25:  *Photo showing the actual CX5106 DIP switch locations on the device*
27:  The DIP switches are located on the side of the CX5106 unit and are clearly
      labeled 1-8 from left to right.
```

**The guide embeds the photograph that disproves its own central claim, one line above making it.** The
photo shows a 7-position block plus a separate 2-position block, on the face of the unit with the lid
removed — not eight in a row, and not "on the side". **Two factual errors in one sentence, refuted by the
image directly above it.**

⚠ **And here is the root cause of the longevity: S132's only change to this file was fixing the image
path** (`../../assets/…` → `../assets/…`). From `doc/`, the old path resolved outside the repo, so **the
image never rendered.** The disproving evidence was cited, present, and invisible for the file's entire
life.

**Lesson to carry into every future spec: a document that cites evidence is not the same as a document
whose evidence has been looked at.** Verify the link renders, then verify the artifact says what the prose
claims. This is the same failure shape as the S114 truncated audit — the check was performed, but on
nothing.

### Step 0 actions

1. Correct Part 1 (DIP switch logic) to the 7 + 2 block model.
2. Correct Q4/Q5/Q6 — the cylinder-count, stroke-type and gear-ratio questions map to nothing on this
   hardware. Replace with the single engine-type → ratio question.
3. **Keep Q7 and Q8 unchanged** — tank-sender standard and engine position are correct.
4. Fix the "located on the side… labeled 1-8" sentence.
5. Add a dated correction note; **preserve the original as superseded**, not deleted — it is the record of
   what the wizard implements today and reviewers will need it during Step 2.
6. Cross-link `docs/CX5106_DIP_SWITCH.md` (S132's derivation guide) as the authority.

---

## 2. STEP 1 — GATE CLEARED. The lookup exists, and it changes the design.

⚠ **Superseded:** an earlier draft of this spec treated the engine-to-ratio lookup as unread and
blocked on installing `poppler-utils`. **It is already transcribed** — `docs/CX5106_DIP_SWITCH.md`
section 6 carries all three of the leaflet's lookup tables. Read that, not the PDF.

### The three tables (transcribed from the leaflet by S132)

**Inboard gasoline** — ratio is half the cylinder count:

| Cylinders | Cycle | Ratio |
|---|---|---|
| 4 | 4 | 2 |
| 6 | 4 | 3 |
| **8** | **4** | **4** |
| 10 | 4 | 5 |
| 12 | 4 | 6 |

**Outboard** — keyed on **poles**, not cylinders: 4→2, 6→3, 8→4, 10→5, 12→6.

**Diesel** — the leaflet's entire rule is `Speed Ratio = Gear Number`. No table. "Gear Number" is
not defined anywhere in the leaflet.

### THE DESIGN PROBLEM THIS EXPOSES — read before coding

**The wizard's existing inputs are sufficient for only one of the three engine families.**

| Family | Leaflet needs | Wizard collects? |
|---|---|---|
| Inboard gasoline | cylinders + cycle | ✅ yes — computable today |
| **Outboard** | **pole count** | ❌ **no.** Poles are not cylinders, and the figure normally lives in the *service* manual, not the owner's manual |
| **Diesel** | **"Gear Number"** | ❌ **no.** Undefined term, no table, nothing to look up |

So a `RATIO_BY_ENGINE` map keyed on `cylinders + stroke` — which is what the earlier draft of this
spec proposed — **is correct for inboard gasoline and silently wrong for every outboard and every
diesel.** That is the same defect class as BUG-81 itself: a model that fits the reference boat and
fails everything else.

⚠ **Note on my own earlier caution.** This spec previously forbade inferring `ratio = cylinders ÷ 2`.
The leaflet's inboard-gasoline table turns out to match that formula exactly — so the inference was
*right for one family*. The caution was still correct, and this is why: coding it blindly would have
produced wrong settings for every outboard and diesel on the strength of a pattern that only holds
for petrol inboards. **Being accidentally right about a third of the cases is not the same as being
right.**

### Required wizard behaviour

1. **Ask engine family first** — inboard gasoline / outboard / diesel. The wizard currently collects
   `fuel` and `isTwoStroke` but **not** inboard-vs-outboard. ⚠ **Do not infer outboard from
   2-stroke.** It correlates and is not equivalent.
2. **Inboard gasoline** → compute from the table. This is the only automatic path.
3. **Outboard** → new input: pole count, with a plain-language note that it is usually in the
   service manual. If unknown → route to (5).
4. **Diesel** → ask for the gear number if the owner has it; state plainly that the leaflet does not
   define the term. If unknown → route to (5).
5. **Unknown → the empirical method, not a guess.** `docs/CX5106_DIP_SWITCH.md` section 10 gives the
   procedure: start at ratio 2, run at a steady known RPM, compare displayed against the analogue
   tachometer, adjust by the observed factor, **try both directions**, and confirm at idle *and*
   cruise. The wizard must present this as a first-class outcome — for outboards and diesels it is
   the *expected* path, not a failure state.

⚠ **The wizard must never state which direction the ratio scales RPM.** Section 10 step 4 is
explicit that this depends on internals the leaflet does not document. Any confident statement about
direction would be a fabricated hardware claim — the exact defect being fixed.

⚠ **One useful diagnostic to surface in the UI**, straight from section 10: a ratio error is a
*constant factor*, so it is wrong by the same proportion at every engine speed. **If the error
changes with RPM, the ratio is not the problem — the tachometer signal source is.** This is worth
showing the user, because it saves them chasing switch settings for a wiring fault.

## 3. STEP 2 (Tier 3) — the wizard replacements

**Target:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html`

### Prerequisites — abort if any fails

| # | Check | Expected |
|---|---|---|
| P1 | `grep -c "cylinderMap" setup.html` | `1` |
| P2 | `grep -c "buildDIPRow1" setup.html` | `3` (definition + 2 call sites) |
| P3 | `grep -c "Actisense CX5106" setup.html` | `2` (lines 796, 1328) |
| P4 | `grep -c "(8 switches)" setup.html` | `2` (both on line 1348) |
| P5 | `buildDIPRow2` returns a 2-element array | true — **this one is CORRECT, do not touch it** |

### Replacement A — the encoder replaces the fabricated field map

`old` (exact):
```javascript
  var cylinderMap = {
    '1':[0,0],'2':[1,0],'3':[0,1],'4':[0,0],'6':[1,0],'8':[0,1],'12':[1,1]
  };

  function buildDIPRow1(cylinders, isTwoStroke, instance) {
    var c = cylinderMap[String(cylinders)] || [0,0];
    var inst = (instance === 1) ? [1,0] : [0,0];
    return [inst[0], inst[1], 0, 0, c[0], c[1], isTwoStroke ? 1 : 0, 0];
  }
```

`new`:
```javascript
  /* Block A - 7 positions, ONE binary field: the RPM speed ratio.
   * sw1 = LSB.  ratio = 1 + (sw1*1 + sw2*2 + sw3*4 + sw4*8 + sw5*16 + sw6*32 + sw7*64)
   * Source: CX5106 leaflet sheet D2026-B section 6, verified against every fully
   * printed row of its table (ratios 1-16 and 125-128).
   * There is NO engine-instance, RPM-sensor-type, cylinder-count, stroke-type or
   * gear-ratio field on this device. Those were fabricated. See BUG-81.
   * Engine instance / PORT-STBD is Block B switch 2 - see buildDIPRow2. */
  /* Three separate lookups - one per engine family. Transcribed from the
   * leaflet via docs/CX5106_DIP_SWITCH.md section 6.
   * NOTE: outboard is keyed on POLES, not cylinders. Diesel has no table at
   * all - the leaflet says only "Speed Ratio = Gear Number" and never defines
   * the term. Do NOT collapse these into one cylinder-keyed map: that is
   * correct for petrol inboards and silently wrong for everything else. */
  var RATIO_INBOARD_GAS = { '4':2, '6':3, '8':4, '10':5, '12':6 };   /* cylinders, 4-cycle */
  var RATIO_OUTBOARD    = { '4':2, '6':3, '8':4, '10':5, '12':6 };   /* POLES, not cylinders */

  function ratioForEngine(family, cylinders, poles, gearNumber) {
    if (family === 'inboard-gas') return RATIO_INBOARD_GAS[String(cylinders)] || null;
    if (family === 'outboard')    return RATIO_OUTBOARD[String(poles)]        || null;
    if (family === 'diesel')      return (gearNumber > 0) ? gearNumber : null;
    return null;                  /* null = unknown -> route to the empirical
                                   * method (guide section 10). NEVER guess. */
  }

  function encodeRatio(ratio) {
    if (!(ratio >= 1 && ratio <= 128)) return null;
    var n = ratio - 1, out = [];
    for (var i = 0; i < 7; i++) { out.push((n >> i) & 1); }
    return out;                             /* 7 elements, sw1 first */
  }

  function buildDIPBlockA(cylinders, isTwoStroke) {
    var r = ratioForEngine(cylinders, isTwoStroke);
    return r === null ? null : encodeRatio(r);
  }
```

⚠ **`null` propagates deliberately.** If the engine type is not in the transcribed table, the wizard must
**say so** and refuse to display a setting. **It must never fall back to a default.** The old code's
`|| [0,0]` fallback is how a wrong-but-plausible setting reached every user — a silent default on a
hardware-configuration screen is worse than an error message, because the user acts on it.

### Replacement B — key text

Replace `buildRow1Key(...)` entirely. It must state the ratio and the derivation, not invented fields:
```
Block A (7 switches): RPM speed ratio 4  —  switches 1,2 ON; 3-7 OFF
Derived from: 8-cylinder 4-cycle → leaflet section 6.1
```
**`buildRow2Key()` is correct — leave it exactly as it is.**

### Replacement C — remove the fabricated explanations

`buildWhyText()` explains SW1–2 engine instance, SW3–4 RPM sensor, SW5–6 cylinder count, SW7 stroke,
SW8 gear ratio. **Five of those six fields do not exist.** Replace with an explanation of the ratio
model. **Retain only the tank-sender paragraph, which is correct** — including its true and useful
warning that the wrong setting inverts the reading.

### Replacement D — the "(8 switches)" labels

`old` (exact, both on one line):
```javascript
      portTitle.textContent = twinEnabled ? '⚓ Port Engine — Row 1 (8 switches)' : '⚓ Row 1 — Engine Configuration (8 switches)';
```
`new`: `(7 switches)`, and rename "Row 1" → **"Block A"** / "Row 2" → **"Block B"**. The blocks are
physically separate on the device — visible in the photo — and "Row 1 / Row 2" implies one component.
Apply the same rename to the `dip-*-row1` / `row2` element IDs **only if** every reference is updated
together; otherwise leave the IDs and change display text only. **A half-renamed ID is BUG-38.**

### Replacement E — remove the Actisense attribution (P4)

`old`: `            <option value="cx5106">Actisense CX5106</option>`
`new`: `            <option value="cx5106">Matsutec CX5106</option>`

⚠ **Use "Matsutec", not "no brand".** An earlier draft of this spec suggested leaving it unbranded
because the label plate carries none. **The operator corrected that:** `project_cx5106_status.md`
already recorded Matsutec from S119 research, so the fix is to replace a wrong maker with the right
one, not to mark it unknown. The plate being unbranded is a fact about the plate, not about the
manufacturer.

`old`: `      var ctxTitle = 'Actisense CX5106 &mdash; Complete Configuration';`
`new`: `      var ctxTitle = 'CX5106 &mdash; Complete Configuration';`

⚠ **Leave the Actisense EMU-1 entries untouched** (lines 797, 888, 889). The EMU-1 **is** an Actisense
product and is correctly attributed; conflating the two is what created P4. **Do not sweep "Actisense"
globally** — that would break a correct entry. Two precise replacements, no more.

### Twin-engine handling — a behavioural change to confirm

The old model put engine instance on Block A SW1–2. On the real hardware, PORT/STBD is **Block B switch
2**, which `buildDIPRow2` already handles correctly. So for a twin installation, **both gateways get the
same Block A** (same engine type → same ratio) and differ only in Block B sw2.

⚠ **This is a real behavioural change and the twin path must be re-tested.** The starboard block at lines
1355–1361 currently calls `buildDIPRow1(..., 1)`; after this change Block A takes no instance argument.

---

## 4. TESTS — TDD, failing first

**Target:** `tests/bug81-cx5106-dip.spec.ts` (Playwright, asserting the **rendered DOM**, per BUG-43/49)

| # | Test | Pre-fix | Post-fix |
|---|---|---|---|
| T1 | Block A renders exactly **7** switch elements | FAIL (8) | PASS |
| T2 | 8-cyl 4-cycle → Block A = `ON ON OFF OFF OFF OFF OFF` | FAIL | PASS |
| T3 | `encodeRatio(13)` → switches 3,4 ON (leaflet-printed row) | FAIL | PASS |
| T4 | `encodeRatio(125)` → switches 3,4,5,6,7 ON (leaflet-printed row) | FAIL | PASS |
| T5 | `encodeRatio(1)` → all seven OFF | FAIL | PASS |
| **T6** | **Unknown engine type → an explicit "cannot determine" message, and NO switch diagram** | FAIL (silently emits a default) | PASS |
| T7 | Twin: both gateways identical Block A; Block B sw2 differs | FAIL | PASS |
| T8 | Block B unchanged from current correct behaviour | PASS | PASS (**must not regress**) |
| T9 | No "Actisense" on any CX5106 element; EMU-1 entries still say Actisense | FAIL | PASS |
| T10 | No rendered text contains "8 switches" | FAIL | PASS |
| T11 | All wizard text ≥ 18px (AODA) | PASS | PASS |
| **T12** | **Outboard selected, pole count unknown** | n/a | **empirical-method instructions shown, NO switch diagram** |
| **T13** | **Diesel selected, gear number unknown** | n/a | **same** — and the text states the leaflet does not define the term |
| T14 | Outboard, 8 poles | n/a | ratio 4 — and **not** derived from cylinders |
| T15 | Diesel, gear number 3 | n/a | ratio 3 |
| T16 | No rendered text claims a direction for RPM scaling | n/a | PASS |

**T6 is the most important test.** T1–T5 prove the arithmetic; T6 proves the wizard refuses to guess.
Given this defect was born from a confident guess, the fix must be structurally incapable of one.
**T8 is the regression guard** for the two mappings that were already right.

---

## 5. ROLLBACK

`setup.html.pre-bug81.bak` on the Pi; `git checkout` the one repo file. No service restart needed for
static assets — but **`setup.html` is a template, so restart `d3kos-dashboard`** (templates require a
restart; static files do not).

---

## 6. DEFINITION OF DONE

- [ ] Leaflet section 6.1 transcribed and cited — **Step 1 gate cleared, nothing inferred**
- [ ] `poppler-utils` installed so the manual is readable by future sessions
- [ ] Confirmed whether a newer manual revision exists (operator's note)
- [ ] T1–T11 pass; T6 and T8 verified by injection
- [ ] Twin-engine path re-tested (section 3 behavioural change)
- [ ] Deployed to lab Pi under the standing authorisation; `d3kos-dashboard` restarted
- [ ] Screenshot of Step 5 reviewed by the operator against the physical device
- [ ] BUG-81 entry updated: **P1 and P4 closed; P2 and P3 still open**

---

## 7. WHY THIS MATTERS BEYOND THE WIZARD

BUG-14 is open: the CX5106 sits on the bus at source 106, emits a heartbeat every 60 s, and produces
**zero data PGNs even with the engine running**.

⚠ **Do not treat this fix as BUG-14's root cause.** A wrong ratio yields a **wrong RPM number**, not the
**absence** of data PGNs, and it cannot explain missing oil/temperature/fuel PGNs, which do not depend on
the ratio at all. BUG-81's own record states this correctly and it must not drift.

**But:** setting the ratio correctly is nearly free while the enclosure is already open, and the switch
count alone proves the previous setting was arbitrary. **Do it on the same visit, then re-observe the bus
for ≥130 s** — under that, the 60-second heartbeat is missed and a working device reads as dead.

## 8. EXPLICITLY OUT OF SCOPE

- **P2 — `docs/CX5106_CONFIGURATION_GUIDE.md` on public `main`, README-linked twice.** ⚠ **This is the
  highest-impact part of BUG-81** — a stranger following the README today gets wrong instructions for
  their hardware. It is a **public GitHub change requiring explicit operator approval**, so it is not in
  this spec. **It should be sequenced first, not last.**
- **P3 — `doc/CX5106_USER_MANUAL.md` line 53.**
- ⚠ **NO LONGER out of scope: `doc/CX5106_CONFIGURATION_GUIDE.md`.** It is the wizard's specification and
  is now **Step 0** (section 1.5). It is local-only, so it needs no GitHub approval — only the ordinary
  Pre-Change File List.
- **`docs/CX5106_DIP_SWITCH.md`** — written S132, currently **uncommitted in the working tree**. Publishing
  it is part of the P2 decision.
- ⚠ **Six files are modified and uncommitted, and `doc/CX5106_CONFIGURATION_GUIDE.md` is open in an editor
  (`.~lock` present). Commit or stash that work before anyone edits those files.**
