import unittest
from finance_kpi_cards import kpi_view_models

class FinanceKpiCardTests(unittest.TestCase):
    def setUp(self):
        self.report = {'current': {'receipts': 150, 'expenses': 20, 'net_cash_movement': 130},
                       'previous': {'receipts': 100, 'expenses': 40, 'net_cash_movement': 60},
                       'changes': {'receipts': 50.0, 'expenses': -50.0, 'net_cash_movement': 116.7}}
    def test_three_cards(self): self.assertEqual(len(kpi_view_models(self.report)), 3)
    def test_farsi(self): self.assertIn('دریافتی', kpi_view_models(self.report)[0]['label'])
    def test_english(self): self.assertEqual(kpi_view_models(self.report, 'en')[0]['label'], 'Recorded receipts')
    def test_direction(self): self.assertEqual(kpi_view_models(self.report)[1]['direction'], 'down')
    def test_value(self): self.assertEqual(kpi_view_models(self.report)[2]['current'], 130)
    def test_unknown(self):
        self.report['changes']['receipts'] = None
        self.assertEqual(kpi_view_models(self.report)[0]['direction'], 'unknown')
    def test_flat(self):
        self.report['changes']['receipts'] = 0
        self.assertEqual(kpi_view_models(self.report)[0]['direction'], 'flat')
    def test_invalid_language(self):
        with self.assertRaises(ValueError): kpi_view_models(self.report, 'de')

if __name__ == '__main__': unittest.main()
