let cached = null;
let cachedAt = 0;
export async function report(request, env) {
  const headers = {'Content-Type':'application/json', 'Cache-Control':'no-store'};
  if (request.method !== 'GET') return new Response(null, {status:405, headers});
  if (!env.METRICS_REPORT_KEY || request.headers.get('Authorization') !== 'Bearer ' + env.METRICS_REPORT_KEY) return new Response(null, {status:403, headers});
  try {
    if (!cached || Date.now() - cachedAt >= 60000) {
      const start = new Date(Date.now() - 29 * 86400000).toISOString().slice(0,10);
      const {results, meta} = await env.DB.prepare('SELECT day,scene,event,project,count FROM metrics_daily WHERE day >= ? ORDER BY day,scene,event,project LIMIT 10000').bind(start).all();
      cached = JSON.stringify({start, updated:new Date().toISOString(), rows:results, reads:meta?.rows_read ?? 10000});
      cachedAt = Date.now();
    }
    return new Response(cached, {headers});
  } catch (_) { return new Response(null, {status:503, headers}); }
}
