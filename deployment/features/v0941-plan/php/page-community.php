<?php
/**
 * Template Name: Community Page
 * T1+ only — community map, forum activity, hall of fame, challenges
 */

if ( ! is_user_logged_in() ) {
    wp_safe_redirect( wp_login_url( home_url( '/community/' ) ) );
    exit;
}

$current_user = wp_get_current_user();
$tier         = get_user_meta( $current_user->ID, 'atmyboat_tier', true ) ?: 'T1';
$pi_paired    = get_user_meta( $current_user->ID, 'atmyboat_pi_paired', true ) === '1';
$map_sharing  = get_user_meta( $current_user->ID, 'atmyboat_map_sharing', true );
$map_sharing  = ( $map_sharing === '' ) ? '1' : $map_sharing; // default on
$app_token    = get_user_meta( $current_user->ID, 'atmyboat_app_token', true ) ?: '';
$can_add_marker = in_array( $tier, [ 'T1', 'T2', 'T3' ], true );

// Community stats
$total_users    = count_users();
$member_count   = $total_users['total_users'];
$post_count     = wp_count_posts( 'topic' )->publish ?? 0;

// Recent forum activity — latest 5 topics
$recent_topics = [];
if ( function_exists( 'bbp_get_topic_post_type' ) ) {
    $topic_query = new WP_Query( [
        'post_type'      => bbp_get_topic_post_type(),
        'posts_per_page' => 5,
        'post_status'    => 'publish',
        'orderby'        => 'date',
        'order'          => 'DESC',
    ] );
    $recent_topics = $topic_query->posts;
    wp_reset_postdata();
}

// Active challenge
$active_challenge = null;
$challenge_query = new WP_Query( [
    'post_type'      => 'amboat_challenge',
    'posts_per_page' => 1,
    'post_status'    => 'publish',
    'meta_key'       => '_challenge_active',
    'meta_value'     => '1',
] );
if ( $challenge_query->have_posts() ) {
    $challenge_query->the_post();
    $active_challenge = [
        'title'   => get_the_title(),
        'prize'   => get_post_meta( get_the_ID(), '_challenge_prize', true ),
        'ends'    => get_post_meta( get_the_ID(), '_challenge_end_date', true ),
        'url'     => get_permalink(),
    ];
    wp_reset_postdata();
}

// Hall of fame — top 3 users by forum post count this month
$hof_users = get_users( [
    'meta_key'   => 'atmyboat_forum_score',
    'orderby'    => 'meta_value_num',
    'order'      => 'DESC',
    'number'     => 3,
] );

get_header();
?>
<main id="site-content" class="amboat-page amboat-community-page">
  <div class="amboat-page-inner amboat-page-inner--full">

    <header class="amboat-page-header">
      <p class="amboat-section-label">COMMUNITY</p>
      <h1>The Fleet</h1>
    </header>

    <!-- COMMUNITY MAP -->
    <section class="amboat-map-section" aria-label="Community fleet map">
      <div id="amboat-community-map" role="img" aria-label="Map showing d3kOS boats on the water">
        <div class="amboat-map-loading" aria-live="polite">Loading map…</div>
      </div>
      <div class="amboat-map-legend" aria-label="Map legend">
        <span class="amboat-legend-item">
          <span class="amboat-dot amboat-dot--red" aria-hidden="true"></span>
          Your boat
        </span>
        <span class="amboat-legend-item">
          <span class="amboat-dot amboat-dot--green" aria-hidden="true"></span>
          d3kOS fleet
        </span>
        <span class="amboat-map-privacy-note">
          Positions approximate (~500m). Click a dot for no details — privacy protected.
        </span>
      </div>
      <div class="amboat-map-controls">
        <label class="amboat-toggle-label" for="amboat-map-sharing">
          <input type="checkbox" id="amboat-map-sharing"
                 <?php checked( $map_sharing, '1' ); ?>
                 data-nonce="<?php echo esc_attr( wp_create_nonce( 'atmyboat_map_sharing' ) ); ?>">
          Show my boat on the community map
        </label>
        <?php if ( $can_add_marker ) : ?>
        <button id="amboat-add-marker-btn" class="btn-secondary" type="button"
                aria-haspopup="dialog">
          + Add Marker
        </button>
        <?php endif; ?>
      </div>
    </section>

    <?php if ( $can_add_marker ) : ?>
    <!-- ADD MARKER OVERLAY -->
    <div id="amboat-marker-overlay" role="dialog" aria-modal="true"
         aria-labelledby="amboat-marker-title"
         style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;
                display:none;align-items:center;justify-content:center;">
      <div style="background:#fff;border-radius:12px;padding:28px 24px;max-width:380px;
                  width:90%;box-shadow:0 8px 32px rgba(0,0,0,.25);">
        <h2 id="amboat-marker-title" style="margin:0 0 16px;font-size:1.2rem;">Add Map Marker</h2>
        <p id="amboat-marker-instructions" style="font-size:.9rem;color:#555;margin:0 0 16px;">
          Click a location on the map, then fill in the details below.
        </p>
        <div id="amboat-marker-coords" style="font-size:.85rem;color:#888;margin-bottom:16px;min-height:1.2em;"></div>
        <div style="margin-bottom:14px;">
          <label for="amboat-marker-type" style="display:block;font-size:.9rem;font-weight:600;margin-bottom:4px;">Type</label>
          <select id="amboat-marker-type" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;font-size:.9rem;">
            <option value="hazard">⚠ Hazard</option>
            <option value="shallow">Shallow Water</option>
            <option value="debris">Debris</option>
            <option value="anchorage">⚓ Anchorage</option>
            <option value="fuel">⛽ Fuel</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div style="margin-bottom:14px;">
          <label for="amboat-marker-severity" style="display:block;font-size:.9rem;font-weight:600;margin-bottom:4px;">Severity</label>
          <select id="amboat-marker-severity" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;font-size:.9rem;">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div style="margin-bottom:18px;">
          <label for="amboat-marker-desc" style="display:block;font-size:.9rem;font-weight:600;margin-bottom:4px;">Description (optional)</label>
          <textarea id="amboat-marker-desc" rows="2" maxlength="200"
                    style="width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;
                           font-size:.9rem;resize:vertical;box-sizing:border-box;"
                    placeholder="e.g. Submerged rock, visible at low tide"></textarea>
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;">
          <button id="amboat-marker-cancel" type="button"
                  style="padding:9px 18px;border:1px solid #ccc;border-radius:6px;
                         background:#fff;cursor:pointer;font-size:.9rem;">Cancel</button>
          <button id="amboat-marker-submit" type="button" disabled
                  style="padding:9px 18px;border:none;border-radius:6px;
                         background:#1a6b3a;color:#fff;cursor:pointer;font-size:.9rem;
                         opacity:.5;">Submit Marker</button>
        </div>
        <p id="amboat-marker-status" style="font-size:.85rem;margin:10px 0 0;min-height:1.2em;color:#c00;"></p>
      </div>
    </div>
    <?php endif; ?>

    <!-- COMMUNITY STATS -->
    <section class="amboat-community-stats" aria-label="Community statistics">
      <div class="amboat-stat">
        <span class="amboat-stat-number" id="boats-online">—</span>
        <span class="amboat-stat-label">boats synced today</span>
      </div>
      <div class="amboat-stat">
        <span class="amboat-stat-number"><?php echo esc_html( number_format( $member_count ) ); ?></span>
        <span class="amboat-stat-label">members</span>
      </div>
      <div class="amboat-stat">
        <span class="amboat-stat-number"><?php echo esc_html( number_format( $post_count ) ); ?></span>
        <span class="amboat-stat-label">forum discussions</span>
      </div>
    </section>

    <div class="amboat-community-grid">

      <!-- RECENT FORUM ACTIVITY -->
      <section class="amboat-community-section amboat-recent-threads">
        <header class="amboat-section-header">
          <h2>Recent Discussions</h2>
          <a href="<?php echo esc_url( home_url( '/forum/' ) ); ?>" class="amboat-see-all">View all in Forum →</a>
        </header>
        <?php if ( empty( $recent_topics ) ) : ?>
        <p class="amboat-empty-state">No discussions yet. <a href="<?php echo esc_url( home_url( '/forum/' ) ); ?>">Start one →</a></p>
        <?php else : ?>
        <ul class="amboat-thread-list">
          <?php foreach ( $recent_topics as $topic ) : ?>
          <li class="thread-item">
            <a href="<?php echo esc_url( get_permalink( $topic ) ); ?>" class="thread-title">
              <?php echo esc_html( $topic->post_title ); ?>
            </a>
            <span class="thread-meta">
              <?php echo esc_html( human_time_diff( strtotime( $topic->post_date ), current_time( 'timestamp' ) ) ); ?> ago
            </span>
          </li>
          <?php endforeach; ?>
        </ul>
        <?php endif; ?>
      </section>

      <!-- HALL OF FAME -->
      <section class="amboat-community-section amboat-hall-of-fame-preview">
        <header class="amboat-section-header">
          <h2>Hall of Fame</h2>
          <a href="<?php echo esc_url( home_url( '/hall-of-fame/' ) ); ?>" class="amboat-see-all">See full leaderboard →</a>
        </header>
        <?php if ( empty( $hof_users ) ) : ?>
        <p class="amboat-empty-state">Be the first on the leaderboard — <a href="<?php echo esc_url( home_url( '/forum/' ) ); ?>">post in the forum</a>.</p>
        <?php else : ?>
        <ol class="amboat-hof-list">
          <?php foreach ( $hof_users as $i => $hof_user ) : ?>
          <li class="amboat-hof-item">
            <span class="amboat-hof-rank" aria-label="Rank <?php echo $i + 1; ?>"><?php echo $i + 1; ?></span>
            <?php echo get_avatar( $hof_user->ID, 44 ); ?>
            <span class="amboat-hof-name"><?php echo esc_html( $hof_user->display_name ); ?></span>
          </li>
          <?php endforeach; ?>
        </ol>
        <?php endif; ?>
      </section>

      <!-- ACTIVE CHALLENGE -->
      <?php if ( $active_challenge ) : ?>
      <section class="amboat-community-section amboat-challenge-preview">
        <header class="amboat-section-header">
          <h2>Active Challenge</h2>
          <a href="<?php echo esc_url( home_url( '/challenges/' ) ); ?>" class="amboat-see-all">All challenges →</a>
        </header>
        <div class="amboat-challenge-card card">
          <h3><?php echo esc_html( $active_challenge['title'] ); ?></h3>
          <?php if ( $active_challenge['prize'] ) : ?>
          <p class="amboat-challenge-prize">
            <span class="tag tag-amber">PRIZE</span>
            <?php echo esc_html( $active_challenge['prize'] ); ?>
          </p>
          <?php endif; ?>
          <?php if ( $active_challenge['ends'] ) : ?>
          <p class="amboat-text-muted">
            Ends: <?php echo esc_html( date( 'F j, Y', strtotime( $active_challenge['ends'] ) ) ); ?>
          </p>
          <?php endif; ?>
          <a href="<?php echo esc_url( $active_challenge['url'] ); ?>" class="btn-primary">Join Challenge →</a>
        </div>
      </section>
      <?php endif; ?>


    <!-- Community photo strip -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.25rem;margin:2.5rem 0 0;">
      <figure style="margin:0;border-radius:12px;overflow:hidden;">
        <img src="<?php echo esc_url( get_stylesheet_directory_uri() ); ?>/images/site/b3-boat-dock.jpg"
             alt="Boats moored at a dock — the AtMyBoat community"
             loading="lazy"
             style="width:100%;height:200px;object-fit:cover;display:block;">
      </figure>
      <figure style="margin:0;border-radius:12px;overflow:hidden;">
        <img src="<?php echo esc_url( get_stylesheet_directory_uri() ); ?>/images/site/t4-group-boaters.jpg"
             alt="Group of boaters on the water"
             loading="lazy"
             style="width:100%;height:200px;object-fit:cover;display:block;">
      </figure>
      <figure style="margin:0;border-radius:12px;overflow:hidden;">
        <img src="<?php echo esc_url( get_stylesheet_directory_uri() ); ?>/images/site/s6-community-map-desktop.jpg"
             alt="AtMyBoat community map showing fleet dots across the region"
             loading="lazy"
             style="width:100%;height:200px;object-fit:cover;display:block;">
      </figure>
    </div>

    </div><!-- .amboat-community-grid -->

  </div>
</main>

<script>
// ── Community map ─────────────────────────────────────────────────────────────

(function () {
  'use strict';

  var COMMUNITY_GET_URL  = '<?php echo esc_url( home_url( '/wp-content/themes/twentytwenty-child/mobile/community-get.php' ) ); ?>';
  var MARKER_WRITE_URL   = '<?php echo esc_url( home_url( '/wp-content/themes/twentytwenty-child/mobile/community-markers-write.php' ) ); ?>';
  var APP_TOKEN          = '<?php echo esc_js( $app_token ); ?>';
  var CAN_ADD_MARKER     = <?php echo $can_add_marker ? 'true' : 'false'; ?>;

  // ── Initialise Leaflet map ──────────────────────────────────────────────────
  var mapEl = document.getElementById('amboat-community-map');
  if (!mapEl || typeof L === 'undefined') return;

  // Remove the loading placeholder once Leaflet takes over
  var loadingEl = mapEl.querySelector('.amboat-map-loading');
  if (loadingEl) loadingEl.remove();

  var map = L.map('amboat-community-map', { zoomControl: true }).setView([45, -76], 6);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18
  }).addTo(map);

  // Layer groups — cleared on each refresh
  var fleetLayer   = L.layerGroup().addTo(map);
  var markerLayer  = L.layerGroup().addTo(map);

  // ── Icon helpers ────────────────────────────────────────────────────────────
  var MARKER_ICONS = {
    hazard    : { emoji: '⚠',  color: '#e53935' },
    shallow   : { emoji: '〰', color: '#fb8c00' },
    debris    : { emoji: '🪨', color: '#6d4c41' },
    anchorage : { emoji: '⚓', color: '#1565c0' },
    fuel      : { emoji: '⛽', color: '#2e7d32' },
    other     : { emoji: '★',  color: '#7b1fa2' }
  };

  function makeMarkerIcon(type) {
    var cfg = MARKER_ICONS[type] || MARKER_ICONS.other;
    return L.divIcon({
      html: '<span style="font-size:22px;line-height:1;display:block;' +
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">' + cfg.emoji + '</span>',
      iconSize   : [28, 28],
      iconAnchor : [14, 14],
      className  : ''
    });
  }

  // ── Load community data ─────────────────────────────────────────────────────
  function loadCommunityData() {
    fetch(COMMUNITY_GET_URL)
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.success) return;
        var data = res.data;

        // Update fleet count stat
        var boatsEl = document.getElementById('boats-online');
        if (boatsEl) boatsEl.textContent = data.fleet_count || '0';

        // Fleet positions — small blue circles, no popup (privacy)
        fleetLayer.clearLayers();
        (data.positions || []).forEach(function (pos) {
          L.circleMarker([pos.lat, pos.lng], {
            radius      : 7,
            fillColor   : '#1565c0',
            color       : '#fff',
            weight      : 1.5,
            fillOpacity : 0.8
          }).addTo(fleetLayer);
        });

        // Hazard / anchorage / fuel markers
        markerLayer.clearLayers();
        (data.markers || []).forEach(function (m) {
          var icon    = makeMarkerIcon(m.type);
          var desc    = m.description ? '<br><em>' + escHtml(m.description) + '</em>' : '';
          var dateStr = m.created_at  ? '<br><small>' + escHtml(m.created_at) + '</small>' : '';
          L.marker([m.lat, m.lng], { icon: icon })
           .bindPopup('<strong>' + escHtml(ucFirst(m.type)) + '</strong>' + desc + dateStr)
           .addTo(markerLayer);
        });
      })
      .catch(function () { /* silent — map stays with prior data */ });
  }

  loadCommunityData();
  setInterval(loadCommunityData, 5 * 60 * 1000); // auto-refresh every 5 min

  // ── Map sharing toggle ──────────────────────────────────────────────────────
  var sharingChk = document.getElementById('amboat-map-sharing');
  if (sharingChk) {
    sharingChk.addEventListener('change', function () {
      var data = new FormData();
      data.append('action', 'atmyboat_toggle_map_sharing');
      data.append('nonce', this.dataset.nonce);
      data.append('sharing', this.checked ? '1' : '0');
      fetch('<?php echo esc_url( admin_url( 'admin-ajax.php' ) ); ?>', { method: 'POST', body: data });
    });
  }

  // ── Add Marker flow ─────────────────────────────────────────────────────────
  if (!CAN_ADD_MARKER) return;

  var addBtn      = document.getElementById('amboat-add-marker-btn');
  var overlay     = document.getElementById('amboat-marker-overlay');
  var cancelBtn   = document.getElementById('amboat-marker-cancel');
  var submitBtn   = document.getElementById('amboat-marker-submit');
  var coordsEl    = document.getElementById('amboat-marker-coords');
  var statusEl    = document.getElementById('amboat-marker-status');
  var typeEl      = document.getElementById('amboat-marker-type');
  var severityEl  = document.getElementById('amboat-marker-severity');
  var descEl      = document.getElementById('amboat-marker-desc');

  if (!addBtn || !overlay) return;

  var pendingLat = null;
  var pendingLng = null;
  var pickingMode = false;
  var pickCursor  = null;

  function openOverlay() {
    pendingLat = null;
    pendingLng = null;
    coordsEl.textContent = 'Click on the map to set location…';
    submitBtn.disabled = true;
    submitBtn.style.opacity = '.5';
    statusEl.textContent = '';
    descEl.value = '';
    overlay.style.display = 'flex';
    overlay.setAttribute('aria-hidden', 'false');
    pickingMode = true;
    map.getContainer().style.cursor = 'crosshair';
  }

  function closeOverlay() {
    overlay.style.display = 'none';
    overlay.setAttribute('aria-hidden', 'true');
    pickingMode = false;
    map.getContainer().style.cursor = '';
    if (pickCursor) { map.removeLayer(pickCursor); pickCursor = null; }
  }

  addBtn.addEventListener('click', openOverlay);
  cancelBtn.addEventListener('click', closeOverlay);

  // Close on backdrop click
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeOverlay();
  });

  // Map click — pick coordinates
  map.on('click', function (e) {
    if (!pickingMode) return;
    pendingLat = e.latlng.lat;
    pendingLng = e.latlng.lng;
    coordsEl.textContent = 'Location: ' +
      pendingLat.toFixed(4) + '°, ' + pendingLng.toFixed(4) + '°';
    submitBtn.disabled = false;
    submitBtn.style.opacity = '1';
    // Visual pin
    if (pickCursor) map.removeLayer(pickCursor);
    pickCursor = L.circleMarker([pendingLat, pendingLng], {
      radius: 8, fillColor: '#e53935', color: '#fff', weight: 2, fillOpacity: 1
    }).addTo(map);
  });

  submitBtn.addEventListener('click', function () {
    if (pendingLat === null) return;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';
    statusEl.textContent = '';

    fetch(MARKER_WRITE_URL, {
      method  : 'POST',
      headers : {
        'Content-Type'  : 'application/json',
        'Authorization' : 'Bearer ' + APP_TOKEN
      },
      body: JSON.stringify({
        lat         : pendingLat,
        lon         : pendingLng,
        marker_type : typeEl.value,
        severity    : severityEl.value,
        description : descEl.value.trim()
      })
    })
    .then(function (r) { return r.json(); })
    .then(function (res) {
      if (res.success) {
        closeOverlay();
        loadCommunityData(); // refresh map immediately
      } else {
        statusEl.textContent = res.error || 'Submit failed. Try again.';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Marker';
      }
    })
    .catch(function () {
      statusEl.textContent = 'Network error. Try again.';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Marker';
    });
  });

  // ── Utilities ────────────────────────────────────────────────────────────────
  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function ucFirst(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  }

}());
</script>

<?php get_footer(); ?>
