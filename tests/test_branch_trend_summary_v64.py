import unittest
from branch_trend_summary import merge_monthly_branches, trend_caption

class BranchTrendSummaryTests(unittest.TestCase):
    def row(self, month='2026-01', receipts=100, expenses=40):
        return dict(month=month, receipts=receipts, expenses=expenses, net=receipts-expenses)

    def test_empty(self): self.assertEqual(merge_monthly_branches([]), [])
    def test_one(self): self.assertEqual(merge_monthly_branches([('A',[self.row()])])[0]['net'],60)
    def test_merge(self): self.assertEqual(merge_monthly_branches([('A',[self.row()]),('B',[self.row(receipts=30,expenses=20)])])[0]['net'],70)
    def test_sorted(self): self.assertEqual([r['month'] for r in merge_monthly_branches([('A',[self.row('2026-03'),self.row('2026-01')])])],['2026-01','2026-03'])
    def test_duplicate_branch(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[]),('A',[])])
    def test_duplicate_month(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[self.row(),self.row()])])
    def test_invalid_month(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[self.row('2026-13')])])
    def test_inconsistent_net(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[dict(self.row(),net=999)])])
    def test_bool_amount(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[dict(self.row(),receipts=True)])])
    def test_negative_receipts(self):
        with self.assertRaises(ValueError):merge_monthly_branches([('A',[self.row(receipts=-2,expenses=0)])])
    def test_caption_fa(self):self.assertIn('60',trend_caption([self.row()], 'fa'))
    def test_caption_en(self):self.assertIn('Reporting months',trend_caption([self.row()], 'en'))
    def test_invalid_language(self):
        with self.assertRaises(ValueError):trend_caption([], 'fr')
