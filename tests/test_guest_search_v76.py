import unittest
from guest_search import normalize_query, matches_guest

class GuestSearchTests(unittest.TestCase):
    def test_persian_digits(self):
        self.assertEqual(normalize_query('۱۲٣'), '123')
    def test_arabic_letters(self):
        self.assertTrue(matches_guest(['علي كريمي'], 'علی کریمی'))
    def test_multiword(self):
        self.assertTrue(matches_guest(['Ali Reza', '09123456789'], 'ali 567'))
    def test_no_match(self):
        self.assertFalse(matches_guest(['Sara', '123'], 'Ali'))
    def test_blank(self):
        self.assertTrue(matches_guest(['Sara'], ''))
