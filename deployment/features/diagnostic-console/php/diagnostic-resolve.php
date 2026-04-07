<?php
/**
 * diagnostic-resolve.php — v0.9.7 Remote Diagnostic Console
 * Logs a resolved diagnostic case and runs pattern detection.
 * Auto-creates a rule in amboat_diagnostics_rules when 3+ cases share the same symptoms.
 *
 * Method: POST
 * Auth:   Bearer ADMIN_API_KEY
 * Body: {
 *   "ticket_id": N,
 *   "problem_category": "signalk_404",
 *   "root_cause": "SignalK not running after reboot",
 *   "fix_applied": "sudo systemctl restart signalk",
 *   "outcome": "resolved",
 *   "time_to_resolution_min": 15
 * }
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

$body                  = json_decode(file_get_contents('php://input'), true);
$ticket_id             = (int)($body['ticket_id'] ?? 0);
$problem_category      = trim($body['problem_category'] ?? '');
$root_cause            = trim($body['root_cause'] ?? '');
$fix_applied           = trim($body['fix_applied'] ?? '');
$outcome               = $body['outcome'] ?? 'resolved';
$time_to_resolution    = isset($body['time_to_resolution_min']) ? (int)$body['time_to_resolution_min'] : null;

$valid_outcomes = ['resolved', 'unresolved', 'partial'];
if (!in_array($outcome, $valid_outcomes, true)) {
    $outcome = 'resolved';
}

if ($ticket_id < 1 || !$root_cause || !$fix_applied) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'ticket_id, root_cause, and fix_applied required']);
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

// ── Get installation_id_hash from device_token on ticket ─────────────────────
$stmt = $db->prepare(
    "SELECT COALESCE(t.device_token, p.pi_id) AS device_token
     FROM amboat_support_tickets t
     LEFT JOIN d3kos_pairings p ON p.user_id = t.user_id
     WHERE t.ticket_id = ? LIMIT 1"
);
$stmt->bind_param('i', $ticket_id);
$stmt->execute();
$ticket_row = $stmt->get_result()->fetch_assoc();
$stmt->close();

$device_token         = $ticket_row['device_token'] ?? 'unknown';
$installation_id_hash = substr(md5($device_token), 0, 16);

// ── Build symptoms_hash from problem_category + root_cause keywords ───────────
// Normalise: lowercase, strip non-alpha, sort words, hash
$combined_text  = strtolower($problem_category . ' ' . $root_cause);
$words          = array_unique(preg_split('/\W+/', $combined_text, -1, PREG_SPLIT_NO_EMPTY));
sort($words);
$symptoms_hash  = substr(md5(implode(' ', $words)), 0, 16);

// ── Insert resolved case ──────────────────────────────────────────────────────
$stmt = $db->prepare(
    "INSERT INTO amboat_diagnostics_resolved
        (ticket_id, installation_id_hash, problem_category, symptoms_hash,
         root_cause, fix_applied, outcome, time_to_resolution_min, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())"
);
$stmt->bind_param(
    'issssssd',
    $ticket_id, $installation_id_hash, $problem_category, $symptoms_hash,
    $root_cause, $fix_applied, $outcome, $time_to_resolution
);
$stmt->execute();
$case_id = (int)$db->insert_id;
$stmt->close();

// ── Pattern detection: count matching symptoms across resolved cases ──────────
$stmt = $db->prepare(
    "SELECT COUNT(*) AS cnt FROM amboat_diagnostics_resolved
     WHERE symptoms_hash = ? AND outcome = 'resolved'"
);
$stmt->bind_param('s', $symptoms_hash);
$stmt->execute();
$count_row = $stmt->get_result()->fetch_assoc();
$stmt->close();
$match_count = (int)($count_row['cnt'] ?? 0);

$rule_created = false;
$rule_id      = null;

if ($match_count >= 3) {
    // Upsert rule (INSERT ... ON DUPLICATE KEY UPDATE match_count)
    $stmt = $db->prepare(
        "INSERT INTO amboat_diagnostics_rules
            (symptoms_hash, recommended_fix, match_count, last_matched_at, created_at)
         VALUES (?, ?, ?, NOW(), NOW())
         ON DUPLICATE KEY UPDATE
            match_count = match_count + 1,
            recommended_fix = IF(match_count < VALUES(match_count), VALUES(recommended_fix), recommended_fix),
            last_matched_at = NOW()"
    );
    $stmt->bind_param('ssi', $symptoms_hash, $fix_applied, $match_count);
    $stmt->execute();
    $rule_id      = (int)$db->insert_id ?: null;
    $rule_created = true;
    $stmt->close();
}

// ── Also mark the support ticket as resolved ──────────────────────────────────
$db->query("UPDATE amboat_support_tickets SET status='resolved', updated_at=NOW() WHERE ticket_id={$ticket_id}");

$db->close();

echo json_encode([
    'success'      => true,
    'data'         => [
        'case_id'      => $case_id,
        'symptoms_hash'=> $symptoms_hash,
        'match_count'  => $match_count,
        'rule_created' => $rule_created,
        'rule_id'      => $rule_id,
    ],
]);
