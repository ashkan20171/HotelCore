import unittest
from navigation_groups import NAV_GROUPS, group_for_index, group_title, visible_groups

class NavigationGroupsTests(unittest.TestCase):
    def test_all_routes_covered_once(self):
        indices = [i for _, group in NAV_GROUPS for i in group]
        self.assertEqual(sorted(indices), list(range(26)))
    def test_every_route_has_group(self):
        for i in range(26): self.assertTrue(group_for_index(i))
    def test_invalid_route(self):
        for i in (-1, 26, True, '2'):
            with self.assertRaises(ValueError): group_for_index(i)
    def test_farsi_titles(self):
        self.assertEqual(group_title('finance', 'fa'), 'مالی و گزارش‌ها')
    def test_english_titles(self):
        self.assertEqual(group_title('finance', 'en'), 'FINANCE & REPORTS')
    def test_invalid_language(self):
        with self.assertRaises(ValueError): group_title('finance', 'de')
    def test_empty_search(self):
        self.assertEqual(visible_groups([]), set())
    def test_search_only_matching_group(self):
        self.assertEqual(visible_groups([24]), {'finance'})
    def test_search_multiple_groups(self):
        self.assertEqual(visible_groups([0, 25]), {'frontdesk', 'administration'})
