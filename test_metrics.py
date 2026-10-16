import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import metrics_dashboard
import metrics_report

class MetricsTests(unittest.TestCase):
    def test_client_and_endpoint(self):
        subprocess.run(['node', 'tools/test_metrics.mjs'], cwd=ROOT, check=True)

    def test_schema_aggregates_and_rejects_unknown_events(self):
        db=sqlite3.connect(':memory:')
        db.executescript((ROOT/'worker/metrics-schema.sql').read_text())
        sql="INSERT INTO metrics_daily VALUES('2026-09-24','website','live_click','aero',1) ON CONFLICT(day,scene,event,project) DO UPDATE SET count=count+1"
        db.execute(sql); db.execute(sql)
        self.assertEqual(db.execute('SELECT count FROM metrics_daily').fetchone()[0],2)
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO metrics_daily VALUES('2026-09-24','website','unknown','',1)")

    def test_game_migration_preserves_existing_counts(self):
        db = sqlite3.connect(':memory:')
        db.execute("CREATE TABLE metrics_daily(day TEXT,scene TEXT,event TEXT,project TEXT,count INTEGER,PRIMARY KEY(day,scene,event,project))")
        db.execute("INSERT INTO metrics_daily VALUES('2026-09-24','temple','live_click','pyxel',9)")
        db.executescript((ROOT/'worker/metrics-games-migration.sql').read_text())
        self.assertEqual(db.execute('SELECT count FROM metrics_daily').fetchone()[0],9)
        db.execute("INSERT INTO metrics_daily VALUES('2026-09-25','games','game_launch','pyxel',1)")
        self.assertEqual(db.execute('SELECT SUM(count) FROM metrics_daily').fetchone()[0],10)

    def test_artdex_migration_preserves_counts_and_restricts_new_activity(self):
        db = sqlite3.connect(':memory:')
        db.executescript((ROOT/'worker/metrics-games-migration.sql').read_text().split('INSERT INTO')[0].replace('metrics_daily_v2', 'metrics_daily'))
        old_rows = [('2026-09-24', 'temple', 'live_click', 'pyxel', 9),
                    ('2026-09-25', 'games', 'game_launch', 'pyxel', 4),
                    ('2026-10-14', 'website', 'page_view', '', 107)]
        db.executemany('INSERT INTO metrics_daily VALUES(?,?,?,?,?)', old_rows)
        db.execute('CREATE TABLE metrics_limit(id INTEGER PRIMARY KEY,minute INTEGER,count INTEGER)')
        db.execute('INSERT INTO metrics_limit VALUES(1,123,5)')
        db.executescript((ROOT/'worker/metrics-artdex-migration.sql').read_text())
        self.assertEqual(db.execute('SELECT * FROM metrics_daily ORDER BY day').fetchall(), old_rows)
        self.assertEqual(db.execute('SELECT * FROM metrics_daily_pre_artdex ORDER BY day').fetchall(), old_rows)
        self.assertEqual(db.execute('SELECT * FROM metrics_limit').fetchall(), [(1,123,5)])
        for event in ('page_view', 'asset_view', 'asset_download', 'filter_use', 'asset_save'):
            db.execute("INSERT INTO metrics_daily VALUES('2026-10-15','artdex',?,'',1)", (event,))
        for scene,event,project in [('website','asset_view',''), ('temple','filter_use',''),
                                    ('artdex','asset_save','asset-id'), ('artdex','project_click','aero'),
                                    ('artdex','unknown','')]:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO metrics_daily VALUES('2026-10-15',?,?,?,1)", (scene,event,project))
        fresh = sqlite3.connect(':memory:')
        fresh.executescript((ROOT/'worker/metrics-schema.sql').read_text())
        migrated_sql = db.execute("SELECT sql FROM sqlite_master WHERE name='metrics_daily'").fetchone()[0]
        fresh_sql = fresh.execute("SELECT sql FROM sqlite_master WHERE name='metrics_daily'").fetchone()[0]
        self.assertEqual(migrated_sql.replace('"',''), fresh_sql.replace('"',''))

    def test_dashboard_caches_and_enforces_budget(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(metrics_dashboard,'ROOT',Path(tmp)):
            def report(days,usage):
                usage['rows_read']=10
                p=Path(tmp)/'artifacts/metrics/report.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('report')
            cache=metrics_dashboard.ReportCache(30)
            with patch.object(metrics_dashboard,'report',side_effect=report) as query:
                self.assertEqual(cache.get(),b'report');self.assertEqual(cache.get(),b'report')
                self.assertEqual(query.call_count,1)
                budget=json.loads(cache.budget.read_text());self.assertEqual(budget['reserved_reads'],10)
                budget['reserved_reads']=1_000_000;cache.budget.write_text(json.dumps(budget));cache.at=metrics_dashboard.time.monotonic()-61
                with self.assertRaises(RuntimeError):cache.get()
                self.assertEqual(query.call_count,1)

    def test_local_report_separates_artdex_from_portfolio(self):
        rows = [dict(day='2026-10-15', scene='website', event='page_view', project='', count=3),
                dict(day='2026-10-15', scene='artdex', event='page_view', project='', count=11),
                dict(day='2026-10-15', scene='artdex', event='asset_download', project='', count=7)]
        response = type('Result', (), {'returncode':0, 'stdout':json.dumps([{'results':rows}])})()
        with tempfile.TemporaryDirectory() as tmp, patch.object(metrics_report.subprocess,'run',return_value=response), patch('builtins.print'):
            output = Path(tmp)/'report.html'
            metrics_report.report(output=output)
            body = output.read_text()
        artdex, portfolio = body.split('<h2>Portfolio &amp; website</h2>')
        self.assertIn('<strong>11</strong><span>Artdex visits</span>', artdex)
        self.assertIn('<strong>7</strong><span>Download clicks</span>', artdex)
        self.assertIn('<strong>3</strong><span>Site / scene visits</span>', portfolio)
        self.assertNotIn('<strong>14</strong>', portfolio)
