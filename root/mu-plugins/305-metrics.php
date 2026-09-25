<?php
/**
 * Plugin Name: 305 Anonymous Metrics
 * Description: Small first-party activity counts with no visitor identifiers.
 */
if (!defined('ABSPATH')) { exit; }
add_action('wp_enqueue_scripts', function () {
    // exclude editing and signed-in visits from the public-site totals.
    if (is_admin() || is_user_logged_in() || is_preview()) { return; }
    wp_enqueue_script('305-anonymous-metrics', home_url('/portfolio/assets/metrics.js'), array(), '20260925', true);
});

add_action('admin_menu', function () {
    add_dashboard_page('305 Metrics', '305 Metrics', 'manage_options', '305-metrics', 'studios_metrics_page');
});
add_action('wp_ajax_studios_metrics_report', function () {
    if (!current_user_can('manage_options')) { wp_send_json_error(null, 403); }
    check_ajax_referer('studios_metrics_report');
    $days = isset($_POST['days']) && is_scalar($_POST['days']) ? absint($_POST['days']) : 30;
    if (!in_array($days, array(7, 30, 90), true)) { wp_send_json_error(null, 400); }
    $cache_key = 'studios_metrics_report_v2_' . $days;
    $data = get_transient($cache_key);
    if ($data === false) {
        $key_file = __DIR__ . '/305-metrics-key.php';
        if (!is_file($key_file)) { wp_send_json_error(null, 503); }
        $key = require $key_file;
        // share a short cache across admins and devices; no polling runs on a schedule.
        $budget = get_option('studios_metrics_read_budget', array());
        $day = gmdate('Y-m-d');
        if (!isset($budget['day']) || $budget['day'] !== $day) { $budget = array('day'=>$day, 'reads'=>0); }
        if (($budget['reads'] ?? 0) + 40000 > 1000000) { wp_send_json_error(array('message'=>'Daily refresh limit reached. Updates resume tomorrow UTC.'), 429); }
        $budget['reads'] = ($budget['reads'] ?? 0) + 40000;
        update_option('studios_metrics_read_budget', $budget, false);
        $response = wp_remote_get(add_query_arg('days', $days, home_url('/api/metrics-report')), array('timeout'=>15, 'headers'=>array('Authorization'=>'Bearer ' . $key)));
        if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) { wp_send_json_error(null, 503); }
        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($data) || !isset($data['rows'])) { wp_send_json_error(null, 503); }
        $budget['reads'] -= 40000 - min(40000, max(0, intval($data['reads'] ?? 40000)));
        update_option('studios_metrics_read_budget', $budget, false);
        set_transient($cache_key, $data, 60);
    }
    wp_send_json_success($data);
});
function studios_metrics_page() {
    if (!current_user_can('manage_options')) { return; }
    ?>
    <div class="wrap" id="studios-metrics"><h1>Portfolio &amp; website activity</h1>
    <p><label for="metrics-range">Date range </label><select id="metrics-range"><option value="7">Last 7 days</option><option value="30" selected>Last 30 days</option><option value="90">Last 90 days</option></select></p>
    <p id="metrics-status" role="status">Loading activity…</p>
    <div id="metrics-content"></div>
    <p>Anonymous activity, not unique people. Each action counts once per site or scene, project and tab session. Clicks do not confirm inquiries or downloads. Counts began when tracking was installed. Game launches count Play Beta link clicks, not completed plays. Separate launch tracking began September 25, 2026; older clicks remain under other project links.</p>
    <p>Refreshes every 60 seconds while visible. Pauses when hidden. Reports share a cache across devices and a daily database read limit.</p></div>
    <style>#studios-metrics{max-width:1400px}#studios-metrics .stats{display:flex;gap:12px;flex-wrap:wrap}#studios-metrics .stat{background:#fff;padding:18px;flex:1;min-width:140px}#studios-metrics strong{display:block;font-size:28px}#studios-metrics .table-wrap{overflow:auto}#studios-metrics table{border-collapse:collapse;width:100%;background:white}#studios-metrics th,#studios-metrics td{padding:12px;text-align:left;border-bottom:1px solid #ddd;white-space:nowrap}</style>
    <script>
    (() => {
      const labels = {page_view:'Site / scene visits',project_click:'Project buttons',project_view:'Details opened',live_click:'Other project link clicks',game_launch:'Game launches',resume_click:'Résumé clicks',contact_click:'Contact clicks',portfolio_click:'Website to portfolio'};
      const names = {website:'Website',temple:'Temple',redwoods:'Redwoods',forest:'Forest',shop:'Gundry MD',autodex:'AutoDex',aero:'AERO',studio:'305 Studios',games:'Game field logs',pyxel:'Pyxel Game',blockshooter:'Block Shooter',newegg:'Newegg Email Campaigns',manhattan:'Manhattan Funding',tranomics:'Tranomics',godayone:'Go Day One',alliance:'Alliance Française',lewislaw:'Lewis Law',erikka:'Erikka Dawn',cards:'Flavor Cards',moomenu:'Moodaepo Menu',reactor:'Reactor Branding',teastory:'Teastory Packaging',shoboomenu:'Shoboo Menu',ara:'ARA Campaign',pilot:'Light Pulse Campaign',moolunch:'Email Campaigns',starke:'Starke Branding',sean:'Sean Website',spatel:'Spatel Website',cot:'COT Website'};
      const container = document.getElementById('metrics-content'), status = document.getElementById('metrics-status');
      function element(tag,text) {const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;}
      function table(title,heading,groups,keys) {
        container.append(element('h2',title));const wrap=element('div');wrap.className='table-wrap';const t=element('table'),head=element('tr');
        [heading,...keys.map(k=>labels[k])].forEach(x=>head.append(element('th',x)));t.append(head);
        Object.entries(groups).forEach(([name,counts])=>{const row=element('tr');[names[name]||name,...keys.map(k=>counts[k]||0)].forEach(x=>row.append(element('td',x)));t.append(row)});wrap.append(t);container.append(wrap);
      }
      const range = document.getElementById('metrics-range');
      let busy=false,last=0,stopped=false;
      async function refresh() {
        if(document.hidden||busy||stopped||Date.now()-last<60000)return;busy=true;range.disabled=true;last=Date.now();
        try {
          const params=new URLSearchParams({action:'studios_metrics_report',days:range.value,_ajax_nonce:<?php echo wp_json_encode(wp_create_nonce('studios_metrics_report')); ?>});
          const response=await fetch(ajaxurl,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:params});
          if(response.status===429){stopped=true;throw new Error('Daily refresh limit reached. Reopen tomorrow UTC.');}
          if(response.status===403){stopped=true;throw new Error('Session expired. Reload and sign in again.');}
          if(!response.ok)throw new Error('Could not refresh. Retrying in 60 seconds.');
          const result=await response.json();if(!result.success)throw new Error('Report unavailable.');
          const totals={},scenes={},projects={},days={};
          for(const row of result.data.rows){totals[row.event]=(totals[row.event]||0)+row.count;for(const [group,key] of [[scenes,row.scene],[days,row.day],[projects,row.project]]){if(!key)continue;group[key]||={};group[key][row.event]=(group[key][row.event]||0)+row.count;}}
          container.replaceChildren();const stats=element('div');stats.className='stats';
          for(const [key,label] of Object.entries(labels)){const card=element('div');card.className='stat';card.append(element('strong',totals[key]||0),element('span',label));stats.append(card);}container.append(stats);
          table('By site and scene','Site / scene',scenes,Object.keys(labels));table('Project interest','Project',projects,['project_click','project_view','game_launch','live_click']);table('Daily activity (UTC)','Date',Object.fromEntries(Object.entries(days).reverse()),Object.keys(labels));
          status.textContent='Last '+result.data.days+' days · Updated '+new Date(result.data.updated).toLocaleString();
        }catch(error){status.textContent=error.message;}finally{busy=false;range.disabled=false;}
      }
      range.addEventListener('change',()=>{last=0;refresh();});
      refresh();setInterval(refresh,60000);document.addEventListener('visibilitychange',refresh);
    })();
    </script>
    <?php
}
