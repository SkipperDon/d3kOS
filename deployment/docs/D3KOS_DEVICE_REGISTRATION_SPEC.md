# d3kOS Device-Tied Forum Registration Specification

**Version:** 2.0.0
**Date:** 2026-08-22 (S127)
**Status:** Requirements Draft — awaiting operator approval
**Supersedes:** v1.0.0 (same file). v1.0.0 was **not implementable** — see §10 Defect Log.
**Related bugs:** BUG-57, BUG-60, BUG-62, BUG-63, BUG-64

---

## Executive Summary

A forum account on atmyboat.com may be created **only** by someone holding an
operator-approved d3kOS device. Blog stays public and unchanged.

Four stages:

```
1. ENROL    Pi generates an Ed25519 keypair on first boot, sends its PUBLIC key
            to atmyboat.com. Lands in a queue as `pending`.
2. APPROVE  Operator approves the device in wp-admin. This is the trust anchor.
3. ISSUE    Approved Pi asks the server for a registration code. The SERVER
            generates it, stamps it, and returns a short code + QR.
4. REDEEM   User submits code + real name + alias + email + password.
            One account is created and bound to that device.
```

**The trust anchor is operator approval (§3), not cryptography.** The signatures
prevent one device impersonating another; they cannot prove a device is genuine.
That distinction is explained in §3.1 and must not be lost in later revisions.

---

## 1. Operator Decisions Recorded (S127)

| # | Decision | Value |
|---|----------|-------|
| D1 | Who may hold an account | Anyone with a **Tier 1 or higher** device, i.e. an approved device. Tier 0 (unpaired, standalone) does not qualify. |
| D2 | Enrolment anchor | **Manual approval queue.** Per-download enrolment keys deferred until volume justifies them. |
| D3 | Per-device key | Yes — generated **on the Pi**, on first boot. |
| D4 | Accounts per device | **Exactly 1.** |
| D5 | Name handling | Real/legal name captured and stored **private** (admin-visible only). Public posts show a user-chosen **alias**. |
| D6 | Interim control | Done — `/register/` page set to Draft, self-registration off, comment moderation on (S127). |

---

## 2. Cryptography

**Ed25519 — not HMAC.** v1.0.0 specified HMAC-SHA256 while giving the server only
`SHA256(secret_key)`. HMAC is symmetric: a verifier needs the identical key, and
the hash of a key cannot verify anything. That design could not be built.

| | Pi | atmyboat.com |
|---|---|---|
| Holds | private key (32 B) | **public** key (32 B) — safe at rest |
| Operation | `sign(message, priv)` → 64 B | `verify(message, sig, pub)` → bool |

**Availability:** libsodium is bundled in PHP core from 7.2, so
`sodium_crypto_sign_verify_detached()` needs no extension install on HostPapa.
Pi side: `cryptography` (`ed25519.Ed25519PrivateKey`) or PyNaCl.

`[VERIFY BEFORE BUILD]` Confirm HostPapa's PHP version is ≥ 7.2 and that
`sodium_crypto_sign_verify_detached` exists. One-line check.

### 2.1 Key handling on the Pi

- Path: `/opt/d3kos/config/device-signing.key`
- Mode `0600`, owner `root`. Never logged, never exported, never in a backup that leaves the device.
- Added to `.gitignore` alongside `api-keys.json`, `license.json`, `device-token.json`.
- **Generated on first boot — never baked into the shipped image.** A key inside
  the `.img` would be shared by every d3kOS on earth and would void the entire
  scheme. Reuse the BUG-39 sentinel pattern (`.identity-regenerated`) so the
  master image cannot carry one.
- Re-flash generates a new keypair and a new `device_token` → the device is new
  and must be approved again. This satisfies the operator requirement that a
  change of boat ownership requires a complete reinstall and cannot inherit the
  previous owner's account.

---

## 3. The Trust Anchor — Approval Queue

### 3.1 What signatures can and cannot do

A key generated on the Pi proves *"this message came from the holder of key K."*
It does **not** prove *"K belongs to a real d3kOS install."*

The d3kOS image is a free, anonymous, public download (MASTER_SYSTEM_SPEC §12.1,
GitHub Releases), so it contains no per-copy secret. An attacker therefore skips
the download entirely: invent a UUID, generate a keypair, enrol. Every signature
they produce verifies correctly.

Nothing in the existing identity chain closes this. Verified in code S127:

| Artifact | Origin | Server-side check |
|---|---|---|
| `device_token` | `cat /proc/sys/kernel/random/uuid` — `regenerate-identity.sh:120` | none — auto-upserted |
| `installation_id` | `uuidgen \| head -c 16` — `first-boot-setup.sh:128` | none — local tier only |
| `tier` | filesystem test for `/opt/opencpn` — MASTER_SYSTEM_SPEC L3298–3311 | none |
| Pi→server auth | fleet-wide static `AMBOAT_API_KEY`, cleartext on every Pi | shared, not per-device |

`version-heartbeat.php:82` does `INSERT … ON DUPLICATE KEY UPDATE`, so any UUID
presented with the shared key self-registers a device row.

**Therefore the anchor must be a human decision.** Approval is the one thing an
attacker cannot forge.

### 3.2 Queue behaviour

- Enrolment creates a row with `status = 'pending'`. A pending device can do nothing.
- Operator reviews in wp-admin → **d3kOS → Device Approvals**.
- Actions: **Approve**, **Reject**, **Block** (reject + refuse future enrolments from that IP/email).
- Only `status = 'approved'` may request registration codes.

To make approval a judgement about a *person* rather than a random UUID, the
wizard collects a contact email and a free-text note at enrolment ("who are you,
where did you get this"). The queue shows: short device reference (first 8 chars
of `device_token`), contact email, note, source IP, first-seen timestamp, and
whether that IP or email already has approved devices.

### 3.3 Accepted cost

New users **wait** for approval — this is not self-service. At current volume
(v1.0 gated behind the security audit; external installs ≈ 0) that is minutes per
week. Recommend publishing an expected turnaround on the wizard screen.

**Scaling path (not built now):** gate the image download behind an email form
that issues a one-time enrolment key, and auto-approve devices presenting a valid
unused key. That converts "free and unlimited" into "one email per device, and
traceable." Add when manual review stops being viable.

---

## 4. Registration Codes — Server-Issued

The Pi is required to be online at registration time (operator decision), so the
code does **not** need to be self-contained. The Pi asks the server for one.

```
Pi                                          atmyboat.com
 |-- POST /device/request-code -------------->|  verify Ed25519 sig
 |    {device_token, ts, nonce, signature}    |  check status = 'approved'
 |<-- { code: "K7M4QP2X9T", expires_at } -----|  generate + store code
 |
 [wizard shows code + QR]
                                              |
 user submits code ------------------------->|  atomic claim → create account
```

This is **outbound-only from the Pi**, so it does not violate the standing rule
"no open inbound ports on the Pi, ever" (`project-v094.md`). The earlier
"website calls into the Pi" option was correctly rejected for that reason.

### 4.1 Code properties

| Property | Value | Rationale |
|---|---|---|
| Format | 10 chars, Crockford Base32 (no I/L/O/U) | ~50 bits; hand-typable; no ambiguous glyphs |
| Display | `K7M4-QP2X-9T` | grouped for readability |
| QR | `https://atmyboat.com/register?code=K7M4QP2X9T` | scan path |
| Lifetime | 15 minutes, **server-clocked** | see §4.2 |
| Uses | exactly 1, claimed atomically | see §6.2 |
| Concurrent live codes per device | 1 — issuing a new code invalidates the previous | prevents code hoarding |

### 4.2 Why the server stamps the time

The Pi's clock is unreliable on this hardware — `PROJECT_CHECKLIST.md` PART 17
records the boat Pi's journal showing "Jul 20 18:09" for services `ps` reported
as started 2026-07-27. A Pi-stamped code from a device with a bad RTC would be
rejected as "expired" the instant the user tried it, with no diagnosable cause.

Server-clocked expiry removes that failure mode entirely. The Pi's clock only
affects the `/device/request-code` call, where skew is tolerated at ±10 minutes
and produces an explicit, logged error instead of a silent user-facing failure.

### 4.3 Why the code carries no cryptography

v1.0.0 embedded `device_token + timestamp + nonce + signature` in the code
itself. The arithmetic did not work: that payload is 68–88 bytes, which
Base32-encodes to **109–141 characters** — not the 16-character
`DEV-XXXX-XXXX-XXXX-XXXX` the document displayed. It would have been QR-only,
impossible to read aloud or type. It also published `device_token` inside every
QR URL.

A server-issued opaque handle is shorter, leaks nothing, and moves all
verification to an authenticated Pi→server channel where it belongs.

---

## 5. Threat Model

| Threat | Status | What actually stops it |
|---|---|---|
| **Bot mass registration** | Mitigated | Approval queue (§3). A bot may enrol; it stays `pending` and can issue no codes. **Not** mitigated by cryptography — see §3.1. |
| **Device impersonation** | Mitigated | Enrolment binds `device_token` → public key on first sight. A second party cannot re-enrol or rotate a key for an existing token without an operator-authorised reset. |
| **Forged codes** | Mitigated | Codes exist only in the server's table. There is nothing to forge; an invented string simply misses. |
| **Code brute force** | Mitigated | ~50-bit space, 15-minute window, per-IP rate limit. |
| **QR interception / front-running** | Mitigated | 15-minute expiry, single use, atomic claim (§6.2). If beaten to it, the owner reissues; both attempts are logged against one `device_token` for audit. |
| **Replay** | Mitigated | Atomic single-use claim on the code; nonce + timestamp on Pi→server calls. |
| **Enrolment replay / key rotation attack** | Mitigated | `device_token` is unique; re-enrolment of a known token is refused and logged. Legitimate re-key requires operator reset. |
| **Tier self-elevation** | ⚠ **Out of scope, still open** | `license.json` is unsigned, mode 644 — editing `"tier": 3` grants T3 locally. Does not affect this design (approval, not tier, gates registration) but is a real defect. See §10. |
| **Fleet-wide `AMBOAT_API_KEY`** | ⚠ **Out of scope, still open** | One static secret in cleartext on every Pi authenticates 12 server endpoints. See §10. |

### 5.1 Rate limits

- **Per IP:** 10 registration submissions/hour → 15-minute block.
- **Per email:** 3 accounts/day.
- **Per device:** 1 code request/minute; 1 live code at a time.
- **No per-code lockout.** v1.0.0 locked a code after 5 failed attempts, which let
  anyone who photographed a QR deny the owner by submitting garbage five times.
  Guessing a 50-bit code is already infeasible, so the counter bought nothing and
  only created a griefing vector. Failed attempts are logged, not penalising.

---

## 6. Data Model

```sql
CREATE TABLE amboat_device_enrolments (
  device_token     VARCHAR(36)  PRIMARY KEY,
  public_key       VARBINARY(32) NOT NULL,       -- Ed25519 raw public key
  status           ENUM('pending','approved','rejected','blocked') NOT NULL DEFAULT 'pending',
  contact_email    VARCHAR(254) NULL,
  enrol_note       TEXT         NULL,
  enrolled_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  enrolled_ip      VARBINARY(16) NULL,
  reviewed_at      TIMESTAMP    NULL,
  reviewed_by      BIGINT       NULL,
  INDEX (status),
  INDEX (contact_email)
);

CREATE TABLE amboat_registration_codes (
  code_hash        CHAR(64)     PRIMARY KEY,     -- SHA256 of the issued code
  device_token     VARCHAR(36)  NOT NULL,
  issued_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at       TIMESTAMP    NOT NULL,        -- server-clocked
  status           ENUM('valid','used','superseded') NOT NULL DEFAULT 'valid',
  used_at          TIMESTAMP    NULL,
  used_by_user_id  BIGINT       NULL,
  FOREIGN KEY (device_token) REFERENCES amboat_device_enrolments(device_token),
  INDEX (device_token, status),
  INDEX (expires_at)
);

CREATE TABLE amboat_device_accounts (
  device_token     VARCHAR(36)  PRIMARY KEY,     -- D4: exactly 1 account per device
  user_id          BIGINT       NOT NULL UNIQUE,
  created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (user_id)
);

CREATE TABLE amboat_registration_audit (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  event        ENUM('enrol','approve','reject','block','code_issued',
                    'redeem_ok','redeem_fail','rate_limited') NOT NULL,
  device_token VARCHAR(36) NULL,
  user_id      BIGINT      NULL,
  ip           VARBINARY(16) NULL,
  detail       VARCHAR(255) NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (device_token), INDEX (created_at), INDEX (event)
);
```

`amboat_registration_codes` stores only `SHA256(code)`, so a database read does
not yield usable codes.

### 6.1 Store nothing needless

The issued code's plaintext is returned to the Pi once and never persisted
server-side. No signature is stored — the signature authenticates the *request*,
it is not an artifact worth keeping.

### 6.2 Redemption must be atomic

Two simultaneous submissions of the same code must not both succeed. Claim the
row first, then create the user:

```sql
UPDATE amboat_registration_codes
   SET status = 'used', used_at = NOW(), used_by_user_id = NULL
 WHERE code_hash = ? AND status = 'valid' AND expires_at > NOW();
-- proceed ONLY if affected_rows = 1
```

Create the WordPress user only after that returns 1, then backfill
`used_by_user_id`. Wrap in a transaction; on user-creation failure, roll back so
the code returns to `valid`. v1.0.0 had a check-then-act race here.

---

## 7. Interfaces

### 7.1 Pi → server

All requests carry `X-Device-Token`, `X-Timestamp`, `X-Nonce`, and
`X-Signature` (Ed25519 over `device_token|timestamp|nonce|path`, base64). Server
rejects timestamps skewed > 600 s and replayed nonces (cache them for 600 s).

```
POST /wp-json/amboat-device/v1/enrol
  Body   : { device_token, public_key (base64), contact_email, note }
  Note   : first enrolment only — signed with the key being enrolled (proof of possession)
  200    : { status: "pending" }
  409    : device_token already enrolled

GET  /wp-json/amboat-device/v1/status
  200  : { status: "pending" | "approved" | "rejected" | "blocked" }

POST /wp-json/amboat-device/v1/request-code
  200  : { code: "K7M4QP2X9T", expires_at: "2026-08-22T14:15:00Z" }
  403  : { error: "not_approved" | "already_registered" }
  429  : rate limited
```

`already_registered` enforces D4 — one account per device.

### 7.2 Pi-local (wizard)

```
GET  /api/registration/state    → { enrolment: "...", code: ..., expires_at: ... }
POST /api/registration/enrol    → triggers 7.1 enrol
POST /api/registration/code     → triggers 7.1 request-code
```

Wizard screens: **Enrol device** (collect contact email + note) → **Awaiting
approval** (poll `status`) → **Get forum code** (display code + QR).

Wizard text must be ≥ 18 px per the AODA rule, with 48×48 px minimum touch targets.

### 7.3 Registration form — `/register/`

Replaces the current template. Fields:

| Field | Required | Storage |
|---|---|---|
| Registration code | yes | consumed, not stored |
| Legal name | yes | `user_meta.atmyboat_legal_name` — **private, admin-visible only** (D5) |
| Display alias | yes | `display_name` / `nickname` — public (D5) |
| Email | yes | `user_email`; existing verification flow retained |
| Password | yes | WordPress hashing |

Alias validation: 3–30 chars, must not collide, must not look like an email.
**Legal name is never rendered on the public site** — enforce with a test.

⚠ **Honest limitation:** "real name required" is an accountability control, not a
bot filter. No software can tell that "Robert Smith" is genuine. The prevention
is the approval queue; the name is what lets you ban a person and know who they
were. The spec must not imply otherwise.

### 7.4 My Account

Existing page (`page-my-account.php`, 556 lines) is **retained**. Additions:

- Edit **alias** (public), edit **legal name** (private), email, password — unchanged flows.
- Read-only panel: bound device reference (first 8 chars) + enrolment date.
- Users cannot unbind or rebind a device. That is operator-only.

Per BUG-64, `/my-account/` needs its own security review (access control,
privilege escalation, email-change verification, rate limiting, CSRF). **Out of
scope here** — tracked separately, must not be assumed done.

---

## 8. Migration

1. Existing accounts: bulk-delete unverified Subscribers
   (`atmyboat_email_verified = '0'`) after an export for the record. Per BUG-57
   these are the ~62k bot rows.
2. Genuine existing users: flag `atmyboat_legacy = 1`, keep access, prompt for an
   alias and legal name at next login. Do not force device binding retroactively.
3. Keep `/register/` in Draft until the new form ships. It is the live hole
   (§10, BUG-63).

---

## 9. Test Plan

Playwright + PHPUnit, per the Master Standard. TDD — failing test before fix.

| # | Test | Expect |
|---|---|---|
| T1 | Enrol with a valid self-signature | `pending` |
| T2 | Request code while `pending` | 403 `not_approved` |
| T3 | Approve, then request code | code returned, `expires_at` server-clocked |
| T4 | Re-enrol an existing `device_token` | 409, no key overwrite |
| T5 | Tampered signature on request-code | 401, nothing issued |
| T6 | Replayed nonce | 401 |
| T7 | Pi clock 6 h fast → request-code | explicit skew error, **not** a silent expiry |
| T8 | Redeem valid code | account created, alias public, legal name absent from page source |
| T9 | Redeem same code twice | second fails; exactly one user exists |
| T10 | Two concurrent redemptions of one code | exactly one succeeds (§6.2) |
| T11 | Redeem after 15 min 1 s | expired |
| T12 | Second code request for a device with an account | 403 `already_registered` (D4) |
| T13 | 11 submissions from one IP in an hour | 11th → 429 |
| T14 | Issue code B while A live | A `superseded`, A unusable |
| T15 | Legal name never appears in any public HTML | pass |

---

## 10. Defect Log — v1.0.0

Recorded so they are not reintroduced.

| # | Defect | Resolution |
|---|---|---|
| V1 | HMAC verification with `SHA256(key)` — mathematically impossible. Spec line 204 contained a literal `?` where the key belonged. | Ed25519 (§2) |
| V2 | Unauthenticated enrolment endpoint — any bot could enrol a keypair and mint valid codes. Table claimed "Bot Creation: MITIGATED"; it was not. | Approval queue (§3) |
| V3 | Code length arithmetic wrong — 68–88 B payload → 109–141 chars, not the 16 shown. | Server-issued 10-char code (§4) |
| V4 | Pi-stamped expiry, on hardware with a documented bad RTC. | Server-clocked (§4.2) |
| V5 | Check-then-act race on redemption. | Atomic claim (§6.2) |
| V6 | Per-code lockout after 5 failures = free denial-of-service on the owner. | Removed (§5.1) |
| V7 | Contradiction: "failed attempts do not consume the code" vs "5 failures lock it". | Removed with V6 |
| V8 | `device_token` published inside every QR URL. | Opaque server-issued code (§4.3) |
| V9 | Two sections numbered "6". | Renumbered |

### Related defects found while reviewing — NOT in this scope

- **`page-register.php:88` calls `wp_create_user()` directly**, bypassing
  WordPress's `users_can_register` setting entirely. No CAPTCHA, no honeypot, no
  rate limit; the nonce is harvestable by any bot that GETs the page first.
  **This is the mechanism behind BUG-57/63.** → belongs in BUG-63's record.
- **`license.json` is unsigned, mode 644** — local edit to `"tier": 3` grants
  Tier 3. → new bug candidate.
- **`AMBOAT_API_KEY` is fleet-wide and cleartext** on every Pi, authenticating 12
  endpoints; `version-heartbeat.php:82` upserts any UUID presented with it. If the
  shipped `.img` carries a live key, publishing the image publishes the fleet key.
  `[UNVERIFIED — image contents not inspected]` → new bug candidate.
- **BUG-62 may be a misdiagnosis** — it was logged from
  `atmyboat.com/staging/staging/wp-admin/`, which is the known-broken double-path
  URL from BUG-61. A 404 from a broken path is not an exposed admin directory.
  Verify against a live read before acting.
- **MASTER_SYSTEM_SPEC §9.2 is stale** — "No phone-home / no telemetry / no
  license validation servers" contradicts §8.3 central sync, telemetry category
  #9, fleet management and `version-heartbeat`. This design phones home, in line
  with actual practice. §9.2 needs correcting.

---

## 11. Rollout

| Phase | Work | Gate |
|---|---|---|
| 0 | `/register/` in Draft, self-registration off, moderation on | ✅ done S127 |
| 1 | Server: 4 tables, enrol/status/request-code endpoints, Ed25519 verify, rate limits | T1–T7 pass |
| 2 | wp-admin **Device Approvals** queue | operator can approve/reject/block |
| 3 | Pi: keypair on first boot, three wizard screens, three local endpoints | on lab Pi first |
| 4 | New `/register/` form + My Account additions | T8–T15 pass |
| 5 | Publish `/register/`, migrate legacy accounts (§8) | operator approval |

Deploy order matters: **server before Pi** — a Pi that enrols against a server
without the tables will fail closed, which is safe; the reverse is not.

Pi changes go to the **lab Pi (192.168.1.237) only** until validated. The boat Pi
is 20+ fixes behind (BUG-28) and is not a deployment target for this.

---

## 12. Open Items

1. `[VERIFY]` HostPapa PHP ≥ 7.2 with libsodium (§2).
2. `[DECISION]` Do PWA users sign in with an atmyboat.com account, or a separate
   one? If the same, folding device pairing into registration means one event
   does both and Tier 1 follows automatically. Not redesigning the pairing flow
   without direction.
3. `[DECISION]` Log the four related defects in §10 as bugs?
4. `[DECISION]` Approval turnaround to publish on the wizard screen.
5. `[DEFERRED]` Gated download + one-time enrolment keys (§3.3) when manual
   review stops scaling.

---

**Status:** awaiting operator approval.
**Changed nothing outside this file.**
