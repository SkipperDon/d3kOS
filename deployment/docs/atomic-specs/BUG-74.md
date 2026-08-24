# ATOMIC SPEC — BUG-74

**Defect:** `MASTER_SYSTEM_SPEC` section 8.4.2 P5 specified a credential file that has never existed. The real
file, `cloud-config.json`, is world-readable, is **not** covered by `.gitignore`, and holds more secrets
than previously recorded.
**Severity:** MEDIUM in isolation; HIGH as a contributing cause of BUG-66. **Not** an independent
release gate, but it is a prerequisite of BUG-66's fix.
**Tier:** Steps 1–2 are Tier 3 (mechanical). Step 3 is Tier 2. Step 0 is Tier 1 (already done).
**Created:** 2026-08-24 (S131)
**Bug record:** `deployment/docs/V09994_BUG_FIXES.md` BUG-74

---

## 0. WHAT THE S131 INVESTIGATION ESTABLISHED

Three things were verified live. Two of them were not in the original bug entry.

**(a) The spec named a file that does not exist.** section 8.4.2 P5 specified
`/opt/d3kos/config/cloud-credentials.json` for five months, including a `.example` template. Live read
of the lab Pi: **ABSENT**. The real file is `cloud-config.json`, mode **644**, 312 bytes.
*Corrected in `MASTER_SYSTEM_SPEC` v4.0, S131.*

**(b) `.gitignore` protects the fictional file and not the real one.** Current entries:

```
api-keys.json
cloud-credentials.json          <- does not exist
**/config/api-keys.json
**/config/cloud-credentials.json <- does not exist
```

**`cloud-config.json` appears nowhere in `.gitignore`.** A copy is already tracked at
`deployment/v0.9.4/pi_source/cloud-config.json`.

**(c) The file holds more than the API key.** Field inventory, live Pi vs tracked template (values never
printed — lengths and shapes only):

| Field | Live Pi | Tracked template |
|---|---|---|
| `amboat_api_key` | 64 chars, **live** | `PLACEHOLDER` ✅ |
| `amboat_base_url` | 20 chars | present |
| `poll_interval_seconds` | 2 chars | present |
| `turn_username` | 24 chars, **live** | **absent** |
| `turn_credential` | 16 chars, **live** | **absent** |
| `device_token` | 36 chars (UUID), **live** | **absent** |

**Two consequences that change the risk assessment:**

1. **Metered.ca TURN credentials live in this file.** They were not previously identified as residing
   here. Any local user can read them at mode 644, and they are a metered paid service — abuse costs
   money. BUG-66 was scoped to the API key alone; **the blast radius is wider.**
2. **The pre-commit hook would NOT stop this file being committed.** Its patterns are `amboat_…{20,}`,
   `AIza…`, `sk_live_`, `pk_live_`, `sk-ant-api`, and PRIVATE KEY. `turn_credential` (16 chars) and
   `device_token` (a UUID) match **none** of them. So the hook catches the API key and silently passes
   the TURN credentials and the device identity. **The hook is a backstop, not the control.** The
   `.gitignore` rule is the control, and it is currently pointed at the wrong filename.

✅ **No live key is committed today.** The tracked template is a genuine placeholder. This is a
latent exposure, not a realised one.

---

## 1. PREREQUISITES — verify before editing. Abort if any check fails.

| # | Check | Expected |
|---|---|---|
| P1 | `grep -c '^cloud-config.json$' .gitignore` | `0` (the gap) |
| P2 | `git ls-files \| grep -c 'cloud-config.json'` | `1` (the tracked template) |
| P3 | Tracked template's `amboat_api_key` is a placeholder | true — **if false, STOP: a live key is committed and this becomes a BUG-58-class incident requiring history rewrite** |
| P4 | `stat -c %a /opt/d3kos/config/cloud-config.json` on the lab Pi | `644` (the defect) |

**P3 is a hard gate.** If the tracked value is ever live, do not proceed with this spec — escalate to
the BUG-58 remediation path (rotate, rewrite history, and note that a force-push deletes nothing:
per S130, blobs remain reachable by SHA and only GitHub Support can purge them).

---

## 2. STEP 1 (Tier 3) — fix `.gitignore` to name the real files

**Target:** `.gitignore` (repo root)

`old` (exact):
```
api-keys.json
cloud-credentials.json
```

`new`:
```
api-keys.json
cloud-config.json
cloud-credentials.json
device-token.json
device-signing.key
subscription.key
```

`old` (exact):
```
**/config/api-keys.json
**/config/cloud-credentials.json
```

`new`:
```
**/config/api-keys.json
**/config/cloud-config.json
**/config/cloud-credentials.json
**/config/device-token.json
**/config/device-signing.key
**/config/subscription.key
```

**`cloud-credentials.json` is deliberately retained** even though it does not exist. It costs nothing,
and if anything ever creates it — a script written from the old spec text, for instance — it is covered.

**Do not add `license.json`.** It is legitimately tracked as a template in places and is not a secret in
the same sense; it is a forgeable tier claim (BUG-65), which is a different defect with a different fix.

⚠ **The tracked template at `deployment/v0.9.4/pi_source/cloud-config.json` will now be ignored for
future changes but stays tracked** (gitignore does not untrack). That is the correct outcome: keep the
placeholder template, prevent new copies. Do **not** `git rm --cached` it — it is a useful template and
removing it would break anything referencing it.

---

## 3. STEP 2 (Tier 3) — complete the template

**Target:** `deployment/v0.9.4/pi_source/cloud-config.json`

The template has 3 fields; the live file has 6. A fresh install from this template lacks
`turn_username`, `turn_credential` and `device_token`, so WebRTC TURN fallback and device identity would
be silently absent.

Add the three missing keys **as placeholders**, preserving existing values and key order:

```json
{
  "amboat_api_key": "<existing placeholder — DO NOT CHANGE>",
  "amboat_base_url": "<existing value — DO NOT CHANGE>",
  "poll_interval_seconds": <existing value — DO NOT CHANGE>,
  "turn_username": "YOUR_TURN_USERNAME_HERE",
  "turn_credential": "YOUR_TURN_CREDENTIAL_HERE",
  "device_token": ""
}
```

**`device_token` is empty, not a placeholder string.** It is generated on first boot; a non-empty
placeholder would be a shared identity across every install — precisely the BUG-39 failure. Confirm the
consuming code treats `""` as "generate one", and if it does not, that is a **new bug to log, not to fix
here.**

`Uncertainty flag: I have NOT read the code that consumes turn_username/turn_credential. Confirm the
exact key names against the consumer before relying on this template.`

---

## 4. STEP 3 (Tier 2) — permissions on the Pi

Mode `644` → `600`, owner unchanged (`d3kos:d3kos`).

**Before changing it, establish which processes read the file.** `cloud_agent.py`,
`export_worker.py` and `fleet_push_service.py` all reference it. If any runs as a different user, `600`
breaks it — and a broken export path is how BUG-54 went unnoticed for five months.

| Step | Action |
|---|---|
| 1 | Determine the `User=` of every unit that reads the file (`d3kos-cloud-agent`, `d3kos-export`, fleet push) |
| 2 | If all run as `d3kos`: `chmod 600`. If any runs as another user: **STOP and report** — the fix is a group, not a mode |
| 3 | Restart the affected services and confirm each is `active` |
| 4 | Confirm the export path still works: `failed_exports/` count must not increase |

⚠ **This is the step that can break something.** Everything above it is inert text. Sequence it last and
verify the services, not just the mode.

---

## 5. TDD TEST

**Target:** `deployment/v0.9.9.4/tools/verify-bug74.sh` (new; follow the existing `verify-bug*.sh` pattern)

| # | Assertion | Pre-fix | Post-fix |
|---|---|---|---|
| T1 | `.gitignore` contains `cloud-config.json` and the `**/config/` form | FAIL | PASS |
| T2 | Template contains all six keys | FAIL | PASS |
| T3 | Template's `amboat_api_key` matches no live-key pattern | PASS | PASS (must not regress) |
| T4 | Template's `device_token` is `""` | FAIL | PASS |
| T5 | Pi file mode is `600` | FAIL | PASS |
| **T6** | **Negative test:** `git check-ignore -q <path>/cloud-config.json` returns 0 — the rule actually matches | FAIL | PASS |
| **T7** | **Negative test:** every service reading the file is `active` after the mode change | n/a | PASS |

T6 proves the ignore rule *matches* rather than merely being present — a rule in the wrong section or
with wrong glob syntax reads correctly and does nothing. T7 is the regression guard for Step 3.

---

## 6. ROLLBACK

- `.gitignore` and template: `git revert`.
- Pi mode: `chmod 644` restores prior state; no file content is altered at any point in this spec.

---

## 7. DEFINITION OF DONE

- [ ] P3 confirmed — no live key in git history
- [ ] `verify-bug74.sh` fails pre-fix, passes 7/7 post-fix
- [ ] TURN credentials recorded in the BUG-66 scope (they were missing from it)
- [ ] `turn_*` key names confirmed against the consuming code, not assumed
- [ ] BUG-74 entry updated with the `.gitignore` and TURN findings

---

## 8. FEEDS INTO

- **BUG-66** — the per-device credential replacing this shared key. **Update its scope: the file also
  holds TURN credentials and the device token.**
- **BUG-78** — this file is first on the image credential-strip list. BUG-78 removes it from the
  distribution; this spec protects it in the repo and on disk. Both are needed; neither substitutes.
- **BUG-59** — the pre-commit hook's pattern set does not cover TURN credentials or UUIDs. Extending it
  is a **candidate new bug**, not part of this fix.
