<?php
/**
 * d3kOS v0.9.4.1 — Community Position Endpoint (Pi-facing)
 *
 * POST: UPSERT a Pi's current position into amboat_community_positions.
 * One row per device_token — updated_at auto-refreshes on every POST.
 *
 * Auth: Ed25519 per-device signature OR legacy Bearer AMBOAT_API_KEY (transition, audited).
 *       X-Device-Token: <device_token UUID>
 *
 * Body (JSON):
 *   { lat, lon, heading (optional), speed (optional) }
 *
 * Response: { success: true }
 *
 * Positions older than 48h are excluded by community-get.php reads.
 * Coordinates stored at full precision; served rounded to 2dp (~1.1km blur).
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/community-position.php
 * Wired by: Node-RED "Post to Community DB" flow (Phase 3 — post live push)
 */

error_reporting(0);
@ini_set('display_errors', 0);

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Device-Token');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/device-auth.php';

// ── Authentication — Pi-facing only ──────────────────────────────────────────
// verify_device_request() handles Ed25519 + legacy key transition; exits on failure.
$device_token = verify_device_request();

// Basic UUID / token format guard (36 chars max)
if (strlen($device_token) > 36) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid device token']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON body']);
    exit;
}

$lat     = isset($body['lat'])     ? (float)$body['lat']     : null;
$lon     = isset($body['lon'])     ? (float)$body['lon']     : null;
$heading = isset($body['heading']) ? (int)$body['heading']   : null;
$speed   = isset($body['speed'])   ? (float)$body['speed']   : null;

// Validate coordinates
if ($lat === null || $lon === null) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'lat and lon required']);
    exit;
}
if ($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Coordinates out of range']);
    exit;
}
// Reject null-island (no GPS fix)
if ($lat == 0.0 && $lon == 0.0) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'No GPS fix']);
    exit;
}

// Clamp heading to 0–359
if ($heading !== null) {
    $heading = (($heading % 360) + 360) % 360;
}

// ── Database ──────────────────────────────────────────────────────────────────

mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(503);
    echo json_encode(['success' => false, 'error' => 'DB unavailable']);
    exit;
}

// Auto-create table if absent
$db->query(
    "CREATE TABLE IF NOT EXISTS amboat_community_positions (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        device_token VARCHAR(36)  NOT NULL UNIQUE,
        lat          DECIMAL(9,6) NOT NULL,
        lon          DECIMAL(9,6) NOT NULL,
        heading      SMALLINT     DEFAULT NULL,
        speed        DECIMAL(5,2) DEFAULT NULL,
        updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_updated (updated_at)
    )"
);

// UPSERT — one row per device_token, updated_at refreshes automatically
$stmt = $db->prepare(
    "INSERT INTO amboat_community_positions
         (device_token, lat, lon, heading, speed)
     VALUES (?, ?, ?, ?, ?)
     ON DUPLICATE KEY UPDATE
         lat        = VALUES(lat),
         lon        = VALUES(lon),
         heading    = VALUES(heading),
         speed      = VALUES(speed),
         updated_at = CURRENT_TIMESTAMP"
);

$stmt->bind_param('sddid',
    $device_token,
    $lat,
    $lon,
    $heading,
    $speed
);

if (!$stmt->execute()) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Write failed']);
    $stmt->close();
    $db->close();
    exit;
}

$stmt->close();
$db->close();

echo json_encode(['success' => true]);
