import unittest
from executive_financial_filters_v148 import filter_daily_series,filtered_snapshot
ROWS=[{'date':'2026-10-01','income':500,'expenses':100}, {'date':'2026-10-02','income':200,'expenses':600}, {'date':'2026-10-03','income':0,'expenses':0}]
class FinancialFilterTests(unittest.TestCase):
    def test_minimum_and_mode(self):
        self.assertEqual(len(filter_daily_series(ROWS,minimum=500)),2)
        self.assertEqual([r['date'] for r in filter_daily_series(ROWS,minimum=500,mode='receipts')],['2026-10-01'])
    def test_maximum_and_net(self):
        self.assertEqual([r['date'] for r in filter_daily_series(ROWS,minimum=0,maximum=300,mode='net')],['2026-10-03'])
    def test_date(self):
        self.assertEqual(len(filter_daily_series(ROWS,search='10-02')),1)
    def test_invalid(self):
        with self.assertRaises(ValueError):filter_daily_series(ROWS,minimum=100,maximum=20)
        with self.assertRaises(ValueError):filter_daily_series(ROWS,mode='oops')
    def test_copy(self):
        original={'series':ROWS,'room_types':[]};filtered=filtered_snapshot(original,minimum=500)
        self.assertEqual(len(filtered['series']),2)
        self.assertEqual(len(original['series']),3)
