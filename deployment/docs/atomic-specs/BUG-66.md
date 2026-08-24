# ATOMIC SPEC — BUG-66

**Defect:** One fleet-wide static API key in cleartext on every Pi authenticates all 12 server endpoints.
**Severity:** CRITICAL — **v0.9.9.4 release gate** (operator decision S131: severity held at CRITICAL as
a gate on the *design*, not on present exploitability).
**Created:** 2026-08-24 (S131)
**Bug record:** `V09994_BUG_FIXES.md` BUG-66 · **Design of record:** `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0

---

## 0. READ THIS FIRST — this is not a Tier 3 task

**The fix is predominantly new-file creation: 4 SQL tables, 3 new PHP endpoints, and a Pi-side signing
module.** The standing rule — *Tier 3 gets exact `old`/`new` replacements, never whole files* — was
established because a whole-file dispatch in S118 produced invalid bash. That rule holds here.

**Therefore:**
- **Phase A and B are Tier 1/2 authored.** Tier 3 cannot write them.
- **Phase C and D are Tier 3 implementable** — they are constrained edits to 12 existing files.

Do not attempt to save cost by dispatching Phase A to Gemma-4. The output would be a plausible
authentication layer, and a plausible authentication layer is worse than none.

## 0.1 What S131 verified live — corrections to the bug record

| Claim in the record | Verified? | Detail |
|---|---|---|
| Shared key authenticates the endpoints | ✅ **Confirmed in code** | `version-heartbeat.php`: `hash_equals(AMBOAT_API_KEY, $m[1])` is the *only* credential check |
| `device_token` checked "non-empty and nothing else" | ✅ **Confirmed** | `if (empty($device_token)) { 400 }` — no lookup, no binding, no verification |
| Line 82 blind UPSERT self-registers any UUID | ✅ **Confirmed** | `INSERT … ON DUPLICATE KEY UPDATE` on `amboat_devices` |
| The vector is live | ❌ **NO — `version-heartbeat.php` returns 404, not deployed** (BUG-72) | The design flaw ships the moment it deploys |
| Only the API key is at risk | ❌ **WIDER — see BUG-74** | `cloud-config.json` also holds `turn_username`, `turn_credential` (Metered.ca, a *paid metered* service) and `device_token` |
| `[VERIFY]` PHP ≥ 7.2 + libsodium | ✅ **RESOLVED S131** | `x-powered-by: PHP/8.3.33`. libsodium is bundled in core from 7.2, so `sodium_crypto_sign_verify_detached()` needs no extension install |

**Credit where due:** the existing check uses `hash_equals()`, which is timing-safe. The flaw is the
shared secret, not sloppy comparison.

**Two further observations from the same file, logged as candidates rather than fixed here:**
- `error_reporting(0)` at the top of the endpoint. This is why BUG-71's `pair-device.php` 500 returns a
  completely **empty body** — verified. It makes every server-side fault undiagnosable from outside.
- The endpoint runs `ALTER TABLE … ADD COLUMN` on **every request** as a schema migration. Works, but it
  is a per-request DDL check on shared hosting.

---

## 1. THE DESIGN — one mechanism, two problems

`D3KOS_DEVICE_REGISTRATION_SPEC.md` section 2 already specifies Ed25519 per-device identity for *forum
registration*. **Use the same mechanism for device authentication.** One keypair, one verification path,
solving BUG-66 and BUG-63's trust anchor together. Building two credential systems would be the error.

```
Pi                                              atmyboat.com
 ├─ device-signing.key  (private, 0600, root)    ├─ public_key  (32B, safe at rest)
 └─ sign(device_token|ts|nonce|path)             └─ sodium_crypto_sign_verify_detached()
```

**What the signature does and does not prove** (registration spec section 3.1 — do not lose this):
it proves *"this message came from the holder of key K."* It does **not** prove *"K belongs to a genuine
d3kOS install"* — the image is a free anonymous public download (`MASTER_SYSTEM_SPEC` section 12.1), so no
per-copy secret exists. **The trust anchor is the operator approval queue, not cryptography.** Signatures
stop device *impersonation*; approval stops *illegitimate enrolment*.

---

## 2. PHASE A (Tier 1/2) — server side. Do this first.

**Deploy order is server-before-Pi.** A Pi enrolling against a server without the tables fails closed,
which is safe. The reverse is not.

**A1 — the four tables.** Take them verbatim from `D3KOS_DEVICE_REGISTRATION_SPEC.md` section 6:
`amboat_device_enrolments`, `amboat_registration_codes`, `amboat_device_accounts`,
`amboat_registration_audit`. Do not redesign them; section 6 already handles code hashing and the atomic claim.

**A2 — a shared verifier**, `mobile/device-auth.php`, used by every endpoint:

```
verify_device_request() ->  device_token | 401
  1. read X-Device-Token, X-Timestamp, X-Nonce, X-Signature
  2. reject |now - ts| > 600s                      (explicit skew error, never a silent failure)
  3. reject replayed nonce (cache 600s)
  4. look up public_key WHERE device_token = ? AND status = 'approved'
     - not found      -> 401   (do NOT create the row — this is the BUG-66 fix)
     - status pending -> 403 not_approved
  5. sodium_crypto_sign_verify_detached(sig, "$token|$ts|$nonce|$path", $pubkey)
  6. return device_token, or 401
```

**Rule: identity is the *result* of verification, never a client-supplied field.** Today
`$device_token` comes straight from a header and is trusted. After this change the header is only a
lookup hint; the signature decides.

**A3 — three endpoints** per registration spec section 7.1: `enrol` (self-signed, proof of possession, 409 on a
known token, **never overwrite an existing key**), `status`, `request-code`.

**A4 — wp-admin approval queue** per section 3.2: Approve / Reject / Block, showing device reference, contact
email, note, source IP, and whether that IP or email already has approved devices.

**Sequence A1 → A2 → A3 → A4.** Nothing after A2 is meaningful without it.

---

## 3. PHASE B (Tier 1/2) — Pi side

**B1 — generate the keypair on first boot. Hook into the existing sentinel; do not invent a new one.**

`regenerate-identity.sh` already implements the correct pattern, verified S131:
- line 16 — guards on `/opt/d3kos/config/.identity-regenerated`
- line 120 — `NEW_TOKEN=$(cat /proc/sys/kernel/random/uuid)`
- line 160–168 — **creates the sentinel LAST, only if every step succeeded**, so a partial failure
  re-runs instead of silently half-completing

Add Ed25519 generation into that script, before the sentinel:
`/opt/d3kos/config/device-signing.key`, mode **0600**, owner root, POSTing only the public key.

⚠ **Never bake a key into the image.** One key in the `.img` would be shared by every d3kOS on earth and
would void the scheme entirely (registration spec section 2.1). BUG-78 adds `device-signing.key` to the image
strip list; **BUG-78 must land before any image is built from a card carrying a key.**

**B2 — a signing helper** used by `cloud_agent.py`, `export_worker.py` and `fleet_push_service.py`.
Python side: `cryptography`'s `ed25519.Ed25519PrivateKey` or PyNaCl.

⚠ **B1 gap found S131 — first boot does not create the credential files.** `first-boot-setup.sh` creates
`license.json` only (line 128, and note it `chmod 644` at line 147 — see BUG-65). It does **not** create
`cloud-config.json` or `device-token.json`; the latter comes from `regenerate-identity.sh`. So after
BUG-78's strip, a fresh image boots with **no** `cloud-config.json`. That is arguably correct — no
credentials until paired — **but every consumer must degrade gracefully rather than crash.** Verify
`cloud_agent.py`, `export_worker.py` and `fleet_push_service.py` all handle the file being absent. If any
crashes, that is a new bug to log.

---

## 4. PHASE C (Tier 3) — migrate the 12 endpoints

Now it is constrained edits, and Tier 3 applies. The 12: `version-heartbeat`, `fleet-create`,
`fleet-join`, `fleet-status`, `fleet-map`, `fleet-analytics`, `fleet-leave`, `failure-report`,
`fix-confirmed`, `community-markers-write`, `community-position`, `config-backup`.

Per endpoint, one replacement. Pattern (anchor verified in `version-heartbeat.php`):

`old`:
```php
if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) {
```
`new`: replace the whole shared-key block with `require_once __DIR__.'/device-auth.php';
$device_token = verify_device_request();`

**Constraints — state these in the dispatch:**
1. **One endpoint per dispatch.** Do not batch 12. If one is wrong the others are still trustworthy.
2. **`$device_token` must no longer be read from the header** anywhere below the auth block.
3. Do not touch `error_reporting(0)`, the `ALTER TABLE` block, or any SQL. Out of scope.
4. **Transition period:** accept *either* a valid signature *or* the legacy key, with **every legacy use
   logged**, until all Pis are migrated. Then remove the legacy path. Do not flip 12 endpoints and the
   whole fleet in one step — that is how a boat loses connectivity at sea.

---

## 5. PHASE D (Tier 3) — remove the blind UPSERT

**Target:** `version-heartbeat.php`, the statement at ~line 82.

`old` — `INSERT INTO amboat_devices … ON DUPLICATE KEY UPDATE …`
`new` — `UPDATE amboat_devices SET … WHERE device_token = ?`, and if `affected_rows === 0`, return
**404 unknown_device**. A device row is created *only* by enrolment + approval (Phase A), never by a
heartbeat.

⚠ **The code comment above that statement reads: `// device_token has UNIQUE constraint so INSERT … ON
DUPLICATE KEY UPDATE is safe`.** It is safe against *duplicate rows*. It is not safe against
*unauthorised registration*, which is what it is guarding. **Delete the comment along with the
statement** — leaving it would tell the next reader the construct is fine. An unsourced code comment is
a hypothesis, not a fact.

⚠ **SESSION_LOG records the UPDATE→UPSERT change as deliberate.** Something needed auto-registration —
probably a Pi heartbeating before it was ever registered. **Find out what, before reverting it**, or
Phase D breaks that path. This is the one place in this spec most likely to cause a regression.

---

## 6. TDD TESTS — failing first

| # | Test | Expect |
|---|---|---|
| T1 | Valid signature from an approved device | 200 |
| T2 | Valid signature, status `pending` | 403 `not_approved` |
| T3 | **Unknown `device_token` + valid legacy key** | **401, and NO row created** — this is the BUG-66 regression test |
| T4 | Tampered signature | 401 |
| T5 | Replayed nonce | 401 |
| T6 | Timestamp skewed 6 h | **explicit skew error, not a silent expiry** (registration spec section 4.2 — the Pi's RTC is unreliable; PART 17 records the boat Pi's journal 7 days out) |
| T7 | Re-enrol an existing `device_token` | 409, **public key unchanged** |
| T8 | Heartbeat from an unknown device (Phase D) | 404 `unknown_device`, no row created |
| T9 | Legacy-key request during transition | 200 **and an audit log entry written** |

**T3 and T8 are the tests that prove BUG-66 is fixed.** Everything else proves the crypto works.
`hash_equals` already worked; the defect was that any UUID could self-register.

---

## 7. DEFINITION OF DONE

- [ ] `verify_device_request()` is the single auth path for all 12 endpoints
- [ ] T3 and T8 pass — an unknown token cannot create a row by any route
- [ ] Legacy key path removed after fleet migration, with the audit log proving zero remaining users
- [ ] `device-signing.key` mode 0600, generated at first boot, **on BUG-78's strip list**
- [ ] TURN credentials moved out of a 644 file (BUG-74) — **they are in BUG-66's scope, contrary to the original record**
- [ ] The S131 finding about why UPDATE became UPSERT is resolved, not assumed
- [ ] `MASTER_SYSTEM_SPEC` section 9 updated to describe the resulting model (BUG-79)

## 8. WHAT THIS DOES NOT FIX

- **BUG-65.** Tier 2/3 remain forgeable filesystem tests. Option (a) makes only Tier 1 trustworthy.
- **BUG-72.** Deploying `version-heartbeat.php` is gated *behind* this spec by the S131 decision.
- **BUG-71.** `pair-device.php`'s 500 is unrelated and still needs cPanel access.
- **`error_reporting(0)`.** Real, and out of scope — log separately.
