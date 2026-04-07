<?php
/**
 * ticket-list.php — AtMyBoat.com PWA: My Tickets list
 * v0.9.7 Phase 2: Returns all support tickets for the authenticated user.
 *
 * Auth:   Bearer app_token (validated against wpax_usermeta)
 * Method: GET or POST
 * Returns: { success, tickets: [ { ticket_id, subject, status, admin_note, created_at, updated_at } ] }
 */

error_reporting(0);
@ini_set('display_errors', 0);

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
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

if (!preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $app_token)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Invalid app token format']);
    exit;
}

// ── DB ────────────────────────────────────────────────────────────────────────
try {
    $db = new mysqli('127.0.0.1', 'atmyb197_wp302', 'atmyboat2026', 'atmyb197_wp302');
    if ($db->connect_error) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'DB connection failed']);
        exit;
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

// ── Resolve app_token → user_id ───────────────────────────────────────────────
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

// ── Fetch tickets ─────────────────────────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT ticket_id, subject, status, admin_note, created_at, updated_at
     FROM amboat_support_tickets
     WHERE user_id = ?
     ORDER BY created_at DESC
     LIMIT 20"
);
$stmt->bind_param('i', $user_id);
$stmt->execute();
$tickets = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();

$db->close();

echo json_encode(['success' => true, 'tickets' => $tickets]);
