<?php
/**
 * d3kOS Version Heartbeat Receiver
 * v0.9.9.4 — BUG-66 Phase C (S134-cont)
 *
 * Called by AA2 UpdateAgent on every 24h run, whether or not an update
 * was applied. Records the Pi's current version in amboat_devices so the
 * CRM can show fleet-wide version distribution.
 *
 * Auth: Ed25519 per-device signature (X-Device-Token + X-Timestamp + X-Nonce + X-Signature)
 *       OR legacy Bearer AMBOAT_API_KEY during transition — every legacy use is audited.
 * Method: POST
 * Body (JSON): {version: "0.9.9.4", checked_at: "2026-08-25 01:00:00"}
 *
 * Response: {success: true, latest_version: "0.9.9.4", update_available: false}
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/version-heartbeat.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/device-auth.php';

// ── Auth — identity is the result of verification, never a client-supplied field ──
$device_token = verify_device_request();

// ── Parse body ────────────────────────────────────────────────────────────────

$body    = json_decode(file_get_contents('php://input'), true) ?? [];
$version = substr(trim($body['version'] ?? ''), 0, 20);

if (!$version) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'version required']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────
// Device tables (amboat_devices) live in the WordPress DB, not the mobile config DB.
// Use WP_DB_* constants (defined in config.php alongside DB_*).

$wp_db_user = defined('WP_DB_USER') ? WP_DB_USER : DB_USER;
$wp_db_pass = defined('WP_DB_PASS') ? WP_DB_PASS : DB_PASS;
$wp_db_name = defined('WP_DB_NAME') ? WP_DB_NAME : DB_NAME;

$db = new mysqli('localhost', $wp_db_user, $wp_db_pass, $wp_db_name);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

// Add columns to amboat_devices if not present.
// Uses information_schema instead of IF NOT EXISTS — safe on MySQL 5.7 and 8.x.
$existing_cols = [];
$col_res = $db->query(
    "SELECT COLUMN_NAME FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'amboat_devices'"
);
if ($col_res) {
    while ($r = $col_res->fetch_assoc()) {
        $existing_cols[] = $r['COLUMN_NAME'];
    }
}
if (!in_array('current_version',    $existing_cols)) $db->query("ALTER TABLE amboat_devices ADD COLUMN current_version VARCHAR(20)");
if (!in_array('version_updated_at', $existing_cols)) $db->query("ALTER TABLE amboat_devices ADD COLUMN version_updated_at DATETIME");
if (!in_array('version_check_count',$existing_cols)) $db->query("ALTER TABLE amboat_devices ADD COLUMN version_check_count INT DEFAULT 0");

// Update existing device row. A row is created only by enrolment + approval (Phase A),
// never by a heartbeat. An unknown device_token was already rejected by verify_device_request()
// above — but if amboat_devices has no row yet (approval gap), we return 404.
$stmt = $db->prepare(
    'UPDATE amboat_devices
        SET current_version     = ?,
            version_updated_at  = NOW(),
            version_check_count = COALESCE(version_check_count, 0) + 1
      WHERE device_token = ?'
);
$stmt->bind_param('ss', $version, $device_token);
$stmt->execute();
$updated = $db->affected_rows;
$stmt->close();

if ($updated === 0) {
    $db->close();
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'unknown_device',
        'detail' => 'Device not found in amboat_devices — enrolment + approval required']);
    exit;
}

// Fetch latest active incremental version so Pi knows if it's current
mysqli_report(MYSQLI_REPORT_OFF);
$latest_res = $db->query(
    "SELECT version FROM amboat_versions
     WHERE update_type='incremental' AND is_active=1
     ORDER BY published_at DESC LIMIT 1"
);
$latest_row = $latest_res ? $latest_res->fetch_assoc() : null;
$latest_version  = $latest_row ? $latest_row['version'] : $version;
$update_available = version_compare($latest_version, $version, '>');

$db->close();

echo json_encode([
    'success'          => true,
    'recorded_version' => $version,
    'latest_version'   => $latest_version,
    'update_available' => $update_available,
    'device_found'     => $updated > 0,
]);
