import unittest,sqlite3
from datetime import date
from booking_pace_v158 import booking_pace,pace_alerts
class PaceTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE reservations(id INTEGER PRIMARY KEY,created_at TEXT,status TEXT)')
        self.db.executemany('INSERT INTO reservations(created_at,status) VALUES(?,?)', [('2026-10-20 10:00:00','confirmed'),('2026-10-20 11:00:00','cancelled'),('2026-10-12 12:00:00','confirmed'),('2026-10-01 12:00:00','confirmed')])
    def tearDown(self):self.db.close()
    def test_counts(self):
        x=booking_pace(self.db,date(2026,10,23),7)
        self.assertEqual(x['current_total'],2)
        self.assertEqual(x['previous_total'],1)
        self.assertEqual(x['change_percent'],100)
        self.assertEqual(len(x['rows']),7)
    def test_cancellation_included(self):self.assertEqual(booking_pace(self.db,date(2026,10,23),7)['current_total'],2)
    def test_zero_baseline(self):
        x=booking_pace(self.db,date(2026,11,15),7)
        self.assertEqual(x['previous_total'],0)
        self.assertIsNone(x['change_percent'])
    def test_invalid_days(self):
        with self.assertRaises(ValueError):booking_pace(self.db,date.today(),91)
    def test_alert(self):self.assertIn('low_booking_creation_rate',pace_alerts(booking_pace(self.db,date(2026,10,23),7),2))
