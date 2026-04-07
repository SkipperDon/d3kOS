<?php
/**
 * diagnostic-bundle.php — v0.9.7 Remote Diagnostic Console
 * Admin endpoint: returns diagnostic bundle metadata + base64-encoded bundle data.
 *
 * Method: GET ?ticket_id=N
 * Auth:   Bearer ADMIN_API_KEY (same key as admin-api.php)
 * Response: {
 *   "success": true,
 *   "data": {
 *     "bundle_id": N,
 *     "ticket_id": N,
 *     "bundle_size_bytes": N,
 *     "created_at": "datetime",
 *     "ai_diagnosis": null | "...",
 *     "bundle_b64": "base64string"
 *   }
 * }
 */

require_once __DIR__ . '/config.php';

if (!defined('ADMIN_API_KEY')) {
    define('ADMIN_API_KEY', 'amboat_admin_74899205409692603cb9c951c3c895ce27d92599');
}

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'GET required']);
    exit;
}

// ── Auth ──────────────────────────────────────────────────────────────────────
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if ($auth_header !== 'Bearer ' . ADMIN_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

$ticket_id = (int)($_GET['ticket_id'] ?? 0);
if ($ticket_id < 1) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id required']);
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

$stmt = $db->prepare(
    "SELECT bundle_id, ticket_id, bundle_data, bundle_size_bytes, ai_diagnosis, created_at
     FROM amboat_diagnostic_bundles
     WHERE ticket_id = ?
     ORDER BY bundle_id DESC LIMIT 1"
);
$stmt->bind_param('i', $ticket_id);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();
$stmt->close();
$db->close();

if (!$row) {
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'No bundle found for this ticket']);
    exit;
}

echo json_encode([
    'success' => true,
    'data'    => [
        'bundle_id'        => (int)$row['bundle_id'],
        'ticket_id'        => (int)$row['ticket_id'],
        'bundle_size_bytes'=> (int)$row['bundle_size_bytes'],
        'created_at'       => $row['created_at'],
        'ai_diagnosis'     => $row['ai_diagnosis'],
        'bundle_b64'       => base64_encode($row['bundle_data']),
    ],
]);
