<?php
/**
 * Template Name: Dashboard — The Chart Room
 * T1+ authenticated. History + management only (not real-time).
 */

if ( ! is_user_logged_in() ) {
    wp_safe_redirect( wp_login_url( home_url( '/dashboard/' ) ) );
    exit;
}

$current_user = wp_get_current_user();
$user_id      = $current_user->ID;
$tier         = get_user_meta( $user_id, 'atmyboat_tier', true ) ?: 'T1';
$pi_paired    = get_user_meta( $user_id, 'atmyboat_pi_paired', true ) === '1';
$first_name   = get_user_meta( $user_id, 'first_name', true ) ?: $current_user->display_name;

// Last Pi sync info (stored by mobile/data-ingress.php when Pi posts a sync)
$last_sync       = get_user_meta( $user_id, 'atmyboat_last_sync', true );
$last_lat        = get_user_meta( $user_id, 'atmyboat_position_lat', true );
$last_lng        = get_user_meta( $user_id, 'atmyboat_position_lng', true );
$last_engine_rpm = get_user_meta( $user_id, 'atmyboat_last_rpm', true );
$last_engine_tmp = get_user_meta( $user_id, 'atmyboat_last_coolant_temp', true );
$vessel_name     = get_user_meta( $user_id, 'atmyboat_vessel_name', true );
$d3kos_version   = get_user_meta( $user_id, 'atmyboat_d3kos_version', true );

// Fix My Pi history (stored as serialized array of report objects)
$fmp_history = get_user_meta( $user_id, 'atmyboat_fmp_history', true );
$fmp_history = is_array( $fmp_history ) ? $fmp_history : [];
$fmp_remaining = null;
if ( $tier === 'T2' ) {
    $fmp_remaining = max( 0, 3 - (int) get_user_meta( $user_id, 'atmyboat_fmp_used_month', true ) );
}

// PDF reports history (T2/T3 only)
$pdf_reports = [];
if ( in_array( $tier, [ 'T2', 'T3' ], true ) ) {
    $pdf_reports = get_user_meta( $user_id, 'atmyboat_pdf_reports', true );
    $pdf_reports = is_array( $pdf_reports ) ? array_slice( $pdf_reports, 0, 10 ) : [];
}

get_header();
?>
<main id="site-content" class="amboat-page amboat-dashboard-page">
  <div class="amboat-page-inner">

    <header class="amboat-page-header">
      <p class="amboat-section-label">
        <?php echo esc_html( $tier ); ?> MEMBER
      </p>
      <h1>Welcome back, <?php echo esc_html( $first_name ); ?></h1>
      <?php if ( $vessel_name ) : ?>
      <p class="amboat-page-subtitle">Your vessel: <strong><?php echo esc_html( $vessel_name ); ?></strong></p>
      <?php endif; ?>
    </header>

    <!-- NOT PAIRED — ONBOARDING PROMPT -->
    <?php if ( ! $pi_paired ) : ?>
    <section class="amboat-dashboard-onboarding card" aria-label="Get started">
      <h2>Get Started</h2>
      <p>You haven't paired a Raspberry Pi yet. Pair your Pi to start syncing boat data,
         unlock the community map, and use Fix My Pi.</p>
      <a href="<?php echo esc_url( home_url( '/pair-device/' ) ); ?>" class="btn-primary">
        Pair Your Pi →
      </a>
    </section>
    <?php endif; ?>

    <!-- BOAT STATUS SNAPSHOT -->
    <?php if ( $pi_paired && $last_sync ) : ?>
    <section class="amboat-dashboard-snapshot" aria-label="Last known boat status">
      <h2>Last Known Status</h2>
      <p class="amboat-text-muted">
        Synced <?php echo esc_html( human_time_diff( strtotime( $last_sync ), current_time( 'timestamp' ) ) ); ?> ago
      </p>
      <div class="amboat-snapshot-grid">
        <?php if ( $last_lat && $last_lng ) : ?>
        <div class="amboat-snapshot-item card">
          <h3>Position</h3>
          <p class="amboat-snapshot-value">
            <?php echo esc_html( number_format( (float) $last_lat, 4 ) ); ?>°N,
            <?php echo esc_html( number_format( abs( (float) $last_lng ), 4 ) ); ?>°W
          </p>
          <p class="amboat-snapshot-note amboat-text-muted">Approximate — privacy protected</p>
        </div>
        <?php endif; ?>

        <?php if ( $last_engine_rpm !== '' && $last_engine_rpm !== false ) : ?>
        <div class="amboat-snapshot-item card">
          <h3>Engine RPM</h3>
          <p class="amboat-snapshot-value"><?php echo esc_html( number_format( (int) $last_engine_rpm ) ); ?> RPM</p>
          <p class="amboat-snapshot-note amboat-text-muted">At last sync</p>
        </div>
        <?php endif; ?>

        <?php if ( $last_engine_tmp !== '' && $last_engine_tmp !== false ) : ?>
        <div class="amboat-snapshot-item card">
          <h3>Coolant Temp</h3>
          <p class="amboat-snapshot-value"><?php echo esc_html( (int) $last_engine_tmp ); ?>°C</p>
          <p class="amboat-snapshot-note amboat-text-muted">At last sync</p>
        </div>
        <?php endif; ?>

        <?php if ( $d3kos_version ) : ?>
        <div class="amboat-snapshot-item card">
          <h3>d3kOS Version</h3>
          <p class="amboat-snapshot-value"><?php echo esc_html( $d3kos_version ); ?></p>
        </div>
        <?php endif; ?>
      </div>
    </section>
    <?php elseif ( $pi_paired ) : ?>
    <section class="amboat-dashboard-snapshot card" aria-label="No sync data yet">
      <h2>No Sync Data Yet</h2>
      <p>Open the d3kOS companion app on your phone and connect to your Pi to start syncing data.</p>
    </section>
    <?php endif; ?>

    <!-- FIX MY PI SECTION -->
    <section class="amboat-dashboard-fmp" aria-label="Fix My Pi">
      <h2>Fix My Pi</h2>
      <div class="amboat-fmp-status card">
        <?php if ( $tier === 'T1' ) : ?>
        <p>Fix My Pi is available for <strong>$29.99 per incident</strong> on T1.</p>
        <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="btn-primary">
          Request Fix My Pi — $29.99
        </a>
        <?php elseif ( $tier === 'T2' ) : ?>
        <p>
          <strong><?php echo esc_html( $fmp_remaining ); ?> Fix My Pi request<?php echo $fmp_remaining !== 1 ? 's' : ''; ?></strong>
          remaining this month (3 included in T2).
        </p>
        <?php if ( $fmp_remaining > 0 ) : ?>
        <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="btn-primary">
          Request Fix My Pi →
        </a>
        <?php else : ?>
        <p class="amboat-text-muted">Monthly allowance used. Resets on the 1st.</p>
        <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="btn-secondary">
          Request Additional Fix — $29.99 →
        </a>
        <?php endif; ?>
        <?php elseif ( $tier === 'T3' ) : ?>
        <p>Unlimited Fix My Pi included in your T3 subscription.</p>
        <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="btn-primary">
          Request Fix My Pi →
        </a>
        <?php endif; ?>
      </div>

      <!-- FMP History -->
      <?php if ( ! empty( $fmp_history ) ) : ?>
      <div class="amboat-fmp-history">
        <h3>History</h3>
        <table class="amboat-history-table">
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Status</th>
              <th scope="col">Issue</th>
              <th scope="col">Report</th>
            </tr>
          </thead>
          <tbody>
            <?php foreach ( $fmp_history as $report ) : ?>
            <tr>
              <td><?php echo esc_html( isset( $report['date'] ) ? date( 'M j, Y', strtotime( $report['date'] ) ) : '—' ); ?></td>
              <td>
                <span class="tag <?php echo $report['status'] === 'completed' ? 'tag-green' : 'tag-amber'; ?>">
                  <?php echo esc_html( ucfirst( $report['status'] ?? 'pending' ) ); ?>
                </span>
              </td>
              <td><?php echo esc_html( $report['issue'] ?? '—' ); ?></td>
              <td>
                <?php if ( ! empty( $report['report_url'] ) ) : ?>
                <a href="<?php echo esc_url( $report['report_url'] ); ?>" target="_blank" rel="noopener">View Report →</a>
                <?php else : ?>
                —
                <?php endif; ?>
              </td>
            </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
      </div>
      <?php endif; ?>
    </section>

    <!-- PDF REPORTS (T2/T3) -->
    <?php if ( in_array( $tier, [ 'T2', 'T3' ], true ) ) : ?>
    <section class="amboat-dashboard-reports" aria-label="PDF boat reports">
      <h2>PDF Boat Reports</h2>
      <?php if ( empty( $pdf_reports ) ) : ?>
      <div class="amboat-empty-state card">
        <p>No reports yet. PDF reports are generated from your boat's data and include
           AI-powered maintenance recommendations.</p>
        <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="btn-secondary">
          Generate Report →
        </a>
      </div>
      <?php else : ?>
      <div class="amboat-reports-list">
        <?php foreach ( $pdf_reports as $report ) : ?>
        <div class="amboat-report-item card">
          <div class="amboat-report-info">
            <span class="amboat-report-date">
              <?php echo esc_html( isset( $report['date'] ) ? date( 'F j, Y', strtotime( $report['date'] ) ) : '—' ); ?>
            </span>
            <span class="amboat-report-type amboat-text-muted">
              <?php echo esc_html( $report['type'] ?? 'Boat Health Report' ); ?>
            </span>
          </div>
          <?php if ( ! empty( $report['url'] ) ) : ?>
          <a href="<?php echo esc_url( $report['url'] ); ?>"
             class="btn-secondary amboat-report-download"
             target="_blank" rel="noopener noreferrer">
            Download PDF →
          </a>
          <?php endif; ?>
        </div>
        <?php endforeach; ?>
      </div>
      <?php endif; ?>
    </section>
    <?php endif; ?>

    <!-- ACCOUNT SETTINGS -->
    <section class="amboat-dashboard-account card" aria-label="Account settings">
      <h2>Account</h2>
      <div class="amboat-account-grid">
        <div>
          <p><strong>Email:</strong> <?php echo esc_html( $current_user->user_email ); ?></p>
          <p><strong>Member since:</strong> <?php echo esc_html( date( 'F Y', strtotime( $current_user->user_registered ) ) ); ?></p>
          <p><strong>Plan:</strong> <?php echo esc_html( $tier ); ?>
            <?php if ( $tier === 'T1' ) : ?>
            — <a href="<?php echo esc_url( home_url( '/fix-my-pi/' ) ); ?>" class="amboat-inline-link">Upgrade</a>
            <?php endif; ?>
          </p>
        </div>
        <div class="amboat-account-actions">
          <a href="<?php echo esc_url( admin_url( 'profile.php' ) ); ?>" class="btn-secondary">Edit Profile</a>
          <a href="<?php echo esc_url( wp_logout_url( home_url() ) ); ?>" class="btn-secondary amboat-logout-btn">Log Out</a>
        </div>
      </div>
    </section>

  </div><!-- .amboat-page-inner -->
</main>
<?php get_footer(); ?>
