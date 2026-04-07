<?php
/**
 * mobile/fleet-ingest.php
 * Pi pushes GPS position + engine snapshot every 1 minute.
 *
 * Method: POST
 * Auth:   Authorization: Bearer <AMBOAT_API_KEY>
 *         X-Device-Token: <UUID>
 * Body: {
 *   "fleet_id": N,
 *   "lat": 43.635,
 *   "lon": -79.380,
 *   "cog": 270.0,      (optional — course over ground degrees)
 *   "sog": 5.2,        (optional — speed over ground knots)
 *   "rpm": 2200,       (optional)
 *   "oil_pressure_kpa": 310.5,  (optional)
 *   "coolant_temp_c": 82.1,     (optional)
 *   "engine_hours": 124.5       (optional)
 * }
 *
 * Rate limit: 1 write per 50 seconds per device (enforced server-side).
 * Prunes: positions older than 24h, engine snapshots older than 7 days.
 *
 * Response: { "success": true, "data": { "position_id": N } }
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Device-Token');
header('Access-Control-Allow-Methods: POST, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST')    { amboat_send_error('Method not allowed.', 405); }

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$auth         = amboat_auth_pi_request();
$device_token = $auth['device_token'];

$body     = amboat_json_body();
$fleet_id = isset($body['fleet_id']) ? (int)$body['fleet_id'] : 0;
$lat      = isset($body['lat'])      ? (float)$body['lat']     : null;
$lon      = isset($body['lon'])      ? (float)$body['lon']     : null;

if (!$fleet_id || $lat === null || $lon === null) {
    amboat_send_error('fleet_id, lat, and lon required.', 400);
}
if ($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) {
    amboat_send_error('Invalid GPS coordinates.', 400);
}

$cog     = isset($body['cog'])              ? (float)$body['cog']              : null;
$sog     = isset($body['sog'])              ? (float)$body['sog']              : null;
$rpm     = isset($body['rpm'])              ? (int)$body['rpm']                : null;
$oil     = isset($body['oil_pressure_kpa']) ? (float)$body['oil_pressure_kpa'] : null;
$cool    = isset($body['coolant_temp_c'])   ? (float)$body['coolant_temp_c']   : null;
$hours   = isset($body['engine_hours'])     ? (float)$body['engine_hours']     : null;

$db = amboat_get_db();

// Verify device is a member of this fleet
$stmt = $db->prepare(
    "SELECT m.member_id FROM amboat_fleet_members m
     WHERE m.fleet_id = ? AND m.device_token = ? LIMIT 1"
);
$stmt->bind_param('is', $fleet_id, $device_token);
$stmt->execute();
if ($stmt->get_result()->num_rows === 0) {
    amboat_send_error('Device is not a member of this fleet.', 403);
}

// Rate limit: reject if a position was written for this device within the last 50 seconds
$stmt = $db->prepare(
    "SELECT ts FROM amboat_fleet_positions
     WHERE fleet_id = ? AND device_token = ?
     ORDER BY ts DESC LIMIT 1"
);
$stmt->bind_param('is', $fleet_id, $device_token);
$stmt->execute();
$last = $stmt->get_result()->fetch_assoc();
if ($last) {
    $age = time() - strtotime($last['ts']);
    if ($age < 50) {
        amboat_send_success(['rate_limited' => true, 'retry_after_s' => 50 - $age]);
    }
}

// Write position
$ts   = date('Y-m-d H:i:s');
$stmt = $db->prepare(
    "INSERT INTO amboat_fleet_positions (fleet_id, device_token, lat, lon, cog, sog, ts)
     VALUES (?, ?, ?, ?, ?, ?, ?)"
);
$stmt->bind_param('isdddds', $fleet_id, $device_token, $lat, $lon, $cog, $sog, $ts);
$stmt->execute();
$pos_id = $db->insert_id;

// Write engine snapshot if any engine fields provided
if ($rpm !== null || $oil !== null || $cool !== null || $hours !== null) {
    $stmt = $db->prepare(
        "INSERT INTO amboat_fleet_engine_snapshots
         (fleet_id, device_token, rpm, oil_pressure_kpa, coolant_temp_c, engine_hours, ts)
         VALUES (?, ?, ?, ?, ?, ?, ?)"
    );
    $stmt->bind_param('isiidds', $fleet_id, $device_token, $rpm, $oil, $cool, $hours, $ts);
    $stmt->execute();
}

// Prune old rows (run 1-in-60 chance to avoid every request doing cleanup)
if (mt_rand(1, 60) === 1) {
    $db->query("DELETE FROM amboat_fleet_positions WHERE ts < DATE_SUB(NOW(), INTERVAL 24 HOUR)");
    $db->query("DELETE FROM amboat_fleet_engine_snapshots WHERE ts < DATE_SUB(NOW(), INTERVAL 7 DAY)");
}

amboat_send_success(['position_id' => $pos_id]);
