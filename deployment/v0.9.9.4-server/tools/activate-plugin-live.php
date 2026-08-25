<?php
/**
 * One-shot: activate d3kOS device auth plugin on LIVE atmyboat.com
 * Run once then DELETE THIS FILE immediately.
 * Creates 6 device auth tables + activates plugin in wp_options.
 */
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: text/plain');

require_once __DIR__ . '/config.php';

$db_host = defined('WP_DB_HOST') ? WP_DB_HOST : 'localhost';
$db_name = defined('WP_DB_NAME') ? WP_DB_NAME : '';
$db_user = defined('WP_DB_USER') ? WP_DB_USER : '';
$db_pass = defined('WP_DB_PASS') ? WP_DB_PASS : '';

echo "DB: $db_name as $db_user\n";

$mysqli = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($mysqli->connect_error) {
    die("Connect failed: " . $mysqli->connect_error . "\n");
}
echo "Connected OK\n\n";

// --- Create device auth tables ---
$tables = [
    "amboat_device_enrolments" =>
        "CREATE TABLE IF NOT EXISTS amboat_device_enrolments (
            device_token  VARCHAR(36)   NOT NULL,
            public_key    VARBINARY(32) NOT NULL,
            status        ENUM('pending','approved','rejected','blocked') NOT NULL DEFAULT 'pending',
            contact_email VARCHAR(254)  NULL,
            enrol_note    TEXT          NULL,
            enrolled_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            enrolled_ip   VARBINARY(16) NULL,
            reviewed_at   TIMESTAMP     NULL,
            reviewed_by   BIGINT        NULL,
            PRIMARY KEY (device_token)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    "amboat_registration_codes" =>
        "CREATE TABLE IF NOT EXISTS amboat_registration_codes (
            code_hash       CHAR(64)    NOT NULL,
            device_token    VARCHAR(36) NOT NULL,
            issued_at       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at      TIMESTAMP   NOT NULL,
            status          ENUM('valid','used','superseded') NOT NULL DEFAULT 'valid',
            used_at         TIMESTAMP   NULL,
            used_by_user_id BIGINT      NULL,
            PRIMARY KEY (code_hash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    "amboat_device_accounts" =>
        "CREATE TABLE IF NOT EXISTS amboat_device_accounts (
            device_token VARCHAR(36) NOT NULL,
            user_id      BIGINT      NOT NULL,
            created_at   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (device_token),
            UNIQUE KEY uq_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    "amboat_registration_audit" =>
        "CREATE TABLE IF NOT EXISTS amboat_registration_audit (
            id           BIGINT AUTO_INCREMENT NOT NULL,
            event        ENUM('enrol','approve','reject','block','code_issued',
                             'redeem_ok','redeem_fail','rate_limited','legacy_key_used') NOT NULL,
            device_token VARCHAR(36)   NULL,
            user_id      BIGINT        NULL,
            ip           VARBINARY(16) NULL,
            detail       VARCHAR(255)  NULL,
            created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    "amboat_devices" =>
        "CREATE TABLE IF NOT EXISTS amboat_devices (
            device_token        VARCHAR(36) NOT NULL,
            current_version     VARCHAR(20) NULL,
            version_updated_at  DATETIME    NULL,
            version_check_count INT         NOT NULL DEFAULT 0,
            PRIMARY KEY (device_token)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    "d3kos_nonce_cache" =>
        "CREATE TABLE IF NOT EXISTS d3kos_nonce_cache (
            nonce_key CHAR(32) NOT NULL,
            used_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (nonce_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
];

foreach ($tables as $name => $sql) {
    echo ($mysqli->query($sql) ? "OK" : "FAIL: " . $mysqli->error) . ": $name\n";
}

// --- Activate plugin in WordPress ---
// Live table prefix is wp_ (standard production)
$plugin_path = 'd3kos-device-auth/d3kos-device-auth.php';
$row = $mysqli->query("SELECT option_value FROM wp_options WHERE option_name = 'active_plugins' LIMIT 1");
if (!$row) { die("Cannot read wp_options: " . $mysqli->error . "\n"); }
$r = $row->fetch_assoc();
$active = maybe_unserialize_simple($r['option_value']);

if (in_array($plugin_path, $active)) {
    echo "\nPlugin already active.\n";
} else {
    $active[] = $plugin_path;
    sort($active);
    $serialized = serialize($active);
    $safe = $mysqli->real_escape_string($serialized);
    $mysqli->query("UPDATE wp_options SET option_value = '$safe' WHERE option_name = 'active_plugins'");
    echo "\nPlugin ACTIVATED (rows affected: " . $mysqli->affected_rows . ")\n";
}

$mysqli->close();
echo "\nDELETE THIS FILE NOW.\n";

function maybe_unserialize_simple($data) {
    if (@unserialize($data) !== false || $data === 'b:0;') return unserialize($data);
    return [];
}
