import unittest
from dashboard_insights import revenue_change, occupancy_message, revenue_message

class DashboardInsightsTests(unittest.TestCase):
    def test_growth(self): self.assertEqual(revenue_change([('a',100),('b',150)]),50)
    def test_decline(self): self.assertEqual(revenue_change([('a',200),('b',100)]),-50)
    def test_no_baseline(self): self.assertIsNone(revenue_change([('a',0),('b',100)]))
    def test_insufficient(self): self.assertIsNone(revenue_change([('a',100)]))
    def test_negative(self):
        with self.assertRaises(ValueError): revenue_change([('a',-1),('b',20)])
    def test_fa(self): self.assertIn('اشغال',occupancy_message(90,'fa'))
    def test_en(self): self.assertIn('occupancy',occupancy_message(90,'en'))
    def test_invalid_rate(self):
        with self.assertRaises(ValueError): occupancy_message(101)
    def test_revenue_text(self): self.assertIn('+25.0%',revenue_message(25,'en'))

if __name__=='__main__': unittest.main()
