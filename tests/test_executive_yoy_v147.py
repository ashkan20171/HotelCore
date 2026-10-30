import sqlite3
import unittest
from datetime import date
from executive_yoy_v147 import year_over_year_calendar,previous_jalali_year_window

class CalendarYearTests(unittest.TestCase):
    def test_invalid_calendar(self):
        with sqlite3.connect(':memory:') as conn:
            with self.assertRaises(ValueError):
                year_over_year_calendar(conn,date(2026,1,1),date(2026,1,2),{},'invalid')
    def test_gregorian_compatibility(self):
        conn=sqlite3.connect(':memory:')
        try:
            conn.execute('CREATE TABLE payments(amount INTEGER,created_at TEXT)')
            conn.execute('CREATE TABLE expenses(amount INTEGER,created_at TEXT)')
            result=year_over_year_calendar(conn,date(2026,10,1),date(2026,10,2),{'income':0,'expenses':0,'difference':0})
            self.assertEqual(result['prior_start'],'2025-10-01')
            self.assertEqual(result['calendar'],'gregorian')
        finally:conn.close()
    def test_jalali_shift(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime not installed')
        start=date(2026,3,21)
        a,b=previous_jalali_year_window(start,date(2026,3,23))
        self.assertEqual(jdatetime.date.fromgregorian(date=a).year,jdatetime.date.fromgregorian(date=start).year-1)
        self.assertEqual((b-a).days,2)
    def test_jalali_esfand_leap(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime not installed')
        start=jdatetime.date(1399,12,30).togregorian()
        prior,_=previous_jalali_year_window(start,start)
        self.assertEqual(jdatetime.date.fromgregorian(date=prior).day,29)

if __name__=='__main__':unittest.main()
