import sqlite3
import unittest
from datetime import date
from executive_multiyear_v151 import historical_windows,historical_cashflow

class MultiYearTests(unittest.TestCase):
    def test_windows(self):
        rows=historical_windows(date(2026,10,1),date(2026,10,3),years=2)
        self.assertEqual(rows[1],(date(2025,10,1),date(2025,10,3)))
        self.assertEqual(rows[2],(date(2024,10,1),date(2024,10,3)))
    def test_invalid(self):
        for years in (0,6,True):
            with self.assertRaises(ValueError):historical_windows(date(2026,1,1),date(2026,1,2),years=years)
        with self.assertRaises(ValueError):historical_windows(date(2026,1,1),date(2026,1,2),calendar='bad')
        with self.assertRaises(ValueError):historical_windows(date(2026,1,1),date(2026,4,1))
    def test_leap(self):
        rows=historical_windows(date(2024,2,29),date(2024,3,1),years=1)
        self.assertEqual(rows[1][0],date(2023,2,28))
        self.assertEqual((rows[1][1]-rows[1][0]).days,1)
    def test_cashflow(self):
        db=sqlite3.connect(':memory:')
        try:
            db.execute('CREATE TABLE payments(amount INTEGER,created_at TEXT)')
            db.execute('CREATE TABLE expenses(amount INTEGER,created_at TEXT)')
            db.executemany('INSERT INTO payments VALUES (?,?)',[(200,'2026-10-02 08:00:00'),(50,'2025-10-02 08:00:00'),(999,'2026-10-04 00:00:00')])
            db.executemany('INSERT INTO expenses VALUES (?,?)',[(30,'2026-10-03 09:00:00'),(10,'2025-10-02 08:00:00')])
            result=historical_cashflow(db,date(2026,10,1),date(2026,10,3),years=2)
            self.assertEqual([r['income'] for r in result['rows']],[200,50,0])
            self.assertEqual(result['rows'][0]['difference'],170)
            self.assertEqual(result['rows'][1]['expense_count'],1)
        finally:db.close()
    def test_jalali_window(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime not installed')
        rows=historical_windows(date(2026,10,1),date(2026,10,3),calendar='jalali',years=2)
        self.assertEqual(len(rows),3)
        self.assertEqual((rows[1][1]-rows[1][0]).days,2)
