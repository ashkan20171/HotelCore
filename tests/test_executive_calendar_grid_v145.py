import unittest
from executive_calendar_grid_v145 import adjacent_month,month_grid
from executive_monthly_chart_v145 import chart_bars

class CalendarGridTests(unittest.TestCase):
    def test_adjacent_year(self):
        self.assertEqual(adjacent_month(1405,12,1),(1406,1))
        self.assertEqual(adjacent_month(1405,1,-1),(1404,12))
    def test_invalid(self):
        with self.assertRaises(ValueError):adjacent_month(1405,0,1)
    def test_month_grid(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime not installed')
        rows=month_grid(1405,1)
        self.assertEqual([x for row in rows for x in row if x is not None],list(range(1,32)))
        self.assertTrue(all(len(row)==7 for row in rows))
    def test_esfand(self):
        try:import jdatetime
        except ImportError:self.skipTest('jdatetime not installed')
        for year in (1404,1405):
            values=[x for row in month_grid(year,12) for x in row if x is not None]
            self.assertIn(len(values),(29,30))
    def test_bars(self):
        self.assertEqual(chart_bars([{'month':'1','income':20,'expenses':10}])[0]['expenses'],.5)
        self.assertEqual(chart_bars([]),[])
    def test_bad_bars(self):
        with self.assertRaises(ValueError):chart_bars([{'month':'1','income':float('nan'),'expenses':0}])
