import unittest
from property_executive_visuals import kpi_display,comparative_bars
class ExecutiveVisualTests(unittest.TestCase):
 def test_kpis_empty(self):
  result=kpi_display({'branches':0,'rooms':0,'occupancy_percent':None,'estimated_adr':None,'estimated_revpar':None,'missing_quotes':0},'en')
  self.assertEqual(result[2][1],'—')
 def test_language(self):
  with self.assertRaises(ValueError):kpi_display({},'de')
 def test_comparison_ranking(self):
  result=comparative_bars([{'branch_name':'A','estimated_adr':100},{'branch_name':'B','estimated_adr':200}], 'estimated_adr')
  self.assertEqual([x['branch_name'] for x in result],['B','A'])
  self.assertEqual([x['percent'] for x in result],[100,50])
 def test_missing_and_invalid(self):
  self.assertEqual(comparative_bars([{'branch_name':'A','estimated_revpar':None},{'branch_name':'B','estimated_revpar':-5}], 'estimated_revpar'),[])
 def test_invalid_metric(self):
  with self.assertRaises(ValueError):comparative_bars([], 'bad')
 def test_zero_values(self):
  self.assertEqual(comparative_bars([{'branch_name':'A','estimated_revpar':0}],'estimated_revpar')[0]['percent'],0)
