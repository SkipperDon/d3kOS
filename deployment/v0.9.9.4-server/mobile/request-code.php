<?php
// Handler for POST /wp-json/amboat-device/v1/request-code — BUG-66 Phase A.
// Issues a 10-character Crockford Base32 registration code to an approved device.
// Server-clocked expiry (15 min) — the Pi's RTC is unreliable (registration spec §4.2).
// Issuing a new code supersedes any existing live code for that device.

if (!defined('ABSPATH')) {
    exit;
}

require_once __DIR__ . '/device-auth.php';

/**
 * Crockford Base32 alphabet — no I, L, O, U to prevent visual confusion.
 * 10 characters = 50 bits. 256 mod 32 = 0, so no modulo bias.
 */
function d3kos_generate_code(int $length = 10): string {
    $chars = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
    $bytes = random_bytes($length);
    $code  = '';
    for ($i = 0; $i < $length; $i++) {
        $code .= $chars[ord($bytes[$i]) % 32];
    }
    return $code;
}

/**
 * Handle POST /wp-json/amboat-device/v1/request-code
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function d3kos_handle_request_code(WP_REST_Request $request): WP_REST_Response|WP_Error {
    global $wpdb;

    // Requires approved status — pending devices cannot request codes.
    $token = verify_device_request($request);
    if (is_wp_error($token)) {
        return $token;
    }

    // D4: one account per device — if already registered, refuse to issue a code.
    $existing_account = $wpdb->get_var($wpdb->prepare(
        "SELECT device_token FROM amboat_device_accounts WHERE device_token = %s",
        $token
    ));
    if ($existing_account !== null) {
        return new WP_Error('already_registered',
            'This device already has a registered account',
            ['status' => 403]
        );
    }

    // Rate limit: 1 request per minute per device.
    // Check for a code issued in the last 60 seconds that is still 'valid'.
    $recent = $wpdb->get_var($wpdb->prepare(
        "SELECT code_hash FROM amboat_registration_codes
          WHERE device_token = %s AND status = 'valid' AND issued_at > DATE_SUB(NOW(), INTERVAL 60 SECOND)",
        $token
    ));
    if ($recent !== null) {
        return new WP_Error('rate_limited', 'Code request rate limited: 1 per minute', ['status' => 429]);
    }

    // Supersede any existing live codes for this device.
    $wpdb->query($wpdb->prepare(
        "UPDATE amboat_registration_codes SET status = 'superseded' WHERE device_token = %s AND status = 'valid'",
        $token
    ));

    // Generate code, store SHA256 only — plaintext is returned once and never persisted.
    $code      = d3kos_generate_code(10);
    $code_hash = hash('sha256', $code);
    $expires   = date('Y-m-d H:i:s', time() + 900); // 15 minutes, server-clocked

    $inserted = $wpdb->insert(
        'amboat_registration_codes',
        [
            'code_hash'    => $code_hash,
            'device_token' => $token,
            'expires_at'   => $expires,
            'status'       => 'valid',
        ],
        ['%s', '%s', '%s', '%s']
    );

    if (!$inserted) {
        return new WP_Error('code_generation_failed', 'Failed to store registration code', ['status' => 500]);
    }

    // Audit log
    $wpdb->insert('amboat_registration_audit', [
        'event'        => 'code_issued',
        'device_token' => $token,
        'detail'       => substr($code_hash, 0, 8), // First 8 chars of hash for correlation
    ], ['%s', '%s', '%s']);

    return new WP_REST_Response([
        'code'       => $code,
        'expires_at' => gmdate('Y-m-d\TH:i:s\Z', strtotime($expires)),
    ], 200);
}
