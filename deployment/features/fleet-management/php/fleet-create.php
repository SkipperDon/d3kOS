<?php
/**
 * mobile/fleet-create.php
 * Create a new fleet. One fleet per device (owner role).
 *
 * Method: POST
 * Auth:   Authorization: Bearer <app_token>  (PWA user)
 *         X-Device-Token: <UUID>
 * Body:   { "name": "My Charter Fleet", "fleet_type": "charter" }
 *
 * fleet_type: charter | fishing | marina | other
 *
 * Response: { "success": true, "data": { "fleet_id": N, "fleet_code": "ABC123" } }
 *
 * Rules:
 *  - T3 only
 *  - One fleet per device (owner)
 *  - fleet_code is 6 uppercase alphanumeric, unique, auto-generated
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Device-Token');
header('Access-Control-Allow-Methods: POST, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST')    { amboat_send_error('Method not allowed.', 405); }

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$auth         = amboat_auth_app_request();
$user_id      = $auth['user_id'];
$device_token = $_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '';

// If no X-Device-Token header (PWA flow), look up from wpax_usermeta
if (empty($device_token)) {
    $device_token = amboat_get_user_meta($user_id, 'atmyboat_device_token') ?? '';
}

if (empty($device_token) ||
    !preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $device_token)) {
    amboat_send_error('X-Device-Token required (or device not paired to this account).', 400);
}

// T3 gate
$tier = amboat_get_user_tier($user_id);
if ($tier < 3) {
    amboat_send_error('Fleet management requires Tier 3. Upgrade at atmyboat.com/upgrade', 403);
}

$body       = amboat_json_body();
$name       = trim($body['name'] ?? '');
$fleet_type = in_array($body['fleet_type'] ?? '', ['charter', 'fishing', 'marina', 'other'])
              ? $body['fleet_type'] : 'fishing';

if (empty($name) || strlen($name) > 100) {
    amboat_send_error('Fleet name required (max 100 chars).', 400);
}

$db = amboat_get_db();

// Check if this device is already a fleet owner
$stmt = $db->prepare(
    "SELECT fleet_id FROM amboat_fleets WHERE owner_device_token = ? LIMIT 1"
);
$stmt->bind_param('s', $device_token);
$stmt->execute();
if ($stmt->get_result()->num_rows > 0) {
    amboat_send_error('Device already owns a fleet. Leave or delete it before creating a new one.', 409);
}

// Generate unique 6-char fleet code
$fleet_code = '';
$attempts   = 0;
do {
    $fleet_code = strtoupper(substr(str_shuffle('ABCDEFGHJKLMNPQRSTUVWXYZ23456789'), 0, 6));
    $stmt = $db->prepare("SELECT fleet_id FROM amboat_fleets WHERE fleet_code = ? LIMIT 1");
    $stmt->bind_param('s', $fleet_code);
    $stmt->execute();
    $attempts++;
} while ($stmt->get_result()->num_rows > 0 && $attempts < 20);

if ($attempts >= 20) {
    amboat_send_error('Could not generate unique fleet code. Try again.', 503);
}

// Insert fleet
$stmt = $db->prepare(
    "INSERT INTO amboat_fleets (fleet_code, name, fleet_type, owner_device_token) VALUES (?, ?, ?, ?)"
);
$stmt->bind_param('ssss', $fleet_code, $name, $fleet_type, $device_token);
$stmt->execute();
$fleet_id = $db->insert_id;

// Add owner as first member
$role = 'owner';
$stmt = $db->prepare(
    "INSERT INTO amboat_fleet_members (fleet_id, device_token, role) VALUES (?, ?, ?)"
);
$stmt->bind_param('iss', $fleet_id, $device_token, $role);
$stmt->execute();

amboat_send_success([
    'fleet_id'   => $fleet_id,
    'fleet_code' => $fleet_code,
    'name'       => $name,
    'fleet_type' => $fleet_type,
    'message'    => "Fleet created. Share code $fleet_code with other vessels to join.",
]);

// ── Helpers ───────────────────────────────────────────────────────────────────

function amboat_get_user_tier(int $user_id): int {
    $raw = amboat_get_user_meta($user_id, 'atmyboat_tier');
    if ($raw === null) return 0;
    // Handle both "T3" string and integer 3
    if (is_string($raw) && preg_match('/^T(\d)$/', $raw, $m)) return (int)$m[1];
    return (int)$raw;
}
