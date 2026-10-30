import unittest
from branch_sorting import sort_branch_rows

class SortBranchRowsTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'branch':'Beta','receipts':20,'expenses':30,'net':-10}, {'branch':'alpha','receipts':10,'expenses':0,'net':10}, {'branch':'Gamma','receipts':20,'expenses':1,'net':19}]
    def test_receipts_desc(self):
        self.assertEqual([r['branch'] for r in sort_branch_rows(self.rows)],['Gamma','Beta','alpha'])
    def test_receipts_asc(self):
        self.assertEqual([r['branch'] for r in sort_branch_rows(self.rows,descending=False)],['alpha','Beta','Gamma'])
    def test_expenses(self):
        self.assertEqual(sort_branch_rows(self.rows,'expenses')[0]['branch'],'Beta')
    def test_negative_net(self):
        self.assertEqual(sort_branch_rows(self.rows,'net',False)[0]['net'],-10)
    def test_name(self):
        self.assertEqual(sort_branch_rows(self.rows,'branch',False)[0]['branch'],'alpha')
    def test_empty(self):
        self.assertEqual(sort_branch_rows([]),[])
    def test_immutable(self):
        self.assertEqual(self.rows[0]['branch'],'Beta');self.assertIsNot(sort_branch_rows(self.rows),self.rows)
    def test_bad_key(self):
        with self.assertRaises(ValueError):sort_branch_rows(self.rows,'secret')
    def test_bad_direction(self):
        with self.assertRaises(ValueError):sort_branch_rows(self.rows,descending=1)
