<?php
/**
 * mobile/fleet-join.php
 * Join an existing fleet using a 6-char fleet_code.
 *
 * Method: POST
 * Auth:   Authorization: Bearer <app_token>  (PWA user)
 *         X-Device-Token: <UUID>
 * Body:   { "fleet_code": "ABC123" }
 *
 * Response: { "success": true, "data": { "fleet_id": N, "fleet_name": "...", "member_count": N } }
 *
 * Rules:
 *  - T3 only
 *  - Max 15 members per fleet (including owner)
 *  - Cannot join if already a member
 *  - Cannot join own fleet (already owner)
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

if (empty($device_token) ||
    !preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $device_token)) {
    amboat_send_error('X-Device-Token header required.', 400);
}

// T3 gate
$tier = amboat_get_user_tier($user_id);
if ($tier < 3) {
    amboat_send_error('Fleet management requires Tier 3. Upgrade at atmyboat.com/upgrade', 403);
}

$body       = amboat_json_body();
$fleet_code = strtoupper(trim($body['fleet_code'] ?? ''));

if (!preg_match('/^[A-Z0-9]{6}$/', $fleet_code)) {
    amboat_send_error('fleet_code must be 6 alphanumeric characters.', 400);
}

$db = amboat_get_db();

// Look up fleet
$stmt = $db->prepare("SELECT fleet_id, name, fleet_type FROM amboat_fleets WHERE fleet_code = ? LIMIT 1");
$stmt->bind_param('s', $fleet_code);
$stmt->execute();
$fleet = $stmt->get_result()->fetch_assoc();
if (!$fleet) {
    amboat_send_error('Fleet code not found.', 404);
}
$fleet_id = (int)$fleet['fleet_id'];

// Check already a member
$stmt = $db->prepare(
    "SELECT member_id FROM amboat_fleet_members WHERE fleet_id = ? AND device_token = ? LIMIT 1"
);
$stmt->bind_param('is', $fleet_id, $device_token);
$stmt->execute();
if ($stmt->get_result()->num_rows > 0) {
    amboat_send_error('Device is already a member of this fleet.', 409);
}

// Count current members — enforce 15-vessel cap
$stmt = $db->prepare("SELECT COUNT(*) AS n FROM amboat_fleet_members WHERE fleet_id = ?");
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$member_count = (int)$stmt->get_result()->fetch_assoc()['n'];
if ($member_count >= 15) {
    amboat_send_error('Fleet has reached the maximum of 15 vessels.', 409);
}

// Add member
$role = 'member';
$stmt = $db->prepare(
    "INSERT INTO amboat_fleet_members (fleet_id, device_token, role) VALUES (?, ?, ?)"
);
$stmt->bind_param('iss', $fleet_id, $device_token, $role);
$stmt->execute();

amboat_send_success([
    'fleet_id'     => $fleet_id,
    'fleet_name'   => $fleet['name'],
    'fleet_type'   => $fleet['fleet_type'],
    'member_count' => $member_count + 1,
    'message'      => "Joined fleet '{$fleet['name']}'. Fleet push service will activate within 1 minute.",
]);

function amboat_get_user_tier(int $user_id): int {
    $raw = amboat_get_user_meta($user_id, 'atmyboat_tier');
    if ($raw === null) return 0;
    if (is_string($raw) && preg_match('/^T(\d)$/', $raw, $m)) return (int)$m[1];
    return (int)$raw;
}
