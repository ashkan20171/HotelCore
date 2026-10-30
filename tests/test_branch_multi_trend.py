import unittest
from branch_multi_trend import build_branch_trend_series


class BranchMultiTrendTests(unittest.TestCase):
    def setUp(self):
        self.reports = [
            ('North', [
                {'month': '2026-01', 'receipts': 100, 'expenses': 60, 'net': 40},
                {'month': '2026-02', 'receipts': 80, 'expenses': 90, 'net': -10},
            ]),
            ('South', [
                {'month': '2026-02', 'receipts': 200, 'expenses': 100, 'net': 100},
            ]),
        ]

    def test_returns_aligned_months_for_all_branches(self):
        result = build_branch_trend_series(self.reports)
        self.assertEqual(result['months'], ['2026-01', '2026-02'])
        self.assertEqual(result['series'][0]['values'], [40, -10])
        self.assertEqual(result['series'][1]['values'], [0, 100])

    def test_selection_and_metric(self):
        result = build_branch_trend_series(self.reports, ['South'], 'receipts')
        self.assertEqual(result['series'], [{'branch': 'South', 'values': [0, 200]}])

    def test_unknown_branch_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series(self.reports, ['Hidden'])

    def test_duplicate_branch_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series(self.reports + [self.reports[0]])

    def test_duplicate_month_rejected(self):
        bad = [('North', self.reports[0][1] * 1)]
        bad[0][1].append({'month': '2026-01', 'receipts': 1, 'expenses': 0, 'net': 1})
        with self.assertRaises(ValueError):
            build_branch_trend_series(bad)

    def test_invalid_month_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series([('A', [{'month': '2026-13', 'receipts': 1, 'expenses': 0, 'net': 1}])])

    def test_boolean_amount_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series([('A', [{'month': '2026-01', 'receipts': True, 'expenses': 0, 'net': 1}])])

    def test_inconsistent_net_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series([('A', [{'month': '2026-01', 'receipts': 10, 'expenses': 3, 'net': 99}])])

    def test_negative_receipts_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series([('A', [{'month': '2026-01', 'receipts': -1, 'expenses': 0, 'net': -1}])])

    def test_invalid_metric_rejected(self):
        with self.assertRaises(ValueError):
            build_branch_trend_series(self.reports, metric='profit')

    def test_empty_input(self):
        self.assertEqual(build_branch_trend_series([]), {'months': [], 'metric': 'net', 'series': []})


if __name__ == '__main__':
    unittest.main()
