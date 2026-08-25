<?php
/**
 * d3kOS Device Registration Helpers — BUG-63
 *
 * amboat_claim_registration_code() — atomic single-use code claim.
 * amboat_rollback_registration_code() — returns code to 'valid' on wp_create_user failure.
 * amboat_registration_audit() — appends to amboat_registration_audit table.
 *
 * Deploy to: wp-content/themes/twentytwenty-child/device-registration.php
 * Required by: page-register.php (via require_once __DIR__ . '/device-registration.php')
 * Depends on: amboat_device_enrolments, amboat_registration_codes, amboat_registration_audit
 *             tables created by the d3kos-device-auth WordPress plugin.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Never load directly.
}

/**
 * Claim a registration code atomically.
 *
 * Normalises the input (Crockford Base32: uppercase, O→0, I→1), hashes it with SHA-256,
 * and performs an atomic UPDATE WHERE status='valid' AND expires_at > NOW().
 *
 * Returns device_token (string) on success, WP_Error on any failure.
 * Two simultaneous submissions for the same code: exactly one gets affected_rows=1.
 *
 * @param  string $raw_code User-supplied code (case-insensitive, spaces ignored).
 * @return string|WP_Error  device_token on success, WP_Error on failure.
 */
function amboat_claim_registration_code( string $raw_code ): string|WP_Error {
    global $wpdb;

    // Normalise: strip whitespace, uppercase, Crockford substitutions (O→0, I→1)
    $code = strtoupper( preg_replace( '/\s+/', '', $raw_code ) );
    $code = strtr( $code, [ 'O' => '0', 'I' => '1' ] );

    if ( strlen( $code ) !== 10 ) {
        return new WP_Error( 'invalid_code', 'Registration code must be 10 characters.' );
    }

    $code_hash = hash( 'sha256', $code );

    $table_codes = $wpdb->prefix . 'amboat_registration_codes';
    $table_enrol = $wpdb->prefix . 'amboat_device_enrolments';

    // Transaction: SELECT FOR UPDATE to prevent concurrent redemption, then UPDATE.
    $wpdb->query( 'START TRANSACTION' );

    $row = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT rc.code_hash, ae.device_token
               FROM {$table_codes} rc
               JOIN {$table_enrol} ae ON ae.device_token = rc.device_token
              WHERE rc.code_hash = %s
                AND rc.status = 'valid'
                AND rc.expires_at > NOW()
              FOR UPDATE",
            $code_hash
        )
    );

    if ( ! $row ) {
        $wpdb->query( 'ROLLBACK' );
        return new WP_Error( 'invalid_code', 'That code is invalid, expired, or already used.' );
    }

    $updated = $wpdb->query(
        $wpdb->prepare(
            "UPDATE {$table_codes}
                SET status    = 'used',
                    used_at   = NOW(),
                    used_at_ip = %s
              WHERE code_hash = %s
                AND status    = 'valid'
                AND expires_at > NOW()",
            substr( $_SERVER['REMOTE_ADDR'] ?? '', 0, 45 ),
            $code_hash
        )
    );

    if ( $updated !== 1 ) {
        // Race: another request claimed it between our SELECT and UPDATE.
        $wpdb->query( 'ROLLBACK' );
        return new WP_Error( 'invalid_code', 'That code is invalid, expired, or already used.' );
    }

    $wpdb->query( 'COMMIT' );

    return (string) $row->device_token;
}

/**
 * Roll a claimed code back to 'valid' when wp_create_user() fails.
 * Call immediately after a failed wp_create_user() before any other error handling.
 *
 * @param string $code_hash The SHA-256 hash of the normalised code (from amboat_claim_registration_code).
 */
function amboat_rollback_registration_code( string $code_hash ): void {
    global $wpdb;
    $table_codes = $wpdb->prefix . 'amboat_registration_codes';
    $wpdb->update(
        $table_codes,
        [ 'status' => 'valid', 'used_at' => null, 'used_at_ip' => null ],
        [ 'code_hash' => $code_hash, 'status' => 'used' ],
        [ '%s', null, null ],
        [ '%s', '%s' ]
    );
}

/**
 * Append an event to the registration audit log.
 *
 * @param string   $event   One of: 'enrol', 'code_issued', 'code_superseded', 'redeem_ok',
 *                          'redeem_fail', 'account_created', 'admin_approve', 'admin_reject', 'admin_block'.
 * @param int|null $user_id WordPress user ID (null if account not yet created).
 * @param string   $detail  Short detail string (error code, IP, etc).
 */
function amboat_registration_audit( string $event, ?int $user_id, string $detail = '' ): void {
    global $wpdb;
    $table = $wpdb->prefix . 'amboat_registration_audit';
    $wpdb->insert(
        $table,
        [
            'event'      => $event,
            'user_id'    => $user_id,
            'detail'     => substr( $detail, 0, 255 ),
            'ip'         => substr( $_SERVER['REMOTE_ADDR'] ?? '', 0, 45 ),
            'created_at' => current_time( 'mysql', true ),
        ],
        [ '%s', '%d', '%s', '%s', '%s' ]
    );
}
