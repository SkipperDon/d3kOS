<?php
/**
 * d3kOS FI2 — Fix Confirmation Receiver
 * v0.9.8
 *
 * Called by AA2 update_agent._confirm_fix() after a successful update apply.
 * Finds all released issues that are fixed in the applied version and records
 * that this device now has the fix. Auto-closes issues when ≥ 90% of affected
 * devices have confirmed the fix and no new reports appear for 48h.
 *
 * Auth: Bearer amboat_api_key + X-Device-Token
 * Method: POST
 * Body (JSON): {device_token, version}
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/fix-confirmed.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth_header  = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$device_token = $_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '';

if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────

$body    = json_decode(file_get_contents('php://input'), true);
$version = substr(trim($body['version'] ?? ''), 0, 20);
$device  = substr(trim($body['device_token'] ?? $device_token), 0, 36);

if (!$version || !$device) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'version and device_token required']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

// Find issues that are released and fixed in this version (or earlier)
$stmt = $db->prepare(
    "SELECT id, affected_count, resolved_count, fixed_in_version
     FROM amboat_issues
     WHERE status IN ('released', 'fix_validated')
       AND fixed_in_version IS NOT NULL
       AND fixed_in_version <= ?"
);
$stmt->bind_param('s', $version);
$stmt->execute();
$issues = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
$stmt->close();

$resolved = [];

foreach ($issues as $issue) {
    $issue_id      = $issue['id'];
    $affected      = max(1, (int)$issue['affected_count']);

    // Record resolution for this device (ignore duplicate)
    $stmt = $db->prepare(
        'INSERT IGNORE INTO amboat_issue_resolutions
         (issue_id, device_token, version_applied)
         VALUES (?, ?, ?)'
    );
    $stmt->bind_param('iss', $issue_id, $device, $version);
    $stmt->execute();
    $new = $db->affected_rows;
    $stmt->close();

    if ($new > 0) {
        // Update resolved_count
        $db->query(
            "UPDATE amboat_issues
             SET resolved_count = resolved_count + 1
             WHERE id = $issue_id"
        );

        // Re-fetch updated counts
        $row = $db->query(
            "SELECT resolved_count FROM amboat_issues WHERE id = $issue_id"
        )->fetch_assoc();
        $resolved_count = (int)$row['resolved_count'];

        // Auto-close if ≥ 90% resolved
        if ($resolved_count >= ceil($affected * 0.9)) {
            // Also check no new reports in last 48h
            $recent = $db->query(
                "SELECT COUNT(*) AS c FROM amboat_failure_reports r
                 JOIN amboat_issues i ON r.error_signature = i.error_signature
                 WHERE i.id = $issue_id
                   AND r.received_at > DATE_SUB(NOW(), INTERVAL 48 HOUR)"
            )->fetch_assoc()['c'];

            if ($recent == 0) {
                $db->query(
                    "UPDATE amboat_issues SET status = 'closed' WHERE id = $issue_id"
                );
            }
        }

        $resolved[] = $issue_id;
    }
}

$db->close();

echo json_encode([
    'success'          => true,
    'version'          => $version,
    'issues_updated'   => $resolved,
]);
