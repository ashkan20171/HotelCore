import sqlite3
import unittest
from dashboard_reporting import reporting_window,payment_totals,compare_periods


class DashboardReportingTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER);
        CREATE TABLE payments(id INTEGER PRIMARY KEY,reservation_id INTEGER,amount INTEGER,created_at TEXT);
        INSERT INTO reservations VALUES(1,1),(2,2);
        INSERT INTO payments VALUES(1,1,100,'2026-10-19 10:00:00'),(2,1,250,'2026-10-20 12:00:00'),
        (3,2,9999,'2026-10-20 12:00:00'),(4,1,75,'2026-10-01 09:00:00');""")

    def tearDown(self):self.db.close()
    def test_window_inclusive(self):self.assertEqual(reporting_window('2026-10-20',7),('2026-10-14','2026-10-20'))
    def test_window_crosses_year(self):self.assertEqual(reporting_window('2026-01-02',7),('2025-12-27','2026-01-02'))
    def test_invalid_window(self):
        for n in (0,367,True):
            with self.subTest(n=n),self.assertRaises(ValueError):reporting_window('2026-10-20',n)
    def test_branch_isolation(self):self.assertEqual(payment_totals(self.db,1,'2026-10-14','2026-10-20'),{'payments':2,'revenue':350})
    def test_other_branch(self):self.assertEqual(payment_totals(self.db,2,'2026-10-14','2026-10-20'),{'payments':1,'revenue':9999})
    def test_empty_period(self):self.assertEqual(payment_totals(self.db,1,'2026-10-10','2026-10-12'),{'payments':0,'revenue':0})
    def test_invalid_branch(self):
        with self.assertRaises(ValueError):payment_totals(self.db,0,'2026-10-14','2026-10-20')
    def test_invalid_date_range(self):
        with self.assertRaises(ValueError):payment_totals(self.db,1,'2026-10-20','2026-10-14')
    def test_compare(self):self.assertEqual(compare_periods(150,100),50.0)
    def test_no_baseline(self):self.assertIsNone(compare_periods(150,0))
    def test_negative_rejected(self):
        with self.assertRaises(ValueError):compare_periods(-1,1)
