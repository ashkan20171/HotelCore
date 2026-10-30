import unittest
from executive_monthly_v144 import monthly_totals

class MonthlyCalendarTests(unittest.TestCase):
    def test_gregorian(self):
        rows=[{'date':'2026-03-20','income':10,'expenses':4},{'date':'2026-03-21','income':20,'expenses':3}]
        self.assertEqual(len(monthly_totals(rows)),1)
    def test_invalid_date(self):
        with self.assertRaises(ValueError):monthly_totals([{'date':'2026-02-30','income':1,'expenses':1}])
    def test_nonfinite(self):
        with self.assertRaises(ValueError):monthly_totals([{'date':'2026-01-01','income':float('nan'),'expenses':1}])
    def test_jalali_new_year_boundary(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime unavailable')
        rows=[{'date':'2026-03-20','income':10,'expenses':2},{'date':'2026-03-21','income':20,'expenses':3}]
        groups=monthly_totals(rows,'jalali')
        self.assertEqual(len(groups),2)
        self.assertEqual(sum(g['income'] for g in groups),30)
    def test_bad_calendar(self):
        with self.assertRaises(ValueError):monthly_totals([],calendar='other')
