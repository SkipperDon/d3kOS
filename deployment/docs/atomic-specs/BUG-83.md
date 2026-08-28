# ATOMIC SPEC — BUG-83

**Defect:** `services/ai/alert_watcher.py` is a stale divergent copy of the `alert_watcher.py` systemd
actually runs.
**Severity:** MEDIUM · **Tier:** Tier 3 — one deletion, but see the trap.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-83

---

## 1. THE FACTS — verified 2026-08-28

| Path | Version | Lines | md5 | Runs? |
|---|---|---|---|---|
| `opt/d3kos/services/alert_watcher.py` | 0.9.6 | 405 | `2e94fe79…` | **YES** |
| `opt/d3kos/services/ai/alert_watcher.py` | 0.9.5 | 338 | `48b07c5e…` | no |

`d3kos-alert-watcher.service`: `WorkingDirectory=/opt/d3kos/services`, `ExecStart=… alert_watcher.py`
→ **the root copy is live.**

The root file is a **strict superset**. `ai/` lacks `USER_PREFS_FILE`, `load_alert_prefs()` and
`local_prefs_allow()`. Nothing exists in `ai/` that is absent from root.

## 2. ⛔ THE TRAP — promote, do not prune

This is the **third instance** of the pattern Phase 0.4 fixed for `cloud_agent.py` (719-line superset vs
630) and `ota_upgrade.py`. **Phase 0.4 missed it**, because that pass was scoped to two named files
instead of driven by a search for the shape.

⛔ **"De-duplicate" reads like "delete one." Deleting the ROOT copy destroys the only copy of
`load_alert_prefs` and `local_prefs_allow`.** Delete `ai/`, keep root.

## 3. PREREQUISITES — abort on mismatch

| # | Check | Expected |
|---|---|---|
| P1 | `diff services/alert_watcher.py services/ai/alert_watcher.py` | differences **only** as §1 describes |
| P2 | `comm -13` of `^def` lists (root vs ai) | **empty** — nothing unique to `ai/` |
| P3 | `grep ExecStart etc/systemd/system/d3kos-alert-watcher.service` | `alert_watcher.py`, WorkingDirectory `/opt/d3kos/services` |
| P4 | `grep -rn "ai/alert_watcher" opt/ etc/` | **no importer** — nothing requires the `ai/` copy |

⛔ **If P2 is non-empty, STOP.** The relationship is not a clean superset and this spec does not apply.
**Re-run the diff at fix time — do not trust the S135 result.**

## 4. FIX

Delete `deployment/v0.9.9.4/opt/d3kos/services/ai/alert_watcher.py`. **Own commit, nothing else in it.**
Then remove it from the Pi and regenerate `MANIFEST.md5`.

## 5. ⛔ DO NOT STOP AT ONE — sweep for the shape

Phase 0.4's method is what let this survive. Run a basename-collision scan:

```
find deployment/v0.9.9.4/opt -name '*.py' -printf '%f\n' | sort | uniq -d
```

For each collision: diff, determine which systemd runs, and **log what you find as new bugs.**
Do not fix them in this spec. Do not cap the audit and call it coverage (STANDING TRAP 2).

## 6. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | `systemctl is-active d3kos-alert-watcher` after removal | **active** |
| T2 | Trigger an alert; confirm it is handled | works |
| T3 | `grep -rn "ai/alert_watcher"` | 0 hits |
| T4 | `release-state.sh` | clean; `MANIFEST.md5` regenerated as part of the change |
| **T5** | `load_alert_prefs` and `local_prefs_allow` still present in the surviving file | **the promote-not-prune guard** — proves the right copy survived |
| T6 | §5 sweep run | collisions listed and logged, or "none found" stated |

## 7. DEFINITION OF DONE

- [ ] P1–P4 pass, **diff re-run at fix time**
- [ ] `ai/` copy removed in its own commit; Pi updated; `MANIFEST.md5` regenerated
- [ ] T1–T6 pass, **T5 explicitly checked**
- [ ] §5 sweep run and its findings logged as new bugs
- [ ] Lab Pi only
