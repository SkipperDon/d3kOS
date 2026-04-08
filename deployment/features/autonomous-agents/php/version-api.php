<?php
/**
 * d3kOS Version API — CRM Fleet Version Dashboard
 * v0.9.8 — S33
 *
 * CRM-facing API for reading fleet version state.
 * Auth: Bearer amboat_api_key (same as all CRM proxies).
 *
 * Actions (GET):
 *   ?action=fleet          — per-device version list + summary stats
 *   ?action=distribution   — version count breakdown (for chart)
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/version-api.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!preg_match('/^Bearer\s+(.+)$/i', $auth, $m) || $m[1] !== AMBOAT_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

$action = $_GET['action'] ?? 'fleet';

// ── GET: fleet — per-device version list ──────────────────────────────────────

if ($action === 'fleet') {
    // Fetch latest active incremental version for "up to date" comparison
    $latest_row = $db->query(
        "SELECT version FROM amboat_versions
         WHERE update_type='incremental' AND is_active=1
         ORDER BY published_at DESC LIMIT 1"
    )->fetch_assoc();
    $latest_version = $latest_row ? $latest_row['version'] : '';

    // All paired devices with version info
    // Left join so devices that haven't reported yet still appear
    $rows = $db->query(
        "SELECT
            d.device_token,
            d.current_version,
            d.version_updated_at,
            d.version_check_count,
            u.display_name,
            u.user_email,
            um_tier.meta_value AS tier,
            p.last_seen_at
         FROM amboat_devices d
         LEFT JOIN d3kos_pairings p ON p.pi_id = d.device_token
         LEFT JOIN wpax_users u ON u.ID = p.user_id
         LEFT JOIN wpax_usermeta um_tier
               ON um_tier.user_id = p.user_id AND um_tier.meta_key = 'atmyboat_tier'
         ORDER BY d.version_updated_at DESC
         LIMIT 200"
    );

    if (!$rows) {
        // amboat_devices may not have version columns yet — try without them
        $rows = $db->query(
            "SELECT
                d.device_token,
                NULL AS current_version,
                NULL AS version_updated_at,
                NULL AS version_check_count,
                u.display_name,
                u.user_email,
                um_tier.meta_value AS tier,
                p.last_seen_at
             FROM amboat_devices d
             LEFT JOIN d3kos_pairings p ON p.pi_id = d.device_token
             LEFT JOIN wpax_users u ON u.ID = p.user_id
             LEFT JOIN wpax_usermeta um_tier
                   ON um_tier.user_id = p.user_id AND um_tier.meta_key = 'atmyboat_tier'
             ORDER BY p.last_seen_at DESC
             LIMIT 200"
        );
    }

    $devices     = [];
    $counts      = ['up_to_date' => 0, 'behind' => 0, 'unknown' => 0, 'offline' => 0];
    $now         = time();

    while ($row = $rows->fetch_assoc()) {
        $ver      = $row['current_version'] ?? null;
        $last_upd = $row['version_updated_at'] ?? null;
        $last_pi  = $row['last_seen_at'] ?? null;

        // Staleness: if version_updated_at > 48h ago, consider offline for version purposes
        $hours_since = $last_upd
            ? round((strtotime('now') - strtotime($last_upd)) / 3600, 1)
            : null;

        $pi_online = $last_pi
            ? (time() - strtotime($last_pi) < 300)
            : false;

        if (!$ver) {
            $version_status = 'unknown';
            $counts['unknown']++;
        } elseif ($hours_since !== null && $hours_since > 48) {
            $version_status = 'offline';
            $counts['offline']++;
        } elseif ($latest_version && version_compare($ver, $latest_version, '<')) {
            $version_status = 'behind';
            $counts['behind']++;
        } else {
            $version_status = 'up_to_date';
            $counts['up_to_date']++;
        }

        $devices[] = [
            'device_token'       => $row['device_token'],
            'device_short'       => substr($row['device_token'] ?? '', 0, 12),
            'display_name'       => $row['display_name'] ?? '—',
            'user_email'         => $row['user_email'] ?? '—',
            'tier'               => $row['tier'] ?? 'T0',
            'current_version'    => $ver ?? '—',
            'latest_version'     => $latest_version ?: '—',
            'version_status'     => $version_status,
            'version_updated_at' => $last_upd ?? '—',
            'hours_since_check'  => $hours_since,
            'check_count'        => (int)($row['version_check_count'] ?? 0),
            'pi_online'          => $pi_online,
            'last_seen'          => $last_pi ?? '—',
        ];
    }

    $total = count($devices);
    $db->close();

    echo json_encode([
        'success'        => true,
        'latest_version' => $latest_version ?: '—',
        'total'          => $total,
        'summary'        => $counts,
        'devices'        => $devices,
    ]);
    exit;
}

// ── GET: distribution — version count breakdown ────────────────────────────────

if ($action === 'distribution') {
    $rows = $db->query(
        "SELECT current_version, COUNT(*) AS count
         FROM amboat_devices
         WHERE current_version IS NOT NULL
         GROUP BY current_version
         ORDER BY count DESC"
    )->fetch_all(MYSQLI_ASSOC);

    $db->close();
    echo json_encode(['success' => true, 'distribution' => $rows]);
    exit;
}

$db->close();
http_response_code(400);
echo json_encode(['success' => false, 'error' => 'Unknown action']);
