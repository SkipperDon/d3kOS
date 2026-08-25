<?php
// One-shot: publish /register/ page (ID 339). DELETE after.
header('Content-Type: text/plain');
require_once __DIR__ . '/config.php';

$db_host = defined('WP_DB_HOST') ? WP_DB_HOST : 'localhost';
$db_name = defined('WP_DB_NAME') ? WP_DB_NAME : (defined('DB_NAME') ? DB_NAME : '');
$db_user = defined('WP_DB_USER') ? WP_DB_USER : (defined('DB_USER') ? DB_USER : '');
$db_pass = defined('WP_DB_PASS') ? WP_DB_PASS : (defined('DB_PASS') ? DB_PASS : '');

$db = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($db->connect_error) { die("Connect failed: " . $db->connect_error . "\n"); }
echo "Connected: $db_name\n";

// Check current status
$check = $db->query("SELECT ID, post_name, post_status FROM wpax_posts WHERE ID = 339 LIMIT 1");
$row = $check->fetch_assoc();
echo "Before: ID={$row['ID']} slug='{$row['post_name']}' status='{$row['post_status']}'\n";

// Set to publish
$db->query("UPDATE wpax_posts SET post_status = 'publish' WHERE ID = 339");
echo "Rows affected: {$db->affected_rows}\n";

// Verify
$check2 = $db->query("SELECT post_status FROM wpax_posts WHERE ID = 339 LIMIT 1");
$row2 = $check2->fetch_assoc();
echo "After:  status='{$row2['post_status']}'\n";

$db->close();
echo "Done. DELETE THIS FILE NOW.\n";
