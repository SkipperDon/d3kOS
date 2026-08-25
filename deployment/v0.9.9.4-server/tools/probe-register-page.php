<?php
header('Content-Type: text/plain');
require_once __DIR__ . '/config.php';

$db_host = defined('WP_DB_HOST') ? WP_DB_HOST : 'localhost';
$db_name = defined('WP_DB_NAME') ? WP_DB_NAME : (defined('DB_NAME') ? DB_NAME : '');
$db_user = defined('WP_DB_USER') ? WP_DB_USER : (defined('DB_USER') ? DB_USER : '');
$db_pass = defined('WP_DB_PASS') ? WP_DB_PASS : (defined('DB_PASS') ? DB_PASS : '');
$prefix  = 'wpax_';

$db = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($db->connect_error) { die("Connect failed: " . $db->connect_error . "\n"); }
echo "Connected: $db_name\n\n";

// List all pages with 'register' in their name or slug
$r = $db->query(
    "SELECT ID, post_title, post_name, post_status, post_type
     FROM {$prefix}posts
     WHERE (post_name LIKE '%register%' OR post_title LIKE '%register%')
       AND post_type IN ('page','post')
     ORDER BY ID"
);
if (!$r) { die("Query error: " . $db->error . "\n"); }
echo "Pages/posts matching 'register':\n";
while ($row = $r->fetch_assoc()) {
    echo "  ID={$row['ID']}  slug='{$row['post_name']}'  status='{$row['post_status']}'  type='{$row['post_type']}'  title='{$row['post_title']}'\n";
}

echo "\nDELETE THIS FILE\n";
$db->close();
