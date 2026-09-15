# BUG-127 — Wizard Not Triggered After Imaging · Atomic Spec

**Document:** V09995-BUG127-001 · **Version:** 1.0 · **Date:** 2026-09-15 (S164)
**Author:** Tier 2 (Sonnet) · **Implementer:** Tier 3 (qwen2.5-coder:7b)
**Bug severity:** High — first-boot wizard never fires; boat name/config from previous owner persists
**Root cause confirmed:** S164 — code read of app.py (line 231-233) and sanitize.sh

---

## 1. Root Cause (confirmed from code)

`app.py` wizard gate at line 231-233:
```python
# First-run: show onboarding wizard if vessel.env is missing
if not os.path.exists(_VESSEL_ENV_PATH):
    return redirect('/setup')
```

Gate is a **file-existence check** on `vessel.env`.

`sanitize.sh` STEP 9 removes: `onboarding-config.json`, `.first-boot-complete`, `.identity-regenerated`
but **never removes `vessel.env`**.

Result: `vessel.env` from the previous imaging session persists through `sanitize.sh`. The gate
never triggers. The wizard never fires. Every fresh image retains the previous vessel name,
owner details, and configuration.

---

## 2. Files Changed

| # | File | Op | Description |
|---|------|----|-------------|
| 1 | `deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh` | modify | Add `rm -f /opt/d3kos/config/vessel.env` to STEP 9 |

One-line fix. No other files need to change.

---

## 3. Exact Change — sanitize.sh

**Find STEP 9** in sanitize.sh. It currently removes onboarding files. Add one line:

```bash
rm -f /opt/d3kos/config/vessel.env
```

Add it immediately after the existing `rm -f /opt/d3kos/config/onboarding-config.json` line
(or wherever the other config removals are in STEP 9). The exact position within STEP 9 does
not matter — it just needs to be in the same cleanup block.

**Why this is safe:** `vessel.env` holds vessel-specific owner config (name, MMSI, etc.).
Sanitize.sh's purpose is to create a generic deployable image. Retaining vessel.env defeats
the entire purpose of sanitize.sh. This omission was always a bug, not a design choice.

---

## 4. Guard Test

File: `tests/test_bug127_wizard_trigger.py`

```
test_vessel_env_removed_by_sanitize:
  - Simulate sanitize.sh behavior: vessel.env exists in test tmpdir
  - Run sanitize cleanup logic (or assert the rm command is present in the script)
  - Assert vessel.env does NOT exist after cleanup

test_wizard_redirects_when_vessel_env_missing:
  - Flask test client: vessel.env does not exist
  - GET /
  - Assert response is 302 redirect to /setup

test_wizard_skips_when_vessel_env_present:
  - Flask test client: vessel.env exists with minimal content
  - GET /
  - Assert response is NOT a redirect to /setup (200 or redirect to dashboard)
```

Minimum bar: all 3 pass before BUG-127 is marked done.

Test #2 and #3 require Flask test client against app.py — import the app in test mode.

---

## 5. Dispatch Block for Tier 3

```
TASK: BUG-127 — Wizard Trigger Fix
IMPLEMENTER: Tier 3 (qwen2.5-coder:7b)

DELIVERABLES:

1. Modify deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh
   - Find STEP 9 (the block that removes onboarding-config.json and first-boot markers)
   - Add this line to that block:
       rm -f /opt/d3kos/config/vessel.env
   - Do NOT change any other line in the file

2. Create tests/test_bug127_wizard_trigger.py
   - Three test functions from spec §4
   - test_wizard_* tests use Flask test client: import app from
     deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py
   - All three must pass

PRE-FLIGHT: Before writing, read STEP 9 of sanitize.sh and show the
existing rm -f lines in that block. Confirm vessel.env is absent. Then
report where you will insert the new rm -f line.

CONSTRAINTS:
- Do NOT remove any other line from sanitize.sh
- Do NOT modify app.py — the wizard gate is correct as-is
- The Flask app may need VESSEL_ENV_PATH monkeypatched to tmpdir for tests

VERIFICATION:
[ ] rm -f /opt/d3kos/config/vessel.env is present in STEP 9
[ ] No other lines changed in sanitize.sh
[ ] All 3 tests pass
```
