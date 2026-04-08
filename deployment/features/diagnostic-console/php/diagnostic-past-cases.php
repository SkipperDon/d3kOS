<?php
/**
 * diagnostic-past-cases.php — v0.9.7 Remote Diagnostic Console
 * Returns similar resolved cases (knowledge base) for a ticket.
 * Matches on symptoms_hash derived from the ticket's stored AI diagnosis.
 *
 * Method: GET ?ticket_id=N
 * Auth:   Bearer ADMIN_API_KEY
 */

require_once __DIR__ . '/config.php';


header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'GET required']);
    exit;
}

$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if ($auth_header !== 'Bearer ' . ADMIN_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

$ticket_id = (int)($_GET['ticket_id'] ?? 0);
if ($ticket_id < 1) {
    echo json_encode(['success' => true, 'cases' => [], 'rule' => null]);
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

// ── Get AI diagnosis for this ticket ─────────────────────────────────────────
$stmt = $db->prepare(
    "SELECT ai_diagnosis FROM amboat_diagnostic_bundles WHERE ticket_id=? ORDER BY bundle_id DESC LIMIT 1"
);
$stmt->bind_param('i', $ticket_id);
$stmt->execute();
$bundle_row = $stmt->get_result()->fetch_assoc();
$stmt->close();

$cases = [];
$rule  = null;

if ($bundle_row && $bundle_row['ai_diagnosis']) {
    $diagnosis = json_decode($bundle_row['ai_diagnosis'], true);
    $root_cause = $diagnosis['root_cause'] ?? '';
    $problem_category = '';

    if ($root_cause) {
        // Build symptoms_hash the same way diagnostic-resolve.php does
        $combined_text = strtolower($problem_category . ' ' . $root_cause);
        $words         = array_unique(preg_split('/\W+/', $combined_text, -1, PREG_SPLIT_NO_EMPTY));
        sort($words);
        $symptoms_hash = substr(md5(implode(' ', $words)), 0, 16);

        // Look for matching resolved cases (exclude current ticket)
        $stmt = $db->prepare(
            "SELECT case_id, ticket_id, problem_category, root_cause, fix_applied,
                    outcome, time_to_resolution_min, created_at
             FROM amboat_diagnostics_resolved
             WHERE symptoms_hash = ? AND ticket_id != ?
             ORDER BY created_at DESC LIMIT 5"
        );
        $stmt->bind_param('si', $symptoms_hash, $ticket_id);
        $stmt->execute();
        $res = $stmt->get_result();
        while ($row = $res->fetch_assoc()) {
            $cases[] = $row;
        }
        $stmt->close();

        // Check for a matching auto-rule
        $stmt = $db->prepare(
            "SELECT rule_id, recommended_fix, match_count, last_matched_at
             FROM amboat_diagnostics_rules WHERE symptoms_hash = ? LIMIT 1"
        );
        $stmt->bind_param('s', $symptoms_hash);
        $stmt->execute();
        $rule = $stmt->get_result()->fetch_assoc() ?: null;
        $stmt->close();
    }
}

$db->close();

echo json_encode(['success' => true, 'cases' => $cases, 'rule' => $rule]);
