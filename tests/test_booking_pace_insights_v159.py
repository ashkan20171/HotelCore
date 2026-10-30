import sqlite3,unittest
from datetime import date
from booking_pace_insights_v159 import creation_cohorts,cohort_alerts
class CohortTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE reservations(id INTEGER PRIMARY KEY,created_at TEXT,status TEXT)')
        self.db.executemany('INSERT INTO reservations(created_at,status) VALUES (?,?)',[
            ('2026-10-20 10:00:00','confirmed'),('2026-10-20 11:00:00','cancelled'),
            ('2026-10-12 12:00:00','confirmed'),('2026-10-01 12:00:00','confirmed')])
    def tearDown(self):self.db.close()
    def test_totals(self):
        x=creation_cohorts(self.db,date(2026,10,23),7)
        self.assertEqual(x['current']['gross'],2);self.assertEqual(x['current']['net'],1)
        self.assertEqual(x['previous']['net'],1)
    def test_status_and_daily(self):
        x=creation_cohorts(self.db,date(2026,10,23),7)
        self.assertEqual(x['current']['cancelled_pct'],50)
        self.assertEqual(sum(r['cancelled'] for r in x['rows']),1)
    def test_alerts(self):
        x=creation_cohorts(self.db,date(2026,10,23),7)
        self.assertIn('high_cancellation_share',cohort_alerts(x,cancel_pct=30))
    def test_zero(self):
        x=creation_cohorts(self.db,date(2026,11,30),7)
        self.assertIsNone(x['net_change_pct']);self.assertEqual(x['current']['cancelled_pct'],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):creation_cohorts(self.db,date.today(),91)
        with self.assertRaises(ValueError):cohort_alerts({},cancel_pct=-1)
