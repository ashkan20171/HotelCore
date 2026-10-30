import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from branch_trend_excel import validate_trend_rows,export_trend_excel

class TrendExcelTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'month':'2026-02','receipts':120,'expenses':20,'net':100},{'month':'2026-01','receipts':50,'expenses':70,'net':-20}]
    def test_sort(self):self.assertEqual(validate_trend_rows(self.rows)[0][0],'2026-01')
    def test_empty(self):self.assertEqual(validate_trend_rows([]),[])
    def test_duplicate(self):
        with self.assertRaises(ValueError):validate_trend_rows(self.rows+self.rows[:1])
    def test_invalid_month(self):
        with self.assertRaises(ValueError):validate_trend_rows([dict(self.rows[0],month='2026-13')])
    def test_invalid_net(self):
        with self.assertRaises(ValueError):validate_trend_rows([dict(self.rows[0],net=3)])
    def test_bool_amount(self):
        with self.assertRaises(ValueError):validate_trend_rows([dict(self.rows[0],net=True)])
    def test_negative_receipts(self):
        with self.assertRaises(ValueError):validate_trend_rows([dict(self.rows[0],receipts=-1)])
    def test_language(self):
        with self.assertRaises(ValueError):export_trend_excel('bad.xlsx',self.rows,'xx')
    def test_excel(self):
        try:from openpyxl import load_workbook
        except ImportError:self.skipTest('openpyxl unavailable')
        with TemporaryDirectory() as d:
            p=export_trend_excel(Path(d)/'trend.xlsx',self.rows,'en')
            ws=load_workbook(p).active
            self.assertEqual(ws['A2'].value,'2026-01')
            self.assertEqual(ws['D3'].value,100)
            self.assertEqual(len(ws._charts),1)
    def test_persian(self):
        try:from openpyxl import load_workbook
        except ImportError:self.skipTest('openpyxl unavailable')
        with TemporaryDirectory() as d:
            ws=load_workbook(export_trend_excel(Path(d)/'fa.xlsx',[], 'fa')).active
            self.assertTrue(ws.sheet_view.rightToLeft)
