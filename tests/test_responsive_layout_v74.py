import unittest
from responsive_layout import dashboard_columns, grid_positions

class DashboardLayoutTests(unittest.TestCase):
    def test_narrow(self): self.assertEqual(dashboard_columns(350), 1)
    def test_medium(self): self.assertEqual(dashboard_columns(620), 2)
    def test_wide(self): self.assertEqual(dashboard_columns(900), 3)
    def test_boundaries(self):
        self.assertEqual(dashboard_columns(519), 1)
        self.assertEqual(dashboard_columns(520), 2)
        self.assertEqual(dashboard_columns(809), 2)
        self.assertEqual(dashboard_columns(810), 3)
    def test_empty(self): self.assertEqual(dashboard_columns(800, count=0), 0)
    def test_one_card(self): self.assertEqual(dashboard_columns(1200, count=1), 1)
    def test_invalid_width(self):
        for width in (-1, 1.5, True):
            with self.assertRaises(ValueError): dashboard_columns(width)
    def test_invalid_count(self):
        for count in (-1, True):
            with self.assertRaises(ValueError): dashboard_columns(500, count=count)
    def test_positions(self): self.assertEqual(grid_positions(5, 2), [(0,0),(0,1),(1,0),(1,1),(2,0)])
    def test_invalid_columns(self):
        for columns in (0,-1,False):
            with self.assertRaises(ValueError): grid_positions(2,columns)

if __name__ == '__main__': unittest.main()
