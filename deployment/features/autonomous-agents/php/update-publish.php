<?php
/**
 * d3kOS Update Publisher API
 * v0.9.8 — S32
 *
 * CRM-facing endpoint for managing the version manifest.
 * Auth: Bearer amboat_api_key (same as all CRM proxies).
 *
 * Actions (GET):
 *   ?action=list                 — version history (all records)
 *   ?action=current              — currently active versions (incremental + major)
 *
 * Actions (POST, JSON body):
 *   {action: "publish", update_type, version, url, checksum, released,
 *    t1_upgrade, services_to_restart, release_notes}
 *                                — publish new version, deactivate old of same type
 *   {action: "deactivate", id}   — pull a version (revert to nothing available)
 *   {action: "reactivate", id}   — re-publish a previous version
 *
 * Deploy: wp-content/themes/twentytwenty-child/mobile/update-publish.php
 */

error_reporting(0);
header('Content-Type: application/json');

require_once __DIR__ . '/config.php';

// ── Auth ──────────────────────────────────────────────────────────────────────

$auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!preg_match('/^Bearer\s+(.+)$/i', $auth, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) {
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

// Ensure table exists
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

$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? '';

// ── GET: list ─────────────────────────────────────────────────────────────────

if ($method === 'GET' && $action === 'list') {
    $rows = $db->query(
        "SELECT id, update_type, version, url, checksum, released,
                t1_upgrade, services_to_restart, release_notes, published_at, is_active
         FROM amboat_versions
         ORDER BY published_at DESC
         LIMIT 50"
    )->fetch_all(MYSQLI_ASSOC);

    foreach ($rows as &$r) {
        $r['t1_upgrade'] = (bool)$r['t1_upgrade'];
        $r['is_active']  = (bool)$r['is_active'];
        if (!empty($r['services_to_restart'])) {
            $r['services_to_restart'] = json_decode($r['services_to_restart']) ?? [];
        } else {
            $r['services_to_restart'] = [];
        }
    }

    $db->close();
    echo json_encode(['success' => true, 'versions' => $rows]);
    exit;
}

// ── GET: current ──────────────────────────────────────────────────────────────

if ($method === 'GET' && $action === 'current') {
    $out = ['incremental' => null, 'major' => null];
    foreach (['incremental', 'major'] as $type) {
        $row = $db->query(
            "SELECT * FROM amboat_versions
             WHERE update_type='$type' AND is_active=1
             ORDER BY published_at DESC LIMIT 1"
        )->fetch_assoc();
        if ($row) {
            $row['t1_upgrade'] = (bool)$row['t1_upgrade'];
            $row['is_active']  = (bool)$row['is_active'];
            if (!empty($row['services_to_restart'])) {
                $row['services_to_restart'] = json_decode($row['services_to_restart']) ?? [];
            }
            $out[$type] = $row;
        }
    }
    $db->close();
    echo json_encode(['success' => true] + $out);
    exit;
}

// ── POST ──────────────────────────────────────────────────────────────────────

if ($method === 'POST') {
    $body   = json_decode(file_get_contents('php://input'), true) ?? [];
    $action = $body['action'] ?? '';

    // ── publish ──────────────────────────────────────────────────────────────

    if ($action === 'publish') {
        $update_type = $body['update_type'] ?? '';
        if (!in_array($update_type, ['incremental', 'major'])) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'update_type must be incremental or major']);
            $db->close();
            exit;
        }

        $version    = substr(trim($body['version']      ?? ''), 0, 20);
        $url        = substr(trim($body['url']          ?? ''), 0, 500);
        $checksum   = substr(trim($body['checksum']     ?? ''), 0, 120);
        $released   = trim($body['released'] ?? date('Y-m-d'));
        $t1_upgrade = (int)(bool)($body['t1_upgrade']   ?? false);
        $notes      = substr(trim($body['release_notes'] ?? ''), 0, 2000);

        // Normalise services list → JSON
        $services_raw = $body['services_to_restart'] ?? [];
        if (is_string($services_raw)) {
            // Allow comma-separated input from CRM form
            $services_raw = array_filter(array_map('trim', explode(',', $services_raw)));
        }
        $services_json = json_encode(array_values($services_raw));

        if (!$version) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'version required']);
            $db->close();
            exit;
        }

        // Deactivate existing active versions of same type
        $stmt = $db->prepare('UPDATE amboat_versions SET is_active=0 WHERE update_type=? AND is_active=1');
        $stmt->bind_param('s', $update_type);
        $stmt->execute();
        $stmt->close();

        // Insert new version
        $stmt = $db->prepare(
            'INSERT INTO amboat_versions
             (update_type, version, url, checksum, released, t1_upgrade,
              services_to_restart, release_notes, is_active)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)'
        );
        $stmt->bind_param('sssssiss',
            $update_type, $version, $url, $checksum,
            $released, $t1_upgrade, $services_json, $notes
        );
        $stmt->execute();
        $new_id = $db->insert_id;
        $stmt->close();
        $db->close();

        echo json_encode([
            'success'     => true,
            'id'          => $new_id,
            'update_type' => $update_type,
            'version'     => $version,
            'message'     => "v$version published — all T1+ Pis will receive it within 24h",
        ]);
        exit;
    }

    // ── deactivate ────────────────────────────────────────────────────────────

    if ($action === 'deactivate') {
        $id = (int)($body['id'] ?? 0);
        if (!$id) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'id required']);
            $db->close();
            exit;
        }
        $db->query("UPDATE amboat_versions SET is_active=0 WHERE id=$id");
        $db->close();
        echo json_encode(['success' => true, 'message' => 'Version pulled — no update available until next publish']);
        exit;
    }

    // ── reactivate ────────────────────────────────────────────────────────────

    if ($action === 'reactivate') {
        $id = (int)($body['id'] ?? 0);
        if (!$id) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'id required']);
            $db->close();
            exit;
        }
        // Get type of this version first — deactivate others of same type
        $row = $db->query("SELECT update_type FROM amboat_versions WHERE id=$id")->fetch_assoc();
        if (!$row) {
            http_response_code(404);
            echo json_encode(['success' => false, 'error' => 'Version not found']);
            $db->close();
            exit;
        }
        $type = $row['update_type'];
        $stmt = $db->prepare('UPDATE amboat_versions SET is_active=0 WHERE update_type=? AND is_active=1');
        $stmt->bind_param('s', $type);
        $stmt->execute();
        $stmt->close();
        $db->query("UPDATE amboat_versions SET is_active=1 WHERE id=$id");
        $db->close();
        echo json_encode(['success' => true, 'message' => 'Version reactivated']);
        exit;
    }
}

http_response_code(400);
echo json_encode(['success' => false, 'error' => 'Unknown request']);
$db->close();
