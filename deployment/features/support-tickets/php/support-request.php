<?php
/**
 * support-request.php — AtMyBoat.com PWA Support Button
 * v0.9.7 Phase 1: Sends email + inserts ticket record. Returns ticket_id.
 *
 * Auth:      Bearer app_token (validated against wpax_usermeta)
 * Rate limit: 3 requests per user per 24 hours (stored in wpax_usermeta)
 */

// Suppress PHP notices/warnings — any stray output breaks JSON response
error_reporting(0);
@ini_set('display_errors', 0);

define('WP_USE_THEMES', false);
require_once __DIR__ . '/../../../../wp-load.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'POST required']);
    exit;
}

// ── Auth ──────────────────────────────────────────────────────────────────────
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$app_token = trim($m[1]);

global $wpdb;
$prefix = 'wpax_';

$meta_row = $wpdb->get_row($wpdb->prepare(
    "SELECT user_id FROM {$prefix}usermeta WHERE meta_key='atmyboat_app_token' AND meta_value=%s LIMIT 1",
    $app_token
));

if (!$meta_row) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}
$user_id = (int)$meta_row->user_id;

// ── Rate limit (3 per 24h) ────────────────────────────────────────────────────
$rate_key  = 'atmyboat_support_requests_24h';
$rate_data = get_user_meta($user_id, $rate_key, true);
$now       = time();
$window    = 24 * 3600;
$max       = 3;

if ($rate_data) {
    $entries = json_decode($rate_data, true) ?: [];
    $entries = array_filter($entries, fn($ts) => ($now - $ts) < $window);
} else {
    $entries = [];
}

if (count($entries) >= $max) {
    $oldest   = min($entries);
    $reset_in = $window - ($now - $oldest);
    $mins     = (int)ceil($reset_in / 60);
    http_response_code(429);
    echo json_encode([
        'success' => false,
        'error'   => "Support request limit reached (3 per 24 hours). Try again in {$mins} minutes.",
    ]);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────
$body         = json_decode(file_get_contents('php://input'), true);
$message      = trim($body['message'] ?? '');
$device_token = trim($body['device_token'] ?? '');
$subject_raw  = trim($body['subject'] ?? '');

if (!$message || strlen($message) < 10 || strlen($message) > 500) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Message must be 10–500 characters.']);
    exit;
}

// Auto-derive subject if not provided
if (!$subject_raw) {
    $subject_raw = strlen($message) > 80 ? substr($message, 0, 77) . '…' : $message;
}
$subject_raw = substr($subject_raw, 0, 200);

// ── Customer context ──────────────────────────────────────────────────────────
$user = get_userdata($user_id);
$tier = get_user_meta($user_id, 'atmyboat_tier', true) ?: 'T0';
$fmp  = get_user_meta($user_id, 'atmyboat_fmp_used_month', true) ?: '0';

$pairing = $wpdb->get_row($wpdb->prepare(
    "SELECT p.vessel_name, p.vessel_type, p.last_seen_at, d.d3kos_version, d.device_token
     FROM d3kos_pairings p
     LEFT JOIN amboat_devices d ON d.device_token = p.device_token
     WHERE p.user_id = %d ORDER BY p.last_seen_at DESC LIMIT 1",
    $user_id
));

// Use pairing device_token if not supplied in body
if (!$device_token && $pairing && $pairing->device_token) {
    $device_token = $pairing->device_token;
}

$alert_count = (int)$wpdb->get_var($wpdb->prepare(
    "SELECT COUNT(*) FROM amboat_alerts WHERE user_id = %d AND triggered_at > DATE_SUB(NOW(), INTERVAL 7 DAY)",
    $user_id
));

// ── Insert ticket record ───────────────────────────────────────────────────────
$ticket_id = null;
try {
    $wpdb->suppress_errors(true);
    $inserted = $wpdb->insert(
        'amboat_support_tickets',
        [
            'user_id'      => $user_id,
            'device_token' => $device_token ?: null,
            'subject'      => $subject_raw,
            'body'         => $message,
            'status'       => 'open',
            'created_at'   => current_time('mysql'),
            'updated_at'   => current_time('mysql'),
        ],
        ['%d', '%s', '%s', '%s', '%s', '%s', '%s']
    );
    $ticket_id = $inserted ? (int)$wpdb->insert_id : null;
} catch (Exception $e) {
    // DB failure is non-fatal — email still sends
    $ticket_id = null;
}

// ── Build email ───────────────────────────────────────────────────────────────
$ticket_ref = $ticket_id ? " [Ticket #{$ticket_id}]" : '';
$email_subj = "[AtMyBoat Support]{$ticket_ref} {$user->display_name} ({$tier}) — " . date('Y-m-d H:i') . ' UTC';

$email_body  = "Customer Support Request{$ticket_ref}\n";
$email_body .= str_repeat('─', 50) . "\n\n";
$email_body .= "Name:        {$user->display_name}\n";
$email_body .= "Email:       {$user->user_email}\n";
$email_body .= "User ID:     {$user_id}\n";
$email_body .= "Tier:        {$tier}\n";
$email_body .= "FMP used:    {$fmp} this month\n";

if ($pairing) {
    $email_body .= "Vessel:      " . ($pairing->vessel_name ?: 'unnamed') . " ({$pairing->vessel_type})\n";
    $email_body .= "d3kOS:       v" . ($pairing->d3kos_version ?: '?') . "\n";
    $email_body .= "Last seen:   " . ($pairing->last_seen_at ?: 'never') . " UTC\n";
}

$email_body .= "Alerts (7d): {$alert_count}\n";
$email_body .= "\n" . str_repeat('─', 50) . "\n\n";
$email_body .= "MESSAGE:\n\n{$message}\n";

if ($ticket_id) {
    $email_body .= "\n" . str_repeat('─', 50) . "\n";
    $email_body .= "Reply via Admin CRM → Tickets → #{$ticket_id}\n";
}

$sent = wp_mail('skipperdon@atmyboat.com', $email_subj, $email_body, [
    'From: AtMyBoat Support <noreply@atmyboat.com>',
    'Reply-To: ' . $user->user_email,
]);

if (!$sent && !$ticket_id) {
    // Both email and DB failed — only hard error if both fail
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to send support request. Please try again.']);
    exit;
}

// ── Record rate limit entry ────────────────────────────────────────────────────
$entries[] = $now;
update_user_meta($user_id, $rate_key, json_encode(array_values($entries)));

echo json_encode([
    'success' => true,
    'data'    => [
        'sent'      => $sent,
        'ticket_id' => $ticket_id,
    ],
]);
