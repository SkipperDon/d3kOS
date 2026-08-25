<?php
// Shared Ed25519 device authentication verifier — BUG-66 Phase A/C.
// Required by all mobile endpoints that authenticate a Pi.
// Never serve this file directly — it returns nothing on direct access.
//
// Two execution contexts:
//   WordPress REST  → define('ABSPATH', ...) present → verify_device_signature(WP_REST_Request) available
//   Standalone PHP  → config.php loaded before this file → verify_device_request_server() uses PDO

// ---------------------------------------------------------------------------
// WordPress REST path — only registered when running inside WordPress
// ---------------------------------------------------------------------------

if (defined('ABSPATH')) {

    /**
     * Verify Ed25519 signature from a WP REST request.
     * Returns ['token' => string, 'status' => string] on success.
     * Returns WP_Error on any auth failure.
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

        $skew = abs(time() - (int)$ts);
        if ($skew > 600) {
            return new WP_Error('timestamp_skew',
                sprintf('Request timestamp skewed by %d seconds (limit 600)', $skew),
                ['status' => 401, 'skew_seconds' => $skew]
            );
        }

        $nonce_key = 'd3kos_nonce_' . md5($nonce);
        if (get_transient($nonce_key) !== false) {
            return new WP_Error('replayed_nonce', 'Nonce has already been used', ['status' => 401]);
        }

        $row = $wpdb->get_row($wpdb->prepare(
            "SELECT HEX(public_key) AS pub_hex, status FROM amboat_device_enrolments WHERE device_token = %s",
            $token
        ));

        if ($row === null) {
            return new WP_Error('unknown_device', 'Device token not enrolled', ['status' => 401]);
        }

        $path    = $request->get_route();
        $message = implode('|', [$token, $ts, $nonce, $path]);
        $sig_bin = base64_decode($sig64, true);
        $pub_bin = hex2bin($row->pub_hex);

        if ($sig_bin === false || strlen($sig_bin) !== SODIUM_CRYPTO_SIGN_BYTES) {
            return new WP_Error('invalid_signature_format', 'Signature must be 64 bytes base64-encoded', ['status' => 401]);
        }
        if ($pub_bin === false || strlen($pub_bin) !== SODIUM_CRYPTO_SIGN_PUBLICKEYBYTES) {
            return new WP_Error('public_key_corrupt', 'Stored public key is invalid', ['status' => 500]);
        }

        if (!sodium_crypto_sign_verify_detached($sig_bin, $message, $pub_bin)) {
            return new WP_Error('signature_failed', 'Ed25519 signature verification failed', ['status' => 401]);
        }

        set_transient($nonce_key, 1, 600);

        return ['token' => $token, 'status' => $row->status];
    }

}

// ---------------------------------------------------------------------------
// Shared entrypoint — routes to WP path or standalone path
// ---------------------------------------------------------------------------

/**
 * Full device auth. Requires status = 'approved'.
 *
 * In WordPress REST context ($request provided): returns device_token string or WP_Error.
 * In standalone PHP context ($request = null): exits on failure, returns device_token string.
 *
 * @param mixed $request  WP_REST_Request or null
 * @return string|mixed   device_token on success; WP_Error in REST path on failure
 */
function verify_device_request($request = null) {
    if (defined('ABSPATH') && $request !== null) {
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
    return verify_device_request_server();
}

// ---------------------------------------------------------------------------
// Standalone PHP path — PDO, reads DB_* constants from config.php
// ---------------------------------------------------------------------------

/**
 * PDO helper — uses DB_HOST / DB_USER / DB_PASS / DB_NAME from config.php.
 */
function _d3kos_get_pdo(): PDO {
    // Device auth tables live in the WordPress DB (WP_DB_* constants, added to config.php).
    // Fall back to DB_* if WP_DB_* not defined (forward-compat).
    $db   = defined('WP_DB_NAME') ? WP_DB_NAME : (defined('DB_NAME') ? DB_NAME : '');
    $user = defined('WP_DB_USER') ? WP_DB_USER : (defined('DB_USER') ? DB_USER : '');
    $pass = defined('WP_DB_PASS') ? WP_DB_PASS : (defined('DB_PASS') ? DB_PASS : '');
    // Use localhost (Unix socket) — HostPapa grants @'localhost', not @'127.0.0.1'
    return new PDO(
        "mysql:host=localhost;dbname=$db;charset=utf8mb4",
        $user, $pass,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
}

/**
 * Nonce replay check — uses d3kos_nonce_cache table (created on first call).
 */
function _d3kos_nonce_used(PDO $pdo, string $nonce): bool {
    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS d3kos_nonce_cache (
            nonce_key CHAR(32) NOT NULL,
            used_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (nonce_key)
         ) ENGINE=InnoDB"
    );
    $stmt = $pdo->prepare(
        "SELECT 1 FROM d3kos_nonce_cache
          WHERE nonce_key = ? AND used_at > DATE_SUB(NOW(), INTERVAL 600 SECOND)"
    );
    $stmt->execute([md5($nonce)]);
    return $stmt->fetchColumn() !== false;
}

function _d3kos_mark_nonce_used(PDO $pdo, string $nonce): void {
    $stmt = $pdo->prepare("INSERT IGNORE INTO d3kos_nonce_cache (nonce_key) VALUES (?)");
    $stmt->execute([md5($nonce)]);
}

/**
 * Standalone (plain PHP) endpoint auth.
 * Reads Ed25519 headers from $_SERVER; falls back to legacy Bearer key during transition.
 * Every legacy-key use is written to amboat_registration_audit for migration tracking.
 * Exits with 401/403 on any failure. Returns device_token string on success.
 *
 * @return string device_token
 */
function verify_device_request_server(): string {
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

        $pdo = _d3kos_get_pdo();

        if (_d3kos_nonce_used($pdo, $nonce)) {
            http_response_code(401);
            echo json_encode(['success' => false, 'error' => 'replayed_nonce']);
            exit;
        }

        $stmt = $pdo->prepare(
            "SELECT HEX(public_key) AS pub_hex, status FROM amboat_device_enrolments WHERE device_token = ?"
        );
        $stmt->execute([$token]);
        $row = $stmt->fetch(PDO::FETCH_OBJ);

        if (!$row) {
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

        _d3kos_mark_nonce_used($pdo, $nonce);
        return $token;
    }

    // ── Legacy Bearer-key path — transition period only ───────────────────────
    if (defined('AMBOAT_API_KEY')
        && preg_match('/^Bearer\s+(.+)$/i', $auth, $m)
        && hash_equals(AMBOAT_API_KEY, $m[1])
        && !empty($token)) {
        try {
            $pdo  = _d3kos_get_pdo();
            $stmt = $pdo->prepare(
                "INSERT IGNORE INTO amboat_registration_audit
                    (event, user_id, detail, ip, created_at)
                 VALUES ('legacy_key_used', NULL, ?, ?, NOW())"
            );
            $stmt->execute([
                substr($token, 0, 8) . '... endpoint=' . ($_SERVER['SCRIPT_NAME'] ?? '?'),
                substr($_SERVER['REMOTE_ADDR'] ?? '', 0, 45),
            ]);
        } catch (PDOException $e) {
            // Audit write failure is non-fatal — still allow the request through
        }
        return $token;
    }

    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
