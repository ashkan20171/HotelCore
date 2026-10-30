import unittest
from transfer_executive_dashboard import dashboard

ROWS=[{'branch_id':1,'branch':'North','transfers':3,'reservations':2,'source_rooms':2,'destination_rooms':1,'active_staff':2,'top_actor':'a'},
      {'branch_id':2,'branch':'South','transfers':6,'reservations':4,'source_rooms':3,'destination_rooms':2,'active_staff':1,'top_actor':'b'}]
class DashboardTests(unittest.TestCase):
 def test_totals_and_ranking(self):
  data=dashboard(ROWS)
  self.assertEqual(data['totals']['transfers'],9)
  self.assertEqual([r['branch'] for r in data['rows']],['South','North'])
  self.assertEqual(data['rows'][0]['bar_percent'],100)
 def test_search_and_sort(self):
  data=dashboard(ROWS,search='nor',order='reservations',descending=False)
  self.assertEqual(data['totals']['branches'],1)
  self.assertEqual(data['rows'][0]['branch'],'North')
 def test_empty_and_zero(self):
  self.assertEqual(dashboard([])['rows'],[])
  self.assertEqual(dashboard([{**ROWS[0],'transfers':0}])['rows'][0]['bar_percent'],0)
 def test_reject_invalid_metric(self):
  with self.assertRaises(ValueError):dashboard(ROWS,order='sql')
 def test_no_mutation(self):
  import copy
  before=copy.deepcopy(ROWS);dashboard(ROWS)
  self.assertEqual(ROWS,before)
