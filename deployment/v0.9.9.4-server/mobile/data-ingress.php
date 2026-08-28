<?php
/**
 * mobile/data-ingress.php
 * Pi posts boat state data periodically (every 30 min default, on events)
 * Also receives community map position if user has sharing enabled
 *
 * Method: POST
 * Headers: Authorization: Bearer <API_KEY>, X-Device-Token: <UUID>
 * Body (JSON):
 *   timestamp       string  ISO8601
 *   d3kos_version   string
 *   vessel_name     string
 *   position:
 *     lat           float   exact GPS lat (stored blurred in community meta)
 *     lng           float   exact GPS lng
 *   engine:
 *     rpm           int
 *     coolant_temp  float   Celsius
 *     oil_pressure  float   kPa
 *     fuel_level    float   percent 0-100
 *     hours         float   engine hours
 *   system:
 *     uptime_s      int
 *     disk_free_mb  int
 *     cpu_temp      float
 *     mem_free_mb   int
 *   alerts          array   [ { "type": "anchor_drag", "message": "..." } ]
 *
 * Privacy rules:
 * - Exact GPS is stored only in community map meta (blurred to 500m on read)
 * - Engine data stored in user meta for dashboard snapshot
 * - Alert data stored in amboat_alerts table
 * - NEVER store question text or voice content
 * - Token counts and timestamps only for AI usage
 */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

if ( $_SERVER['REQUEST_METHOD'] !== 'POST' ) {
    amboat_send_error( 'Method not allowed.', 405 );
}

$auth               = amboat_auth_pi_request();
$user_id            = $auth['user_id'];
$body               = amboat_json_body();
// Use the authenticated device_token as the canonical pi_installation_id.
// Pi sends installation_id (license.json hex) in the body but the app queries by device_token UUID
// (from d3kos_pairings.pi_id). Using device_token here keeps all tables consistent with the app.
$pi_installation_id = $auth['device_token'] ?: null;

// Update last sync timestamp
amboat_update_user_meta( $user_id, 'atmyboat_last_sync', date( 'Y-m-d H:i:s' ) );

// Write pi_installation_id + last_seen_at + d3kos_version to amboat_devices
// This is the gap fix: Pi sends its UUID on every ping; we persist it to the device record.
$db      = amboat_get_db();
$ver_val = ! empty( $body['d3kos_version'] ) ? sanitize_version( $body['d3kos_version'] ) : null;
$stmt    = $db->prepare(
    "UPDATE amboat_devices
     SET last_seen_at  = NOW(),
         d3kos_version = COALESCE(?, d3kos_version),
         pi_id         = COALESCE(?, pi_id)
     WHERE user_id = ? AND device_token = ?"
);
$stmt->bind_param( 'ssis', $ver_val, $pi_installation_id, $user_id, $auth['device_token'] );
$stmt->execute();

// Update d3kos_pairings.last_seen_at — powers T3 fleet management view
if ( $pi_installation_id ) {
    $stmt = $db->prepare(
        "UPDATE d3kos_pairings SET last_seen_at = NOW() WHERE pi_id = ? AND user_id = ?"
    );
    $stmt->bind_param( 'si', $pi_installation_id, $user_id );
    $stmt->execute();
}

// d3kOS version
if ( ! empty( $body['d3kos_version'] ) ) {
    amboat_update_user_meta( $user_id, 'atmyboat_d3kos_version', sanitize_version( $body['d3kos_version'] ) );
}

// Vessel name (sync from Pi)
if ( ! empty( $body['vessel_name'] ) ) {
    amboat_update_user_meta( $user_id, 'atmyboat_vessel_name',
        substr( strip_tags( $body['vessel_name'] ), 0, 80 ) );
}

// Position — check user's map sharing preference before storing
$position = $body['position'] ?? null;
if ( $position && isset( $position['lat'], $position['lng'] ) ) {
    $lat = (float) $position['lat'];
    $lng = (float) $position['lng'];

    // Validate lat/lng ranges
    if ( $lat >= -90 && $lat <= 90 && $lng >= -180 && $lng <= 180 ) {
        // Always store last known position for Find My Boat (not shared publicly unless sharing=1)
        amboat_update_user_meta( $user_id, 'atmyboat_position_lat',       $lat );
        amboat_update_user_meta( $user_id, 'atmyboat_position_lng',       $lng );
        amboat_update_user_meta( $user_id, 'atmyboat_last_position_time', date( 'Y-m-d H:i:s' ) );
    }
}

// Engine snapshot
$engine = $body['engine'] ?? null;
if ( $engine ) {
    if ( isset( $engine['rpm'] ) ) {
        amboat_update_user_meta( $user_id, 'atmyboat_last_rpm', (int) $engine['rpm'] );
    }
    if ( isset( $engine['coolant_temp'] ) ) {
        amboat_update_user_meta( $user_id, 'atmyboat_last_coolant_temp', (float) $engine['coolant_temp'] );
    }
    if ( isset( $engine['fuel_level'] ) ) {
        amboat_update_user_meta( $user_id, 'atmyboat_last_fuel', (float) $engine['fuel_level'] );
    }
    if ( isset( $engine['hours'] ) ) {
        amboat_update_user_meta( $user_id, 'atmyboat_engine_hours', (float) $engine['hours'] );
    }

    // Store engine snapshot in amboat_engine_snapshots table
    $db = amboat_get_db();
    $stmt = $db->prepare(
        "INSERT INTO amboat_engine_snapshots
         (user_id, pi_installation_id, rpm, coolant_temp, oil_pressure_kpa, fuel_level_pct, engine_hours_h, battery_voltage_v, snapshot_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())"
    );
    if ( $stmt ) {
        $rpm     = isset( $engine['rpm'] )             ? (int)   $engine['rpm']             : null;
        $temp    = isset( $engine['coolant_temp'] )    ? (float) $engine['coolant_temp']    : null;
        $oil     = isset( $engine['oil_pressure'] )    ? (float) $engine['oil_pressure']    : null;
        $fuel    = isset( $engine['fuel_level'] )      ? (float) $engine['fuel_level']      : null;
        $hours   = isset( $engine['hours'] )            ? (float) $engine['hours']            : null;
        $bat     = isset( $engine['battery_voltage'] ) ? (float) $engine['battery_voltage'] : null;
        $stmt->bind_param( 'isiddddd', $user_id, $pi_installation_id, $rpm, $temp, $oil, $fuel, $hours, $bat );
        $stmt->execute();
    }
}

// Alerts — store T2/T3 SMS-eligible alerts
$alerts = $body['alerts'] ?? [];
if ( is_array( $alerts ) && ! empty( $alerts ) ) {
    $db   = amboat_get_db();
    $stmt = $db->prepare(
        "INSERT INTO amboat_alerts (user_id, pi_installation_id, alert_type, message, triggered_at)
         VALUES (?, ?, ?, ?, NOW())"
    );

    $tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T0';

    foreach ( $alerts as $alert ) {
        $alert_type = substr( strip_tags( $alert['type'] ?? 'unknown' ), 0, 50 );
        $alert_msg  = substr( strip_tags( $alert['message'] ?? '' ), 0, 500 );

        if ( $stmt ) {
            $stmt->bind_param( 'isss', $user_id, $pi_installation_id, $alert_type, $alert_msg );
            $stmt->execute();
        }

        // SMS for T2/T3 (placeholder — Twilio integration in v1.1)
        // if ( in_array( $tier, ['T2','T3'], true ) ) {
        //     amboat_send_sms( $user_id, $alert_msg );
        // }
    }
}

// Boatlog text entries (v0.9.4 S1)
// Stores boatlog entries from Pi. Text content only — voice/audio files remain on Pi.
// INSERT IGNORE on (pi_installation_id, pi_entry_id) prevents duplicates across pushes.
$boatlog = $body['boatlog'] ?? [];
if ( is_array( $boatlog ) && ! empty( $boatlog ) ) {
    $db   = amboat_get_db();
    $stmt = $db->prepare(
        "INSERT IGNORE INTO amboat_boatlog
         (user_id, pi_installation_id, pi_entry_id, entry_type, content, entry_timestamp, received_at)
         VALUES (?, ?, ?, ?, ?, ?, NOW())"
    );

    if ( $stmt ) {
        foreach ( $boatlog as $entry ) {
            $pi_entry_id = substr( strip_tags( (string) ( $entry['entry_id'] ?? '' ) ), 0, 64 ) ?: null;
            $entry_type  = substr( strip_tags( $entry['type'] ?? 'general' ), 0, 50 );
            $content     = substr( strip_tags( $entry['content'] ?? '' ), 0, 5000 );
            $entry_ts    = ! empty( $entry['timestamp'] )
                ? date( 'Y-m-d H:i:s', strtotime( $entry['timestamp'] ) )
                : null;

            $stmt->bind_param( 'isssss', $user_id, $pi_installation_id, $pi_entry_id, $entry_type, $content, $entry_ts );
            $stmt->execute();
        }
    }
}

// Award map-sharing community points (3 pts/day if sharing and has GPS)
$sharing = amboat_get_user_meta( $user_id, 'atmyboat_map_sharing' );
if ( $sharing === '1' && $position ) {
    $last_daily = amboat_get_user_meta( $user_id, 'atmyboat_map_points_date' );
    $today      = date( 'Y-m-d' );
    if ( $last_daily !== $today ) {
        $score = (int) amboat_get_user_meta( $user_id, 'atmyboat_forum_score' );
        amboat_update_user_meta( $user_id, 'atmyboat_forum_score', $score + 3 );
        $monthly = (int) amboat_get_user_meta( $user_id, 'atmyboat_forum_score_month' );
        amboat_update_user_meta( $user_id, 'atmyboat_forum_score_month', $monthly + 3 );
        amboat_update_user_meta( $user_id, 'atmyboat_map_points_date', $today );
    }
}

// Build response — include any pending commands so Pi can act on them
$db   = amboat_get_db();
$stmt = $db->prepare(
    "SELECT id, command, payload FROM amboat_command_queue
     WHERE user_id = ? AND status = 'pending'
     ORDER BY created_at ASC LIMIT 5"
);
$stmt->bind_param( 'i', $user_id );
$stmt->execute();
$result = $stmt->get_result();

$pending_commands = [];
while ( $row = $result->fetch_assoc() ) {
    $pending_commands[] = [
        'id'      => (int) $row['id'],
        'command' => $row['command'],
        'payload' => json_decode( $row['payload'], true ) ?: [],
    ];
}

$tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T0';

// Return full feature flags so Pi always has current entitlements without a separate call
$feature_matrix = [
    'T0' => [
        'live_monitoring'      => false,
        'find_my_boat'         => false,
        'ota_upgrades'         => true,
        'anchor_alerts'        => false,
        'engine_alerts'        => false,
        'community_map'        => false,
        'fix_my_pi'            => false,
        'pdf_reports'          => false,
        'sms_alerts'           => false,
        'multiple_phones'      => false,
        'fleet_management'     => false,
        'camera'               => false,
        'cloud_sync'           => false,
        'engine_monitoring'    => false,
        'maintenance_schedule' => false,
        'mobile_app'           => false,
        'predictive_alerts'    => false,
        'voice_assistant'      => false,
    ],
    'T1' => [
        'live_monitoring'      => true,
        'find_my_boat'         => true,
        'ota_upgrades'         => true,
        'anchor_alerts'        => true,
        'engine_alerts'        => true,
        'community_map'        => true,
        'fix_my_pi'            => 'paid',
        'pdf_reports'          => false,
        'sms_alerts'           => false,
        'multiple_phones'      => false,
        'fleet_management'     => false,
        'camera'               => true,
        'cloud_sync'           => true,
        'engine_monitoring'    => true,
        'maintenance_schedule' => false,
        'mobile_app'           => true,
        'predictive_alerts'    => false,
        'voice_assistant'      => true,
    ],
    'T2' => [
        'live_monitoring'      => true,
        'find_my_boat'         => true,
        'ota_upgrades'         => true,
        'anchor_alerts'        => true,
        'engine_alerts'        => true,
        'community_map'        => true,
        'fix_my_pi'            => '3_per_month',
        'pdf_reports'          => true,
        'sms_alerts'           => true,
        'multiple_phones'      => true,
        'fleet_management'     => false,
        'camera'               => true,
        'cloud_sync'           => true,
        'engine_monitoring'    => true,
        'maintenance_schedule' => true,
        'mobile_app'           => true,
        'predictive_alerts'    => true,
        'voice_assistant'      => true,
    ],
    'T3' => [
        'live_monitoring'      => true,
        'find_my_boat'         => true,
        'ota_upgrades'         => true,
        'anchor_alerts'        => true,
        'engine_alerts'        => true,
        'community_map'        => true,
        'fix_my_pi'            => 'unlimited',
        'pdf_reports'          => true,
        'sms_alerts'           => true,
        'multiple_phones'      => true,
        'fleet_management'     => true,
        'camera'               => true,
        'cloud_sync'           => true,
        'engine_monitoring'    => true,
        'maintenance_schedule' => true,
        'mobile_app'           => true,
        'predictive_alerts'    => true,
        'voice_assistant'      => true,
    ],
];

$features      = $feature_matrix[ $tier ] ?? $feature_matrix['T0'];
$fmp_remaining = null;
if ( $tier === 'T2' ) {
    $used          = (int) amboat_get_user_meta( $user_id, 'atmyboat_fmp_used_month' );
    $fmp_remaining = max( 0, 3 - $used );
}

amboat_send_success( [
    'synced_at'           => date( 'Y-m-d H:i:s' ),
    'tier'                => $tier,
    'features'            => $features,
    'fix_my_pi_remaining' => $fmp_remaining,
    'pending_commands'    => $pending_commands,
] );

// ─────────────────────────────────────────────
function sanitize_version( $v ) {
    return preg_replace( '/[^v0-9\.\-]/', '', substr( $v, 0, 20 ) );
}
