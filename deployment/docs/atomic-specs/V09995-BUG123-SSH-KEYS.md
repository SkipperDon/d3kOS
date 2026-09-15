# BUG-123 — SSH Host Keys Missing After Imaging · Atomic Spec

**Document:** V09995-BUG123-001 · **Version:** 1.0 · **Date:** 2026-09-15 (S164)
**Author:** Tier 2 (Sonnet) · **Implementer:** Tier 3 (qwen2.5-coder:7b)
**Bug severity:** Medium — SSH inaccessible on first boot until operator manually runs ssh-keygen -A
**Root cause confirmed:** S164 — code read of first-boot-setup.sh and sanitize.sh

---

## 1. Root Cause (confirmed from code)

`sanitize.sh` STEP 9 strips SSH host keys (lines 161-163) with comment:
```bash
# SSH host keys will be regenerated on first boot
rm -f /etc/ssh/ssh_host_*
```

`first-boot-setup.sh` runs on first boot but has **no `ssh-keygen -A` step**.
The comment promised something the script never delivered. Result: every imaged Pi
has no SSH host keys until an operator manually runs `sudo ssh-keygen -A && systemctl start ssh`.

Lab workaround applied S160: manual `sudo ssh-keygen -A`. This spec eliminates the need.

---

## 2. Files Changed

| # | File | Op | Description |
|---|------|----|-------------|
| 1 | `deployment/v0.9.9.4/opt/d3kos/scripts/first-boot-setup.sh` | modify | Add ssh-keygen -A step after filesystem expand |
| 2 | `deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh` | modify | Update comment lines 161-163 to accurately reflect fix |

Fix goes in v0.9.9.4 tree (bug fix, not new feature).

---

## 3. Exact Change — first-boot-setup.sh

Find the section that marks first-boot complete (near `touch /opt/d3kos/.first-boot-complete`).
Insert **before** the `touch` command:

```bash
# Regenerate SSH host keys stripped during image prep (BUG-123)
if ! ls /etc/ssh/ssh_host_*_key > /dev/null 2>&1; then
    ssh-keygen -A
    systemctl restart ssh 2>/dev/null || true
fi
```

**Why the guard:** `ssh-keygen -A` is a no-op if keys already exist, but the `if` guard
makes the intent explicit and prevents double-generation on re-runs.

**Why `systemctl restart ssh`:** Key files exist on disk but sshd loaded with no keys;
restart picks them up. `|| true` prevents failure if ssh isn't running yet.

---

## 4. Exact Change — sanitize.sh

Lines 161-163 currently read:
```bash
# SSH host keys will be regenerated on first boot
rm -f /etc/ssh/ssh_host_*
```

Update comment to:
```bash
# SSH host keys stripped here; first-boot-setup.sh regenerates them via ssh-keygen -A (BUG-123 fix)
rm -f /etc/ssh/ssh_host_*
```

This is documentation-only — the `rm -f` line is correct and stays unchanged.

---

## 5. Guard Test

File: `tests/test_bug123_ssh_keys.py`

```
test_ssh_keygen_called_when_keys_missing:
  - Precondition: /etc/ssh/ssh_host_*_key does not exist (simulate with tmpdir)
  - Assert: ssh-keygen -A is called (mock subprocess.run)

test_ssh_keygen_skipped_when_keys_present:
  - Precondition: at least one ssh_host_*_key file exists
  - Assert: ssh-keygen -A is NOT called

test_first_boot_marker_still_created:
  - The first-boot-complete marker file must be created regardless of ssh key state
```

Minimum bar: all 3 pass before BUG-123 is marked done.

---

## 6. Dispatch Block for Tier 3

```
TASK: BUG-123 — SSH Host Keys Fix
IMPLEMENTER: Tier 3 (qwen2.5-coder:7b)

DELIVERABLES:

1. Modify deployment/v0.9.9.4/opt/d3kos/scripts/first-boot-setup.sh
   - Find the line: touch /opt/d3kos/.first-boot-complete
   - Insert BEFORE it (spec §3 verbatim):
       # Regenerate SSH host keys stripped during image prep (BUG-123)
       if ! ls /etc/ssh/ssh_host_*_key > /dev/null 2>&1; then
           ssh-keygen -A
           systemctl restart ssh 2>/dev/null || true
       fi
   - Do not change any other part of the file

2. Modify deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh
   - Find the comment: # SSH host keys will be regenerated on first boot
   - Replace only the comment line (not the rm -f line) with:
       # SSH host keys stripped here; first-boot-setup.sh regenerates them via ssh-keygen -A (BUG-123 fix)
   - The rm -f /etc/ssh/ssh_host_* line stays EXACTLY as-is

3. Create tests/test_bug123_ssh_keys.py
   - Three test functions from spec §5
   - Mock subprocess.run and file existence checks
   - All three must pass

PRE-FLIGHT: Before writing, read lines 155-170 of sanitize.sh and confirm
the comment text matches what spec §4 says. If it differs, report the
actual text before making any change.

VERIFICATION:
[ ] ssh-keygen -A block is BEFORE the touch .first-boot-complete line
[ ] Guard condition prevents re-run on existing keys
[ ] sanitize.sh rm -f line is unchanged
[ ] All 3 tests pass
```
