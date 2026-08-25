<?php
// Shared Ed25519 device authentication verifier — BUG-66 Phase A.
// Required by all endpoints that authenticate a Pi (new + migrated).
// Never serve this file directly — it returns nothing on direct access.

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Verify the Ed25519 signature from a Pi request.
 * Returns ['token' => string, 'status' => string] on success.
 * Returns WP_Error on any auth failure.
 *
 * Identity is the RESULT of verification — never a client-supplied field.
 * The X-Device-Token header is only a lookup hint; the signature decides.
 *
 * @param WP_REST_Request $request
 * @return array{token: string, status: string}|WP_Error
 */
function verify_device_signature(WP_REST_Request $request): array|WP_Error {
    global $wpdb;

    $token = trim((string)($request->get_header('X-Device-Token') ?? ''));
    $ts    = trim((string)($request->get_header('X-Timestamp')    ?? ''));
    $nonce = trim((string)($request->get_header('X-Nonce')        ?? ''));
    $sig64 = trim((string)($request->get_header('X-Signature')    ?? ''));

    if (!$token || !$ts || !$nonce || !$sig64) {
        return new WP_Error('missing_headers', 'Missing required auth headers', ['status' => 401]);
    }

    // Timestamp check: explicit skew error, never a silent failure.
    // Pi RTC is unreliable — skew is expected; the error must be diagnosable.
    $skew = abs(time() - (int)$ts);
    if ($skew > 600) {
        return new WP_Error('timestamp_skew',
            sprintf('Request timestamp skewed by %d seconds (limit 600)', $skew),
            ['status' => 401, 'skew_seconds' => $skew]
        );
    }

    // Nonce replay prevention — cache via WordPress transients for 600s.
    // md5 keeps the transient key short and option-table-safe.
    $nonce_key = 'd3kos_nonce_' . md5($nonce);
    if (get_transient($nonce_key) !== false) {
        return new WP_Error('replayed_nonce', 'Nonce has already been used', ['status' => 401]);
    }

    // Look up stored public key — do NOT create a row if the device is unknown.
    // This is the BUG-66 fix: an unrecognised token is rejected, never registered.
    $row = $wpdb->get_row($wpdb->prepare(
        "SELECT HEX(public_key) AS pub_hex, status FROM amboat_device_enrolments WHERE device_token = %s",
        $token
    ));

    if ($row === null) {
        return new WP_Error('unknown_device', 'Device token not enrolled', ['status' => 401]);
    }

    // Signature verification using libsodium (bundled in PHP >= 7.2; PHP 8.3.33 on HostPapa).
    $path    = $request->get_route();
    $message = implode('|', [$token, $ts, $nonce, $path]);
    $sig_bin = base64_decode($sig64, true);
    $pub_bin = hex2bin($row->pub_hex);

    if ($sig_bin === false || strlen($sig_bin) !== SODIUM_CRYPTO_SIGN_BYTES) {
        return new WP_Error('invalid_signature_format', 'Signature must be 64 bytes base64-encoded', ['status' => 401]);
    }
    if ($pub_bin === false || strlen($pub_bin) !== SODIUM_CRYPTO_SIGN_PUBLICKEYBYTES) {
        // Stored key is corrupted — this indicates a data integrity problem.
        return new WP_Error('public_key_corrupt', 'Stored public key is invalid', ['status' => 500]);
    }

    if (!sodium_crypto_sign_verify_detached($sig_bin, $message, $pub_bin)) {
        return new WP_Error('signature_failed', 'Ed25519 signature verification failed', ['status' => 401]);
    }

    // Mark nonce consumed AFTER successful verification only.
    set_transient($nonce_key, 1, 600);

    return ['token' => $token, 'status' => $row->status];
}

/**
 * Full device auth — requires status = 'approved'.
 * Returns device_token string on success.
 * Returns WP_Error (403 not_approved) for pending/rejected/blocked devices.
 *
 * Use this for all endpoints except /status (which permits pending devices).
 *
 * @param WP_REST_Request $request
 * @return string|WP_Error device_token on success
 */
function verify_device_request(WP_REST_Request $request): string|WP_Error {
    $result = verify_device_signature($request);
    if (is_wp_error($result)) {
        return $result;
    }

    if ($result['status'] !== 'approved') {
        return new WP_Error('not_approved',
            'Device is not approved for this operation',
            ['status' => 403, 'device_status' => $result['status']]
        );
    }

    return $result['token'];
}
