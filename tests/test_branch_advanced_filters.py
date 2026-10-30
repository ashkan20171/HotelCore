import unittest
from branch_advanced_filters import filter_financial_rows
ROWS=[{'branch':'A','receipts':120,'expenses':20,'net':100},{'branch':'B','receipts':30,'expenses':50,'net':-20},{'branch':'C','receipts':0,'expenses':0,'net':0}]
class FilterTests(unittest.TestCase):
 def test_all(self):self.assertEqual(len(filter_financial_rows(ROWS)),3)
 def test_minimum(self):self.assertEqual(len(filter_financial_rows(ROWS,minimum='0')),2)
 def test_maximum(self):self.assertEqual(len(filter_financial_rows(ROWS,maximum='0')),2)
 def test_range(self):self.assertEqual(len(filter_financial_rows(ROWS,minimum='-20',maximum='0')),2)
 def test_positive(self):self.assertEqual(len(filter_financial_rows(ROWS,state='positive')),1)
 def test_negative(self):self.assertEqual(len(filter_financial_rows(ROWS,state='negative')),1)
 def test_zero(self):self.assertEqual(len(filter_financial_rows(ROWS,state='zero')),1)
 def test_receipts(self):self.assertEqual(len(filter_financial_rows(ROWS,metric='receipts',minimum='100')),1)
 def test_bad_metric(self):
  with self.assertRaises(ValueError):filter_financial_rows(ROWS,metric='bad')
 def test_bad_state(self):
  with self.assertRaises(ValueError):filter_financial_rows(ROWS,state='bad')
 def test_inverted(self):
  with self.assertRaises(ValueError):filter_financial_rows(ROWS,minimum='10',maximum='0')
 def test_nan(self):
  with self.assertRaises(ValueError):filter_financial_rows(ROWS,minimum='NaN')
 def test_original_not_mutated(self):
  filter_financial_rows(ROWS,minimum='1');self.assertEqual(len(ROWS),3)
