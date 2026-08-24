# ATOMIC SPEC — PHASE 1: The Contract Test (A1.7)

**Purpose:** assert that every Signal K path the dashboard subscribes to, every DOM ID the JS writes to,
and every route the templates call **actually exists**. Make this defect class non-recurring.
**Severity:** highest-value item in Phase 1. **This class has recurred six times.**
**Tier:** Tier 1 specified; Tier 3 implementable (one test file + one generator).
**Created:** 2026-08-24 (S131) · **Target:** `tests/contract-dashboard.spec.ts`

---

## 1. WHY THIS EXISTS — six instances of one defect

| Bug | The mismatch |
|---|---|
| BUG-29 | subscribed `propulsion.0.*`; SK publishes `propulsion.port.*` — **every engine gauge dead** |
| BUG-30 | read `belowKeel`; SK publishes `belowTransducer` — depth dead |
| BUG-37 | `app.py` missing all seven v0.9.9.2 routes |
| BUG-38 | `overlays.js` writes three DOM IDs `index.html` never defines |
| BUG-41 | `/settings` HTTP 500 — `tier_num`/`device_token` never passed to the template |
| BUG-47 | no handler for `propulsion.port.coolantTemperature` — **the coolant gauge would still have been dead after the CX5106 was repaired** |

Six separate sessions, one defect: **a name on one side of a boundary that does not exist on the other.**
Every instance was found by a human noticing a dead gauge, sometimes on a boat, sometimes months later.

BUG-47 is the clearest argument for this test. It was found only because someone audited the alias block
by hand. Without that, the hardware fix would have landed and the gauge would still have read `---`, and
the conclusion would have been "the CX5106 repair failed."

**The same shape recurred three times for URLs** (BUG-34 → 46 → 48). BUG-48's guard test
(`bug48-no-hardcoded-localhost.spec.ts`) is the proof this approach works — that class has not returned.
This spec generalises it.

---

## 2. THE THREE CONTRACTS

### C1 — Signal K paths
**Derive, do not hardcode.** Extract every subscribed path from the served JS
(`instruments.js`, `boatlog-engine.js`, `overlays.js`, `helm-assistant.html`), then assert each exists in
the live SK tree (`GET /signalk/v1/api/vessels/self`) **or** in an explicit `EXPECTED_ABSENT` allow-list.

⚠ **The allow-list is mandatory and must be justified per entry.** The lab Pi has no engine, no depth,
no GPS and no AIS — 19 paths the dashboard consumes are legitimately absent. Without the allow-list the
test fails permanently and gets ignored, which is worse than not having it.

⚠ **Use LAB-SIM to populate the tree first** (`deployment/tools/lab-sim/run.sh cruise`), so real paths are
present and the allow-list stays small. LAB-SIM covers all 19 paths and is the reason this is testable at
all. Note its own history: it was publishing `coolantTemperature` with no handler — **the simulator had
the BUG-47 bug too.** Assert in both directions (section 3).

### C2 — DOM IDs
Extract every `getElementById` / `querySelector('#…')` target from the served JS; assert each exists in
the rendered DOM of the page that loads that JS. This is BUG-38 exactly.

⚠ **Assert against the rendered DOM, not the template source.** BUG-43's tests were written this way
deliberately, and BUG-49 proved why: the "invisible wordmark" was never a text element at all — the logo
404'd and the browser rendered `alt` text. Source inspection would have confirmed a wordmark that did not
exist.

### C3 — Routes
Extract every `fetch()` / `href` / form action from the templates and JS; assert each returns something
other than 404 from the live Flask app. This is BUG-37 and BUG-41.

⚠ **A 500 must fail the test.** BUG-41 was a 500, not a 404. Accept 200/302/401/405; **fail on 404 and on
any 5xx.**

---

## 3. THE BIDIRECTIONAL ASSERTION — the part that catches the next BUG-47

A one-way check ("every path I subscribe to exists") would **not** have caught BUG-47, because the
dashboard never subscribed to `coolantTemperature` at all. The defect was a *missing* handler.

So assert both directions:

1. **Every path subscribed → exists in SK** (or allow-listed).
2. **Every path in the BUG-29 alias block has its `propulsion.port.*` twin.** BUG-47's own test already
   does this — *"the alias test computes what is required from the live page, so a NEW `propulsion.0.*`
   handler added without its port alias fails the suite."* **Reuse that mechanism; do not reinvent it.**
3. **Every path LAB-SIM publishes has a handler.** This is what would have caught the simulator's own
   defect.

Direction 2 is what makes the test *preventive* rather than merely descriptive.

---

## 4. IMPLEMENTATION CONSTRAINTS

- **Read from the served files, not the repo.** `http://<pi>:3000/static/js/instruments.js`. The repo and
  the Pi can differ (the entire point of BUG-28), and the contract that matters is the one being served.
- **Never run against `localhost`.** BUG-46's test refuses to, because a tunnel hides the bug. Same rule.
- **No hardcoded path list.** A hardcoded list is documentation that rots. Extract at runtime.
- **Fail with the specific name.** `"propulsion.port.coolantTemperature subscribed but absent from SK
  and not allow-listed"` — not `"contract violation"`. BUG-48 was found because a test named the missing
  sites.
- **Count what you extracted and assert the count is non-zero.** If the regex silently matches nothing,
  a broken test passes. This is the S114 lesson in test form: **an audit that returns nothing is not a
  clean audit.**

---

## 5. TESTS OF THE TEST

A guard test is worthless unless it demonstrably bites. Prove each historical bug would have been caught:

| # | Inject | Expect |
|---|---|---|
| T1 | Revert `instruments.js` to `propulsion.0.*` only | FAIL naming the missing aliases (BUG-29) |
| T2 | Change `belowTransducer` → `belowKeel` | FAIL (BUG-30) |
| T3 | Remove a route from `app.py` | FAIL naming it (BUG-37) |
| T4 | Remove a DOM ID from `index.html` | FAIL naming it (BUG-38) |
| T5 | Break `/settings` to 500 | FAIL — proves 5xx is not treated as pass (BUG-41) |
| T6 | Delete the `coolantTemperature` alias | FAIL (BUG-47) — **the bidirectional test** |
| T7 | Make every extraction regex match nothing | **FAIL, not pass** (section 4 last bullet) |
| T8 | Clean system, LAB-SIM `cruise` running | PASS, exit 0 |

**T6 and T7 are the two that matter.** T6 proves it catches an absence rather than only a mismatch. T7
proves the test cannot pass by failing to look — which is precisely how the S114 spec came to list 17
call sites when there were 30.

---

## 6. DEFINITION OF DONE

- [ ] T1–T8 all behave as specified, **each verified by actually injecting the regression**
- [ ] Wired into `tests/run-all.sh`, exiting non-zero on violation
- [ ] `EXPECTED_ABSENT` allow-list has a one-line justification per entry, reviewed by Tier 1
- [ ] Runs green against the lab Pi with LAB-SIM `cruise` active
- [ ] BUG-29/30/37/38/41/47 entries cross-referenced to this test as their non-recurrence guard

## 7. WHAT THIS DOES NOT DO

- **Does not test values, only existence.** A gauge wired to a real path can still render the wrong
  number (BUG-43 units, BUG-13 flicker). Those need their own tests and have them.
- **Does not cover the Pi↔HostPapa boundary.** Same idea, different surface — `PHASE3-endpoint-contract-test.md`.
- **Does not replace LAB-SIM.** It depends on it.
