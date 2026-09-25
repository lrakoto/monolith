/* aggregate in place so the database never becomes a visitor history. */
export const PROJECTS = new Set(['studio','autodex','shop','aero','newegg','manhattan','tranomics','godayone','alliance','lewislaw','erikka','cards','moomenu','reactor','teastory','shoboomenu','ara','pilot','moolunch','starke','sean','spatel','cot','pyxel','blockshooter']);
const EVENTS = new Set(['page_view','project_click','project_view','live_click','game_launch','resume_click','contact_click','portfolio_click']);
const SCENES = new Set(['temple','redwoods','forest','website','games']);
const headers = {'cache-control':'no-store'};
const reply = status => new Response(null, {status, headers});
export async function metrics(request, env) {
  if (request.method !== 'POST') return reply(405);
  if (request.headers.get('Origin') !== 'https://threeohfivestudios.com') return reply(403);
  if (request.headers.get('Sec-GPC') === '1' || request.headers.get('DNT') === '1') return reply(204);
  if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return reply(415);
  let input;
  try {
    const reader = request.body?.getReader();
    if (!reader) return reply(400);
    let size = 0, text = ''; const decoder = new TextDecoder();
    while (true) {
      const {done,value} = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > 512) { await reader.cancel(); return reply(413); }
      text += decoder.decode(value, {stream:true});
    }
    input = JSON.parse(text + decoder.decode());
  } catch (_) { return reply(400); }
  if (!input || typeof input !== 'object' || Array.isArray(input)) return reply(400);
  const {event,scene,project = ''} = input;
  if (!EVENTS.has(event) || !SCENES.has(scene)) return reply(400);
  const projectEvent = event === 'project_click' || event === 'project_view' || event === 'live_click' || event === 'game_launch';
  if (event === 'game_launch' && !['pyxel','blockshooter'].includes(project)) return reply(400);
  if (projectEvent ? !PROJECTS.has(project) : project !== '') return reply(400);
  try {
    /* one rolling bucket limits spam without tracking callers; origin checks
       reduce accidental submissions but cannot authenticate a visitor. */
    const minute = Math.floor(Date.now() / 60000);
    const limit = await env.DB.prepare(`INSERT INTO metrics_limit (id, minute, count) VALUES (1, ?, 1)
      ON CONFLICT(id) DO UPDATE SET minute=excluded.minute,
      count=CASE WHEN metrics_limit.minute=excluded.minute THEN metrics_limit.count+1 ELSE 1 END
      WHERE metrics_limit.minute<>excluded.minute OR metrics_limit.count<240 RETURNING count`).bind(minute).first();
    if (!limit) return reply(429);
    await env.DB.prepare(`INSERT INTO metrics_daily (day, scene, event, project, count) VALUES (?, ?, ?, ?, 1)
      ON CONFLICT(day,scene,event,project) DO UPDATE SET count=count+1`)
      .bind(new Date().toISOString().slice(0,10),scene,event,project).run();
    return reply(204);
  } catch (_) { return reply(503); }
}
