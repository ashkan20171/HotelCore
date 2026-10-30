import unittest
from branch_trend_data import normalize_chart_rows

class BranchTrendChartTests(unittest.TestCase):
    def test_sorts_rows_by_month(self):
        rows = [
            {'month':'2026-02','receipts':100,'expenses':30,'net':70},
            {'month':'2026-01','receipts':80,'expenses':20,'net':60},
        ]
        self.assertEqual([r['month'] for r in normalize_chart_rows(rows)], ['2026-01','2026-02'])

    def test_rejects_duplicate_month(self):
        row={'month':'2026-01','receipts':10,'expenses':5,'net':5}
        with self.assertRaises(ValueError): normalize_chart_rows([row,row])

    def test_rejects_invalid_month(self):
        with self.assertRaises(ValueError): normalize_chart_rows([{'month':'2026-13','receipts':10,'expenses':5,'net':5}])

    def test_rejects_boolean_amount(self):
        with self.assertRaises(ValueError): normalize_chart_rows([{'month':'2026-01','receipts':True,'expenses':5,'net':-4}])

    def test_rejects_inconsistent_net(self):
        with self.assertRaises(ValueError): normalize_chart_rows([{'month':'2026-01','receipts':10,'expenses':5,'net':6}])

    def test_accepts_empty_data(self):
        self.assertEqual(normalize_chart_rows([]), [])

if __name__ == '__main__': unittest.main()
