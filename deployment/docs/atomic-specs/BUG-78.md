# ATOMIC SPEC — BUG-78

**Defect:** The image builder never invokes the sanitizer, and the sanitizer misses every credential file.
**Severity:** CRITICAL — v0.9.9.4 release gate. Delivery mechanism for BUG-66 at fleet scale.
**Tier:** Tier 1 authored this spec. **Steps 2–4 are Tier 3 implementable** (exact replacements).
Steps 1 and 6 are Tier 2. Step 0 is operator-only.
**Created:** 2026-08-24 (S131)
**Bug record:** `deployment/docs/V09994_BUG_FIXES.md` BUG-78 (read the ROOT CAUSE CORRECTED block first)

---

## 0. OPERATOR GATE — do this before any code changes

**This step is not optional and nothing below it matters if it fails.**

Mount the most recently published `d3kos-*.img.gz` from GitHub Releases and read
`/opt/d3kos/config/`. If `cloud-config.json` contains a live `AMBOAT_API_KEY`:

1. **Rotate the key** on HostPapa (`mobile/config.php`) and on every Pi.
2. **Unpublish the release.**
3. Then proceed.

If the config directory is empty or holds placeholders, record that in the bug entry and proceed.

`Uncertainty flag: no .img has been inspected. This spec cannot tell you whether exposure has already
occurred — only how to stop it recurring.`

---

## 1. PREREQUISITES — verify before editing. Abort if any check fails.

Run against the lab Pi (`192.168.1.237`). **If any line does not match, STOP and report — do not adapt.**

| # | Check | Expected |
|---|---|---|
| P1 | `test -f /opt/d3kos/scripts/create-image.sh && echo ok` | `ok` |
| P2 | `test -f /opt/d3kos/scripts/sanitize.sh && echo ok` | `ok` |
| P3 | `grep -c sanitize /opt/d3kos/scripts/create-image.sh` | `0` (the wiring gap) |
| P4 | `grep -c 'cloud-config\|api-keys\|device-token' /opt/d3kos/scripts/sanitize.sh` | `0` (the coverage gap) |
| P5 | `grep -c 'chmod 644 "$LICENSE_FILE"' /opt/d3kos/scripts/sanitize.sh` | `1` (the mode defect) |
| P6 | `find . -name create-image.sh -not -path './.git/*'` in the repo | **no output** (unsourced) |

P3–P5 are the three defects. If any is already `0`/absent, someone has partially fixed this — stop and
reconcile before proceeding.

---

## 2. STEP 1 (Tier 2) — bring the tooling under version control FIRST

Nothing is edited on the Pi only. Both scripts are production tooling with no version history (D4).

Copy from the Pi into the canonical tree, byte-identical, and commit **before** any edit so the diff of
the fix is reviewable:

```
/opt/d3kos/scripts/create-image.sh  ->  deployment/v0.9.9.4/opt/d3kos/scripts/create-image.sh
/opt/d3kos/scripts/sanitize.sh      ->  deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh
```

Verify md5 equality repo↔Pi for both, then commit with message
`S1xx: BUG-78 step 1 — bring create-image.sh + sanitize.sh under version control (no changes)`.

**Do not proceed to Step 2 until this commit exists.** If the fix goes wrong, this is the rollback point.

---

## 3. STEP 2 (Tier 3) — extend `sanitize.sh` with a credential strip

**Target:** `deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh`

### 3.1 Replacement A — fix the world-readable mode (defect D3)

`old` (exact, single occurrence — verified by P5):
```
    chown d3kos:d3kos "$LICENSE_FILE"
    chmod 644 "$LICENSE_FILE"
    log "  License file reset to defaults"
```

`new`:
```
    chown d3kos:d3kos "$LICENSE_FILE"
    chmod 600 "$LICENSE_FILE"
    log "  License file reset to defaults (mode 600 — BUG-78 D3)"
```

**Why 600, not 644:** the sanitizer was hardcoding the exact condition BUG-65 reports. A world-readable
tier claim is readable by any local process. Nothing legitimately reads `license.json` as a non-owner —
verify with Step 5 T4.

### 3.2 Replacement B — add the credential-and-identity strip (defect D2)

Insert a new step immediately **before** the license reset, so that if the script aborts partway the
secrets are already gone.

`old` (exact, single occurrence):
```
# STEP 8: Reset license.json (clear installation ID)
```

`new`:
```
# STEP 7b: Strip credentials and device identity  (BUG-78 D2)
# ==============================================================================
# These five files are secrets or per-device identity. If ANY of them survives
# into a distribution image, publishing the image publishes them. cloud-config.json
# carries the FLEET-WIDE AMBOAT_API_KEY that authenticates 12 server endpoints
# (BUG-66); subscription.key grants Tier 3 by mere existence (BUG-65);
# device-token.json is the identity BUG-39 exists to keep unique per device.
# All five are regenerated on first boot. Removing them here is safe and required.

log ""
log "STEP 7b: Stripping credentials and device identity..."

D3K_SECRETS="
/opt/d3kos/config/cloud-config.json
/opt/d3kos/config/api-keys.json
/opt/d3kos/config/device-token.json
/opt/d3kos/config/device-signing.key
/opt/d3kos/config/subscription.key
"

for f in $D3K_SECRETS; do
    if [ -e "$f" ]; then
        log "  Removing $(basename "$f")"
        rm -f "$f"
    fi
done

# Backups of secrets are secrets.
rm -f /opt/d3kos/config/*.bak
rm -f /opt/d3kos/config/*.pre-*.bak

log "  Credential strip complete"

# ==============================================================================
# STEP 8: Reset license.json (clear installation ID)
```

**Constraint — do not widen this.** Delete only the five named files plus `.bak` variants in
`/opt/d3kos/config/`. Do **not** `rm -rf` the config directory: it also holds `vessel.env`,
`timezone.txt`, `slots.json`, `hardware.json` and `cameras.json.bak`, and the last of those is marked
"never delete" in the camera-overhaul record.

---

## 4. STEP 3 (Tier 3) — wire the sanitizer into the builder and add a hard assertion

**Target:** `deployment/v0.9.9.4/opt/d3kos/scripts/create-image.sh`

### 4.1 Replacement C — invoke the sanitizer, and add a build-time assertion (defects D1 + the S129 lesson)

`old` (exact, single occurrence — this is the real cleanup block, **not** the fictional one in §12.1):
```
echo "Step 1: Pre-image cleanup..."
echo "  - Cleaning APT cache..."
apt-get clean
echo "  - Vacuuming journal logs (limit to 50MB)..."
journalctl --vacuum-size=50M
echo "  - Removing temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*
echo "  - Cleanup complete"
```

`new`:
```
echo "Step 1: Pre-image cleanup..."
echo "  - Cleaning APT cache..."
apt-get clean
echo "  - Vacuuming journal logs (limit to 50MB)..."
journalctl --vacuum-size=50M
echo "  - Removing temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*
rm -f /root/.bash_history /home/d3kos/.bash_history
echo "  - Cleanup complete"

# --- BUG-78 D1: run the sanitizer. It was never invoked before this change. ---
echo ""
echo "Step 1b: Sanitizing (SSH keys, license, credentials, identity)..."
SANITIZE="/opt/d3kos/scripts/sanitize.sh"
if [ ! -x "$SANITIZE" ]; then
    echo "FATAL: $SANITIZE missing or not executable — refusing to build an unsanitized image" >&2
    exit 1
fi
if ! "$SANITIZE" --unattended; then
    echo "FATAL: sanitize.sh failed — refusing to build" >&2
    exit 1
fi

# --- BUG-78: build-time assertion. This MUST fail the build, not warn. ---
# A documented manual checklist step is not sufficient: S129 demonstrated that a
# documented step gets skipped under pressure. The build itself is the enforcement.
echo ""
echo "Step 1c: Verifying no secrets survive..."
SECRET_FOUND=0
for f in cloud-config.json api-keys.json device-token.json device-signing.key subscription.key; do
    if [ -e "/opt/d3kos/config/$f" ]; then
        echo "  FATAL: /opt/d3kos/config/$f is present in the image" >&2
        SECRET_FOUND=1
    fi
done
if [ -n "$(ls -A /etc/ssh/ssh_host_*_key 2>/dev/null)" ]; then
    echo "  FATAL: SSH host keys present in the image" >&2
    SECRET_FOUND=1
fi
if [ "$SECRET_FOUND" -ne 0 ]; then
    echo "" >&2
    echo "Build ABORTED: secrets would ship inside the image (BUG-78)." >&2
    echo "Do not work around this check. Fix sanitize.sh." >&2
    exit 1
fi
echo "  No secrets found — safe to image"
```

### 4.2 `--unattended` is a required prerequisite, not an assumption

`sanitize.sh` currently warns interactively. **Before Replacement C is deployed, confirm whether
`sanitize.sh` accepts a non-interactive flag.**

`Uncertainty flag: I have NOT read sanitize.sh's argument handling. If it has no --unattended mode,
Replacement C hangs the build waiting for input.` Two options, Tier 1 decision:
- (a) add an `--unattended` flag to `sanitize.sh` that skips only the confirmation prompt; or
- (b) drop the flag from Replacement C if the script is already non-interactive.

**Verify first. Do not guess.** This is the one open item in this spec.

---

## 5. STEP 4 — TDD test, written and failing BEFORE the fix

**Target:** `deployment/v0.9.9.4/tools/verify-bug78.sh` (new file, follow the existing `verify-bug*.sh`
pattern — there are 10 of them, e.g. `verify-bug54.sh`, `verify-bug55.sh`)

The test must **fail before Steps 2–3 and pass after**. Assertions:

| # | Assertion | Pre-fix | Post-fix |
|---|---|---|---|
| T1 | `create-image.sh` contains a call to `sanitize.sh` | FAIL | PASS |
| T2 | `create-image.sh` contains the secret-assertion loop and `exit 1` | FAIL | PASS |
| T3 | `sanitize.sh` names all five secret files | FAIL | PASS |
| T4 | `sanitize.sh` sets `license.json` to mode `600`, and `644` appears nowhere for it | FAIL | PASS |
| T5 | Repo and Pi md5 match for both scripts | FAIL (absent from repo) | PASS |
| **T6** | **Negative test — the assertion actually bites.** Create a dummy `/opt/d3kos/config/api-keys.json`, run only the assertion block, expect **exit 1** | n/a | PASS |

**T6 is the assertion that matters most.** T1–T5 prove the text is present; only T6 proves the guard
works. A guard that is present but non-functional is worse than no guard, because it produces false
confidence. Do not mark BUG-78 fixed on T1–T5 alone.

---

## 6. STEP 5 (Tier 2) — deploy and verify

Lab Pi only, under the standing S131 lab-deploy authorisation.

1. Deploy both scripts to `/opt/d3kos/scripts/`, preserving mode `755` and ownership.
2. Confirm md5 equality repo↔Pi.
3. Run `verify-bug78.sh` — expect all six PASS.
4. **Do not run `create-image.sh` end-to-end as a test.** It `dd`s the whole SD card (30–60 min) and
   `sanitize.sh` destroys the lab Pi's SSH keys and license. Test the *blocks* in isolation (T6 does
   this). A full image build is a deliberate, separate, operator-scheduled activity.

⚠ **Sanitising the lab Pi would remove the `~/.ssh/authorized_keys` this session depends on.** Never
invoke `sanitize.sh` on a Pi you are working on.

---

## 7. STEP 6 — spec reconciliation

`MASTER_SYSTEM_SPEC` §12.1 was corrected to v4.0 in S131, but it was corrected against the **fictional**
script. Once Steps 1–5 land, replace §12.1's build script with the **real** `create-image.sh` contents,
and note that `sanitize.sh` is the sanitisation authority. Otherwise the spec continues to describe
software that does not exist — which is the defect that produced this bug's original mis-diagnosis.

---

## 8. ROLLBACK

- Repo: `git revert` the Step 2–3 commit. Step 1's commit is content-free and stays.
- Pi: `/opt/d3kos/scripts/*.pre-bug78.bak` written by the deploy.
- Nothing else on the Pi is modified. No service is restarted. No data is touched.

---

## 9. DEFINITION OF DONE

- [ ] Step 0 operator image inspection completed and recorded in the bug entry
- [ ] Both scripts in the canonical tree, md5-identical to the Pi (T5)
- [ ] `verify-bug78.sh` fails pre-fix and passes 6/6 post-fix, **including T6**
- [ ] `--unattended` question resolved by reading `sanitize.sh`, not assumed
- [ ] BUG-78 entry updated with the evidence
- [ ] §12.1 reconciled with the real script (Step 6)
- [ ] BUG-74 (mode 600 on `cloud-config.json`) done or explicitly sequenced after this

---

## 10. WHAT THIS SPEC DELIBERATELY DOES NOT DO

- **Does not fix BUG-66.** Stripping the key from the image stops distribution; it does not stop one
  shared key authenticating 12 endpoints. That is BUG-66, and it remains CRITICAL.
- **Does not fix BUG-65.** Mode 600 raises the bar; the tier is still trusted verbatim from a local file
  and Tier 2/3 are still filesystem tests.
- **Does not implement first-boot regeneration.** The five files must be regenerated on first boot or a
  sanitised image boots into a non-functional state. `first-boot-setup.sh` already generates
  `license.json` and `installation_id`; whether it generates `cloud-config.json` and
  `device-token.json` is **UNVERIFIED and must be checked before an image is built from a sanitised
  card.** Tracked as a follow-up, not silently assumed.
