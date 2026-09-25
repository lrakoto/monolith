/* counts describe interest, not people. no identifiers leave the browser. */
(() => {
  'use strict';
  const scenes = {'/portfolio/':'temple','/portfolio/index.html':'temple','/portfolio/temple.html':'temple','/portfolio/redwoods.html':'redwoods','/portfolio/monolith.html':'redwoods','/portfolio/forest.html':'forest','/portfolio/pyxel/':'games','/portfolio/pyxel/index.html':'games','/portfolio/blockshooter/':'games','/portfolio/blockshooter/index.html':'games'};
  const scene = scenes[location.pathname] || (!location.pathname.startsWith('/portfolio/') ? 'website' : null);
  if (location.hostname !== 'threeohfivestudios.com' || !scene || navigator.webdriver || navigator.globalPrivacyControl || navigator.doNotTrack === '1') return;
  const seen = new Set();
  function track(event, project = '') {
    if (document.visibilityState !== 'visible') return;
    const key = 'portfolio-metric:' + scene + ':' + event + ':' + project;
    if (seen.has(key)) return;
    try { if (sessionStorage.getItem(key)) return; } catch (_) {}
    const body = JSON.stringify({event, scene, project});
    let sent = false;
    try { sent = navigator.sendBeacon('/api/events', new Blob([body], {type:'application/json'})); } catch (_) {}
    if (!sent) {
      try { fetch('/api/events', {method:'POST',body,headers:{'Content-Type':'application/json'},keepalive:true,credentials:'omit'}).catch(() => {}); } catch (_) {}
    }
    seen.add(key);
    try { sessionStorage.setItem(key, '1'); } catch (_) {}
  }
  window.portfolioMetric = track;
  const rootProjects = {'/recent-work-autodex/':'autodex','/recent-work-gundry-md/':'shop','/recent-work-aero/':'aero','/recent-work-305-studios/':'studio'};
  const visit = () => {
    track('page_view');
    if (scene === 'website' && rootProjects[location.pathname]) track('project_view', rootProjects[location.pathname]);
  };
  visit();
  document.addEventListener('visibilitychange', visit);
  function click(event) {
    if (!event.isTrusted || (event.type === 'auxclick' && event.button !== 1)) return;
    const link = event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    const local = url.origin === location.origin;
    if (link.dataset.metricEvent === 'game_launch' && ['pyxel','blockshooter'].includes(link.dataset.metricProject)) track('game_launch', link.dataset.metricProject);
    else if (url.protocol === 'mailto:' || (local && url.pathname.startsWith('/cdn-cgi/l/email-protection'))) track('contact_click');
    else if (/Lova_Resume_2026\.pdf$/.test(url.pathname)) track('resume_click');
    else if (scene === 'website') {
      if (local && rootProjects[url.pathname]) track('project_click', rootProjects[url.pathname]);
      else if (local && url.pathname.startsWith('/portfolio/')) track('portfolio_click');
      else if (url.hostname === 'autodx.io') track('live_click', 'autodex');
      else if (['gundrymd.com','www.gundrymd.com'].includes(url.hostname)) track('live_click', 'shop');
      else if (local && url.pathname.startsWith('/aero/')) track('live_click', 'aero');
    } else if (link.dataset.metricProject) track('live_click', link.dataset.metricProject);
    else if (link.dataset.work && (event.button === 1 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) track('live_click', link.dataset.work);
  }
  document.addEventListener('click', click);
  document.addEventListener('auxclick', click);
})();
