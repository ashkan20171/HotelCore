import unittest
from navigation_search import normalize_query, matching_navigation_indices


class NavigationSearchTests(unittest.TestCase):
    def setUp(self):
        self.fa = ['داشبورد', 'مدیریت کاربران', 'گزارش شعب']
        self.en = ['Dashboard', 'User Management', 'Branch Reports']

    def test_empty(self):
        self.assertEqual(matching_navigation_indices('', self.fa, self.en), {0, 1, 2})

    def test_english(self):
        self.assertEqual(matching_navigation_indices('branch', self.fa, self.en), {2})

    def test_persian(self):
        self.assertEqual(matching_navigation_indices('شعب', self.fa, self.en), {2})

    def test_casefold(self):
        self.assertEqual(matching_navigation_indices('USER', self.fa, self.en), {1})

    def test_multiple_terms(self):
        self.assertEqual(matching_navigation_indices('branch report', self.fa, self.en), {2})

    def test_arabic_characters(self):
        self.assertEqual(normalize_query('كاربران'), 'کاربران')

    def test_no_match(self):
        self.assertEqual(matching_navigation_indices('xyz', self.fa, self.en), set())

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            matching_navigation_indices('', ['x'], [])

    def test_non_string(self):
        with self.assertRaises(TypeError):
            normalize_query(None)
