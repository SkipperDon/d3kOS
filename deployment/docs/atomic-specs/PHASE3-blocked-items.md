# ATOMIC SPEC — PHASE 3: Blocked Items (BUG-71, 73, 56, 54 Part 2)

**Purpose:** these four cannot be specced as fixes, because their root causes are unknown and cannot be
determined from outside. This spec states **exactly what unblocks each one**, so no session wastes effort
guessing — and so the blocker is visible rather than rediscovered.
**Created:** 2026-08-24 (S131)

⚠ **Do not write an implementation spec for any item below until its unblock condition is met.** S114's
lesson: *"an atomic spec must state the exact fix. Writing specs for those would be Tier 1 guessing and
Tier 3 faithfully implementing the guess."* All four are OPEN with root cause unknown.

---

## BUG-71 — `pair-device.php` HTTP 500

**Verified S131:** returns **500 twice**, against a stable 401 control. Sibling endpoints in the same
directory return 401/405 correctly, so the directory resolves and PHP executes — the fault is inside the
file. The response body is **completely empty**, consistent with `error_reporting(0)` at the top of these
endpoints.

**No source copy exists anywhere in the repo.** There is no reference implementation to diff against and
no record of intended behaviour beyond one line in `ARCH_SERVICE_MAP.md`: *"Links `app_token` to
`device_token`, returns tier level", auth = `app_token`.*

### Unblock condition — one of:
1. **Main cPanel FTP credentials** (home = `public_html`), or
2. the operator pasting the file contents, or
3. the **PHP error log entry** for a 500 on this endpoint.

⚠ The FTP account supplied in S131 (`admin@atmyboat.com`) is **chrooted to an empty home** — `../` and
`../../` return the same three entries and no path reaches `public_html`. It cannot read site files.

### Why this one matters most in Phase 3
It is **step 2 of PWA device pairing**. With it broken, `register-device` → `pair-device` →
`dashboard-data` cannot complete, so **every PWA integration test for a new device is blocked behind it**.
It is the critical path, not a side issue.

### First action once unblocked — before any fix
Bring the file **under version control unmodified**, then diff. It is unsourced production code; editing
it first destroys the only record of what was running.

---

## BUG-73 — `fix-my-pi-billing.php` absent from production *and* repo

**Verified S131:** 404 twice. The app-facing half (`fix-my-pi-app.php`) **is** deployed and returns 405
correctly. Repo-wide search returns nothing for the billing half.

`ARCH_SERVICE_MAP.md` documents the flow as
`fix-my-pi-app.php` (initiate charge) → Stripe → `fix-my-pi-billing.php` (webhook) → queued command.
With the webhook absent, **Stripe has nowhere to deliver the payment event, so paid work is never queued.**

### Unblock condition — operator action, in this order
1. **Check the Stripe dashboard for FMP charges with no corresponding queued command.** This determines
   whether the exposure is theoretical or whether **a customer has been charged for work never done.**
   Everything else is secondary to that answer.
2. Confirm the intended contract: what the webhook must write, which command it queues.

`Uncertainty flag: it is NOT established that fix-my-pi-app.php can initiate a charge at all. If it
cannot, no customer has been charged and severity drops from HIGH. Do not assume financial exposure, and
do not assume its absence.`

⚠ **Any verification uses Stripe TEST mode only.** Never test a billing path against live payments.
⚠ **Related precedent:** BUG-10 was Stripe webhooks left pointing at `/staging/` after the Phase 4 live
push. Same class. **Check where the Stripe dashboard currently points before writing anything.**

---

## BUG-56 — `api-admin.php` returns 404

**Re-diagnosed S131** (the S120 entry said HTTP 400; it is 404, and all six S120 candidate causes are
superseded — every one assumed the endpoint exists). **No source in the repo either.** The Admin Console
is calling an endpoint that exists in neither place.

**This is a build task, not a debugging task.**

### Unblock condition
Read **`crm-proxy.php` on the Admin Console VM (192.168.236.5)** to establish the exact contract the
console expects — method, headers, payload shape, response shape. Without it, writing `api-admin.php`
means inventing an interface and hoping the console agrees.

⚠ **Unresolved and worth stating:** why it read 400 in S120 and 404 now. Either the file was removed
between the two sessions, or the 400 came from a different layer (proxy/WAF) and was attributed to the
endpoint. `Uncertainty flag: cannot distinguish these without the HostPapa access logs.` **Do not build
on the assumption that it once existed.**

⚠ **`support-request.php` returns 405 — it works.** BUG-56's original entry suggested cross-referencing
against it, and that remains the right move: it is the nearest working endpoint of the same shape.
*Diff against what works.*

---

## BUG-54 Part 2 — nginx HTTP 400 on cloud export

**Part 1 is fixed** (S118): `Environment=PYTHONUNBUFFERED=1` — `export_worker.py` used `print()`, systemd
gave it a socket rather than a TTY, CPython block-buffered at 8 KB, and every diagnostic was trapped for
five months.

**Part 2 remains open.** Recorded evidence: 63 failures returning nginx's **HTML** error page rather than
PHP JSON, so **nginx rejects before PHP runs.** Already ruled out: malformed headers (both values pure
printable ASCII), missing config, and body size (~50 KB would give 413, not 400).

### Unblock condition
The **HostPapa nginx error log** entry for one of these 400s. This cannot be diagnosed from the client
side — that is what "nginx rejects before PHP" means.

⚠ **New S131 datum, and do not conflate it:** `MASTER_SYSTEM_SPEC` §8.4.2 P1 specified
`/mobile/data-ingress.php`, which **returns 404** (BUG-75). Anything built to the spec would have failed
differently. `Uncertainty flag: it is NOT established that BUG-54's 400 relates to the wrong URL. The 400
came from the full theme path. Do not merge the two diagnoses without log evidence.` **This bug has
already been misdiagnosed once (S117, corrected S118) — that is exactly why.**

⚠ **Also still unchecked: the boat Pi's `failed_exports/` count.** It alone sets true severity, and the
boat Pi is unreachable from the lab. Add it to the boat test card.

---

## SUMMARY — what to ask for, once

| Need | Unblocks |
|---|---|
| **Main cPanel FTP** (home = `public_html`) | BUG-71, `PHASE3-server-canonical-tree.md` Step 1.2, and the ~23 unprobed endpoints |
| **HostPapa nginx + PHP error logs** | BUG-54 Part 2, BUG-71 |
| **Stripe dashboard check** | BUG-73 severity — and whether a customer was charged for nothing |
| **`crm-proxy.php` from 192.168.236.5** | BUG-56 |
| **Boat trip** | BUG-54's `failed_exports/` count, BUG-26/27 boat state |

**The first two unblock four of the five items.** They are the highest-value operator actions in Phase 3.

## DEFINITION OF DONE FOR THIS SPEC

This spec is "done" when each item above has either been unblocked and given a real implementation spec,
or been explicitly deferred out of v0.9.9.4 by operator decision. **It is not done by being written** —
it is a register of blockers, and its purpose is to stop them being silently rediscovered next session.
