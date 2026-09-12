# D05 — signalk-forward-watch v0.2.4 · Atomic Spec

**Document:** V09995-D05-001 · **Version:** 1.0 · **Date:** 2026-09-12 (S161)
**Author:** Claude Opus 5 (Tier 1) · **Implementer:** Tier 3 (Haiku) · **Orchestrator:** Tier 2 (Sonnet)
**Design reference:** `V09995_SOLUTION_DESIGN.md` §6 — ⚠ **see §1: §6.1 is factually wrong about this repo**

---

## 1. ⚠ READ THIS FIRST — the design doc's §6.1 does not match the repo

`V09995_SOLUTION_DESIGN.md` §6.1 was written **without reading the plugin repo.** Verified
against the live repo on 2026-09-12 (S161):

| §6.1 says | Reality |
|---|---|
| "Export the model: `yolo export model=yolov8n.pt format=onnx`" | ❌ The model is **not stock yolov8n**. It is **custom-trained** — exported from `best.pt` via `export_onnx.bat` (ultralytics, `imgsz=640`, `simplify=True`). |
| "Commit `assets/models/yolov8n.onnx` (≈6 MB)" | ❌ Wrong path, wrong name, wrong size. It is **`models/forward-watch.onnx`, 12.3 MB**, and it is **already committed** (`git ls-files` confirms). |
| `"files": ["index.js", "lib/", "assets/models/yolov8n.onnx"]` | ❌ There is no `lib/` — the code is in **`plugin/`**. |
| "Delete `scripts/install-model.js` if present" | ➖ No-op. No `scripts/` directory exists. |
| "v1.0 implemented a `postinstall` script that downloads from GitHub" | ➖ **No `postinstall` exists and never did.** That was a v1.0 *proposal*, not shipped code. |
| `npm pack --dry-run \| grep yolov8n.onnx` | ❌ Would **fail** — the file is `forward-watch.onnx`. |

### 1.1 SK-FW-1 is ALREADY SATISFIED

Decision **D05-1 (Option C — bundled asset, no download)** is already implemented:

```
✅ models/forward-watch.onnx is tracked in git
✅ npm pack --dry-run ships it:  "npm notice 12.3MB models/forward-watch.onnx"
✅ index.js:9  const MODEL_PATH = path.join(__dirname, 'models', 'forward-watch.onnx');
✅ no postinstall, no network fetch anywhere
```

**Do not re-bundle the model. Do not export a new one. Do not touch `models/`.**

What is genuinely left of SK-FW-1 is **one defect**: `index.js` has **no existence check**, so
a missing or corrupt model surfaces as a cryptic `onnxruntime` error instead of an
actionable one. That is §3 task 1.

🔺 **This whole section is a Tier-1 finding. `V09995_SOLUTION_DESIGN.md` §6.1 must be
corrected.** Tier 2: escalate to Tier 1 to amend the design doc; do **not** amend it
yourself.

---

## 2. Location — outside the Helm-OS repo

```
/home/boatiq/signalk-forward-watch        ← a SEPARATE git repository
```

⛔ This is **not** inside `Helm-OS/`. `git status` in `Helm-OS` will not show these changes.
Run git commands **inside the plugin directory.** Current version: **0.2.3** → target **0.2.4**.

### 2.1 PRE-EDIT SNAPSHOT — PRE-CLEARED, DO NOT HALT

Your baseline is commit **`74e57be`** (*"chore: bump to 0.2.3"*). The working tree carries
**eight untracked files that are NOT yours** — operator working notes (`*.txt`) and a
stray `! npm config set registry.npmjs.org.txt`. Verified S161.

The Pre-Edit Snapshot Rule would normally make you stop and refuse to proceed. **The
operator has acknowledged these and you are authorised to continue.** Do not touch them, do
not commit them, do not mention them again.

`models/`, `index.js`, `package.json` and `README.md` are all **clean and tracked** — which
is what matters for this task.

⛔ **Never `git push` from here either.** The GitHub remote is
`SkipperDon/signalk-forward-watch`, and `npm publish` is **explicitly out of scope for
v0.9.9.5** (the publish decision is v0.9.9.6, D02-9 / §8.0).

---

## 3. Scope — four tasks

| # | Task | File | Tier |
|---|---|---|---|
| 1 | Actionable model-load failure | `index.js` | `[T3]` |
| 2 | Pin the tarball with a `files` array + version bump | `package.json` | `[T3]` |
| 3 | README — remove any model-download step, bump version refs | `README.md` | `[T3]` |
| 4 | **SK-FW-2a** — Signal K plugin-contract test on the lab Pi | *procedure, no file* | `[T3]` runs it, `[T2]` verifies |

**SK-FW-2b (OpenPlotter platform validation) is OUT OF SCOPE** — deferred to a field trial,
no OpenPlotter instance available (operator, S159). Do not attempt it.

---

## 4. Task 1 — actionable model-load failure `[T3]`

`index.js` line 9 defines `MODEL_PATH`; line 77 hands it to `new Detector(...)`. Nothing
checks the file exists first.

Insert immediately **after** the `MODEL_PATH` definition (line 9):

```javascript
if (!fs.existsSync(MODEL_PATH)) {
  throw new Error(
    'signalk-forward-watch: bundled model missing at ' + MODEL_PATH +
    ' — reinstall the plugin. This build never downloads models.');
}
```

### Constraints

- `fs` must already be required at the top of `index.js`. **If it is not, add
  `const fs = require('fs');`** — that is the only new require permitted.
- The message must name the **actual** path and state that the build never downloads. Do not
  reword it to mention `yolov8n`.
- **Do not change `MODEL_PATH` itself.** `models/forward-watch.onnx` is correct.
- Throw at module scope as shown. Do not convert it to a warning, a log line, or a
  `plugin.start()` guard — a missing model means the plugin cannot function, and silent
  degradation in a *safety* plugin is the defect being closed.

---

## 5. Task 2 — `package.json` `[T3]`

Two changes only.

### 5.1 Version

```
"version": "0.2.3"   →   "version": "0.2.4"
```

### 5.2 Add a `files` array

There is currently **no `files` array**, so npm falls back to `.npmignore`. That works today
(the tarball is correct — verified) but it is fragile: any new top-level file ships by
default. Pin it explicitly.

```json
"files": [
  "index.js",
  "plugin/",
  "models/forward-watch.onnx"
]
```

### 5.3 Constraints

- **`plugin/`, not `lib/`.** The design doc says `lib/`; that directory does not exist.
- **`models/forward-watch.onnx`, not `assets/models/yolov8n.onnx`.**
- Do **not** add a `postinstall`. Do not add any script that touches the network.
- Do **not** change `dependencies`, `engines`, `signalk-plugin`, `main`, or `repository`.
- Do **not** change `"license"` — see §8, it needs an operator decision, not an edit.

### 5.4 Verification gate — this is the one that matters

```bash
cd /home/boatiq/signalk-forward-watch
npm pack --dry-run 2>&1 | grep "forward-watch.onnx"
```

Must print the entry. **If it does not, the tarball is wrong — stop and escalate.** Also
confirm the tarball still contains all seven `plugin/*.js` files; a `files` array that omits
one produces a plugin that installs and then crashes at runtime.

---

## 6. Task 3 — README `[T3]`

```bash
grep -niE "download|yolov8n|model.*(download|fetch)|step 2" README.md
```

- **If** a "Download the YOLO model" step exists, delete it and make Step 1 read:
  > **Install the plugin.** The detection model ships inside the package — no download is
  > required, and the plugin never contacts the network for model data.
- ⛔ **Do NOT write** that the model *"downloads automatically during npm install"*. v1.0's
  replacement text said that and it contradicts D05-1 outright.
- Bump any `0.2.3` version reference to `0.2.4`.
- Add the SK-FW-3 platform wording **verbatim**:
  > *"Tested on Signal K Node Server 2.x on Raspberry Pi OS. Expected to work on OpenPlotter
  > installations running the same Signal K version; not yet validated on OpenPlotter
  > itself."*

Understating this is better than overstating it. Do not upgrade "expected to work" to
"works".

---

## 7. Task 4 — SK-FW-2a plugin-contract test `[T3]` runs, `[T2]` verifies

Proves the plugin installs, appears in the Signal K admin UI, enables without error, and
processes frames — on the lab Pi's existing Signal K server.

### 7.1 ⛔ PREREQUISITE — the Signal K unit name is UNKNOWN and must not be guessed

`V09995_SOLUTION_DESIGN.md` §11 lists this as an open item: *"Signal K systemd unit name —
Read on lab Pi: `systemctl list-units '*signalk*'`. **Not guessed.**"*

```bash
ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237 "systemctl list-units '*signalk*' --all --no-pager"
```

🔺 **ESCALATE-IF** that command returns no unit, more than one, or you cannot reach the Pi →
**CLARIFICATION**. Do **not** substitute `signalk.service`, `signalk-server.service`, or any
other plausible name. Guessing a unit name produces a restart command that silently does
nothing.

### 7.2 Procedure

```bash
cd /home/boatiq/signalk-forward-watch
npm pack --dry-run | grep forward-watch.onnx     # gate — must match
npm pack                                         # → signalk-forward-watch-0.2.4.tgz

# on the lab Pi:
cd ~/.signalk
npm install /path/to/signalk-forward-watch-0.2.4.tgz
sudo systemctl restart "$SK_UNIT"                # the name confirmed in 7.1
journalctl -u "$SK_UNIT" -f | grep forward-watch
```

### 7.3 Pass conditions

| # | Condition |
|---|---|
| 1 | `npm install` of the tarball completes with **no network fetch for model data** |
| 2 | Plugin appears in the Signal K admin UI plugin list |
| 3 | Enabling it produces **no error** in `journalctl` |
| 4 | The model loads — no `onnxruntime` failure, and the §4 guard does **not** fire |
| 5 | An **offline** install works: repeat step 1 with the NIC down. §10.5 requires *"plugin runs with NIC down"*. |

### 7.4 ⛔ Deploy authorisation

Installing on the lab Pi is a **state-changing action on a shared device.** Per the standing
rule it needs **explicit operator approval in the current session.** Prior-session approval
does not carry.

**Tier 3: do not run §7.2 against the Pi. Prepare the commands, run the local `npm pack`
gate only, and hand the Pi steps to Tier 2**, who obtains approval.

---

## 8. Operator flag — the licence problem is worse than §6.1 states

§6.1 flags YOLOv8's **AGPL-3.0** and notes that bundling weights is the moment it becomes
redistribution. Two things it did not know, now verified:

1. **The model is a fine-tune of YOLOv8** (`export_onnx.bat` runs `ultralytics`, from
   `best.pt`). A fine-tuned derivative is a stronger AGPL claim than redistributing stock
   weights, not a weaker one.
2. **`package.json` declares `"license": "Apache-2.0"`** while the shipped artefact is
   AGPL-3.0-derived. That is an internal inconsistency in the package metadata, and it ships
   today at v0.2.3.

**This is an operator/legal decision, not a code change.** Do **not** edit the `license`
field, do not add an AGPL notice, do not remove the model. Flag it and stop.

It does **not** block v0.9.9.5 — nothing is published this release. It **does** block
`npm publish` in v0.9.9.6.

---

## 9. Definition of done

D05 touches **no** file under `Helm-OS/`, so **the 160 guard tests are unaffected.** Expected
state after D05: still **160 failed, 0 errors**. If any count changes, you edited something
you should not have.

Return, as real pasted output:

```bash
cd /home/boatiq/signalk-forward-watch
git diff                                          # expect: index.js, package.json, README.md
node --check index.js                             # syntax
node -e "JSON.parse(require('fs').readFileSync('package.json'))" && echo "package.json valid"
npm pack --dry-run 2>&1 | grep -cE "plugin/.*\.js"   # must be 7
npm pack --dry-run 2>&1 | grep forward-watch.onnx    # must match
grep -n '"version"' package.json                  # must read 0.2.4

# prove the guard actually fires
mv models/forward-watch.onnx /tmp/fw.onnx && node -e "require('./index.js')" 2>&1 | head -3
mv /tmp/fw.onnx models/forward-watch.onnx         # PUT IT BACK — mandatory
git status --short                                # models/ must be clean
```

That last pair is the real test of task 1: the error message must name the path and say the
build never downloads. **Restoring the model is not optional** — leaving it moved breaks the
plugin and `git status` must come back clean.

---

## 10. HARD CONSTRAINTS

- Edit **only** `index.js`, `package.json`, `README.md` in `/home/boatiq/signalk-forward-watch`.
- **Do not touch `models/`.** The model is correct, committed, and ships. Do not re-export,
  re-name, move, or delete it.
- **Do not touch `best.pt` / `last.pt`** — training weights, correctly `.gitignore`d and
  `.npmignore`d.
- **Do not add a `postinstall`** or any network call.
- **Do not change the `license` field** (§8).
- **Do not `npm publish`.** Out of scope until v0.9.9.6.
- **Do not `git push`.**
- **Do not install on the Pi** — Tier 2 handles that after operator approval (§7.4).
- **Do not edit any file under `Helm-OS/`**, including the design doc. §1's correction is
  Tier 1's to apply.
- Do not attempt SK-FW-2b (OpenPlotter).

---

## 11. ESCALATE-IF (§25.6)

| Condition | Type |
|---|---|
| `systemctl list-units '*signalk*'` returns zero or multiple units | **CLARIFICATION** — never guess the unit name |
| Lab Pi `192.168.1.237` unreachable | **CLARIFICATION** |
| `npm pack --dry-run` does **not** list `models/forward-watch.onnx` after the `files` edit | **SOLUTION-REQUEST** — the tarball is broken |
| `npm pack --dry-run` lists fewer than 7 `plugin/*.js` files | **SOLUTION-REQUEST** |
| `index.js` has no `fs` require and no obvious top-of-file require block | **CLARIFICATION** |
| README has no model-download step to remove | **PROCEEDING** — note it in the Decision Log, no escalation needed |
| You believe the `license` field should change | **CLARIFICATION** — §8, operator decision |
| Anything tempts you to modify `models/` | **CLARIFICATION** — almost certainly wrong |

**Forced stop (§25.5):** Confidence below 75 on any task → emit the escalation block instead
of code.

### 11.1 Known-limitation pre-approval (§25.5.2)

**No escalation required** for: the absence of `scripts/install-model.js`, the absence of a
`postinstall`, and the absence of `lib/`. All three are §6.1 errors already diagnosed in §1.
Note them in the Decision Log and continue.

---

## 12. Pre-flight self-check (§25.7.1(4))

1. Which three files am I editing, and in which repository?
2. What proves done — what must `npm pack --dry-run` print?
3. What am I forbidden to touch? (`models/`, `license`, anything in `Helm-OS/`, the Pi)
4. Is the model already bundled? (**Yes.** If you are about to export one, re-read §1.)

---

## 13. What Tier 2 checks when it comes back

1. **`models/` is untouched.** `git status --short` must show it clean, and
   `git diff --stat` must not list it. A re-exported or moved model is an immediate reject —
   12.3 MB of binary churn in a git repo is not reversible cheaply.
2. **The `files` array did not shrink the tarball.** Count `plugin/*.js` — must be **7**.
   This is the classic `files`-array failure: it looks right and silently drops a module,
   producing a plugin that installs then crashes on a code path nobody tested.
3. **The guard was actually proven to fire.** Task 1 is unverifiable by reading the diff. If
   there is no pasted output from the move-and-run step showing the real error message, the
   work is incomplete regardless of how correct the code looks.
4. **The Helm-OS 160 still read `160 failed, 0 errors`.** D05 must not move them at all.

Also confirm the README does **not** claim the model downloads during install, and that the
`license` field still reads `Apache-2.0` (unchanged, flagged, not fixed).

---

## 14. Tier 3 Dispatch Prompt

Paste everything below the line to the Tier 3 implementer. **Do not paraphrase it — the
constraints are the point.**

---

TASK TYPE: [IMPLEMENT] — Tier 3

You are the Tier 3 implementer on d3kOS v0.9.9.5, item D05. Tier 1 (Opus 5) wrote your spec
and will verify your work under AAO §25.8. Do exactly what the spec says and nothing more.
**You are not being asked to design anything.**

WORKING DIRECTORY: `/home/boatiq/signalk-forward-watch` — **this is a SEPARATE git repo from
Helm-OS.** Run all `npm` and `git` commands from here.

READ THIS FILE FIRST, IN FULL, BEFORE TOUCHING ANYTHING:
`/home/boatiq/Helm-OS/deployment/docs/atomic-specs/V09995-D05-FORWARD-WATCH.md`

⚠ **Its §1 is the most important section.** The solution design's §6.1 is **wrong about this
repo** — it tells you to export and commit a `yolov8n.onnx` model. **That is already done, with
a different model, at a different path.** `models/forward-watch.onnx` is committed and ships
in the tarball. **Do not export a model. Do not touch `models/`.**

YOUR TASK — D05 ONLY. Three file edits plus one local pack gate:
1. `index.js` — add the model-existence guard (§4)
2. `package.json` — version 0.2.3 → 0.2.4, add the `files` array (§5)
3. `README.md` — remove any model-download step, add the platform wording (§6)
4. Run the local `npm pack --dry-run` gate (§5.4). **Do NOT install on the Pi** — that needs
   operator approval and Tier 2 handles it.

Not D17. Not D16. Not D02. Not SK-FW-2b. Not `npm publish`.

TDD / VERIFICATION — MANDATORY, PASTE REAL OUTPUT
1. `npm pack --dry-run` **before** any edit. Paste it. Confirm `forward-watch.onnx` is
   already listed — that is your proof §1 is right.
2. Make the three edits.
3. Run every command in §9. Paste real output for each.
4. The move-and-run step in §9 is **required** — it is the only proof the §4 guard works.
   **Put the model back afterwards** and show `git status --short` clean.

Do not claim a run you did not perform. **If you did not paste real terminal output, the work
is rejected.**

THE FOUR THINGS THAT WILL GET YOUR WORK REJECTED
1. **Touching `models/`** — re-exporting, renaming, moving or deleting the model.
2. **A `files` array that drops a `plugin/*.js`.** There must be **7**. Count them.
3. **Writing that the model downloads during `npm install`** — it contradicts decision D05-1.
4. **Changing the `license` field.** It is flagged for the operator (§8), not for you to fix.

IF YOU ARE UNSURE ABOUT ANYTHING
Do not guess. Emit the §25.4 escalation block and stop:

```
🔺 ESCALATION — D05/<task>
Tier asking     : Haiku / Tier 3
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

**Never guess the Signal K systemd unit name.** §7.1 — read it off the Pi or escalate.

WHEN DONE, RETURN
1. `git diff` — expect exactly three files.
2. Every §9 command output, real, pasted, including the before-and-after `npm pack`.
3. `git status --short` proving `models/` is clean.
4. **Decision Log** — every deviation from this spec, or the single word `none`. Note the §11.1
   pre-approved items you encountered.

---

*Authored by Claude Opus 5 (Tier 1), S161 2026-09-12. §1 corrections verified against the
live plugin repo the same day.*
