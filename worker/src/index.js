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
   visitors would be a different and worse thing.

   The tip figure is not stored at all. It is read from Base on demand, so it
   cannot drift from the truth, and anyone who doubts it can ask the chain the
   same question this does. */

const WALLET   = '0x23178a649a868ff0b8280125982a0fb9e9016164';
const USDC     = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'; /* native USDC on Base, per Circle */
/* More than one, and tried in order, because a worker's outbound requests leave
   from shared cloudflare addresses and the public endpoints rate-limit those
   hard. mainnet.base.org answers a laptop instantly and returns 429 "over rate
   limit" to this, every time — which is what the first deploy did, silently.
   Any one of these answering is enough. */
const RPCS = [
  'https://base-rpc.publicnode.com',
  'https://base.llamarpc.com',
  'https://1rpc.io/base',
  'https://mainnet.base.org'
];
const DECIMALS = 6n;   /* confirmed by calling decimals() rather than assumed */

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

/* the isolate outlives a request, so a minute of memory here spares the public
   rpc a call per visitor and costs no storage */
let tipCache = { at: 0, value: null };

async function tips() {
  if (tipCache.value && Date.now() - tipCache.at < 60000) return tipCache.value;

  const body = JSON.stringify({
    jsonrpc: '2.0', id: 1, method: 'eth_call',
    params: [{ to: USDC, data: '0x70a08231' + '0'.repeat(24) + WALLET.slice(2) }, 'latest']
  });

  let usdc = null;
  for (const rpc of RPCS) {
    try {
      const res = await fetch(rpc, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: body
      });
      const j = res.ok ? await res.json() : null;
      if (!j || j.error || !j.result) {
        /* an empty catch here cost an afternoon: the balance simply read null
           and nothing anywhere said why. observability is on, so say it. */
        console.log('tip read: ' + rpc + ' -> ' + res.status
                    + (j && j.error ? ' ' + JSON.stringify(j.error) : ''));
        continue;
      }
      const raw  = BigInt(j.result);
      const unit = 10n ** DECIMALS;
      const frac = (raw % unit).toString().padStart(Number(DECIMALS), '0').replace(/0+$/, '');
      usdc = frac ? (raw / unit) + '.' + frac : String(raw / unit);
      break;
    } catch (e) {
      console.log('tip read: ' + rpc + ' threw ' + (e && e.message ? e.message : String(e)));
    }
  }

  const value = { usdc, wallet: WALLET, asset: 'native USDC', network: 'Base', chainId: 8453 };
  if (usdc !== null) tipCache = { at: Date.now(), value };
  return value;
}

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
            'GET /api/tally': 'the counts, and the tip wallet balance',
            'GET /api/hello?agent=': 'say you came by',
            'GET /api/signal?helpful=yes|no&agent=': 'say whether it was any use'
          }
        }, 404);
      }

      const [counts, tip] = await Promise.all([tally(env), tips()]);
      const body = { ...counts, tips: tip };
      if (recorded !== undefined) {
        body.recorded = recorded;
        if (!recorded) body.note = 'not recorded: more than a minute’s worth of signals arrived at once';
      }
      body.about = 'Signals are self-reported and unverified — anyone can call these endpoints. '
                 + 'The tip figure is the live USDC balance of the wallet on Base, which anyone can check against the chain.';
      return json(body);
    } catch (e) {
      return json({ error: 'the tally is unavailable' }, 500);
    }
  }
};
