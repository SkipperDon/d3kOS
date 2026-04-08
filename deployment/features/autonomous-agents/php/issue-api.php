<?php
/**
 * d3kOS FI2 — Issue Lifecycle API
 * v0.9.8
 *
 * CRM-facing API for reading and managing failure intelligence issues.
 * Auth: X-Admin-Key header (same key as admin-api.php).
 *
 * Actions (GET):
 *   ?action=list[&status=open][&page=1]  — list issues, paginated
 *   ?action=get&id=N                     — issue detail + affected devices + resolutions
 *   ?action=stats                        — summary counts by status
 *
 * Actions (POST, JSON body):
 *   {action: "update", id: N, status: "...", fixed_in_version: "...", validation_device: "..."}
 *                                        — update issue lifecycle fields
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/issue-api.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth (admin key) ──────────────────────────────────────────────────────────

$admin_key = $_SERVER['HTTP_X_ADMIN_KEY'] ?? '';
if ($admin_key !== ADMIN_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? (json_decode(file_get_contents('php://input'), true)['action'] ?? '');

// ── GET: list ─────────────────────────────────────────────────────────────────

if ($method === 'GET' && $action === 'list') {
    $status = $_GET['status'] ?? '';
    $page   = max(1, (int)($_GET['page'] ?? 1));
    $limit  = 25;
    $offset = ($page - 1) * $limit;

    $where = $status ? "WHERE status = '" . $db->real_escape_string($status) . "'" : '';

    $total = $db->query("SELECT COUNT(*) AS c FROM amboat_issues $where")->fetch_assoc()['c'];
    $rows  = $db->query(
        "SELECT id, error_signature, service, error_type, sample_message,
                first_seen, last_seen, affected_count, resolved_count,
                status, fixed_in_version, validation_device
         FROM amboat_issues $where
         ORDER BY
           CASE status WHEN 'open' THEN 1 WHEN 'diagnosed' THEN 2
           WHEN 'fix_validated' THEN 3 WHEN 'released' THEN 4
           ELSE 5 END,
           last_seen DESC
         LIMIT $limit OFFSET $offset"
    )->fetch_all(MYSQLI_ASSOC);

    $db->close();
    echo json_encode([
        'success' => true,
        'total'   => (int)$total,
        'page'    => $page,
        'pages'   => max(1, (int)ceil($total / $limit)),
        'issues'  => $rows,
    ]);
    exit;
}

// ── GET: get single issue ─────────────────────────────────────────────────────

if ($method === 'GET' && $action === 'get') {
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'id required']);
        $db->close();
        exit;
    }

    $issue = $db->query(
        "SELECT * FROM amboat_issues WHERE id = $id"
    )->fetch_assoc();

    if (!$issue) {
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'Issue not found']);
        $db->close();
        exit;
    }

    // Affected devices — distinct devices that reported this signature
    $affected = $db->query(
        "SELECT DISTINCT device_token, MIN(reported_at) AS first_report, COUNT(*) AS report_count
         FROM amboat_failure_reports
         WHERE error_signature = '" . $db->real_escape_string($issue['error_signature']) . "'
         GROUP BY device_token
         ORDER BY first_report DESC
         LIMIT 50"
    )->fetch_all(MYSQLI_ASSOC);

    // Resolutions — devices that confirmed the fix
    $resolutions = $db->query(
        "SELECT device_token, version_applied, resolved_at
         FROM amboat_issue_resolutions
         WHERE issue_id = $id
         ORDER BY resolved_at DESC
         LIMIT 50"
    )->fetch_all(MYSQLI_ASSOC);

    // Recent failure reports
    $reports = $db->query(
        "SELECT device_token, service, error_type, message, reported_at
         FROM amboat_failure_reports
         WHERE error_signature = '" . $db->real_escape_string($issue['error_signature']) . "'
         ORDER BY reported_at DESC
         LIMIT 20"
    )->fetch_all(MYSQLI_ASSOC);

    $db->close();
    echo json_encode([
        'success'     => true,
        'issue'       => $issue,
        'affected'    => $affected,
        'resolutions' => $resolutions,
        'reports'     => $reports,
    ]);
    exit;
}

// ── GET: stats ────────────────────────────────────────────────────────────────

if ($method === 'GET' && $action === 'stats') {
    $rows = $db->query(
        "SELECT status, COUNT(*) AS count FROM amboat_issues GROUP BY status"
    )->fetch_all(MYSQLI_ASSOC);

    $stats = ['open' => 0, 'diagnosed' => 0, 'fix_validated' => 0, 'released' => 0, 'closed' => 0];
    foreach ($rows as $r) {
        $stats[$r['status']] = (int)$r['count'];
    }

    $db->close();
    echo json_encode(['success' => true, 'stats' => $stats]);
    exit;
}

// ── POST: update issue lifecycle ──────────────────────────────────────────────

if ($method === 'POST') {
    $body   = json_decode(file_get_contents('php://input'), true) ?? [];
    $action = $body['action'] ?? '';

    if ($action !== 'update') {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Unknown action']);
        $db->close();
        exit;
    }

    $id = (int)($body['id'] ?? 0);
    if (!$id) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'id required']);
        $db->close();
        exit;
    }

    $allowed_statuses = ['open', 'diagnosed', 'fix_validated', 'released', 'closed'];
    $updates = [];
    $params  = [];
    $types   = '';

    if (isset($body['status']) && in_array($body['status'], $allowed_statuses)) {
        $updates[] = 'status = ?';
        $params[]  = $body['status'];
        $types    .= 's';
    }
    if (isset($body['fixed_in_version'])) {
        $updates[] = 'fixed_in_version = ?';
        $params[]  = substr($body['fixed_in_version'], 0, 20);
        $types    .= 's';
    }
    if (isset($body['validation_device'])) {
        $updates[] = 'validation_device = ?';
        $params[]  = substr($body['validation_device'], 0, 36);
        $types    .= 's';
    }

    if (!$updates) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'No fields to update']);
        $db->close();
        exit;
    }

    $params[] = $id;
    $types   .= 'i';
    $sql      = 'UPDATE amboat_issues SET ' . implode(', ', $updates) . ' WHERE id = ?';
    $stmt     = $db->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $affected = $db->affected_rows;
    $stmt->close();
    $db->close();

    echo json_encode(['success' => true, 'updated' => $affected > 0]);
    exit;
}

http_response_code(400);
echo json_encode(['success' => false, 'error' => 'Unknown request']);
$db->close();
