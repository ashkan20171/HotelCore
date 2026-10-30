import sqlite3,unittest
from datetime import date
from unittest.mock import patch
from executive_dashboard_v131 import snapshot,validate

class ExecutiveTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,checkin TEXT,checkout TEXT,status TEXT,created_at TEXT);
        CREATE TABLE payments(id INTEGER PRIMARY KEY,amount INTEGER,created_at TEXT);
        CREATE TABLE expenses(id INTEGER PRIMARY KEY,amount INTEGER,created_at TEXT);
        INSERT INTO rooms VALUES(1);INSERT INTO rooms VALUES(2);
        INSERT INTO reservations VALUES(1,'2026-10-22','2026-10-24','confirmed','2026-10-23 12:00:00');
        INSERT INTO reservations VALUES(2,'2026-10-22','2026-10-24','cancelled','2026-10-23 12:00:00');
        INSERT INTO payments VALUES(1,100,'2026-10-23 12:00:00');
        INSERT INTO expenses VALUES(1,25,'2026-10-23 12:00:00');""")
    def tearDown(self):self.db.close()
    def test_kpis_and_series(self):
        with patch('executive_dashboard_v131._actor'):
            r=snapshot(self.db,1,days=2,today=date(2026,10,23))
        self.assertEqual(r['current']['income'],100)
        self.assertEqual(r['current']['expenses'],25)
        self.assertEqual(r['current']['cash_difference'],75)
        self.assertEqual(r['current']['occupied_nights'],2)
        self.assertEqual(r['current']['occupancy_pct'],50)
        self.assertEqual(r['current']['new_reservations'],2)
        self.assertEqual(len(r['series']),2)
        self.assertEqual(r['series'][-1]['income'],100)
    def test_previous_period(self):
        with patch('executive_dashboard_v131._actor'):
            r=snapshot(self.db,1,days=2,today=date(2026,10,23))
        self.assertEqual(r['previous']['income'],0)
    def test_invalid_periods(self):
        for days in (0,91,True,'30'):
            with self.assertRaises(ValueError):validate(days,date(2026,10,23))
    def test_fail_closed(self):
        with patch('executive_dashboard_v131._actor',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):snapshot(self.db,1)
    def test_no_rooms(self):
        self.db.execute('DELETE FROM rooms')
        with patch('executive_dashboard_v131._actor'):
            r=snapshot(self.db,1,days=2,today=date(2026,10,23))
        self.assertEqual(r['current']['occupancy_pct'],0)
