<?php
// Handler for POST /wp-json/amboat-device/v1/enrol — BUG-66 Phase A.
// First enrolment only. Signs with the key being enrolled (proof of possession).
// Uses the supplied public key for verification — not a DB lookup.
// 409 on re-enrolment: the stored key must NEVER be overwritten.

if (!defined('ABSPATH')) {
    exit;
}

require_once __DIR__ . '/device-auth.php';

/**
 * Handle POST /wp-json/amboat-device/v1/enrol
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function d3kos_handle_enrol(WP_REST_Request $request): WP_REST_Response|WP_Error {
    global $wpdb;

    $token  = trim((string)($request->get_param('device_token')  ?? ''));
    $pub64  = trim((string)($request->get_param('public_key')    ?? ''));
    $email  = sanitize_email((string)($request->get_param('contact_email') ?? ''));
    $note   = sanitize_text_field((string)($request->get_param('note') ?? ''));

    $ts    = trim((string)($request->get_header('X-Timestamp') ?? ''));
    $nonce = trim((string)($request->get_header('X-Nonce')     ?? ''));
    $sig64 = trim((string)($request->get_header('X-Signature') ?? ''));

    if (!$token || !$pub64 || !$ts || !$nonce || !$sig64) {
        return new WP_Error('missing_fields', 'device_token, public_key, X-Timestamp, X-Nonce, X-Signature are required', ['status' => 400]);
    }

    // UUID format check
    if (!preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $token)) {
        return new WP_Error('invalid_device_token', 'device_token must be a UUID', ['status' => 400]);
    }

    // Timestamp check
    $skew = abs(time() - (int)$ts);
    if ($skew > 600) {
        return new WP_Error('timestamp_skew',
            sprintf('Request timestamp skewed by %d seconds (limit 600)', $skew),
            ['status' => 401, 'skew_seconds' => $skew]
        );
    }

    // Nonce replay check
    $nonce_key = 'd3kos_nonce_' . md5($nonce);
    if (get_transient($nonce_key) !== false) {
        return new WP_Error('replayed_nonce', 'Nonce has already been used', ['status' => 401]);
    }

    // Check for existing enrolment — 409 on re-enrolment, key NEVER overwritten.
    $existing = $wpdb->get_var($wpdb->prepare(
        "SELECT device_token FROM amboat_device_enrolments WHERE device_token = %s",
        $token
    ));
    if ($existing !== null) {
        return new WP_Error('already_enrolled', 'Device token already enrolled', ['status' => 409]);
    }

    // Decode and validate the supplied public key
    $pub_bin = base64_decode($pub64, true);
    if ($pub_bin === false || strlen($pub_bin) !== SODIUM_CRYPTO_SIGN_PUBLICKEYBYTES) {
        return new WP_Error('invalid_public_key',
            sprintf('public_key must be a %d-byte Ed25519 public key, base64-encoded', SODIUM_CRYPTO_SIGN_PUBLICKEYBYTES),
            ['status' => 400]
        );
    }

    // Proof-of-possession: verify signature using the SUPPLIED key.
    // This confirms the enrolling party holds the corresponding private key.
    $path    = $request->get_route();
    $message = implode('|', [$token, $ts, $nonce, $path]);
    $sig_bin = base64_decode($sig64, true);

    if ($sig_bin === false || strlen($sig_bin) !== SODIUM_CRYPTO_SIGN_BYTES) {
        return new WP_Error('invalid_signature_format', 'Signature must be 64 bytes base64-encoded', ['status' => 401]);
    }
    if (!sodium_crypto_sign_verify_detached($sig_bin, $message, $pub_bin)) {
        return new WP_Error('signature_failed', 'Ed25519 signature verification failed', ['status' => 401]);
    }

    // Mark nonce consumed after successful verification
    set_transient($nonce_key, 1, 600);

    // Store IP as binary (inet_pton handles both IPv4 and IPv6)
    $ip_raw = $_SERVER['REMOTE_ADDR'] ?? '';
    $ip_bin = @inet_pton($ip_raw);
    $ip_hex = ($ip_bin !== false) ? bin2hex($ip_bin) : null;
    $pub_hex = bin2hex($pub_bin);

    // Insert enrolment — public key as raw binary via UNHEX, IP similarly
    if ($ip_hex !== null) {
        $inserted = $wpdb->query($wpdb->prepare(
            "INSERT INTO amboat_device_enrolments (device_token, public_key, status, contact_email, enrol_note, enrolled_ip)
             VALUES (%s, UNHEX(%s), 'pending', %s, %s, UNHEX(%s))",
            $token, $pub_hex, $email ?: null, $note ?: null, $ip_hex
        ));
    } else {
        $inserted = $wpdb->query($wpdb->prepare(
            "INSERT INTO amboat_device_enrolments (device_token, public_key, status, contact_email, enrol_note)
             VALUES (%s, UNHEX(%s), 'pending', %s, %s)",
            $token, $pub_hex, $email ?: null, $note ?: null
        ));
    }

    if (!$inserted) {
        return new WP_Error('enrolment_failed', 'Failed to store enrolment', ['status' => 500]);
    }

    // Audit log
    $wpdb->query($wpdb->prepare(
        "INSERT INTO amboat_registration_audit (event, device_token, ip, detail) VALUES ('enrol', %s, %s, %s)",
        $token,
        $ip_hex ? null : null, // Stored as VARBINARY via separate path below
        $email ?: null
    ));
    if ($ip_hex !== null) {
        // Update the audit row's IP to binary
        $last_id = $wpdb->insert_id;
        $wpdb->query($wpdb->prepare(
            "UPDATE amboat_registration_audit SET ip = UNHEX(%s) WHERE id = %d",
            $ip_hex, $last_id
        ));
    }

    return new WP_REST_Response(['status' => 'pending'], 200);
}
