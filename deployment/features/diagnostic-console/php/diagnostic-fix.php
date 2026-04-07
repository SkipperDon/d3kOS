<?php
/**
 * diagnostic-fix.php — v0.9.7 Remote Diagnostic Console
 * Admin enqueues a whitelisted fix command to the Pi command queue.
 *
 * Method: POST
 * Auth:   Bearer ADMIN_API_KEY
 * Body:   { "ticket_id": N, "fix_type": "restart_service", "fix_target": "signalk" }
 * Response: { "success": true, "data": { "command_id": N, "fix_type": "...", "fix_target": "..." } }
 *
 * Fix whitelist:
 *   restart_service  : d3kos-voice, d3kos-ai-bridge, d3kos-fleet-push, signalk, nodered,
 *                      d3kos-cloud-link, d3kos-predictive, d3kos-gemini-proxy, d3kos-cloud-agent
 *   clear_cache      : signalk_cache, ai_cache, temp_files
 *   rotate_logs      : d3kos, nginx
 *   update_config    : gps_timeout, ai_model_id, log_retention_days
 *   restart_pi       : (requires active diagnostic consent for this ticket)
 *   recalibrate_sensor: gps, temperature, pressure, fuel
 *   restart_signalk  : (no target required)
 */

require_once __DIR__ . '/config.php';

if (!defined('ADMIN_API_KEY')) {
    define('ADMIN_API_KEY', 'amboat_admin_74899205409692603cb9c951c3c895ce27d92599');
}

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if ($auth_header !== 'Bearer ' . ADMIN_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

$body       = json_decode(file_get_contents('php://input'), true);
$ticket_id  = (int)($body['ticket_id'] ?? 0);
$fix_type   = trim($body['fix_type'] ?? '');
$fix_target = trim($body['fix_target'] ?? '');
$fix_value  = $body['fix_value'] ?? null;  // for update_config

if ($ticket_id < 1 || !$fix_type) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id and fix_type required']);
    exit;
}

// ── Whitelist enforcement ─────────────────────────────────────────────────────
$WHITELIST = [
    'restart_service'   => ['d3kos-voice','d3kos-ai-bridge','d3kos-fleet-push','signalk',
                             'nodered','d3kos-cloud-link','d3kos-predictive','d3kos-gemini-proxy',
                             'd3kos-cloud-agent'],
    'clear_cache'       => ['signalk_cache','ai_cache','temp_files'],
    'rotate_logs'       => ['d3kos','nginx'],
    'update_config'     => ['gps_timeout','ai_model_id','log_retention_days'],
    'recalibrate_sensor'=> ['gps','temperature','pressure','fuel'],
    'restart_signalk'   => [],    // no target
    'restart_pi'        => [],    // requires active consent check below
];

if (!array_key_exists($fix_type, $WHITELIST)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => "Fix type '{$fix_type}' is not whitelisted"]);
    exit;
}

$allowed_targets = $WHITELIST[$fix_type];
if (!empty($allowed_targets) && !in_array($fix_target, $allowed_targets, true)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => "Target '{$fix_target}' not allowed for {$fix_type}"]);
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

// ── restart_pi requires active diagnostic consent ─────────────────────────────
if ($fix_type === 'restart_pi') {
    $stmt = $db->prepare(
        "SELECT consent_id FROM amboat_diagnostic_consents
         WHERE ticket_id=? AND status='active' AND expires_at > NOW() LIMIT 1"
    );
    $stmt->bind_param('i', $ticket_id);
    $stmt->execute();
    $consent = $stmt->get_result()->fetch_assoc();
    $stmt->close();
    if (!$consent) {
        $db->close();
        http_response_code(403);
        echo json_encode(['success' => false,
            'error' => 'restart_pi requires active user diagnostic consent (not expired/revoked)']);
        exit;
    }
}

// ── Look up user_id from ticket ───────────────────────────────────────────────
$stmt = $db->prepare("SELECT user_id FROM amboat_support_tickets WHERE ticket_id=? LIMIT 1");
$stmt->bind_param('i', $ticket_id);
$stmt->execute();
$ticket = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$ticket) {
    $db->close();
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'Ticket not found']);
    exit;
}
$user_id = (int)$ticket['user_id'];

// ── Enqueue diagnostic_fix command ───────────────────────────────────────────
$payload = json_encode(array_filter([
    'ticket_id'  => $ticket_id,
    'fix_type'   => $fix_type,
    'fix_target' => $fix_target ?: null,
    'fix_value'  => $fix_value,
]));

$cmd    = 'diagnostic_fix';
$status = 'pending';
$stmt   = $db->prepare(
    "INSERT INTO amboat_command_queue (user_id, command, payload, status, created_at)
     VALUES (?, ?, ?, ?, NOW())"
);
$stmt->bind_param('isss', $user_id, $cmd, $payload, $status);
$stmt->execute();
$command_id = (int)$db->insert_id;
$stmt->close();
$db->close();

echo json_encode([
    'success' => true,
    'data'    => [
        'command_id' => $command_id,
        'fix_type'   => $fix_type,
        'fix_target' => $fix_target ?: null,
    ],
]);
