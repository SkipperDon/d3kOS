<?php
/**
 * diagnostic-upload.php — v0.9.7 Remote Diagnostic Console
 * Pi POSTs multipart diagnostic bundle here after collection.
 * Validates active consent exists before storing.
 *
 * Method: POST (multipart/form-data)
 * Auth:   Bearer AMBOAT_API_KEY  +  X-Device-Token header  (Pi auth)
 * Fields: ticket_id (int), bundle (file upload)
 * Response: { "success": true, "data": { "bundle_id": N, "size_bytes": N } }
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

// ── Pi auth (AMBOAT_API_KEY + device_token) ───────────────────────────────────
$auth         = amboat_auth_pi_request();
$device_token = $auth['device_token'];

// ── Parse multipart fields ────────────────────────────────────────────────────
$ticket_id = (int)($_POST['ticket_id'] ?? 0);
if ($ticket_id < 1) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id required']);
    exit;
}

if (empty($_FILES['bundle']) || $_FILES['bundle']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'bundle file required']);
    exit;
}

$bundle_size = (int)$_FILES['bundle']['size'];
if ($bundle_size > 52428800) { // 50 MB hard limit
    http_response_code(413);
    echo json_encode(['success' => false, 'error' => 'Bundle exceeds 50 MB limit']);
    exit;
}

$bundle_tmp = $_FILES['bundle']['tmp_name'];

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

// ── Expire stale consents then verify active consent exists ──────────────────
$dt_safe = $db->real_escape_string($device_token);
$db->query(
    "UPDATE amboat_diagnostic_consents SET status='expired'
     WHERE ticket_id={$ticket_id} AND device_token='{$dt_safe}'
     AND status='active' AND expires_at < NOW()"
);

$stmt = $db->prepare(
    "SELECT consent_id FROM amboat_diagnostic_consents
     WHERE ticket_id=? AND device_token=? AND status='active' LIMIT 1"
);
$stmt->bind_param('is', $ticket_id, $device_token);
$stmt->execute();
$consent = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$consent) {
    $db->close();
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'No active consent for this ticket']);
    exit;
}

// ── Store bundle as LONGBLOB via send_long_data ───────────────────────────────
$now  = date('Y-m-d H:i:s');
$null = null;

$stmt = $db->prepare(
    "INSERT INTO amboat_diagnostic_bundles
        (ticket_id, device_token, bundle_data, bundle_size_bytes, created_at)
     VALUES (?, ?, ?, ?, ?)"
);
// 'b' = blob (passed via send_long_data), 'd' = double/int for size
$stmt->bind_param('isbds', $ticket_id, $device_token, $null, $bundle_size, $now);

// Stream bundle file in 1 MB chunks to avoid memory spike
$fh = fopen($bundle_tmp, 'rb');
while (!feof($fh)) {
    $stmt->send_long_data(2, fread($fh, 1048576));
}
fclose($fh);

$stmt->execute();
$bundle_id = (int)$db->insert_id;
$stmt->close();
$db->close();

if (!$bundle_id) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to store bundle']);
    exit;
}

echo json_encode([
    'success' => true,
    'data'    => [
        'bundle_id'  => $bundle_id,
        'size_bytes' => $bundle_size,
    ],
]);
