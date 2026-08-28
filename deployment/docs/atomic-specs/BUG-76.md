# ATOMIC SPEC — BUG-76

**Defect:** §8.4.4 marks five endpoints REQUIRED; all five are absent. Five documents/code sites name
the community endpoints five different ways.
**Severity:** MEDIUM (was HIGH — the pipeline is not blocked) · **Tier:** Tier 1/2 — spec + a decision.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-76

---

## 1. ⛔ THE FIX IS TO CORRECT THE SPEC, NOT TO BUILD FIVE ENDPOINTS

§8.4.4 describes an architecture that was never built, **running in parallel with one that was and
works**:

```
export_worker.py:299 -> data-ingress.php (11,517 B, deployed, 405 on GET)
                     -> wpax_usermeta
                     -> community-get.php (3,888 B) + community-markers.php (4,691 B)
```

The S134-cont audit found the same independently: *"community map DOES NOT NEED these flows; fleet dots
work via this existing path."*

**Verified absent (FTP listing, not status codes):** `community-markers-post.php`,
`community-markers-get.php`, `community-position.php`, and `telemetry-push.php` +
`community-benchmark.php` which exist in **neither repo — never written**.

⚠ **Probe to find a candidate; list the directory to conclude.** BUG-73 and BUG-75 were files that
existed and answered 404/405. These five are actually not there. The difference came from a listing.

## 2. THE FIVE NAMING SCHEMES — decide from what is DEPLOYED

| # | Source | Name |
|---|---|---|
| 1 | `MASTER_SYSTEM_SPEC` §8.4.4 | `community-markers-post.php` / `-get.php` |
| 2 | `ARCH_SERVICE_MAP.md` | `community/markers.php` |
| 3 | **Production — authoritative** | **`community-markers.php` + `community-get.php`** |
| 4 | `features/v0941-plan/php/` (a DESIGN tree) | `community-markers-write.php` |
| 5 | **`community-api.py:49,73` — live Pi code** | `/api/community/markers` |

⚠ BUG-76 originally said *three* schemes and recommended "the flat form, since those files exist" —
which would have selected #4, a **design-tree** file. **Canonical = the two that are DEPLOYED (#3).**
⚠ **The running Pi (#5) matches none of them.** A doc-only fix leaves the Pi calling a 404 (BUG-89 B).

## 3. FIX

1. Correct `MASTER_SYSTEM_SPEC` §8.4.4 to the deployed reality: `data-ingress.php`,
   `community-get.php`, `community-markers.php`. **Remove `community-markers-post`/`-get` as REQUIRED.**
2. Correct `ARCH_SERVICE_MAP.md` to the same names. ⚠ **Fix both, or the conflict just moves.**
3. Retire `community-markers-write.php` from the design tree, or rename it to the canonical name.
4. **Hand the canonical name to BUG-89 B** so `community-api.py` is corrected in the same wave.
5. **Operator decision — not an implementation task:** are `telemetry-push` and `community-benchmark`
   wanted *capabilities*? They were never written.
   - **Yes** → v0.9.9.5 features, out of v0.9.9.4 scope.
   - **No** → delete them from the spec.
   ⛔ **Do not build them to satisfy a document.**

⚠ `deployment/features/v0941-plan/php/` is a **DESIGN tree** (it holds `page-*-ORIGINAL.php` mockups).
**Nothing in it is deployed.** This trapped BUG-66 Phase C into reporting 3 undeployed files as migrated.

## 4. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Grep §8.4.4 and `ARCH_SERVICE_MAP.md` for the retired names | 0 hits in both |
| T2 | Every endpoint named in §8.4.4 | resolves (not 404) — **probe each** |
| T3 | `community-api.py` uses the canonical name | pass (with BUG-89 B) |
| T4 | Community map still renders fleet dots | **no regression from the renaming** |
| **T5** | **Grep both repos + the Pi tree for all five old names** | 0 hits. ⛔ Fixing two documents and leaving code on a sixth name is the failure this bug is about |

## 5. DEFINITION OF DONE

- [ ] Both documents corrected to the deployed names
- [ ] Design-tree file retired or renamed
- [ ] Canonical name handed to BUG-89 B
- [ ] Operator decision recorded on `telemetry-push` / `community-benchmark`
- [ ] T1–T5 pass
- [ ] ⛔ No new endpoint was built
