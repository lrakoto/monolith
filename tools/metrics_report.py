#!/usr/bin/env python3
"""Read private aggregate metrics through the existing Cloudflare login."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'page_view': 'Site / scene visits', 'project_click': 'Project button clicks', 'project_view': 'Project details opened',
          'game_launch': 'Game launches', 'live_click': 'Other project link clicks', 'resume_click': 'Résumé clicks',
          'contact_click': 'Email-contact clicks', 'portfolio_click': 'WordPress → portfolio clicks'}

def report(days=30, output=None, usage=None):
    start = (datetime.now(timezone.utc).date() - timedelta(days=days - 1)).isoformat()
    query = "SELECT day,scene,event,project,count FROM metrics_daily WHERE day >= '" + start + "' ORDER BY day,scene,event,project"
    proc = subprocess.run(['wrangler', 'd1', 'execute', 'signals', '--remote', '--json', '--command', query], cwd=ROOT/'worker', text=True, capture_output=True, timeout=45)
    if proc.returncode:
        raise RuntimeError('Cloudflare report could not be read. Check wrangler login.\n' + proc.stderr)
    result = json.loads(proc.stdout)[0]
    rows = result['results']
    if usage is not None:
        usage['rows_read'] = result.get('meta', {}).get('rows_read')
    total = Counter(); scopes = {}; projects = {}; daily = {}
    for row in rows:
        total[row['event']] += row['count']
        scopes.setdefault(row['scene'], Counter())[row['event']] += row['count']
        daily.setdefault(row['day'], Counter())[row['event']] += row['count']
        if row['project']:
            projects.setdefault(row['project'], Counter())[row['event']] += row['count']
    print('Anonymous activity, ' + start + ' through today (UTC)')
    for key,label in LABELS.items(): print(f'{label}: {total[key]}')
    def table(headers, records):
        return '<table><thead><tr>'+''.join('<th>'+html.escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in record)+'</tr>' for record in records)+'</tbody></table>'
    stats = ''.join('<div class="stat"><strong>'+str(total[k])+'</strong><span>'+v+'</span></div>' for k,v in LABELS.items())
    body = '<h1>Portfolio &amp; website activity</h1><p>'+start+' through today · UTC · generated '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')+'</p><div class="stats">'+stats+'</div>'
    body += '<h2>By site and scene</h2>'+table(['Site / scene',*LABELS.values()], [[name,*[counts[k] for k in LABELS]] for name,counts in sorted(scopes.items())])
    body += '<h2>Project interest</h2>'+table(['Project','Project buttons','Details opened','Game launches','Other links'], [[name,counts['project_click'],counts['project_view'],counts['game_launch'],counts['live_click']] for name,counts in sorted(projects.items(),key=lambda x:sum(x[1].values()),reverse=True)])
    body += '<h2>Daily activity</h2>'+table(['Date',*LABELS.values()], [[day,*[counts[k] for k in LABELS]] for day,counts in sorted(daily.items(),reverse=True)])
    body += '<p class="note">Counts begin at installation. Each event and project counts once per site or scene per tab session. Visits are not unique people, and a person can appear in multiple scenes. Storage-disabled browsers deduplicate only until reload. Clicks do not confirm downloads, emails sent, or leads. Privacy opt-outs, blockers and delivery failures can reduce counts; bots can inflate them. No cross-site conversion rate is inferred.</p><p class="note">Only UTC day, site/scene, event, project slug and total are stored. No cookie IDs, IP addresses, full URLs, referrers or form contents are stored by this metrics code. Reports require your Cloudflare login and are not published.</p>'
    if not rows: body += '<p>No activity has been recorded yet.</p>'
    doc = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>305 activity report</title><style>body{font:15px/1.6 system-ui;background:#101b1a;color:#e4ebe6;margin:0;padding:40px;max-width:1400px}h1{font-size:32px}h2{margin-top:36px}.stats{display:flex;flex-wrap:wrap;gap:16px}.stat{background:#20312e;padding:18px;min-width:145px;flex:1}.stat strong{display:block;font-size:32px}.stat span,.note{color:#b9c9c2}table{border-collapse:collapse;width:100%;display:block;overflow-x:auto}th,td{text-align:left;padding:10px 14px;border-bottom:1px solid #344740;white-space:nowrap}th{color:#b9c9c2}.note{max-width:95ch;font-size:13px}</style>'+body+'</html>'
    output = Path(output) if output else ROOT/'artifacts/metrics/report.html'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(doc)
    print('Private report:',output)
    return rows

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days',type=int,default=30)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not 1 <= args.days <= 366:parser.error('--days must be between 1 and 366')
    report(args.days,args.output)
