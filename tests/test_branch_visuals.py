import unittest
from branch_visuals import comparison_bars

class BranchVisualTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(comparison_bars([]), [])
    def test_normalized(self):
        rows=comparison_bars([('A', {'receipts':100,'expenses':25}),('B',{'receipts':50,'expenses':75})])
        self.assertEqual(rows[0]['receipt_percent'],100)
        self.assertEqual(rows[0]['expense_percent'],25)
    def test_negative_net(self):
        row=comparison_bars([('A',{'receipts':10,'expenses':30})])[0]
        self.assertTrue(row['net_negative'])
        self.assertEqual(row['net'],-20)
        self.assertEqual(row['net_percent'],67)
    def test_zero(self):
        row=comparison_bars([('A',{'receipts':0,'expenses':0})])[0]
        self.assertEqual(row['net_percent'],0)
    def test_limit(self):
        rows=comparison_bars([(str(i),{'receipts':i,'expenses':0}) for i in range(15)],limit=3)
        self.assertEqual(len(rows),3)
    def test_bad_limit(self):
        for value in (0,-1,True,1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):comparison_bars([],limit=value)
    def test_invalid_language(self):
        with self.assertRaises(ValueError):comparison_bars([],language='de')
