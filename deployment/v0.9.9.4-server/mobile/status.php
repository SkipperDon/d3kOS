<?php
// Handler for GET /wp-json/amboat-device/v1/status — BUG-66 Phase A.
// Returns the current enrolment status of a device.
// Uses verify_device_signature (not verify_device_request) so pending devices
// can poll for their approval status.

if (!defined('ABSPATH')) {
    exit;
}

require_once __DIR__ . '/device-auth.php';

/**
 * Handle GET /wp-json/amboat-device/v1/status
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function d3kos_handle_status(WP_REST_Request $request): WP_REST_Response|WP_Error {
    // verify_device_signature accepts any enrolled device regardless of approval status.
    // A pending device needs to poll its own status — we cannot require approved here.
    $result = verify_device_signature($request);
    if (is_wp_error($result)) {
        return $result;
    }

    return new WP_REST_Response(['status' => $result['status']], 200);
}
