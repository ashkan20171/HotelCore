import unittest
import tempfile
from pathlib import Path
from room_transfer_analytics import summarize_transfers, export_transfers_excel

class TransferAnalyticsTests(unittest.TestCase):
 def setUp(self):
  self.rows=[(1,'2026-09-02 10:00',4,'101','102','admin'),(2,'2026-09-03 12:00',5,'101','103','admin'),(3,'2026-10-01 09:00',6,'102','103','manager')]
 def test_total(self):self.assertEqual(summarize_transfers(self.rows)['total'],3)
 def test_popular_source(self):self.assertEqual(summarize_transfers(self.rows)['by_source']['101'],2)
 def test_months(self):self.assertEqual(summarize_transfers(self.rows)['by_month']['2026-09'],2)
 def test_empty(self):self.assertEqual(summarize_transfers([])['total'],0)
 def test_excel(self):
  try:import openpyxl
  except ImportError:self.skipTest('openpyxl unavailable')
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'report.xlsx';export_transfers_excel(file,self.rows)
   wb=openpyxl.load_workbook(file)
   self.assertEqual(wb['Transfers'].max_row,4)
   self.assertEqual(wb['Summary']['B2'].value,3)
