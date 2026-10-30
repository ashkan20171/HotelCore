import unittest
from executive_filter_kpis_v149 import filtered_kpis,yoy_chart_values

class FilterKpiTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'date':'2026-01-01','income':100,'expenses':40},
                   {'date':'2026-01-02','income':20,'expenses':60}]
    def test_all(self):
        self.assertEqual(filtered_kpis(self.rows),dict(days=2,total_days=2,income=120,expenses=100,difference=20))
    def test_receipts(self):
        self.assertEqual(filtered_kpis(self.rows,minimum=50,mode='receipts')['difference'],60)
    def test_empty(self):
        self.assertEqual(filtered_kpis(self.rows,minimum=1000)['days'],0)
    def test_yoy_negative(self):
        values=yoy_chart_values({'metrics':{'difference':{'current':-30,'previous':20}}})
        self.assertEqual(values[0]['current'],-30)
    def test_yoy_bad(self):
        with self.assertRaises(ValueError):yoy_chart_values({'metrics':{'income':{'current':'bad','previous':1}}})
