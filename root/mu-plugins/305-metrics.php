<?php
/**
 * Plugin Name: 305 Anonymous Metrics
 * Description: Small first-party activity counts with no visitor identifiers.
 */
if (!defined('ABSPATH')) { exit; }
add_action('wp_enqueue_scripts', function () {
    // exclude editing and signed-in visits from the public-site totals.
    if (is_admin() || is_user_logged_in() || is_preview()) { return; }
    wp_enqueue_script('305-anonymous-metrics', home_url('/portfolio/assets/metrics.js'), array(), '20260924', true);
});
