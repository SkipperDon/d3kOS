<?php
/**
 * mobile/fleet-analytics.php
 * Fleet analytics: engine hours, alert history, last-seen per vessel.
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
 *     "generated_at": "2026-04-07T14:23:00Z",
 *     "vessels": [
 *       {
 *         "device_token": "...",
 *         "role": "owner|member",
 *         "engine_hours_total":  124.5,    (max engine_hours in last 7 days)
 *         "engine_hours_7d":     4.2,      (hours recorded in last 7 days)
 *         "avg_rpm_24h":         2180,     (average RPM over last 24h)
 *         "avg_coolant_24h":     81.5,     (avg coolant temp °C last 24h)
 *         "avg_oil_24h":         309.1,    (avg oil pressure kPa last 24h)
 *         "last_seen":           "...",    (ISO8601)
 *         "age_minutes":         3
 *       }, ...
 *     ],
 *     "fleet_summary": {
 *       "vessels_active_24h": N,       (vessels with data in last 24h)
 *       "total_engine_hours":  N,      (sum of all vessel engine_hours)
 *       "fleet_avg_rpm":       N
 *     }
 *   }
 * }
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

$tier = amboat_get_user_tier($user_id);
if ($tier < 3) {
    amboat_send_error('Fleet analytics requires Tier 3.', 403);
}

$db = amboat_get_db();

// Verify requester is a member
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

// Fleet info
$stmt = $db->prepare("SELECT name, fleet_type FROM amboat_fleets WHERE fleet_id = ? LIMIT 1");
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$fleet = $stmt->get_result()->fetch_assoc();
if (!$fleet) {
    amboat_send_error('Fleet not found.', 404);
}

// All members
$stmt = $db->prepare(
    "SELECT device_token, role FROM amboat_fleet_members WHERE fleet_id = ? ORDER BY joined_at ASC"
);
$stmt->bind_param('i', $fleet_id);
$stmt->execute();
$members = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);

$vessels             = [];
$total_eng_hours     = 0.0;
$fleet_rpm_sum       = 0;
$fleet_rpm_count     = 0;
$vessels_active      = 0;
$fleet_alerts_total  = 0;

foreach ($members as $member) {
    $dt = $member['device_token'];

    // Last seen
    $stmt = $db->prepare(
        "SELECT ts FROM amboat_fleet_positions
         WHERE fleet_id = ? AND device_token = ? ORDER BY ts DESC LIMIT 1"
    );
    $stmt->bind_param('is', $fleet_id, $dt);
    $stmt->execute();
    $last_pos = $stmt->get_result()->fetch_assoc();

    $last_seen   = $last_pos ? $last_pos['ts'] : null;
    $age_minutes = $last_seen ? (int)round((time() - strtotime($last_seen)) / 60) : null;

    // Engine hours (max in last 7 days = running total; delta = hours this week)
    $stmt = $db->prepare(
        "SELECT MAX(engine_hours) AS max_h, MIN(engine_hours) AS min_h,
                AVG(rpm) AS avg_rpm, AVG(coolant_temp_c) AS avg_cool, AVG(oil_pressure_kpa) AS avg_oil,
                COUNT(*) AS snap_count
         FROM amboat_fleet_engine_snapshots
         WHERE fleet_id = ? AND device_token = ? AND ts >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    );
    $stmt->bind_param('is', $fleet_id, $dt);
    $stmt->execute();
    $eng = $stmt->get_result()->fetch_assoc();

    $eng_hours_total = $eng['max_h'] !== null ? round((float)$eng['max_h'], 1) : null;
    $eng_hours_7d    = ($eng['max_h'] !== null && $eng['min_h'] !== null)
                       ? round((float)$eng['max_h'] - (float)$eng['min_h'], 1) : null;

    // 24h averages
    $stmt = $db->prepare(
        "SELECT AVG(rpm) AS avg_rpm, AVG(coolant_temp_c) AS avg_cool, AVG(oil_pressure_kpa) AS avg_oil
         FROM amboat_fleet_engine_snapshots
         WHERE fleet_id = ? AND device_token = ? AND ts >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
    );
    $stmt->bind_param('is', $fleet_id, $dt);
    $stmt->execute();
    $eng24 = $stmt->get_result()->fetch_assoc();

    $avg_rpm_24h     = $eng24['avg_rpm']  !== null ? (int)round((float)$eng24['avg_rpm'])  : null;
    $avg_cool_24h    = $eng24['avg_cool'] !== null ? round((float)$eng24['avg_cool'], 1)   : null;
    $avg_oil_24h     = $eng24['avg_oil']  !== null ? round((float)$eng24['avg_oil'], 1)    : null;

    if ($eng_hours_total !== null) $total_eng_hours += $eng_hours_total;
    if ($avg_rpm_24h !== null)     { $fleet_rpm_sum += $avg_rpm_24h; $fleet_rpm_count++; }
    if ($age_minutes !== null && $age_minutes <= 1440) $vessels_active++;

    // ── Alert history (last 30 days) ───────────────────────────────────────────
    // amboat_alerts.pi_installation_id stores the device_token UUID
    $stmt = $db->prepare(
        "SELECT alert_type, COUNT(*) AS cnt
         FROM amboat_alerts
         WHERE pi_installation_id = ? AND triggered_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
         GROUP BY alert_type"
    );
    $stmt->bind_param('s', $dt);
    $stmt->execute();
    $alert_rows = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
    $stmt->close();

    $alerts_30d = ['total' => 0];
    foreach ($alert_rows as $ar) {
        $alerts_30d[$ar['alert_type']] = (int)$ar['cnt'];
        $alerts_30d['total']          += (int)$ar['cnt'];
    }
    $fleet_alerts_total += $alerts_30d['total'];

    $vessels[] = [
        'device_token'       => $dt,
        'role'               => $member['role'],
        'engine_hours_total' => $eng_hours_total,
        'engine_hours_7d'    => $eng_hours_7d,
        'avg_rpm_24h'        => $avg_rpm_24h,
        'avg_coolant_24h'    => $avg_cool_24h,
        'avg_oil_24h'        => $avg_oil_24h,
        'last_seen'          => $last_seen ? date('Y-m-d\TH:i:s\Z', strtotime($last_seen)) : null,
        'age_minutes'        => $age_minutes,
        'alerts_30d'         => $alerts_30d,
    ];
}

amboat_send_success([
    'fleet_id'      => $fleet_id,
    'fleet_name'    => $fleet['name'],
    'generated_at'  => date('Y-m-d\TH:i:s\Z'),
    'vessel_count'  => count($vessels),
    'vessels'       => $vessels,
    'fleet_summary' => [
        'vessels_active_24h'  => $vessels_active,
        'total_engine_hours'  => round($total_eng_hours, 1),
        'fleet_avg_rpm'       => $fleet_rpm_count > 0 ? (int)round($fleet_rpm_sum / $fleet_rpm_count) : null,
        'fleet_alerts_30d'    => $fleet_alerts_total,
    ],
]);

function amboat_get_user_tier(int $user_id): int {
    $raw = amboat_get_user_meta($user_id, 'atmyboat_tier');
    if ($raw === null) return 0;
    if (is_string($raw) && preg_match('/^T(\d)$/', $raw, $m)) return (int)$m[1];
    return (int)$raw;
}
