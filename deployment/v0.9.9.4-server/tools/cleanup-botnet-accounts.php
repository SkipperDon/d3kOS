<?php
/**
 * BUG-63 Step 3 — One-shot botnet account cleanup + /register/ republish.
 * Run ONCE. DELETE THIS FILE immediately after.
 *
 * Deletes wp_users rows where:
 *   - atmyboat_email_verified = '0'  (unverified — cannot login)
 *   - role = 'subscriber' only       (no other capabilities)
 *   - user_registered >= 2026-06-01  (attack period)
 *
 * Then sets /register/ page status = 'publish' in wpax_posts.
 *
 * Reads DB credentials from WP_DB_* constants in config.php (set S134).
 * Table prefix: wpax_
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: text/plain; charset=utf-8');

// Safety: require a ?run=1 confirmation to avoid accidental execution
if (($_GET['run'] ?? '') !== '1') {
    echo "DRY RUN — append ?run=1 to execute. Counts only.\n\n";
    $dry_run = true;
} else {
    $dry_run = false;
    echo "LIVE RUN — deletions will execute.\n\n";
}

require_once __DIR__ . '/config.php';

$db_host = defined('WP_DB_HOST') ? WP_DB_HOST : 'localhost';
$db_name = defined('WP_DB_NAME') ? WP_DB_NAME : (defined('DB_NAME') ? DB_NAME : '');
$db_user = defined('WP_DB_USER') ? WP_DB_USER : (defined('DB_USER') ? DB_USER : '');
$db_pass = defined('WP_DB_PASS') ? WP_DB_PASS : (defined('DB_PASS') ? DB_PASS : '');
$prefix  = 'wpax_';

echo "DB: $db_name as $db_user\n";

$db = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($db->connect_error) {
    die("Connect failed: " . $db->connect_error . "\n");
}
echo "Connected OK\n\n";

// ── Step 1: Find candidate bot user IDs ──────────────────────────────────────
// Candidates: unverified + subscriber-only role + registered in attack window
$candidates_sql = "
    SELECT u.ID, u.user_email, u.user_registered, u.user_login
    FROM {$prefix}users u
    INNER JOIN {$prefix}usermeta m1
        ON m1.user_id = u.ID
        AND m1.meta_key = 'atmyboat_email_verified'
        AND m1.meta_value = '0'
    INNER JOIN {$prefix}usermeta m2
        ON m2.user_id = u.ID
        AND m2.meta_key = '{$prefix}capabilities'
        AND m2.meta_value LIKE '%subscriber%'
    LEFT JOIN {$prefix}usermeta m3
        ON m3.user_id = u.ID
        AND m3.meta_key = '{$prefix}capabilities'
        AND m3.meta_value LIKE '%administrator%'
    LEFT JOIN {$prefix}usermeta m4
        ON m4.user_id = u.ID
        AND m4.meta_key = '{$prefix}capabilities'
        AND m4.meta_value LIKE '%editor%'
    WHERE u.user_registered >= '2026-06-01'
      AND m3.user_id IS NULL
      AND m4.user_id IS NULL
";

$result = $db->query($candidates_sql);
if (!$result) {
    die("Query failed: " . $db->error . "\n");
}

$candidates = [];
while ($row = $result->fetch_assoc()) {
    $candidates[] = (int) $row['ID'];
}
$count = count($candidates);

echo "Candidate bot accounts (unverified, subscriber-only, registered >= 2026-06-01): $count\n\n";

// ── Step 2: Delete bot accounts (if any) ────────────────────────────────────
if ($count === 0) {
    echo "Nothing to delete — accounts already cleared.\n\n";
} elseif ($dry_run) {
    $sample_result = $db->query($candidates_sql . " LIMIT 10");
    echo "Sample (up to 10):\n";
    while ($row = $sample_result->fetch_assoc()) {
        echo "  ID={$row['ID']}  login={$row['user_login']}  registered={$row['user_registered']}\n";
    }
    echo "\nRe-run with ?run=1 to delete all $count accounts and republish /register/.\n";
} else {
    $deleted_users = 0;
    $deleted_meta  = 0;
    $batch_size    = 200;

    foreach (array_chunk($candidates, $batch_size) as $batch) {
        $ids = implode(',', $batch);
        $db->query("DELETE FROM {$prefix}usermeta WHERE user_id IN ($ids)");
        $deleted_meta += $db->affected_rows;
        $db->query("DELETE FROM {$prefix}users WHERE ID IN ($ids)");
        $deleted_users += $db->affected_rows;
    }

    echo "Deleted $deleted_users user rows, $deleted_meta usermeta rows.\n\n";
}

// ── Step 3: Republish /register/ (always — independent of delete count) ─────
if (!$dry_run) {
    $reg = $db->query(
        "SELECT ID, post_status FROM {$prefix}posts
         WHERE post_name = 'register' AND post_type = 'page'
         LIMIT 1"
    );
    if (!$reg || $reg->num_rows === 0) {
        echo "WARNING: /register/ page not found by slug 'register'. Republish manually in wp-admin.\n";
    } else {
        $page       = $reg->fetch_assoc();
        $page_id    = (int) $page['ID'];
        $old_status = $page['post_status'];

        if ($old_status === 'publish') {
            echo "/register/ page (ID=$page_id) is already published.\n";
        } else {
            $db->query(
                "UPDATE {$prefix}posts SET post_status = 'publish' WHERE ID = $page_id"
            );
            echo "/register/ page (ID=$page_id) status: '$old_status' → 'publish' (rows affected: {$db->affected_rows})\n";
        }
    }
    echo "\nDone. DELETE THIS FILE NOW.\n";
}

$db->close();
