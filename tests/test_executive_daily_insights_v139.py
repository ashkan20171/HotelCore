import unittest
from executive_daily_insights_v139 import daily_insight

class DailyInsightsTests(unittest.TestCase):
    def test_normal(self):
        result=daily_insight({'date':'2026-10-22','income':200,'expenses':50})
        self.assertEqual(result['net'],150)
        self.assertEqual(result['expense_ratio_label'],'25.0%')
    def test_zero_income(self):
        result=daily_insight({'date':'2026-10-22','income':0,'expenses':50})
        self.assertIsNone(result['expense_ratio_pct'])
    def test_invalid(self):
        for row in ({'date':'2026-02-30','income':1,'expenses':0},{'date':'2026-10-22','income':float('inf'),'expenses':0},{'date':'2026-10-22','income':-1,'expenses':0}):
            with self.subTest(row=row),self.assertRaises(ValueError):daily_insight(row)
