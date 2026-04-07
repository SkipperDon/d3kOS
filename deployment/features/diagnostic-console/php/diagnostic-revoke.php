<?php
/**
 * diagnostic-revoke.php — v0.9.7 Remote Diagnostic Console
 * User revokes active diagnostic consent for a ticket.
 *
 * Method: POST
 * Auth:   Bearer app_token (wpax_usermeta)
 * Body:   { "ticket_id": N }
 * Response: { "success": true, "data": { "revoked": true } }
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
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

// ── Body ──────────────────────────────────────────────────────────────────────
$body      = json_decode(file_get_contents('php://input'), true);
$ticket_id = (int)($body['ticket_id'] ?? 0);

if ($ticket_id < 1) {
    $db->close();
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id required']);
    exit;
}

// ── Revoke active consent ─────────────────────────────────────────────────────
$stmt = $db->prepare(
    "UPDATE amboat_diagnostic_consents
     SET status='revoked', revoked_at=NOW()
     WHERE ticket_id=? AND user_id=? AND status='active'"
);
$stmt->bind_param('ii', $ticket_id, $user_id);
$stmt->execute();
$affected = $stmt->affected_rows;
$stmt->close();
$db->close();

echo json_encode([
    'success' => true,
    'data'    => ['revoked' => $affected > 0],
]);
