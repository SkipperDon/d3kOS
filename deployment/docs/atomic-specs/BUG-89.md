# ATOMIC SPEC — BUG-89

**Defect:** Three Pi→server destination URLs return 404. One is the OTA update path.
**Severity:** HIGH · **Tier:** Tier 3 for the edits; **Tier 1/2 for choosing the correct endpoints.**
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-89

---

## 1. THE THREE — all confirmed 404 on 2026-08-28

| # | Site | URL | |
|---|---|---|---|
| A | `opt/d3kos/services/agents/agents/update_agent.py:47` | `…/mobile/version.php` | 404 |
| B | `opt/d3kos/services/community/community-api.py:49,73` | `atmyboat.com/api/community/markers` | 404 |
| C | `opt/d3kos/services/cloud/cloud-link-api.py:66` | `atmyboat.com/api/notify` (default) | 404 |

Control: `…/mobile/version-api.php` → **401**. The path resolves; these three are genuinely absent.

## 2. A — the OTA path

Production has `version-api.php`, `version-heartbeat.php`, `version-registry.php`. **No `version.php`.**

⚠ **BUG-55 fixed this line's HOST and left its FILENAME wrong** — from *the wrong site* to *the right
site and a file that does not exist*. `verify-bug55.sh` asserts the string `atmyboat.com/staging` is
absent; it never asserts the URL resolves. **The verifier passes while the endpoint 404s.**

⛔ **Do not guess between `version-api.php` and `version-registry.php`.** Read what each returns and
what `update_agent.py` expects to parse, then choose. Record the reasoning.

`Uncertainty flag: "this is why no OTA has ever run" is an INFERENCE from two facts (the URL 404s;
PHASE4 records no OTA has run). update_agent.py's error handling and the Pi journal were NOT read.
Confirm before recording it as BUG-35's cause.`

## 3. B — a fifth naming scheme

`/api/community/markers` matches **none** of the four names BUG-76 catalogued. Production serves
`community-markers.php` and `community-get.php`.

⛔ **Gated on BUG-76's canonical-name decision.** Fixing this file before that decision just adds a
sixth name. Do BUG-76 first, then point this at the chosen name.

## 4. C — a latent fallback default

`data.get('webhook_url', 'https://atmyboat.com/api/notify')` — the **default** 404s. Bites only when a
caller omits `webhook_url`; the exact BUG-55 Category A shape.

**Preferred fix: remove the default and fail loudly** on a missing key. ⚠ A silent fallback to a 404 is
worse than a missing-key error.

## 5. THE SYSTEMIC FIX — `tools/verify-endpoints.sh`

All three fail silently: a 404 on a background POST has no operator-visible symptom.
**`verify-bug55.sh` and `release-state.sh` both PASS while all three are broken** — they check *text*
and *file identity*, never *whether a destination resolves*.

Build a verifier that extracts every `atmyboat.com/...` literal from the canonical tree and asserts each
is not 404.

⚠ **Sequential requests only, with a delay.** Wordfence treats a parallel sweep as a scanner and may
block the operator's own IP (`PHASE3-server-canonical-tree.md` Step 2).
⚠ **Exclude the script from its own scan** — `verify-bug55.sh` self-failed on first run by matching its
own grep pattern.

## 6. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Probe A's corrected URL | not 404 (401/200/405 all acceptable) |
| T2 | `update_agent.py` run against it | parses the response without error |
| T3 | B's URL after BUG-76 | not 404 |
| T4 | C with `webhook_url` omitted | **loud failure**, not a silent 404 |
| T5 | `verify-endpoints.sh` over the tree | 0 unresolvable URLs |
| **T6** | **Negative: plant a URL that 404s, re-run T5** | T5 **fails.** ⛔ Without this the verifier is decoration |
| T7 | `release-state.sh` still clean | no regression |

## 7. DEFINITION OF DONE

- [ ] A pointed at a verified endpoint, choice justified in the entry
- [ ] B gated on and aligned with BUG-76
- [ ] C's default removed or corrected; fails loudly
- [ ] `verify-endpoints.sh` written, **T6 demonstrated**
- [ ] BUG-35's "no OTA has ever run" re-assessed once A resolves
- [ ] Lab Pi only — **boat Pi out of scope per operator directive S135**
