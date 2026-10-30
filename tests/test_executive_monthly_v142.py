import unittest
from datetime import date
from executive_monthly_v142 import monthly_totals
from executive_dashboard_v131 import snapshot

class MonthlyTests(unittest.TestCase):
    def test_aggregation(self):
        result=monthly_totals([{'date':'2026-01-31','income':10,'expenses':3},{'date':'2026-02-01','income':20,'expenses':7},{'date':'2026-02-02','income':5,'expenses':1}])
        self.assertEqual(result,[{'month':'2026-01','income':10,'expenses':3,'difference':7},{'month':'2026-02','income':25,'expenses':8,'difference':17}])
    def test_empty(self):self.assertEqual(monthly_totals([]),[])
    def test_invalid(self):
        with self.assertRaises(ValueError):monthly_totals([{'date':'bad','income':1,'expenses':0}])
    def test_negative(self):
        with self.assertRaises(ValueError):monthly_totals([{'date':'2026-01-01','income':-1,'expenses':0}])
