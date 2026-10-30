import unittest
from unittest.mock import patch
from property_period_comparison import compare_property_periods

class PeriodComparisonTests(unittest.TestCase):
 def test_equal_length_and_deltas(self):
  now=[dict(branch_id=1,branch_name='A',occupancy_percent=70,estimated_adr=100,estimated_revpar=None,estimated_value=700)]
  old=[dict(branch_id=1,branch_name='A',occupancy_percent=50,estimated_adr=80,estimated_revpar=50,estimated_value=500)]
  with patch('property_period_comparison.branch_scorecard',side_effect=[now,old]) as score:
   result=compare_property_periods(None,user_id=1,role='admin',start='2026-10-01',end='2026-10-08')
  self.assertEqual(result['previous_start'],'2026-09-24')
  self.assertEqual(result['rows'][0]['changes']['occupancy_percent'],20)
  self.assertIsNone(result['rows'][0]['changes']['estimated_revpar'])
  self.assertEqual(score.call_count,2)
 def test_invalid_window(self):
  with self.assertRaises(ValueError):compare_property_periods(None,user_id=1,role='admin',start='2026-10-08',end='2026-10-01')
 def test_authorization_propagates(self):
  with patch('property_period_comparison.branch_scorecard',side_effect=PermissionError):
   with self.assertRaises(PermissionError):compare_property_periods(None,user_id=1,role='user',start='2026-10-01',end='2026-10-08')
