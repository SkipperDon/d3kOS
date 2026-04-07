<?php
/**
 * mobile/fleet-leave.php
 * Leave (member) or delete (owner) a fleet.
 *
 * Method: POST
 * Auth:   Authorization: Bearer <app_token>  (PWA user)
 * Body:   { "fleet_id": N }
 *
 * Owner:  deletes entire fleet + all member rows + positions + engine snapshots
 * Member: removes only this device from fleet_members
 *
 * Response: { "success": true, "data": { "action": "deleted"|"left", "fleet_id": N } }
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

if (empty($device_token)) {
    $device_token = amboat_get_user_meta($user_id, 'atmyboat_device_token') ?? '';
}

if (empty($device_token) ||
    !preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $device_token)) {
    amboat_send_error('X-Device-Token required (or device not paired to this account).', 400);
}

$body     = amboat_json_body();
$fleet_id = (int)($body['fleet_id'] ?? 0);
if ($fleet_id <= 0) {
    amboat_send_error('fleet_id required.', 400);
}

$db = amboat_get_db();

// Verify this device is actually in this fleet
$stmt = $db->prepare(
    "SELECT role FROM amboat_fleet_members WHERE fleet_id = ? AND device_token = ? LIMIT 1"
);
$stmt->bind_param('is', $fleet_id, $device_token);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();

if (!$row) {
    amboat_send_error('Device is not a member of this fleet.', 404);
}

$role = $row['role'];

if ($role === 'owner') {
    // Delete entire fleet and all related data
    foreach ([
        "DELETE FROM amboat_fleet_engine_snapshots WHERE fleet_id = ?",
        "DELETE FROM amboat_fleet_positions       WHERE fleet_id = ?",
        "DELETE FROM amboat_fleet_members         WHERE fleet_id = ?",
        "DELETE FROM amboat_fleets                WHERE fleet_id = ?",
    ] as $sql) {
        $stmt = $db->prepare($sql);
        $stmt->bind_param('i', $fleet_id);
        $stmt->execute();
    }
    // Tell Pi to clear fleet.json and stop pushing
    amboat_enqueue_fleet_unassign($db, $user_id);
    amboat_send_success(['action' => 'deleted', 'fleet_id' => $fleet_id]);
} else {
    // Member: just remove self
    $stmt = $db->prepare(
        "DELETE FROM amboat_fleet_members WHERE fleet_id = ? AND device_token = ?"
    );
    $stmt->bind_param('is', $fleet_id, $device_token);
    $stmt->execute();
    // Tell Pi to clear fleet.json and stop pushing
    amboat_enqueue_fleet_unassign($db, $user_id);
    amboat_send_success(['action' => 'left', 'fleet_id' => $fleet_id]);
}

function amboat_enqueue_fleet_unassign($db, int $user_id): void {
    $cmd    = 'fleet_unassign';
    $status = 'pending';
    $stmt   = $db->prepare(
        "INSERT INTO amboat_command_queue (user_id, command, payload, status, created_at)
         VALUES (?, ?, '{}', ?, NOW())"
    );
    $stmt->bind_param('iss', $user_id, $cmd, $status);
    $stmt->execute();
}
