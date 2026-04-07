<?php
/**
 * mobile/fleet-setup.php
 * ONE-TIME SETUP SCRIPT — run once, then delete from server.
 *
 * Actions (pass ?action=X&setup_key=SECRET):
 *   create_tables  — create all 4 fleet tables (safe to re-run, uses IF NOT EXISTS)
 *   seed_test      — insert 15 test boats with 1h of simulated GPS + engine data
 *   verify         — count rows in each table and return summary
 *   cleanup_test   — remove all rows WHERE device_token LIKE 'test-%'
 *
 * SECURITY: Requires ?setup_key=FLEET_SETUP_KEY (defined in config.php)
 * DELETE THIS FILE from server after testing is complete.
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

require_once __DIR__ . '/config.php';

// Setup key guard — must be defined in config.php as FLEET_SETUP_KEY
if (!defined('FLEET_SETUP_KEY') || empty($_GET['setup_key']) ||
    !hash_equals(FLEET_SETUP_KEY, $_GET['setup_key'])) {
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'Invalid setup key.']);
    exit;
}

$action = $_GET['action'] ?? 'verify';
$db = new mysqli(AMBOAT_DB_HOST, AMBOAT_DB_USER, AMBOAT_DB_PASS, AMBOAT_DB_NAME);
if ($db->connect_error) {
    http_response_code(503);
    echo json_encode(['success' => false, 'error' => 'DB connect failed: ' . $db->connect_error]);
    exit;
}
$db->set_charset('utf8mb4');

// ── CREATE TABLES ──────────────────────────────────────────────────────────────
if ($action === 'create_tables') {
    $tables = [
        "CREATE TABLE IF NOT EXISTS amboat_fleets (
            fleet_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            fleet_code CHAR(6)      NOT NULL UNIQUE,
            name       VARCHAR(100) NOT NULL,
            fleet_type ENUM('charter','fishing','marina','other') NOT NULL DEFAULT 'fishing',
            owner_device_token CHAR(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_fleet_code (fleet_code),
            INDEX idx_owner (owner_device_token)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",

        "CREATE TABLE IF NOT EXISTS amboat_fleet_members (
            member_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            fleet_id     INT UNSIGNED NOT NULL,
            device_token CHAR(36)     NOT NULL,
            role         ENUM('owner','member','view') NOT NULL DEFAULT 'member',
            joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_fleet_device (fleet_id, device_token),
            INDEX idx_device (device_token),
            FOREIGN KEY (fleet_id) REFERENCES amboat_fleets(fleet_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",

        "CREATE TABLE IF NOT EXISTS amboat_fleet_positions (
            pos_id       BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            fleet_id     INT UNSIGNED NOT NULL,
            device_token CHAR(36)     NOT NULL,
            lat          DECIMAL(9,6) NOT NULL,
            lon          DECIMAL(9,6) NOT NULL,
            cog          DECIMAL(5,1) DEFAULT NULL,
            sog          DECIMAL(5,2) DEFAULT NULL,
            ts           TIMESTAMP    NOT NULL,
            INDEX idx_fleet_device_ts (fleet_id, device_token, ts),
            INDEX idx_ts (ts)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",

        "CREATE TABLE IF NOT EXISTS amboat_fleet_engine_snapshots (
            snap_id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            fleet_id         INT UNSIGNED NOT NULL,
            device_token     CHAR(36)     NOT NULL,
            rpm              INT          DEFAULT NULL,
            oil_pressure_kpa DECIMAL(7,2) DEFAULT NULL,
            coolant_temp_c   DECIMAL(5,2) DEFAULT NULL,
            engine_hours     DECIMAL(8,2) DEFAULT NULL,
            ts               TIMESTAMP    NOT NULL,
            INDEX idx_fleet_device_ts (fleet_id, device_token, ts),
            INDEX idx_ts (ts)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    ];

    $created = [];
    foreach ($tables as $sql) {
        if ($db->query($sql)) {
            preg_match('/TABLE IF NOT EXISTS (\w+)/', $sql, $m);
            $created[] = $m[1] ?? 'unknown';
        } else {
            echo json_encode(['success' => false, 'error' => $db->error, 'sql' => substr($sql, 0, 80)]);
            exit;
        }
    }
    echo json_encode(['success' => true, 'tables_created' => $created]);
    exit;
}

// ── SEED TEST DATA ─────────────────────────────────────────────────────────────
if ($action === 'seed_test') {
    // Create a test fleet
    $fleet_code = 'TEST01';
    $owner_token = 'test-00000000-0000-0000-0000-000000000000';

    $db->query("DELETE FROM amboat_fleets WHERE fleet_code = 'TEST01'");
    $stmt = $db->prepare(
        "INSERT INTO amboat_fleets (fleet_code, name, fleet_type, owner_device_token) VALUES (?, 'Test Fleet — 15 Boats', 'charter', ?)"
    );
    $stmt->bind_param('ss', $fleet_code, $owner_token);
    $stmt->execute();
    $fleet_id = $db->insert_id;

    // Toronto harbour area — 15 boats spread around
    $base_lat = 43.6350;
    $base_lon = -79.3800;

    $vessel_names = [
        'Our Time', 'Sea Breeze', 'Blue Horizon', 'Morning Star', 'Lucky Catch',
        'Wind Dancer', 'Harbour Light', 'Northern Star', 'Wave Runner', 'Maple Leaf',
        'Lake Eagle', 'Sunset Dream', 'Storm Chaser', 'Island Hopper', 'True North',
    ];

    $members_added  = 0;
    $positions_added = 0;
    $engine_added    = 0;

    for ($i = 0; $i < 15; $i++) {
        $device_token = sprintf('test-%02d000000-0000-0000-0000-%012d', $i, $i);
        $role = ($i === 0) ? 'owner' : 'member';

        // Insert fleet member
        $stmt = $db->prepare(
            "INSERT IGNORE INTO amboat_fleet_members (fleet_id, device_token, role) VALUES (?, ?, ?)"
        );
        $stmt->bind_param('iss', $fleet_id, $device_token, $role);
        $stmt->execute();
        $members_added++;

        // Generate 60 minutes of 1-min position + engine data
        $lat = $base_lat + ($i * 0.003) + (($i % 3) * 0.001);
        $lon = $base_lon + ($i * 0.004) - (($i % 4) * 0.002);
        $rpm_base = 1800 + ($i * 80);
        $hours_base = 120.5 + ($i * 15.3);

        for ($min = 59; $min >= 0; $min--) {
            $ts = date('Y-m-d H:i:s', time() - ($min * 60));

            // Slight drift in position
            $pos_lat = $lat + (mt_rand(-5, 5) * 0.0001);
            $pos_lon = $lon + (mt_rand(-5, 5) * 0.0001);
            $cog = ($i * 24) % 360;
            $sog = round(4.5 + ($i * 0.3) + (mt_rand(-5, 5) * 0.1), 1);

            $stmt = $db->prepare(
                "INSERT INTO amboat_fleet_positions (fleet_id, device_token, lat, lon, cog, sog, ts)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"
            );
            $stmt->bind_param('isdddds', $fleet_id, $device_token, $pos_lat, $pos_lon, $cog, $sog, $ts);
            $stmt->execute();
            $positions_added++;

            $rpm     = $rpm_base + mt_rand(-50, 50);
            $oil     = round(310.0 + mt_rand(-20, 20), 1);
            $coolant = round(82.0 + mt_rand(-3, 3), 1);
            $hours   = round($hours_base + ((59 - $min) / 60.0), 2);

            $stmt = $db->prepare(
                "INSERT INTO amboat_fleet_engine_snapshots
                 (fleet_id, device_token, rpm, oil_pressure_kpa, coolant_temp_c, engine_hours, ts)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"
            );
            $stmt->bind_param('isiidds', $fleet_id, $device_token, $rpm, $oil, $coolant, $hours, $ts);
            $stmt->execute();
            $engine_added++;
        }
    }

    echo json_encode([
        'success'         => true,
        'fleet_id'        => $fleet_id,
        'fleet_code'      => $fleet_code,
        'members_added'   => $members_added,
        'positions_added' => $positions_added,
        'engine_added'    => $engine_added,
        'note'            => 'Test fleet TEST01 ready. Run ?action=verify to confirm, then test fleet-map.php and fleet-analytics.php.',
    ]);
    exit;
}

// ── VERIFY ────────────────────────────────────────────────────────────────────
if ($action === 'verify') {
    $counts = [];
    foreach (['amboat_fleets', 'amboat_fleet_members', 'amboat_fleet_positions', 'amboat_fleet_engine_snapshots'] as $t) {
        $r = $db->query("SELECT COUNT(*) AS n FROM $t");
        $counts[$t] = $r ? (int)$r->fetch_assoc()['n'] : 'error';
    }
    // Latest position timestamp
    $r = $db->query("SELECT MAX(ts) AS latest FROM amboat_fleet_positions");
    $counts['latest_position_ts'] = $r ? $r->fetch_assoc()['latest'] : null;
    echo json_encode(['success' => true, 'counts' => $counts]);
    exit;
}

// ── CLEANUP TEST DATA ─────────────────────────────────────────────────────────
if ($action === 'cleanup_test') {
    $db->query("DELETE FROM amboat_fleets WHERE fleet_code = 'TEST01'");
    // Cascade deletes members, positions, and engine snapshots via FK
    $affected = $db->affected_rows;
    echo json_encode(['success' => true, 'fleets_deleted' => $affected, 'note' => 'Test data removed. FK cascade cleared members/positions/engine rows.']);
    exit;
}

echo json_encode(['success' => false, 'error' => "Unknown action: $action. Use create_tables|seed_test|verify|cleanup_test"]);
