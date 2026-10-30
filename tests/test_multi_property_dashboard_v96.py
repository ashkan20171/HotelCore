import unittest
from unittest.mock import patch
from multi_property_dashboard import branch_scorecard,overview_totals

class MultiPropertyTests(unittest.TestCase):
 def test_weighted_occupancy(self):
  rows=[{'capacity_nights':100,'occupied_nights':80,'estimated_value':200,'rooms':10,'missing_quotes':0},{'capacity_nights':300,'occupied_nights':150,'estimated_value':300,'rooms':30,'missing_quotes':0}]
  self.assertEqual(overview_totals(rows)['occupancy_percent'],57.5)
 def test_missing_quotes(self):
  rows=[{'capacity_nights':100,'occupied_nights':50,'estimated_value':200,'rooms':10,'missing_quotes':1}]
  self.assertIsNone(overview_totals(rows)['estimated_revpar'])
 def test_invalid_range(self):
  with self.assertRaises(ValueError):branch_scorecard(None,user_id=1,role='admin',start='2026-01-01',end='2026-05-01')
 def test_duplicate_branches(self):
  with patch('multi_property_dashboard.allowed_branches',return_value=[(1,'A')]):
   with self.assertRaises(ValueError):branch_scorecard(None,user_id=1,role='admin',start='2026-01-01',end='2026-01-08',branch_ids=[1,1])
 def test_authorization(self):
  with patch('multi_property_dashboard.allowed_branches',return_value=[(1,'A')]),patch('multi_property_dashboard.require_branch',side_effect=PermissionError):
   with self.assertRaises(PermissionError):branch_scorecard(None,user_id=1,role='staff',start='2026-01-01',end='2026-01-08',branch_ids=[2])
 def test_scorecard(self):
  record={'rooms':2,'capacity_nights':14,'occupied_nights':7,'estimated_value':700,'missing_quotes':0,'overcapacity':False}
  with patch('multi_property_dashboard.allowed_branches',return_value=[(1,'A')]),patch('multi_property_dashboard.require_branch'),patch('multi_property_dashboard.room_type_performance',return_value=[record]):
   rows=branch_scorecard(None,user_id=1,role='admin',start='2026-01-01',end='2026-01-08')
   self.assertEqual(rows[0]['occupancy_percent'],50.0)
   self.assertEqual(rows[0]['estimated_revpar'],50.0)
