import unittest
from branch_period_insights import previous_interval, branch_period_insights, insight_caption

class PeriodInsightsTests(unittest.TestCase):
    def test_previous_month(self):
        self.assertEqual(previous_interval('2026-10-01','2026-10-31'),('2026-09-01','2026-10-01'))
    def test_leap_year(self):
        self.assertEqual(previous_interval('2024-03-01','2024-03-02'),('2024-02-29','2024-03-01'))
    def test_invalid(self):
        with self.assertRaises(ValueError): previous_interval('2026-01-02','2026-01-01')
    def test_equal_invalid(self):
        with self.assertRaises(ValueError): previous_interval('2026-01-01','2026-01-01')
    def test_improving(self):
        result=branch_period_insights({1:{'net_cash_movement':80}},{1:{'net_cash_movement':40}})[0]
        self.assertEqual((result['change'],result['direction'],result['change_percent']),(40,'up',100))
    def test_negative_baseline(self):
        result=branch_period_insights({1:{'net_cash_movement':-10}},{1:{'net_cash_movement':-20}})[0]
        self.assertEqual(result['change_percent'],50)
    def test_zero_baseline(self):
        result=branch_period_insights({1:{'net_cash_movement':10}},{1:{'net_cash_movement':0}})[0]
        self.assertIsNone(result['change_percent'])
    def test_decline(self):
        result=branch_period_insights({1:{'net_cash_movement':-3}},{1:{'net_cash_movement':7}})[0]
        self.assertEqual(result['direction'],'down')
    def test_flat(self):
        result=branch_period_insights({1:{'net_cash_movement':7}},{1:{'net_cash_movement':7}})[0]
        self.assertEqual(result['direction'],'flat')
    def test_mismatched_branches_rejected(self):
        with self.assertRaises(ValueError): branch_period_insights({1:{'net_cash_movement':1}}, {})
    def test_empty(self):
        self.assertEqual(branch_period_insights({},{}),[])
    def test_labels(self):
        self.assertIn('Net improved',insight_caption([], 'en'))
        self.assertIn('خالص منفی',insight_caption([], 'fa'))
    def test_bad_language(self):
        with self.assertRaises(ValueError): insight_caption([], 'fr')
