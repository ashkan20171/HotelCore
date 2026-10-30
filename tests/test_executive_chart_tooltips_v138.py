import unittest
from executive_chart_tooltips_v138 import nearest_point
class HoverTests(unittest.TestCase):
 def test_empty(self):self.assertIsNone(nearest_point([],50,200,35,18))
 def test_first_last(self):
  rows=[{'date':str(i)} for i in range(3)]
  self.assertEqual(nearest_point(rows,35,253,35,18),rows[0])
  self.assertEqual(nearest_point(rows,235,253,35,18),rows[-1])
 def test_outside(self):self.assertIsNone(nearest_point([1,2,3],-100,253,35,18))
 def test_single(self):self.assertEqual(nearest_point([42],35,253,35,18),42)
