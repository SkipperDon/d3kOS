<?php
/**
 * AtMyBoat.com — Authentication Hooks
 *
 * Loaded by functions.php. Add ONE line to the existing functions.php:
 *
 *   require_once get_template_directory() . '/inc/auth.php';
 *
 * Provides:
 *   1. login_url filter     — redirect wp-login.php → /login/ (bbPress compatible)
 *   2. authenticate filter  — block unverified accounts (belt-and-suspenders)
 *   3. logout_redirect      — send to home page after logout
 *   4. lostpassword_redirect — return to /login/?reset_sent=1 after WP reset email
 *
 * Deploy to: wp-content/themes/twentytwenty-child/inc/auth.php
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // No direct file access
}


// ── 1. Redirect wp-login.php to /login/ ───────────────────────────────────
//
// bbPress and other plugins call wp_login_url() to redirect unauthenticated
// users. Without this filter, they land on the default wp-login.php form.
// With it, they land on our branded /login/ page template.
//
add_filter( 'login_url', function ( $login_url, $redirect ) {
    $custom = home_url( '/login/' );
    if ( ! empty( $redirect ) ) {
        $custom = add_query_arg( 'redirect_to', rawurlencode( $redirect ), $custom );
    }
    return $custom;
}, 10, 2 );


// ── 2. Block login for unverified email accounts ───────────────────────────
//
// page-login.php checks email-verified status before calling wp_signon().
// This filter is a belt-and-suspenders guard that catches any other login
// path (e.g. direct wp-login.php access, plugin authentication calls).
//
// Logic:
//   - atmyboat_email_verified = '0'  → block (explicitly unverified)
//   - atmyboat_email_verified = '1'  → allow
//   - meta not set (empty string)    → allow (legacy or admin-created accounts)
//
add_filter( 'authenticate', function ( $user, $username, $password ) {
    // Pass through errors and null/false values from earlier filters
    if ( is_wp_error( $user ) || ! ( $user instanceof WP_User ) ) {
        return $user;
    }

    $verified = get_user_meta( $user->ID, 'atmyboat_email_verified', true );

    if ( $verified === '0' ) {
        return new WP_Error(
            'email_not_verified',
            esc_html__(
                'Please verify your email address before signing in. '
                . 'Check your inbox for the verification link.',
                'twentytwenty-child'
            )
        );
    }

    return $user;
}, 30, 3 );
// Priority 30 — runs after wp_authenticate_username_password (priority 20)
// and wp_authenticate_email_password (priority 20), so $user is already a
// resolved WP_User when this check runs.


// ── 3. Redirect to home after logout ──────────────────────────────────────
//
// Without this, wp_logout() redirects to wp-login.php?loggedout=true.
//
add_filter( 'logout_redirect', function () {
    return home_url( '/login/?logged_out=1' );
} );


// ── 4. Return to /login/ after WP lost-password email is sent ─────────────
//
// WP's built-in reset flow (wp-login.php?action=lostpassword) handles the
// email send. This filter redirects the confirmation screen back to our
// branded login page with a status notice.
//
add_filter( 'lostpassword_redirect', function () {
    return add_query_arg( 'reset_sent', '1', home_url( '/login/' ) );
} );
