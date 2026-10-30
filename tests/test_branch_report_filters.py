import unittest
from branch_report_filters import filter_branches, comparison_csv, safe_csv_cell

ROWS=[{'branch':'Tehran','receipts':100,'expenses':30,'net':70}, {'branch':'Berlin','receipts':80,'expenses':90,'net':-10}]
class BranchReportFiltersTests(unittest.TestCase):
    def test_empty_search(self):self.assertEqual(filter_branches(ROWS),ROWS)
    def test_case_insensitive(self):self.assertEqual(len(filter_branches(ROWS,'BER')),1)
    def test_whitespace(self):self.assertEqual(filter_branches(ROWS,' Tehran '),ROWS[:1])
    def test_no_match(self):self.assertEqual(filter_branches(ROWS,'Paris'),[])
    def test_reject_non_string(self):
        with self.assertRaises(TypeError):filter_branches(ROWS,None)
    def test_english_csv(self):self.assertIn('Branch,Receipts,Expenses,Net cash movement',comparison_csv(ROWS,'en'))
    def test_persian_csv(self):self.assertIn('شعبه',comparison_csv(ROWS,'fa'))
    def test_negative_net(self):self.assertIn('Berlin,80,90,-10',comparison_csv(ROWS,'en'))
    def test_invalid_language(self):
        with self.assertRaises(ValueError):comparison_csv(ROWS,'de')
    def test_formula_injection(self):self.assertIn("'=SUM(1+1)",comparison_csv([dict(ROWS[0],branch='=SUM(1+1)')],'en'))
    def test_csv_bom(self):self.assertTrue(comparison_csv([]).startswith('\ufeff'))
    def test_no_mutation(self):
        copy=list(ROWS);filter_branches(ROWS,'x');self.assertEqual(copy,ROWS)
