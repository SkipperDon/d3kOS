<?php
/**
 * support-migrate.php — One-shot migration
 * Creates amboat_support_tickets table.
 * Protected by FLEET_SETUP_KEY.
 * Delete from HostPapa after running once.
 */
require_once __DIR__ . '/config.php';

$key = $_GET['setup_key'] ?? '';
if (!defined('FLEET_SETUP_KEY') || empty($key) || $key !== FLEET_SETUP_KEY) {
    http_response_code(403);
    echo json_encode(['error' => 'Forbidden']);
    exit;
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'DB connect: ' . $db->connect_error]);
    exit;
}

$results = [];

$sql = "CREATE TABLE IF NOT EXISTS amboat_support_tickets (
    ticket_id    INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    user_id      INT               NOT NULL,
    device_token VARCHAR(64)       DEFAULT NULL,
    subject      VARCHAR(200)      NOT NULL DEFAULT 'Support Request',
    body         TEXT              NOT NULL,
    status       ENUM('open','in_progress','resolved') NOT NULL DEFAULT 'open',
    admin_note   TEXT              DEFAULT NULL,
    created_at   DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY  (ticket_id),
    KEY idx_user_id  (user_id),
    KEY idx_status   (status),
    KEY idx_created  (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

if ($db->query($sql)) {
    $results[] = 'amboat_support_tickets — created (or already existed)';
} else {
    $results[] = 'ERROR: ' . $db->error;
}

$db->close();
header('Content-Type: application/json');
echo json_encode(['success' => true, 'results' => $results]);
