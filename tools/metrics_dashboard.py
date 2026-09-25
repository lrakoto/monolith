#!/usr/bin/env python3
"""Private localhost dashboard. Open while needed; no background polling."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import argparse
import json
import secrets
import time
from datetime import datetime, timezone
from metrics_report import report, ROOT

PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>305 live metrics</title><style>body{margin:0;background:#101b1a;color:#e4ebe6;font:15px system-ui}header{padding:16px 40px}iframe{width:100%;height:calc(100vh - 64px);border:0}</style><header id="status">Loading private metrics…</header><iframe title="Activity report"></iframe><script>
const status = document.getElementById('status');
let busy = false, last = 0;
async function refresh() {
  if (document.hidden || busy || Date.now() - last < 60000) return;
  busy = true; last = Date.now();
  try {
    const response = await fetch('report', {cache:'no-store'});
    if (!response.ok) throw new Error('Refresh unavailable');
    document.querySelector('iframe').srcdoc = await response.text();
    status.textContent = 'Updated ' + new Date().toLocaleTimeString() + ' · refreshes every 60 seconds while visible';
  } catch (_) { status.textContent = 'Could not refresh. Last successful report remains below. Retrying in 60 seconds.'; }
  finally { busy = false; }
}
refresh(); setInterval(refresh, 60000);
document.addEventListener('visibilitychange', refresh);
</script></html>'''

class ReportCache:
    def __init__(self, days):
        self.days = days
        self.at = 0
        self.body = None
        self.budget = ROOT / 'artifacts/metrics/read-budget.json'

    def get(self):
        if self.body is not None and time.monotonic() - self.at < 60:
            return self.body
        today = datetime.now(timezone.utc).date().isoformat()
        try:
            budget = json.loads(self.budget.read_text())
        except FileNotFoundError:
            budget = {'day': today, 'reserved_reads': 0}
        if budget['day'] != today:
            budget = {'day': today, 'reserved_reads': 0}
        # reserve an upper bound before querying, including failed attempts.
        # allowlisted events and projects bound each day's aggregate rows.
        reserve = self.days * 4 * (26 * 3 + 4)
        if budget['reserved_reads'] + reserve > 1_000_000:
            raise RuntimeError('Daily dashboard read budget reached; resumes tomorrow UTC.')
        budget['reserved_reads'] += reserve
        self.budget.parent.mkdir(parents=True, exist_ok=True)
        self.budget.write_text(json.dumps(budget))
        usage = {}
        report(self.days, usage=usage)
        actual = usage.get('rows_read')
        if isinstance(actual, int) and 0 <= actual < reserve:
            budget['reserved_reads'] -= reserve - actual
            self.budget.write_text(json.dumps(budget))
        self.body = (ROOT / 'artifacts/metrics/report.html').read_bytes()
        self.at = time.monotonic()
        return self.body


def serve(port=5198, days=30):
    cache = ReportCache(days)
    token = secrets.token_urlsafe(24)
    prefix = '/' + token + '/'
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # the random local path and host check prevent other websites from
            # turning the local login into an accessible metrics proxy.
            if self.headers.get('Host') != f'127.0.0.1:{port}' or not self.path.startswith(prefix):
                self.send_error(404); return
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                self.send_error(403); return
            path = self.path[len(prefix):]
            if path == '':
                body = PAGE.encode()
            elif path == 'report':
                try: body = cache.get()
                except Exception as error:
                    print('Report refresh failed:', type(error).__name__, flush=True)
                    self.send_error(503); return
            else:
                self.send_error(404); return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Frame-Options', 'SAMEORIGIN')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *args): pass
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'Private metrics: http://127.0.0.1:{port}{prefix}', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5198)
    parser.add_argument('--days', type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.days <= 366: parser.error('days must be 1 to 366')
    serve(args.port, args.days)
