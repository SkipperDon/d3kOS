# ATOMIC SPEC — BUG-111 … BUG-116 — One-event registration: Pi → atmyboat.com account

**Defect:** There is no working path from a fresh Pi to an atmyboat.com account. Five separate
defects sit between the user and a system that otherwise works: `/register/` silently accepts bad
codes and creates unlinked T0 accounts (BUG-111); the setup wizard never asks the server for a code
and its QR encodes an unusable `d3kos://` deep link (BUG-112); the QR library is CDN-only so nothing
renders offline (BUG-113); the code shown on screen carries an `R-` prefix both server validators
reject (BUG-114); and the PWA login screen contains no route to registration at all (BUG-115).
BUG-116 is a cosmetic placeholder in the same UI.
**Severity:** HIGH — registration is core, not optional. Blocks **v0.9.9.4.2** alongside BUG-108.
**Tier:** Tier 1 (Opus) authored this spec. **Every step is Tier 3 implementable.** Exact `old`/`new`
replacements only — never rewrite a file. Sections 0 and 9 are operator-only.
**Created:** 2026-09-06 (S150)
**Bug records:** `deployment/docs/V09994_BUG_FIXES.md` BUG-108, 111, 112, 113, 114, 115, 116, 119,
120, 121 — read all before editing anything. (BUG-117 is CLOSED NOT A BUG; BUG-118 is very likely
invalid — neither is in scope.)
**Fix order is a dependency chain:** BUG-111 (stop corrupting data) → BUG-113 (offline QR) →
BUG-114 (code format) → BUG-112 (wizard) → BUG-119 (existing owners) → BUG-115 (PWA) →
BUG-116 (Pi ID) → BUG-120 (approval email) → BUG-121 (identifier audit).
Do not reorder. BUG-111 must land first: every later step drives users through the endpoint it
protects.

**All gates are answered. Nothing is blocked.** G1 — wizard says "you'll get an email", no duration
quoted. G2 — both schemas read from `install-schema.php`. G3 — one `wp_mail()` on approve, to
`contact_email` or the admin address. **There is no G4 and no tier-ladder work in this spec.**

---

## Operator decisions already made (S150) — do not re-open

- **ONE EVENT.** Redeeming the Pi's code creates the atmyboat.com account **and** links the Pi, with
  Tier 1 following automatically. Device pairing folds into registration. This closes
  `MASTER_SYSTEM_SPEC.md` §12 Open Item #2, which was explicitly awaiting operator direction.
- **TIER 0 MAY REGISTER.** Open self-serve web registration stays available. The registration code is
  a **linking** mechanism, not an entry gate. This reverses `D3KOS_DEVICE_REGISTRATION_SPEC.md`
  decision D1 ("Tier 0 does not qualify"). Update D1 when this spec is executed.
- **Anonymous use is fully supported and must be stated in the UI.** Tier 0 is spec-correct
  (`MASTER_SYSTEM_SPEC.md` §9.2 as corrected, §12.1) and nothing breaks if a user never registers.

## Constraint boundaries — what this spec may NOT do

- **Must not** require a registration code for signup. An **empty** token stays permitted; only a
  token that is *present and bad* may block. Requiring one breaks open web registration.
- **Must not** remove or weaken the manual wp-admin approval queue (registration-spec D2 — "this is
  the trust anchor"). The approval delay is a designed property, not a defect to engineer around.
- **Must not** open any inbound port on the Pi. All Pi→server traffic stays outbound-initiated.
- **Must not** introduce a payment or Stripe surface. Stripe lives on atmyboat.com only, never
  in-app or on the Pi (`project-v094.md`).
- **Must not** touch `tier_service.py` at all. The OpenCPN-presence tier check is a **deliberate
  operator fallback**, not a defect (BUG-117 closed NOT A BUG, S150). Leave it exactly as it is.
- **Must not** use any font size below 18px in new or edited CSS (AODA, zero exceptions).
- **Must not** change the `/api/generate-reg-token` JSON response field names. `token`,
  `register_url`, `expires_at`, `expires_min` are the contract; `settings.html` and the new Step 6
  both consume them.

---

## 0. OPERATOR GATES — ALL ANSWERED S150. Recorded for context; nothing here blocks work.

**G1 — Approval turnaround wording.** `generate-reg-token.php:8-9` and `:138-139` confirm
`verify_device_request()` "confirms device status is 'approved'. Exits with 401/403 JSON on failure."
A device is `pending` at first boot, so **Step 6 cannot issue a code for most users** — auto-enrolment
fires 2 minutes after boot and then waits on a human. `MASTER_SYSTEM_SPEC.md` §12 Open Item #4 asks
for the approval turnaround to publish on this screen and it has never been answered.
**ANSWERED S150 — operator decision: "You'll get an email."** No turnaround time is to be published.
Wizard and Settings copy must say the user will receive an email when the Pi is approved, and must
**not** state or imply any duration. `MASTER_SYSTEM_SPEC.md` §12 Open Item #4 is closed by this.

**Dependency, already resolved:** that copy promises an email, and none is sent today. Step 6b builds
it — one `wp_mail()` call. Ship Step 6b in the same pass as Step 4's copy.

**G2 — RESOLVED S150, no longer blocking.** Both schemas were found in
`atmyboat-forum/wp-content/themes/twentytwenty-child/setup/install-schema.php` — the script that
created them. **This file is in `atmyboat-forum/`, not `Helm-OS/`**; the S135 search-both-repos rule
was the deciding factor and a first search that covered only `Helm-OS/` produced a bug that does not
exist.

- `amboat_reg_tokens` (`:126`) **has** `created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` →
  **BUG-118 is very likely invalid.** The rate-limit query is fine.
- `d3kos_pairings` (`:112`): `id, user_id, pi_id CHAR(36), device_token CHAR(36) NULL,
  vessel_name VARCHAR(80) DEFAULT '', vessel_type VARCHAR(50) DEFAULT 'powerboat',
  is_primary TINYINT(1) DEFAULT 0, paired_at DATETIME DEFAULT CURRENT_TIMESTAMP`,
  **`UNIQUE KEY pi_id (pi_id)`**, `KEY user_id (user_id)`.

**Confirmation item, not a gate:** one `SHOW CREATE TABLE amboat_reg_tokens` in phpMyAdmin would close
BUG-118 for good — `PROJECT_CHECKLIST_ARCHIVE.md:262` records seven historical `ALTER TABLE`
statements against these tables, so the creating script is strong but not final evidence. Work may
proceed without it.

**G3 — ANSWERED S150, not a gate.** There is no approval-notification email today
(`d3kos-device-auth.php` has zero `wp_mail` calls; the approve branch at `:179` only updates status).
Operator ruling: **"just send an email to notify me."** So: one `wp_mail()` in the approve branch, to
`contact_email` when set, else `get_option('admin_email')`. That is the whole requirement — see
Step 6b. No decision needed, nothing blocked.

**There is no G4.** An earlier draft invented one for a tier-ladder change. See the note below.

⚠ **BUG-117 IS CLOSED, NOT A BUG — and nothing in this spec touches `tier_service.py`.** The
OpenCPN-presence tier check is a **deliberate operator fallback**: *"I put opencpn in there as a
fallback I don't care about it."* An earlier draft of this spec raised it as an entitlement hole and
added a whole step plus an operator gate for it. That was an unrequested security inference on top of
an intentional design, and it is withdrawn. **Do not re-raise it, and do not modify `tier_service.py`.**

---

## 1. PREREQUISITES — verify before editing. Abort on any mismatch.

1. `git status` in **both** `/home/boatiq` and `/home/boatiq/Helm-OS` — both trees clean.
2. Live lab Pi reachable: `ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237 true`.
3. Canonical tree and lab Pi agree for the two templates being edited:
   `md5sum` of `setup.html` and `settings.html` must match between
   `Helm-OS/deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/` and
   `/opt/d3kos/services/dashboard/templates/` on the Pi. (At S150 they were byte-identical:
   `setup.html` = `340bb871…`, `settings.html` = `d18d6a14…`.) If they have diverged, stop and
   reconcile — do not edit over drift.
4. Download the live `page-register.php` fresh via FTP before editing it. **Never edit the repo copy
   and assume it matches production** — the S135 two-source rule. At S150 the live file was 22,660
   bytes. Search **both** `Helm-OS/` and `atmyboat-forum/` for any repo copy.
5. Confirm the endpoint still behaves as recorded:
   `ssh … 'curl -s -X POST http://localhost:3000/api/generate-reg-token'` returns
   `{"success":true,"data":{"token":"R-XXXXXXX","register_url":"https://atmyboat.com/register/?rt=XXXXXXX",…}}`.
   If it returns 401/403 the lab Pi's approval has lapsed — re-approve in wp-admin first, or Steps 4
   and 8 cannot be verified.

---

## 2. STEP 1 — BUG-111: `/register/` must refuse a bad code instead of creating an unlinked account

**Target:** live `wp-content/themes/twentytwenty-child/page-register.php`
**Anchors derived from the live file** (downloaded and read contiguously S150).

### 2.1 Replacement A — record an error for a present-but-malformed token

The `else` that reports a bad token currently sits *inside* the `preg_match` branch, so a token that
fails the pattern produces no error at all. Add the missing outer `else`.

`old` (lines 96–108):
```php
        if ( $post_token !== '' && preg_match( '/^[A-Z2-9]{7}$/', $post_token ) ) {
            $token_row = $wpdb->get_row( $wpdb->prepare(
                "SELECT token, pi_id FROM amboat_reg_tokens
                 WHERE token = %s AND expires_at > NOW() AND used_at IS NULL LIMIT 1",
                $post_token
            ) );
            if ( $token_row ) {
                $reg_token       = $post_token;
                $reg_token_pi_id = $token_row->pi_id;
            } else {
                $reg_error = 'Your registration code has expired or already been used. Return to your d3kOS dashboard and generate a new one.';
            }
        }
```

`new`:
```php
        if ( $post_token !== '' && preg_match( '/^[A-Z2-9]{7}$/', $post_token ) ) {
            $token_row = $wpdb->get_row( $wpdb->prepare(
                "SELECT token, pi_id FROM amboat_reg_tokens
                 WHERE token = %s AND expires_at > NOW() AND used_at IS NULL LIMIT 1",
                $post_token
            ) );
            if ( $token_row ) {
                $reg_token       = $post_token;
                $reg_token_pi_id = $token_row->pi_id;
            } else {
                $reg_error = 'Your registration code has expired or already been used. Return to your d3kOS dashboard and generate a new one.';
            }
        } elseif ( $post_token !== '' ) {
            // Present but malformed. Never fall through silently — that created an unlinked
            // account and showed the success screen (BUG-111). An EMPTY token stays permitted:
            // open Tier 0 registration is authorised (operator decision S150).
            $reg_error = 'That registration code is not valid. Codes are 7 characters, letters and numbers only. Check the code on your d3kOS dashboard, or leave the field blank to create an account without linking a Pi.';
        }
```

### 2.2 Replacement B — make a token error actually stop account creation

The field-validation chain never reads `$reg_error`, so an error set above is discarded and
`wp_create_user()` runs anyway. Make it the first condition.

`old` (lines 113–114):
```php
        if ( empty( $first ) ) {
            $reg_error = 'Please enter your first name.';
```

`new`:
```php
        if ( $reg_error !== '' ) {
            // A token error was already recorded above (expired, used, or malformed).
            // Abort before wp_create_user() — do not create an account we cannot link.
            // No reassignment: preserve the specific message the user needs to see.
        } elseif ( empty( $first ) ) {
            $reg_error = 'Please enter your first name.';
```

⚠ **Verify `$reg_error` is initialised to `''` before line 96.** If it is initialised `null` or not at
all, use `empty( $reg_error )` in both places instead. Read the declaration; do not assume.

### 2.3 Replacement C — tolerate the `R-` prefix on both entry paths (pairs with BUG-114)

Two normalisation sites, GET (line ~55) and POST (line ~95). Both `strtoupper(...)` the value. Strip a
leading `R-` immediately after, so a user who types the code exactly as the Pi displays it succeeds.

At the GET site, `old`:
```php
$rt_param = strtoupper( sanitize_text_field( wp_unslash( $_GET['rt'] ?? '' ) ) );
```
`new`:
```php
$rt_param = strtoupper( sanitize_text_field( wp_unslash( $_GET['rt'] ?? '' ) ) );
$rt_param = preg_replace( '/^R-/', '', $rt_param ); // BUG-114: dashboard displays the code prefixed
```

At the POST site, `old`:
```php
        $post_token = strtoupper( sanitize_text_field( wp_unslash( $_POST['reg_token'] ?? '' ) ) );
```
`new`:
```php
        $post_token = strtoupper( sanitize_text_field( wp_unslash( $_POST['reg_token'] ?? '' ) ) );
        $post_token = preg_replace( '/^R-/', '', $post_token ); // BUG-114
```

### 2.4 What NOT to change in this file

Lines 134–136 are a **correct** `if ( is_wp_error( $user_id ) ) { … } else { … }`. During S150 an
initial read that stitched non-contiguous `sed` ranges appeared to show the entire success path —
verification email included — nested inside the error branch. A contiguous read with line numbers
disproved it. **The conditional is sound. Do not "fix" it.** If a future reader believes otherwise,
re-read lines 126–190 in one contiguous block before touching anything.

---

## 3. STEP 2 — BUG-113: vendor the QR library so it works with no internet

**Targets:** `static/js/` (new file), `setup.html`, `settings.html`

1. Fetch `qrcode.min.js` (qrcodejs 1.0.0 — the exact version both templates already reference) and
   commit it to
   `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/qrcode.min.js`.
   Record its SHA256 in the BUG-113 record.
2. `setup.html` — `old` (line 1067):
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"
  onerror="document.getElementById('qr-fallback').style.display='block'"></script>
```
   `new`:
```html
<script src="/static/js/qrcode.min.js"
  onerror="document.getElementById('qr-fallback').style.display='block'"></script>
```
3. `settings.html` — `old` (lines ~680–686):
```javascript
    function _loadQrLib(cb) {
      if (window.QRCode) { cb(); return; }
      var s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
      s.onload = cb; s.onerror = cb; // cb handles missing lib gracefully
      document.head.appendChild(s);
    }
```
   `new`:
```javascript
    function _loadQrLib(cb) {
      if (window.QRCode) { cb(); return; }
      var s = document.createElement('script');
      s.src = '/static/js/qrcode.min.js';
      s.onload = cb; s.onerror = cb; // cb handles missing lib gracefully
      document.head.appendChild(s);
    }
```
4. Delete the now-false comment above `_loadQrLib` (`settings.html:679`), which reads
   "loaded from CDN only when Register section is used (internet required anyway)".
5. Regenerate `MANIFEST.md5` — a new file was added to the canonical tree.

---

## 4. STEP 3 — BUG-114: display the bare code

**Target:** `settings.html`

`old` (line 707):
```javascript
          document.getElementById('reg-token-display').textContent = d.token;
```
`new`:
```javascript
          // BUG-114: the API returns the code prefixed ("R-CDEDWMH") but both server
          // validators are /^[A-Z2-9]{7}$/. Show what the user must actually type.
          document.getElementById('reg-token-display').textContent = String(d.token).replace(/^R-/, '');
```

Do **not** change the `token` field in `app.py` — `register_url` already carries the bare code and the
response shape is a fixed contract (see Constraint boundaries). Step 2.3 strips the prefix
server-side as a second layer.

---

## 5. STEP 4 — BUG-112: Step 6 becomes a four-state registration screen

**Target:** `setup.html`

**Exact extent, read from the file S150.** Step 6 occupies `setup.html` lines **930–967**:
`930` `card-head-over` · `931` `card-head-title` · `932-937` `card-head-sub` · `938` closes
`card-head` · `939` `card-body` · `940` `pairing-box` · `941` `#qr-canvas` · `942-944`
`#qr-fallback` · `945-947` `.pairing-uuid #uuid-display` (`{{ device_uuid }}`) · `948`
`#uuid-copied` · `949-961` `.pairing-sub` prose · `962` closes `pairing-box` · `963` NEXT · `964`
Back · `965` Skip · `966-967` closers.

⚠ **The existing header copy is already close to what the operator asked for and must be preserved in
spirit** — `932-937` already reads "Connecting … is **free**", "connecting will share information
about your Pi with AtMyBoat.com", "**If you do not connect, your Pi stays completely anonymous.**",
"Skip this to continue without sharing any information." Do not discard this. Re-aim it from *pairing*
to *registration*; keep the free/anonymous/skip framing verbatim where it still applies.

⚠ **A Skip control already exists** at `965`
(`<button type="button" class="btn-skip-step" onclick="goTo(7)">Skip this to continue &rsaquo;</button>`).
Do not add a second one. Verify it is ≥48×48px and leave it wired to `goTo(7)`.

### 5.1 Why the screen has four states

`generate-reg-token.php` requires the device to be **approved** before it will issue a code
(`:8-9`, `:138-139` — `verify_device_request()` "confirms device status is 'approved'. Exits with
401/403 JSON on failure"). At first boot the device is `pending`. Therefore **the common case at Step 6
is that no code can be issued yet.** The screen must be honest about that rather than showing a broken
QR. States:

| State | Condition | What the user sees |
|---|---|---|
| **A — Offline** | fetch fails / no network | "Registration needs an internet connection. You can do this later from Settings → Community." + anonymous reassurance + Skip |
| **B — Pending approval** | endpoint returns 401/403 | "This Pi is enrolled with AtMyBoat.com and is waiting to be approved." + G1 turnaround wording + "create your account later from Settings → Community" + Skip |
| **C — Code issued** | `success: true` | QR of `register_url`, tappable link, bare 7-char code, expiry countdown |
| **D — Other error** | `success: false` | the server's message + Retry + Skip |

Every state must show the anonymity statement and a working **Skip** control. Registration is never
mandatory to finish the wizard.

### 5.2 Replace `initQR()`

`old` (lines ~1205–1216):
```javascript
  function initQR() {
    var canvas = document.getElementById('qr-canvas');
    if (!canvas || canvas.children.length > 0) return;
    if (typeof QRCode !== 'undefined') {
      new QRCode(canvas, {
        text: 'd3kos://pair/' + DEVICE_UUID, width: 200, height: 200,
        colorDark: '#000000', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.M
      });
    } else {
      document.getElementById('qr-fallback').style.display = 'block';
    }
  }
```

`new`:
```javascript
  /* BUG-112: Step 6 is a REGISTRATION screen, not a mobile-pairing screen.
     Operator decision S150 — one event: redeeming the code creates the account AND
     links this Pi, so registering IS the pairing. The old d3kos:// deep link had no
     handler on a phone camera, which is why scanning it reported "no data found". */
  function initQR() {
    var canvas = document.getElementById('qr-canvas');
    if (!canvas || canvas.children.length > 0) return;
    _regSetState('loading');
    fetch('/api/generate-reg-token', { method: 'POST' })
      .then(function (r) {
        if (r.status === 401 || r.status === 403) { _regSetState('pending'); return null; }
        return r.json();
      })
      .then(function (data) {
        if (!data) return;
        if (!data.success) { _regSetState('error', data.error || 'Unknown error.'); return; }
        var d = data.data;
        _regSetState('code', d);
        if (typeof QRCode !== 'undefined') {
          new QRCode(canvas, {
            text: d.register_url, width: 200, height: 200,
            colorDark: '#000000', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.M
          });
        } else {
          document.getElementById('qr-fallback').style.display = 'block';
        }
      })
      .catch(function () { _regSetState('offline'); });
  }
```

`_regSetState(state, payload)` is a new helper the implementer writes alongside the markup. It shows
exactly one of the four state containers, and in the `code` state fills the QR, the link `href`, the
`register_url` text, the **bare** code (`String(d.token).replace(/^R-/, '')` — BUG-114) and
`d.expires_min`.

### 5.3 Replace the Step 6 prose — exact `old`

`old` (lines 949–961, verbatim from the file):
```html
          <div class="pairing-sub">
            <strong>How to pair using your smartphone:</strong><br><br>
            &bull; <strong>Step 1 &mdash; Create a free account:</strong><br>
            On your smartphone, go to <strong>atmyboat.com/register</strong> and create your free account.<br><br>
            &bull; <strong>Step 2 &mdash; Open the d3kOS app:</strong><br>
            After signing in, open <strong>atmyboat.com/app</strong> on your smartphone.<br><br>
            &bull; <strong>Step 3 &mdash; Scan the QR code above:</strong><br>
            Tap <strong>Pair with Pi</strong> in the app, then point your smartphone camera at the QR code above to scan it.
            If the QR code does not scan, type the vessel ID shown above directly into the app.<br><br>
            &bull; <strong>Step 4 &mdash; Link your account to this Pi:</strong><br>
            Follow the on-screen steps in the app to link your account to this vessel.
            Your phone is now paired and can monitor your Pi remotely.
          </div>
```

Every one of those four steps is now wrong: Step 1 sends the user to the **bare** URL with no code
(the BUG-111 unlinked-account path), Step 2 sends them to a PWA with no registration route (BUG-115),
Step 3 tells them to scan a QR no camera can read (BUG-112) and to type a "vessel ID" the server has
never seen (BUG-121), and Step 4 describes an in-app linking flow that the one-event decision removes.

`new` — replace the single `.pairing-sub` div with four sibling state containers, exactly one visible
at a time, driven by `_regSetState()`. Structure to implement:

```html
          <div class="pairing-sub" id="reg-state-loading">Contacting AtMyBoat.com&hellip;</div>
          <div class="pairing-sub" id="reg-state-code"    style="display:none;"><!-- QR + link + bare code + expiry --></div>
          <div class="pairing-sub" id="reg-state-pending" style="display:none;"><!-- awaiting approval --></div>
          <div class="pairing-sub" id="reg-state-offline" style="display:none;"><!-- no internet --></div>
          <div class="pairing-sub" id="reg-state-error"   style="display:none;"><span id="reg-state-error-msg"></span></div>
```

Copy requirements per state (final wording is the implementer's, these are the constraints):

- **Anonymity first, and unconditional:** registering is optional; d3kOS works fully without an
  account; the Pi does not require one to navigate, monitor the engine, or keep a boat log.
- **What Tier 1 adds, and that it is free:** mobile app, cameras, voice assistant, anchor alerts,
  cloud sync, data export, community map. Tier 1 is free — say so, because "upgrade" reads as paid.
- **One event:** completing the form both creates the account and links this Pi. The user does not
  register twice, even though enrolment and account creation are separate underneath.
- **Approval expectation:** say the user will receive an email when the Pi is approved. **Quote no
  duration** (operator decision G1). ⚠ Blocked on **G3/BUG-120** — that email does not exist yet.
- **`{{ device_uuid }}` at lines 945-947 must be RE-LABELLED, not just kept.** Per BUG-121 it is the
  `/etc/machine-id`-derived value, **not** the `pi_id` the server knows (`pi_id` = `device_token`).
  Leaving it captioned as a vessel/pairing ID perpetuates the defect. Keep it and `copyUUID()` only as
  a clearly-labelled **support/diagnostic** identifier, or remove it from this screen. It must never
  again be presented as something to type into an app or a form.
- 18px minimum on every new element, 48×48px minimum on the Skip and Retry controls.

### 5.4 Keep `goTo(6)` → `initQR()` wiring

The call site (`setup.html:~1176`, `if (n === 6) initQR();`) is unchanged. But `initQR()` now performs
a network request, so it must be idempotent — the `canvas.children.length > 0` guard alone is no
longer sufficient once state containers exist. Add a module-level `_regRequested` flag and return
early if a request is already in flight or has succeeded.

---

## 5A. STEP 4b — BUG-119: one QR must work for an existing owner too

**Target:** live `page-register.php`

An owner who already has an account and sets up a second Pi scans the same registration QR and is
silently bounced — the code is discarded before it is read.

`old` (lines 19–22):
```php
// Redirect logged-in users — nothing to do here
if ( is_user_logged_in() ) {
    wp_safe_redirect( home_url( '/my-account/' ) );
    exit;
}
```

`new` — branch on whether a code is present:
```php
// Logged-in visitors: if they arrived with a registration code, LINK the Pi to the
// account they already have instead of throwing the code away (BUG-119). The
// "nothing to do here" assumption predates this URL carrying a device-linking token.
if ( is_user_logged_in() ) {
    $rt_linked = strtoupper( sanitize_text_field( wp_unslash( $_GET['rt'] ?? '' ) ) );
    $rt_linked = preg_replace( '/^R-/', '', $rt_linked ); // BUG-114
    if ( $rt_linked !== '' && preg_match( '/^[A-Z2-9]{7}$/', $rt_linked ) ) {
        $link_result = atmyboat_link_pi_from_token( get_current_user_id(), $rt_linked );
        wp_safe_redirect( add_query_arg( 'pi_link', $link_result, home_url( '/my-account/' ) ) );
        exit;
    }
    wp_safe_redirect( home_url( '/my-account/' ) );
    exit;
}
```

**`atmyboat_link_pi_from_token( $user_id, $token )` is new** and must be written in
`inc/registration.php` (not inline in the template). It returns a short status slug for the redirect
notice — `linked`, `expired`, `invalid`, or `already`. It must:

1. Look the token up in `amboat_reg_tokens` with the **same** conditions used at line 96
   (`expires_at > NOW() AND used_at IS NULL`) and read its `pi_id`.
2. **Reuse the existing pairing logic — do not duplicate it.** `mobile/pair-device.php`'s
   `atmyboat_confirm_pairing()` already derives `is_primary` by counting the account's existing rows
   (`SELECT COUNT(*) FROM d3kos_pairings WHERE user_id = %d`), upserts `d3kos_pairings`, and queues a
   `pair_confirmed` command on `amboat_command_queue`. All three are still required on this path — the
   Pi learns it was paired by polling that queue. Factor the shared body out rather than copying it.
3. Set `used_at` on the token.
4. Be idempotent: re-scanning an already-redeemed code must return `already`, not create a duplicate
   row or a second queue command.

`/my-account/` needs to render the four `pi_link` notices. Read that template before adding them.

**Schema — read from `install-schema.php:112` (in `atmyboat-forum/`), no longer inferred:**
```sql
id INT UNSIGNED AUTO_INCREMENT, user_id BIGINT UNSIGNED NOT NULL, pi_id CHAR(36) NOT NULL,
device_token CHAR(36) NULL, vessel_name VARCHAR(80) NOT NULL DEFAULT '',
vessel_type VARCHAR(50) NOT NULL DEFAULT 'powerboat', is_primary TINYINT(1) NOT NULL DEFAULT 0,
paired_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (id), UNIQUE KEY pi_id (pi_id), KEY user_id (user_id)
```

⚠⚠ **`UNIQUE KEY` is on `pi_id` ALONE, not `(user_id, pi_id)`. This changes the design and must be
handled explicitly.** A Pi can belong to exactly one account — that is registration-spec **D4 enforced
at the database level**. Consequences:

1. `pair-device.php`'s `ON DUPLICATE KEY UPDATE` list is `vessel_name`, `vessel_type`, `paired_at` —
   **`user_id` is deliberately not updated.** So if user A owns Pi X and user B redeems a code for
   Pi X, the row silently stays with user A while the query reports success. **`atmyboat_link_pi_from_token()`
   must detect this and return a distinct status** (`owned_by_other`) with a clear message — never a
   false success. Check the existing row's `user_id` **before** writing.
2. `is_primary` is derived by counting the account's existing rows, so the first Pi linked to an
   account becomes primary. That logic is correct as written — reuse it, do not reimplement.
3. `vessel_name` and `vessel_type` are supplied by the `/pair-device/` form and have **no source on
   the registration path**. Both have safe DB defaults (`''` and `'powerboat'`), so omit them and let
   the defaults apply, or read the vessel name the Pi already holds if it is available at redemption.
   **Do not invent a value.**
4. `device_token` is `NULL`-able here, and `amboat_reg_tokens` already stores `device_token` alongside
   `pi_id` — populate it from the token row so the two tables agree.

**Remaining confirmation (not blocking):** `install-schema.php` is the creating script, and
`PROJECT_CHECKLIST_ARCHIVE.md:262` records seven historical `ALTER TABLE` statements against these
tables (including one adding `last_seen_at` to `d3kos_pairings`, which the definition above does not
show — so production has at least one column the script does not). One `SHOW CREATE TABLE
d3kos_pairings` closes the gap. Write against the columns listed above; they are all present.

---

## 6. STEP 5 — BUG-115: give the PWA a route to registration

**Target:** live `/app/app.js` on HostPapa (and any repo copy — search **both** `Helm-OS/` and
`atmyboat-forum/`).

`screens.login` is defined at **line 420** and builds its DOM with an `el()` helper — **not** template
strings or `innerHTML`. An HTML snippet will not work here. The append block is at lines 472–490.

`old` (the tail of the `container.appendChild` call, verbatim):
```javascript
      el('div', { class: 'field' },
        el('label', { for: 'login-pass' }, 'Password'),
        passwordInput,
      ),
      submitBtn,
    )
  );
```

`new`:
```javascript
      el('div', { class: 'field' },
        el('label', { for: 'login-pass' }, 'Password'),
        passwordInput,
      ),
      submitBtn,
      // BUG-115: the login screen had no route to registration at all — the operator
      // reported "there is no way for a user to register" from exactly this screen.
      el('p', { class: 'login-register-hint' },
        'No account yet? ',
        el('a', { href: 'https://atmyboat.com/register/' }, 'Create one'),
      ),
    )
  );
```

Add a `.login-register-hint` rule to the app's stylesheet — centred, `margin-top: 18px`,
**`font-size: 18px` minimum** (AODA). Do not inline the styles; the surrounding code uses classes.

⚠ **Verify the `el()` signature before editing.** It is used throughout as
`el(tag, attrsObject, ...children)` with plain strings accepted as text children (see lines 474–489),
but read its definition to confirm it handles a bare string child and an `href` attribute — do not
assume from usage alone.

`/app` is a physical directory served by Apache with no WordPress in the path, so there is no PHP
templating available; this is a static edit to the JS bundle. **Bump the service-worker cache version
in `/app/sw.js`** or installed PWAs will keep serving the cached old bundle indefinitely.

Bump the service-worker cache version so the change actually reaches installed PWAs. Find the version
constant in `/app/sw.js`; a shipped PWA will otherwise serve the cached old bundle indefinitely.

---

## 7. STEP 6 — BUG-116: render the real Pi ID

**Target:** `settings.html:~648`

`old`:
```html
              <span class="info-v" style="font-family:'Chakra Petch',monospace;color:var(--g-txt);">d3k-2024-boatiq-001</span>
```
`new`:
```html
              <span class="info-v" style="font-family:'Chakra Petch',monospace;color:var(--g-txt);">{{ device_token }}</span>
```

⚠ **`device_token`, NOT `device_uuid` — this was verified, not assumed.** Per BUG-121, the server's
`pi_id` **is** the device token: `app.py:528` sends `json={'pi_id': device_token}`. The
`/etc/machine-id`-derived `device_uuid` is a different value the server has never seen, so displaying
it as "Pi ID" would be wrong in exactly the way that made mobile pairing dead.

**No route change is needed.** The Settings render call at `app.py:489-498` already passes
`device_token=device_token` (read from `/opt/d3kos/config/device-token.json` at `:484-488`) and does
**not** pass `device_uuid` — so `{{ device_token }}` resolves and `{{ device_uuid }}` would render
empty. `app.py:255` and `:304` are both `setup.html` renders, not Settings.

**Handle the empty case:** `:487-488` falls back to `device_token = ''` when the file is missing or
unparseable — the correct state on a Pi that has not completed setup. Render "Not yet enrolled" rather
than an empty box.

---

## 7A. STEP 6b — BUG-120: build the approval email the wizard promises

**Target:** `wp-content/plugins/d3kos-device-auth/d3kos-device-auth.php` (HostPapa live), possibly
`auto_enrol.py` (canonical tree).

**Operator ruling: "just send an email to notify me." One `wp_mail()` call. Keep it that small.**

1. In the approve branch — where `$new_status` is set at `:179` — call `wp_mail()`.
2. Recipient: the enrolment row's `contact_email` if it has a value, else
   `get_option('admin_email')`. That one-line fallback covers the NULL case; `contact_email` stays
   `'required' => false` and **the Pi-side enrolment payload does not change.**
3. Plain text, matching `page-register.php:180`'s existing style
   (`[ 'Content-Type: text/plain; charset=UTF-8' ]`). No HTML template.
4. Body: the Pi is approved, and to register open Settings → Community on the Pi (or the wizard's
   Step 6). **Do not embed a registration code** — codes have a 30-minute TTL and would be expired on
   arrival.
5. **Do not** build a rejection email. Not requested.

⚠ **Do not expand this step.** An earlier draft turned it into an operator decision about making
`contact_email` mandatory, changing `auto_enrol.py`, and cross-version enrolment compatibility. That
was withdrawn on operator instruction as over-engineering a one-line requirement.

**Verification:** approve a device in wp-admin and confirm a real email arrives.

---

## 7B. STEP 6c — BUG-121: stop presenting the machine-id as an identifier

**Targets:** `setup.html`, `settings.html`

`grep -n "DEVICE_UUID\|device_uuid" setup.html settings.html` and audit **every** remaining hit. After
Steps 4 and 6 the only legitimate use is a clearly-labelled support/diagnostic identifier. Any hit
that still presents it as a pairing ID, vessel ID, or something to type into a form or app is a
residual instance of this bug. `setup.html:918`, `:1050` and `:945-947` are the known sites.

No code change is required in `app.py` — `_get_device_uuid()` is correct for what it is, and
`pi_id`/`device_token` is correct for the server. This step is purely about not lying to the user
about which identifier matters.

---

## 8. STEP 7 — TDD: Playwright UI tests, written and FAILING before Steps 2–7

**Non-negotiable.** These tests are also the standing operator ask approved in S148 and S149 and not
yet started. Write them first; watch them fail; then implement.

`deployment/v0.9.9.4/tests/registration-flow.spec.ts` — real DOM assertions, no `curl`, no
backend-only checks. `--workers=1`. Confirm chromium can launch before trusting any result:
`LD_LIBRARY_PATH="$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu"`.

| # | Test | Asserts |
|---|---|---|
| T1 | Step 6 renders a QR whose payload is an `https://atmyboat.com/register/?rt=` URL | read the `<canvas>`/`<img>` the library produced; assert **no** `d3kos://` string anywhere in the Step 6 DOM |
| T2 | Step 6 with the QR library present but the endpoint returning 403 | shows the pending-approval state, no broken QR, Skip is present and 48×48px+ |
| T3 | Step 6 with the network stubbed to fail | shows the offline state naming Settings → Community; Skip present |
| T4 | Step 6 offline-asset test — block `cdnjs.cloudflare.com` at the route level | QR still renders (proves BUG-113 fixed) |
| T5 | Displayed code matches `/^[A-Z2-9]{7}$/` | no `R-` prefix in `#reg-token-display` (Settings) or the Step 6 code element |
| T6 | Anonymity copy present in **all four** Step 6 states | the words that state registration is optional are visible in each state |
| T7 | Every new/edited element ≥18px | computed style, not the CSS token — measure it (standing rule) |
| T8 | Skip completes the wizard | wizard reaches its final step with no account and no error |

**Server-side tests for BUG-111** — `deployment/v0.9.9.4/tests/test_register_token_guard.py`, run
against a **local PHP fixture or staging, never production**:

| # | Case | Expected |
|---|---|---|
| T9 | empty `reg_token` + valid fields | account created, T0, no Pi link, success screen |
| T10 | `reg_token=R-CDEDWMH` | visible error, **no account created** |
| T11 | expired valid-format 7-char code | visible error, **no account created** |
| T12 | already-used code | visible error, **no account created** |
| T13 | fresh valid code | account created, `used_at` set, `atmyboat_pending_pi_id` written |
| T14 | `?rt=R-CDEDWMH` on GET | prefix stripped, form pre-fills the bare code, no format-error banner |

T10–T12 are the regression guards for BUG-111 and must fail against the current live file before the
Step 1 edits, and pass after.

---

## 9. STEP 8 — OPERATOR VERIFICATION — the only verification that counts

Backend `curl` is **not** verification. This rule was recorded S148, violated S149, and is why BUG-108
was wrongly marked FIXED. The acceptance test is physical:

1. Flash or reset a Pi to first-boot state. Reach the wizard on the touchscreen.
2. Advance to Step 6. **Expect the pending-approval state** unless the device is already approved.
3. Approve the device in wp-admin. Return to the Pi, Settings → Community → Get Registration Code.
4. **Scan the QR with a phone camera.** It must open `https://atmyboat.com/register/?rt=<code>` with
   the code pre-filled — not "no data found".
5. Complete the form on the phone. Verify the email arrives and the link activates the account.
6. Confirm the Pi reaches Tier 1 and `atmyboat_pending_pi_id` is set for that user.
7. Repeat step 4 with the Pi's internet disconnected — the QR must still **render** (BUG-113). Note
   that an offline Pi cannot *issue* a code; state A is the correct outcome there.
8. Type the code by hand instead of scanning (BUG-114). It must succeed.
9. Open `/app` logged out on a phone; the create-account link must be present and land on `/register/`
   (BUG-115).

Record each step's observed result in the BUG record. "Verified" without a step-by-step observation is
not acceptable for this spec.

---

## 10. ROLLBACK

- **Pi templates + static JS:** `git checkout` the canonical tree, redeploy, restart
  `d3kos-dashboard.service` (templates require a restart; static assets do not).
- **HostPapa `page-register.php` and `/app/app.js`:** back up the live file to
  `.aao-backups/<ts>_S150/mirrored/<path>.bak` **before** upload — state the path and wait for
  acknowledgement per AAO §18. Restore by re-uploading the `.bak`.
- **DB:** Steps 2–7 make no schema change. If G2 reveals a missing column, that fix is BUG-118 and is
  scoped separately.

---

## 11. DEFINITION OF DONE

- [ ] All gates answered S150 — nothing outstanding
- [ ] T1–T14 written, failing first, then all passing
- [ ] BUG-120 approval email sends and was received at a real address
- [ ] BUG-121 audit: no remaining `DEVICE_UUID` use presents it as a pairing or registration ID
- [ ] BUG-119: `owned_by_other` path tested — a code for a Pi already owned by another account must
      show a clear error, never a false success
- [ ] `tier_service.py` **unmodified** — confirm with `git diff`
- [ ] `./tests/run-all.sh` exits zero — the only trustworthy runner
- [ ] Linter clean; no font-size below 18px anywhere touched
- [ ] Section 9 walked physically by the operator, each step's result recorded
- [ ] BUG-111 … BUG-116 records updated with fix + evidence; BUG-108 status revisited
- [ ] `MANIFEST.md5` regenerated (a new static file was added)
- [ ] Registration-spec D1 amended to reflect "Tier 0 may register"
- [ ] `MASTER_SYSTEM_SPEC.md` §12 Open Item #2 closed, citing the one-event decision
- [ ] **User manual §17.4 REWRITTEN** (not merely "re-checked") — six specific changes:
      (1) its current **Step 4 "go to `atmyboat.com/pair-device/`" is deleted for new users** — under
      the one-event decision, redeeming the code links the Pi in the same action;
      (2) the **setup wizard is documented as a registration surface** — §17.4 currently mentions only
      Settings, so a first-boot user following the manual never learns Step 6 exists;
      (3) state that approval is a **manual human step and the user will receive an email**, with **no
      turnaround time quoted** (operator decision G1);
      (4) state plainly that **registration is optional and Tier 1 is free** — list what Tier 0 keeps
      and what Tier 1 adds;
      (5) add the **existing-owner / second-Pi** path (BUG-119): sign in, scan, the Pi links to the
      current account;
      (6) codes are **7 characters** and expire in **30 minutes** — the manual must match the
      validator, not the prefixed `R-` form (BUG-114).
      Version-bump the manual header and re-deploy to atmyboat.com's manual page.
- [ ] Release Package Manifest produced (a Pi deploy occurred)

---

## 12. WHAT THIS SPEC DELIBERATELY DOES NOT DO

**Coverage:** BUG-108 (via decomposition), 111, 112, 113, 114, 115, 116, 119, 120, 121 are all
specified. BUG-109 and BUG-110 were fixed in S149.

Genuinely excluded:

- **BUG-117 — CLOSED, NOT A BUG.** The OpenCPN-presence tier check is a deliberate operator fallback.
  `tier_service.py` must not be touched. **Do not re-raise this.**
- **BUG-118's fix** — because there is nothing to fix. `created_at` exists (`install-schema.php:126`).
  One `SHOW CREATE TABLE` closes the record.
- **Removing the `d3kos://pair/` scheme from the PWA.** Step 4 stops the wizard *using* it and Step 6c
  stops presenting the machine-id as an identifier, but any handler inside the PWA is left alone.
  Deleting it needs its own audit of the mobile client.
- **Anything in `tier_service.py`.** Not touched, by instruction.
- **MailPoet auto-create-user (BUG-57 G8).** Still an unconfirmed account-creation vector, unrelated
  to this path.
- **Rewriting the PWA login screen.** One link and one CSS class are added. No redesign.
- **The `last_seen_at` column** on `d3kos_pairings` (`PROJECT_CHECKLIST_ARCHIVE.md:262`) — production
  has it, `install-schema.php` does not show it. Nothing here writes it; do not start.

**Corrections to this spec's own first draft, recorded so the reasoning is auditable:**
1. The second-Pi case was called an unsolved design gap on the strength of D4. **Wrong** —
   multi-Pi-per-account is the designed model (`d3kos_pairings` + `is_primary`), D4 constrains the
   device side, and it is now Step 4b.
2. BUG-117 was first marked "out of scope" by unrequested judgment, then over-corrected into a full
   step plus an operator gate. **Both were wrong.** It is not a bug at all — the OpenCPN check is the
   operator's deliberate fallback, and the security framing was an inference nobody asked for. The
   step and gate are removed and the bug is closed. Lesson: a filesystem check that resembles the
   BUG-65 pattern is not automatically a defect; confirm scope before raising one.
5. BUG-120 was inflated into a decision matrix (mandatory `contact_email`, `auto_enrol.py` payload
   changes, cross-version compatibility) when the requirement was one `wp_mail()` call.
3. BUG-118 was logged as a MEDIUM defect from a search that covered only `Helm-OS/`. The schema was in
   `atmyboat-forum/`. **The S135 search-both-repos rule was the deciding factor, twice.**
4. Steps 4, 5 and 4b originally carried "read the file and derive the anchor" instructions instead of
   exact replacements. That pushed the spec author's job onto the implementer and is corrected — every
   anchor above is now read from its target file.
- **Removing the `d3kos://pair/` mechanism.** Step 6 stops *using* it, but the scheme and any PWA
  handling stay in place. Deleting it needs its own audit.
- **MailPoet auto-create-user (BUG-57 G8).** Still an unconfirmed account-creation vector, unrelated
  to this path.
- **Rewriting the PWA login screen.** One link is added. No redesign.
