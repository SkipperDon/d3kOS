<?php
/**
 * Plugin Name: d3kOS Device Authentication
 * Plugin URI:  https://atmyboat.com
 * Description: Ed25519 per-device authentication and forum registration for d3kOS devices.
 *              Implements BUG-66 Phase A: enrolment queue, approval workflow, registration codes.
 * Version:     1.0.0
 * Author:      AtMyBoat.com
 * License:     Private — not for redistribution
 *
 * Deployment: wp-content/plugins/d3kos-device-auth/d3kos-device-auth.php
 * Activate via wp-admin → Plugins.
 */

if (!defined('ABSPATH')) {
    exit;
}

// Require handler files from the mobile/ directory (child theme path).
// Phase C will add a require_once to this same device-auth.php from the 12 existing endpoints.
define('D3KOS_MOBILE_DIR', get_stylesheet_directory() . '/mobile');

require_once D3KOS_MOBILE_DIR . '/device-auth.php';
require_once D3KOS_MOBILE_DIR . '/enrol.php';
require_once D3KOS_MOBILE_DIR . '/status.php';
require_once D3KOS_MOBILE_DIR . '/request-code.php';

// ---------------------------------------------------------------------------
// REST API registration
// ---------------------------------------------------------------------------

add_action('rest_api_init', function () {
    register_rest_route('amboat-device/v1', '/enrol', [
        'methods'             => 'POST',
        'callback'            => 'd3kos_handle_enrol',
        'permission_callback' => '__return_true', // auth inside handler
        'args'                => [
            'device_token' => ['required' => true, 'type' => 'string'],
            'public_key'   => ['required' => true, 'type' => 'string'],
            'contact_email'=> ['required' => false, 'type' => 'string'],
            'note'         => ['required' => false, 'type' => 'string'],
        ],
    ]);

    register_rest_route('amboat-device/v1', '/status', [
        'methods'             => 'GET',
        'callback'            => 'd3kos_handle_status',
        'permission_callback' => '__return_true',
    ]);

    register_rest_route('amboat-device/v1', '/request-code', [
        'methods'             => 'POST',
        'callback'            => 'd3kos_handle_request_code',
        'permission_callback' => '__return_true',
    ]);
});

// ---------------------------------------------------------------------------
// Table creation on plugin activation (dbDelta — idempotent, WordPress-safe)
// ---------------------------------------------------------------------------

register_activation_hook(__FILE__, 'd3kos_create_device_tables');

function d3kos_create_device_tables(): void {
    global $wpdb;
    require_once ABSPATH . 'wp-admin/includes/upgrade.php';

    $charset = $wpdb->get_charset_collate();

    $sqls = [
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
            PRIMARY KEY (device_token),
            INDEX idx_status (status),
            INDEX idx_email (contact_email)
        ) $charset",

        "CREATE TABLE IF NOT EXISTS amboat_registration_codes (
            code_hash       CHAR(64)    NOT NULL,
            device_token    VARCHAR(36) NOT NULL,
            issued_at       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at      TIMESTAMP   NOT NULL,
            status          ENUM('valid','used','superseded') NOT NULL DEFAULT 'valid',
            used_at         TIMESTAMP   NULL,
            used_by_user_id BIGINT      NULL,
            PRIMARY KEY (code_hash),
            INDEX idx_device_status (device_token, status),
            INDEX idx_expires (expires_at)
        ) $charset",

        "CREATE TABLE IF NOT EXISTS amboat_device_accounts (
            device_token VARCHAR(36) NOT NULL,
            user_id      BIGINT      NOT NULL,
            created_at   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (device_token),
            UNIQUE KEY uq_user (user_id),
            INDEX idx_user (user_id)
        ) $charset",

        "CREATE TABLE IF NOT EXISTS amboat_registration_audit (
            id           BIGINT AUTO_INCREMENT NOT NULL,
            event        ENUM('enrol','approve','reject','block','code_issued','redeem_ok',
                             'redeem_fail','rate_limited','legacy_key_used') NOT NULL,
            device_token VARCHAR(36)  NULL,
            user_id      BIGINT       NULL,
            ip           VARBINARY(16) NULL,
            detail       VARCHAR(255) NULL,
            created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            INDEX idx_device (device_token),
            INDEX idx_created (created_at),
            INDEX idx_event (event)
        ) $charset",

        // Phase A gap fix: amboat_devices must exist before the approval handler can INSERT.
        // version-heartbeat.php Phase D does UPDATE only — it returns 404 if no row exists.
        // This table is assumed to pre-exist in older installs; dbDelta is idempotent.
        "CREATE TABLE IF NOT EXISTS amboat_devices (
            device_token        VARCHAR(36) NOT NULL,
            current_version     VARCHAR(20) NULL,
            version_updated_at  DATETIME    NULL,
            version_check_count INT         NOT NULL DEFAULT 0,
            PRIMARY KEY (device_token)
        ) $charset",
    ];

    foreach ($sqls as $sql) {
        dbDelta($sql);
    }
}

// ---------------------------------------------------------------------------
// wp-admin approval queue — A4
// ---------------------------------------------------------------------------

add_action('admin_menu', function () {
    add_menu_page(
        'd3kOS Device Approvals',
        'd3kOS Devices',
        'manage_options',
        'd3kos-device-approvals',
        'd3kos_render_approval_queue',
        'dashicons-admin-network',
        80
    );
});

function d3kos_render_approval_queue(): void {
    if (!current_user_can('manage_options')) {
        wp_die('Access denied');
    }

    global $wpdb;

    // Handle approve / reject / block actions
    if (
        isset($_POST['d3kos_action'], $_POST['device_token'], $_POST['d3kos_nonce']) &&
        wp_verify_nonce(sanitize_text_field($_POST['d3kos_nonce']), 'd3kos_device_action')
    ) {
        $action = sanitize_key($_POST['d3kos_action']);
        $token  = sanitize_text_field($_POST['device_token']);

        if (in_array($action, ['approve', 'reject', 'block'], true)) {
            $new_status = ($action === 'approve') ? 'approved' : $action . 'd';
            $new_status = ($action === 'block') ? 'blocked' : $new_status;

            $wpdb->query($wpdb->prepare(
                "UPDATE amboat_device_enrolments
                    SET status = %s, reviewed_at = NOW(), reviewed_by = %d
                  WHERE device_token = %s",
                $new_status, get_current_user_id(), $token
            ));

            // Phase A gap fix: INSERT into amboat_devices on approval so that
            // version-heartbeat.php Phase D UPDATE WHERE device_token = ? finds a row.
            // Without this, the first heartbeat after approval returns 404.
            if ($action === 'approve') {
                $wpdb->query($wpdb->prepare(
                    "INSERT IGNORE INTO amboat_devices (device_token) VALUES (%s)",
                    $token
                ));
            }

            $wpdb->insert('amboat_registration_audit', [
                'event'        => $action === 'approve' ? 'approve' : ($action === 'block' ? 'block' : 'reject'),
                'device_token' => $token,
                'user_id'      => get_current_user_id(),
                'detail'       => 'via wp-admin',
            ], ['%s', '%s', '%d', '%s']);

            echo '<div class="notice notice-success"><p>Device ' . esc_html($token) . ' ' . esc_html($action) . 'd.</p></div>';
        }
    }

    // Load pending devices, including duplicate-IP / duplicate-email warnings
    $devices = $wpdb->get_results(
        "SELECT e.*,
                INET6_NTOA(e.enrolled_ip) AS enrolled_ip_display,
                (SELECT COUNT(*) FROM amboat_device_enrolments e2
                  WHERE e2.enrolled_ip = e.enrolled_ip AND e2.status = 'approved') AS approved_from_same_ip,
                (SELECT COUNT(*) FROM amboat_device_enrolments e3
                  WHERE e3.contact_email = e.contact_email AND e3.status = 'approved' AND e3.contact_email IS NOT NULL) AS approved_same_email
           FROM amboat_device_enrolments e
          WHERE e.status = 'pending'
          ORDER BY e.enrolled_at ASC"
    );

    $nonce = wp_create_nonce('d3kos_device_action');

    echo '<div class="wrap"><h1>d3kOS Device Approvals</h1>';
    echo '<p>Review pending d3kOS device enrolments. Approval is the trust anchor — see BUG-66 §3.1.</p>';

    if (empty($devices)) {
        echo '<p>No pending devices.</p></div>';
        return;
    }

    echo '<table class="wp-list-table widefat fixed striped">';
    echo '<thead><tr>
        <th>Device Ref</th>
        <th>Contact Email</th>
        <th>Note</th>
        <th>Source IP</th>
        <th>Enrolled At</th>
        <th>Warnings</th>
        <th>Actions</th>
    </tr></thead><tbody>';

    foreach ($devices as $d) {
        $ref      = esc_html(substr($d->device_token, 0, 8));
        $email    = esc_html($d->contact_email ?? '—');
        $note     = esc_html($d->enrol_note    ?? '—');
        $ip       = esc_html($d->enrolled_ip_display ?? '—');
        $enrolled = esc_html($d->enrolled_at);

        $warnings = [];
        if ((int)$d->approved_from_same_ip > 0) {
            $warnings[] = sprintf('%d approved device(s) from this IP', (int)$d->approved_from_same_ip);
        }
        if ((int)$d->approved_same_email > 0) {
            $warnings[] = sprintf('%d approved device(s) with this email', (int)$d->approved_same_email);
        }
        $warn_html = $warnings ? '<span style="color:#c00">' . implode('<br>', array_map('esc_html', $warnings)) . '</span>' : '—';

        $token_field = '<input type="hidden" name="device_token" value="' . esc_attr($d->device_token) . '">';
        $nonce_field = '<input type="hidden" name="d3kos_nonce" value="' . esc_attr($nonce) . '">';

        echo "<tr><td>$ref</td><td>$email</td><td>$note</td><td>$ip</td><td>$enrolled</td><td>$warn_html</td><td>";

        foreach (['approve' => 'Approve', 'reject' => 'Reject', 'block' => 'Block'] as $act => $label) {
            $btn_style = ($act === 'approve') ? 'button-primary' : 'button';
            echo "<form method='post' style='display:inline;margin-right:4px'>"
               . $token_field . $nonce_field
               . "<input type='hidden' name='d3kos_action' value='" . esc_attr($act) . "'>"
               . "<button type='submit' class='button $btn_style'>" . esc_html($label) . "</button>"
               . "</form>";
        }

        echo "</td></tr>";
    }

    echo '</tbody></table></div>';
}
