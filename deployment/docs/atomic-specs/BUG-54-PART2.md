# ATOMIC SPEC — BUG-54 PART 2

**Defect:** Cloud export POSTs to `data-ingress.php` are rejected by nginx with HTTP 400, before PHP runs.
**Severity:** HIGH — telemetry, community map and tier sync all ride this pipeline.
**Tier:** Tier 1/2 — diagnosis, not yet implementation.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-54

---

## 1. ⛔ THE REGRESSION HAS A DATE — 2026-04-22

The bug record says *"failed silently every ~10 minutes since 2026-02-20."* **That framing is wrong.**
From the Pi's own `export_queue.json`:

| Period | Outcome |
|---|---|
| 2026-02-20 → 03-26 | 110 failures — placeholder host `d3kos-cloud-api.example.com` |
| 2026-03-26 → **04-22** | **237 SUCCESSES** (155 Mar, 82 Apr) |
| **2026-04-22** → 08-28 | **99 nginx 400s** (1 Apr, 19 Jul, 79 Aug) — still accumulating |

**Export worked for four weeks. The last success and the first nginx 400 are both 2026-04-22.**
⚠ Phase 4 went live 2026-04-12, ten days earlier. **Ask what changed on the server on or about 22 April.**
⚠ The count is **99**, not the 63 in the record.

## 2. ELIMINATED — do not re-test any of these

| Hypothesis | Verdict |
|---|---|
| Wrong URL / staging leftover | **No.** `amboat_base_url = https://atmyboat.com`; endpoint string correct |
| Malformed header values | **No.** api_key 64 ch, device_token 36 ch, **zero** non-printable or space chars |
| Headers rejected by nginx | **No.** All three real headers POSTed to `atmyboat.com/` **from the Pi** → **200**. Singly too |
| Body too large | **No.** 1/16/64/128/256 KB to `/` → all 200. Real payloads **23–33 KB** (n=237, median 25,650 B) |
| PHP rejecting it | **No.** **Zero `data-ingress` entries** in `mobile/error_log` over a full week. nginx rejects **before PHP** |
| `/exports/exports/` doubled path | **NOT a bug.** Directory exists with 248 files; all 473 queue entries use it consistently |

**Asymmetry to reason from:** `GET` on `data-ingress.php` reaches PHP (**405**). `POST` gets nginx **400**.
Same headers and comparable body sizes are accepted at `/`.

## 3. THE NEXT DIAGNOSTIC — one request settles the split

⛔ **Requires explicit operator `APPROVED` — it is a POST to a production data endpoint.**

From the Pi, POST a **minimal** payload to `data-ingress.php` with the real headers.

| Result | Meaning | Next |
|---|---|---|
| **Not 400** (401/200/422…) | size- or content-dependent | **Bisect the payload.** Halve until it passes; the failing half names the trigger |
| **Still 400** | path- or method-dependent; payload irrelevant | Escalate to HostPapa with the exact request — it is their nginx layer |

⚠ Use a payload that PHP will reject on validation (e.g. absent required fields) so **nothing is
persisted** even if it reaches the application.

## 4. IF IT ESCALATES TO HOSTPAPA

Give them: the exact URL, the three header names (**not** their values), the body size, the UTC
timestamp of a failure, and the fact that **GET succeeds while POST 400s on the same path**. Ask for the
**nginx error-log line**. That is the one artefact FTP cannot reach and the only thing that names the rule.

## 5. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Trigger one export; read the journal | upload returns **200** |
| T2 | `export_queue.json` after T1 | new entry in `completed`, not `failed` |
| **T3** | Retry the 11 `pending` entries | they drain — **the operator-visible proof** |
| T4 | `mobile/error_log` | data-ingress entries now appear (PHP is being reached) |
| **T5** | **Negative: restore whatever triggered the 400, confirm it fails again** | proves the cause was identified, not coincidence |

## 6. DEFINITION OF DONE

- [ ] §3 diagnostic run with operator approval; result recorded
- [ ] Cause **named**, not inferred — `Uncertainty flag: as of S135 the nginx rule is still unidentified`
- [ ] T1–T5 pass, **T5 demonstrated**
- [ ] The record's "failed continuously since 2026-02-20" framing corrected (done S135)
- [ ] Boat Pi `failed_exports/` count added to the boat test card (lab Pi = **0**); boat out of scope S135
