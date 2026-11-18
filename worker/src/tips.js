const WALLET = '0x23178a649a868ff0b8280125982a0fb9e9016164';
const USDC = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913';
const TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const WALLET_TOPIC = '0x' + WALLET.slice(2).padStart(64, '0');
const RPC = 'https://base-rpc.publicnode.com';
const BALANCE_RPC = 'https://base.gateway.tenderly.co';
const FIRST_BLOCK = 51018127; // September 8, 2026 UTC, before the tip jar went live.
const RANGE = 50_000;
const hex = n => '0x' + n.toString(16);

function hexInt(value) {
  if (typeof value !== 'string' || !/^0x[\da-f]+$/i.test(value)) throw new Error('Invalid Base integer');
  return BigInt(value);
}

function formatUSDC(raw) {
  const unit = 1_000_000n;
  const fraction = (raw % unit).toString().padStart(6, '0').replace(/0+$/, '');
  return (raw / unit).toString() + (fraction ? '.' + fraction : '');
}

async function rpc(method, params, url = RPC) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({id: 1, jsonrpc: '2.0', method, params}),
    signal: AbortSignal.timeout(2500)
  });
  if (!response.ok) throw new Error('Base RPC unavailable');
  const data = await response.json();
  if (data.error || data.result == null) throw new Error('Base RPC returned no result');
  return data.result;
}

export function parseTransfer(log, timestamp) {
  const [topic, from, to] = log.topics.map(value => value.toLowerCase());
  if (log.address.toLowerCase() !== USDC || topic !== TOPIC || log.removed ||
      (from !== WALLET_TOPIC && to !== WALLET_TOPIC) ||
      !/^0x[\da-f]{64}$/i.test(log.transactionHash)) {
    throw new Error('Unexpected Base transfer');
  }
  const direction = from === WALLET_TOPIC ? (to === WALLET_TOPIC ? 'self' : 'out') : 'in';
  return {
    hash: log.transactionHash.toLowerCase(),
    index: Number(hexInt(log.logIndex)),
    block: Number(hexInt(log.blockNumber)),
    timestamp: Number(hexInt(timestamp)),
    direction,
    amount: formatUSDC(hexInt(log.data))
  };
}

async function syncTransfers(db) {
  const cursor = await db.prepare("SELECT value FROM meta WHERE key = 'tip_coverage'").first();
  const from = cursor ? JSON.parse(cursor.value).next : FIRST_BLOCK;
  const finalized = await rpc('eth_getBlockByNumber', ['finalized', false]);
  const last = Number(hexInt(finalized.number));
  if (last < from) return;
  const to = Math.min(last, from + RANGE - 1);
  const filter = {address: USDC, fromBlock: hex(from), toBlock: hex(to)};
  const [outgoing, incoming] = await Promise.all([
    rpc('eth_getLogs', [{...filter, topics: [TOPIC, WALLET_TOPIC]}]),
    rpc('eth_getLogs', [{...filter, topics: [TOPIC, null, WALLET_TOPIC]}])
  ]);
  const unique = new Map([...outgoing, ...incoming].map(log => [log.transactionHash + ':' + log.logIndex, log]));
  const timestamps = new Map([[finalized.number, finalized.timestamp]]);
  const inserts = [];
  for (const log of unique.values()) {
    if (!log.blockTimestamp && !timestamps.has(log.blockNumber)) {
      const block = await rpc('eth_getBlockByNumber', [log.blockNumber, false]);
      timestamps.set(log.blockNumber, block.timestamp);
    }
    const transfer = parseTransfer(log, log.blockTimestamp ?? timestamps.get(log.blockNumber));
    if (transfer.block < from || transfer.block > to) throw new Error('Transfer outside requested blocks');
    inserts.push(db.prepare(
      'INSERT OR IGNORE INTO tip_transfers (hash, log_index, block, timestamp, direction, amount) VALUES (?, ?, ?, ?, ?, ?)'
    ).bind(transfer.hash, transfer.index, transfer.block, transfer.timestamp, transfer.direction, transfer.amount));
  }
  const boundary = to === last ? finalized : await rpc('eth_getBlockByNumber', [hex(to), false]);
  const checkpoint = JSON.stringify({next: to + 1, timestamp: Number(hexInt(boundary.timestamp))});
  inserts.push(db.prepare(`
    INSERT INTO meta (key, value) VALUES ('tip_coverage', ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
    WHERE json_extract(excluded.value, '$.next') > json_extract(meta.value, '$.next')
  `).bind(checkpoint));
  await db.batch(inserts);
}

async function readBalance(db) {
  const params = [{to: USDC, data: '0x70a08231' + WALLET_TOPIC.slice(2)}, 'latest'];
  const [raw, baseline] = await Promise.all([
    rpc('eth_call', params).catch(() => rpc('eth_call', params, BALANCE_RPC)),
    db.prepare("SELECT value FROM meta WHERE key = 'tip_baseline_raw'").first()
  ]);
  const balance = hexInt(raw);
  const initial = baseline ? BigInt(baseline.value) : null;
  return {balance: formatUSDC(balance), received: initial === null ? null : formatUSDC(balance > initial ? balance - initial : 0n)};
}

async function load(db) {
  const [balance, sync] = await Promise.allSettled([readBalance(db), syncTransfers(db)]);
  const {results} = await db.prepare(
    'SELECT hash, timestamp, direction, amount FROM tip_transfers ORDER BY block DESC, log_index DESC LIMIT 100'
  ).all();
  const row = await db.prepare("SELECT value FROM meta WHERE key = 'tip_coverage'").first();
  return {
    ...(balance.status === 'fulfilled' ? balance.value : {balance: null, received: null}),
    transfers: results,
    syncedThrough: row ? JSON.parse(row.value).timestamp : null,
    refreshFailed: sync.status === 'rejected'
  };
}

let pending, cached;
export async function tipReport(env) {
  if (cached && Date.now() - cached.at < 60_000) return cached.value;
  if (!pending) {
    pending = load(env.DB).then(value => {
      cached = {value, at: Date.now()};
      return value;
    }).finally(() => { pending = null; });
  }
  return pending;
}
