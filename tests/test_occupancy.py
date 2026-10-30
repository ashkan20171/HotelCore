import unittest
from occupancy import build_grid, occupancy_summary

class OccupancyTests(unittest.TestCase):
    def test_checkout_exclusive(self):
        _, grid = build_grid([(1, '101')], [(1, '2026-10-20', '2026-10-22', 'رزرو شده')], '2026-10-20', 3)
        self.assertEqual(grid[1], ['رزرو شده', 'رزرو شده', 'آزاد'])
    def test_cancelled_ignored(self):
        _, grid = build_grid([(1, '101')], [(1, '2026-10-20', '2026-10-21', 'لغو شده')], '2026-10-20', 1)
        self.assertEqual(grid[1], ['آزاد'])
    def test_summary(self):
        self.assertEqual(occupancy_summary({1:['آزاد','رزرو شده'], 2:['آزاد','آزاد']},2)['occupancy_percent'],25.0)
    def test_no_rooms(self):
        self.assertEqual(occupancy_summary({}, 7)['occupancy_percent'],0)
    def test_invalid_days(self):
        with self.assertRaises(ValueError): build_grid([], [], '2026-10-20', 0)
