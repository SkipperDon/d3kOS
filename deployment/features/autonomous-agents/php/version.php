<?php
/**
 * version.php — d3kOS Update Version Manifest
 * Public endpoint — no authentication required.
 * Called by AA2 UpdateAgent on every Pi (T0 and T1+).
 *
 * Deploy to: staging/wp-content/themes/twentytwenty-child/mobile/version.php
 *
 * To release an incremental update:
 *   1. Upload d3kos-X.X.X.tar.gz to archive.org
 *   2. Get the SHA-256 checksum: sha256sum d3kos-X.X.X.tar.gz
 *   3. Update 'incremental' block below with version, url, checksum, released
 *   4. Deploy this file to HostPapa
 *   All T1+ Pis will auto-apply within 24h. T0 Pis will see a notice.
 *
 * To release a major version (T1+ auto-upgrade):
 *   1. Same process but update 'major' block
 *   2. Set t1_upgrade: true when T1+ Pis should receive it automatically
 *
 * Package format (tar.gz contents):
 *   manifest.json                        — file list + services to restart
 *   opt/d3kos/services/...               — changed files (mirrored path from /)
 */

error_reporting(0);
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');   // Pi can be on any network

echo json_encode([
    'incremental' => [
        'version'   => '0.9.8',
        'url'       => '',       // fill when first update package is uploaded to archive.org
        'checksum'  => '',       // sha256:xxxxxxxx...
        'released'  => '2026-04-08',
        't1_upgrade' => false,
    ],
    'major' => [
        'version'   => '0.9.8',
        'url'       => '',       // fill when v1.0 package is ready
        'checksum'  => '',
        'released'  => '',
        't1_upgrade' => false,   // set true when T1+ Pis should auto-receive major upgrade
    ],
], JSON_PRETTY_PRINT);
