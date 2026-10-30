import unittest
from executive_multiyear_trends_v152 import growth_percent,historical_trends
class TrendTests(unittest.TestCase):
    def test_growth(self):
        self.assertEqual(growth_percent(120,100),20)
        self.assertEqual(growth_percent(80,100),-20)
        self.assertIsNone(growth_percent(10,0))
    def test_history(self):
        rows=[dict(years_ago=i,start='2020-01-01',end='2020-01-02',income=100*(3-i),expenses=10,difference=100*(3-i)-10) for i in (0,1,2)]
        points=historical_trends(rows)
        self.assertEqual([x['years_ago'] for x in points],[2,1,0])
        self.assertEqual(points[-1]['income_growth_pct'],50)
    def test_bad_values(self):
        for value in (float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):growth_percent(value,10)
        with self.assertRaises(ValueError):historical_trends([])
    def test_zero_baseline(self):
        rows=[dict(years_ago=i,start='2020-01-01',end='2020-01-02',income=v,expenses=0,difference=v) for i,v in ((0,5),(1,0))]
        self.assertIsNone(historical_trends(rows)[-1]['income_growth_pct'])
