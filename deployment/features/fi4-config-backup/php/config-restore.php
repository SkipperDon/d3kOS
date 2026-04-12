<?php
/**
 * d3kOS Config Restore
 * FI4 — Config Backup & Recovery — Phase 1
 *
 * Called by the d3kOS setup wizard (recovery mode) on a freshly flashed Pi,
 * or by the d3kOS app (Path 3 offline cache fallback lookup).
 *
 * No API key required — the device_token UUID itself is the credential.
 * A fresh Pi has no api_key yet; the token is what it knows.
 *
 * Rate limit: 5 restore requests per token per hour (prevent brute-force).
 * Returns 404 for both "unknown token" and "no backup found" — does not
 * confirm whether a given token exists in the database.
 *
 * Tier gate: T1, T2, T3 only. T0 Pis have no backup — will receive 404.
 *
 * Auth:   none (token in query string is the credential)
 * Method: GET
 * Query:  ?token={device_token}
 *
 * Response (success):
 *   {
 *     "success":      true,
 *     "device_token": "701e5754-...",
 *     "config_json":  "{...all config files...}",
 *     "version":      "0.9.9.3",
 *     "updated_at":   "2026-04-12T09:43:00Z"
 *   }
 *
 * Response (not found / rate limited):
 *   HTTP 404  {success: false, error: "No backup found"}
 *   HTTP 429  {success: false, error: "Too many restore attempts — try again later"}
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/config-restore.php
 */

error_reporting(0);
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'GET required']);
    exit;
}

// ── Token from query string ───────────────────────────────────────────────────

$device_token = trim($_GET['token'] ?? '');

if (empty($device_token) || strlen($device_token) > 64) {
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'No backup found']);
    exit;
}

// ── Database ──────────────────────────────────────────────────────────────────

require_once __DIR__ . '/config.php';

$db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB connect failed']);
    exit;
}
mysqli_report(MYSQLI_REPORT_OFF);

// Fetch the backup row — if table does not exist yet, treat as not found
$stmt = $db->prepare(
    'SELECT config_json, d3kos_version, restore_attempts, last_restore_at,
            DATE_FORMAT(updated_at, \'%Y-%m-%dT%H:%i:%sZ\') AS updated_at
     FROM amboat_config_packages
     WHERE device_token = ?
     LIMIT 1'
);
if (!$stmt) {
    // Table does not exist yet — no backups stored
    $db->close();
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'No backup found']);
    exit;
}

$stmt->bind_param('s', $device_token);
$stmt->execute();
$result = $stmt->get_result();
$row    = $result ? $result->fetch_assoc() : null;
$stmt->close();

if (!$row) {
    $db->close();
    http_response_code(404);
    echo json_encode(['success' => false, 'error' => 'No backup found']);
    exit;
}

// ── Rate limit — 5 restore attempts per token per hour ────────────────────────

$restore_attempts = (int)($row['restore_attempts'] ?? 0);
$last_restore_at  = $row['last_restore_at'];          // NULL or datetime string
$rate_limit       = 5;
$window_seconds   = 3600;

$within_window = false;
if ($last_restore_at) {
    $last_ts       = strtotime($last_restore_at);
    $within_window = (time() - $last_ts) < $window_seconds;
}

if ($within_window && $restore_attempts >= $rate_limit) {
    $db->close();
    http_response_code(429);
    echo json_encode(['success' => false, 'error' => 'Too many restore attempts — try again later']);
    exit;
}

// Reset counter if we are outside the rate-limit window
$new_attempts = $within_window ? $restore_attempts + 1 : 1;

$upd = $db->prepare(
    'UPDATE amboat_config_packages
     SET restore_attempts = ?, last_restore_at = NOW()
     WHERE device_token = ?'
);
$upd->bind_param('is', $new_attempts, $device_token);
$upd->execute();
$upd->close();

$db->close();

// ── Return config package ────────────────────────────────────────────────────

echo json_encode([
    'success'      => true,
    'device_token' => $device_token,
    'config_json'  => $row['config_json'],
    'version'      => $row['d3kos_version'],
    'updated_at'   => $row['updated_at'],
]);
