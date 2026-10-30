import unittest
from branch_comparison_pdf import validate_report, HEADERS

class BranchComparisonPdfTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'branch':'Alpha','receipts':100,'expenses':35,'net':65},
                     {'branch':'Beta','receipts':20,'expenses':50,'net':-30}]
    def test_totals(self):
        _, total, _, _ = validate_report(self.rows,'2026-01-01','2026-02-01')
        self.assertEqual(total,{'branches':2,'receipts':120,'expenses':85,'net':35})
    def test_empty(self):
        _, total, _, _ = validate_report([],'2026-01-01','2026-02-01')
        self.assertEqual(total['branches'],0)
    def test_exclusive_end(self):
        _, _, _, last=validate_report(self.rows,'2026-01-01','2026-02-01')
        self.assertEqual(last.isoformat(),'2026-01-31')
    def test_order_preserved(self):
        rows, _, _, _=validate_report(self.rows,'2026-01-01','2026-02-01')
        self.assertEqual([r['branch'] for r in rows],['Alpha','Beta'])
    def test_no_mutation(self):
        rows, _, _, _=validate_report(self.rows,'2026-01-01','2026-02-01')
        rows[0]['branch']='Changed'
        self.assertEqual(self.rows[0]['branch'],'Alpha')
    def test_language(self):
        self.assertEqual(HEADERS['fa'][0],'شعبه')
        with self.assertRaises(ValueError):validate_report([], '2026-01-01','2026-02-01','de')
    def test_date(self):
        with self.assertRaises(ValueError):validate_report([], '2026-02-01','2026-02-01')
    def test_bad_amount(self):
        for bad in (True,1.2,'100',None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_report([{'branch':'X','receipts':bad,'expenses':0,'net':0}], '2026-01-01','2026-02-01')
    def test_bad_name(self):
        with self.assertRaises(ValueError):validate_report([{'branch':None,'receipts':1,'expenses':0,'net':1}], '2026-01-01','2026-02-01')
