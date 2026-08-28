<?php
/**
 * mobile/version.php
 * Public OTA version manifest — read by update_agent.py on every 24h cycle.
 * No auth required — version numbers are not sensitive.
 * Update this file when a new d3kOS release is ready to ship.
 *
 * Format expected by update_agent.py:
 *   incremental.version  string   Version string e.g. "0.9.9.5"
 *   incremental.url      string   HTTPS URL to tar.gz package (empty = no package ready)
 *   incremental.checksum string   SHA-256 of the tar.gz (empty when url is empty)
 *   major.version        string   Major release version (same or higher)
 *   major.t1_upgrade     bool     true = T1 subscribers get this major release
 */

header( 'Content-Type: application/json' );
header( 'Cache-Control: max-age=3600, public' );

echo json_encode( [
    'incremental' => [
        'version'    => '0.9.9.4',
        'url'        => '',
        'checksum'   => '',
        't1_upgrade' => false,
    ],
    'major' => [
        'version'    => '0.9.9.4',
        'url'        => '',
        'checksum'   => '',
        't1_upgrade' => false,
    ],
    '_updated' => '2026-08-28',
    '_note'    => 'Increment version + add url+checksum when packaging a new release',
], JSON_PRETTY_PRINT );
