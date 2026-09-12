# D16 — 3D Surround View (Phase 1) · Atomic Spec

**Document:** V09995-D16-001 · **Version:** 1.0 · **Date:** 2026-09-12 (S161)
**Author:** Claude Opus 5 (Tier 1) · **Implementer:** Tier 3 (Haiku) · **Orchestrator:** Tier 2 (Sonnet)
**Design reference:** `V09995_SOLUTION_DESIGN.md` §7
**Decision:** D16-1 — go2rtc **alongside** `camera_stream_manager.py`. Port 8084 untouched.

---

## 1. ⛔ THIS SPEC IS GATED. Do not dispatch it yet.

Three prerequisites must clear **before** any D16 code is written. Two of them cannot be
done by a model.

| # | Prerequisite | Owner | Status |
|---|---|---|---|
| **P1** | §7.2 CPU / thermal / RTSP-client measurement on the lab Pi | **operator + Tier 2** | ⬜ **NOT RUN** |
| **P2** | go2rtc **installed** — no binary exists anywhere in this project | **operator + Tier 2** | ⬜ **NOT DONE** |
| **P3** | go2rtc default port map verified against the pinned README | Tier 2 | ⬜ **~90 % confident only** |

### 1.1 P1 — the measurement gate (§7.2)

v1.0 made **no performance claim at all** while proposing a second RTSP consumer on a Pi 4B
that already runs four decodes, plus SafeHelm, the dashboard, Signal K and AvNav.

| Risk | Pass condition |
|---|---|
| Pi 4B CPU / thermal | 3D view open 10 min → sustained load average **< 3.0**, `vcgencmd measure_temp` **< 80 °C**, no dashboard frame stalls |
| Reolink concurrent RTSP clients | go2rtc **and** `camera_stream_manager` both stream the **bow** camera for 10 min, **neither drops** |

The second risk is the one "alongside" did not account for: **Reolink units cap concurrent
streams**, and go2rtc becomes a *second* client on a camera `camera_stream_manager` already
holds.

⛔ **If the client cap is hit**, the fix is for go2rtc to become the single bow-camera
consumer and re-publish to `camera_stream_manager`. That is a partial move toward Option B
and **requires a new operator decision.** §7.2: *"Do not make that change unilaterally."*
Escalate to Tier 1.

### 1.2 P2 — go2rtc is not installed

Verified S161: `grep -rl "go2rtc" deployment/v0.9.9.4/` returns **nothing**. There is no
binary, no package, no install script. The design doc's unit specifies
`ExecStart=/opt/d3kos/bin/go2rtc` — that path does not exist.

Obtaining, verifying and placing the binary is an **operator/Tier 2** task (it is a download
from an external source onto a shared device). **Tier 3 must not download or install it.**

### 1.3 P3 — the port map is an uncertainty flag, not a fact

§7.3 carries this explicitly:

> *Uncertainty flag: ~90 % confident on go2rtc's default port map. **Verify against the
> go2rtc README for the pinned version before deploying.***

v1.0 wrote `api: listen: ":8554"`. 8554 is go2rtc's own default **RTSP** listener; its HTTP
API defaults to **1984**. Binding the API to 8554 collides with go2rtc's internal RTSP
server — and v1.0 paired that with `Restart=always` + `RestartSec=5`, so a bind failure
becomes a restart loop. **That is the BUG-105 pattern: ~40 restarts/sec, 2.6 GB of log,
eight days.**

Tier 2: confirm 1984/8554/8555 against the README of the exact pinned version before the
YAML ships.

---

## 2. Scope — Phase 1 only

v1.0 presented the bird's-eye stitch as *"~50 lines of OpenCV"* and then quietly required
*"operator enters 4 reference points per camera via a calibration UI"* — a whole
touch-screen feature appearing in no build task and no test plan. Establishing water-plane
homography from a floating, rolling hull is genuinely hard: reference marks must be at known
distances and the hull must be still.

**Phase 1 (v0.9.9.5) ships:**

- Forward panel — bow camera via go2rtc WebRTC + SVG range rings
- Bird's-eye panel — **4-up grid of live camera thumbnails** (v1.0's own fallback path)
- `/3d-view` route, three-zone layout, AvNav ↔ 3D toggle

**Phase 2 — homography stitch + calibration UI — is DEFERRED** to backlog item **D16-P2**,
and only after P1 passes. **Do not build any stitching, homography, or calibration UI.**

---

## 3. File placement

`camera_stream_manager.py` lives at
`deployment/v0.9.9.4/opt/d3kos/services/marine-vision/camera_stream_manager.py` (verified
S161 — note **`marine-vision/`**, not `camera/`; the `camera/` path in `Helm-OS/CLAUDE.md` is
a stale v0.9.2 note). **It is not modified by D16.** Port 8084 untouched.

| # | File | Op | Guard test |
|---|---|---|---|
| 1 | `deployment/v0.9.9.5/etc/go2rtc/go2rtc-d16.yaml` | create | `test_v0995_config_guards.py` (`require_file`) |
| 2 | `deployment/v0.9.9.5/opt/d3kos/scripts/configure-go2rtc.sh` | create, `chmod +x` | `test_v0995_config_guards.py` (`require_file`) |
| 3 | `deployment/v0.9.9.5/etc/systemd/system/d3kos-go2rtc.service` | create | U1 (restart storm) |
| 4 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/templates/3d-view.html` | create | Playwright (Tier-1 authored) |
| 5 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/app.py` | **edit** | — |
| 6 | `deployment/v0.9.9.5/opt/d3kos/services/dashboard/static/js/*` | **edit** | S2 (no hardcoded localhost) |

The two `require_file` paths are **exact**. The guard tests will not find them at any other
location.

⚠ `slots.json` and `hardware.json` exist **only on the Pi** — they are operator data and are
not in the repo (verified S161). `configure-go2rtc.sh` therefore cannot be executed locally;
it is verified by content, not by running it.

---

## 4. `[T1]` — go2rtc YAML

Copy from design §7.3, **lines 634–647**, verbatim — **subject to P3 confirming the ports.**

```yaml
# /etc/go2rtc/go2rtc-d16.yaml   —   chmod 600, root:d3kos
api:
  listen: "127.0.0.1:1984"      # loopback only; dashboard proxies to it
rtsp:
  listen: "127.0.0.1:8554"      # loopback only
webrtc:
  candidates: ["127.0.0.1:8555"]
streams:
  d16_forward:
    - "{BOW_SUBSTREAM_RTSP_URL}#video=copy"   # passthrough, no transcode
log:
  level: warn
```

### Invariants

| # | Invariant | Why |
|---|---|---|
| Y1 | Every `listen` is `127.0.0.1:` — **never** `:port` and never `0.0.0.0` | `listen: ":8554"` binds all interfaces. The boat runs Wi-Fi **with guests aboard** — that publishes unauthenticated camera streams and the control API to everyone. Guarded by **U2**. |
| Y2 | `#video=copy` — passthrough, no transcode | Pi 4B CPU budget |
| Y3 | Camera **sub-stream** URL, not the main stream | ditto |
| Y4 | `{BOW_SUBSTREAM_RTSP_URL}` is a **placeholder** in the committed file | Reolink RTSP URLs embed `user:password@`. A real credential in a repo file is a secret leak. Guarded by **U3**. |
| Y5 | File mode **600**, owner `root:d3kos` | ditto |

---

## 5. `[T3]` — `configure-go2rtc.sh`

Resolves the real stream URL **at runtime on the Pi** and writes the YAML.

1. Read `/opt/d3kos/config/slots.json`; find the slot whose `roles` contains
   **`forward_watch`**.
2. Resolve that slot's `hw_id` → `rtsp_url` in `/opt/d3kos/config/hardware.json`.
3. Write `/etc/go2rtc/go2rtc-d16.yaml` from the §4 template with the URL substituted, under
   **`umask 077`**.
4. `chown root:d3kos`, `chmod 600`.

### Constraints

- ⛔ **Redact the password in every journal/stdout line.** §7.3: *"redacts the password when
  echoing anything to the journal."* Print `rtsp://***:***@host/path`, never the real URL.
  A credential in `journalctl` is a credential leak.
- Use `jq` for JSON. Do not parse JSON with `grep`/`sed`.
- `umask 077` **before** the first write, so the file is never briefly world-readable.
- Fail loudly with a non-zero exit if the `forward_watch` slot or the `rtsp_url` is missing.
  Do **not** write a YAML with an empty or placeholder stream — go2rtc would fail its bind
  and (before U1's start limit) loop.

---

## 6. `[T3]` — systemd unit

Copy design §7.3, **lines 660–677**.

| # | Invariant | Why |
|---|---|---|
| Z1 | `Restart=on-failure` — **never** `Restart=always` | BUG-105. Guarded by **U1**. |
| Z2 | `StartLimitIntervalSec=300` **and** `StartLimitBurst=5` in `[Unit]` | a misconfiguration stops after five attempts instead of looping forever |
| Z3 | `RestartSec=10` | not 5 |
| Z4 | `User=d3kos`, `SupplementaryGroups=video` | not root |

---

## 7. `[T3]` — layout, range rings, toggle

### 7.1 Layout (§7.4)

```
┌─────────────────────────┬──────────────────────┐
│  FORWARD PANEL   65%    │  BIRD'S EYE     35%  │
│  go2rtc WebRTC          │  Phase 1: 4-up grid  │
│  (bow sub-stream)       │  (port 8084 MJPEG)   │
│  SVG range rings        │                      │
├─────────────────────────┴──────────────────────┤
│  MARINE VISION (existing — unchanged)          │
└────────────────────────────────────────────────┘
```

### 7.2 Range rings

```
ring_y = frame_height × (0.5 − arctan(h/d) / θ_v)
```

`d ∈ {10, 25, 50} m` · `θ_v = 48°` (RLC-810A vertical FOV) · `h` = bow camera height above
waterline, **default 1.35 m until measured**.

⛔ **The overlay MUST carry the label *"Estimated — uncalibrated"* until `h` is entered by
the operator.** Distances must never be presented as surveyed when they are a default. `h`
is an unresolved §11 item — a tape measure at the next boat visit.

### 7.3 Toggle — `[T1]`, and it must be exactly this

```javascript
function toggleAvNav3D() {
    const f = document.getElementById('avnav-frame');
    f.src = f.src.includes('3d-view') ? AVNAV_URL : '/3d-view';
}
```

⛔ **`AVNAV_URL` is built from `window.location.hostname`. NEVER a hardcoded `localhost`.**

> **BUG-48.** Hardcoded `localhost` in front-end code resolves in the **browser**, not on the
> Pi — it killed every remote gauge once already. v1.0's snippet hardcoded
> `http://localhost:8080` and would have regressed it. Guarded by **S2** and by the existing
> `tests/bug48-no-hardcoded-localhost.spec.ts`, which **must stay green**.

- **iframe `src` swap only.** No contact with `showRow()`, the engine ribbon, or the nav
  ribbon. A D16 toggle that disturbs the engine ribbon is a regression in a safety display.

### 7.4 AODA

18px minimum on all text; 48×48px minimum on the toggle and any control. Verified from
**computed style**, never CSS tokens (S115).

---

## 8. Definition of done

| Suite | Expected |
|---|---|
| `test_v0995_config_guards.py` | D16 subset (U1, U2, U3, go2rtc YAML, `configure-go2rtc.sh`) **green** |
| `tests/bug48-no-hardcoded-localhost.spec.ts` | **stays green** |
| every other suite | unchanged |

**`errors` must be 0.**

```bash
cd /home/boatiq/Helm-OS
./tests/run-all.sh
bash -n deployment/v0.9.9.5/opt/d3kos/scripts/configure-go2rtc.sh

# no all-interface bind anywhere
grep -rnE '0\.0\.0\.0|listen:\s*"?:[0-9]' deployment/v0.9.9.5/ | grep -v node_modules   # expect NO match

# no restart storm
grep -rn "Restart=always" deployment/v0.9.9.5/etc/systemd/system/                        # expect NO match

# no credential in the committed YAML
grep -nE "rtsp://[^*]*:[^*]*@" deployment/v0.9.9.5/etc/go2rtc/go2rtc-d16.yaml            # expect NO match

# no hardcoded localhost in delivered JS
grep -rn "localhost" deployment/v0.9.9.5/opt/d3kos/services/dashboard/static/js/         # expect NO match
```

---

## 9. HARD CONSTRAINTS

- Edit **only** the six paths in §3.
- **Do not modify `camera_stream_manager.py`.** Port **8084 is untouched** (decision D16-1).
- **Do not build Phase 2** — no homography, no stitching, no calibration UI. Backlog D16-P2.
- **Do not download or install the go2rtc binary** (§1.2 — operator/Tier 2).
- **No real RTSP credential** in any committed file. Placeholder only.
- **No `0.0.0.0` bind. No bare `:port` listen.**
- **No `Restart=always`** without a start limit.
- **No hardcoded `localhost`** in any browser-delivered file.
- Do not touch `showRow()`, the engine ribbon, or the nav ribbon.
- Do not present range rings as calibrated.
- Do not touch the Pi. Do not commit. Do not `git push`. Do not edit `tests/`.

---

## 10. ESCALATE-IF (§25.6)

| Condition | Type |
|---|---|
| P1 measurement has not been run / you cannot see its result | **BLOCKED — CLARIFICATION.** Do not write code. |
| P1 shows load ≥ 3.0, temp ≥ 80 °C, or either RTSP consumer dropping | **SOLUTION-REQUEST → Tier 1.** Needs a new operator decision. |
| go2rtc binary absent at `/opt/d3kos/bin/go2rtc` | **CLARIFICATION** (expected — §1.2) |
| P3 unconfirmed, or the README shows a different default port map | **CLARIFICATION** |
| `slots.json` has no slot with role `forward_watch` | **CLARIFICATION** — never guess a slot |
| `hardware.json` has no `rtsp_url` for that `hw_id` | **CLARIFICATION** |
| Bow camera height `h` has not been measured | **PROCEEDING** on 1.35 m **with the "Estimated" label** — pre-approved, §10.1 |
| `app.py` already defines `/3d-view` | **CLARIFICATION** |
| A guard test still fails and you believe the **test** is wrong | **SOLUTION-REQUEST** — never edit the test |

**Forced stop (§25.5):** Confidence below 75 → escalation block instead of code.

### 10.1 Known-limitation pre-approval (§25.5.2)

- **Bow camera height** — 1.35 m default is pre-approved *provided* the "Estimated —
  uncalibrated" label ships. No escalation.
- **`configure-go2rtc.sh` cannot be executed locally** (its input JSON is Pi-only). Verify by
  **content and `bash -n`**; that tests the same assertion. No escalation.

---

## 11. Pre-flight self-check

1. Has P1 passed? **If you cannot answer yes with evidence, stop.**
2. Which six files am I touching, and which two paths are exact `require_file` targets?
3. What am I forbidden to touch? (`camera_stream_manager.py`, port 8084, Phase 2, the Pi)
4. Is the toggle using `window.location.hostname`?

---

## 12. What Tier 2 checks when it comes back

1. **Any bind that is not `127.0.0.1`.** Grep the YAML *and* the unit. A bare `:8554` looks
   harmless and publishes camera video to every guest on the boat Wi-Fi. This is the highest
   severity D16 failure.
2. **A real credential in the committed YAML.** `grep -E "rtsp://[^*]*:[^*]*@"`. If found,
   the file is a secret leak — reject, and check whether it was committed.
3. **`Restart=always`, or a start limit in the wrong section.** `StartLimitIntervalSec` and
   `StartLimitBurst` belong in **`[Unit]`**, not `[Service]`. Placed in `[Service]` they are
   silently ignored and the BUG-105 protection is absent while appearing present.
4. **The toggle using string concatenation that yields a literal `${...}`**, or reverting to
   `localhost`. Read the emitted URL, do not trust the diff shape.

Also confirm: port 8084 unchanged, no stitching code, the "Estimated" ring label present,
`tests/` diff empty.

---

## 13. Tier 3 Dispatch Prompt

⛔ **DO NOT DISPATCH until P1, P2 and P3 in §1 are all cleared.** Tier 2: if you are reading
this and P1 has not been run, stop and tell the operator.

---

TASK TYPE: [IMPLEMENT] — Tier 3

You are the Tier 3 implementer on d3kOS v0.9.9.5, item D16. Tier 1 (Opus 5) wrote your spec
and will verify your work under AAO §25.8. Do exactly what the spec says and nothing more.
**You are not being asked to design anything.**

WORKING DIRECTORY: `/home/boatiq/Helm-OS`

READ THIS FILE FIRST, IN FULL:
`deployment/docs/atomic-specs/V09995-D16-SURROUND-VIEW.md`

YOUR TASK — D16 **Phase 1 only**. The forward panel, the 4-up thumbnail grid, the `/3d-view`
route and the toggle. **No stitching. No homography. No calibration UI.** Those are Phase 2
(backlog D16-P2) and are explicitly out of scope.

Not D17, not D05, not D02.

USE GRAFT, DO NOT GREP:
```
graft ask "dashboard iframe avnav frame toggle" --source
graft grep "avnav-frame"
graft skeleton deployment/v0.9.9.4/opt/d3kos/services/marine-vision/camera_stream_manager.py
```

MANDATORY SEQUENCE — PASTE REAL OUTPUT
1. `./tests/run-all.sh` **first**. Paste it. Note which `test_v0995_config_guards.py` cases
   are red.
2. Write the files per §3–§7.
3. `./tests/run-all.sh` again. Paste it. The D16 config-guard subset must be green,
   `errors` must be **0**, and `bug48-no-hardcoded-localhost.spec.ts` must still pass.
4. Run every command in §8. Paste real output for each.

Do not claim a run you did not perform. **No pasted output means the work is rejected.**

THE FOUR THINGS THAT WILL GET YOUR WORK REJECTED
1. **A bind that is not `127.0.0.1`** — including a bare `:8554`. It publishes the boat's
   camera feeds to every guest on the Wi-Fi.
2. **A real RTSP username/password in any committed file.** Placeholder only.
3. **`Restart=always`**, or `StartLimitBurst` placed in `[Service]` instead of `[Unit]`
   (where it is silently ignored).
4. **A hardcoded `localhost`** in browser-delivered JS. It resolves in the *browser* and
   already broke every remote gauge once (BUG-48).

IF YOU ARE UNSURE ABOUT ANYTHING
Emit the §25.4 escalation block and stop:

```
🔺 ESCALATION — D16/<task>
Tier asking     : Haiku / Tier 3
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

**Never guess a port, a slot name, or an RTSP URL.** §10 pre-approves exactly two
assumptions; everything else escalates.

WHEN DONE, RETURN
1. `git status --short` and `git diff --stat` — zero files under `tests/`.
2. Full `git diff` for the go2rtc YAML, the unit file, and the toggle JS.
3. `./tests/run-all.sh` before and after.
4. Every §8 command output, real, pasted.
5. **Decision Log** — every deviation, or `none`. Note which §10.1 pre-approvals you used.

---

*Authored by Claude Opus 5 (Tier 1), S161 2026-09-12.*
