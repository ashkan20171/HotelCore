import unittest
from finance_chart import chart_points,chart_scale,tooltip_text

class FinanceChartTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(chart_points([]),[])
    def test_empty_scale(self): self.assertEqual(chart_scale([]),1)
    def test_zero_scale(self): self.assertEqual(chart_scale(chart_points([{'month':'2026-01','receipts':0,'expenses':0}])),1)
    def test_sorted(self):
        rows=chart_points([{'month':'2026-02','receipts':4,'expenses':3},{'month':'2026-01','receipts':2,'expenses':5}])
        self.assertEqual([r['month'] for r in rows],['2026-01','2026-02'])
        self.assertEqual(rows[0]['net'],-3)
    def test_negative(self):
        with self.assertRaises(ValueError): chart_points([{'month':'2026-01','receipts':-1,'expenses':0}])
    def test_duplicate(self):
        with self.assertRaises(ValueError): chart_points([{'month':'2026-01','receipts':1,'expenses':0}]*2)
    def test_invalid_month(self):
        with self.assertRaises(ValueError): chart_points([{'month':'2026-13','receipts':1,'expenses':0}])
    def test_scale(self): self.assertEqual(chart_scale(chart_points([{'month':'2026-01','receipts':10,'expenses':20}])),20)
    def test_tooltips(self):
        row={'month':'2026-01','receipts':1000,'expenses':500,'net':500}
        self.assertIn('1,000',tooltip_text(row,'en'))
        self.assertIn('دریافتی',tooltip_text(row,'fa'))
    def test_bad_language(self):
        with self.assertRaises(ValueError): tooltip_text({},'de')
