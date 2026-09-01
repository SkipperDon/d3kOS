<?php
/**
 * mobile/community-markers.php
 * Pi POSTs a community hazard marker (shallow water, debris, anchorage, etc.)
 * Awards 1 community point per submission.
 *
 * Method: POST
 * Auth: Ed25519 per-device signature (X-Device-Token + X-Timestamp + X-Nonce + X-Signature)
 *       OR legacy Bearer AMBOAT_API_KEY during transition — every legacy use is audited.
 * Body (JSON):
 *   lat           float   required  — exact GPS lat
 *   lng           float   required  — exact GPS lng
 *   marker_type   string  optional  — hazard|shallow|debris|anchorage|fuel|other (default: hazard)
 *   description   string  optional  — max 300 chars
 *   expires_hours int     optional  — hours until marker expires (omit for permanent)
 *
 * Response:
 *   { "success": true, "data": { "id": 42, "marker_type": "hazard", "message": "..." } }
 *
 * Privacy:
 *   Exact coordinates are stored in the DB.
 *   On read (community-get.php), coords are blurred to 2dp (~1km).
 */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/device-auth.php';
require_once __DIR__ . '/auth.php';

if ( $_SERVER['REQUEST_METHOD'] !== 'POST' ) {
    amboat_send_error( 'POST required.', 405 );
}

$device_token = verify_device_request();
$user_id      = amboat_get_user_by_device_token( $device_token );
if ( ! $user_id ) {
    amboat_send_error( 'Device not paired.', 403 );
}
$body = amboat_json_body();

// ── Validate coordinates ─────────────────────────────────────────────────────
$lat = isset( $body['lat'] ) ? (float) $body['lat'] : null;
$lng = isset( $body['lng'] ) ? (float) $body['lng'] : null;

if ( $lat === null || $lng === null
     || $lat < -90 || $lat > 90
     || $lng < -180 || $lng > 180 ) {
    amboat_send_error( 'Valid lat and lng are required.' );
}

// ── Validate marker type ─────────────────────────────────────────────────────
$allowed_types = [ 'hazard', 'shallow', 'debris', 'anchorage', 'fuel', 'other' ];
$marker_type   = in_array( $body['marker_type'] ?? '', $allowed_types, true )
                 ? $body['marker_type'] : 'hazard';

// ── Sanitize description ─────────────────────────────────────────────────────
$description = isset( $body['description'] )
               ? substr( strip_tags( $body['description'] ), 0, 300 ) : null;
if ( $description !== null && trim( $description ) === '' ) {
    $description = null;
}

// ── Expiry ───────────────────────────────────────────────────────────────────
$expires_at    = null;
$expires_hours = (int) ( $body['expires_hours'] ?? 0 );
if ( $expires_hours > 0 && $expires_hours <= 8760 ) { // max 1 year
    $expires_at = date( 'Y-m-d H:i:s', time() + $expires_hours * 3600 );
}

// ── Rate limit: max 20 markers per user per day ──────────────────────────────
$db    = amboat_get_db();
$stmt  = $db->prepare(
    "SELECT COUNT(*) AS cnt FROM amboat_community_markers
     WHERE user_id = ? AND created_at >= CURDATE()"
);
$stmt->bind_param( 'i', $user_id );
$stmt->execute();
$count_row = $stmt->get_result()->fetch_assoc();
if ( (int) $count_row['cnt'] >= 20 ) {
    amboat_send_error( 'Daily marker limit reached (20 per day). Try again tomorrow.', 429 );
}

// ── Insert marker ────────────────────────────────────────────────────────────
$stmt = $db->prepare(
    "INSERT INTO amboat_community_markers (user_id, lat, lng, marker_type, description, expires_at)
     VALUES (?, ?, ?, ?, ?, ?)"
);
$stmt->bind_param( 'iddsss', $user_id, $lat, $lng, $marker_type, $description, $expires_at );
$stmt->execute();
$marker_id = $db->insert_id;

if ( ! $marker_id ) {
    amboat_send_error( 'Failed to save marker. Please try again.', 500 );
}

// ── Award 1 community point ──────────────────────────────────────────────────
$score = (int) amboat_get_user_meta( $user_id, 'atmyboat_forum_score' );
amboat_update_user_meta( $user_id, 'atmyboat_forum_score', $score + 1 );
$monthly = (int) amboat_get_user_meta( $user_id, 'atmyboat_forum_score_month' );
amboat_update_user_meta( $user_id, 'atmyboat_forum_score_month', $monthly + 1 );

amboat_send_success( [
    'id'          => $marker_id,
    'marker_type' => $marker_type,
    'message'     => 'Marker submitted. Thank you for contributing to the community.',
] );
