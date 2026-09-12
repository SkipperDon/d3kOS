# D17 — Hardware Capability Detection · Atomic Spec

**Document:** V09995-D17-001 · **Version:** 1.0 · **Date:** 2026-09-12 (S161)
**Author:** Claude Opus 5 (Tier 1) · **Implementer:** Tier 3 (Haiku) · **Orchestrator:** Tier 2 (Sonnet)
**Source of truth:** `deployment/docs/V09995_SOLUTION_DESIGN.md` §5, §9
**Requirements:** `deployment/docs/HARDWARE_CAPABILITY_DETECTION_REQUIREMENTS.md` (HCD-REQ-001 v1.0 — **63 requirements, not 97**)

---

## 1. Why this is first

D17 has no dependencies. It is also the foundation for the other three items: D16 and D02
both gate features on `feature_available()`, so the gate must exist and **fail closed**
before anything relies on it.

One v1.0 defect in this item is the reason the whole design was re-reviewed:

> `ram_gb=$(( ram_kb / 1048576 ))` **truncates.** `MemTotal` excludes reserved memory, so a
> 4 GB Pi reports ≈3 882 000 kB → `3`, and an 8 GB Pi → `7`. A manifest entry
> `ram_gb_min: 8` could **never** be satisfied on 8 GB hardware. The fix is to work in
> **MB** throughout and never gate on the rounded GB value.

---

## 2. Scope

| Task | Deliverable | Tier |
|---|---|---|
| **HCD-1** | `hardware-probe.sh` + service unit + timer unit | `[T1]` code, `[T3]` placement |
| **HCD-2** | udev rule + `notify-hardware-change.sh` | `[T1]` code, `[T3]` placement |
| **HCD-3** | `d3kos_feature_gate.py` + `capabilities-manifest.json` | `[T1]` code, `[T3]` manifest |
| **HCD-4** | `/hardware` route + `hardware.html` | `[T3]` |
| **HCD-5** | `setup.html` final wizard screen | `[T3]` |
| **HCD-6** | Gated services watch the profile (REQ-HCD-032) | `[T3]` |
| **HCD-7** | Probe-failure fallback profile (REQ-HCD-097) | `[T3]` |

**HCD-8** (wizard questions for propulsion + length class, decision D02-8) is **NOT in this
spec.** It closes COLREGs Rules 9 and 12 for D02 and is specified in
`V09995-D02-SAFEHELM.md`. Do not build it here.

---

## 3. Exact file placement — this is a contract, not a suggestion

The guard tests resolve modules by path. `tests/conftest.py` inserts these on `sys.path`:

```
deployment/v0.9.9.5/opt/d3kos/services/safehelm     ← D02 modules
deployment/v0.9.9.5/opt/d3kos/services              ← d3kos_feature_gate.py lives HERE
```

and `require_file()` resolves every config path relative to `deployment/v0.9.9.5/`.

| # | File | Op | Source (copy verbatim) |
|---|---|---|---|
| 1 | `deployment/v0.9.9.5/opt/d3kos/scripts/hardware-probe.sh` | create, `chmod +x` | design §5 HCD-1, **lines 171–257** |
| 2 | `deployment/v0.9.9.5/etc/systemd/system/d3kos-hardware-probe.service` | create | design §5, **lines 268–284** |
| 3 | `deployment/v0.9.9.5/etc/systemd/system/d3kos-hardware-probe.timer` | create | design §5, **lines 286–298** |
| 4 | `deployment/v0.9.9.5/etc/udev/rules.d/99-d3kos-accelerator.rules` | create | design §5 HCD-2, **lines 311–319** |
| 5 | `deployment/v0.9.9.5/opt/d3kos/scripts/notify-hardware-change.sh` | create, `chmod +x` | design §5, **lines 325–330** |
| 6 | `deployment/v0.9.9.5/opt/d3kos/services/d3kos_feature_gate.py` | create | design §5 HCD-3, **lines 346–447** |
| 7 | `deployment/v0.9.9.5/opt/d3kos/config/capabilities-manifest.json` | create | §5 — you author, per §5.2 below |
| 8 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/templates/hardware.html` | create | §6 below |
| 9 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/app.py` | **edit** | add routes, §6 |
| 10 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/templates/setup.html` | **edit** | §7 below |

⛔ **`hardware-profile.json` is NOT in the deployed tree.** REQ-HCD-096: it is *operator
data*, and an update that rsyncs `config/` would overwrite it. The probe creates it; HCD-7's
fallback covers first boot. **Do not create it, do not ship a default copy.**

### 3.1 The `deployment/v0.9.9.5/` tree does not exist yet — you create it

Verified S161: **the directory is absent.** That is expected and is exactly why all 160
guard tests currently fail with `NOT YET IMPLEMENTED` — `conftest.py` puts paths under it on
`sys.path` and they resolve to nothing.

**You are the first task in this release.** Create the directory structure as you go
(`mkdir -p`). Do **not** escalate about the tree being missing, and do **not** copy or move
the `deployment/v0.9.9.4/` tree wholesale — create only the ten paths in §3.

Two files in §3 are marked **edit** (`app.py`, `setup.html`). Since the v0.9.9.5 tree is
empty, they do not exist there yet either. **Copy each from its v0.9.9.4 counterpart first,
then edit the copy:**

```bash
V4=deployment/v0.9.9.4/opt/d3kos/services/dashboard
V5=deployment/v0.9.9.5/opt/d3kos/services/dashboard
mkdir -p "$V5/templates"
cp "$V4/app.py"             "$V5/app.py"
cp "$V4/templates/setup.html" "$V5/templates/setup.html"
```

🔺 **ESCALATE-IF** either v0.9.9.4 source file is absent → **CLARIFICATION**.

---

## 4. `[T1]` — HCD-1, HCD-2, HCD-3 code

Copy from the design doc line ranges in §3 **character-for-character.** Do not reformat, do
not rename variables, do not "tidy" the `jq` invocation. After copying, verify each
invariant below. If any fails, you copied it wrong — re-copy, do not patch.

### 4.1 `hardware-probe.sh` invariants

| # | Invariant | Why |
|---|---|---|
| A1 | `ram_mb=$(( ram_kb / 1024 ))` is present | the truncation defect |
| A2 | `ram_gb_nominal` is commented **DISPLAY ONLY** and is never compared in a gate | ditto |
| A3 | JSON is built with a single `jq -n` call using `--arg`/`--argjson` | v1.0 interpolated `$pi_model` unescaped; one quote in a model string produced invalid JSON and failed every gate closed |
| A4 | `mv "$TMP" "$PROFILE"` — atomic rename, never `>` onto the live file | the gate's mtime reload depends on it |
| A5 | `probe_version` reads the current value and increments on **every** write | decision D17-1 |
| A6 | `content_hash` is computed with `probe_version` and `probed_at` deleted | D17-1 — consumers detect *payload* change |
| A7 | `dt()` strips NULs (`tr -d '\0'`) | device-tree strings are NUL-terminated |
| A8 | `chmod 644 "$PROFILE"` after the move | dashboard runs as a different user |

### 4.2 Unit invariants — BUG-105 is the reason these exist

| # | Invariant |
|---|---|
| B1 | `.service` is `Type=oneshot` with **`RemainAfterExit=no`** — v1.0 used `yes`, which stops the timer re-triggering the unit |
| B2 | `.service` has `Before=d3kos-dashboard.service` |
| B3 | `.timer` has `OnBootSec=5min`, `OnUnitActiveSec=15min` (REQ-HCD-027 — **absent from v1.0**) |
| B4 | Neither unit contains `Restart=always` |

> **BUG-105 context:** a `Restart=always` unit paired with a hard exit produced ~40
> restarts/sec for eight days and a 2.6 GB log. `test_v0995_config_guards.py::U1` greps for
> this pattern. It will fail your work if you reintroduce it.

### 4.3 udev invariants

| # | Invariant | Why |
|---|---|---|
| C1 | The rule's `RUN+=` calls **`systemd-run --no-block`** and nothing else | v1.0 ran `lsusb`, a PCI walk and an HTTP POST *inside the udev worker*. udev kills slow `RUN` processes and a blocked worker stalls **all** device events. |
| C2 | No `lsusb`, no `curl`, no lockfile inside the rule | ditto |
| C3 | `flock` serialisation lives in `notify-hardware-change.sh`, outside udev | blocking is safe there |
| C4 | Matches `ATTR{idVendor}=="18d1"`, `ATTR{idProduct}=="9302|9303"`, `ACTION=="add|remove"` | Coral USB + Coral USB Mini |

### 4.4 `d3kos_feature_gate.py` invariants — the fail-open defect

| # | Invariant | Why |
|---|---|---|
| D1 | `_accel_ok()` is a **standalone function**, and the whitelist check runs **even when an accelerator is present** | **v1.0's whitelist sat inside `if req.get('accelerator_any') and not accel['present']:` — so the whole block was skipped whenever an accelerator *was* fitted, and a Coral USB satisfied a Hailo-only feature. Same shape as BUG-91.** Guarded by `F1`. |
| D2 | `feature_available()` returns **`False`** on `FeatureGateUnavailable` | fails **closed**. Guarded by `F7`. |
| D3 | `_load()` compares `os.stat(...).st_mtime_ns` and reloads only on change | REQ-HCD-065 stated deviation — an in-process counter cannot work across the dashboard / SafeHelm / marine-vision processes. Guarded by `F8`. |
| D4 | Gates compare `plat['ram_mb']` against `req['ram_mb_min']` — **never** `ram_gb` | the truncation defect. Guarded by `F5`, `F6`. |
| D5 | `feature_reason()` and `feature_upgrade_path()` never raise | the Hardware page renders them directly |

---

## 5. `[T3]` — `capabilities-manifest.json`

You author this file. Shape:

```json
{
  "features": {
    "<feature_key>": {
      "label": "<plain-language name shown on the Hardware page>",
      "requires": {
        "pi_gen_min": 4,
        "ram_mb_min": 3500,
        "accelerator_any": false,
        "accelerator_class_any": ["hailo-8l", "coral-usb"]
      },
      "operator_override": false
    }
  }
}
```

### 5.1 Contract

- `ram_mb_min` — **MB, never GB.** A "4 GB Pi" requirement is written **`3500`**, below the
  ≈3790 MB a 4 GB board actually reports. An 8 GB requirement is **`7500`**.
- `accelerator_any: false` → `_accel_ok()` returns `True` regardless. Omit
  `accelerator_class_any` when `accelerator_any` is false.
- `accelerator_class_any` present → whitelist is **enforced**. Valid values are exactly the
  classes `hardware-probe.sh` can emit: `hailo-8l`, `hailo-8`, `coral-usb`,
  `coral-usb-mini`.
- `operator_override: true` → gate returns available with no checks. Default `false`.

### 5.2 Required entries

Seed **only** these. Do not invent features.

| Key | Requirement | Rationale |
|---|---|---|
| `ollama_local` | `pi_gen_min: 5`, `ram_mb_min: 7500`, `accelerator_any: true`, `accelerator_class_any: ["hailo-8l", "coral-usb"]` | operator decision S157 — Ollama gates on Pi 5 **plus** an accelerator |
| `marine_vision` | `pi_gen_min: 4`, `ram_mb_min: 3500`, `accelerator_any: false` | runs today on the 4B |
| `surround_view_3d` | `pi_gen_min: 4`, `ram_mb_min: 3500`, `accelerator_any: false` | D16 Phase 1; the real constraint is the §7.2 CPU gate, not hardware class |

🔺 **ESCALATE-IF** you believe a fourth feature key is needed → **CLARIFICATION**. Do not add
one on your own judgment.

---

## 6. `[T3]` — HCD-4 Hardware page

### 6.1 Routes in `app.py`

Copy the route bodies from design §5 HCD-4, **lines 454–479**. Three requirements the
snippet does not state:

1. `POST /api/hardware/profile-updated` **binds loopback only** — reject any request whose
   `request.remote_addr` is not `127.0.0.1` with **403**. The notifier is local; an open
   endpoint lets anyone on the boat Wi-Fi trigger dashboard churn.
2. `POST /api/hardware/reprobe` runs `systemctl start d3kos-hardware-probe.service`. Same
   loopback restriction. Use `subprocess.run` with a **list**, never `shell=True`.
3. `ADVISORY_BLIND_SPOTS` (ADV-3) is the blind-spot list from design §1, **verbatim**, passed
   to the template. Define it as a module-level list in `app.py`.

### 6.2 `hardware.html`

Renders, for each manifest feature: the label, enabled/locked state, `feature_reason(key)`,
and `feature_upgrade_path(key)`. Plus the platform block (`pi_model`, `ram_gb_nominal` for
display), HAT block, accelerator block, and the ADV-3 blind-spot list.

When `error` is set (profile unreadable) the page shows the error and the instruction
**"Run d3kos-probe"** — it must not render a blank page or a stack trace.

### 6.3 AODA — hard requirement, and v1.0 specified no sizes at all

| Element | Minimum |
|---|---|
| **All** text — including the MMSI-style monospace, units, captions | **18px** |
| Section headings | 22px |
| Enable / Re-probe / toast-dismiss controls | **48×48px** |

`test_v0995_config_guards.py` includes a `hardware.html` content guard.

⚠ **Playwright is deferred (operator decision S161), so nothing measures the rendered
result.** A content guard confirms a string is in the template; it cannot confirm what the
browser draws. Reading CSS tokens instead of computed style is exactly how S115 produced a
false pass. Therefore:

- Use **explicit `px`** for every size. Do **not** use `rem`/`em`/`%` for text, where the
  resolved value depends on a root font-size you cannot see from the template.
- When you report this task, write **"pytest green, computed style not measured."** Do not
  write "AODA verified" — you have not verified it, and Tier 1 needs that distinction to
  decide whether a Playwright spec is required here.

---

## 7. `[T3]` — HCD-5 Wizard final screen

Add a final step to `setup.html`, titled **"Your d3kOS Hardware Profile"**, before Finish:

- the same Setup Description rendering as `/hardware`
- the ADV-3 blind-spot list
- an inline **Re-probe** button calling `POST /api/hardware/reprobe`, then re-rendering **in
  place** — the operator must be able to fit hardware without restarting the wizard

Do **not** alter the existing wizard gate (`config/vessel.env`) or any earlier step.

---

## 8. `[T3]` — HCD-6 and HCD-7: the two gaps §9 found

### HCD-7 — probe failure must still leave a valid profile (REQ-HCD-097)

> *"A probe failure SHALL produce a valid `hardware-profile.json` with all unknown fields set
> to safe defaults — it SHALL NOT leave the profile file absent."*

`hardware-probe.sh` uses `trap 'rm -f "$TMP"' EXIT`, so a `jq` failure removes the temp and
leaves the previous profile — or on first boot, **none at all**.

Add a fallback: if the `jq -n` pipeline fails **and** `$PROFILE` does not already exist,
write a minimal valid profile:

```json
{
  "probe_version": 1,
  "probed_at": "<ISO8601 Z>",
  "probe_failed": true,
  "platform":    { "pi_model": "unknown", "pi_gen": 0, "ram_mb": 0, "ram_gb_nominal": 0 },
  "hat":         { "present": false, "product": "", "vendor": "", "product_id": "", "product_ver": "", "hat_class": "" },
  "accelerator": { "present": false, "accelerator_class": [], "devices": [] }
}
```

Every value is chosen so the gate denies everything. The gate failing closed is the correct
second line of defence — but the profile must never be **absent**.

Add `probe_failed: true` to the schema. `hardware.html` shows a warning banner when it is
true.

### HCD-6 — gated services must watch the profile (REQ-HCD-032)

> *"Each d3kOS systemd service that is feature-gated SHALL watch `hardware-profile.json` for
> changes and re-evaluate its enabled state on change."*

Currently only the **dashboard** gets a webhook; gated services never watch the file — so a
service keeps running after its accelerator is unplugged. Interacts with REQ-HCD-034
(graceful stop on removal).

Because `_load()` already does an `os.stat()` mtime check, "or equivalent" is satisfied by a
service **re-calling `feature_available()` on its own existing loop**. Implement as a small
helper in `d3kos_feature_gate.py`:

```python
def watch(key, on_change, interval_s=30):
    """Call on_change(available: bool) whenever the gated state of `key` changes."""
```

No new thread inside the gate module, no `inotify` dependency: the helper is a generator or
a callback the *caller's* loop drives. A gated service that must stop calls its own shutdown
path — the gate never kills anything itself.

🔺 **ESCALATE-IF** no existing service has a loop you can hook → **ADVICE**. Do not create a
new systemd unit to do the watching.

---

## 9. Definition of done

```bash
cd /home/boatiq/Helm-OS
./tests/run-all.sh          # THE only trusted runner
```

| Suite | Before | After | Note |
|---|---|---|---|
| `test_feature_gate.py` | 16 red | **16 green** | all of F1–F8 |
| `test_v0995_config_guards.py` | 36 red | **D17 subset green** | udev rule, timer, `hardware.html`. D16 + D02 rows **stay red** — that is correct. |
| every other suite | red | **unchanged red** | D02/D16 modules do not exist yet |

**`errors` must be 0.** §12.1 condition 2 requires assertion failures, never import errors.

Plus, pasted as **real terminal output**:

```bash
# 1. probe produces valid JSON and correct RAM
bash deployment/v0.9.9.5/opt/d3kos/scripts/hardware-probe.sh   # note: writes /opt/... — run on Pi, or override PROFILE
jq . /opt/d3kos/config/hardware-profile.json                   # must exit 0
awk '/^MemTotal:/{print int($2/1024)}' /proc/meminfo           # must equal .platform.ram_mb

# 2. shell syntax
bash -n deployment/v0.9.9.5/opt/d3kos/scripts/hardware-probe.sh
bash -n deployment/v0.9.9.5/opt/d3kos/scripts/notify-hardware-change.sh

# 3. no restart-storm pattern
grep -rn "Restart=always" deployment/v0.9.9.5/etc/systemd/system/   # expect NO match

# 4. no 0.0.0.0 bind
grep -rn "0\.0\.0\.0" deployment/v0.9.9.5/ | grep -v node_modules   # expect NO match
```

---

## 10. HARD CONSTRAINTS

- Edit **only** the ten files in §3. Nothing else.
- **Never** write to `deployment/v0.9.4/pi_source/` or `d3kOS/dashboard/` — SUPERSEDED,
  read-only.
- **Do not create `hardware-profile.json`** in the deployed tree (REQ-HCD-096).
- **Do not edit any file under `tests/`.** The 160 guards are the contract. Editing a test
  to go green is an automatic rejection.
- No `Restart=always` without `StartLimitBurst`. No `0.0.0.0` bind anywhere.
- No `shell=True` in any `subprocess` call.
- No text below **18px**. No touch target below **48×48px**.
- Do **not** touch the Pi: no `ssh`, no `scp`, no `systemctl` against `192.168.1.237`.
  Tier 1 deploys.
- Do **not** commit. Do **not** `git push`. Do **not** regenerate `MANIFEST.md5`.
- Do not build HCD-8. It is in the D02 spec.

---

## 11. ESCALATE-IF (§25.6 — concrete triggers, not self-assessment)

| Condition | Type |
|---|---|
| Design doc lines 171–257 are not a bash script starting `#!/usr/bin/env bash` | **CLARIFICATION** — you are reading the wrong range |
| A file in §3 marked **edit** does not exist | **CLARIFICATION** |
| `app.py` has no obvious place to add a route, or already defines `/hardware` | **CLARIFICATION** |
| `setup.html` structure makes "a final step before Finish" ambiguous | **ADVICE** |
| A `test_feature_gate.py` case still fails after HCD-3 and you believe the **test** is wrong | **SOLUTION-REQUEST** — never edit the test |
| No existing service loop to hook HCD-6 into | **ADVICE** |
| You think a manifest feature key beyond the three in §5.2 is needed | **CLARIFICATION** |
| Any invariant in §4.1–§4.4 cannot be satisfied by verbatim copy | **SOLUTION-REQUEST** |

**Forced stop (§25.5):** before writing each file, compute your Confidence Score. If it is
**below 75**, emit the escalation block instead of code. Asking is free; a silent wrong
assumption is a UAC event.

---

## 12. Pre-flight self-check (§25.7.1(4))

Answer these from **this spec alone** before writing anything. If you cannot answer one,
escalate.

1. Which exact file am I creating or editing, and does it already exist?
2. What proves it is done — which named test cases flip green?
3. What am I forbidden to touch?
4. Is this block `[T1]` (copy verbatim) or `[T3]` (I author it)?

---

## 13. Return this

1. `git status --short` and `git diff --stat` — expect ~10 files, zero under `tests/`.
2. Full `git diff` for `d3kos_feature_gate.py` and `hardware-probe.sh`.
3. `./tests/run-all.sh` output — before **and** after.
4. The four §9 command outputs, real, pasted.
5. **Decision Log** — every deviation from this spec, or the single word `none`.

---

## 14. What Tier 2 checks when it comes back

Three specific failure modes, in priority order:

1. **`_accel_ok()` folded back into a conditional.** This is the fail-open defect and it
   *looks* correct. Read the function standalone: with a Coral fitted and
   `accelerator_class_any: ["hailo-8l"]`, does it return `False`? `F1` asserts exactly this —
   but confirm by reading, because a subtly wrong refactor could pass one assertion.
2. **A gate comparing GB instead of MB.** `grep -n "ram_gb" d3kos_feature_gate.py` — every
   hit must be display-only. `F5`/`F6` cover the two known board sizes; a third size could
   still be wrong.
3. **Only a green run shown.** The commonest Tier 3 failure is writing code first and running
   the suite once. No before-run means the TDD sequence was not followed — reject regardless
   of the diff.

Also confirm: `tests/` diff is **empty**; no `hardware-profile.json` in the deployed tree;
`RemainAfterExit=no`; the udev rule contains no `curl`.

---

## 15. Tier 3 Dispatch Prompt

Paste everything below the line to the Tier 3 implementer. **Do not paraphrase it — the
constraints are the point.**

---

TASK TYPE: [IMPLEMENT] — Tier 3

You are the Tier 3 implementer on d3kOS v0.9.9.5, item D17. Tier 1 (Opus 5) wrote your spec
and will verify your work under AAO §25.8. Do exactly what the spec says and nothing more.
**You are not being asked to design anything.**

WORKING DIRECTORY: `/home/boatiq/Helm-OS`

READ THIS FILE FIRST, IN FULL, BEFORE TOUCHING ANYTHING:
`deployment/docs/atomic-specs/V09995-D17-HARDWARE.md`

It contains the exact file table (§3), the code line ranges to copy verbatim (§4), the
invariants to verify after copying (§4.1–§4.4), the manifest contract (§5), the definition of
done (§9), the hard constraints (§10) and your ESCALATE-IF list (§11).

YOUR TASK — D17 ONLY. HCD-1 through HCD-7. Not HCD-8. Not D05, D16 or D02.

USE GRAFT, DO NOT GREP. The repo is indexed:
```
graft ask "dashboard app.py route registration" --source
graft skeleton deployment/v0.9.9.5/opt/d3kos/services/dashboard/app.py
graft grep "ADVISORY_BLIND_SPOTS"
```

TDD — MANDATORY SEQUENCE, NO SHORTCUTS
1. Run `./tests/run-all.sh` **first**. Paste the real output. Baseline is **160 failed,
   0 errors**. If it differs, STOP and escalate.
2. Copy the `[T1]` code per §3/§4. Verify every invariant in §4.1–§4.4.
3. Author the `[T3]` files per §5–§8.
4. Re-run `./tests/run-all.sh`. Paste the real output. `test_feature_gate.py` must be
   **16 green**, `errors` must be **0**.
5. Run the four verification commands in §9. Paste real output for each.

Do not write the fix first. Do not claim a run you did not perform. **If you did not paste
real terminal output, the work is rejected.**

THE THREE THINGS THAT WILL GET YOUR WORK REJECTED
1. **Editing anything under `tests/`.** The 160 guard tests are the contract. `git diff
   --stat tests/` must be empty.
2. **Folding the accelerator whitelist back inside a conditional** in `_accel_ok()`. That is
   the exact v1.0 fail-open defect (a Coral satisfying a Hailo-only feature). Keep it a
   standalone function.
3. **Gating on GB instead of MB.** `ram_mb` only. `ram_gb_nominal` is display-only.

IF YOU ARE UNSURE ABOUT ANYTHING
Do not guess and do not invent a default. Emit the §25.4 escalation block and stop:

```
🔺 ESCALATION — D17/<task>
Tier asking     : Haiku / Tier 3
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

Never assume on anything touching a **port number, a file path, or a RAM unit**.

WHEN DONE, RETURN the five items in §13 of the spec.

---

*Authored by Claude Opus 5 (Tier 1), S161 2026-09-12.*
