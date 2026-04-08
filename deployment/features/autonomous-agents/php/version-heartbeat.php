<?php
/**
 * d3kOS Version Heartbeat Receiver
 * v0.9.8 — S33
 *
 * Called by AA2 UpdateAgent on every 24h run, whether or not an update
 * was applied. Records the Pi's current version in amboat_devices so the
 * CRM can show fleet-wide version distribution.
 *
 * Auth: Bearer amboat_api_key + X-Device-Token
 * Method: POST
 * Body (JSON): {version: "0.9.8", checked_at: "2026-04-08 01:00:00"}
 *
 * Response: {success: true, latest_version: "0.9.8.1", update_available: false}
 * (Pi can use this to confirm what the server considers current — optional use)
 *
 * Side effect: adds current_version + version_updated_at columns to
 * amboat_devices on first call if not present.
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/version-heartbeat.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth_header  = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$device_token = $_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '';

if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || $m[1] !== AMBOAT_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
if (empty($device_token)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing X-Device-Token']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────

$body    = json_decode(file_get_contents('php://input'), true) ?? [];
$version = substr(trim($body['version'] ?? ''), 0, 20);

if (!$version) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'version required']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

// Add columns to amboat_devices if not present (safe — ALTER IGNORE on MySQL)
$db->query("ALTER TABLE amboat_devices ADD COLUMN IF NOT EXISTS current_version VARCHAR(20)");
$db->query("ALTER TABLE amboat_devices ADD COLUMN IF NOT EXISTS version_updated_at DATETIME");
$db->query("ALTER TABLE amboat_devices ADD COLUMN IF NOT EXISTS version_check_count INT DEFAULT 0");

// Update device row
$stmt = $db->prepare(
    'UPDATE amboat_devices
     SET current_version = ?,
         version_updated_at = NOW(),
         version_check_count = COALESCE(version_check_count, 0) + 1
     WHERE device_token = ?'
);
$stmt->bind_param('ss', $version, $device_token);
$stmt->execute();
$updated = $db->affected_rows;
$stmt->close();

// Fetch latest active incremental version so Pi knows if it's current
$latest_row = $db->query(
    "SELECT version FROM amboat_versions
     WHERE update_type='incremental' AND is_active=1
     ORDER BY published_at DESC LIMIT 1"
)->fetch_assoc();
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
