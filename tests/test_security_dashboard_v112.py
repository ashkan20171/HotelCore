import unittest
from unittest.mock import patch
from datetime import datetime,timezone
from security_dashboard_v112 import compare_windows,kpi_labels

class SecurityDashboardTests(unittest.TestCase):
 def test_rising_failures(self):
  def fake(conn,actor_id,*,days,username,now):
   recent=now.day==20
   return {'totals':{'success':10,'failure':7 if recent else 2,'locked':1},'success_rate':55.6,'series':[]}
  with patch('security_dashboard_v112.chart_data',side_effect=fake):
   result=compare_windows(None,1,days=7,now=datetime(2026,10,20,tzinfo=timezone.utc))
  self.assertEqual(result['failed_delta'],5)
  self.assertEqual(result['alert'],'high')
  self.assertEqual(len(kpi_labels(result)),5)
 def test_invalid_threshold(self):
  with self.assertRaises(ValueError):compare_windows(None,1,alert_threshold=0)
 def test_naive_now(self):
  with self.assertRaises(ValueError):compare_windows(None,1,now=datetime(2026,10,20))
