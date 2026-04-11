<?php
/**
 * d3kOS v0.9.4.1 — Community Map Data Endpoint
 *
 * Returns anonymised fleet positions and hazard markers for the community map.
 * No authentication required — all position data is blurred to ~1km precision.
 *
 * Method: GET
 * Params: (optional) lat, lng, radius_km (default 500)
 *
 * Response: { success, data: { positions: [...], markers: [...], fleet_count } }
 *
 * Positions come from wpax_usermeta of users who have:
 *   - atmyboat_map_sharing = '1'
 *   - atmyboat_last_sync within 48 hours
 *   - atmyboat_position_lat/lng set (non-zero)
 *
 * Markers come from amboat_community_markers (table auto-created on first call).
 * All coordinates rounded to 2 decimal places on output (~1km privacy blur).
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/community-get.php
 */

error_reporting(0);
@ini_set('display_errors', 0);

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');   // public read endpoint

require_once __DIR__ . '/config.php';

mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    echo json_encode(['success' => false, 'error' => 'DB unavailable']);
    exit;
}

// Auto-create community markers table if absent
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

// Auto-create community positions table if absent (for Pi-direct posting, Phase 3)
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

// ── Fleet positions — from usermeta (users who enabled map sharing) ────────────
//
// Reads from wpax_usermeta — no Pi changes needed, data already flows through
// data-ingress.php. Positions rounded to 2 decimal places (~1.1km precision).
// Users with sharing off or no position data are excluded.

$positions_res = $db->query(
    "SELECT
        ROUND(CAST(um_lat.meta_value AS DECIMAL(9,6)), 2) AS lat,
        ROUND(CAST(um_lng.meta_value AS DECIMAL(9,6)), 2) AS lng
     FROM wpax_usermeta um_lat
     JOIN wpax_usermeta um_lng
          ON um_lng.user_id = um_lat.user_id
          AND um_lng.meta_key = 'atmyboat_position_lng'
     JOIN wpax_usermeta um_sharing
          ON um_sharing.user_id = um_lat.user_id
          AND um_sharing.meta_key = 'atmyboat_map_sharing'
          AND um_sharing.meta_value = '1'
     JOIN wpax_usermeta um_sync
          ON um_sync.user_id = um_lat.user_id
          AND um_sync.meta_key = 'atmyboat_last_sync'
     WHERE um_lat.meta_key = 'atmyboat_position_lat'
       AND um_lat.meta_value != ''
       AND um_lat.meta_value != '0'
       AND CAST(um_lat.meta_value AS DECIMAL(9,6)) != 0
       AND um_sync.meta_value > DATE_SUB(NOW(), INTERVAL 48 HOUR)
     LIMIT 500"
);

$positions = [];
if ($positions_res) {
    while ($r = $positions_res->fetch_assoc()) {
        // Skip zero coordinates (no GPS fix)
        if ((float)$r['lat'] == 0.0 && (float)$r['lng'] == 0.0) continue;
        $positions[] = [
            'lat' => (float)$r['lat'],
            'lng' => (float)$r['lng'],
        ];
    }
}

// Also include positions from amboat_community_positions (Phase 3 — Pi-direct)
$cp_res = $db->query(
    "SELECT
        ROUND(lat, 2) AS lat,
        ROUND(lon, 2) AS lng
     FROM amboat_community_positions
     WHERE updated_at > DATE_SUB(NOW(), INTERVAL 48 HOUR)
     LIMIT 500"
);
if ($cp_res) {
    while ($r = $cp_res->fetch_assoc()) {
        if ((float)$r['lat'] == 0.0 && (float)$r['lng'] == 0.0) continue;
        $positions[] = ['lat' => (float)$r['lat'], 'lng' => (float)$r['lng']];
    }
}

// ── Hazard markers ─────────────────────────────────────────────────────────────

$markers_res = $db->query(
    "SELECT
        ROUND(lat, 2)          AS lat,
        ROUND(lon, 2)          AS lng,
        marker_type            AS type,
        description,
        DATE(created_at)       AS created_at
     FROM amboat_community_markers
     WHERE (expires_at IS NULL OR expires_at > NOW())
     ORDER BY created_at DESC
     LIMIT 200"
);

$markers = [];
if ($markers_res) {
    while ($r = $markers_res->fetch_assoc()) {
        $markers[] = [
            'lat'         => (float)$r['lat'],
            'lng'         => (float)$r['lng'],
            'type'        => $r['type'],
            'description' => $r['description'] ?? '',
            'created_at'  => $r['created_at'],
        ];
    }
}

// ── Fleet count — boats synced today ──────────────────────────────────────────

$count_res = $db->query(
    "SELECT COUNT(DISTINCT user_id) AS c FROM wpax_usermeta
     WHERE meta_key = 'atmyboat_last_sync'
       AND meta_value > DATE_SUB(NOW(), INTERVAL 24 HOUR)"
);
$fleet_count = $count_res ? (int)$count_res->fetch_assoc()['c'] : 0;

$db->close();

echo json_encode([
    'success' => true,
    'data'    => [
        'positions'   => $positions,
        'markers'     => $markers,
        'fleet_count' => $fleet_count,
    ],
]);
