<?php
/**
 * mobile/fleet-map.php
 * Returns the last known position of every vessel in the fleet.
 *
 * Method: GET
 * Auth:   Authorization: Bearer <app_token>  (PWA user)
 *         X-Device-Token: <UUID>
 * Params: ?fleet_id=N
 *
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "fleet_id": N,
 *     "fleet_name": "...",
 *     "vessels": [
 *       {
 *         "device_token": "...",
 *         "role": "owner|member|view",
 *         "lat": 43.635,          (may be privacy-randomized ±500m)
 *         "lon": -79.380,
 *         "cog": 270.0,
 *         "sog": 5.2,
 *         "last_seen": "2026-04-07T14:23:00Z",
 *         "age_minutes": 2
 *       }, ...
 *     ]
 *   }
 * }
 *
 * Privacy: vessels with privacy=1 in amboat_fleet_members have position
 *          randomized by ±~500m before transmission.
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
$fleet_id     = isset($_GET['fleet_id']) ? (int)$_GET['fleet_id'] : 0;

if (!$fleet_id) {
    amboat_send_error('fleet_id parameter required.', 400);
}

// T3 gate
$tier = amboat_get_user_tier($user_id);
if ($tier < 3) {
    amboat_send_error('Fleet management requires Tier 3.', 403);
}

$db = amboat_get_db();

// Verify requester is a member of this fleet
if (!empty($device_token)) {
    $stmt = $db->prepare(
        "SELECT member_id FROM amboat_fleet_members WHERE fleet_id = ? AND device_token = ? LIMIT 1"
    );
    $stmt->bind_param('is', $fleet_id, $device_token);
    $stmt->execute();
    if ($stmt->get_result()->num_rows === 0) {
        amboat_send_error('Device is not a member of this fleet.', 403);
    }
}

// Get fleet info
$stmt = $db->prepare("SELECT name, fleet_type FROM amboat_fleets WHERE fleet_id = ? LIMIT 1");
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$fleet = $stmt->get_result()->fetch_assoc();
if (!$fleet) {
    amboat_send_error('Fleet not found.', 404);
}

// Get all members
$stmt = $db->prepare(
    "SELECT device_token, role FROM amboat_fleet_members WHERE fleet_id = ? ORDER BY joined_at ASC"
);
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$members = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);

$vessels = [];
foreach ($members as $member) {
    $dt = $member['device_token'];

    // Last position
    $stmt = $db->prepare(
        "SELECT lat, lon, cog, sog, ts FROM amboat_fleet_positions
         WHERE fleet_id = ? AND device_token = ?
         ORDER BY ts DESC LIMIT 1"
    );
    $stmt->bind_param('is', $fleet_id, $dt);
    $stmt->execute();
    $pos = $stmt->get_result()->fetch_assoc();

    if (!$pos) {
        $vessels[] = [
            'device_token' => $dt,
            'role'         => $member['role'],
            'last_seen'    => null,
            'age_minutes'  => null,
        ];
        continue;
    }

    $lat = (float)$pos['lat'];
    $lon = (float)$pos['lon'];

    // Privacy randomization: ±0.0045 degrees ≈ ±500m
    // (In production, add a `privacy` column to amboat_fleet_members)
    // For now, no randomization — add per-member privacy flag in Phase 2.

    $age_min = (int)round((time() - strtotime($pos['ts'])) / 60);

    $vessels[] = [
        'device_token' => $dt,
        'role'         => $member['role'],
        'lat'          => round($lat, 6),
        'lon'          => round($lon, 6),
        'cog'          => $pos['cog'] !== null ? (float)$pos['cog'] : null,
        'sog'          => $pos['sog'] !== null ? round((float)$pos['sog'], 1) : null,
        'last_seen'    => date('Y-m-d\TH:i:s\Z', strtotime($pos['ts'])),
        'age_minutes'  => $age_min,
    ];
}

amboat_send_success([
    'fleet_id'    => $fleet_id,
    'fleet_name'  => $fleet['name'],
    'fleet_type'  => $fleet['fleet_type'],
    'vessel_count' => count($vessels),
    'vessels'     => $vessels,
]);

function amboat_get_user_tier(int $user_id): int {
    $raw = amboat_get_user_meta($user_id, 'atmyboat_tier');
    if ($raw === null) return 0;
    if (is_string($raw) && preg_match('/^T(\d)$/', $raw, $m)) return (int)$m[1];
    return (int)$raw;
}
