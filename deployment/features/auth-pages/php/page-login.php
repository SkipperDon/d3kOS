<?php
/**
 * Template Name: Login Page
 *
 * AtMyBoat.com sign-in — custom AODA-compliant template.
 * AODA: 20px base text, 48px touch targets, skip-to-content, WCAG AA contrast.
 *
 * Handles POST via wp_signon(). Checks email-verified flag before login.
 * On success: redirects to /my-account/ (or ?redirect_to= param from bbPress etc).
 *
 * Also shows "reset link sent" notice when redirected back from WP lost-password flow.
 *
 * Deploy to: wp-content/themes/twentytwenty-child/page-login.php
 * WP Admin:  Create page with slug "login", assign template "Login Page"
 */

// Redirect logged-in users — nothing to do here
if ( is_user_logged_in() ) {
    wp_safe_redirect( home_url( '/my-account/' ) );
    exit;
}

// ── Handle form submission ─────────────────────────────────────────────────
$login_error = '';

if ( $_SERVER['REQUEST_METHOD'] === 'POST' && isset( $_POST['atmyboat_login_nonce'] ) ) {

    if ( ! wp_verify_nonce( wp_unslash( $_POST['atmyboat_login_nonce'] ), 'atmyboat_login_action' ) ) {
        $login_error = 'Security check failed. Please refresh and try again.';
    } else {
        $email    = sanitize_email( wp_unslash( $_POST['email']    ?? '' ) );
        $password =                 wp_unslash( $_POST['password'] ?? ''   );
        $remember = ! empty( $_POST['remember_me'] );

        if ( ! is_email( $email ) ) {
            $login_error = 'Please enter a valid email address.';
        } elseif ( $password === '' ) {
            $login_error = 'Please enter your password.';
        } else {
            $user = get_user_by( 'email', $email );

            if ( ! $user ) {
                // Generic message — do not reveal whether the email exists
                $login_error = 'Email address or password is incorrect.';
            } else {
                // Check email verification before attempting wp_signon()
                $verified = get_user_meta( $user->ID, 'atmyboat_email_verified', true );
                if ( $verified === '0' ) {
                    $login_error = 'Please verify your email address before signing in. '
                        . 'Check your inbox for the verification link.';
                } else {
                    $result = wp_signon(
                        [
                            'user_login'    => $user->user_login,
                            'user_password' => $password,
                            'remember'      => $remember,
                        ],
                        is_ssl()
                    );

                    if ( is_wp_error( $result ) ) {
                        $login_error = 'Email address or password is incorrect.';
                    } else {
                        // Determine redirect target
                        $redirect_to = home_url( '/my-account/' );
                        if ( isset( $_GET['redirect_to'] ) ) {
                            $requested = wp_sanitize_redirect( wp_unslash( $_GET['redirect_to'] ) );
                            // Only trust same-origin redirects
                            if ( $requested !== '' && strpos( $requested, home_url() ) === 0 ) {
                                $redirect_to = $requested;
                            }
                        }
                        wp_safe_redirect( $redirect_to );
                        exit;
                    }
                }
            }
        }
    }
}

// ── Show password-reset sent notice (from WP lostpassword redirect) ────────
$reset_sent = isset( $_GET['reset_sent'] ) && $_GET['reset_sent'] === '1';

get_header();
?>
<a class="amboat-skip-link" href="#login-main">Skip to main content</a>

<main id="login-main" class="amboat-auth-wrap">
<style>
/* ── Login Page — scoped styles (page-login.php) ────────────────────────── */
.amboat-skip-link {
    position: absolute; left: -9999px; top: 1rem; z-index: 9999;
    background: #D4A017; color: #0A2342;
    padding: .75rem 1.5rem; border-radius: 4px;
    font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 1rem;
    text-decoration: none;
}
.amboat-skip-link:focus { left: 1rem; }

.amboat-auth-wrap {
    min-height: 80vh;
    background: #0A2342;
    display: flex; flex-direction: column;
    align-items: center; justify-content: flex-start;
    padding: 3rem 1rem 4rem;
    font-family: 'Nunito', 'Segoe UI', sans-serif;
    font-size: 1rem; line-height: 1.85;
    color: #F0EAD8;
}
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
    width: 100%; max-width: 440px;
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
    line-height: 1.2; margin: 0;
}

.auth-body { padding: 2rem; }

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

.auth-field { margin-bottom: 1.25rem; }
.auth-lbl {
    display: block;
    font-size: 0.9rem; font-weight: 700;
    color: #C8BEA8; letter-spacing: .04em;
    margin-bottom: .4rem;
}
.auth-inp {
    display: block; width: 100%;
    background: rgba(10,35,66,.7);
    border: 1px solid rgba(240,234,216,.15);
    border-radius: 4px;
    color: #F0EAD8;
    font-family: 'Nunito', sans-serif; font-size: 1rem;
    padding: 0 1rem; height: 52px; /* AODA: ≥48px */
    transition: border-color .2s; box-sizing: border-box;
}
.auth-inp:focus {
    outline: none; border-color: #D4A017;
    box-shadow: 0 0 0 3px rgba(212,160,23,.2);
}
.auth-inp::placeholder { color: rgba(200,190,168,.4); }

.auth-check-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 1.5rem; gap: .5rem;
}
.auth-check {
    display: flex; align-items: center; gap: .5rem; cursor: pointer;
}
.auth-check input[type=checkbox] {
    width: 20px; height: 20px; /* AODA: ≥18px clickable */
    accent-color: #D4A017; cursor: pointer; flex-shrink: 0;
}
.auth-check-lbl { font-size: .95rem; color: #C8BEA8; }

.auth-forgot {
    font-size: .9rem; color: #D4A017; text-decoration: none; white-space: nowrap;
}
.auth-forgot:hover { text-decoration: underline; }

.auth-submit {
    display: flex; align-items: center; justify-content: center;
    width: 100%;
    background: #D4A017; color: #0A2342;
    border: none; border-radius: 4px;
    font-family: 'Nunito', sans-serif;
    font-size: 1.05rem; font-weight: 800;
    letter-spacing: .05em; text-transform: uppercase;
    height: 56px; cursor: pointer; text-decoration: none;
    transition: background .2s, transform .15s;
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
</style>

<div class="auth-card">
    <div class="auth-card-hd">
        <div class="auth-eyebrow">AtMyBoat.com</div>
        <h1 class="auth-title">Sign in</h1>
    </div>
    <div class="auth-body">

        <?php if ( $reset_sent ) : ?>
        <div class="auth-alert ok" role="status">
            Check your inbox — a password reset link has been sent to your email address.
        </div>
        <?php endif; ?>

        <?php if ( $login_error ) : ?>
        <div class="auth-alert err" role="alert" aria-live="assertive">
            <?php echo esc_html( $login_error ); ?>
        </div>
        <?php endif; ?>

        <form method="post" action="<?php echo esc_url( home_url( '/login/' ) ); ?>" novalidate>
            <?php wp_nonce_field( 'atmyboat_login_action', 'atmyboat_login_nonce' ); ?>

            <?php
            // Pass redirect_to through the form if present
            if ( isset( $_GET['redirect_to'] ) ) : ?>
            <input type="hidden" name="redirect_to" value="<?php echo esc_attr( wp_sanitize_redirect( wp_unslash( $_GET['redirect_to'] ) ) ); ?>">
            <?php endif; ?>

            <div class="auth-field">
                <label class="auth-lbl" for="email">Email address</label>
                <input
                    class="auth-inp" type="email" id="email" name="email"
                    value="<?php echo isset( $_POST['email'] ) ? esc_attr( sanitize_email( wp_unslash( $_POST['email'] ) ) ) : ''; ?>"
                    autocomplete="email" required aria-required="true"
                >
            </div>

            <div class="auth-field">
                <label class="auth-lbl" for="password">Password</label>
                <input
                    class="auth-inp" type="password" id="password" name="password"
                    autocomplete="current-password" required aria-required="true"
                >
            </div>

            <div class="auth-check-row">
                <label class="auth-check">
                    <input type="checkbox" name="remember_me" id="remember_me">
                    <span class="auth-check-lbl">Keep me signed in</span>
                </label>
                <a class="auth-forgot"
                   href="<?php echo esc_url( wp_lostpassword_url( add_query_arg( 'reset_sent', '1', home_url( '/login/' ) ) ) ); ?>">
                    Forgot password?
                </a>
            </div>

            <button type="submit" class="auth-submit">Sign In</button>
        </form>

    </div>
    <div class="auth-foot">
        New to AtMyBoat? <a href="<?php echo esc_url( home_url( '/register/' ) ); ?>">Create a free account</a>
    </div>
</div>

</main>
<?php get_footer(); ?>
