<?php
/**
 * d3kOS Config Backup Receiver
 * FI4 — Config Backup & Recovery — Phase 1
 *
 * Called by cloud_agent.py on every sync cycle (hash-change only) and
 * after pair_confirmed. Stores a full snapshot of the Pi's config files
 * in amboat_config_packages so it can be restored after a reflash.
 *
 * Tier gate: T1, T2, T3 only. T0 Pis have no account — not applicable.
 *
 * Auth:   Authorization: Bearer {amboat_api_key}
 *         X-Device-Token: {device_token}
 * Method: POST
 * Body (JSON):
 *   {
 *     "config_json":  "{escaped JSON string — all config files}",
 *     "version":      "0.9.9.3",
 *     "checksum":     "{sha256 of config_json — optional, for integrity log}"
 *   }
 *
 * Response:
 *   {success: true, updated_at: "2026-04-12T09:43:00Z"}
 *
 * Table auto-created on first call.
 * One row per Pi (device_token UNIQUE) — UPSERT on every call.
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/config-backup.php
 */

error_reporting(0);
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth_header  = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$device_token = trim($_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '');

if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

if (empty($device_token) || strlen($device_token) > 64) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing or invalid X-Device-Token']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true);
if (!is_array($body)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON body']);
    exit;
}

$config_json = $body['config_json'] ?? '';
$version     = substr(trim($body['version']  ?? ''), 0, 20);
$checksum    = substr(trim($body['checksum'] ?? ''), 0, 64);

if (empty($config_json)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'config_json required']);
    exit;
}

// Validate config_json is valid JSON (catches corrupt payloads early)
if (json_decode($config_json, true) === null) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'config_json must be valid JSON']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}
mysqli_report(MYSQLI_REPORT_OFF);

// Auto-create table on first call — safe to run on every request
$db->query(
    "CREATE TABLE IF NOT EXISTS amboat_config_packages (
        id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        device_token     VARCHAR(64)   NOT NULL,
        config_json      MEDIUMTEXT    NOT NULL,
        d3kos_version    VARCHAR(20)   NOT NULL DEFAULT '',
        checksum         VARCHAR(64)   NOT NULL DEFAULT '',
        restore_attempts INT UNSIGNED  NOT NULL DEFAULT 0,
        last_restore_at  DATETIME      NULL,
        created_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_device_token (device_token)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
);

// Validate device_token belongs to a real registered device
// Check amboat_devices (written by version-heartbeat.php on first sync — T1+)
$stmt = $db->prepare(
    'SELECT id FROM amboat_devices WHERE device_token = ? LIMIT 1'
);
$stmt->bind_param('s', $device_token);
$stmt->execute();
$stmt->store_result();
$device_known = $stmt->num_rows > 0;
$stmt->close();

if (!$device_known) {
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'Device not registered']);
    exit;
}

// UPSERT — one row per Pi, updated on every backup push
$stmt = $db->prepare(
    'INSERT INTO amboat_config_packages
         (device_token, config_json, d3kos_version, checksum)
     VALUES (?, ?, ?, ?)
     ON DUPLICATE KEY UPDATE
         config_json   = VALUES(config_json),
         d3kos_version = VALUES(d3kos_version),
         checksum      = VALUES(checksum),
         updated_at    = NOW()'
);
$stmt->bind_param('ssss', $device_token, $config_json, $version, $checksum);
$ok = $stmt->execute();
$stmt->close();

if (!$ok) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to save backup']);
    $db->close();
    exit;
}

// Return updated_at so Pi can log it
$sel  = $db->prepare(
    "SELECT DATE_FORMAT(updated_at, '%Y-%m-%dT%H:%i:%sZ') AS updated_at
     FROM amboat_config_packages
     WHERE device_token = ?
     LIMIT 1"
);
$sel->bind_param('s', $device_token);
$sel->execute();
$res = $sel->get_result();
$row = $res ? $res->fetch_assoc() : null;
$sel->close();

$db->close();

echo json_encode([
    'success'    => true,
    'updated_at' => $row['updated_at'] ?? date('Y-m-d\TH:i:s\Z'),
]);
