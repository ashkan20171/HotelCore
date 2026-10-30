import unittest
from cashflow_trends import month_intervals,scale_bars

class TrendTests(unittest.TestCase):
 def test_cross_year(self):
  self.assertEqual(list(month_intervals('2025-12-30','2026-02-02')),[('2025-12-30','2026-01-01','2025-12'),('2026-01-01','2026-02-01','2026-01'),('2026-02-01','2026-02-02','2026-02')])
 def test_same_month(self):
  self.assertEqual(len(list(month_intervals('2026-01-02','2026-01-04'))),1)
 def test_bad_interval(self):
  with self.assertRaises(ValueError):list(month_intervals('2026-01-02','2026-01-02'))
 def test_zero_bars(self):
  self.assertEqual(scale_bars([{'receipts':0,'expenses':0}])[0]['receipt_percent'],0)
 def test_proportional_bars(self):
  row=scale_bars([{'receipts':200,'expenses':50}])[0]
  self.assertEqual((row['receipt_percent'],row['expense_percent']),(100,25))
 def test_invalid_width(self):
  with self.assertRaises(ValueError):scale_bars([],width=0)
