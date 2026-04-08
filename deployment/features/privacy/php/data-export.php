<?php
/**
 * d3kOS v0.9.9 — GDPR Data Export
 *
 * Returns all personal data held for the authenticated user as a JSON object.
 * Satisfies GDPR Article 15 (right of access) and CCPA right to know.
 *
 * Auth:   Bearer app_token (wpax_usermeta.atmyboat_app_token)
 * Method: GET or POST
 * Returns: { success, exported_at, user: {...}, devices: [...], tickets: [...],
 *            commands: [...], billing: [...] }
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/data-export.php
 */

error_reporting(0);
@ini_set('display_errors', 0);

header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$app_token = trim($m[1]);

if (!preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $app_token)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Invalid token format']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

// ── Resolve token → user_id ───────────────────────────────────────────────────

$stmt = $db->prepare(
    "SELECT user_id FROM wpax_usermeta WHERE meta_key='atmyboat_app_token' AND meta_value=? LIMIT 1"
);
$stmt->bind_param('s', $app_token);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$row) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$user_id = (int)$row['user_id'];

// ── Collect account data ──────────────────────────────────────────────────────

$stmt = $db->prepare(
    "SELECT user_email, display_name, user_registered FROM wpax_users WHERE ID = ? LIMIT 1"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$user_row = $stmt->get_result()->fetch_assoc();
$stmt->close();

$stmt = $db->prepare(
    "SELECT meta_key, meta_value FROM wpax_usermeta
     WHERE user_id = ? AND meta_key IN
       ('atmyboat_tier','atmyboat_fmp_used_month','atmyboat_fmp_reset_date')"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$meta_rows = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();

$meta = [];
foreach ($meta_rows as $m_row) {
    $meta[$m_row['meta_key']] = $m_row['meta_value'];
}

$account = [
    'user_id'          => $user_id,
    'email'            => $user_row['user_email']      ?? '',
    'display_name'     => $user_row['display_name']    ?? '',
    'registered_at'    => $user_row['user_registered'] ?? '',
    'tier'             => $meta['atmyboat_tier']             ?? 'T0',
    'fmp_used_month'   => $meta['atmyboat_fmp_used_month']   ?? '0',
    'fmp_reset_date'   => $meta['atmyboat_fmp_reset_date']   ?? '',
];

// ── Collect paired devices ────────────────────────────────────────────────────

$stmt = $db->prepare(
    "SELECT p.pi_id, p.vessel_name, p.paired_at, p.last_seen_at,
            d.current_version
     FROM d3kos_pairings p
     LEFT JOIN amboat_devices d ON d.device_token = p.pi_id
     WHERE p.user_id = ?
     ORDER BY p.paired_at DESC"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$devices = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();

// ── Collect support tickets ───────────────────────────────────────────────────

$stmt = $db->prepare(
    "SELECT ticket_id, subject, body, status, admin_note, created_at, updated_at
     FROM amboat_support_tickets
     WHERE user_id = ?
     ORDER BY created_at DESC"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$tickets = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();

// ── Collect command history (via paired device tokens) ────────────────────────

$commands = [];
if (!empty($devices)) {
    $tokens = array_column($devices, 'pi_id');
    $placeholders = implode(',', array_fill(0, count($tokens), '?'));
    $types = str_repeat('s', count($tokens));
    $stmt = $db->prepare(
        "SELECT command_type, payload, status, queued_at, completed_at
         FROM amboat_command_queue
         WHERE device_token IN ($placeholders)
         ORDER BY queued_at DESC
         LIMIT 100"
    );
    $stmt->bind_param($types, ...$tokens);
    $stmt->execute();
    $commands = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
    $stmt->close();
}

// ── Collect billing history ───────────────────────────────────────────────────

$billing = [];
$billing_res = $db->query(
    "SHOW TABLES LIKE 'amboat_billing'"
);
if ($billing_res && $billing_res->num_rows > 0) {
    $stmt = $db->prepare(
        "SELECT amount, currency, product, status, billing_date
         FROM amboat_billing
         WHERE user_id = ?
         ORDER BY billing_date DESC
         LIMIT 50"
    );
    $stmt->bind_param('i', $user_id);
    $stmt->execute();
    $billing = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
    $stmt->close();
}

$db->close();

// ── Return ────────────────────────────────────────────────────────────────────

echo json_encode([
    'success'     => true,
    'exported_at' => date('Y-m-d H:i:s'),
    'account'     => $account,
    'devices'     => $devices,
    'tickets'     => $tickets,
    'commands'    => $commands,
    'billing'     => $billing,
], JSON_PRETTY_PRINT);
