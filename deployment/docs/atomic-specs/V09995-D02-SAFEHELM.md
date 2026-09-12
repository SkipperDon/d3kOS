# D02 — SafeHelm Advisory Mode · Atomic Spec

**Document:** V09995-D02-001 · **Version:** 1.0 · **Date:** 2026-09-12 (S161)
**Author:** Claude Opus 5 (Tier 1) · **Implementer:** Tier 3 (Haiku) · **Orchestrator:** Tier 2 (Sonnet)
**Design reference:** `V09995_SOLUTION_DESIGN.md` §8 (all sub-sections), §12.4, §13, §14
**Port:** 8095, bound `127.0.0.1` · **AIS source:** Signal K WebSocket **8099** · **Voice:** `POST http://127.0.0.1:3002/webhook/alert`

---

## 1. Read this before anything else

This is the most safety-critical component in d3kOS. §1 of the design doc is normative:

> **SafeHelm assists the captain. It does not command, steer, or decide.** Every output is a
> recommendation. The captain's judgment overrides the system in all cases.
> **Silence is not clearance** — no alert means no *qualifying AIS target*, not "clear water".

**Wrong right-of-way advice is the worst output this system can produce.** That is not
rhetoric — v1.0 of this design contained two defects that would have produced exactly that:

| v1.0 defect | What the captain would have heard |
|---|---|
| **Rule 14 inverted** — `course_diff < 15` fires on *parallel* courses (0 = same direction, 180 = reciprocal) | Two boats cruising **side by side**: *"Danger. Head-on situation."* A real head-on fell through to the crossing branch and never fired. |
| **Rule 13 role inverted** — bearing 112.5–247.5 is abaft **our** beam, so they overtake **us** and **we are stand-on** | *"You do not have right-of-way"* — told to give way while legally obliged to hold course and speed. |

Both were authored by a capable model and caught only by review. Four further COLREGs rules
(11, 13(c), 13(d), 17(b), 18) were found missing over four subsequent review rounds.

**Consequence for you: every algorithm in §4 is `[T1]`-authored and is transcribed
verbatim. Nobody at Tier 2 or Tier 3 reasons about COLREGs geometry.** If a `[T1]` block
looks wrong, escalate — you may be right, but the path is escalation, never a silent edit.

### 1.1 Gate status

- ✅ **Gate item 6 is CLOSED** (S161, design §12.4). Maritime sign-off was withdrawn as
  unobtainable and replaced by the two-phase split: **option B now**, Rule 19(d) / D18 in
  v0.9.9.6. 6a is done; **6b is an operator action that does not gate code**; **6c is a
  build task in this spec** (§8). **Do not re-raise maritime sign-off.**
- ✅ **§12.1 items 1–5 DONE** — 160 guard cases exist, verified red (`160 failed, 0 errors`),
  validated in both directions, and `run-all.sh` can no longer report a non-collecting file
  as green (BUG-124).

---

## 2. ⚠ TIER-1 ARCHITECTURAL RULING — the D02 layout conflict

**The design doc contradicts itself on where D02 code lives, and the 160 guard tests encode
one side of it.** Found S161.

| Source | Says |
|---|---|
| **§8.1** (written v1.1) | Flat layout: `opt/d3kos/services/safehelm/{cpa_engine,colregs_classifier,alert_gate,alert_manager,voice_arbiter,signalk_client,...}.py` |
| **§8.0 / D02-9** (operator decision, v1.12) | Plugin-shaped: `signalk-safehelm/engine/*.py` behind a Node shim — and *"deletes `signalk_client.py`, the reconnect logic and the port question outright"* |
| **v1.11 revision note** | *"**Blocks the §8.1 file layout.**"* — §8.1 was meant to be revised and never was |
| **The 160 tests** | `conftest.py` puts `opt/d3kos/services/safehelm/` on `sys.path`; **test S1 requires `safehelm/signalk_client.py` to exist and contain `8099`** |

### 2.1 The ruling

**Engine modules land in `opt/d3kos/services/safehelm/` — the §8.1 paths. Unconditionally.**

This is not a compromise, it is the correct reading: **what makes the v0.9.9.6 plugin cheap
is the *purity* of the engine modules, not their directory.** §8.1 already states that
`cpa_engine`, `colregs_classifier` and `alert_gate` are pure functions with no I/O,
*"deliberately: they are the safety-critical parts and they must be unit-testable in
isolation."* A pure module moves into a Node shim's `engine/` directory in v0.9.9.6 by
being copied. No rewrite. The 1,608 lines and 160 guard cases survive either way — which
was the entire point of operator ruling D02-9 ("engine stays Python").

**For the Signal K data path in v0.9.9.5: build `signalk_client.py` (Python WebSocket
consumer on 8099).** Reasons:

1. §8.0 itself says v0.9.9.5 is *"**Build plugin-shaped, do not publish.** Same code,
   running inside d3kOS's own Signal K."* Nothing is published this release.
2. §8.0 correction #2 is explicit: *"**No `d3kOS-alerts/` Node package.** The d3kOS consumer
   is the **existing Flask dashboard**… Adding a Node service means a new runtime, a new
   systemd unit, a new restart policy and a new failure mode, for no gain."* Building the
   Node shim now incurs exactly those costs for zero benefit this release.
3. Test **S1 guards BUG-46** — the 8099-vs-3000 defect, which is real and worth guarding
   whatever the transport. Retiring S1 would drop a guard on a previously-shipped bug.
4. D02-9's *"deletes `signalk_client.py`"* describes the **end state once the plugin is the
   data path** (v0.9.9.6). It is not a v0.9.9.5 deliverable.

So: **plugin-*ready* in v0.9.9.5, plugin-*shaped* in v0.9.9.6.** No test changes. No new
runtime. Every one of the 160 cases stays valid.

> 🔺 **OPERATOR CONFIRMATION REQUESTED.** D02-9 is a recorded **operator** decision, and the
> ruling above interprets its scope rather than following its literal wording. **The engine
> work in §4 is unaffected either way and may proceed now.** Only §5 (the transport layer)
> depends on this. Tier 2: dispatch §4 immediately; hold §5 until the operator confirms.

---

## 3. File placement

`conftest.py` (verified S161) inserts on `sys.path`:

```
deployment/v0.9.9.5/opt/d3kos/services/safehelm     ← every module below
```

Module import names are **exact** — the tests import them by name:
`cpa_engine`, `colregs_classifier`, `alert_gate`, `alert_manager`, `voice_arbiter`,
`standon_escalation`, `safehelm`.

| # | File | Tier | Source (copy verbatim) | Flips |
|---|---|---|---|---|
| 1 | `safehelm/cpa_engine.py` | `[T1]` | §8.5 **lines 1136–1173** | `test_cpa_engine.py` **8** |
| 2 | `safehelm/colregs_classifier.py` | `[T1]` | §8.4 **lines 933–1079** + `VOICE_PHRASES` **1088–1121** | `test_colregs_classifier.py` **38** |
| 3 | `safehelm/alert_gate.py` | `[T1]` | §8.2 **lines 793–818** | `test_alert_gate.py` **14** |
| 4 | `safehelm/alert_manager.py` | `[T1]` | §8.5 **lines 1183–1297** | `test_alert_manager.py` **20** |
| 5 | `safehelm/voice_arbiter.py` | `[T1]` | §8.3 **lines 840–874** | `test_voice_arbiter.py` **8** |
| 6 | `safehelm/standon_escalation.py` | `[T1]` | §8.9 **lines 1457–1501** + `STANDON_PHRASES` **1507–1513** | `test_standon_escalation.py` **14** |
| 7 | `safehelm/safehelm.py` | **mixed** | `advisory_tick` §8.8 **lines 1533–1594** is `[T1]`; Flask scaffolding is `[T3]` | `test_advisory_loop.py` **6** |
| 8 | `safehelm/signalk_client.py` | `[T3]` | §5 below — **gated on §2.1** | S1 |
| 9 | `safehelm/voice_client.py` | `[T3]` | §6 | — |
| 10 | `safehelm/shadow_logger.py` | `[T3]` | §7 | — |
| 11 | `safehelm/static/safehelm-widget.{js,css}` | `[T3]` | §8 | S2 |
| 12 | `etc/systemd/system/d3kos-safehelm.service` | `[T1]` | §8.6 **lines 1634–1653** | U1 |
| 13 | `dashboard/app.py` | `[T3]` **edit** | §9 proxy routes | — |
| 14 | `dashboard/templates/setup.html` | `[T3]` **edit** | §10 HCD-8 | — |

**Total: 108 of the 160 cases flip on this item.** The remaining 52 belong to D17 and D16.

⚠ The `deployment/v0.9.9.5/` tree is created by D17. If D17 has not run, create the
directories with `mkdir -p` — do not escalate about it.

---

## 4. `[T1]` — the engine. Transcribe verbatim.

Copy files 1–7 from the design-doc line ranges in §3, **character-for-character.** Do not
reformat. Do not rename. Do not reorder branches — **in `colregs_classifier.classify()` the
branch order IS the COLREGs precedence** (13(d) lock → Rule 13 → Rule 18 → Rule 14 → Rule
15). Reordering it is a safety defect that the tests may not fully catch.

After copying, verify every invariant. **A failed invariant means you copied it wrong —
re-copy, do not patch.**

### 4.1 `colregs_classifier.py`

| # | Invariant | Guards |
|---|---|---|
| K1 | `HEADON_COURSE_MIN = 165.0` and the head-on test is **`cdiff > HEADON_COURSE_MIN`** | **the v1.0 inversion.** `< 15` fires on parallel courses. C3, C4 |
| K2 | Two **separate** Rule 13 returns: `rule13_being_overtaken` (we stand on) and `rule13_overtaking` (we give way) | **the v1.0 role inversion.** C1, C2 |
| K3 | The 13(d) lock (`prior_rule in RULE13_LOCKED and not is_past_and_clear`) is the **first** test in the function, before any geometry | 13(d) forbids re-reading geometry mid-encounter — a ferry drawing forward of 112.5° must not flip the captain from stand-on to give-way |
| K4 | Rule 18 check sits **after** Rule 13 and **before** Rules 14/15 | Rule 13's preamble excepts 9/10/13; 18 overrides 14/15. C11, C11b, C12 |
| K5 | `tgt_class is None or not in_sight` → `rule15_standon_unconfirmed`, **never** `rule15_standon` | **never assert Stand-On on an unidentified target.** Class B AIS carries no nav status. C13, C13c |
| K6 | Rule 13's stand-on branch is **also** gated on `in_sight` → `rule13_being_overtaken_unconfirmed` | Rule 13 is in Section II, so Rule 11 gates it too (D02-7 option B) |
| K7 | `OVERTAKE_SOG_DEADBAND_KTS = 0.5`, applied **symmetrically** | anti-flap under AIS noise. C9, C9b, C10, C10b |
| K8 | 13(c) biases **only** toward give-way — never manufactures a stand-on claim | 13(c) is "assume you are overtaking"; the dangerous verdict must never be assumed |
| K9 | No `VOICE_PHRASES` value begins an imperative with `Alter`/`Hold`/`Keep`/`Turn`/`Reduce` | **D02-6** — an imperative shifts liability from captain to software. C8 |
| K10 | No phrase asserts water is clear, a target is safe, or no action is needed | ADV-4. C8b, C8c |

### 4.2 `alert_gate.py`

| # | Invariant | Guards |
|---|---|---|
| G-a | `tcpa_s < 0.0` → `None` | **lower-bound defect in the supplied policy** — a target at TCPA −3 min satisfies "≤ 7 min" and would alert. G4 |
| G-b | `inf`/`nan` TCPA → `None` | v1.0's stationary target could never clear. G5 |
| G-c | All three of CPA, TCPA **and** range must hold; highest tier wins | G1–G3, G8 |
| G-d | `voice` is `None` for `advisory`, `'once'` for `warning`, `'repeat'` for `critical` | Tier 1 **never speaks**. G3 |
| G-e | `HEADON_TCPA_BONUS_S = 120.0`, added **only** when `is_headon` | closing speed roughly doubles. G6, G7 |

### 4.3 `alert_manager.py`

| # | Invariant | Guards |
|---|---|---|
| M-a | Degradation measured against **`cpa_at_ack`**, not the previous tick | at 1 Hz the original needed a 20 % drop inside one second, so it effectively never fired. M2 |
| M-b | `CLEAR_HYSTERESIS = 3` ungated ticks before `CLEARED` | M4 |
| M-c | `REPEAT_GAP_S = 60` (Tier 3) vs `ONCE_GAP_S = 120` (Tier 2), selected by `voice_mode` | v1.2 declared `voice` and **never read it** — Critical was no more insistent than Warning. M9–M11 |
| M-d | `_preempt` is **one-shot**, cleared in `mark_spoken()` | a Critical must not monopolise the audio channel. D02-5 |
| M-e | `execute_ui_acknowledgement()` touches **only** this instance | ACK is per-target and must never silence another target. D02-5 |

### 4.4 `voice_arbiter.py`

| # | Invariant | Guards |
|---|---|---|
| A-a | `GLOBAL_MIN_GAP_S = 15.0`, enforced globally | D02-4 |
| A-b | Ordering is `(TIER_RANK, tcpa_s)` — Critical first, then lowest TCPA | A3, A4 |
| A-c | A candidate with `preempt=True` **bypasses** the global gap | D02-5 |

### 4.5 `safehelm.py::advisory_tick` — the glue

| # | Invariant | Guards |
|---|---|---|
| I-a | `mark_spoken()` is called on the arbiter **and on the winning manager only** | **calling it on losers resets their cadence without them having spoken, silencing each for a full gap — a bug that looks like "quiet system", not an error.** I1 |
| I-b | `prior_rule` is threaded from `managers[mmsi].rule_id` into `classify()` | the 13(d) lock lives in `managers`; the classifier stays pure |
| I-c | `shadow_logger.record(...)` is called for **every** target, including non-qualifying | §8.2 — suppressed classifications are still logged |
| I-d | A target with `tier is None` or `rule == 'no_situation'` and no existing manager is skipped, never given one | I5 |

---

## 5. `[T3]` — `signalk_client.py` ⚠ GATED on §2.1

**Hold until the operator confirms the §2.1 ruling.**

- WebSocket to `ws://<host>:8099/signalk/v1/stream`.
- ⛔ **Port 8099. NEVER 3000.** `app.py` carries the comment *"CRITICAL: Signal K WebSocket is
  ws://localhost:8099 — NOT ws://localhost:3000"*, tagged **BUG-46**. 3000 is the
  **dashboard**. Guarded by **S1**, which greps for any `:3000` Signal K URL.
- Host from config, not hardcoded. Reconnect with **exponential backoff** — the unit
  deliberately does **not** list Signal K in `After=` because its unit name is unverified
  (§11 open item).
- Reads: own `navigation.position/courseOverGroundTrue/speedOverGround`; per target the same
  plus `design.aisShipType` and `navigation.state`.
- **Normalise `aisShipType` / `navigation.state` against ITU-R M.1371** into the
  `RULE18_OUTRANKS_US` vocabulary: `not-under-command`, `restricted-manoeuverability`,
  `engaged-in-fishing`, `sailing`. **Anything unrecognised → `None`, never a guess.** `None`
  must never be treated as "power-driven" — K5 depends on this.

🔺 **ESCALATE-IF** the ITU-R enumeration values are not documented in the repo →
**CLARIFICATION**. §8.4 says *"map the raw AIS enumerations against ITU-R M.1371 at
implementation time"* and deliberately does **not** assert the numbers. **Do not invent
them.**

---

## 6. `[T3]` — `voice_client.py`

Thin wrapper. **`ai_bridge` already exists and works** — a Python service on **3002** with
`speak_urgent`, espeak-ng, the mute file and the speaking file. §8.0 correction #1:
**call it, do not reimplement it.**

```
POST http://127.0.0.1:3002/webhook/alert
```

- Short timeout, and a failure must **never** raise into `advisory_tick`.
- **ADV-2:** on service start speak once — *"SafeHelm advisory active. AIS targets only. Not
  a substitute for lookout."*

---

## 7. `[T3]` — `shadow_logger.py`

Appends one record per target per tick: timestamp, MMSI, CPA, TCPA, range, rule, tier
(including `None`). This is a **diagnostic log, not Shadow Mode** — D02-1 rules Shadow Mode
explicitly out of scope, and SH-11 is SUPERSEDED (§2.1).

Rotate or cap the file. At 1 Hz with 30 targets this is ~2.6 M records/day — an uncapped log
is the 2.6 GB BUG-105 lesson in a different costume.

---

## 8. `[T3]` — widget, including gate item 6c

Copy the layout from §8.7 **lines 1681–1694**.

### 8.1 Gate item 6c — explainability. **Required, not polish.**

§12.3 6c: the widget **SHALL** show the inputs behind the verdict, not just the verdict:

```
Rule 13 — you are STAND-ON
  target bearing 160° (abaft your beam)
  target SOG 12.0 kt vs yours 10.0 kt (+2.0)
```

> *"A captain who can see why in one glance can overrule it. A captain shown only 'You are
> Stand-On' cannot."* This is the **strongest mitigation available** for a classifier that is
> regulation-traced but not domain-endorsed — it makes a wrong call catchable at the helm.

### 8.2 Hard requirements

| # | Requirement |
|---|---|
| W1 | **ADV-1 footer visible at all times the widget is visible:** *"Advisory only — AIS targets only. Captain remains responsible for lookout and navigation."* |
| W2 | Same-origin only — the browser talks to the **dashboard on :3000**, which proxies to 8095. v1.0 served the widget from :3000 and subscribed to SSE on :8095 — **cross-origin; the browser would have blocked it**, and v1.0 never mentioned CORS. |
| W3 | **No hardcoded `localhost`** (BUG-48, guarded by **S2** and `bug48-no-hardcoded-localhost.spec.ts`) |
| W4 | **AODA:** ≥18px on **every** element including MMSI, units and the ADV-1 footer; header and CPA/TCPA ≥22px; ACK and DISMISS ≥48×48px with ≥8px separation. The widget ends up ~320px tall on the 7″ touchscreen — **that is the correct outcome, not a reason to shrink text.** |
| W5 | The 2 Hz flash is **`border-color` only** — no opacity, no transform, and **never applied to text** (seizure risk and legibility) |

---

## 9. `[T3]` — dashboard proxy routes

| Browser calls (:3000) | Proxies to |
|---|---|
| `GET /api/safehelm/events` (SSE) | `http://127.0.0.1:8095/widget/events` |
| `POST /api/safehelm/alert/<mmsi>/ack` | `http://127.0.0.1:8095/alert/<mmsi>/ack` |
| `POST /api/safehelm/alert/<mmsi>/dismiss` | `http://127.0.0.1:8095/alert/<mmsi>/dismiss` |

- `<mmsi>` validated as **exactly 9 digits** before proxying; anything else **400**.
- SafeHelm binds **`127.0.0.1:8095`**. v1.0 left the bind unspecified, which meant **anyone on
  the boat Wi-Fi could silence a collision alarm.** Closed by the loopback bind plus the
  dashboard's existing session auth. Guarded by **U2**.

---

## 10. `[T3]` — HCD-8 wizard questions (decision D02-8)

Two questions in `setup.html`. These close the §14 **Rule 9** and **Rule 12** gaps properly
rather than by disclaimer — they are *"two questions nobody has ever asked the operator."*

| Field | Options | Why |
|---|---|---|
| **Propulsion** | power-driven / sailing | Rule 12 (two sailing vessels) and own-vessel Rule 18 standing |
| **Length class** | under 12 m / 12–20 m / over 20 m | **three bands because 12 m is its own threshold in Rules 25 and 35**; Rule 9 matters because the reference vessel is under 20 m and Rule 13's preamble excepts Rule 9 |

⛔ **No defaults and no skip** (D02-8). A guessed own-vessel type produces wrong advice
silently. Persist to `config/vessel.env` alongside the existing wizard gate.

---

## 11. `[T3]` — engine liveness, E9/E10. **A dead engine must be loud.**

> §13.1 tells the captain that silence means no qualifying target. **Silence caused by a
> crash is therefore indistinguishable from silence caused by clear water — the worst
> failure this system can have.**

| # | Requirement | Guards |
|---|---|---|
| E9 | The engine exposes a **liveness signal** (heartbeat) the consumer polls | E9 |
| E10 | On engine failure, d3kOS speaks *"SafeHelm engine stopped. Collision advisory is not running."* and the widget shows it | E10 |
| — | Restart is **bounded** — `Restart=on-failure` + `StartLimitBurst=5`. **Never unbounded** (BUG-105) | U1 |

### 11.1 SH-15 / phase flag

Copy §8.6 **lines 1604–1626**. `SAFEHELM_PHASE=1`. Phase 2 code does not execute, so the
SH-15 whitelist is never required.

⛔ **No compile-time bypass. No stub returning `true`.** §3 of the design doc rejects
`verify_signalk_whitelist() { return true; }` outright — *"a safety whitelist check that
returns true when unconfigured is fail-open — the exact defect class as BUG-91."*

⛔ On an SH-15 violation: **log `critical` and stay in Advisory Mode.** Do **not**
`raise SystemExit`. v1.0 paired a hard exit with `Restart=always` — a config error became a
permanent restart loop. The boat keeps its collision advisory instead of losing the service.

`Environment=PYTHONUNBUFFERED=1` is **required** for any Python systemd service using
`print()` (BUG-54).

---

## 12. Definition of done

```bash
cd /home/boatiq/Helm-OS && ./tests/run-all.sh
```

| Suite | Before | After |
|---|---|---|
| `test_cpa_engine.py` | 8 red | **8 green** |
| `test_colregs_classifier.py` | 38 red | **38 green** |
| `test_alert_gate.py` | 14 red | **14 green** |
| `test_alert_manager.py` | 20 red | **20 green** |
| `test_voice_arbiter.py` | 8 red | **8 green** |
| `test_standon_escalation.py` | 14 red | **14 green** |
| `test_advisory_loop.py` | 6 red | **6 green** |
| `test_v0995_config_guards.py` | — | **D02 subset (S1, S2, U1, U2) green** |

**`errors` must be 0.** Plus, as real pasted output:

```bash
# every module imports standalone (purity check)
cd deployment/v0.9.9.5/opt/d3kos/services/safehelm
for m in cpa_engine colregs_classifier alert_gate alert_manager voice_arbiter standon_escalation; do
  python3 -c "import $m; print('$m OK')"
done

# the engine modules must have NO I/O imports
grep -nE "^(import|from) +(requests|socket|websocket|flask|urllib|http)" \
  cpa_engine.py colregs_classifier.py alert_gate.py standon_escalation.py   # expect NO match

# no Signal K URL on the dashboard port (BUG-46)
grep -rnE "(ws|http)s?://[^\"']*:3000" . | grep -iE "signalk|stream"        # expect NO match

# no all-interface bind
grep -rn "0\.0\.0\.0" . ../../../../etc/systemd/system/d3kos-safehelm.service  # expect NO match

# no imperative voice phrase (D02-6)
grep -nE "'(Alter|Hold|Keep|Turn|Reduce)" colregs_classifier.py             # expect NO match
```

---

## 13. HARD CONSTRAINTS

- **Never edit a `[T1]` block.** Transcribe it. If it looks wrong, escalate.
- **Never reorder the branches in `classify()`.** Branch order is COLREGs precedence.
- **Never edit any file under `tests/`.** 108 of the 160 cases are your contract.
- **Port 8099 for Signal K. Port 3002 for voice. Port 8095 for SafeHelm, bound `127.0.0.1`.**
  Never 3000 for Signal K (BUG-46).
- **No `0.0.0.0` bind.** Anyone on the boat Wi-Fi could silence a collision alarm.
- **No `raise SystemExit`** on an SH-15 violation. Log `critical`, stay in Advisory Mode.
- **No `Restart=always`** without `StartLimitBurst`.
- **No hardcoded `localhost`** in browser-delivered files.
- **No imperative voice phrase.** No phrase claiming water is clear or a target is safe.
- **Never assert Stand-On on an unconfirmed target.**
- **No Shadow Mode.** D02-1. `shadow_logger` is a log.
- **No Signal K write path, no autopilot, no steering output.** §1, §5.6.
- **No text below 18px. No touch target below 48×48px.**
- Do not build the Node plugin shim (v0.9.9.6). Do not `npm publish`.
- Do not touch the Pi. Do not commit. Do not `git push`.

---

## 14. ESCALATE-IF (§25.6)

| Condition | Type |
|---|---|
| The §2.1 layout ruling has **not** been operator-confirmed and you are about to start §5 | **BLOCKED — CLARIFICATION** |
| A design-doc line range in §3 is not the Python block named | **CLARIFICATION** — wrong range |
| Any invariant in §4.1–§4.5 cannot be satisfied by verbatim copy | **SOLUTION-REQUEST** |
| A `[T1]` block looks logically wrong to you | **SOLUTION-REQUEST → Tier 1.** Never edit it. |
| ITU-R M.1371 enumeration values for `aisShipType` / `navigation.state` are not in the repo | **CLARIFICATION** — never invent them |
| Signal K systemd unit name needed | **CLARIFICATION** — read it off the Pi, never guess |
| `ai_bridge` `/webhook/alert` payload shape is unclear | **CLARIFICATION** |
| A test still fails after verbatim transcription and you believe the **test** is wrong | **SOLUTION-REQUEST** |
| You are tempted to reorder `classify()` branches for readability | **STOP** — that is a safety defect |

**Forced stop (§25.5):** Confidence below 75 → escalation block instead of code. On this
item specifically: **if you find yourself reasoning about what COLREGs requires, stop and
escalate.** That reasoning is not your task.

---

## 15. Pre-flight self-check

1. Which file am I writing, and is it `[T1]` (transcribe) or `[T3]` (author)?
2. Which named test cases flip green, and have I run the suite **before** starting?
3. What am I forbidden to touch? (`tests/`, `[T1]` internals, branch order, the Pi)
4. Am I about to reason about COLREGs? (If yes — **stop.**)

---

## 16. Return this

1. `git status --short`, `git diff --stat` — **zero files under `tests/`**.
2. Full `git diff` for `colregs_classifier.py` and `safehelm.py`.
3. `./tests/run-all.sh` before **and** after. 108 cases must flip; `errors` must be 0.
4. Every §12 command output, real, pasted.
5. **Decision Log** — every deviation, or `none`.

---

## 17. What Tier 2 checks when it comes back

Verify these **by reading the code**, not by trusting a green suite. The tests are good but
they were written against this design, and a subtly wrong transcription can satisfy an
assertion while being wrong.

1. **`cdiff > 165`, not `< 15`.** Read the head-on branch literally. This is the v1.0
   inversion and it would voice *"head-on"* at two boats cruising side by side. **Highest
   severity check in the release.**
2. **Rule 13 returns two distinct values** and `rule13_being_overtaken` maps to a
   **stand-on** phrase. Read the phrase text, not just the constant name.
3. **Branch order:** 13(d) lock → Rule 13 → Rule 18 → Rule 14 → Rule 15. A "tidied" order
   passes many tests and breaks precedence.
4. **`mark_spoken()` on the winner only.** Grep `advisory_tick` for every call site. Called
   on losers, the system goes quiet in a way that looks like calm water.
5. **`tgt_class is None` cannot reach `rule15_standon`.** Trace it by hand.
6. **No `0.0.0.0`, no `:3000` Signal K URL, no `Restart=always`, no `SystemExit`.**
7. **`tests/` diff empty**, and a **before** run was actually pasted.

Then, and only then, the Playwright phase (Tier-1 authored) — §10.5's D02 gates: Tier 2
speaks once, Tier 1 is silent, ACK goes amber and re-fires at 120 s while other targets stay
queued, the ADV-1 footer is always visible, and a 30-target simulation respects both caps.
**`curl` is not verification.**

---

## 18. Tier 3 Dispatch Prompt

⚠ **Tier 2: dispatch §4 (the engine) now. HOLD §5 until the operator confirms the §2.1
ruling.** Everything else is unblocked.

---

TASK TYPE: [IMPLEMENT] — Tier 3

You are the Tier 3 implementer on d3kOS v0.9.9.5, item D02 — **SafeHelm, the most
safety-critical component in this project.** Tier 1 (Opus 5) wrote your spec and will verify
your work under AAO §25.8.

READ THIS FILE FIRST, IN FULL, BEFORE TOUCHING ANYTHING:
`deployment/docs/atomic-specs/V09995-D02-SAFEHELM.md`

WORKING DIRECTORY: `/home/boatiq/Helm-OS`

**THE MOST IMPORTANT INSTRUCTION IN THIS SPEC:** every algorithm in §4 is `[T1]`-authored.
**You transcribe it character-for-character from the line ranges in §3. You do not reason
about COLREGs. You do not reorder branches — the branch order IS the legal precedence. You
do not "improve" anything.**

A previous capable model wrote this logic and got two rules **backwards**: it would have
announced *"Danger. Head-on situation."* to two boats cruising **side by side**, and told a
captain *"You do not have right-of-way"* while they were legally obliged to **hold course**.
That is why this partition exists. It is not about your ability — it is that this logic has
already fooled a careful reader once.

YOUR TASK — D02. Files 1–7 and 9–14 in §3. **NOT file 8 (`signalk_client.py`) until Tier 2
tells you the operator has confirmed §2.1.**

Not D17, not D05, not D16. No Node plugin shim. No Shadow Mode. No Signal K write path.

USE GRAFT, DO NOT GREP:
```
graft ask "ai_bridge webhook alert speak_urgent" --source
graft grep "8099"
graft skeleton deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py
```

MANDATORY SEQUENCE — PASTE REAL OUTPUT
1. `./tests/run-all.sh` **before writing anything.** Paste it. Baseline **160 failed,
   0 errors**.
2. Transcribe the `[T1]` files (§3 rows 1–7) from the given line ranges. Then verify **every**
   invariant in §4.1–§4.5 and state each one pass/fail in your Decision Log.
3. Author the `[T3]` files (§6–§11).
4. `./tests/run-all.sh` again. Paste it. **108 cases must flip green. `errors` must be 0.**
5. Run every command in §12. Paste real output for each.

Do not write code first and run the suite once. **No pasted before-run means rejection.**

THE FIVE THINGS THAT WILL GET YOUR WORK REJECTED
1. **Editing a `[T1]` block** — including reformatting or reordering branches.
2. **Editing anything under `tests/`.** 108 cases are your contract.
3. **A Signal K URL on port 3000.** 3000 is the dashboard. Signal K is **8099** (BUG-46).
4. **A `0.0.0.0` bind** — it lets any guest on the boat Wi-Fi silence a collision alarm.
5. **An imperative voice phrase** (`Alter`, `Hold`, `Keep`, `Turn`, `Reduce`) — D02-6: an
   imperative shifts liability from the captain to the software.

IF YOU ARE UNSURE ABOUT ANYTHING
Emit the §25.4 escalation block and stop:

```
🔺 ESCALATION — D02/<task>
Tier asking     : Haiku / Tier 3
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

**Never invent an ITU-R M.1371 enumeration value. Never guess a port or a unit name. If you
are reasoning about what COLREGs requires — stop and escalate.**

WHEN DONE, RETURN the five items in §16.

---

*Authored by Claude Opus 5 (Tier 1), S161 2026-09-12. §2.1 is a Tier-1 architectural ruling
awaiting operator confirmation; the engine work is unaffected by it.*
