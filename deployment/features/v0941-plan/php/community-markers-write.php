<?php
/**
 * d3kOS v0.9.4.1 — Community Markers Write Endpoint
 *
 * POST: Store a new hazard/anchorage/fuel/other marker.
 * Auth: Bearer app_token (PWA) or Ed25519 device signature / legacy key (Pi, transition audited)
 *
 * Body (JSON):
 *   { device_token, lat, lon, marker_type, description, severity, expires_hours }
 *
 * Response: { success, marker_id }
 *
 * Marker types: hazard, shallow, debris, anchorage, fuel, other
 * Severity: low, medium, high
 * expires_hours: optional — null = permanent
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/community-markers-write.php
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

// ── Authentication ─────────────────────────────────────────────────────────────
// Mode A — PWA: Authorization: Bearer <app_token>
// Mode B — Pi: Ed25519 signature (X-Device-Token + X-Timestamp + X-Nonce + X-Signature)
//              OR legacy Bearer AMBOAT_API_KEY during transition (audited in device-auth.php)
//
// Distinguish by X-Device-Token presence: Pis always send it; PWA never does.

mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    echo json_encode(['success' => false, 'error' => 'DB unavailable']);
    exit;
}

$resolved_device_token = '';

if (!empty($_SERVER['HTTP_X_DEVICE_TOKEN'])) {
    // Mode B: Pi device auth — exits on failure; identity from verified signature
    $resolved_device_token = verify_device_request();
} else {
    // Mode A: PWA app_token
    $auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? ($_SERVER['HTTP_X_AUTHORIZATION'] ?? '');
    if (!preg_match('/^Bearer\s+(\S+)$/i', $auth_header, $m)) {
        http_response_code(401);
        echo json_encode(['success' => false, 'error' => 'Unauthorized']);
        $db->close();
        exit;
    }
    $bearer = $m[1];
    $stmt = $db->prepare(
        "SELECT user_id FROM wpax_usermeta WHERE meta_key='atmyboat_app_token' AND meta_value=? LIMIT 1"
    );
    $stmt->bind_param('s', $bearer);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if (!$row) {
        http_response_code(401);
        echo json_encode(['success' => false, 'error' => 'Unauthorized']);
        $db->close();
        exit;
    }

    $resolved_device_token = 'pwa_' . substr($bearer, 0, 32);
}

// ── Parse + validate input ────────────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON body']);
    $db->close();
    exit;
}

$lat          = isset($body['lat'])  ? (float)$body['lat']  : null;
$lon          = isset($body['lon'])  ? (float)$body['lon']  : null;
$marker_type  = $body['marker_type']  ?? 'hazard';
$description  = isset($body['description']) ? substr(trim($body['description']), 0, 200) : '';
$severity     = $body['severity']    ?? 'low';
$expires_hours = isset($body['expires_hours']) ? (int)$body['expires_hours'] : null;

// Validate coordinates
if ($lat === null || $lon === null || ($lat == 0.0 && $lon == 0.0)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Valid lat/lon required']);
    $db->close();
    exit;
}
if ($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Coordinates out of range']);
    $db->close();
    exit;
}

// Whitelist enums
$allowed_types     = ['hazard', 'shallow', 'debris', 'anchorage', 'fuel', 'other'];
$allowed_severities = ['low', 'medium', 'high'];

if (!in_array($marker_type, $allowed_types, true)) {
    $marker_type = 'hazard';
}
if (!in_array($severity, $allowed_severities, true)) {
    $severity = 'low';
}

// ── Auto-create table if absent ───────────────────────────────────────────────

$db->query(
    "CREATE TABLE IF NOT EXISTS amboat_community_markers (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        device_token VARCHAR(36)  NOT NULL DEFAULT '',
        lat          DECIMAL(9,6) NOT NULL,
        lon          DECIMAL(9,6) NOT NULL,
        marker_type  ENUM('hazard','shallow','debris','anchorage','fuel','other') DEFAULT 'hazard',
        description  VARCHAR(200),
        severity     ENUM('low','medium','high') DEFAULT 'low',
        created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
        expires_at   DATETIME     DEFAULT NULL,
        INDEX idx_loc (lat, lon),
        INDEX idx_type (marker_type)
    )"
);

// ── Rate limit: max 20 markers per device per 24h ─────────────────────────────

$rl_stmt = $db->prepare(
    "SELECT COUNT(*) AS c FROM amboat_community_markers
     WHERE device_token = ? AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)"
);
$rl_stmt->bind_param('s', $resolved_device_token);
$rl_stmt->execute();
$rl_row = $rl_stmt->get_result()->fetch_assoc();
$rl_stmt->close();

if ((int)$rl_row['c'] >= 20) {
    http_response_code(429);
    echo json_encode(['success' => false, 'error' => 'Rate limit: 20 markers per 24 hours']);
    $db->close();
    exit;
}

// ── Insert marker ─────────────────────────────────────────────────────────────

if ($expires_hours !== null && $expires_hours > 0) {
    $stmt = $db->prepare(
        "INSERT INTO amboat_community_markers
            (device_token, lat, lon, marker_type, description, severity, expires_at)
         VALUES (?, ?, ?, ?, ?, ?, DATE_ADD(NOW(), INTERVAL ? HOUR))"
    );
    $stmt->bind_param('sddsssi',
        $resolved_device_token,
        $lat, $lon,
        $marker_type, $description, $severity,
        $expires_hours
    );
} else {
    $stmt = $db->prepare(
        "INSERT INTO amboat_community_markers
            (device_token, lat, lon, marker_type, description, severity)
         VALUES (?, ?, ?, ?, ?, ?)"
    );
    $stmt->bind_param('sddsss',
        $resolved_device_token,
        $lat, $lon,
        $marker_type, $description, $severity
    );
}

if (!$stmt->execute()) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Insert failed']);
    $stmt->close();
    $db->close();
    exit;
}

$marker_id = $db->insert_id;
$stmt->close();
$db->close();

echo json_encode(['success' => true, 'marker_id' => $marker_id]);
