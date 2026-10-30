import csv
import tempfile
import unittest
from pathlib import Path
from branch_csv import safe_cell, export_branch_reservations

class BranchCSVTests(unittest.TestCase):
    def test_formula(self):
        for value in ['=SUM(1,2)', '+cmd', '-cmd', '@SUM(A1)', '  =1', '\t=1']:
            self.assertTrue(safe_cell(value).startswith("'"))
    def test_normal(self):
        self.assertEqual(safe_cell('مهمان'), 'مهمان')
    def test_null(self):
        self.assertEqual(safe_cell(None), '')
    def test_fa_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'out.csv'
            export_branch_reservations(path,[(1,'101','=2+2','2026-01-01','2026-01-03')])
            self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'))
            with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.reader(f))
            self.assertEqual(rows[1][2],"'=2+2")
            self.assertEqual(rows[0][0],'شناسه رزرو')
    def test_en_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'out.csv'
            export_branch_reservations(path,[], 'en')
            self.assertIn('Reservation ID',path.read_text(encoding='utf-8-sig'))
    def test_invalid_language(self):
        with self.assertRaises(ValueError):export_branch_reservations('unused.csv',[], 'de')
    def test_invalid_row(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):export_branch_reservations(Path(folder)/'x.csv',[(1,2)])
