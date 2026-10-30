import unittest
from cashflow_dashboard import cashflow_cards,cashflow_comparison

class CashflowDashboardTests(unittest.TestCase):
 def test_fa(self):
  self.assertEqual(cashflow_cards({'receipts':120,'expenses':30})[-1],('خالص گردش وجوه',90))
 def test_en(self):
  self.assertEqual(cashflow_cards({'receipts':120,'expenses':30},'en')[0],('Recorded receipts',120))
 def test_negative_net(self):
  self.assertEqual(cashflow_cards({'receipts':10,'expenses':30})[-1][1],-20)
 def test_invalid_language(self):
  with self.assertRaises(ValueError):cashflow_cards({'receipts':1,'expenses':2},'de')
 def test_invalid_negative_total(self):
  with self.assertRaises(ValueError):cashflow_cards({'receipts':-1,'expenses':2})
 def test_comparison_sorted(self):
  r=cashflow_comparison([('B',{'receipts':10,'expenses':9}),('A',{'receipts':10,'expenses':1})])
  self.assertEqual([x['branch'] for x in r],['A','B'])
 def test_empty_comparison(self):
  self.assertEqual(cashflow_comparison([]),[])
