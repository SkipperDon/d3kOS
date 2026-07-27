# Atomic Spec — BUG-39 (cloning the master duplicates the Pi's identity)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5) · **Revised same session** — operator answered
Q39.1 and Q39.2, and Q39.3 was resolved by investigation. **This spec is now complete, not partial.**
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-39 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q39.1–Q39.5 first**
**Blocks:** putting the cloned card in the boat.

---

## Operator decisions (binding)

| Item | Decision | Action |
|---|---|---|
| `installation_id` / `license.json` | **per OWNER** | **PRESERVE EXACTLY** — never write this file |
| `device_token` | **the boat gets a NEW one** | **REGENERATE** — fresh UUID4 on the clone |

## Scope correction — Signal K vessel UUID is OUT

The original entry listed the SK vessel UUID as a duplicated identity. Investigation disproved it:
the live value `e1592142-…` appears in **no file** on the system, `serverState/` is empty,
`defaults.json` does not exist, and `settings.json` declares a *different* UUID (`af7d4be0-…`) that
Signal K is ignoring. It is therefore either runtime-generated or derived from `machine-id` — which
the script already regenerates. **Either way the correct action is to do nothing.** Removed from
scope. (The settings.json mismatch is a separate config defect, logged not fixed.)

---

## Final scope

| # | Identity | Action |
|---|---|---|
| 1 | `/etc/machine-id` (+ `/var/lib/dbus/machine-id`) | **regenerate** |
| 2 | SSH host keys (3 pairs) | **regenerate** |
| 3 | `/opt/d3kos/config/device-token.json` | **regenerate** — new UUID4 + new `created_at` |
| 4 | `/opt/d3kos/config/license.json` | **preserve** — never written |
| 5 | Signal K vessel UUID | **out of scope** — not persisted |
| 6 | Filesystem UUIDs | **out of scope** — SD Card Copier's "New Partition UUIDs" handles it; `tune2fs`/`parted`/`e2fsck` are not installed |

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-39   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-39 — first-boot identity regeneration for a cloned card

FILES TO CREATE (exactly two, both NEW)
  deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh
  deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service

WHY THIS EXISTS
  A clone of the master SD card carries the source Pi's identity. Two Pis sharing
  one device_token collide in the atmyboat.com fleet database (amboat_devices).
  This script runs ONCE on a freshly cloned card and gives it its own identity.

REGENERATE — these three
  1. /etc/machine-id  (and /var/lib/dbus/machine-id if that path exists)
  2. SSH host keys: /etc/ssh/ssh_host_*_key and .pub  (3 pairs currently present)
  3. /opt/d3kos/config/device-token.json

PRESERVE — never write this
  4. /opt/d3kos/config/license.json
     installation_id is PER OWNER (operator decision Q39.1). Rewriting it would
     strip the boat of its T3 entitlement. The script must not open it for
     writing at all. Printing its installation_id to the log is fine.

OUT OF SCOPE — do not attempt
  • The Signal K vessel UUID. It is not persisted on disk (Q39.3). Do NOT search
    for it, do NOT edit any file under ~/.signalk.
  • Filesystem/partition UUIDs. Do NOT use tune2fs, fatlabel or mlabel — none are
    installed, and the operator handles this via SD Card Copier (Q39.5).

device-token.json CONTRACT
  Current schema is exactly two keys:
      { "device_token": "701e5754-e2ce-4fa3-97a6-f2c7c7e020c6",
        "created_at":   "2026-03-26T13:37:23.752409Z" }
  After regeneration:
      device_token : a NEW random UUID4, lowercase, hyphenated, different from the old one
      created_at   : regeneration time, UTC, ISO-8601 with microseconds and a trailing Z
      No other keys added. File ownership and mode preserved (currently d3kos:d3kos 0664).
  Generate the UUID with `cat /proc/sys/kernel/random/uuid` (always present on Linux —
  do NOT depend on uuidgen, which may not be installed).
  Write the JSON with python3, NOT with sed/echo — a malformed device-token.json
  breaks cloud_agent at startup.

BEHAVIOUR CONTRACT
  • Sentinel FIRST: if /opt/d3kos/config/.identity-regenerated exists -> print
    "identity already regenerated, nothing to do" and exit 0, changing nothing.
  • Otherwise: perform items 1-3, then CREATE the sentinel as the LAST action.
    If any step fails, do NOT create the sentinel (so a re-run can retry).
  • The sentinel is deleted by the CLONING procedure, not by this script (Q39.4).
  • Back up the old device-token.json to device-token.json.pre-regen before writing.
  • Log every action, old value and new value to
    /var/log/d3kos-identity-regen.log AND stdout.
  • Require root: if EUID != 0, print an error and exit 1.
  • Idempotent: a second run is a no-op via the sentinel.
  • Use `set -u`. Do NOT use `set -e` — a failed optional step must be reported,
    not abort the run silently.
  • Never delete the old SSH keys until the new ones are confirmed written.

SYSTEMD UNIT CONTRACT
  [Unit]
    Description=d3kOS first-boot identity regeneration (BUG-39)
    After=local-fs.target
    Before=  the d3kOS services and signalk
    ConditionPathExists=!/opt/d3kos/config/.identity-regenerated
  [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/opt/d3kos/services/identity/regenerate-identity.sh
  [Install]
    WantedBy=multi-user.target
  READ an existing unit in deployment/v0.9.9.4/etc/systemd/system/d3kos-*.service
  first and match its style and its service naming.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT write license.json. Read/print only.
  • Do NOT touch anything under ~/.signalk.
  • Do NOT use tune2fs / fatlabel / mlabel.
  • Do NOT enable, start, install or otherwise run the unit anywhere.
  • Do NOT RUN THE SCRIPT. It deletes SSH host keys and rewrites the device
    identity. Running it on the lab Pi would damage the master (Q0.2).
  • Do NOT edit any existing file. Both deliverables are new.
  • Do NOT regenerate MANIFEST.md5 (Q0.4).

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/test_bug39_identity_regen.py      (pytest — static analysis only)
  Run : python3 -m pytest tests/test_bug39_identity_regen.py -v
  These tests assert on the SOURCE. They must never execute the destructive paths;
  real behaviour can only be validated by booting a throwaway clone (operator step).

    import pathlib, re, subprocess, pytest

    SH   = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh')
    UNIT = pathlib.Path('deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service')

    def test_files_exist():
        assert SH.exists() and UNIT.exists()

    def test_shebang_and_executable():
        assert SH.read_text().startswith('#!')
        assert SH.stat().st_mode & 0o111, 'must be chmod +x'

    def test_bash_syntax_ok():
        r = subprocess.run(['bash', '-n', str(SH)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def test_sentinel_guard_is_first_logic():
        body = [l for l in SH.read_text().splitlines()
                if l.strip() and not l.strip().startswith('#')]
        head = '\n'.join(body[:15])
        assert '.identity-regenerated' in head, 'sentinel check must come first'

    def test_regenerates_the_three():
        s = SH.read_text()
        assert 'machine-id' in s
        assert 'ssh-keygen' in s
        assert 'device-token.json' in s
        assert '/proc/sys/kernel/random/uuid' in s, 'use the kernel UUID source'

    def test_license_json_is_never_written():
        """installation_id is per-owner — license.json must be read-only here."""
        for line in SH.read_text().splitlines():
            if 'license.json' in line and not line.strip().startswith('#'):
                assert not re.search(r'(>\s*\S*license\.json|>>|sed -i|tee\s+\S*license\.json'
                                     r'|rm\s+\S*license\.json|mv\s+\S*license\.json)', line), \
                    f'license.json must never be written: {line.strip()}'

    def test_signalk_untouched():
        s = SH.read_text()
        assert '.signalk' not in s, 'SK vessel UUID is out of scope (Q39.3)'

    @pytest.mark.parametrize('tool', ['tune2fs', 'fatlabel', 'mlabel'])
    def test_no_filesystem_uuid_tools(tool):
        assert tool not in SH.read_text()

    def test_backs_up_before_rewriting_token():
        assert 'pre-regen' in SH.read_text(), 'must back up device-token.json first'

    def test_writes_json_with_python_not_echo():
        s = SH.read_text()
        assert 'python3' in s, 'device-token.json must be written via python3, not echo/sed'

    def test_requires_root():
        assert re.search(r'EUID|id -u', SH.read_text()), 'must refuse to run as non-root'

    def test_unit_contract():
        u = UNIT.read_text()
        for needed in ('Type=oneshot', 'RemainAfterExit=yes',
                       'ConditionPathExists=!/opt/d3kos/config/.identity-regenerated',
                       'ExecStart=/opt/d3kos/services/identity/regenerate-identity.sh',
                       'WantedBy=multi-user.target'):
            assert needed in u, f'unit missing: {needed}'

  EXPECTED BEFORE THE FIX: test_files_exist fails — neither file exists.

DONE WHEN
  • All tests FAILED before and PASS after. `bash -n` clean. Script is chmod +x.
  • git diff adds exactly the two new files plus the test file. Nothing else.
  • You have NOT executed the script.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • You think license.json must change to make the clone work
                                   → ADVICE. It must not. installation_id is per-owner.
  • The existing d3kos-*.service style conflicts with the unit contract
                                   → CLARIFICATION (show the conflict)
  • systemd-machine-id-setup and dbus-uuidgen both appear unavailable
                                   → SOLUTION-REQUEST (do NOT run anything to find out)
  • Anything tempts you to execute the script to test it
                                   → STOP. Never run it. Not once.

PRE-FLIGHT SELF-CHECK
  1. What do I regenerate?      → machine-id, SSH host keys, device-token.json
  2. What do I preserve?        → license.json, always
  3. Do I touch Signal K?       → no, out of scope
  4. May I run the script?      → NO, never
  5. When is the sentinel made? → last, and only if every step succeeded

RETURN TO TIER 1
  • Both new files
  • pytest output showing fail-before / pass-after
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. **`license.json` is never written.** Read the script line by line. A single `>` here silently
   revokes the boat's T3 licence. This is the highest-consequence check in the spec.
2. `device-token.json` written via `python3`, backed up first, both keys rewritten, no extra keys.
3. Nothing under `~/.signalk`; no `tune2fs`/`fatlabel`/`mlabel`.
4. Sentinel is the first logic and is created last, only on full success.
5. `bash -n` clean; `chmod +x` set.
6. **Confirm nothing was executed:** the lab Pi's SSH host key fingerprints and `device_token`
   (`701e5754-…`) must be unchanged after Tier 3's work. Check this explicitly — it is the one
   spec in this batch where a stray execution damages the master.
7. **Cannot verify remotely:** actual first-boot behaviour. Only a throwaway clone can prove it, and
   it must not be the boat card.

## Operator note carried forward

If the boat Pi is already registered on atmyboat.com under its own token, a brand-new token means it
re-registers as a new device and its prior history stays on the old record. `Uncertainty flag: S107
did not capture the boat Pi's device_token, so I cannot say whether there is history worth keeping.`
Decision implemented as instructed; consequence recorded.

## Out of scope
Pi deployment · enabling the unit · running the script · filesystem UUID regeneration · the clone
procedure itself · the `settings.json` vs live SK UUID mismatch (separate finding).
