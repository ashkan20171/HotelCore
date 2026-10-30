import unittest
import sqlite3
from datetime import datetime, timezone, timedelta
from system_health_analytics_v121 import compare_periods
from unittest.mock import patch

NOW=datetime(2026,10,23,12,tzinfo=timezone.utc)

class HealthAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(':memory:')
        self.conn.execute('CREATE TABLE system_health_checks(id INTEGER PRIMARY KEY, checked_at TEXT, database_status TEXT, monitor_state TEXT, failure_count INTEGER)')
        self.auth=patch('system_health_analytics_v121._actor', return_value={'role':'admin'})
        self.auth.start()
    def tearDown(self):
        self.auth.stop(); self.conn.close()
    def add(self,days,status='ok',state='idle'):
        self.conn.execute('INSERT INTO system_health_checks(checked_at,database_status,monitor_state,failure_count) VALUES(?,?,?,?)',((NOW-timedelta(days=days)).isoformat(),status,state,0))
    def test_empty(self):
        self.assertEqual(compare_periods(self.conn,1,now=NOW)['alerts'],['no_recent_checks'])
    def test_comparison(self):
        self.add(2,'warning');self.add(3);self.add(9)
        r=compare_periods(self.conn,1,now=NOW)
        self.assertEqual(r['current']['checks'],2)
        self.assertEqual(r['previous']['checks'],1)
        self.assertEqual(r['current']['warning_rate'],50)
        self.assertIn('warning_rate_threshold',r['alerts'])
    def test_latest_alert(self):
        self.add(1,'warning','failed')
        self.assertIn('monitor_warning',compare_periods(self.conn,1,now=NOW)['alerts'])
    def test_invalid(self):
        for opts in ({'days':0},{'days':True},{'warning_threshold':101},{'warning_threshold':False},{'now':datetime.now()}):
            with self.assertRaises(ValueError):compare_periods(self.conn,1,**opts)
    def test_no_mutation_of_history(self):
        self.add(1)
        compare_periods(self.conn,1,now=NOW)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM system_health_checks').fetchone()[0],1)
