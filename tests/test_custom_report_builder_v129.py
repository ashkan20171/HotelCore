import unittest
from datetime import datetime, timezone
from custom_report_builder_v129 import validate, write_excel, FIELDS

class ReportBuilderValidationTests(unittest.TestCase):
    def test_valid(self):
        validate(('checked_at','failure_count'),30,'warning',250)
    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):validate(('checked_at','checked_at'),30)
    def test_unknown_columns_rejected(self):
        with self.assertRaises(ValueError):validate(('id',),30)
    def test_empty_columns_rejected(self):
        with self.assertRaises(ValueError):validate((),30)
    def test_bad_days(self):
        for value in (0,366,True,'30'):
            with self.subTest(value=value),self.assertRaises(ValueError):validate(FIELDS,value)
    def test_bad_status(self):
        with self.assertRaises(ValueError):validate(FIELDS,30,'invalid')
    def test_bad_limit(self):
        with self.assertRaises(ValueError):validate(FIELDS,30,limit=1001)
    def test_excel_formula_escaped(self):
        import tempfile
        from pathlib import Path
        from openpyxl import load_workbook
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test.xlsx'
            write_excel(path,('monitor_state',),[('=1+2',)],'en')
            self.assertEqual(load_workbook(path).active['A2'].value,"'=1+2")

if __name__=='__main__':unittest.main()
