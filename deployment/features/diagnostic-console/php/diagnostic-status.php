<?php
/**
 * diagnostic-status.php — v0.9.7 Remote Diagnostic Console
 * Returns consent status + whether diagnostic bundle exists for a ticket.
 *
 * Method: GET ?ticket_id=N
 * Auth:   Bearer app_token (wpax_usermeta)
 * Response: {
 *   "success": true,
 *   "data": {
 *     "consent_status": "active"|"expired"|"revoked"|"none",
 *     "expires_at": "ISO8601" | null,
 *     "bundle_ready": true|false,
 *     "bundle_size_bytes": N | null
 *   }
 * }
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'GET required']);
    exit;
}

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$app_token = trim($m[1]);

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

$stmt = $db->prepare(
    "SELECT user_id FROM wpax_usermeta WHERE meta_key='atmyboat_app_token' AND meta_value=? LIMIT 1"
);
$stmt->bind_param('s', $app_token);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$row) {
    $db->close();
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$user_id = (int)$row['user_id'];

// ── Validate ticket_id ────────────────────────────────────────────────────────
$ticket_id = (int)($_GET['ticket_id'] ?? 0);
if ($ticket_id < 1) {
    $db->close();
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id required']);
    exit;
}

// ── Verify ticket belongs to user ─────────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT ticket_id FROM amboat_support_tickets WHERE ticket_id=? AND user_id=? LIMIT 1"
);
$stmt->bind_param('ii', $ticket_id, $user_id);
$stmt->execute();
$ticket = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$ticket) {
    $db->close();
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'Ticket not found']);
    exit;
}

// ── Expire stale consents ─────────────────────────────────────────────────────
$db->query(
    "UPDATE amboat_diagnostic_consents SET status='expired'
     WHERE ticket_id={$ticket_id} AND status='active' AND expires_at < NOW()"
);

// ── Get latest consent ────────────────────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT status, expires_at FROM amboat_diagnostic_consents
     WHERE ticket_id=? AND user_id=?
     ORDER BY consent_id DESC LIMIT 1"
);
$stmt->bind_param('ii', $ticket_id, $user_id);
$stmt->execute();
$consent = $stmt->get_result()->fetch_assoc();
$stmt->close();

// ── Get bundle status ─────────────────────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT bundle_size_bytes, created_at FROM amboat_diagnostic_bundles
     WHERE ticket_id=? ORDER BY bundle_id DESC LIMIT 1"
);
$stmt->bind_param('i', $ticket_id);
$stmt->execute();
$bundle = $stmt->get_result()->fetch_assoc();
$stmt->close();
$db->close();

echo json_encode([
    'success' => true,
    'data'    => [
        'consent_status'    => $consent ? $consent['status'] : 'none',
        'expires_at'        => $consent ? $consent['expires_at'] : null,
        'bundle_ready'      => (bool)$bundle,
        'bundle_size_bytes' => $bundle ? (int)$bundle['bundle_size_bytes'] : null,
        'bundle_created_at' => $bundle ? $bundle['created_at'] : null,
    ],
]);
