import unittest
from branch_executive_kpis import executive_metrics, executive_labels


class ExecutiveKpiTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {'branch': 'A', 'receipts': 200, 'expenses': 100, 'net': 100},
            {'branch': 'B', 'receipts': 10, 'expenses': 50, 'net': -40},
            {'branch': 'C', 'receipts': 0, 'expenses': 0, 'net': 0},
        ]

    def test_count(self): self.assertEqual(executive_metrics(self.rows)['branches'], 3)
    def test_positive(self): self.assertEqual(executive_metrics(self.rows)['positive_branches'], 1)
    def test_negative(self): self.assertEqual(executive_metrics(self.rows)['negative_branches'], 1)
    def test_zero(self): self.assertEqual(executive_metrics(self.rows)['zero_branches'], 1)
    def test_average(self): self.assertEqual(executive_metrics(self.rows)['average_net'], 20)
    def test_coverage(self): self.assertEqual(executive_metrics(self.rows)['cash_coverage_percent'], 140)
    def test_empty(self): self.assertEqual(executive_metrics([])['average_net'], 0)
    def test_no_expenses(self): self.assertIsNone(executive_metrics([{'branch':'X','receipts':5,'expenses':0,'net':5}])['cash_coverage_percent'])
    def test_fa_labels(self): self.assertEqual(len(executive_labels(executive_metrics(self.rows),'fa')),5)
    def test_en_labels(self): self.assertIn('Visible',executive_labels(executive_metrics(self.rows),'en')[0][0])
    def test_invalid_language(self):
        with self.assertRaises(ValueError): executive_labels(executive_metrics([]),'de')
    def test_invalid_amount(self):
        with self.assertRaises(ValueError): executive_metrics([{'branch':'A','receipts':True,'expenses':0,'net':0}])


if __name__=='__main__': unittest.main()
