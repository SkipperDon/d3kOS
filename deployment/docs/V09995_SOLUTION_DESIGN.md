# v0.9.9.5 — Solution Design
**Document:** V09995-SOL-001
**Version:** 1.2
**Date:** 2026-09-11
**Author:** Claude Opus 5 (S160) — architectural review and correction of v1.0 (Claude Sonnet 4.6, S160)
**Status:** APPROVED for implementation — all four v1.1 open decisions ruled by operator, S160.
Subject to the pre-implementation gate in §12.

> **v1.0 was not safe to implement.** It contained two safety-critical defects in the
> COLREGs classifier, a model-hosting design that did the opposite of decision D05-1,
> a wrong Signal K port, and a fail-open feature gate. This version corrects all of
> them. See Revision History.

---

## Revision History

| Ver | Date | Change |
|---|---|---|
| 1.0 | 2026-09-11 | Initial design (Sonnet 4.6). Marked APPROVED in error — operator had approved the five *decisions*, not the document. |
| 1.2 | 2026-09-11 | **Operator rulings on all four v1.1 open decisions (§2).** ACK scope = per-target, with Critical from another target winning queue insertion immediately (D02-5). SH-11 marked SUPERSEDED in the checklist (applied). `content_hash` guard approved, `probe_version` stays per-spec (D17-1). Rule 14 phrase changed to advisory language — *"COLREGs require starboard alteration"* — because an imperative shifts liability from captain to software (D02-6). Adds §12 Defect Closure: no BUG entry; the v1.0 defects are closed by named guard tests that must exist and fail before implementation. |
| 1.1 | 2026-09-11 | **Opus 5 review.** Fixed: Rule 14 inversion (fired on *same*-course vessels, never on head-on); Rule 13 role inversion (told captain to give way while stand-on); alert gating policy added (v1.0 had none — every AIS target would voice every 15 s); SK-FW-1 rewritten to actually bundle the model; Signal K port corrected to 8099 (BUG-46); feature-gate accelerator whitelist fail-open fixed; `ram_gb` truncation fixed (8 GB Pi read as 7); REQ-HCD-027 15-minute re-probe added; restart-storm patterns removed from both units; credential and bind-address exposure closed; CORS gap closed; D16 stitch deferred behind a CPU gate; unit-test specifications added; requirements traceability matrix added; Advisory Role section added per operator instruction. |

---

## 1. Advisory Role and Limitations

**Operator instruction, S160: what is being produced is for the captain's assistance.**

This section is normative. It constrains every design decision in D02 and D16.

- **SafeHelm assists the captain. It does not command, steer, or decide.** Every output
  is a recommendation. The captain's judgment overrides the system in all cases.
- **No output alters vessel control.** There is no autopilot path, no steering output, and
  no Signal K write path in this release (see §5.6).
- **COLREGs obligations remain entirely the captain's.** Rule 2 (responsibility) and
  Rule 5 (proper lookout by sight and hearing) are not discharged, reduced, or satisfied
  by this system. SafeHelm is not a lookout.
- **The system will be wrong sometimes, and the captain must know how.** Documented
  blind spots, to be stated in the UI and the manual:
  - Vessels without AIS are **invisible** to it. Small craft, most sailboats, kayaks,
    debris, and navigation marks do not appear.
  - There is no radar and no vision input in this release. AIS is the only source.
  - It depends on the target's own reported COG/SOG, which may be stale, wrong, or absent.
  - Own-vessel COG/SOG comes from GPS; loss of fix degrades or disables all calculations.
- **Silence is not clearance.** No alert means no *qualifying AIS target*, not "clear water".

**Implementation requirements arising from this section:**

| ID | Requirement |
|---|---|
| ADV-1 | The widget footer SHALL display, at all times the widget is visible: *"Advisory only — AIS targets only. Captain remains responsible for lookout and navigation."* |
| ADV-2 | On service start, SafeHelm SHALL speak once: *"SafeHelm advisory active. AIS targets only. Not a substitute for lookout."* |
| ADV-3 | The Hardware page and the user manual SHALL carry the blind-spot list from this section verbatim. |
| ADV-4 | No voice phrase SHALL assert that water is clear, that a target is safe, or that no action is required. |

---

## 2. Locked Decisions

| # | Question | Decision | Source |
|---|---|---|---|
| D02-1 | SafeHelm phase scope | **Advisory Mode — Phase 1 engine + active output.** Voice via ai_bridge + AvNav widget overlay. **Shadow Mode is explicitly NOT in scope.** | Operator S159, reconfirmed S160 ("I do not want shadow") |
| D02-2 | SH-15 gate | Does **not** block v0.9.9.5. Enforced only at Phase 2+ Signal K write path, which is not built in this release. | Operator S159 |
| D02-3 | **Alert gating policy** | **3-tier matrix — see §5.2.** Tier 1 Advisory = visual only, no voice. Tier 2 Warning = voice once. Tier 3 Critical = voice repeated. | Operator S160 |
| D02-4 | **Alert rate caps** | Per-target 60 s; global 15 s between spoken sentences; priority by lowest TCPA. | Operator S160 |
| D16-1 | go2rtc vs camera_stream_manager | **Option A — alongside.** camera_stream_manager stays on 8084, untouched. | Operator S159 |
| D05-1 | YOLOv8n model hosting | **Option C — bundled asset.** Committed to the repo, shipped in the npm tarball. **No download at install or at runtime.** | Operator S159 |
| D05-2 | OpenPlotter test (SK-FW-2) | **Split — see §6.2.** Signal K plugin-contract test runs on the lab Pi now; OpenPlotter-specific validation deferred to a field trial. | Opus S160, revising S159 |
| D02-5 | **ACK queue scope** | **Per-target.** ACK clears only *"the active audio queue segment associated exclusively with that target's ID."* If another target reaches Critical while one is being acknowledged, **the Critical payload immediately wins queue insertion.** | Operator S160 |
| D02-6 | **Rule 14 phrasing** | **Advisory, not imperative:** *"Danger. Head-on situation. COLREGs require starboard alteration."* An imperative command shifts liability from the captain to the software. | Operator S160 |
| D17-1 | `probe_version` invalidation | **`probe_version` increments on every write (per HCD-REQ-001) AND `content_hash` is retained.** Consumers verify in microseconds that the payload did not change, avoiding 96 forced cache clears a day on a marine telemetry bus. | Operator S160 |

### 2.1 Resolved conflict — SH-11 superseded (ruling applied)

`PROJECT_CHECKLIST.md:527` **SH-11** defined Phase 1 as *"Log-only — no alarms, no
autopilot."* Decision D02-1 skips that stage. Two governance records disagreeing is the
failure mode that produced BUG-15 (bug file said OPEN, checklist said FIXED, code said
otherwise), so it was not left open.

**Applied S160 under operator ruling.** SH-11 is now `[–] SUPERSEDED S160 → PART 20 / D02
(v0.9.9.5)` with the justification *"Shadow Mode constraints overridden by explicit active
output mandate defined in PART 20 for build milestone v0.9.9.5,"* the original text
preserved inline, and a pointer to PART 20. Marked **do not re-open as an open task.**

The shadow *logger* is retained (`shadow_logger.py`) as a diagnostic record of every
classification, including those suppressed by the gate. That is a log, not Shadow Mode.

---

## 3. Rejected Inputs

Recorded so that a future session does not resurrect these. All three came from an
external AI consultation reviewed in S160.

| Rejected | Why |
|---|---|
| `#define SH15_COMPILE_TIME_BYPASS 1` → `verify_signalk_whitelist() { return true; }` | A safety whitelist check that returns true when unconfigured is fail-open — the exact defect class as BUG-91 (entitlement authority failing open to Tier 1). The correct pattern is the runtime phase flag in §5.6, which never reaches the check because Phase 2 code does not execute. |
| `safehelm_preflight_check.py` compile-isolation scanner | Scans `src/`, `include/`, `plugins/`, `CMakeLists.txt` — none exist. This is Python; there is no compile step. Its `PHASE_2_SIGNATURES` list flags `ai_bridge`, which is **in scope** for Advisory Mode, so the script would fail the build for correct code. |
| "The build does not compile" framing | D02 has never been written. There is no build to fail. No compile-time workaround is needed or wanted. |

---

## 4. Build Sequence

```
D17  Hardware Probe + Feature Gate    ← foundation; no dependencies
  ↓
D05  signalk-forward-watch v0.2.4     ← independent; smallest change
  ↓
D16  3D Surround View (Phase 1)       ← gated on a measured Pi 4B CPU budget
  ↓
D02  SafeHelm Advisory Mode           ← largest; gated on §5.2 policy (now closed)
```

**Test-first, non-negotiable.** Per the Master Standard, the unit tests in §8 are written
and failing *before* the corresponding implementation. The two worst v1.0 defects
(Rule 14 inversion, `ram_gb` truncation) are each caught by three lines of pytest.

---

## 5. D17 — Hardware Capability Detection

**Build tasks:** HCD-1 … HCD-5 · **Spec:** `HARDWARE_CAPABILITY_DETECTION_REQUIREMENTS.md` (HCD-REQ-001 v1.0)

### 5.1 File structure

```
deployment/v0.9.9.5/
  opt/d3kos/scripts/
    hardware-probe.sh                 ← HCD-1
    notify-hardware-change.sh         ← HCD-2 (webhook poster)
  opt/d3kos/services/
    d3kos_feature_gate.py             ← HCD-3
  opt/d3kos/config/
    capabilities-manifest.json        ← HCD-3
  etc/udev/rules.d/
    99-d3kos-accelerator.rules        ← HCD-2
  etc/systemd/system/
    d3kos-hardware-probe.service      ← HCD-1 (boot + udev-triggered)
    d3kos-hardware-probe.timer        ← HCD-1 (REQ-HCD-027, 15 min)
  opt/d3kos/services/dashboard/
    templates/hardware.html           ← HCD-4
    templates/setup.html              ← HCD-5 (modified)
tests/
  test_feature_gate.py                ← HCD-3 unit tests (§8.1)
  test_hardware_probe.sh              ← HCD-1 probe assertions (§8.1)
```

### HCD-1 — hardware-probe.sh

**Two fixes over v1.0:** JSON is built with `jq -n` (v1.0 interpolated `$pi_model`
unescaped into the single source of truth — one quote in a model string would have
produced invalid JSON and failed every gate closed), and RAM is recorded in **MB**.

> **v1.0 defect:** `ram_gb=$(( ram_kb / 1048576 ))` truncates. `MemTotal` excludes
> reserved memory, so a 4 GB Pi reports ≈3 882 000 kB → `3`, and an 8 GB Pi → `7`.
> Any manifest entry `ram_gb_min: 8` could never be satisfied on 8 GB hardware.

```bash
#!/usr/bin/env bash
# /opt/d3kos/scripts/hardware-probe.sh
# Single source of truth writer for /opt/d3kos/config/hardware-profile.json
set -uo pipefail

PROFILE=/opt/d3kos/config/hardware-profile.json
TMP="${PROFILE}.tmp.$$"
trap 'rm -f "$TMP"' EXIT

command -v jq >/dev/null || { echo "hardware-probe: jq missing" >&2; exit 1; }

dt() { tr -d '\0' < "$1" 2>/dev/null || true; }   # device-tree strings are NUL-terminated

# --- Platform ---
pi_model=$(dt /proc/device-tree/model); : "${pi_model:=unknown}"
if [[ "$pi_model" =~ Raspberry\ Pi\ ([0-9]+) ]]; then pi_gen="${BASH_REMATCH[1]}"; else pi_gen=0; fi
ram_kb=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
ram_mb=$(( ram_kb / 1024 ))
ram_gb_nominal=$(( (ram_mb + 512) / 1024 ))       # rounded, DISPLAY ONLY — gates use ram_mb

# --- HAT (REQ-HCD-009: probed at boot and on every scheduled re-probe; not hot-plugged) ---
hat_present=false; hat_product=""; hat_vendor=""; hat_pid=""; hat_ver=""; hat_class=""
if [ -d /proc/device-tree/hat ]; then
    hat_present=true
    hat_product=$(dt /proc/device-tree/hat/product)
    hat_vendor=$(dt  /proc/device-tree/hat/vendor)
    hat_pid=$(dt     /proc/device-tree/hat/product_id)
    hat_ver=$(dt     /proc/device-tree/hat/product_ver)
    case "$hat_product" in
        *"AI HAT+"*)   hat_class="hailo-ai-hat" ;;
        *"PiCAN-M"*)   hat_class="pican-m"      ;;
        *"PiCAN2"*)    hat_class="pican2"       ;;
        *"Waveshare"*) hat_class="waveshare-can";;
        *)             hat_class="unknown-hat"  ;;
    esac
fi

# --- Accelerators ---
classes=(); devices=()
add_accel() { classes+=("$1"); devices+=("$(jq -nc --arg t "$1" --arg n "$2" --arg b "$3" \
              '{type:$t,node:$n,bus:$b}')"); }

[ -c /dev/hailo0 ] && add_accel hailo-8l      /dev/hailo0 pcie
lsusb 2>/dev/null | grep -q '18d1:9302' && add_accel coral-usb      usb usb
lsusb 2>/dev/null | grep -q '18d1:9303' && add_accel coral-usb-mini usb usb
grep -qls '0x1e60' /sys/bus/pci/devices/*/vendor 2>/dev/null && add_accel hailo-8 pcie pcie

accel_present=false; [ ${#classes[@]} -gt 0 ] && accel_present=true
classes_json=$(printf '%s\n' "${classes[@]:-}" | jq -Rsc 'split("\n")|map(select(length>0))')
devices_json=$(printf '%s\n' "${devices[@]:-}" | jq -sc 'map(select(.!=null))' 2>/dev/null || echo '[]')

# --- probe_version: increments on EVERY write, per HCD-REQ-001 ---
current=$(jq -r '.probe_version // 0' "$PROFILE" 2>/dev/null || echo 0)
[[ "$current" =~ ^[0-9]+$ ]] || current=0

jq -n \
  --argjson probe_version "$(( current + 1 ))" \
  --arg     probed_at      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg     pi_model       "$pi_model" \
  --argjson pi_gen         "$pi_gen" \
  --argjson ram_mb         "$ram_mb" \
  --argjson ram_gb_nominal "$ram_gb_nominal" \
  --argjson hat_present    "$hat_present" \
  --arg     hat_product    "$hat_product" \
  --arg     hat_vendor     "$hat_vendor" \
  --arg     hat_pid        "$hat_pid" \
  --arg     hat_ver        "$hat_ver" \
  --arg     hat_class      "$hat_class" \
  --argjson accel_present  "$accel_present" \
  --argjson accel_classes  "$classes_json" \
  --argjson accel_devices  "$devices_json" \
  '{
     probe_version: $probe_version,
     probed_at:     $probed_at,
     platform:  { pi_model:$pi_model, pi_gen:$pi_gen,
                  ram_mb:$ram_mb, ram_gb_nominal:$ram_gb_nominal },
     hat:       { present:$hat_present, product:$hat_product, vendor:$hat_vendor,
                  product_id:$hat_pid, product_ver:$hat_ver, hat_class:$hat_class },
     accelerator:{ present:$accel_present, accelerator_class:$accel_classes,
                   devices:$accel_devices }
   }
   | .content_hash = (del(.probe_version,.probed_at) | tojson | @base64)' > "$TMP"

mv "$TMP" "$PROFILE"          # atomic replace
chmod 644 "$PROFILE"
```

> **RESOLVED — decision D17-1 (operator, S160).** Keep both. `probe_version` increments on
> every write, exactly as HCD-REQ-001 specifies, so the strict system rule is intact; and
> `content_hash` is retained so consumers verify in microseconds that the payload did not
> actually change. REQ-HCD-027's 15-minute probe would otherwise force 96 cache clears a
> day and produce needless CPU spikes on a marine telemetry bus. Implemented as written.

**Units — HCD-1**

`d3kos-hardware-probe.service`
```ini
[Unit]
Description=d3kOS Hardware Probe
Before=d3kos-dashboard.service
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/opt/d3kos/scripts/hardware-probe.sh
ExecStartPost=-/opt/d3kos/scripts/notify-hardware-change.sh
RemainAfterExit=no
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

`d3kos-hardware-probe.timer` — **REQ-HCD-027, absent from v1.0**
```ini
[Unit]
Description=d3kOS Hardware Probe — 15-minute belt-and-suspenders re-probe (REQ-HCD-027)

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
AccuracySec=30s

[Install]
WantedBy=timers.target
```

**CLI:** `ln -sf /opt/d3kos/scripts/hardware-probe.sh /usr/local/bin/d3kos-probe`

> `RemainAfterExit=no` (v1.0 used `yes`), so the timer can re-trigger the same unit.

### HCD-2 — udev rules

> **v1.0 defect:** `RUN+=` executed `lsusb`, a PCI tree walk and an HTTP POST *inside the
> udev worker*, plus a lockfile that could block it. udev kills slow `RUN` processes and
> blocking a worker stalls all device events. The supported pattern is to hand off to
> systemd and return immediately.

```udev
# /etc/udev/rules.d/99-d3kos-accelerator.rules
# Coral USB Accelerator (9302) and Coral USB Mini (9303).
# Hand off to systemd — never block the udev worker.
ACTION=="add|remove", SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", \
    ATTR{idProduct}=="9302|9303", \
    RUN+="/usr/bin/systemd-run --no-block --unit=d3kos-hw-reprobe-$env{SEQNUM} \
          /opt/d3kos/scripts/hardware-probe.sh"
```

`hardware-probe.sh` runs `notify-hardware-change.sh` via `ExecStartPost` when invoked as a
unit; the `systemd-run` path calls the script directly, so the notifier is invoked from the
script's own `EXIT` trap. Serialisation is by `flock` **outside** udev, where blocking is safe:

```bash
# /opt/d3kos/scripts/notify-hardware-change.sh
exec 9>/run/d3kos-hw-notify.lock
flock 9
curl -fsS --max-time 3 -X POST http://127.0.0.1:3000/api/hardware/profile-updated || true
```

**REQ-HCD-020 (≤5 s)** is met: udev returns immediately, `systemd-run` starts the probe
within milliseconds, and the probe completes in well under a second.

### HCD-3 — d3kos_feature_gate.py

> **v1.0 defect — fail-open.** The accelerator check sat inside
> `if req.get('accelerator_any') and not accel['present']:`, so the whole block was skipped
> whenever an accelerator *was* fitted. A Coral USB therefore satisfied a Hailo-only
> feature. Same shape as BUG-91.
>
> **v1.0 defect — no cache.** `_load()` opened and parsed the profile on every call, so the
> "cache" only saved the manifest read. Reaching in from `app.py` to set
> `feature_gate._cached_version = -1` also could not work across processes.

```python
# /opt/d3kos/services/d3kos_feature_gate.py
"""Hardware feature gate. Fails CLOSED: if the profile is unreadable, nothing is enabled."""
import json, os

_PROFILE_PATH  = '/opt/d3kos/config/hardware-profile.json'
_MANIFEST_PATH = '/opt/d3kos/config/capabilities-manifest.json'

_profile = None
_manifest = None
_profile_mtime = None


class FeatureGateUnavailable(RuntimeError):
    """Hardware profile missing or malformed."""


def _load():
    """Reload only when the profile file has actually been replaced.

    The probe writes via atomic rename, so st_mtime_ns changing is the signal.
    A bare stat() is cheap enough to call per lookup and is correct across
    processes — which an in-process version counter is not.
    """
    global _profile, _manifest, _profile_mtime
    try:
        mtime = os.stat(_PROFILE_PATH).st_mtime_ns
    except OSError as exc:
        raise FeatureGateUnavailable(f'cannot stat {_PROFILE_PATH}: {exc}') from exc
    if mtime == _profile_mtime and _profile is not None:
        return
    try:
        with open(_PROFILE_PATH) as fh:
            profile = json.load(fh)
        with open(_MANIFEST_PATH) as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as exc:
        raise FeatureGateUnavailable(f'cannot load hardware profile: {exc}') from exc
    _profile, _manifest, _profile_mtime = profile, manifest, mtime


def _accel_ok(req, accel) -> bool:
    if not req.get('accelerator_any'):
        return True                                    # feature needs no accelerator
    if not accel.get('present'):
        return False                                   # needs one, none fitted
    allowed = req.get('accelerator_class_any')
    if not allowed:
        return True                                    # any accelerator will do
    fitted = accel.get('accelerator_class') or []
    return any(c in fitted for c in allowed)           # whitelist enforced when fitted


def _unmet(key):
    """Yields (reason, upgrade_action) for each unmet requirement."""
    _load()
    feat = _manifest['features'].get(key)
    if feat is None:
        return None, [('Feature not defined.', None)]
    if feat.get('operator_override'):
        return feat, []
    req, plat = feat['requires'], _profile['platform']
    accel = _profile['accelerator']
    out = []
    if plat['pi_gen'] < req.get('pi_gen_min', 0):
        out.append((f"Requires Raspberry Pi {req['pi_gen_min']} "
                    f"(detected: Pi {plat['pi_gen']})",
                    f"Upgrade to Raspberry Pi {req['pi_gen_min']}"))
    if plat['ram_mb'] < req.get('ram_mb_min', 0):
        out.append((f"Requires {req['ram_mb_min']} MB RAM "
                    f"(detected: {plat['ram_mb']} MB)",
                    f"Install at least {req['ram_mb_min']} MB RAM"))
    if not _accel_ok(req, accel):
        allowed = req.get('accelerator_class_any') or ['any supported accelerator']
        out.append((f"Requires {' or '.join(allowed)}",
                    'Add a Hailo-8L AI HAT+ or Google Coral USB Accelerator'))
    return feat, out


def feature_available(key: str) -> bool:
    try:
        feat, unmet = _unmet(key)
    except FeatureGateUnavailable:
        return False                                   # fail closed
    return feat is not None and not unmet


def feature_reason(key: str) -> str:
    try:
        _, unmet = _unmet(key)
    except FeatureGateUnavailable as exc:
        return f'Hardware profile unavailable ({exc}). Run d3kos-probe.'
    return '. '.join(r for r, _ in unmet) or 'Hardware requirements met.'


def feature_upgrade_path(key: str) -> list:
    try:
        _, unmet = _unmet(key)
    except FeatureGateUnavailable:
        return []
    return [a for _, a in unmet if a]
```

**`capabilities-manifest.json` uses `ram_mb_min`, not `ram_gb_min`.** A "4 GB Pi"
requirement is written `"ram_mb_min": 3500` — below the ≈3790 MB a 4 GB board reports.

### HCD-4 — Dashboard Hardware page

```python
@app.route('/hardware')
def hardware_page():
    try:
        profile = load_hardware_profile()
        error = None
    except FeatureGateUnavailable as exc:
        profile, error = None, str(exc)
    manifest = load_capabilities_manifest()
    keys = list(manifest['features'])
    return render_template(
        'hardware.html',
        profile=profile, error=error,
        enabled=[k for k in keys if feature_gate.feature_available(k)],
        locked=[k for k in keys if not feature_gate.feature_available(k)],
        reason=feature_gate.feature_reason,
        upgrade=feature_gate.feature_upgrade_path,
        blind_spots=ADVISORY_BLIND_SPOTS)        # ADV-3


@app.route('/api/hardware/profile-updated', methods=['POST'])
def hardware_profile_updated():
    # No cache poke needed — the gate detects the new mtime by itself.
    _push_hardware_sse_event()
    return jsonify({'ok': True}), 200
```

`POST /api/hardware/profile-updated` binds to `127.0.0.1` only (the notifier is local).

**Toast notifications** via SSE at `GET /api/hardware/events`: `hardware_changed` carries
`{added: [...], removed: [...]}`. New capability → *"New hardware detected — <feature> now
available"* with an Enable button. Removal → warning toast plus graceful stop of the gated
service.

**AODA:** all text on this page and in the toast is ≥18px; the Enable, Re-probe and toast
dismiss controls are ≥48×48px.

### HCD-5 — Wizard final screen

`setup.html` gains a final step, *"Your d3kOS Hardware Profile"*, before Finish. Same
Setup Description rendering as `/hardware`, plus the ADV-3 blind-spot list. The inline
**Re-probe** button calls `POST /api/hardware/reprobe` (which runs
`systemctl start d3kos-hardware-probe.service`) then re-renders in place, so the operator
can fit hardware without restarting the wizard.

---

## 6. D05 — signalk-forward-watch v0.2.4

### 6.1 SK-FW-1 — bundle the model (decision D05-1)

> **v1.0 contradicted its own locked decision.** D05-1 says *bundled in the npm tarball,
> no external download*. v1.0 implemented a `postinstall` script that downloads from
> GitHub. That is Option A wearing Option C's label. Worse: the model would not exist at
> `npm pack` time, so `files: ["assets/"]` would have shipped nothing, and v1.0's claim
> that this *"eliminates offline install failures"* was backwards — it introduces one.
> The URL it used (`ultralytics/assets/.../yolov8n.onnx`) is also unlikely to exist;
> ultralytics publishes `.pt`, and ONNX requires a local export step.

**Do this instead:**

1. Export the model once, on the workstation: `yolo export model=yolov8n.pt format=onnx`
2. **Commit `assets/models/yolov8n.onnx` to the repo** (≈6 MB, one time).
3. `package.json` — no `postinstall`, no network:
```json
{
  "version": "0.2.4",
  "files": ["index.js", "lib/", "assets/models/yolov8n.onnx"]
}
```
4. Delete `scripts/install-model.js` if present. Ensure `.npmignore` / `.gitignore` do not
   exclude `assets/`.
5. Runtime load path, with an actionable failure instead of a silent one:
```javascript
const MODEL_PATH = path.join(__dirname, 'assets', 'models', 'yolov8n.onnx');
if (!fs.existsSync(MODEL_PATH)) {
  throw new Error(
    'signalk-forward-watch: bundled model missing at ' + MODEL_PATH +
    ' — reinstall the plugin. This build never downloads models.');
}
```
6. **Verify before publishing:** `npm pack --dry-run | grep yolov8n.onnx` must print the
   entry. If it does not, the tarball is wrong — do not publish.

> **Flag for the operator, not a blocker:** YOLOv8 is AGPL-3.0. Redistributing the weights
> *inside* a published package is a different act from a user downloading them, and d3kOS
> is a paid-tier product. Worth a licence read before `npm publish`. The plugin already
> uses YOLOv8n, so this pre-dates v0.9.9.5 — but bundling is the moment it becomes
> redistribution.

### 6.2 SK-FW-2 — split into two tasks

The S159 answer ("lab Pi `npm link` is functionally equivalent") and the S160 external
advice ("defer entirely") are both partly right. Splitting captures the testable part now
and defers only what genuinely needs the hardware.

| Task | Scope | Status |
|---|---|---|
| **SK-FW-2a** — Signal K plugin-contract test | Plugin installs, appears in the Signal K admin UI, enables without error, processes frames. Run on the lab Pi's existing Signal K server. | **In scope, v0.9.9.5** |
| **SK-FW-2b** — OpenPlotter platform validation | OpenPlotter's own admin integration, its Signal K build, its service supervision. | **Deferred — field trial.** No OpenPlotter instance available (operator, S159). Does not block. |

SK-FW-2a is worth doing because the plugin interface is `@signalk/signalk-server`, which
OpenPlotter also uses — so it catches essentially every plugin-contract failure. It does
not prove OpenPlotter packaging, which is what 2b covers.

```bash
cd ~/signalk-forward-watch
npm pack --dry-run | grep yolov8n.onnx        # gate: must match
npm pack
cd ~/.signalk
npm install ~/signalk-forward-watch/signalk-forward-watch-0.2.4.tgz
sudo systemctl restart "$SK_UNIT"             # confirm unit name first — see §10
journalctl -u "$SK_UNIT" -f | grep forward-watch
```

**README wording (SK-FW-3):** *"Tested on Signal K Node Server 2.x on Raspberry Pi OS.
Expected to work on OpenPlotter installations running the same Signal K version;
not yet validated on OpenPlotter itself."* Understating this is better than overstating it.

### 6.3 SK-FW-3 — README

Delete *"Step 2 — Download the YOLO model"*. Step 1 becomes: **"Install the plugin. The
YOLOv8n model ships inside the package — no download is required, and the plugin never
contacts the network for model data."** Bump version references to v0.2.4.

> v1.0's replacement text said the model *"downloads automatically during npm install"* —
> contradicting D05-1 a second time. Do not use that wording.

---

## 7. D16 — 3D Surround View (Phase 1)

**Decision D16-1:** go2rtc alongside `camera_stream_manager.py`. Port 8084 untouched.

### 7.1 Rescope — ship the grid, gate the stitch

v1.0 presented the bird's-eye stitch as *"~50 lines of OpenCV"*, then quietly required
*"operator enters 4 reference points per camera via a calibration UI"*. That calibration
UI is a whole touch-screen feature — four cameras, four points each, on a boat — and it
appears in no build task and no test plan. Establishing water-plane homography reference
points from a floating, rolling hull is also genuinely hard: the reference marks must be
at known distances and the hull must be still.

**Phase 1 (v0.9.9.5) ships:**
- Forward panel: bow camera via go2rtc WebRTC + SVG range rings
- Bird's-eye panel: **4-up grid of the live camera thumbnails** (v1.0's own fallback path)
- `/3d-view` route, three-zone layout, AvNav ↔ 3D toggle

**Phase 2 (deferred, new backlog item D16-P2):** homography stitch + calibration UI, and
only after the CPU gate below passes.

### 7.2 CPU and camera-client gate — run before writing any D16 code

v1.0 made no performance claim. Two concrete risks:

| Risk | Why | Gate |
|---|---|---|
| Pi 4B CPU/thermal | 4 RTSP decodes already running, plus go2rtc, SafeHelm, dashboard, Signal K and AvNav | With the 3D view open for 10 min: sustained load average < 3.0, `vcgencmd measure_temp` < 80 °C, no dashboard frame stalls |
| Reolink concurrent RTSP clients | go2rtc becomes a **second** client on the bow camera while `camera_stream_manager` already holds one. Reolink units cap concurrent streams. "Alongside" did not account for this. | Both consumers stream the bow camera simultaneously for 10 min with no drop on either |

If the client cap is hit, the fix is for go2rtc to be the single bow-camera consumer and
re-publish to `camera_stream_manager` — which is a partial move toward Option B and
**requires a new operator decision.** Do not make that change unilaterally.

Use camera **sub-streams** for the panel, and go2rtc **passthrough** (no transcode).

### 7.3 go2rtc configuration

> **v1.0 defect:** `api: listen: ":8554"`. 8554 is go2rtc's own default **RTSP** listener;
> its HTTP API defaults to 1984. Binding the API to 8554 collides with go2rtc's internal
> RTSP server, and v1.0 paired that with `Restart=always` + `RestartSec=5` — a bind failure
> becomes a restart loop. That is the BUG-105 pattern (self-healing runaway, ~40
> restarts/sec, 2.6 GB log, eight days).
>
> *Uncertainty flag: ~90% confident on go2rtc's default port map. **Verify against the
> go2rtc README for the pinned version before deploying.***
>
> The operator's "port 8554" almost certainly meant *a new port, not 8084*. Honoured: RTSP
> stays on 8554, the API moves to 1984, and neither touches 8084.

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

> **Security — v1.0 exposed both credentials and video.** Reolink RTSP URLs embed
> `user:password@`. v1.0 wrote them into the YAML with no `chmod` (while explicitly
> chmod-ing the hardware profile — inconsistent), and `listen: ":8554"` binds `0.0.0.0`,
> publishing unauthenticated camera streams and the control API to everyone on the boat
> Wi-Fi. Both are closed above: loopback binds, `chmod 600`, and browser access goes
> through the authenticated dashboard on :3000.

`configure-go2rtc.sh` reads `slots.json` for the slot whose `roles` contain
`forward_watch`, resolves `hw_id` → `rtsp_url` in `hardware.json`, writes the YAML with
`umask 077`, and **redacts the password when echoing anything to the journal.**

`d3kos-go2rtc.service`
```ini
[Unit]
Description=d3kOS go2rtc — D16 forward panel stream
After=network-online.target
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
ExecStart=/opt/d3kos/bin/go2rtc -config /etc/go2rtc/go2rtc-d16.yaml
Restart=on-failure
RestartSec=10
User=d3kos
SupplementaryGroups=video

[Install]
WantedBy=multi-user.target
```
`Restart=on-failure` with `StartLimitBurst=5` (v1.0: `Restart=always`, no limit) means a
misconfiguration stops after five attempts instead of looping forever.

### 7.4 Layout, rings, toggle

```
┌─────────────────────────┬──────────────────────┐
│  FORWARD PANEL   65%    │  BIRD'S EYE     35%  │
│  go2rtc WebRTC          │  Phase 1: 4-up grid  │
│  (bow sub-stream)       │  Phase 2: stitch     │
│  SVG range rings        │  (port 8084 MJPEG)   │
├─────────────────────────┴──────────────────────┤
│  MARINE VISION (existing — unchanged)          │
└────────────────────────────────────────────────┘
```

Range rings: `ring_y = frame_height × (0.5 − arctan(h/d) / θ_v)`, with `h` = bow camera
height above waterline, `d` ∈ {10, 25, 50} m, `θ_v` = 48° (RLC-810A vertical FOV).
`h` default **1.35 m** until measured (§10). **The ring overlay carries the label
*"Estimated — uncalibrated"* until `h` is entered by the operator**, so distances are never
presented as surveyed when they are a default.

Toggle — iframe `src` swap only; no contact with `showRow()`, the engine ribbon or the nav ribbon:
```javascript
function toggleAvNav3D() {
    const f = document.getElementById('avnav-frame');
    f.src = f.src.includes('3d-view') ? AVNAV_URL : '/3d-view';
}
```
`AVNAV_URL` is built from `window.location.hostname`, **never `localhost`** — hardcoded
`localhost` in front-end code resolves in the *browser* and broke every remote gauge
(BUG-48; guard test `bug48-no-hardcoded-localhost.spec.ts`). v1.0's snippet hardcoded
`http://localhost:8080` and would have regressed BUG-48.

---

## 8. D02 — SafeHelm Advisory Mode

**Port:** 8095, bound `127.0.0.1` · **Phase:** Advisory (engine + voice + widget), no Shadow
**AIS source:** Signal K WebSocket — **port 8099** · **Voice:** `POST http://127.0.0.1:3002/webhook/alert`

> **v1.0 defect — wrong Signal K port.** v1.0 wrote `ws://localhost:3000/...` in one place
> and listed the port as an open question in another. Port 3000 is the **dashboard** —
> v1.0's own HCD-4 test row uses it. `app.py` carries the comment
> **"CRITICAL: Signal K WebSocket is ws://localhost:8099 — NOT ws://localhost:3000"**,
> tagged **BUG-46**, and three existing front-end files already use 8099. Listing this as
> unknown re-opened a settled, previously-bugged question.

### 8.1 File structure

```
deployment/v0.9.9.5/opt/d3kos/services/safehelm/
  safehelm.py              ← Flask (127.0.0.1:8095) + orchestration loop
  cpa_engine.py            ← CPA/TCPA geometry (pure)
  colregs_classifier.py    ← Rules 13/14/15 geometry (pure, no gating)
  alert_gate.py            ← 3-tier threshold matrix (pure)
  voice_arbiter.py         ← global rate cap + priority queue
  alert_manager.py         ← per-target state machine
  signalk_client.py        ← WebSocket consumer (:8099)
  voice_client.py          ← ai_bridge wrapper
  shadow_logger.py         ← records every classification, including suppressed
  static/safehelm-widget.{js,css}
tests/
  test_cpa_engine.py  test_colregs_classifier.py
  test_alert_gate.py  test_alert_manager.py
```

`cpa_engine`, `colregs_classifier` and `alert_gate` are pure functions with no I/O. That is
deliberate: they are the safety-critical parts and they must be unit-testable in isolation.

### 8.2 Alert gating policy (decision D02-3) — closes the v1.0 gap

> **v1.0 had no gating at all.** `classify()` took no CPA, TCPA or range, so it returned a
> rule for **every** target in the AIS list, and the 15-second throttle then voiced each
> one. Thirty targets in a busy channel would have produced a continuous stream of spoken
> alarms. Alert fatigue is how an advisory system gets switched off — which, for a system
> whose whole purpose is assisting the captain (§1), is the worst possible outcome.

| Tier | CPA | TCPA | Range | Output |
|---|---|---|---|---|
| **1 — Advisory** | ≤ 500 m | 0 … 10 min | ≤ 2.0 NM (3704 m) | Widget entry only. **No voice.** |
| **2 — Warning** | ≤ 300 m | 0 … 7 min | ≤ 1.5 NM (2778 m) | Widget flashes + **voice once** |
| **3 — Critical** | ≤ 150 m | 0 … 4 min | ≤ 0.75 NM (1389 m) | Widget red/2 Hz + **voice repeated** |

- All three conditions must hold. Highest qualifying tier wins.
- **Head-on (Rule 14): TCPA limits for Tiers 2 and 3 extended by +2 min** — closing speed
  is roughly doubled, so the same TCPA leaves less distance.
- Targets that do not qualify are logged by `shadow_logger` and never voiced.

> **Correction to the supplied policy.** As given, every tier read *"TCPA ≤ X"* with no
> lower bound, so a target with TCPA = −3 min (already passed and opening) satisfies
> "≤ 7 min" and would alert. **A lower bound of 0 is required** and is applied above.
> Same defect class as the `tcpa < 0` clear condition in §8.5.

```python
# alert_gate.py
import math

NM = 1852.0
HEADON_TCPA_BONUS_S = 120.0

#      tier,        cpa_max_m, tcpa_max_s, range_max_m, voice
TIERS = (
    ('critical',    150.0,     240.0,      0.75 * NM,   'repeat'),
    ('warning',     300.0,     420.0,      1.50 * NM,   'once'),
    ('advisory',    500.0,     600.0,      2.00 * NM,   None),
)


def classify_tier(cpa_m, tcpa_s, range_m, is_headon=False):
    """Highest qualifying tier, or None. None means: log it, never voice it."""
    if tcpa_s is None or math.isinf(tcpa_s) or math.isnan(tcpa_s):
        return None                      # no relative motion / undefined
    if tcpa_s < 0.0:
        return None                      # already passed and opening
    bonus = HEADON_TCPA_BONUS_S if is_headon else 0.0
    for tier, cpa_max, tcpa_max, range_max, voice in TIERS:
        if cpa_m <= cpa_max and tcpa_s <= tcpa_max + bonus and range_m <= range_max:
            return {'tier': tier, 'voice': voice}
    return None
```

### 8.3 Rate caps (decision D02-4)

| Cap | Value | Notes |
|---|---|---|
| Per-target | 60 s between spoken alerts for one MMSI | **Bypassed** on escalation into Tier 3 Critical |
| Global | 15 s between any two spoken sentences | System-wide. **Bypassed by a Critical preemption — D02-5** |
| Priority | **Critical before Warning, then lowest TCPA** | Others queue |

> **Supersedes the operator-supplied `AlertManager`.** Its `> 15` throttle was
> **per target**; policy D02-4 makes per-target 60 s and 15 s **global**. The constant
> changes to 60 and a separate global arbiter is added.

**ACK scope — decision D02-5.** Acknowledging one target clears *"the active audio queue
segment associated exclusively with that target's ID."* It never silences, drops or delays
any other target. And if another target reaches Critical while one is being acknowledged,
the Critical **immediately wins queue insertion** — it does not wait behind the 15 s global
gap. That bypass is the only way "immediately" is meaningful, and it is one-shot per
escalation event so a Critical cannot monopolise the audio channel.

```python
# voice_arbiter.py
import time

class VoiceArbiter:
    """Global audio arbiter. One spoken sentence at a time, system-wide (D02-4).

    Ordering is Critical before Warning, then lowest TCPA. A candidate flagged
    preempt=True has just escalated into Critical and bypasses the global gap,
    per D02-5: a Critical on target B must win queue insertion immediately even
    while target A is being acknowledged.
    """

    GLOBAL_MIN_GAP_S = 15.0
    TIER_RANK = {'critical': 0, 'warning': 1, 'advisory': 2}

    def __init__(self):
        self._last_spoken = 0.0

    def _order(self, c):
        return (self.TIER_RANK.get(c['tier'], 9), c['tcpa_s'])

    def select(self, candidates):
        """candidates: [{'tcpa_s','target_id','phrase','tier','preempt'}] -> one or None."""
        if not candidates:
            return None
        preempting = [c for c in candidates if c.get('preempt')]
        if preempting:
            return min(preempting, key=self._order)      # bypasses the global gap
        if time.time() - self._last_spoken < self.GLOBAL_MIN_GAP_S:
            return None
        return min(candidates, key=self._order)

    def mark_spoken(self):
        self._last_spoken = time.time()
```

> **Interpretation flagged.** D02-5 says a Critical *"must immediately win queue
> insertion."* Implemented as: Critical sorts first **and** bypasses the 15 s global gap
> once per escalation. If you intended queue-order priority only — Critical goes to the
> head of the queue but still waits out the 15 s gap — say so and I will drop the bypass.
> Everything else about D02-5 is implemented exactly as ruled.

### 8.4 COLREGs classifier — both v1.0 bugs fixed

> **v1.0 defect 1 — Rule 14 fired on the wrong vessels.** The code was
> `course_diff = abs((tgt_cog - own_cog + 180) % 360 - 180)` then `if course_diff < 15`.
> With that formula **0 means parallel, same direction; 180 means reciprocal.** So
> `< 15` fired for vessels travelling *together* and **never** for an actual head-on.
> Two boats cruising side by side would hear *"Danger. Head-on situation. Alter course to
> starboard."* A genuine head-on would fall through to the crossing branch. The test is
> `course_diff > 165`.
>
> **v1.0 defect 2 — Rule 13 role inverted.** `112.5 < rb < 247.5` is the sector **abaft
> own beam**. A target there is coming up on *us*, so under Rule 13(a) **they** keep clear
> and **we are stand-on**. v1.0's phrase said *"You do not have right-of-way."* For a
> system whose purpose is assisting the captain (§1), telling them to give way while they
> are obliged to hold course and speed is the most serious defect in v1.0. The mirror
> case — where *we* are overtaking — was labelled `rule15_giveway`, but Rule 13 overrides
> Rule 15 in an overtaking situation.
>
> **Also:** v1.0's classifier never received CPA, TCPA or range, so it could not return
> `no_conflict`. Gating is now §8.2's job and this module is pure geometry.

```python
# colregs_classifier.py
"""COLREGs Rules 13/14/15 geometric classification. Pure; no gating, no I/O.

Relative bearing convention: degrees clockwise from own COG.
0 = dead ahead, 90 = starboard beam, 180 = astern, 270 = port beam.
22.5 deg abaft the beam = 112.5 (starboard) and 247.5 (port) — the Rule 13(b) boundary.
"""

ABAFT_STBD = 112.5
ABAFT_PORT = 247.5
HEADON_COURSE_MIN  = 165.0   # reciprocal within 15 deg
HEADON_BEARING_TOL = 22.5    # target must be roughly ahead
OVERTAKE_COURSE_MAX = 67.5   # overtaking implies broadly similar courses


def _course_diff(a, b):
    """Angle between two headings, 0..180. 0 = same direction, 180 = reciprocal."""
    return abs((b - a + 180.0) % 360.0 - 180.0)


def _relative_bearing_of_me_from_target(own_cog, tgt_cog, rb):
    true_brg_tgt_from_me = (own_cog + rb) % 360.0
    true_brg_me_from_tgt = (true_brg_tgt_from_me + 180.0) % 360.0
    return (true_brg_me_from_tgt - tgt_cog) % 360.0


def classify(own_cog, own_sog, tgt_cog, tgt_sog, relative_bearing):
    """Returns one of:
         'rule13_being_overtaken'  we are STAND-ON; hold course and speed
         'rule13_overtaking'       we are GIVE-WAY; keep clear
         'rule14_headon'           both alter to starboard
         'rule15_giveway'          target on our starboard; we give way
         'rule15_standon'          target on our port; we stand on
         'no_situation'
    """
    rb = relative_bearing % 360.0
    cdiff = _course_diff(own_cog, tgt_cog)

    # --- Rule 13 first: it overrides 14 and 15 (Rule 13(a) "notwithstanding") ---
    if cdiff < OVERTAKE_COURSE_MAX:
        if ABAFT_STBD < rb < ABAFT_PORT and tgt_sog > own_sog:
            return 'rule13_being_overtaken'          # they overtake us -> we stand on
        rb_me = _relative_bearing_of_me_from_target(own_cog, tgt_cog, rb)
        if ABAFT_STBD < rb_me < ABAFT_PORT and own_sog > tgt_sog:
            return 'rule13_overtaking'               # we overtake them -> we give way

    # --- Rule 14: reciprocal courses AND target roughly ahead ---
    if cdiff > HEADON_COURSE_MIN and (rb <= HEADON_BEARING_TOL
                                      or rb >= 360.0 - HEADON_BEARING_TOL):
        return 'rule14_headon'

    # --- Rule 15: crossing ---
    if rb <= ABAFT_STBD:
        return 'rule15_giveway'                      # target to starboard
    if rb >= ABAFT_PORT:
        return 'rule15_standon'                      # target to port
    return 'no_situation'


HEADON_RULES = frozenset({'rule14_headon'})          # drives the +2 min TCPA bonus
```

**Voice phrases.** Per ADV-4, no phrase claims water is clear.

**Decision D02-6 (operator, S160):** the Rule 14 phrase is **advisory, not imperative.**
An advisory system issuing a command (*"Alter course to starboard"*) shifts liability from
the captain to the software. The phrase now states the legal requirement and leaves the
action to the captain.

```python
VOICE_PHRASES = {
    # D02-6 — advisory form. Was: 'Danger. Head-on situation. Alter course to starboard.'
    'rule14_headon':          'Danger. Head-on situation. '
                              'COLREGs require starboard alteration.',
    'rule15_giveway':         'Warning. Crossing target to starboard. You are Give-Way.',
    'rule15_standon':         'Alert. Crossing target to port. You are Stand-On. Monitor.',

    # NEW in v1.1 — replaces v1.0's inverted single 'rule13_overtake' phrase.
    # SUGGESTED REWORD — awaiting approval. These two are the only remaining
    # imperatives ("Hold course and speed", "Keep clear") and D02-6's liability
    # reasoning applies to them identically. Proposed advisory forms:
    #   rule13_being_overtaken: 'Alert. Vessel overtaking from astern. You are
    #                            Stand-On. COLREGs require you to hold course and speed.'
    #   rule13_overtaking:      'Warning. You are overtaking. You are Give-Way.
    #                            COLREGs require you to keep clear.'
    # NOT APPLIED — operator ruled on Rule 14 only. Do not substitute silently.
    'rule13_being_overtaken': 'Alert. Vessel overtaking from astern. '
                              'You are Stand-On. Hold course and speed.',
    'rule13_overtaking':      'Warning. You are overtaking. You are Give-Way. Keep clear.',

    'critical':               'Critical collision risk. Target {bearing}. CPA {cpa_m} metres.',
}
```

> **SUGGESTION** — apply D02-6's reasoning to the two Rule 13 phrases above, which are the
> only remaining imperatives. They are new in v1.1 and have never been approved in any
> form, so there is no legacy wording to preserve. **Apply the proposed advisory forms?**

### 8.5 CPA engine and alert state machine

The v1.0 CPA geometry is **correct** and is kept: `tcpa = −(r·v)/|v|²`, `cpa = |r + v·tcpa|`,
flat-earth conversion with `m_per_deg_lon = 111320·cos(lat)`, velocity components
`v_east = sog·sin(cog)`, `v_north = sog·cos(cog)`. The defects were in the guards and the
downstream use, not the formula.

```python
# cpa_engine.py
import math

KTS_TO_MS = 0.514444
M_PER_DEG_LAT = 111320.0


def compute_cpa_tcpa(own_lat, own_lon, own_sog, own_cog,
                     tgt_lat, tgt_lon, tgt_sog, tgt_cog):
    """(cpa_m, tcpa_s, range_m). tcpa_s < 0 => already passed. inf => no relative motion.

    Flat-earth approximation; valid well inside the 2 NM gating range of §8.2.
    """
    m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(own_lat))
    dx = (tgt_lon - own_lon) * m_per_deg_lon      # metres east
    dy = (tgt_lat - own_lat) * M_PER_DEG_LAT      # metres north
    range_m = math.hypot(dx, dy)

    ovx = own_sog * KTS_TO_MS * math.sin(math.radians(own_cog))
    ovy = own_sog * KTS_TO_MS * math.cos(math.radians(own_cog))
    tvx = tgt_sog * KTS_TO_MS * math.sin(math.radians(tgt_cog))
    tvy = tgt_sog * KTS_TO_MS * math.cos(math.radians(tgt_cog))
    rvx, rvy = tvx - ovx, tvy - ovy
    v2 = rvx * rvx + rvy * rvy

    if v2 < 1e-9:
        # No relative motion: range is constant. Return inf so the gate rejects it
        # rather than treating a fixed separation as an imminent CPA.
        return range_m, float('inf'), range_m

    tcpa = -(dx * rvx + dy * rvy) / v2
    if tcpa < 0.0:
        # Already passed: the geometric CPA is historical. Report present range as CPA
        # so a receding target cannot hold an alert open on an old closest distance.
        return range_m, tcpa, range_m
    cpa = math.hypot(dx + rvx * tcpa, dy + rvy * tcpa)
    return cpa, tcpa, range_m
```

> **v1.0 defect:** the stationary branch returned `float('inf')` for TCPA, and the clear
> condition was `if self.cpa > 500 and self.tcpa < 0`. `inf < 0` is False, so a target with
> no relative motion **could never clear** — a permanent alert. Separately, v1.0 computed
> `cpa` using a *negative* tcpa, yielding a historical closest distance that could stay
> under 500 m indefinitely for a receding target, also never clearing. Both closed: the
> gate rejects `inf` and negative TCPA, and clearing is now driven by the gate.

```python
# alert_manager.py
import time
from enum import Enum

class AlertState(Enum):
    ACTIVE_UNACKED     = 1
    ACKNOWLEDGED_MUTED = 2
    CLEARED            = 3


class SafeHelmAlertManager:
    """Per-target alert lifecycle. One instance per MMSI.

    Based on the operator-supplied state machine (S159). Three changes, all
    required by policy D02-4 or by a defect in the original:
      1. per-target gap 15s -> 60s   (D02-4; the 15s cap is now global)
      2. 20% degradation measured against CPA *at acknowledgement*, not the
         previous tick -- at 1 Hz the original needed a 20% drop inside one
         second, so the re-trigger effectively never fired
      3. clearing driven by the gate returning None, with hysteresis, instead of
         'cpa > 500 and tcpa < 0' which could never be satisfied (see above)
    """

    PER_TARGET_MIN_GAP_S = 60.0
    SNOOZE_TIMEOUT_S     = 120.0
    DEGRADE_FRACTION     = 0.80
    CLEAR_HYSTERESIS     = 3

    def __init__(self, target_id, cpa, tcpa, bearing, rule_id, tier):
        self.target_id = target_id
        self.cpa, self.tcpa, self.bearing = cpa, tcpa, bearing
        self.rule_id, self.tier = rule_id, tier
        self.state = AlertState.ACTIVE_UNACKED
        self.ack_time = None
        self.cpa_at_ack = None
        self.last_audio_played = 0.0
        self._ungated_ticks = 0
        self._preempt = False

    def update_metrics(self, cpa, tcpa, tier):
        """tier is alert_gate.classify_tier(...) or None."""
        self.cpa, self.tcpa = cpa, tcpa

        if tier is None:
            self._ungated_ticks += 1
            if self._ungated_ticks >= self.CLEAR_HYSTERESIS:
                self.state = AlertState.CLEARED
            return
        self._ungated_ticks = 0

        escalated = tier['tier'] == 'critical' and self.tier != 'critical'
        self.tier = tier['tier']

        if escalated:
            # D02-5: a fresh Critical wins queue insertion immediately, even if
            # another target is mid-acknowledgement. One-shot; cleared on speaking.
            self._preempt = True
            self.last_audio_played = 0.0        # also bypasses the per-target cap

        if self.state is AlertState.ACKNOWLEDGED_MUTED:
            snoozed_out = time.time() - self.ack_time > self.SNOOZE_TIMEOUT_S
            degraded = (self.cpa_at_ack is not None
                        and self.cpa < self.cpa_at_ack * self.DEGRADE_FRACTION)
            if snoozed_out or degraded or escalated:
                self.state = AlertState.ACTIVE_UNACKED

    def execute_ui_acknowledgement(self):
        """D02-5: clears ONLY this target's audio segment. Never touches another target."""
        self.state = AlertState.ACKNOWLEDGED_MUTED
        self.ack_time = time.time()
        self.cpa_at_ack = self.cpa
        self._preempt = False

    def wants_audio(self) -> bool:
        """True if this target is eligible to speak. The global arbiter decides who does."""
        if self.state is not AlertState.ACTIVE_UNACKED:
            return False
        if self.tier == 'advisory':
            return False                        # Tier 1 is visual only (D02-3)
        if self._preempt:
            return True                         # D02-5 preemption ignores the per-target cap
        return time.time() - self.last_audio_played > self.PER_TARGET_MIN_GAP_S

    def preempts(self) -> bool:
        return self._preempt

    def mark_spoken(self):
        self.last_audio_played = time.time()
        self._preempt = False                   # one-shot
```

### 8.6 Phase feature flag — SH-15

Unchanged in intent from v1.0: Phase 2 code does not execute, so the SH-15 whitelist is
never required. **No compile-time bypass and no stub returning `true`** (see §3).

```python
SAFEHELM_PHASE = int(os.environ.get('SAFEHELM_PHASE', '1'))

def initialize_system():
    boot_cpa_engine()
    boot_colregs_classifier()
    boot_alert_gate()
    boot_signalk_consumer()          # ws://<host>:8099/signalk/v1/stream
    boot_voice_arbiter()
    initialize_shadow_logger()
    boot_voice_client()              # Advisory output — in scope (D02-1)
    boot_widget_sse_server()         # Advisory output — in scope (D02-1)
    announce_advisory_role()         # ADV-2

    if SAFEHELM_PHASE < 2:
        logger.info('SafeHelm Advisory Mode. No Signal K write path; SH-15 not engaged.')
        return

    if not verify_signalk_transmit_whitelist():
        logger.critical('SH-15 not satisfied: transmitPGNs whitelist missing. '
                        'Refusing to start Phase 2. Service will stay in Advisory Mode.')
        return                       # degrade to Advisory — do NOT exit
    boot_synthetic_ais_injector()
```

> **v1.0 defect:** `raise SystemExit(...)` on an SH-15 violation, paired with
> `Restart=always` + `RestartSec=10` — a misconfiguration becomes a permanent restart loop.
> BUG-105 again. Now it logs `critical` and stays in Advisory Mode: the boat keeps its
> collision advisory instead of losing the whole service to a config error.

`d3kos-safehelm.service`
```ini
[Unit]
Description=d3kOS SafeHelm — Collision Avoidance Advisory
After=network-online.target d3kos-ai-bridge.service
Wants=d3kos-ai-bridge.service
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
WorkingDirectory=/opt/d3kos/services/safehelm
ExecStart=/opt/d3kos/venv/bin/python safehelm.py
Environment=SAFEHELM_PHASE=1
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=10
User=d3kos

[Install]
WantedBy=multi-user.target
```
`PYTHONUNBUFFERED=1` — required for any Python systemd service using `print()` (BUG-54).
The Signal K unit is **not** listed in `After=`: its unit name is unverified (§10), and
`signalk_client` reconnects with backoff regardless.

### 8.7 Widget overlay

> **v1.0 gap — this could not have worked.** `safehelm-widget.js` is served from the
> dashboard on `:3000` but subscribed to SSE on `:8095`. That is cross-origin; the browser
> would have blocked it. v1.0 did not mention CORS.

**Fix:** SafeHelm binds `127.0.0.1:8095` and the dashboard proxies. Same origin, no CORS,
nothing on 8095 reachable from the boat network.

| Browser calls (dashboard :3000) | Dashboard proxies to |
|---|---|
| `GET /api/safehelm/events` (SSE) | `http://127.0.0.1:8095/widget/events` |
| `POST /api/safehelm/alert/<mmsi>/ack` | `http://127.0.0.1:8095/alert/<mmsi>/ack` |
| `POST /api/safehelm/alert/<mmsi>/dismiss` | `http://127.0.0.1:8095/alert/<mmsi>/dismiss` |

`<mmsi>` is validated as exactly 9 digits before proxying; anything else is 400.

> **v1.0 gap — no authentication, no bind address.** `POST /alert/{id}/ack` on 8095 with an
> unspecified bind meant anyone on the boat Wi-Fi could silence a collision alarm. Closed:
> loopback bind plus the dashboard's existing session auth.

Layout (operator wireframe), with the §1 footer added:
```
+======================================================+
| [severity] (COLREG RULE nn: [situation])             |
+------------------------------------------------------+
| Target: MMSI    | CPA: n m     | Bearing: nnn deg [D]|
| Role: [role]    | TCPA: n m n s| SOG: n.n kts        |
+------------------------------------------------------+
| RECOMMENDATION: [action]                             |
+------------------------------------------------------+
| [ ACKNOWLEDGE & SILENCE (120s) ]  |  [ DISMISS ]     |
+------------------------------------------------------+
| Advisory only - AIS targets only. Captain remains    |
| responsible for lookout and navigation.        ADV-1 |
+======================================================+
```

| State | Border | Flash | Layout |
|---|---|---|---|
| `ACTIVE_UNACKED` Critical | `#FF0000` | 2 Hz | Expanded |
| `ACTIVE_UNACKED` Warning | `#FF0000` | 2 Hz | Expanded |
| `ACKNOWLEDGED_MUTED` | `#FFBF00` solid | none | Minimised |
| Tier 1 Advisory | `#FFBF00` solid | none | Minimised, **no voice** |

**AODA — not optional, and v1.0 specified no sizes at all.** Minimum 18px on every element
including the MMSI, the units and the ADV-1 footer; header and CPA/TCPA values ≥22px;
ACK and DISMISS ≥48×48px with ≥8px separation. The widget is ~320px tall on the 7"
touchscreen at these sizes — **that is the correct outcome, not a reason to shrink text.**
The 2 Hz flash is `border-color` only; no opacity or transform animation, and it must not
be applied to text (seizure risk and legibility).

---

## 9. Requirements Traceability

v1.0 cited spec section ranges but had no REQ-ID mapping, which is how REQ-HCD-027 came to
be missed. This matrix is the coverage evidence.

| Requirement | Design section | Status |
|---|---|---|
| REQ-HCD-009 HAT probed at boot + each scheduled re-probe | §5 HCD-1 + timer | Covered |
| REQ-HCD-020 udev attach/detach, no polling | §5 HCD-2 | Covered |
| REQ-HCD-026…028 scheduled re-probe every 15 min | §5 HCD-1 `.timer` | **Added in v1.1** |
| REQ-HCD-050 manifest at `config/capabilities-manifest.json` | §5 HCD-3 | Covered |
| ADV-1…ADV-4 advisory role | §1, §8.4, §8.7 | **New in v1.1** |
| D02-3 gating matrix | §8.2 | **New in v1.1** |
| D02-4 rate caps | §8.3 | **New in v1.1** |
| SH-15 Phase 2 gate | §8.6 | Covered |

**Outstanding:** the remaining REQ-HCD IDs in HCD-REQ-001 (97 total) are not yet
individually mapped. **Complete this matrix before HCD-1 implementation starts** — it is
the only mechanism that proves coverage, and it already caught one miss.

---

## 10. Test Specifications

TDD, per the Master Standard: these are written and failing before the code.

### 10.1 `test_colregs_classifier.py` — catches both v1.0 safety defects

| Case | Input | Expected | Catches |
|---|---|---|---|
| C1 | own 090/10kt, tgt 090/12kt, rb 180 | `rule13_being_overtaken` | v1.0 said give-way while stand-on |
| C2 | own 090/12kt, tgt 090/8kt, rb 000 | `rule13_overtaking` | v1.0 said `rule15_giveway` |
| C3 | own 090, tgt 270, rb 000 | `rule14_headon` | **v1.0 returned crossing** |
| C4 | own 090, tgt 095, rb 045 | **not** `rule14_headon` | **v1.0 returned head-on for same-course vessels** |
| C5 | own 000, tgt 270, rb 045 | `rule15_giveway` | starboard crossing |
| C6 | own 000, tgt 090, rb 315 | `rule15_standon` | port crossing |
| C7 | rb 113.0, equal SOG | `no_situation` | no Rule 13 without a speed differential |

### 10.2 `test_alert_gate.py`

| Case | Input | Expected | Catches |
|---|---|---|---|
| G1 | cpa 100, tcpa 120, range 900 | `critical` | |
| G2 | cpa 250, tcpa 300, range 2000 | `warning` | |
| G3 | cpa 450, tcpa 540, range 3500 | `advisory`, `voice is None` | Tier 1 must be silent |
| G4 | cpa 100, tcpa **−180**, range 900 | `None` | **lower-bound defect in the supplied policy** |
| G5 | cpa 100, tcpa `inf`, range 900 | `None` | v1.0 stationary-target permanent alert |
| G6 | cpa 250, tcpa 480, range 2000, `is_headon=True` | `warning` | +2 min head-on bonus |
| G7 | cpa 250, tcpa 480, range 2000, `is_headon=False` | `None` | bonus not applied otherwise |
| G8 | cpa 100, tcpa 120, range **4000** | `None` | range must gate independently |

### 10.3 `test_cpa_engine.py`

| Case | Scenario | Expected |
|---|---|---|
| P1 | Head-on, 1 NM apart, 10 kt each | cpa ≈ 0, tcpa ≈ 180 s |
| P2 | Parallel, same course/speed, 500 m abeam | tcpa `inf`, cpa 500 |
| P3 | Target has passed, opening | tcpa < 0, cpa == range |
| P4 | Perpendicular crossing, known geometry | cpa within 1 % of hand calculation |
| P5 | Longitude scaling at lat 45° | dx uses `111320·cos45`, ±0.1 % |

### 10.4 `test_feature_gate.py`

| Case | Profile | Manifest | Expected | Catches |
|---|---|---|---|---|
| F1 | Coral fitted | requires `["hailo-8l"]` | `False` | **v1.0 fail-open returned True** |
| F2 | Hailo-8L fitted | requires `["hailo-8l"]` | `True` | |
| F3 | none fitted | `accelerator_any: true` | `False` | |
| F4 | Coral fitted | `accelerator_any: true`, no whitelist | `True` | |
| F5 | `ram_mb` 3790 | `ram_mb_min` 3500 | `True` | **v1.0 truncation locked 4 GB Pi** |
| F6 | `ram_mb` 7900 | `ram_mb_min` 7500 | `True` | v1.0 read 8 GB as 7 |
| F7 | profile deleted | any | `False` + reason string | must fail closed |
| F8 | profile replaced on disk | — | new value without restart | cross-process mtime reload |

### 10.5 Integration gates

| Item | Gate | Method |
|---|---|---|
| HCD-1 | valid JSON; `jq . ` exits 0; `ram_mb` matches `/proc/meminfo` | `d3kos-probe && jq . $PROFILE` |
| HCD-1 timer | probe runs within 16 min unattended | `systemctl list-timers d3kos-hardware-probe` |
| HCD-2 | profile updates ≤5 s of plug; udev worker not blocked | plug test device; `udevadm monitor` |
| HCD-4 | page renders; all text ≥18px | browser + computed-style check (never CSS tokens — S115) |
| HCD-5 | Setup Description is final wizard screen; inline re-probe works | first-boot walkthrough |
| SK-FW-1 | `npm pack --dry-run` lists `yolov8n.onnx`; plugin runs with NIC down | pack + offline test |
| SK-FW-2a | plugin enables in Signal K admin UI | browser + `journalctl` |
| D16 gate | load < 3.0, temp < 80 °C, both bow-camera consumers stable, 10 min | `top`, `vcgencmd measure_temp` |
| D16 toggle | iframe swaps; engine/nav ribbons unaffected; no `localhost` literal | browser + BUG-48 guard test |
| D02 voice | Tier 2 speaks once; Tier 1 silent; 30-target sim respects both caps | LAB-SIM scenario |
| D02 ACK | mutes, goes amber static, re-fires at 120 s, other targets still queued | browser on Pi |
| D02 ADV | startup announcement plays; ADV-1 footer always visible | browser + audio |

**Verification must be UI-level.** `curl` is not verification — repeated operator
instruction. Every browser-facing gate above needs a Playwright assertion.

---

## 11. Open Items

All four v1.1 decisions were ruled by the operator in S160 and are now closed — see §2
(D02-5, D02-6, D17-1) and §2.1 (SH-11 superseded, applied to the checklist).

| Item | Needed for | Action |
|---|---|---|
| **Rule 13 phrasing** | ADV alignment | Operator choice: apply D02-6's advisory form to the two Rule 13 phrases? (§8.4 SUGGESTION) |
| **Critical preemption scope** | D02 safety | Confirm the D02-5 reading: Critical bypasses the 15 s global gap, or priority-order only? (§8.3) |
| Signal K systemd unit name | SK-FW-2a, D02 | Read on lab Pi: `systemctl list-units '*signalk*'`. Not guessed. |
| go2rtc default port map | D16 | Verify against the pinned go2rtc README before deploy (§7.3) |
| Bow camera height above waterline | D16 rings | Tape measure at next boat visit. 1.35 m default, rings labelled *"Estimated"* until then |
| Bow camera sub-stream URL | D16 | Already in `hardware.json`; `configure-go2rtc.sh` resolves it |
| YOLOv8 AGPL-3.0 redistribution | D05 publish | Licence read before `npm publish` (§6.1) |
| Remaining REQ-HCD ID mapping | D17 | Complete §9 matrix before HCD-1 starts |

---

---

## 12. Defect Closure — no BUG entry, guard tests instead

**Operator ruling S160:** *"the bug entry — let's not create more bugs, but have a solution
for this one prior to implementing it."*

**No BUG number is assigned.** The v1.0 defects were caught in design review, before any
code existed, on any platform. Nothing was deployed and nothing regressed. Logging a BUG
would add a record without adding a control. The bug tracker stays for defects found in
running software.

**What replaces it:** each defect is closed by a named test that must exist and **fail**
before the corresponding implementation is written. A defect with a failing guard test is
closed; a defect with only a corrected document is not.

| v1.0 defect | Closed by | Guard test | Gate |
|---|---|---|---|
| Rule 14 fired on same-course vessels, never on head-on | §8.4 `course_diff > 165` | `test_colregs_classifier.py::C3`, `::C4` | Must fail before `colregs_classifier.py` exists |
| Rule 13 role inverted — advised give-way while stand-on | §8.4 split into `being_overtaken` / `overtaking` | `::C1`, `::C2` | Must fail before `colregs_classifier.py` exists |
| No alert gating — every AIS target voiced | §8.2 3-tier matrix (D02-3) | `test_alert_gate.py::G1`–`G8` | Must fail before `alert_gate.py` exists |
| Feature gate failed open on accelerator whitelist | §5 HCD-3 `_accel_ok()` | `test_feature_gate.py::F1` | Must fail before `d3kos_feature_gate.py` exists |
| `ram_gb` truncation — 8 GB Pi read as 7 | §5 HCD-1 `ram_mb` | `::F5`, `::F6` | Must fail before `hardware-probe.sh` exists |
| Signal K port written as 3000 | §8 header — **8099** (BUG-46) | `test_safehelm_config.py::S1` asserts no `:3000` in any SK URL | Must fail before `signalk_client.py` exists |
| Stationary target could never clear | §8.5 gate rejects `inf` / negative TCPA | `::G4`, `::G5`, `test_alert_manager.py::M4` | Must fail before `alert_manager.py` exists |
| 20 % re-trigger measured against previous tick | §8.5 `cpa_at_ack` | `test_alert_manager.py::M2` | Must fail before `alert_manager.py` exists |
| `Restart=always` + hard exit → restart loop | §7.3, §8.6 `on-failure` + `StartLimitBurst` | `test_units.py::U1` greps both units | Must fail before either unit ships |
| `0.0.0.0` binds, camera creds world-readable | §7.3, §8.7 loopback + `chmod 600` | `test_units.py::U2`, `::U3` | Must fail before `configure-go2rtc.sh` ships |
| Hardcoded `localhost` in front-end (BUG-48) | §7.4 `window.location.hostname` | existing `bug48-no-hardcoded-localhost.spec.ts` | Already in the suite — must stay green |

### 12.1 Pre-implementation gate — blocks the first line of D17 code

All of the following must be true before any implementation file in §5–§8 is created:

1. Every test file in §10 exists and runs.
2. Every case in the tables above **fails** for the right reason (assertion failure, not
   import error). A test that errors out proves nothing.
3. `./tests/run-all.sh` executes them — it is the only trusted runner; per-suite green
   counts have historically been subsets.
4. §9's traceability matrix is completed for the remaining REQ-HCD IDs.

Only then does D17 implementation begin. This is the "solution prior to implementing"
the operator required, made checkable.

> **Why this gate and not a BUG row:** every one of the eleven defects above is mechanically
> detectable. Two of them — the COLREGs inversions — would have shipped wrong right-of-way
> advice to a captain, which §1 identifies as the worst outcome this system can produce.
> A document correction does not prevent recurrence; a failing test does.

---

*End of V09995-SOL-001 v1.2 — APPROVED for implementation, subject to §12.1.*
*Implementation order: D17 → D05 → D16 → D02. Tests in §10 precede code.*
