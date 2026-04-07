<?php
/**
 * diagnostic-consent.php — v0.9.7 Remote Diagnostic Console
 * User grants consent for Pi to collect diagnostic data for a ticket.
 *
 * Method: POST
 * Auth:   Bearer app_token (wpax_usermeta)
 * Body:   { "ticket_id": N }
 * Response: { "success": true, "data": { "consent_id": N, "expires_at": "ISO8601" } }
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

require_once __DIR__ . '/config.php';

// ── Auth: Bearer app_token ────────────────────────────────────────────────────
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

// ── Verify ticket belongs to this user ────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT ticket_id, device_token FROM amboat_support_tickets WHERE ticket_id=? AND user_id=? LIMIT 1"
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
$device_token = $ticket['device_token'] ?? '';

// Fallback: look up pi_id from d3kos_pairings (pi_id = Pi's device_token UUID)
// device_token column on d3kos_pairings is not reliably populated; pi_id is the
// canonical identifier written by the Pi itself.
if (!$device_token) {
    $stmt = $db->prepare(
        "SELECT pi_id FROM d3kos_pairings
         WHERE user_id = ? AND pi_id IS NOT NULL AND pi_id != ''
         ORDER BY last_seen_at DESC LIMIT 1"
    );
    $stmt->bind_param('i', $user_id);
    $stmt->execute();
    $pairing = $stmt->get_result()->fetch_assoc();
    $stmt->close();
    $device_token = $pairing['pi_id'] ?? '';
}

if (!$device_token) {
    $db->close();
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'No device paired to this account']);
    exit;
}

// ── Revoke any existing active consent for this ticket ────────────────────────
$stmt = $db->prepare(
    "UPDATE amboat_diagnostic_consents SET status='revoked', revoked_at=NOW()
     WHERE ticket_id=? AND user_id=? AND status='active'"
);
$stmt->bind_param('ii', $ticket_id, $user_id);
$stmt->execute();
$stmt->close();

// ── Insert new consent (2-hour TTL) ──────────────────────────────────────────
$granted_at = date('Y-m-d H:i:s');
$expires_at = date('Y-m-d H:i:s', strtotime('+2 hours'));

$stmt = $db->prepare(
    "INSERT INTO amboat_diagnostic_consents
        (ticket_id, user_id, device_token, granted_at, expires_at, status)
     VALUES (?, ?, ?, ?, ?, 'active')"
);
$stmt->bind_param('iisss', $ticket_id, $user_id, $device_token, $granted_at, $expires_at);
$stmt->execute();
$consent_id = (int)$db->insert_id;
$stmt->close();

// ── Enqueue diagnostic_collect to Pi command queue ────────────────────────────
$payload = json_encode(['ticket_id' => $ticket_id, 'consent_id' => $consent_id]);
$cmd     = 'diagnostic_collect';
$status  = 'pending';
$stmt    = $db->prepare(
    "INSERT INTO amboat_command_queue (user_id, command, payload, status, created_at)
     VALUES (?, ?, ?, ?, NOW())"
);
$stmt->bind_param('isss', $user_id, $cmd, $payload, $status);
$stmt->execute();
$stmt->close();

$db->close();

echo json_encode([
    'success' => true,
    'data'    => [
        'consent_id' => $consent_id,
        'expires_at' => $expires_at,
    ],
]);
