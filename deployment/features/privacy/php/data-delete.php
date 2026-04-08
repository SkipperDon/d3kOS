<?php
/**
 * d3kOS v0.9.9 — GDPR Account Erasure
 *
 * Anonymizes and deletes all personal data for the authenticated user.
 * Satisfies GDPR Article 17 (right to erasure) and CCPA right to delete.
 *
 * Auth:   Bearer app_token
 * Method: POST
 * Body:   { "confirm": true }
 *
 * What is deleted / anonymized:
 *   - wpax_users.user_email        → deleted_{user_id}@deleted.atmyboat.com
 *   - wpax_users.display_name      → [Deleted User]
 *   - wpax_usermeta atmyboat_*     → all rows deleted (tier, fmp, app_token, etc.)
 *   - d3kos_pairings               → rows for this user deleted
 *   - amboat_support_tickets       → rows for this user deleted
 *   - amboat_command_queue         → rows for this user's device_tokens deleted
 *   - amboat_billing               → user_id set to NULL (legal retention, PII removed)
 *   - amboat_deletion_log          → one row inserted (no PII, just user_id + timestamp)
 *
 * Billing rows are anonymized (not deleted) for financial record-keeping requirements.
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/data-delete.php
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

// ── Require explicit confirmation ─────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true) ?? [];
if (empty($body['confirm'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'confirm:true required']);
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

// ── Get device tokens before we delete pairings ───────────────────────────────

$stmt = $db->prepare("SELECT pi_id FROM d3kos_pairings WHERE user_id = ?");
$stmt->bind_param('i', $user_id);
$stmt->execute();
$pair_rows = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();
$device_tokens = array_column($pair_rows, 'pi_id');

// ── 1. Anonymize WordPress user ───────────────────────────────────────────────

$anon_email = "deleted_{$user_id}@deleted.atmyboat.com";
$stmt = $db->prepare(
    "UPDATE wpax_users SET user_email = ?, display_name = '[Deleted User]' WHERE ID = ?"
);
$stmt->bind_param('si', $anon_email, $user_id);
$stmt->execute();
$stmt->close();

// ── 2. Delete all atmyboat usermeta ───────────────────────────────────────────

$stmt = $db->prepare(
    "DELETE FROM wpax_usermeta WHERE user_id = ? AND meta_key LIKE 'atmyboat_%'"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$stmt->close();

// ── 3. Delete pairings ────────────────────────────────────────────────────────

$stmt = $db->prepare("DELETE FROM d3kos_pairings WHERE user_id = ?");
$stmt->bind_param('i', $user_id);
$stmt->execute();
$stmt->close();

// ── 4. Delete support tickets ─────────────────────────────────────────────────

$stmt = $db->prepare("DELETE FROM amboat_support_tickets WHERE user_id = ?");
$stmt->bind_param('i', $user_id);
$stmt->execute();
$stmt->close();

// ── 5. Delete command queue entries for this user's devices ──────────────────

if (!empty($device_tokens)) {
    $placeholders = implode(',', array_fill(0, count($device_tokens), '?'));
    $types = str_repeat('s', count($device_tokens));
    $stmt = $db->prepare(
        "DELETE FROM amboat_command_queue WHERE device_token IN ($placeholders)"
    );
    $stmt->bind_param($types, ...$device_tokens);
    $stmt->execute();
    $stmt->close();
}

// ── 6. Anonymize billing rows (retain for legal, remove PII) ─────────────────

$billing_check = $db->query("SHOW TABLES LIKE 'amboat_billing'");
if ($billing_check && $billing_check->num_rows > 0) {
    $stmt = $db->prepare(
        "UPDATE amboat_billing SET user_id = NULL WHERE user_id = ?"
    );
    $stmt->bind_param('i', $user_id);
    $stmt->execute();
    $stmt->close();
}

// ── 7. Log the deletion (no PII stored) ──────────────────────────────────────

$db->query(
    "CREATE TABLE IF NOT EXISTS amboat_deletion_log (
        id         INT AUTO_INCREMENT PRIMARY KEY,
        user_id    INT  NOT NULL,
        deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"
);
$stmt = $db->prepare("INSERT INTO amboat_deletion_log (user_id) VALUES (?)");
$stmt->bind_param('i', $user_id);
$stmt->execute();
$stmt->close();

$db->close();

echo json_encode([
    'success'    => true,
    'message'    => 'Your account data has been deleted. Billing records are anonymized as required by law.',
    'deleted_at' => date('Y-m-d H:i:s'),
]);
