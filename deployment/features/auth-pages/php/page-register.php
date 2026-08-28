<?php
/**
 * Template Name: Register Page
 *
 * AtMyBoat.com account registration — custom AODA-compliant template.
 * AODA: 20px base text, 48px touch targets, skip-to-content link, WCAG AA contrast.
 *
 * Fields: first name, last name, email, password, confirm, T&C (required), CASL (optional).
 * Creates WP user, sends email verification. Account inactive until email link clicked.
 *
 * Also handles email verification callback:
 *   /register/?action=verify&token=<token>&uid=<user_id>
 *
 * Deploy to: wp-content/themes/twentytwenty-child/page-register.php
 * WP Admin:  Create page with slug "register", assign template "Register Page"
 */

// Redirect logged-in users — nothing to do here
if ( is_user_logged_in() ) {
    wp_safe_redirect( home_url( '/my-account/' ) );
    exit;
}

// ── Email verification callback ────────────────────────────────────────────
$action         = sanitize_text_field( wp_unslash( $_GET['action'] ?? '' ) );
$verify_success = false;
$verify_error   = '';

if ( $action === 'verify' ) {
    $uid   = absint( $_GET['uid'] ?? 0 );
    $token = sanitize_text_field( wp_unslash( $_GET['token'] ?? '' ) );

    if ( $uid > 0 && $token !== '' ) {
        $stored = get_user_meta( $uid, 'atmyboat_verify_token', true );
        if ( $stored !== '' && hash_equals( (string) $stored, $token ) ) {
            update_user_meta( $uid, 'atmyboat_email_verified', '1' );
            delete_user_meta( $uid, 'atmyboat_verify_token' );
            $verify_success = true;
        } else {
            $verify_error = 'This verification link is invalid or has already been used.';
        }
    } else {
        $verify_error = 'Invalid verification link — the URL appears to be incomplete.';
    }
}

// ── Registration form submission ───────────────────────────────────────────
$reg_error   = '';
$reg_success = false;
$reg_email   = ''; // kept for the success screen
$form        = [ 'first_name' => '', 'last_name' => '', 'email' => '', 'alias' => '', 'code_input' => '' ];

// BUG-63: device-registration gate helpers — claim code BEFORE creating any user.
// require_once here so the functions are available for the submission block below.
require_once __DIR__ . '/device-registration.php';

if ( $_SERVER['REQUEST_METHOD'] === 'POST' && isset( $_POST['atmyboat_register_nonce'] ) ) {

    if ( ! wp_verify_nonce( wp_unslash( $_POST['atmyboat_register_nonce'] ), 'atmyboat_register_action' ) ) {
        $reg_error = 'Security check failed. Please refresh and try again.';
    } else {
        $first      = sanitize_text_field( wp_unslash( $_POST['first_name']       ?? '' ) );
        $last       = sanitize_text_field( wp_unslash( $_POST['last_name']        ?? '' ) );
        $alias      = sanitize_user(       wp_unslash( $_POST['alias']            ?? '' ), true );
        $email      = sanitize_email(      wp_unslash( $_POST['email']            ?? '' ) );
        $pw         =                      wp_unslash( $_POST['password']         ?? ''   );
        $pw2        =                      wp_unslash( $_POST['password_confirm'] ?? ''   );
        $code_input = sanitize_text_field( wp_unslash( $_POST['code_input']       ?? '' ) );
        $tos        = ! empty( $_POST['accept_tos'] );
        $casl       = ! empty( $_POST['accept_casl'] );

        // Re-populate form on error (never passwords)
        $form = [ 'first_name' => $first, 'last_name' => $last, 'email' => $email,
                  'alias' => $alias, 'code_input' => '' ]; // never echo the code back

        if ( empty( $first ) ) {
            $reg_error = 'Please enter your first name.';
        } elseif ( empty( $last ) ) {
            $reg_error = 'Please enter your last name.';
        } elseif ( empty( $alias ) || strlen( $alias ) < 3 ) {
            $reg_error = 'Please choose a display name (at least 3 characters).';
        } elseif ( username_exists( $alias ) ) {
            $reg_error = 'That display name is already taken. Please choose another.';
        } elseif ( ! is_email( $email ) ) {
            $reg_error = 'Please enter a valid email address.';
        } elseif ( email_exists( $email ) ) {
            $reg_error = 'An account with this email already exists. <a href="' . esc_url( home_url( '/login/' ) ) . '">Sign in instead?</a>';
        } elseif ( strlen( $pw ) < 8 ) {
            $reg_error = 'Password must be at least 8 characters.';
        } elseif ( $pw !== $pw2 ) {
            $reg_error = 'Passwords do not match. Please try again.';
        } elseif ( ! $tos ) {
            $reg_error = 'You must accept the Terms of Service and Privacy Policy to create an account.';
        } elseif ( empty( $code_input ) ) {
            $reg_error = 'A d3kOS registration code is required. Open the d3kOS app to generate one.';
        } else {
            // ── BUG-63: device-tied registration gate ─────────────────────────
            // Claim the registration code ATOMICALLY before creating anything.
            // Order matters: claim, then create. Never check-then-act (race defect V5).
            $code_hash = hash( 'sha256', strtoupper( strtr( preg_replace( '/\s+/', '', $code_input ), [ 'O' => '0', 'I' => '1' ] ) ) );
            $claim = amboat_claim_registration_code( $code_input );

            if ( is_wp_error( $claim ) ) {
                $reg_error = esc_html( $claim->get_error_message() );
                amboat_registration_audit( 'redeem_fail', null, $claim->get_error_code() );
            } else {
                $device_token = $claim; // device_token returned on successful claim

                $user_id = wp_create_user( $alias, $pw, $email );

                if ( is_wp_error( $user_id ) ) {
                    // T17: roll the code back so the user can retry
                    amboat_rollback_registration_code( $code_hash );
                    amboat_registration_audit( 'redeem_fail', null, 'wp_create_user_failed' );
                    $reg_error = esc_html( $user_id->get_error_message() );
                } else {
                    // Bind account to device (D4: exactly one account per device_token)
                    global $wpdb;
                    $wpdb->insert(
                        'amboat_device_accounts',
                        [ 'device_token' => $device_token, 'user_id' => $user_id ],
                        [ '%s', '%d' ]
                    );

                    // Set display alias as display name; legal name stored private
                    wp_update_user( [
                        'ID'           => $user_id,
                        'display_name' => $alias,
                        'nickname'     => $alias,
                    ] );

                    // Legal name (first + last) stored as private user_meta — admin-visible only
                    update_user_meta( $user_id, 'atmyboat_legal_name', trim( $first . ' ' . $last ) );

                    // Default tier + consent + email verified flag
                    update_user_meta( $user_id, 'atmyboat_tier',           'T0' );
                    update_user_meta( $user_id, 'atmyboat_casl_consent',   $casl ? '1' : '0' );
                    update_user_meta( $user_id, 'atmyboat_email_verified', '0' );

                    // Generate 40-character verification token
                    $token = wp_generate_password( 40, false );
                    update_user_meta( $user_id, 'atmyboat_verify_token', $token );

                    // Build verification URL (points back to this page with query args)
                    $verify_url = add_query_arg(
                        [ 'action' => 'verify', 'token' => $token, 'uid' => $user_id ],
                        home_url( '/register/' )
                    );

                    // Send verification email via WordPress / HostPapa mail
                    $subject = 'Verify your AtMyBoat.com account';
                    $body    = "Hi {$first},\n\n"
                        . "Welcome aboard! Click the link below to verify your email address and activate your AtMyBoat.com account:\n\n"
                        . "{$verify_url}\n\n"
                        . "This link is valid for 24 hours.\n\n"
                        . "If you did not create this account you can safely ignore this email.\n\n"
                        . "— The AtMyBoat Team\n"
                        . "atmyboat.com";

                    wp_mail( $email, $subject, $body, [ 'Content-Type: text/plain; charset=UTF-8' ] );

                    amboat_registration_audit( 'account_created', $user_id, $device_token );
                    $reg_email   = $email;
                    $reg_success = true;
                }  // end: wp_create_user success
            }  // end: code gate else (claim succeeded)
        }  // end: all-validations-passed else
    }  // end: nonce-check else
}  // end: POST check

get_header();
?>
<a class="amboat-skip-link" href="#reg-main">Skip to main content</a>

<main id="reg-main" class="amboat-auth-wrap">
<style>
/* ── Register Page — scoped styles (page-register.php) ──────────────────── */
.amboat-skip-link {
    position: absolute; left: -9999px; top: 1rem; z-index: 9999;
    background: #D4A017; color: #0A2342;
    padding: 0.75rem 1.5rem; border-radius: 4px;
    font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 1rem;
    text-decoration: none;
}
.amboat-skip-link:focus { left: 1rem; }

.amboat-auth-wrap {
    min-height: 80vh;
    background: #0A2342;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 3rem 1rem 4rem;
    font-family: 'Nunito', 'Segoe UI', sans-serif;
    font-size: 1rem;
    line-height: 1.85;
    color: #F0EAD8;
}

/* Blueprint grid overlay */
.amboat-auth-wrap::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(26,122,110,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(26,122,110,.03) 1px, transparent 1px);
    background-size: 40px 40px;
}

.auth-card {
    position: relative; z-index: 1;
    background: #0D2E55;
    border: 1px solid rgba(184,120,0,.25);
    border-radius: 8px;
    width: 100%; max-width: 480px;
    overflow: hidden;
}

.auth-card-hd {
    padding: 2rem 2rem 1.5rem;
    border-bottom: 1px solid rgba(184,120,0,.15);
}
.auth-eyebrow {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.9rem; letter-spacing: .18em; text-transform: uppercase;
    color: #D4A017; margin-bottom: .5rem;
}
.auth-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(1.7rem, 4vw, 2.2rem);
    font-weight: 700; color: #F0EAD8;
    line-height: 1.2; margin: 0 0 .4rem;
}
.auth-sub {
    font-size: 1rem; color: #C8BEA8;
    line-height: 1.6; margin: 0;
}

.auth-body { padding: 2rem; }

/* Inline alert */
.auth-alert {
    padding: 1rem 1.25rem;
    border-radius: 6px;
    margin-bottom: 1.5rem;
    font-size: 1rem; line-height: 1.6;
}
.auth-alert.err {
    background: rgba(220,50,50,.12);
    border: 1px solid rgba(220,50,50,.4);
    color: #FF8080;
}
.auth-alert.ok {
    background: rgba(0,180,80,.1);
    border: 1px solid rgba(0,180,80,.3);
    color: #60D890;
}
.auth-alert a { color: #D4A017; text-decoration: underline; }

/* Form layout */
.auth-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 0;
}
@media (max-width: 440px) {
    .auth-row { grid-template-columns: 1fr; gap: 0; }
}

.auth-field { margin-bottom: 1.25rem; }

.auth-lbl {
    display: block;
    font-size: 0.9rem; font-weight: 700;
    color: #C8BEA8; letter-spacing: .04em;
    margin-bottom: .4rem;
}
.auth-lbl .hint { font-weight: 400; color: #8A8070; }

.auth-inp {
    display: block; width: 100%;
    background: rgba(10,35,66,.7);
    border: 1px solid rgba(240,234,216,.15);
    border-radius: 4px;
    color: #F0EAD8;
    font-family: 'Nunito', sans-serif; font-size: 1rem;
    padding: 0 1rem;
    height: 52px; /* AODA: ≥48px */
    transition: border-color .2s;
    box-sizing: border-box;
}
.auth-inp:focus {
    outline: none;
    border-color: #D4A017;
    box-shadow: 0 0 0 3px rgba(212,160,23,.2);
}
.auth-inp::placeholder { color: rgba(200,190,168,.4); }

.auth-divider {
    border: none;
    border-top: 1px solid rgba(240,234,216,.08);
    margin: 1.5rem 0;
}

/* Checkboxes */
.auth-check {
    display: flex; align-items: flex-start;
    gap: .85rem; margin-bottom: 1rem;
    cursor: pointer;
}
.auth-check input[type=checkbox] {
    flex-shrink: 0;
    width: 24px; height: 24px;
    margin-top: 2px;
    accent-color: #D4A017;
    cursor: pointer;
}
.auth-check-lbl {
    font-size: .95rem; color: #C8BEA8; line-height: 1.65;
}
.auth-check-lbl a { color: #D4A017; text-decoration: underline; }
.tag-opt {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; letter-spacing: .1em; text-transform: uppercase;
    background: rgba(26,122,110,.15);
    color: #22A090;
    border: 1px solid rgba(26,122,110,.3);
    padding: 2px 7px; border-radius: 2px;
    margin-left: .35rem; vertical-align: middle;
}

.auth-submit {
    display: flex; align-items: center; justify-content: center;
    width: 100%;
    background: #D4A017; color: #0A2342;
    border: none; border-radius: 4px;
    font-family: 'Nunito', sans-serif;
    font-size: 1.05rem; font-weight: 800;
    letter-spacing: .05em; text-transform: uppercase;
    height: 56px; /* AODA: ≥48px */
    cursor: pointer; text-decoration: none;
    transition: background .2s, transform .15s;
    margin-top: .5rem;
}
.auth-submit:hover { background: #E5B828; transform: translateY(-1px); }
.auth-submit:focus { outline: none; box-shadow: 0 0 0 3px rgba(212,160,23,.4); }
.auth-submit:active { transform: translateY(0); }

.auth-foot {
    text-align: center;
    padding: 1.25rem 2rem;
    border-top: 1px solid rgba(240,234,216,.08);
    font-size: .95rem; color: #8A8070;
}
.auth-foot a { color: #D4A017; text-decoration: none; font-weight: 600; }
.auth-foot a:hover { text-decoration: underline; }

/* Success screen */
.auth-big-icon { font-size: 3rem; text-align: center; display: block; margin-bottom: .75rem; }
.auth-success-hd {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.5rem; color: #F0EAD8;
    text-align: center; margin-bottom: .75rem;
}
.auth-success-p {
    font-size: 1rem; color: #C8BEA8;
    text-align: center; line-height: 1.7;
}
.auth-email-mono {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: .9rem; color: #D4A017;
    margin-top: .4rem;
}
</style>

<?php if ( $verify_success ) : ?>
<!-- ── Email Verified ──────────────────────────────────────────────────── -->
<div class="auth-card">
    <div class="auth-card-hd">
        <div class="auth-eyebrow">Email Verified</div>
        <h1 class="auth-title">You're all set!</h1>
    </div>
    <div class="auth-body">
        <div class="auth-alert ok" role="status">
            Your email address has been confirmed. Your AtMyBoat.com account is now active.
        </div>
        <a href="<?php echo esc_url( home_url( '/login/' ) ); ?>" class="auth-submit">
            Sign In to Your Account ›
        </a>
    </div>
</div>

<?php elseif ( $verify_error ) : ?>
<!-- ── Verification Failed ────────────────────────────────────────────── -->
<div class="auth-card">
    <div class="auth-card-hd">
        <div class="auth-eyebrow">Verification Failed</div>
        <h1 class="auth-title">Link not valid</h1>
    </div>
    <div class="auth-body">
        <div class="auth-alert err" role="alert"><?php echo esc_html( $verify_error ); ?></div>
        <p style="font-size:.95rem;color:#C8BEA8;line-height:1.7;">
            Check your inbox for the original verification email, or contact
            <a href="mailto:hello@atmyboat.com" style="color:#D4A017;">hello@atmyboat.com</a>
            if you need a new link.
        </p>
    </div>
</div>

<?php elseif ( $reg_success ) : ?>
<!-- ── Registration Success — Check Your Email ────────────────────────── -->
<div class="auth-card">
    <div class="auth-card-hd">
        <div class="auth-eyebrow">Account Created</div>
        <h1 class="auth-title">Check your inbox</h1>
    </div>
    <div class="auth-body">
        <span class="auth-big-icon" aria-hidden="true">✉</span>
        <p class="auth-success-hd">One step to go — verify your email</p>
        <p class="auth-success-p">
            We've sent a verification link to:<br>
            <span class="auth-email-mono"><?php echo esc_html( $reg_email ); ?></span>
        </p>
        <p class="auth-success-p" style="margin-top:1rem;">
            Click the link in that email to activate your account.
            The link expires in 24 hours. Check your spam folder if you
            don't see it within a few minutes.
        </p>
    </div>
    <div class="auth-foot">
        Already verified? <a href="<?php echo esc_url( home_url( '/login/' ) ); ?>">Sign in here</a>
    </div>
</div>

<?php else : ?>
<!-- ── Registration Form ───────────────────────────────────────────────── -->
<div class="auth-card">
    <div class="auth-card-hd">
        <div class="auth-eyebrow">AtMyBoat.com</div>
        <h1 class="auth-title">Create account</h1>
        <p class="auth-sub">Free to join — connect your d3kOS Pi to unlock cloud features.</p>
    </div>
    <div class="auth-body">

        <?php if ( $reg_error ) : ?>
        <div class="auth-alert err" role="alert" aria-live="assertive">
            <?php echo wp_kses( $reg_error, [ 'a' => [ 'href' => [] ] ] ); ?>
        </div>
        <?php endif; ?>

        <form method="post" action="<?php echo esc_url( home_url( '/register/' ) ); ?>" novalidate>
            <?php wp_nonce_field( 'atmyboat_register_action', 'atmyboat_register_nonce' ); ?>

            <div class="auth-row">
                <div class="auth-field">
                    <label class="auth-lbl" for="first_name">First name</label>
                    <input
                        class="auth-inp" type="text" id="first_name" name="first_name"
                        value="<?php echo esc_attr( $form['first_name'] ); ?>"
                        autocomplete="given-name" required aria-required="true"
                    >
                </div>
                <div class="auth-field">
                    <label class="auth-lbl" for="last_name">Last name</label>
                    <input
                        class="auth-inp" type="text" id="last_name" name="last_name"
                        value="<?php echo esc_attr( $form['last_name'] ); ?>"
                        autocomplete="family-name" required aria-required="true"
                    >
                </div>
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="alias">
                    Display name <span class="hint">(shown publicly — not your legal name)</span>
                </label>
                <input
                    class="auth-inp" type="text" id="alias" name="alias"
                    value="<?php echo esc_attr( $form['alias'] ); ?>"
                    autocomplete="nickname" minlength="3" required aria-required="true"
                    placeholder="e.g. CapnDon"
                >
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="email">Email address</label>
                <input
                    class="auth-inp" type="email" id="email" name="email"
                    value="<?php echo esc_attr( $form['email'] ); ?>"
                    autocomplete="email" required aria-required="true"
                >
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="password">
                    Password <span class="hint">(min. 8 characters)</span>
                </label>
                <input
                    class="auth-inp" type="password" id="password" name="password"
                    autocomplete="new-password" minlength="8" required aria-required="true"
                >
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="password_confirm">Confirm password</label>
                <input
                    class="auth-inp" type="password" id="password_confirm" name="password_confirm"
                    autocomplete="new-password" required aria-required="true"
                >
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="code_input">
                    d3kOS registration code <span class="hint">(from your d3kOS app)</span>
                </label>
                <input
                    class="auth-inp" type="text" id="code_input" name="code_input"
                    autocomplete="off" required aria-required="true"
                    placeholder="XXXX-XXXX-XX"
                    style="letter-spacing: 0.1em; font-family: monospace;"
                >
                <p class="auth-hint" style="font-size:18px; margin-top:0.4rem; color:#555;">
                    Open the d3kOS app on your Pi to generate a one-time registration code.
                </p>
            </div>

            <hr class="auth-divider">

            <label class="auth-check">
                <input type="checkbox" name="accept_tos" id="accept_tos"
                    required aria-required="true"
                    <?php checked( ! empty( $_POST['accept_tos'] ) ); ?>>
                <span class="auth-check-lbl">
                    I agree to the
                    <a href="<?php echo esc_url( home_url( '/terms/' ) ); ?>" target="_blank" rel="noopener noreferrer">Terms of Service</a>
                    and
                    <a href="<?php echo esc_url( home_url( '/privacy/' ) ); ?>" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
                </span>
            </label>

            <label class="auth-check">
                <input type="checkbox" name="accept_casl" id="accept_casl"
                    <?php checked( ! empty( $_POST['accept_casl'] ) ); ?>>
                <span class="auth-check-lbl">
                    Send me product updates and community news
                    <span class="tag-opt">optional</span>
                </span>
            </label>

            <button type="submit" class="auth-submit">Create Account</button>
        </form>

    </div>
    <div class="auth-foot">
        Already have an account? <a href="<?php echo esc_url( home_url( '/login/' ) ); ?>">Sign in</a>
    </div>
</div>
<?php endif; ?>

</main>
<?php get_footer(); ?>
