import unittest
from occupancy_calendar import cell_color, cell_description, is_bookable

class OccupancyCalendarTests(unittest.TestCase):
    def test_available_is_bookable(self):
        self.assertTrue(is_bookable('آزاد'))
    def test_reserved_not_bookable(self):
        self.assertFalse(is_bookable('رزرو شده'))
    def test_checked_in_not_bookable(self):
        self.assertFalse(is_bookable('پذیرش شده'))
    def test_english_translation(self):
        self.assertEqual(cell_description('رزرو شده','en'),'Reserved')
    def test_farsi_translation(self):
        self.assertEqual(cell_description('آزاد','fa'),'آزاد')
    def test_known_color(self):
        self.assertEqual(cell_color('آزاد'),'#0f766e')
    def test_unknown_color(self):
        self.assertEqual(cell_color('unknown'),'#64748b')
