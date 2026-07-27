# Atomic Spec — BUG-39 (cloning the master duplicates six identity values)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-39 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q39.1–Q39.5 first**
**Blocks:** putting the cloned card in the boat.

---

## ⚠ This spec is deliberately PARTIAL

Two of the six identity values cannot be specified yet — they need operator decisions that no tier
can make:

| Question | Blocks |
|---|---|
| **Q39.1** — is `installation_id` per-device or per-owner? | `license.json` — wrong guess either collides two licences or leaves the boat unlicensed |
| **Q39.2** — does a new `device_token` orphan the device's history on atmyboat.com? | `device-token.json` — wrong guess loses telemetry, tickets and PDF reports |

**Scope of THIS spec = Phase A only:** build the script skeleton, the safe regenerations, and a
*read-only report* for the two blocked values. Phase B wires in `device_token` and `license.json`
once the operator answers. Tier 3 must **not** touch either file.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-39 Phase A   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-39 Phase A — first-boot identity regeneration (safe subset)

FILES TO CREATE (exactly two, both NEW)
  deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh
  deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service

WHY THIS EXISTS
  A clone of the master SD card carries the source Pi's identity. Two Pis sharing
  one device_token collide in the atmyboat.com fleet database. This script runs
  ONCE on a freshly cloned card and gives it its own identity.

WHAT PHASE A REGENERATES (safe — decided)
  1. /etc/machine-id  (and /var/lib/dbus/machine-id if it exists)
  2. SSH host keys    (/etc/ssh/ssh_host_*_key and .pub — 3 key pairs present)

WHAT PHASE A ONLY REPORTS, NEVER CHANGES (blocked — see Q39.1 / Q39.2 / Q39.3)
  3. /opt/d3kos/config/device-token.json     ← BLOCKED, print current value only
  4. /opt/d3kos/config/license.json          ← BLOCKED, print current value only
  5. Signal K vessel UUID                    ← location unconfirmed; LOCATE and REPORT only

BEHAVIOUR CONTRACT
  • Sentinel: if /opt/d3kos/config/.identity-regenerated exists -> print
    "identity already regenerated, nothing to do", exit 0. Change nothing.
  • Otherwise: perform items 1-2, report items 3-5, then CREATE the sentinel.
  • The sentinel is deleted by the CLONING procedure, not by this script (Q39.4).
  • Log every action to /var/log/d3kos-identity-regen.log AND stdout.
  • Idempotent: running twice must be harmless.
  • Must exit 0 on success. Exit non-zero ONLY if a regeneration it attempted failed.
  • Must never delete the old SSH keys before the new ones are confirmed written.

SIGNAL K UUID — LOCATE, DO NOT GUESS (Q39.3)
  The value is urn:mrn:signalk:uuid:e1592142-4955-4b4d-a085-40fa674e0e13 (served at
  http://localhost:8099/signalk/v1/api/vessels/self/uuid). Which file holds it is
  NOT confirmed. The script must SEARCH these candidates and report which contains it:
      /home/d3kos/.signalk/settings.json
      /home/d3kos/.signalk/defaults.json
      /home/d3kos/.signalk/baseDeltas.json
  Print the file path if found, or "SK UUID location NOT FOUND - manual step required".
  DO NOT EDIT whichever file it is in. Reporting only, this phase.

SYSTEMD UNIT CONTRACT
  [Unit]
    Description=d3kOS first-boot identity regeneration (BUG-39)
    Before=  the d3kOS services and signalk
    After=local-fs.target
    ConditionPathExists=!/opt/d3kos/config/.identity-regenerated
  [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/opt/d3kos/services/identity/regenerate-identity.sh
  [Install]
    WantedBy=multi-user.target
  Match the style of the existing units in
  deployment/v0.9.9.4/etc/systemd/system/d3kos-*.service — read one first.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT modify device-token.json or license.json. Report only. Blocked on Q39.1/Q39.2.
  • Do NOT modify any Signal K file. Locate and report only.
  • Do NOT touch filesystem UUIDs (tune2fs/fatlabel). Out of scope — the operator
    handles this with SD Card Copier's "New Partition UUIDs" option. e2fsck, parted
    and tune2fs are NOT installed on this Pi anyway. Note this in the script header (Q39.5).
  • Do NOT enable, start, install or run the unit anywhere. Repo files only.
  • Do NOT run the script against the live Pi. It is destructive to host keys (Q0.2).
  • Do NOT edit any existing file. Both deliverables are new. Do NOT regenerate MANIFEST.md5.

IMPLEMENTATION NOTES
  • machine-id:  empty the file, then `systemd-machine-id-setup`; if that binary is
    absent fall back to `dbus-uuidgen > /etc/machine-id`. Detect, do not assume.
  • ssh keys:    `rm -f /etc/ssh/ssh_host_*` then `ssh-keygen -A`. Verify 3 pairs
    exist afterwards before reporting success.
  • Use `set -u` and explicit error checks. Do NOT use `set -e` — a failed optional
    step must be reported, not abort the whole run silently.
  • Require root: if EUID != 0, print an error and exit 1.

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/test_bug39_identity_regen.py       (pytest — static + dry-run only)
  Run : python3 -m pytest tests/test_bug39_identity_regen.py -v
  These tests must NEVER execute the script's destructive paths. They assert on
  the script SOURCE and on the systemd unit. That is the correct level here: the
  real behaviour can only be validated on a throwaway clone, which is an operator step.

    import pathlib, re, pytest

    SH   = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh')
    UNIT = pathlib.Path('deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service')

    def test_files_exist():
        assert SH.exists(),   'regenerate-identity.sh must exist'
        assert UNIT.exists(), 'd3kos-identity-regen.service must exist'

    def test_script_is_executable_and_has_shebang():
        assert SH.read_text().startswith('#!'), 'missing shebang'
        assert SH.stat().st_mode & 0o111, 'script must be executable (chmod +x)'

    def test_sentinel_guard_present():
        s = SH.read_text()
        assert '.identity-regenerated' in s, 'sentinel path must be used'
        assert re.search(r'exit\s+0', s), 'must exit 0 when the sentinel exists'

    def test_regenerates_the_safe_two():
        s = SH.read_text()
        assert 'machine-id' in s,  'must regenerate machine-id'
        assert 'ssh-keygen' in s,  'must regenerate SSH host keys'

    @pytest.mark.parametrize('forbidden', [
        'device-token.json',
        'license.json',
    ])
    def test_blocked_files_are_never_written(forbidden):
        """Phase A may PRINT these paths but must never write to them."""
        s = SH.read_text()
        for line in s.splitlines():
            if forbidden in line and not line.strip().startswith('#'):
                assert not re.search(r'(>|>>|tee|sed -i|mv |rm |cp .*' + re.escape(forbidden) + ')', line), \
                    f'Phase A must not write {forbidden}: {line.strip()}'

    def test_no_filesystem_uuid_tools():
        s = SH.read_text()
        for tool in ('tune2fs', 'fatlabel', 'mlabel'):
            assert tool not in s, f'{tool} is out of scope for BUG-39 Phase A'

    def test_sk_uuid_is_located_not_edited():
        s = SH.read_text()
        assert '.signalk' in s, 'must search the Signal K candidates'
        assert 'sed -i' not in s, 'must not edit any Signal K file in Phase A'

    def test_unit_contract():
        u = UNIT.read_text()
        assert 'Type=oneshot' in u
        assert 'RemainAfterExit=yes' in u
        assert 'ConditionPathExists=!/opt/d3kos/config/.identity-regenerated' in u
        assert 'ExecStart=/opt/d3kos/services/identity/regenerate-identity.sh' in u
        assert 'WantedBy=multi-user.target' in u

    def test_script_passes_shellcheck_syntax():
        import subprocess
        r = subprocess.run(['bash', '-n', str(SH)], capture_output=True, text=True)
        assert r.returncode == 0, f'bash syntax error: {r.stderr}'

  EXPECTED BEFORE THE FIX: test_files_exist fails — neither file exists yet.

DONE WHEN
  • All tests FAILED before (files absent) and PASS after.
  • `bash -n` clean. Script is chmod +x.
  • git diff adds exactly the two new files plus the test. Nothing else changes.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • You believe Phase A cannot be useful without regenerating device_token
                                     → ADVICE (it is blocked on Q39.2 — say so, do not proceed)
  • The existing d3kos-*.service files use a style that conflicts with the unit contract
                                     → CLARIFICATION (show the conflict)
  • You cannot determine how to regenerate machine-id without running it
                                     → SOLUTION-REQUEST (do NOT run it on the live Pi)
  • Anything tempts you to test by executing the script
                                     → STOP. It deletes SSH host keys. Never run it here.

PRE-FLIGHT SELF-CHECK
  1. Which files may I write?     → the 2 new files + the test. Nothing else.
  2. Do I regenerate device_token?→ NO. Blocked. Report only.
  3. Do I edit Signal K files?    → NO. Locate and report only.
  4. May I run the script?        → NO, never, not even once.
  5. What creates the sentinel?   → the script, at the END of a successful run.

RETURN TO TIER 1
  • Both new files
  • pytest output showing fail-before / pass-after
  • A note listing exactly what Phase B still needs (the blocked items)
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. `device-token.json` and `license.json` are read/printed but **never written**. Read the script
   line by line — a single `>` redirect here is a licence or fleet-identity incident.
2. No `tune2fs` / `fatlabel` / `mlabel`. No `sed -i` against any Signal K file.
3. `bash -n` clean; sentinel guard is the **first** logic in the script.
4. Confirm nothing was executed: the lab Pi's SSH host keys must be unchanged (compare fingerprints
   before/after Tier 3's work).
5. **Cannot verify remotely:** actual first-boot behaviour. That can only be validated by booting a
   throwaway clone — an operator step, and it must not be the boat card.

## Phase B — blocked, do not start

Needs operator answers to **Q39.1** (`installation_id` per-device or per-owner) and **Q39.2**
(does a new `device_token` orphan the device's history). Once answered: wire `device-token.json`,
`license.json` and the Signal K vessel UUID into the same script, extend the tests, and re-verify.

## Out of scope
Pi deployment · enabling the unit · filesystem UUID regeneration · the clone procedure itself ·
anything that runs on the live Pi.
