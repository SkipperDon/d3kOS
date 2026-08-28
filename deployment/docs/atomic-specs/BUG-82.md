# ATOMIC SPEC — BUG-82

**Defect:** `boatlog-export-api.py` binds `127.0.0.1`. All four `:8095` endpoints are unreachable from
any browser that is not on the Pi.
**Severity:** MEDIUM · **Tier:** Tier 3 for the edit; **Tier 1/2 for the bind decision.**
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-82

---

## 1. VERIFIED — lab Pi, 2026-08-28

```
ss -tlnp | grep 8095   ->   LISTEN 127.0.0.1:8095   users:(("python3",pid=1016))
```
Source: `opt/d3kos/services/boatlog/boatlog-export-api.py:350` — `app.run(host='127.0.0.1', port=PORT)`.

Callers address it by the **browser's** hostname, so they never reach a loopback socket:
`boat-log.html:316` `'http://' + window.location.hostname + ':8095'`, used at `:447` status,
`:551` voice-note, `:591` export; plus `boatlog-engine.js:16`.

**Status, voice-note and CSV export all fail whenever the dashboard is opened over the LAN.**

⚠ **This is the server side of the BUG-46/48 class.** Those removed hardcoded `localhost` from
front-end code. Nobody then checked whether the services those pages call were listening on a reachable
address. ⛔ **`app.py` binding localhost is CORRECT and unrelated** — that is outbound server-side code.

## 2. WHY IT WAS INVISIBLE

Every caller swallows the error — bare `.catch()` chains, and `boatlog-engine.js:89` is an explicitly
empty `.catch()`. A connection refusal is indistinguishable from success. **Same shape as BUG-54.**

## 3. PREREQUISITE — answer this first

**Does the Pi's kiosk browser load the dashboard via `localhost:3000` or via the LAN IP?**
If `localhost`, these calls work on the touchscreen today and only remote browsers are affected — which
changes the severity and the urgency. `Uncertainty flag: the kiosk URL was NOT read in S135.`

## 4. FIX — two options, operator decides

| Option | Change | Trade-off |
|---|---|---|
| **A — bind `0.0.0.0`** | `:350` `app.run(host='0.0.0.0', …)` | One line. ⚠ **Widens the network surface.** Check against the BUG-66/BUG-74 credential posture before choosing |
| **B — proxy via the dashboard (recommended)** | Add `/api/boatlog/*` passthrough in `app.py` (:3000) | No new listener, same origin, no CORS. Matches the route BUG-24 already takes for `GET /api/boatlog/entries` |

**B is consistent with BUG-24's decision** to serve boat-log reads from `app.py` precisely to avoid this.

## 5. ALSO FIX — the swallowed errors

Replace the empty `.catch()` handlers in `boat-log.html` and `boatlog-engine.js:89` with ones that
surface the failure. ⚠ **Without this, the next binding mistake is equally invisible.** The silent catch
is the reason this lasted.

## 6. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | `ss -tlnp \| grep 8095` (option A) or route present (option B) | reachable |
| **T2** | Load `boat-log.html` from a **remote** browser; check status indicator | shows the real service state — **the operator-facing proof** |
| T3 | CSV export from a remote browser | downloads |
| T4 | Voice-note upload from a remote browser | succeeds or **shows a visible error** |
| **T5** | **Negative: stop the boatlog service, reload the page** | a **visible** error appears — proves §5 landed. Silent failure = FAIL |
| T6 | Pi kiosk browser still works | no regression |

## 7. DEFINITION OF DONE

- [ ] §3 kiosk-URL question answered and recorded
- [ ] Option A or B chosen by the operator, with the reason recorded
- [ ] Swallowed `.catch()` handlers fixed
- [ ] T1–T6 pass, **T5 demonstrated**
- [ ] Lab Pi only — boat out of scope per operator directive S135
- [ ] ⛔ If option A: state the new exposure explicitly in the deploy note
