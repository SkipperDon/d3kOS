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
 *
 * With $request (REST API endpoints): returns string|WP_Error.
 * Without $request (plain PHP endpoints): reads from $_SERVER, exits on failure,
 * returns device_token string. Handles the legacy-key transition path.
 *
 * @param WP_REST_Request|null $request
 * @return string|WP_Error device_token on success; WP_Error only in REST path
 */
function verify_device_request(?WP_REST_Request $request = null): string|WP_Error {
    if ($request !== null) {
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
    // Plain PHP endpoint path — exits on failure; returns string on success.
    return verify_device_request_server();
}

/**
 * Plain-PHP endpoint auth (no WP_REST_Request).
 * Reads Ed25519 headers from $_SERVER; falls back to legacy Bearer key during transition.
 * Every legacy-key use is written to amboat_registration_audit for migration tracking.
 * Exits with 401/403 on any failure. Returns device_token on success.
 *
 * @return string device_token
 */
function verify_device_request_server(): string {
    global $wpdb;

    $token = trim($_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '');
    $ts    = trim($_SERVER['HTTP_X_TIMESTAMP']    ?? '');
    $nonce = trim($_SERVER['HTTP_X_NONCE']        ?? '');
    $sig64 = trim($_SERVER['HTTP_X_SIGNATURE']    ?? '');
    $auth  = $_SERVER['HTTP_AUTHORIZATION']       ?? '';

    // ── Ed25519 path (new devices) ────────────────────────────────────────────
    if ($token && $ts && $nonce && $sig64) {
        $skew = abs(time() - (int)$ts);
        if ($skew > 600) {
            http_response_code(401);
            echo json_encode(['success' => false, 'error' => 'timestamp_skew', 'skew_seconds' => $skew]);
            exit;
        }

        $nonce_key = 'd3kos_nonce_' . md5($nonce);
        if (get_transient($nonce_key) !== false) {
            http_response_code(401);
            echo json_encode(['success' => false, 'error' => 'replayed_nonce']);
            exit;
        }

        $row = $wpdb->get_row($wpdb->prepare(
            "SELECT HEX(public_key) AS pub_hex, status FROM amboat_device_enrolments WHERE device_token = %s",
            $token
        ));

        if ($row === null) {
            http_response_code(401);
            echo json_encode(['success' => false, 'error' => 'unknown_device']);
            exit;
        }
        if ($row->status !== 'approved') {
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => 'not_approved', 'device_status' => $row->status]);
            exit;
        }

        $path    = strtok($_SERVER['REQUEST_URI'] ?? '/', '?');
        $message = implode('|', [$token, $ts, $nonce, $path]);
        $sig_bin = base64_decode($sig64, true);
        $pub_bin = hex2bin($row->pub_hex);

        if ($sig_bin === false || strlen($sig_bin) !== SODIUM_CRYPTO_SIGN_BYTES
            || $pub_bin === false || strlen($pub_bin) !== SODIUM_CRYPTO_SIGN_PUBLICKEYBYTES
            || !sodium_crypto_sign_verify_detached($sig_bin, $message, $pub_bin)) {
            http_response_code(401);
            echo json_encode(['success' => false, 'error' => 'signature_failed']);
            exit;
        }

        set_transient($nonce_key, 1, 600);
        return $token;
    }

    // ── Legacy Bearer-key path — transition period only ───────────────────────
    // Every legacy use is logged; remove this block once all Pis are migrated.
    if (defined('AMBOAT_API_KEY')
        && preg_match('/^Bearer\s+(.+)$/i', $auth, $m)
        && hash_equals(AMBOAT_API_KEY, $m[1])
        && !empty($token)) {
        $wpdb->insert(
            $wpdb->prefix . 'amboat_registration_audit',
            [
                'event'      => 'legacy_key_used',
                'user_id'    => null,
                'detail'     => substr($token, 0, 8) . '... endpoint=' . ($_SERVER['SCRIPT_NAME'] ?? '?'),
                'ip'         => substr($_SERVER['REMOTE_ADDR'] ?? '', 0, 45),
                'created_at' => current_time('mysql', true),
            ],
            ['%s', '%d', '%s', '%s', '%s']
        );
        return $token;
    }

    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
