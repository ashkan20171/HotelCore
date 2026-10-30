import unittest
from branch_aggregates import visible_totals, totals_caption

class VisibleTotalsTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(visible_totals([]),dict(branches=0,receipts=0,expenses=0,net=0))
    def test_multiple(self):
        rows=[dict(receipts=100,expenses=40,net=60),dict(receipts=30,expenses=80,net=-50)]
        self.assertEqual(visible_totals(rows),dict(branches=2,receipts=130,expenses=120,net=10))
    def test_filtered_rows_only(self):
        rows=[dict(receipts=5,expenses=1,net=4)]
        self.assertEqual(visible_totals(rows)['receipts'],5)
    def test_negative(self):
        self.assertEqual(visible_totals([dict(receipts=0,expenses=9,net=-9)])['net'],-9)
    def test_bool_rejected(self):
        with self.assertRaises(ValueError):visible_totals([dict(receipts=True,expenses=1,net=0)])
    def test_float_rejected(self):
        with self.assertRaises(ValueError):visible_totals([dict(receipts=1.5,expenses=1,net=0)])
    def test_fa(self):
        self.assertIn('شعب قابل مشاهده: 0',totals_caption(visible_totals([]),'fa'))
    def test_en(self):
        self.assertIn('Visible branches: 0',totals_caption(visible_totals([]),'en'))
    def test_money_formatter(self):
        self.assertIn('USD 10',totals_caption(dict(branches=1,receipts=10,expenses=0,net=10),'en',lambda x:f'USD {x}'))
