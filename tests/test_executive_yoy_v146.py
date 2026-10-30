import unittest
import sqlite3
from datetime import date
from executive_yoy_v146 import previous_year_window,cash_totals,compare,year_over_year

class YearComparisonTests(unittest.TestCase):
    def test_regular_window(self):
        self.assertEqual(previous_year_window(date(2026,10,1),date(2026,10,10)),(date(2025,10,1),date(2025,10,10)))
    def test_leap_day_clamped(self):
        self.assertEqual(previous_year_window(date(2024,2,29),date(2024,3,1)),(date(2023,2,28),date(2023,3,1)))
    def test_invalid(self):
        with self.assertRaises(ValueError):previous_year_window(date(2026,1,2),date(2026,1,1))
    def test_zero_baseline(self):
        self.assertIsNone(compare({'income':5,'expenses':0,'difference':5},{'income':0,'expenses':0,'difference':0})['income']['percent'])
    def test_db_period(self):
        db=sqlite3.connect(':memory:')
        try:
            db.execute('CREATE TABLE payments(amount INTEGER,created_at TEXT)')
            db.execute('CREATE TABLE expenses(amount INTEGER,created_at TEXT)')
            db.executemany('INSERT INTO payments VALUES (?,?)',[(100,'2025-10-02 10:00:00'),(300,'2026-10-02 10:00:00')])
            db.executemany('INSERT INTO expenses VALUES (?,?)',[(30,'2025-10-02 10:00:00'),(40,'2026-10-02 10:00:00')])
            current=cash_totals(db,date(2026,10,1),date(2026,10,3))
            comparison=year_over_year(db,date(2026,10,1),date(2026,10,3),current)
            self.assertEqual(comparison['metrics']['income']['percent'],200.0)
            self.assertEqual(comparison['metrics']['expenses']['delta'],10)
        finally:db.close()

if __name__=='__main__':unittest.main()
