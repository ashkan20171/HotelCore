import unittest
from executive_chart_interaction_v150 import nearest_category,chart_tooltip,responsive_chart_height

class ChartInteractionTests(unittest.TestCase):
    def test_category_boundaries(self):
        self.assertEqual(nearest_category(30,318,3),0)
        self.assertEqual(nearest_category(165,318,3),1)
        self.assertEqual(nearest_category(300,318,3),2)
        self.assertIsNone(nearest_category(29,318,3))
        self.assertIsNone(nearest_category(301,318,3))
    def test_empty_or_invalid(self):
        self.assertIsNone(nearest_category(40,100,0))
        self.assertIsNone(nearest_category(float('nan'),100,3))
        self.assertIsNone(nearest_category(40,40,3))
    def test_monthly_tooltip(self):
        row={'month':'1405/07','income':200,'expenses':250}
        self.assertIn('-50',chart_tooltip(row,True))
        self.assertIn('Cash difference',chart_tooltip(row,False))
    def test_yoy_tooltip(self):
        row={'key':'difference','current':-12,'previous':35}
        self.assertIn('-12',chart_tooltip(row,False,'yoy'))
        self.assertIn('سال قبل',chart_tooltip(row,True,'yoy'))
    def test_responsive(self):
        self.assertLess(responsive_chart_height(400),responsive_chart_height(1400))
        self.assertEqual(responsive_chart_height(0),140)
        with self.assertRaises(ValueError):responsive_chart_height(float('inf'))
