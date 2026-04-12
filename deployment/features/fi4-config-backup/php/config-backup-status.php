<?php
/**
 * config-backup-status.php — Admin CRM: Config Backup Status
 * FI4 — Config Backup & Recovery
 *
 * Returns all Pi backup records with owner info, sorted by last backup time.
 * Called exclusively by the Admin CRM VM — never by Pis or end users.
 *
 * Auth:   Authorization: Bearer {ADMIN_API_KEY}
 * Method: POST, body: {} (no parameters required)
 *
 * Response (success):
 *   {
 *     "success": true,
 *     "total":   42,
 *     "backups": [
 *       {
 *         "device_token":     "701e5754-...",
 *         "d3kos_version":    "0.9.9.3",
 *         "restore_attempts": 0,
 *         "updated_at":       "2026-04-12T09:43:00Z",
 *         "user_id":          12,
 *         "display_name":     "Captain Don",
 *         "user_email":       "don@example.com",
 *         "tier":             "T2"
 *       },
 *       ...
 *     ]
 *   }
 *
 * Response (table not yet created — no backups):
 *   { "success": true, "total": 0, "backups": [] }
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/config-backup-status.php
 */

error_reporting(0);
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

require_once __DIR__ . '/config.php';

// ── Auth — Bearer ADMIN_API_KEY (CRM-only endpoint) ──────────────────────────
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!hash_equals('Bearer ' . ADMIN_API_KEY, $auth_header)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────
$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}
mysqli_report(MYSQLI_REPORT_OFF);

// ── Query — all backups joined with most-recent pairing owner ─────────────────
// Subquery picks the highest user_id per Pi — reasonable proxy for most recent pairing.
// Most Pis will have exactly one pairing row; the subquery handles the multi-pairing edge case.

$stmt = $db->prepare(
    "SELECT
         c.device_token,
         c.d3kos_version,
         c.restore_attempts,
         DATE_FORMAT(c.updated_at, '%Y-%m-%dT%H:%i:%sZ') AS updated_at,
         p.user_id,
         u.display_name,
         u.user_email,
         um.meta_value AS tier
     FROM amboat_config_packages c
     LEFT JOIN (
         SELECT pi_id, MAX(user_id) AS user_id
         FROM d3kos_pairings
         GROUP BY pi_id
     ) p ON p.pi_id = c.device_token
     LEFT JOIN wpax_users       u  ON u.ID       = p.user_id
     LEFT JOIN wpax_usermeta    um ON um.user_id  = p.user_id
                                  AND um.meta_key = 'amboat_tier'
     ORDER BY c.updated_at DESC"
);

if (!$stmt) {
    // amboat_config_packages does not exist yet — no backups stored
    $db->close();
    echo json_encode(['success' => true, 'total' => 0, 'backups' => []]);
    exit;
}

$stmt->execute();
$result  = $stmt->get_result();
$backups = [];
while ($row = $result->fetch_assoc()) {
    $backups[] = [
        'device_token'     => $row['device_token'],
        'd3kos_version'    => $row['d3kos_version'],
        'restore_attempts' => (int)($row['restore_attempts'] ?? 0),
        'updated_at'       => $row['updated_at'],
        'user_id'          => isset($row['user_id']) ? (int)$row['user_id'] : null,
        'display_name'     => $row['display_name'],
        'user_email'       => $row['user_email'],
        'tier'             => $row['tier'],
    ];
}
$stmt->close();
$db->close();

echo json_encode([
    'success' => true,
    'total'   => count($backups),
    'backups' => $backups,
]);
