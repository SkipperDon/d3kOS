<?php
/**
 * d3kOS Version Manifest Endpoint
 * v0.9.8 — DB-backed (S32)
 *
 * Public endpoint — no auth required. Called by AA2 UpdateAgent every 24h.
 * Returns JSON with current incremental and major version info.
 *
 * Reads from amboat_versions table (managed via CRM /publish-update).
 * Falls back to empty blocks if DB unavailable (Pi stays on current version).
 *
 * Response format:
 * {
 *   "incremental": {
 *     "version":             "0.9.8.1",
 *     "url":                 "https://...",
 *     "checksum":            "sha256:abc123...",
 *     "released":            "2026-04-07",
 *     "services_to_restart": ["d3kos-dashboard"],
 *     "t1_upgrade":          false
 *   },
 *   "major": { ... }
 * }
 *
 * To publish an update: use CRM /publish-update screen.
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/version.php
 */

error_reporting(0);
header('Content-Type: application/json');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Access-Control-Allow-Origin: *');

require_once __DIR__ . '/config.php';

// ── Helpers ───────────────────────────────────────────────────────────────────

function empty_block(): array {
    return [
        'version'             => '',
        'url'                 => '',
        'checksum'            => '',
        'released'            => '',
        'services_to_restart' => [],
        't1_upgrade'          => false,
        'release_notes'       => '',
    ];
}

function row_to_block(array $row): array {
    $services = [];
    if (!empty($row['services_to_restart'])) {
        $decoded  = json_decode($row['services_to_restart'], true);
        $services = is_array($decoded) ? $decoded : [];
    }
    return [
        'version'             => $row['version'],
        'url'                 => $row['url'] ?? '',
        'checksum'            => $row['checksum'] ?? '',
        'released'            => $row['released'] ?? '',
        'services_to_restart' => $services,
        't1_upgrade'          => (bool)($row['t1_upgrade'] ?? false),
        'release_notes'       => $row['release_notes'] ?? '',
    ];
}

// ── Fetch from DB ─────────────────────────────────────────────────────────────

$incremental = empty_block();
$major       = empty_block();

try {
    $db = new mysqli('127.0.0.1', DB_USER, DB_PASS, DB_NAME);

    if (!$db->connect_error) {
        // Create table on first run
        $db->query("
            CREATE TABLE IF NOT EXISTS amboat_versions (
                id                  INT AUTO_INCREMENT PRIMARY KEY,
                update_type         ENUM('incremental','major') NOT NULL,
                version             VARCHAR(20)  NOT NULL,
                url                 VARCHAR(500),
                checksum            VARCHAR(120),
                released            DATE,
                t1_upgrade          TINYINT(1)   DEFAULT 0,
                services_to_restart TEXT,
                release_notes       TEXT,
                published_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
                is_active           TINYINT(1)   DEFAULT 1,
                INDEX idx_type (update_type, is_active)
            )
        ");

        $row = $db->query(
            "SELECT * FROM amboat_versions
             WHERE update_type='incremental' AND is_active=1
             ORDER BY published_at DESC LIMIT 1"
        )->fetch_assoc();
        if ($row) $incremental = row_to_block($row);

        $row = $db->query(
            "SELECT * FROM amboat_versions
             WHERE update_type='major' AND is_active=1
             ORDER BY published_at DESC LIMIT 1"
        )->fetch_assoc();
        if ($row) $major = row_to_block($row);

        $db->close();
    }
} catch (Exception $e) {
    // DB unavailable — return empty (Pi stays on current version, no noise)
}

echo json_encode(['incremental' => $incremental, 'major' => $major], JSON_PRETTY_PRINT);
