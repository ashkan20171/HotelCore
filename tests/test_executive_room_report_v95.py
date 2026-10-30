import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from executive_room_report import validate_thresholds, branch_room_type_comparison, export_branch_comparison_csv

class ExecutiveRoomReportTests(unittest.TestCase):
 def test_thresholds(self):self.assertEqual(validate_thresholds(40,0),(40,0))
 def test_bad_thresholds(self):
  for low,missing in [(-1,0),(101,0),(40,-1),(40,10001),(True,0)]:
   with self.subTest(low=low,missing=missing):
    with self.assertRaises(ValueError):validate_thresholds(low,missing)
 def test_duplicate_branches(self):
  with self.assertRaises(ValueError):
   branch_room_type_comparison(None,branch_ids=[1,1],start='2026-01-01',end='2026-01-08',user_id=1,role='admin')
 def test_unauthorized(self):
  with patch('executive_room_report.allowed_branches',return_value=[(1,'A')]),patch('executive_room_report.require_branch',side_effect=PermissionError):
   with self.assertRaises(PermissionError):
    branch_room_type_comparison(None,branch_ids=[2],start='2026-01-01',end='2026-01-08',user_id=1,role='user')
 def test_branch_scope(self):
  with patch('executive_room_report.allowed_branches',return_value=[(1,'A')]),patch('executive_room_report.require_branch') as check,patch('executive_room_report.room_type_performance',return_value=[{'kind':'Suite','estimated_revpar':4}]) as perf:
   rows=branch_room_type_comparison(None,branch_ids=[1],start='2026-01-01',end='2026-01-08',user_id=1,role='admin')
   self.assertEqual(rows[0]['branch_id'],1)
   check.assert_called_once()
   self.assertEqual(perf.call_args.kwargs['branch_id'],1)
 def test_csv_formula_safety(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'report.csv'
   export_branch_comparison_csv(path,[{'branch_id':1,'branch_name':'=HYPERLINK("x")','kind':'@danger'}])
   with path.open(encoding='utf-8-sig',newline='') as handle:rows=list(csv.DictReader(handle))
   self.assertTrue(rows[0]['branch_name'].startswith("'="))
   self.assertTrue(rows[0]['kind'].startswith("'@"))
