import { report } from './report.js';
import { metrics } from './metrics.js';

/* signals — the tally under the footer of the portfolio.

   The page is one static file on shared hosting, so there is nowhere on the
   origin to keep a number. This runs at the edge instead, and only on /api/*.
   The route deliberately never covers the document: a worker in front of the
   page is a way to take the whole site down, and a counter is not worth that
   risk. If this is broken or gone, the page loses a footer row and nothing
   else.

   Nothing here identifies anyone. A signal is a kind, an optional name the
   caller chose for itself, and a timestamp — no address, no headers, no
   fingerprint. The point is a guestbook, and a guestbook that recorded its
   visitors would be a different and worse thing. */

/* a flood cap rather than a per-caller rate limit. per-caller means keeping
   something about the caller, and that is the one thing this will not do. */
const MAX_PER_MINUTE = 60;

const HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'access-control-allow-origin': '*',
  'cache-control': 'no-store'
};

const json = (body, status = 200) =>
  new Response(JSON.stringify(body, null, 2) + '\n', { status, headers: HEADERS });

async function tally(env) {
  const { results } = await env.DB
    .prepare('SELECT kind, COUNT(*) AS c FROM signals GROUP BY kind').all();
  const signals = { hello: 0, helpful: 0, unhelpful: 0 };
  for (const row of results || []) {
    if (row.kind in signals) signals[row.kind] = row.c;
  }
  signals.total = signals.hello + signals.helpful + signals.unhelpful;

  const first = await env.DB.prepare('SELECT MIN(ts) AS t FROM signals').first();
  return {
    signals: signals,
    first: first && first.t ? new Date(first.t * 1000).toISOString() : null
  };
}

async function record(env, kind, agent) {
  const since  = Math.floor(Date.now() / 1000) - 60;
  const recent = await env.DB
    .prepare('SELECT COUNT(*) AS c FROM signals WHERE ts > ?').bind(since).first();
  if (recent && recent.c >= MAX_PER_MINUTE) return false;

  /* the name is whatever the caller says it is, kept short and stripped of
     anything that is not plainly a name, because it is displayed */
  const raw  = agent ? String(agent).slice(0, 60).replace(/[^\w .,'\-]/g, '').trim() : '';
  await env.DB
    .prepare('INSERT INTO signals (kind, agent, ts) VALUES (?, ?, ?)')
    .bind(kind, raw || null, Math.floor(Date.now() / 1000)).run();
  return true;
}

export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';

    if (path === '/api/metrics-report') return report(request, env);

    if (path === '/api/events') return metrics(request, env);

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: { ...HEADERS, 'access-control-allow-methods': 'GET, POST, OPTIONS' }
      });
    }
    if (request.method !== 'GET' && request.method !== 'POST') {
      return json({ error: 'use GET or POST' }, 405);
    }

    let recorded;
    try {
      if (path === '/api/hello') {
        recorded = await record(env, 'hello', url.searchParams.get('agent'));
      } else if (path === '/api/signal') {
        const h = (url.searchParams.get('helpful') || '').toLowerCase();
        if (h !== 'yes' && h !== 'no') {
          return json({ error: 'pass helpful=yes or helpful=no' }, 400);
        }
        recorded = await record(env, h === 'yes' ? 'helpful' : 'unhelpful',
                                url.searchParams.get('agent'));
      } else if (path !== '/api/tally') {
        return json({
          error: 'not found',
          endpoints: {
            'GET /api/tally': 'the guestbook counts',
            'GET /api/hello?agent=': 'say you came by',
            'GET /api/signal?helpful=yes|no&agent=': 'say whether it was any use'
          }
        }, 404);
      }

      const body = await tally(env);
      if (recorded !== undefined) {
        body.recorded = recorded;
        if (!recorded) body.note = 'not recorded: more than a minute’s worth of signals arrived at once';
      }
      body.about = 'Signals are self-reported and unverified — anyone can call these endpoints.';
      return json(body);
    } catch (e) {
      return json({ error: 'the tally is unavailable' }, 500);
    }
  }
};
