import sqlite3
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from system_health_trends_v122 import daily_trends

NOW=datetime(2026,10,23,12,tzinfo=timezone.utc)

class TrendTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.patch=patch('system_health_trends_v122._actor',return_value={'role':'admin'})
        self.patch.start()
    def tearDown(self):
        self.patch.stop();self.db.close()
    def add(self,when,status='ok',state='idle'):
        self.db.execute('CREATE TABLE IF NOT EXISTS system_health_checks (id INTEGER PRIMARY KEY,checked_at TEXT,database_status TEXT,monitor_state TEXT,failure_count INTEGER)')
        self.db.execute('INSERT INTO system_health_checks(checked_at,database_status,monitor_state,failure_count) VALUES(?,?,?,0)',(when.isoformat(),status,state))
    def test_empty_series(self):
        self.assertEqual(sum(r['checks'] for r in daily_trends(self.db,1,now=NOW)),0)
    def test_aggregation(self):
        self.add(NOW-timedelta(hours=2),'warning')
        self.add(NOW-timedelta(hours=3))
        self.add(NOW-timedelta(days=2),'ok','failed')
        rows=daily_trends(self.db,1,days=7,now=NOW)
        self.assertEqual(sum(r['checks'] for r in rows),3)
        self.assertEqual(sum(r['warnings'] for r in rows),2)
    def test_bounds(self):
        self.add(NOW-timedelta(days=7))
        self.add(NOW)
        self.assertEqual(sum(r['checks'] for r in daily_trends(self.db,1,days=7,now=NOW)),1)
    def test_validation(self):
        for days in (0,91,True,1.5):
            with self.assertRaises(ValueError):daily_trends(self.db,1,days=days,now=NOW)
        with self.assertRaises(ValueError):daily_trends(self.db,1,now=datetime.now())
    def test_authorization(self):
        with patch('system_health_trends_v122._actor',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):daily_trends(self.db,1,now=NOW)
