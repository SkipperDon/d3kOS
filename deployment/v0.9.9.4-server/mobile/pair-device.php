<?php
/**
 * mobile/pair-device.php
 * Called when user scans QR code on Pi — stores pairing code so register-device.php can link it
 * Method: POST (from atmyboat.com /pair-device/ page AJAX form)
 * This endpoint runs in WordPress context (loaded via AJAX action)
 *
 * The Pi's QR code contains:
 *   atmyboat.com/pair-device/?pi_id=<UUID>
 *
 * When user scans with phone:
 * 1. Page loads with ?pi_id= in URL
 * 2. User clicks Confirm — this AJAX endpoint stores pi_id in user meta
 * 3. Pi polls command-queue.php, sees "paired" command, registers via register-device.php
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// This file is loaded in WordPress context via the AJAX handler in registration.php
// The actual handler is: add_action('wp_ajax_atmyboat_confirm_pairing', ...)

add_action( 'wp_ajax_atmyboat_confirm_pairing', 'atmyboat_confirm_pairing' );

function atmyboat_confirm_pairing() {
    check_ajax_referer( 'atmyboat_pair_device', 'nonce' );

    if ( ! is_user_logged_in() ) {
        wp_send_json_error( 'Not logged in.' );
    }

    $pi_id       = sanitize_text_field( $_POST['pi_id'] ?? '' );
    $vessel_name = substr( sanitize_text_field( $_POST['vessel_name'] ?? '' ), 0, 80 );
    $vessel_type = sanitize_key( $_POST['vessel_type'] ?? 'powerboat' );

    $allowed_types = [ 'powerboat', 'sailboat', 'catamaran', 'trawler', 'pontoon', 'other' ];
    if ( ! in_array( $vessel_type, $allowed_types, true ) ) {
        $vessel_type = 'powerboat';
    }

    if ( empty( $pi_id ) ||
         ! preg_match( '/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $pi_id ) ) {
        wp_send_json_error( 'Invalid Pi ID format.' );
    }

    $user_id = get_current_user_id();
    $tier    = get_user_meta( $user_id, 'atmyboat_tier', true ) ?: 'T1';

    // Store pairing code — register-device.php looks this up
    update_user_meta( $user_id, 'atmyboat_pi_pairing_code', $pi_id );
    update_user_meta( $user_id, 'atmyboat_pi_pairing_time', current_time( 'mysql' ) );

    // Determine is_primary: first pairing for this account gets is_primary=1
    global $wpdb;
    $existing_count = (int) $wpdb->get_var(
        $wpdb->prepare( "SELECT COUNT(*) FROM d3kos_pairings WHERE user_id = %d", $user_id )
    );
    $is_primary = ( $existing_count === 0 ) ? 1 : 0;

    // Upsert into d3kos_pairings
    $wpdb->query( $wpdb->prepare(
        "INSERT INTO d3kos_pairings (user_id, pi_id, vessel_name, vessel_type, is_primary, paired_at)
         VALUES (%d, %s, %s, %s, %d, %s)
         ON DUPLICATE KEY UPDATE
           vessel_name = VALUES(vessel_name),
           vessel_type = VALUES(vessel_type),
           paired_at   = VALUES(paired_at)",
        $user_id, $pi_id, $vessel_name, $vessel_type, $is_primary, current_time( 'mysql' )
    ) );

    // Queue a "pair_confirmed" command for the Pi to pick up
    $wpdb->insert( 'amboat_command_queue', [
        'user_id'    => $user_id,
        'pi_id'      => $pi_id,
        'command'    => 'pair_confirmed',
        'payload'    => json_encode( [ 'user_id' => $user_id, 'tier' => $tier ] ),
        'created_at' => current_time( 'mysql' ),
        'status'     => 'pending',
    ] );

    wp_send_json_success( [
        'message'    => 'Pairing confirmed. Your Pi will connect automatically.',
        'is_primary' => (bool) $is_primary,
    ] );
}
