<?php
/**
 * d3kOS FI2 — Failure Report Receiver
 * v0.9.8
 *
 * Receives failure reports from Pi FI1 failure_reporter.py (background sync).
 * Stores in amboat_failure_reports and clusters into amboat_issues by error_signature.
 *
 * Auth: Bearer amboat_api_key + X-Device-Token
 * Method: POST
 * Body (JSON): {service, error_type, message, error_signature, reported_at}
 *
 * Tables created on first call if not present.
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/failure-report.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';   // defines AMBOAT_API_KEY, DB constants

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$device_token = $_SERVER['HTTP_X_DEVICE_TOKEN'] ?? '';

if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
if (empty($device_token)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing X-Device-Token']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON']);
    exit;
}

$service    = substr(trim($body['service']    ?? 'unknown'), 0, 100);
$error_type = substr(trim($body['error_type'] ?? 'error'),   0, 50);
$message    = substr(trim($body['message']    ?? ''),        0, 500);
$sig        = substr(trim($body['error_signature'] ?? ''),   0, 12);
$reported   = trim($body['reported_at'] ?? date('Y-m-d H:i:s'));

if (!$message || !$sig) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'message and error_signature required']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

// Create tables if not present
$db->query("
    CREATE TABLE IF NOT EXISTS amboat_failure_reports (
        id             INT AUTO_INCREMENT PRIMARY KEY,
        device_token   VARCHAR(36)  NOT NULL,
        service        VARCHAR(100) NOT NULL,
        error_type     VARCHAR(50)  NOT NULL,
        message        TEXT         NOT NULL,
        error_signature VARCHAR(12) NOT NULL,
        reported_at    DATETIME,
        received_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_sig    (error_signature),
        INDEX idx_device (device_token)
    )
");

$db->query("
    CREATE TABLE IF NOT EXISTS amboat_issues (
        id                INT AUTO_INCREMENT PRIMARY KEY,
        error_signature   VARCHAR(12)  NOT NULL UNIQUE,
        service           VARCHAR(100) NOT NULL,
        error_type        VARCHAR(50)  NOT NULL,
        sample_message    TEXT,
        first_seen        DATETIME,
        last_seen         DATETIME,
        affected_count    INT          DEFAULT 1,
        status            ENUM('open','diagnosed','fix_validated','released','closed') DEFAULT 'open',
        fixed_in_version  VARCHAR(20),
        validation_device VARCHAR(36),
        resolved_count    INT          DEFAULT 0,
        updated_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_status (status)
    )
");

$db->query("
    CREATE TABLE IF NOT EXISTS amboat_issue_resolutions (
        id              INT AUTO_INCREMENT PRIMARY KEY,
        issue_id        INT          NOT NULL,
        device_token    VARCHAR(36)  NOT NULL,
        version_applied VARCHAR(20),
        resolved_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_issue_device (issue_id, device_token)
    )
");

// ── Insert failure report ──────────────────────────────────────────────────────

$stmt = $db->prepare(
    'INSERT INTO amboat_failure_reports
     (device_token, service, error_type, message, error_signature, reported_at)
     VALUES (?, ?, ?, ?, ?, ?)'
);
$stmt->bind_param('ssssss', $device_token, $service, $error_type, $message, $sig, $reported);
$stmt->execute();
$stmt->close();

// ── Upsert issue (cluster by error_signature) ──────────────────────────────────
//
// New signature  → INSERT new open issue
// Known signature → UPDATE last_seen + affected_count (if new device reporting it)
//                   Do NOT re-open a closed issue — use a new row if signature recurs
//                   after being closed.

$stmt = $db->prepare('SELECT id, affected_count FROM amboat_issues WHERE error_signature = ?');
$stmt->bind_param('s', $sig);
$stmt->execute();
$issue_row = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$issue_row) {
    // New issue
    $stmt = $db->prepare(
        'INSERT INTO amboat_issues
         (error_signature, service, error_type, sample_message, first_seen, last_seen, affected_count, status)
         VALUES (?, ?, ?, ?, ?, ?, 1, "open")'
    );
    $stmt->bind_param('ssssss', $sig, $service, $error_type, $message, $reported, $reported);
    $stmt->execute();
    $issue_id = $db->insert_id;
    $stmt->close();
} else {
    $issue_id = $issue_row['id'];
    // Check if this device has reported this issue before
    $stmt = $db->prepare(
        'SELECT COUNT(*) AS c FROM amboat_failure_reports
         WHERE error_signature = ? AND device_token = ? AND id < LAST_INSERT_ID()'
    );
    $stmt->bind_param('ss', $sig, $device_token);
    $stmt->execute();
    $already = $stmt->get_result()->fetch_assoc()['c'];
    $stmt->close();

    // Increment affected_count only if first time this device reports this sig
    $inc = ($already == 0) ? ', affected_count = affected_count + 1' : '';

    $db->query(
        "UPDATE amboat_issues
         SET last_seen = NOW() $inc
         WHERE id = " . intval($issue_id)
    );
}

$db->close();

echo json_encode(['success' => true, 'issue_id' => $issue_id]);
