<?php
/**
 * mobile/fleet-status.php
 * Returns this device's current fleet membership, if any.
 *
 * Method: GET
 * Auth:   Authorization: Bearer <app_token>  (PWA user)
 *
 * Response (member):
 *   { "success": true, "data": {
 *       "fleet_id": N, "fleet_code": "ABC123", "fleet_name": "My Fleet",
 *       "fleet_type": "fishing", "role": "owner|member",
 *       "member_count": N
 *   } }
 *
 * Response (no fleet):
 *   { "success": true, "data": null }
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Device-Token');
header('Access-Control-Allow-Methods: GET, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'GET')     { amboat_send_error('Method not allowed.', 405); }

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$auth         = amboat_auth_app_request();
$user_id      = $auth['user_id'];
$device_token = $_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '';

if (empty($device_token)) {
    $device_token = amboat_get_user_meta($user_id, 'atmyboat_device_token') ?? '';
}

if (empty($device_token) ||
    !preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $device_token)) {
    amboat_send_error('X-Device-Token required (or device not paired to this account).', 400);
}

$db = amboat_get_db();

// Find fleet membership for this device
$stmt = $db->prepare("
    SELECT m.fleet_id, m.role,
           f.fleet_code, f.name AS fleet_name, f.fleet_type
    FROM amboat_fleet_members m
    JOIN amboat_fleets f ON f.fleet_id = m.fleet_id
    WHERE m.device_token = ?
    LIMIT 1
");
$stmt->bind_param('s', $device_token);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();

if (!$row) {
    amboat_send_success(null);
}

// Count members in this fleet
$fleet_id = (int)$row['fleet_id'];
$stmt = $db->prepare("SELECT COUNT(*) AS n FROM amboat_fleet_members WHERE fleet_id = ?");
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$member_count = (int)$stmt->get_result()->fetch_assoc()['n'];

amboat_send_success([
    'fleet_id'     => $fleet_id,
    'fleet_code'   => $row['fleet_code'],
    'fleet_name'   => $row['fleet_name'],
    'fleet_type'   => $row['fleet_type'],
    'role'         => $row['role'],
    'member_count' => $member_count,
]);
