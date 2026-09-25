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
