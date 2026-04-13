<?php
/**
 * Template Name: My Account Page
 *
 * AtMyBoat.com account management — requires login.
 * AODA: 20px base text, 48px touch targets, skip-to-content, WCAG AA contrast.
 *
 * Sections:
 *   - Account overview (display name, email, tier, Pi paired status)
 *   - Change Password (wp_check_password + wp_set_password)
 *   - Change Email (wp_update_user + re-verification email)
 *   - Data & Privacy (GDPR Art.15 export as JSON + Art.17 account deletion)
 *
 * Data export handled via GET ?action=export_data&nonce=<nonce>
 * All POST actions distinguished by the hidden `account_action` field.
 * Each action has its own nonce keyed by action name.
 *
 * Deploy to: wp-content/themes/twentytwenty-child/page-my-account.php
 * WP Admin:  Create page with slug "my-account", assign template "My Account Page"
 */

// Require login
if ( ! is_user_logged_in() ) {
    wp_safe_redirect(
        add_query_arg(
            'redirect_to',
            urlencode( home_url( '/my-account/' ) ),
            home_url( '/login/' )
        )
    );
    exit;
}

$current_user = wp_get_current_user();
$user_id      = $current_user->ID;
$tier         = get_user_meta( $user_id, 'atmyboat_tier',         true ) ?: 'T0';
$pi_paired    = get_user_meta( $user_id, 'atmyboat_pi_paired',    true ) === '1';
$casl         = get_user_meta( $user_id, 'atmyboat_casl_consent', true ) === '1';

// ── Handle data export (GET) — must run before get_header() ───────────────
if ( isset( $_GET['action'] ) && $_GET['action'] === 'export_data' ) {
    $nonce = wp_unslash( $_GET['nonce'] ?? '' );
    if ( ! wp_verify_nonce( $nonce, 'amboat_export_' . $user_id ) ) {
        // Invalid nonce — fall through to normal page render with error
        $export_error = true;
    } else {
        $export = [
            'account' => [
                'user_id'      => $user_id,
                'first_name'   => $current_user->first_name,
                'last_name'    => $current_user->last_name,
                'email'        => $current_user->user_email,
                'display_name' => $current_user->display_name,
                'registered'   => $current_user->user_registered,
            ],
            'preferences' => [
                'tier'         => $tier,
                'pi_paired'    => $pi_paired,
                'casl_consent' => $casl,
            ],
            'generated_at' => gmdate( 'Y-m-d\TH:i:s\Z' ),
            'note'         => 'AtMyBoat.com stores only your account data. '
                . 'Boat sensor data is processed on your Pi and is not stored on our servers. '
                . '(GDPR Article 15 export)',
        ];
        $json = wp_json_encode( $export, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE );
        header( 'Content-Type: application/json; charset=utf-8' );
        header( 'Content-Disposition: attachment; filename="atmyboat-data-export-' . date( 'Y-m-d' ) . '.json"' );
        header( 'Cache-Control: no-store' );
        echo $json; // phpcs:ignore WordPress.Security.EscapeOutput
        exit;
    }
}

// ── POST action handlers ───────────────────────────────────────────────────
$action_done  = ''; // success key
$action_error = isset( $export_error ) ? 'Export link is invalid. Please try again.' : '';

if ( $_SERVER['REQUEST_METHOD'] === 'POST' && isset( $_POST['account_action'] ) ) {

    $act   = sanitize_key( wp_unslash( $_POST['account_action'] ) );
    $nonce = wp_unslash( $_POST['atmyboat_account_nonce'] ?? '' );

    if ( ! wp_verify_nonce( $nonce, 'amboat_acct_' . $act ) ) {
        $action_error = 'Security check failed. Please refresh and try again.';
    } elseif ( $act === 'change_password' ) {

        $pw_cur = wp_unslash( $_POST['pw_current'] ?? '' );
        $pw_new = wp_unslash( $_POST['pw_new']     ?? '' );
        $pw_cf  = wp_unslash( $_POST['pw_confirm'] ?? '' );

        if ( ! wp_check_password( $pw_cur, $current_user->user_pass, $user_id ) ) {
            $action_error = 'Current password is incorrect.';
        } elseif ( strlen( $pw_new ) < 8 ) {
            $action_error = 'New password must be at least 8 characters.';
        } elseif ( $pw_new !== $pw_cf ) {
            $action_error = 'New passwords do not match.';
        } else {
            wp_set_password( $pw_new, $user_id );
            // wp_set_password() invalidates the current auth cookie.
            // Re-authenticate so the user stays logged in.
            wp_set_auth_cookie( $user_id, true );
            // PRG: redirect so browser refresh doesn't resubmit the POST
            // (wp_set_password changes the session token, staling any prior nonce)
            wp_safe_redirect( add_query_arg( 'action_done', 'change_password', home_url( '/my-account/' ) ) );
            exit;
        }

    } elseif ( $act === 'change_email' ) {

        $new_email = sanitize_email( wp_unslash( $_POST['new_email'] ?? '' ) );

        if ( ! is_email( $new_email ) ) {
            $action_error = 'Please enter a valid email address.';
        } elseif ( strtolower( $new_email ) === strtolower( $current_user->user_email ) ) {
            $action_error = 'That is already your current email address.';
        } elseif ( email_exists( $new_email ) ) {
            $action_error = 'That email address is already associated with another account.';
        } else {
            $result = wp_update_user( [ 'ID' => $user_id, 'user_email' => $new_email ] );
            if ( is_wp_error( $result ) ) {
                $action_error = esc_html( $result->get_error_message() );
            } else {
                // Require re-verification for the new address
                update_user_meta( $user_id, 'atmyboat_email_verified', '0' );
                $token = wp_generate_password( 40, false );
                update_user_meta( $user_id, 'atmyboat_verify_token', $token );

                $verify_url = add_query_arg(
                    [ 'action' => 'verify', 'token' => $token, 'uid' => $user_id ],
                    home_url( '/register/' )
                );
                wp_mail(
                    $new_email,
                    'Verify your new AtMyBoat.com email address',
                    "Hi {$current_user->first_name},\n\n"
                    . "Please verify your new email address:\n\n"
                    . "{$verify_url}\n\n"
                    . "— The AtMyBoat Team",
                    [ 'Content-Type: text/plain; charset=UTF-8' ]
                );

                // PRG: redirect so browser refresh doesn't resubmit the POST
                wp_safe_redirect( add_query_arg( 'action_done', 'change_email', home_url( '/my-account/' ) ) );
                exit;
            }
        }

    } elseif ( $act === 'delete_account' ) {

        $confirm = sanitize_text_field( wp_unslash( $_POST['confirm_delete'] ?? '' ) );

        if ( $confirm !== 'DELETE MY ACCOUNT' ) {
            $action_error = 'Please type DELETE MY ACCOUNT exactly to confirm.';
        } else {
            require_once ABSPATH . 'wp-admin/includes/user.php';
            // Reassign any content to site admin (user 1) rather than deleting posts
            wp_delete_user( $user_id, 1 );
            wp_logout();
            wp_safe_redirect( add_query_arg( 'account_deleted', '1', home_url( '/' ) ) );
            exit;
        }
    }
}

// ── Read PRG success flag from GET (set by redirect after successful POST) ──
if ( $action_done === '' && isset( $_GET['action_done'] ) ) {
    $action_done = sanitize_key( wp_unslash( $_GET['action_done'] ) );
}

// ── Build values for template ──────────────────────────────────────────────
$export_nonce = wp_create_nonce( 'amboat_export_' . $user_id );

$tier_map = [
    'T0' => 'T0 — Tinkerer (Free)',
    'T1' => 'T1 — First Mate',
    'T2' => 'T2 — Skipper',
    'T3' => 'T3 — Captain',
];
$tier_label = $tier_map[ $tier ] ?? $tier;

$action_msg = [
    'change_password' => 'Password updated successfully.',
    'change_email'    => 'Email address updated. A verification link has been sent to your new address.',
];

get_header();
?>
<a class="amboat-skip-link" href="#account-main">Skip to main content</a>

<main id="account-main" class="amboat-acct-page">
<style>
/* ── My Account Page — scoped styles (page-my-account.php) ─────────────── */
.amboat-skip-link {
    position: absolute; left: -9999px; top: 1rem; z-index: 9999;
    background: #D4A017; color: #0A2342;
    padding: .75rem 1.5rem; border-radius: 4px;
    font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 1rem;
    text-decoration: none;
}
.amboat-skip-link:focus { left: 1rem; }

.amboat-acct-page {
    min-height: 80vh;
    background: #0A2342;
    padding: 3rem 1rem 4rem;
    font-family: 'Nunito', 'Segoe UI', sans-serif;
    font-size: 1rem; line-height: 1.85;
    color: #F0EAD8;
}
.amboat-acct-page::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(26,122,110,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(26,122,110,.03) 1px, transparent 1px);
    background-size: 40px 40px;
}

.acct-inner {
    position: relative; z-index: 1;
    max-width: 640px;
    margin: 0 auto;
}

.acct-page-eyebrow {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.9rem; letter-spacing: .18em; text-transform: uppercase;
    color: #D4A017; margin-bottom: .5rem;
}
.acct-page-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(1.8rem, 4vw, 2.4rem);
    color: #F0EAD8; margin: 0 0 .4rem;
}
.acct-page-sub {
    font-size: .95rem; color: #8A8070;
    margin: 0 0 2rem;
}

/* Global messages */
.acct-alert {
    padding: 1rem 1.25rem; border-radius: 6px;
    margin-bottom: 1.5rem; font-size: 1rem; line-height: 1.6;
}
.acct-alert.ok  { background: rgba(0,180,80,.1); border: 1px solid rgba(0,180,80,.3); color: #60D890; }
.acct-alert.err { background: rgba(220,50,50,.12); border: 1px solid rgba(220,50,50,.4); color: #FF8080; }

/* Section cards */
.acct-section {
    background: #0D2E55;
    border: 1px solid rgba(184,120,0,.25);
    border-radius: 8px;
    margin-bottom: 1.5rem;
    overflow: hidden;
}
.acct-sec-hd {
    padding: 1.1rem 1.75rem;
    border-bottom: 1px solid rgba(184,120,0,.15);
}
.acct-sec-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; letter-spacing: .15em; text-transform: uppercase;
    color: #D4A017;
}
.acct-sec-body { padding: 1.75rem; }

/* Profile row */
.acct-profile-row {
    display: flex; justify-content: space-between;
    align-items: flex-start; flex-wrap: wrap; gap: 1rem;
}
.acct-name {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.5rem; color: #F0EAD8; margin: 0 0 .25rem;
}
.acct-email-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; color: #C8BEA8;
}
.acct-badges { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; }
.badge-tier {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; letter-spacing: .1em; text-transform: uppercase;
    background: rgba(212,160,23,.12);
    color: #D4A017; border: 1px solid rgba(184,120,0,.3);
    padding: 6px 12px; border-radius: 3px;
}
.badge-pi {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; letter-spacing: .1em; text-transform: uppercase;
    background: rgba(0,180,80,.1);
    color: #60D890; border: 1px solid rgba(0,180,80,.25);
    padding: 6px 12px; border-radius: 3px;
}

/* Form elements */
.acct-field { margin-bottom: 1.25rem; }
.acct-lbl {
    display: block;
    font-size: 0.9rem; font-weight: 700;
    color: #C8BEA8; letter-spacing: .04em;
    margin-bottom: .4rem;
}
.acct-lbl .hint { font-weight: 400; color: #8A8070; }
.acct-inp {
    display: block; width: 100%;
    background: rgba(10,35,66,.7);
    border: 1px solid rgba(240,234,216,.15);
    border-radius: 4px;
    color: #F0EAD8;
    font-family: 'Nunito', sans-serif; font-size: 1rem;
    padding: 0 1rem; height: 52px; /* AODA: ≥48px */
    transition: border-color .2s; box-sizing: border-box;
}
.acct-inp:focus {
    outline: none; border-color: #D4A017;
    box-shadow: 0 0 0 3px rgba(212,160,23,.2);
}
.acct-inp::placeholder { color: rgba(200,190,168,.4); }

/* Buttons */
.acct-btn {
    display: inline-flex; align-items: center; justify-content: center;
    height: 52px; padding: 0 2rem; border-radius: 4px;
    font-family: 'Nunito', sans-serif;
    font-size: .95rem; font-weight: 800;
    letter-spacing: .04em; text-transform: uppercase;
    cursor: pointer; border: none;
    transition: background .2s, transform .15s;
    text-decoration: none;
}
.acct-btn:focus { outline: none; box-shadow: 0 0 0 3px rgba(212,160,23,.4); }
.acct-btn:active { transform: translateY(0); }

.btn-amber { background: #D4A017; color: #0A2342; }
.btn-amber:hover { background: #E5B828; transform: translateY(-1px); color: #0A2342; }

.btn-teal  {
    background: transparent; color: #22A090;
    border: 1px solid rgba(26,122,110,.5);
}
.btn-teal:hover { background: rgba(26,122,110,.12); }

.btn-danger {
    background: rgba(200,50,50,.15);
    color: #FF8080;
    border: 1px solid rgba(200,50,50,.35);
}
.btn-danger:hover { background: rgba(200,50,50,.25); }

/* Delete zone */
.delete-zone {
    border: 1px solid rgba(200,50,50,.25);
    border-radius: 6px;
    padding: 1.25rem; background: rgba(200,50,50,.04);
}
.delete-zone-title { font-weight: 700; color: #FF8080; font-size: 1rem; margin-bottom: .4rem; }
.delete-zone-body  { font-size: .9rem; color: #8A8070; line-height: 1.6; margin-bottom: 1rem; }

.confirm-form { display: none; margin-top: 1rem; }
.confirm-form.visible { display: block; }

.acct-divider {
    border: none; border-top: 1px solid rgba(240,234,216,.08);
    margin: 1.5rem 0;
}

.sign-out-row {
    text-align: center; margin-top: 2rem;
}
.sign-out-link {
    display: inline-flex; align-items: center; justify-content: center;
    height: 52px; padding: 0 2rem; border-radius: 4px;
    font-family: 'Nunito', sans-serif; font-size: 20px; font-weight: 600;
    color: #C8BEA8; text-decoration: none;
    border: 1px solid rgba(240,234,216,.2);
    background: transparent;
    transition: border-color .2s, color .2s;
    cursor: pointer;
}
.sign-out-link:hover { color: #FF8080; border-color: rgba(200,50,50,.4); text-decoration: none; }
.sign-out-link:focus { outline: none; box-shadow: 0 0 0 3px rgba(212,160,23,.4); }
</style>

<div class="acct-inner">

    <?php if ( $action_done && isset( $action_msg[ $action_done ] ) ) : ?>
    <div class="acct-alert ok" role="status" aria-live="polite">
        <?php echo esc_html( $action_msg[ $action_done ] ); ?>
    </div>
    <?php endif; ?>

    <?php if ( $action_error ) : ?>
    <div class="acct-alert err" role="alert" aria-live="assertive">
        <?php echo esc_html( $action_error ); ?>
    </div>
    <?php endif; ?>

    <p class="acct-page-eyebrow">AtMyBoat.com</p>
    <h1 class="acct-page-title">My Account</h1>
    <p class="acct-page-sub">Manage your account, security, and privacy settings.</p>

    <!-- ── Account Overview ─────────────────────────────────────────────── -->
    <section class="acct-section" aria-labelledby="sec-overview-lbl">
        <div class="acct-sec-hd">
            <span class="acct-sec-lbl" id="sec-overview-lbl">Account</span>
        </div>
        <div class="acct-sec-body">
            <div class="acct-profile-row">
                <div>
                    <p class="acct-name"><?php echo esc_html( $current_user->display_name ); ?></p>
                    <p class="acct-email-mono"><?php echo esc_html( $current_user->user_email ); ?></p>
                </div>
                <div class="acct-badges">
                    <span class="badge-tier"><?php echo esc_html( $tier_label ); ?></span>
                    <?php if ( $pi_paired ) : ?>
                    <span class="badge-pi">Pi Paired</span>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </section>

    <!-- ── Change Password ──────────────────────────────────────────────── -->
    <section class="acct-section" aria-labelledby="sec-pw-lbl">
        <div class="acct-sec-hd">
            <span class="acct-sec-lbl" id="sec-pw-lbl">Change Password</span>
        </div>
        <div class="acct-sec-body">
            <form method="post" action="<?php echo esc_url( home_url( '/my-account/' ) ); ?>">
                <?php wp_nonce_field( 'amboat_acct_change_password', 'atmyboat_account_nonce' ); ?>
                <input type="hidden" name="account_action" value="change_password">

                <div class="acct-field">
                    <label class="acct-lbl" for="pw_current">Current password</label>
                    <input class="acct-inp" type="password" id="pw_current" name="pw_current"
                        autocomplete="current-password" required aria-required="true">
                </div>
                <div class="acct-field">
                    <label class="acct-lbl" for="pw_new">
                        New password <span class="hint">(min. 8 characters)</span>
                    </label>
                    <input class="acct-inp" type="password" id="pw_new" name="pw_new"
                        autocomplete="new-password" minlength="8" required aria-required="true">
                </div>
                <div class="acct-field">
                    <label class="acct-lbl" for="pw_confirm">Confirm new password</label>
                    <input class="acct-inp" type="password" id="pw_confirm" name="pw_confirm"
                        autocomplete="new-password" required aria-required="true">
                </div>

                <button type="submit" class="acct-btn btn-amber">Update Password</button>
            </form>
        </div>
    </section>

    <!-- ── Change Email ─────────────────────────────────────────────────── -->
    <section class="acct-section" aria-labelledby="sec-email-lbl">
        <div class="acct-sec-hd">
            <span class="acct-sec-lbl" id="sec-email-lbl">Change Email Address</span>
        </div>
        <div class="acct-sec-body">
            <p style="font-size:.95rem;color:#8A8070;margin-bottom:1.25rem;line-height:1.6;">
                Current:
                <span class="acct-email-mono" style="color:#C8BEA8;"><?php echo esc_html( $current_user->user_email ); ?></span>
            </p>
            <form method="post" action="<?php echo esc_url( home_url( '/my-account/' ) ); ?>">
                <?php wp_nonce_field( 'amboat_acct_change_email', 'atmyboat_account_nonce' ); ?>
                <input type="hidden" name="account_action" value="change_email">

                <div class="acct-field">
                    <label class="acct-lbl" for="new_email">New email address</label>
                    <input class="acct-inp" type="email" id="new_email" name="new_email"
                        autocomplete="email" required aria-required="true">
                </div>
                <button type="submit" class="acct-btn btn-amber">Update Email</button>
            </form>
        </div>
    </section>

    <!-- ── Data & Privacy ───────────────────────────────────────────────── -->
    <section class="acct-section" aria-labelledby="sec-data-lbl">
        <div class="acct-sec-hd">
            <span class="acct-sec-lbl" id="sec-data-lbl">Data &amp; Privacy</span>
        </div>
        <div class="acct-sec-body">
            <p style="font-size:.95rem;color:#8A8070;line-height:1.7;margin-bottom:1.5rem;">
                AtMyBoat.com stores only your account information listed above.
                Your boat sensor data is processed on your Pi and is never stored on our servers.
                You may download or delete your account data at any time
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;">(GDPR Art.&nbsp;15 &amp; 17)</span>.
            </p>

            <!-- Download -->
            <a
                href="<?php echo esc_url( add_query_arg( [ 'action' => 'export_data', 'nonce' => $export_nonce ], home_url( '/my-account/' ) ) ); ?>"
                class="acct-btn btn-teal"
                style="margin-bottom:1.75rem;"
            >
                Download My Data (JSON)
            </a>

            <hr class="acct-divider">

            <!-- Delete -->
            <div class="delete-zone">
                <p class="delete-zone-title">Delete Account</p>
                <p class="delete-zone-body">
                    Permanently deletes your AtMyBoat.com account, tier assignment, and Pi pairing record.
                    Your forum posts are kept anonymously. This cannot be undone.
                </p>
                <button
                    type="button"
                    class="acct-btn btn-danger"
                    id="show-delete-btn"
                    aria-expanded="false"
                    aria-controls="confirm-delete-form"
                    onclick="
                        this.style.display='none';
                        document.getElementById('confirm-delete-form').classList.add('visible');
                        this.setAttribute('aria-expanded','true');
                    "
                >
                    Delete My Account
                </button>

                <div class="confirm-form" id="confirm-delete-form" aria-hidden="false">
                    <form method="post" action="<?php echo esc_url( home_url( '/my-account/' ) ); ?>">
                        <?php wp_nonce_field( 'amboat_acct_delete_account', 'atmyboat_account_nonce' ); ?>
                        <input type="hidden" name="account_action" value="delete_account">

                        <div class="acct-field">
                            <label class="acct-lbl" for="confirm_delete">
                                Type <strong style="color:#FF8080;">DELETE MY ACCOUNT</strong> to confirm
                            </label>
                            <input class="acct-inp" type="text" id="confirm_delete" name="confirm_delete"
                                autocomplete="off" placeholder="DELETE MY ACCOUNT" aria-required="true">
                        </div>
                        <button type="submit" class="acct-btn btn-danger">Permanently Delete Account</button>
                    </form>
                </div>
            </div>

        </div>
    </section>

    <div class="sign-out-row">
        <a class="sign-out-link" href="<?php echo esc_url( wp_logout_url( home_url( '/' ) ) ); ?>">
            Sign out
        </a>
    </div>

</div><!-- .acct-inner -->
</main>
<?php get_footer(); ?>
