<?php
/**
 * diagnostic-migrate.php — v0.9.7 Remote Diagnostic Console DB Schema
 * Creates: amboat_diagnostic_consents, amboat_diagnostic_bundles,
 *          amboat_diagnostics_resolved, amboat_diagnostics_rules
 *
 * Auth:   FLEET_SETUP_KEY (query string ?key=)
 * Method: GET
 * Usage:  Run once in browser — DELETE this file immediately after.
 */

require_once __DIR__ . '/config.php';

$setup_key = defined('FLEET_SETUP_KEY') ? FLEET_SETUP_KEY : '';
if (!$setup_key || ($_GET['key'] ?? '') !== $setup_key) {
    http_response_code(403);
    echo 'Forbidden — valid ?key= required';
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    die('DB connect error: ' . $db->connect_error);
}

$results = [];

// ── Table 1: amboat_diagnostic_consents ─────────────────────────────────────
$sql = "CREATE TABLE IF NOT EXISTS amboat_diagnostic_consents (
    consent_id   INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ticket_id    INT UNSIGNED NOT NULL,
    user_id      INT UNSIGNED NOT NULL,
    device_token VARCHAR(64)  NOT NULL,
    granted_at   DATETIME     NOT NULL,
    expires_at   DATETIME     NOT NULL,
    revoked_at   DATETIME     NULL DEFAULT NULL,
    status       ENUM('active','expired','revoked') NOT NULL DEFAULT 'active',
    INDEX idx_ticket  (ticket_id),
    INDEX idx_user    (user_id),
    INDEX idx_device  (device_token),
    INDEX idx_status  (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";
$results[] = ['table' => 'amboat_diagnostic_consents', 'ok' => $db->query($sql), 'err' => $db->error];

// ── Table 2: amboat_diagnostic_bundles ──────────────────────────────────────
$sql = "CREATE TABLE IF NOT EXISTS amboat_diagnostic_bundles (
    bundle_id        INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ticket_id        INT UNSIGNED NOT NULL,
    device_token     VARCHAR(64)  NOT NULL,
    bundle_data      LONGBLOB     NOT NULL,
    bundle_size_bytes INT UNSIGNED NOT NULL DEFAULT 0,
    ai_diagnosis     TEXT         NULL DEFAULT NULL,
    created_at       DATETIME     NOT NULL,
    INDEX idx_ticket  (ticket_id),
    INDEX idx_device  (device_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";
$results[] = ['table' => 'amboat_diagnostic_bundles', 'ok' => $db->query($sql), 'err' => $db->error];

// ── Table 3: amboat_diagnostics_resolved ────────────────────────────────────
$sql = "CREATE TABLE IF NOT EXISTS amboat_diagnostics_resolved (
    case_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ticket_id               INT UNSIGNED NOT NULL,
    installation_id_hash    VARCHAR(64)  NOT NULL,
    problem_category        VARCHAR(120) NOT NULL DEFAULT '',
    symptoms_hash           VARCHAR(64)  NOT NULL DEFAULT '',
    root_cause              TEXT         NOT NULL,
    fix_applied             TEXT         NOT NULL,
    outcome                 ENUM('resolved','unresolved','partial') NOT NULL DEFAULT 'resolved',
    time_to_resolution_min  INT UNSIGNED NULL DEFAULT NULL,
    created_at              DATETIME     NOT NULL,
    INDEX idx_ticket         (ticket_id),
    INDEX idx_symptoms_hash  (symptoms_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";
$results[] = ['table' => 'amboat_diagnostics_resolved', 'ok' => $db->query($sql), 'err' => $db->error];

// ── Table 4: amboat_diagnostics_rules ───────────────────────────────────────
$sql = "CREATE TABLE IF NOT EXISTS amboat_diagnostics_rules (
    rule_id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    symptoms_hash    VARCHAR(64)  NOT NULL UNIQUE,
    recommended_fix  TEXT         NOT NULL,
    match_count      INT UNSIGNED NOT NULL DEFAULT 1,
    last_matched_at  DATETIME     NOT NULL,
    created_at       DATETIME     NOT NULL,
    INDEX idx_symptoms_hash (symptoms_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";
$results[] = ['table' => 'amboat_diagnostics_rules', 'ok' => $db->query($sql), 'err' => $db->error];

$db->close();

header('Content-Type: text/plain');
echo "diagnostic-migrate.php — v0.9.7\n\n";
$all_ok = true;
foreach ($results as $r) {
    $status = $r['ok'] ? 'OK' : 'FAILED: ' . $r['err'];
    if (!$r['ok']) $all_ok = false;
    echo sprintf("  %-40s %s\n", $r['table'], $status);
}
echo "\n" . ($all_ok ? "All tables ready. DELETE THIS FILE." : "One or more tables failed — check above.") . "\n";
