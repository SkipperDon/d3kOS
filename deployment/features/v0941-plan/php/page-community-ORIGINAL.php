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
      </div>
    </section>

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

    </div><!-- .amboat-community-grid -->

  </div>
</main>

<script>
// Map sharing toggle
document.getElementById('amboat-map-sharing').addEventListener('change', function() {
  const data = new FormData();
  data.append('action', 'atmyboat_toggle_map_sharing');
  data.append('nonce', this.dataset.nonce);
  data.append('sharing', this.checked ? '1' : '0');
  fetch('<?php echo esc_url( admin_url( 'admin-ajax.php' ) ); ?>', { method: 'POST', body: data });
});
</script>

<?php get_footer(); ?>
