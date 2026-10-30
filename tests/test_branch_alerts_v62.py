import unittest
from branch_alerts import validate_threshold, evaluate_alerts, alert_summary


class BranchAlertsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {'branch_id': 1, 'net': -200, 'change': -70},
            {'branch_id': 2, 'net': 500, 'change': -300},
            {'branch_id': 3, 'net': 0, 'change': 0},
        ]

    def test_zero_threshold(self):
        self.assertEqual(len(evaluate_alerts(self.rows)), 3)

    def test_threshold_exclusive(self):
        self.assertEqual(len(evaluate_alerts(self.rows, 200)), 1)

    def test_threshold_higher_than_all(self):
        self.assertEqual(evaluate_alerts(self.rows, 1000), [])

    def test_empty(self):
        self.assertEqual(evaluate_alerts([]), [])

    def test_original_not_mutated(self):
        evaluate_alerts(self.rows)
        self.assertEqual(self.rows[0]['net'], -200)

    def test_negative_threshold(self):
        with self.assertRaises(ValueError):validate_threshold(-1)

    def test_fractional_threshold(self):
        with self.assertRaises(ValueError):validate_threshold('1.5')

    def test_bool_threshold(self):
        with self.assertRaises(ValueError):validate_threshold(True)

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):validate_threshold('abc')

    def test_persian_caption(self):
        self.assertIn('خالص منفی',alert_summary(evaluate_alerts(self.rows),'fa'))

    def test_english_caption(self):
        self.assertIn('Period decline',alert_summary(evaluate_alerts(self.rows),'en'))

    def test_invalid_language(self):
        with self.assertRaises(ValueError):alert_summary([], 'de')

    def test_sorted_largest_first(self):
        amounts=[x['amount'] for x in evaluate_alerts(self.rows)]
        self.assertEqual(amounts,sorted(amounts,reverse=True))
