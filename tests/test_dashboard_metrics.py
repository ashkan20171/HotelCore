import unittest
from dashboard_metrics import summarize_dashboard

class DashboardMetricsTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_dashboard(0,0,0,0)["occupancy_percent"],0)
    def test_occupancy(self):
        self.assertEqual(summarize_dashboard(8,3,2,100)["occupancy_percent"],37.5)
    def test_invalid_occupied(self):
        with self.assertRaises(ValueError): summarize_dashboard(2,3,0,0)
    def test_negative_income(self):
        with self.assertRaises(ValueError): summarize_dashboard(2,1,0,-1)
