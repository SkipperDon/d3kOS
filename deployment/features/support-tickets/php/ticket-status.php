<?php
/**
 * ticket-status.php — AtMyBoat.com PWA Support Ticket Status
 * v0.9.7 Phase 1: Returns ticket status + admin_note for the authenticated user's ticket.
 *
 * Auth:   Bearer app_token (validated against wpax_usermeta)
 * Method: GET ?ticket_id=N
 */

require_once __DIR__ . '/config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'GET required']);
    exit;
}

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

// ── Validate ticket_id param ──────────────────────────────────────────────────
$ticket_id = (int)($_GET['ticket_id'] ?? 0);
if ($ticket_id < 1) {
    $db->close();
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id required']);
    exit;
}

// ── Fetch ticket — only user's own ────────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT ticket_id, subject, status, admin_note, created_at, updated_at
     FROM amboat_support_tickets
     WHERE ticket_id = ? AND user_id = ?
     LIMIT 1"
);
$stmt->bind_param('ii', $ticket_id, $user_id);
$stmt->execute();
$ticket = $stmt->get_result()->fetch_assoc();
$stmt->close();
$db->close();

if (!$ticket) {
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'Ticket not found']);
    exit;
}

$data = [
    'ticket_id'  => (int)$ticket['ticket_id'],
    'subject'    => $ticket['subject'],
    'status'     => $ticket['status'],
    'created_at' => $ticket['created_at'],
    'updated_at' => $ticket['updated_at'],
];

// Expose admin_note only on resolved tickets
if ($ticket['status'] === 'resolved' && $ticket['admin_note']) {
    $data['admin_note'] = $ticket['admin_note'];
}

echo json_encode(['success' => true, 'data' => $data]);
