import unittest
from property_insights import filtered_rankings,chart_bars
ROWS=[{'branch_name':'Berlin','occupancy_percent':80,'estimated_revpar':200,'alerts':[]},{'branch_name':'Hamburg','occupancy_percent':None,'estimated_revpar':None,'alerts':['missing_quotes']},{'branch_name':'Munich','occupancy_percent':30,'estimated_revpar':100,'alerts':['low_occupancy']}]
class PropertyInsightsTests(unittest.TestCase):
 def test_ranking(self):self.assertEqual([x['branch_name'] for x in filtered_rankings(ROWS)],['Berlin','Munich','Hamburg'])
 def test_search(self):self.assertEqual(len(filtered_rankings(ROWS,search='ber')),1)
 def test_alert_filter(self):self.assertEqual(len(filtered_rankings(ROWS,only_alerts=True)),2)
 def test_invalid_metric(self):
  with self.assertRaises(ValueError):filtered_rankings(ROWS,metric='private_data')
 def test_bars(self):self.assertEqual([x['percent'] for x in chart_bars(ROWS)],[100,0,38])
 def test_zero_bars(self):self.assertEqual(chart_bars([{'branch_name':'X','occupancy_percent':0}])[0]['percent'],0)
