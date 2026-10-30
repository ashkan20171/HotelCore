import unittest
from revenue_occupancy_dashboard import report_window,dashboard_kpis,dashboard_alerts

class ExecutiveAccommodationTests(unittest.TestCase):
 def test_window(self):
  self.assertEqual(report_window('2026-10-22',7),('2026-10-16','2026-10-23'))
 def test_invalid_window(self):
  with self.assertRaises(ValueError):report_window('2026-10-22',12)
 def test_occupancy_and_estimates(self):
  p=dict(available_room_nights=100,occupied_room_nights=45,missing_quotes=0,estimated_adr=200,estimated_revpar=90,estimated_accommodation_value=9000)
  result=dashboard_kpis(p)
  self.assertEqual(result['occupancy_percent'],45)
  self.assertEqual(result['estimated_revpar'],90)
 def test_missing_quote_alert(self):
  p=dict(available_room_nights=100,occupied_room_nights=45,missing_quotes=2,estimated_adr=None,estimated_revpar=None,estimated_accommodation_value=100)
  self.assertTrue(dashboard_alerts(dashboard_kpis(p),'en'))
 def test_capacity_warning(self):
  p=dict(available_room_nights=1,occupied_room_nights=2,missing_quotes=0,estimated_adr=10,estimated_revpar=20,estimated_accommodation_value=20)
  self.assertTrue(dashboard_kpis(p)['overcapacity'])
