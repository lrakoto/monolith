const cache = new Map();
export async function report(request, env) {
  const headers = {'Content-Type':'application/json', 'Cache-Control':'no-store'};
  if (request.method !== 'GET') return new Response(null, {status:405, headers});
  if (!env.METRICS_REPORT_KEY || request.headers.get('Authorization') !== 'Bearer ' + env.METRICS_REPORT_KEY) return new Response(null, {status:403, headers});
  const raw = new URL(request.url).searchParams.get('days') || '30';
  if (!['7','30','90'].includes(raw)) return new Response(null, {status:400, headers});
  const days = Number(raw);
  try {
    let cached = cache.get(days);
    if (!cached || Date.now() - cached.at >= 60000) {
      const start = new Date(Date.now() - (days - 1) * 86400000).toISOString().slice(0,10);
      const {results, meta} = await env.DB.prepare('SELECT day,scene,event,project,count FROM metrics_daily WHERE day >= ? ORDER BY day,scene,event,project LIMIT 40000').bind(start).all();
      cached = {body:JSON.stringify({start, days, updated:new Date().toISOString(), rows:results, reads:meta?.rows_read ?? 40000}),at:Date.now()};
      cache.set(days,cached);
    }
    return new Response(cached.body, {headers});
  } catch (_) { return new Response(null, {status:503, headers}); }
}
