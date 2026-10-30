import unittest
from executive_kpi_presentation_v137 import compare_periods,responsive_columns

class PresentationTests(unittest.TestCase):
    def test_responsive_breakpoints(self):
        self.assertEqual([responsive_columns(x) for x in (400,649,650,899,900,1200)],[1,1,2,2,3,3])
    def test_increase(self):self.assertEqual(compare_periods(120,100)['percent'],20)
    def test_decrease(self):self.assertEqual(compare_periods(80,100)['percent'],-20)
    def test_zero_prior(self):self.assertEqual(compare_periods(5,0)['kind'],'undefined')
    def test_both_zero(self):self.assertEqual(compare_periods(0,0)['kind'],'unchanged')
    def test_negative_prior(self):self.assertEqual(compare_periods(-5,-10)['percent'],50)
    def test_invalid(self):self.assertEqual(compare_periods(float('nan'),1)['kind'],'unavailable')
