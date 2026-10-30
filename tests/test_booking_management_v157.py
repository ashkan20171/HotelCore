import unittest,tempfile
from pathlib import Path
from booking_management_v157 import weekly_coverage,report_rows,export_booking_excel,export_booking_pdf
from datetime import date,timedelta
class BookingManagementTests(unittest.TestCase):
    def rows(self,n=10):
        return [{'date':(date(2026,11,2)+timedelta(days=i)).isoformat(),'booked_rooms':i%3,'total_rooms':3,'booked_pct':round((i%3)/3*100,1),'low_demand':i%3==0} for i in range(n)]
    def test_weekly_change(self):
        weeks=weekly_coverage(self.rows(),week_start=0)
        self.assertEqual(len(weeks),2);self.assertIsNone(weeks[0]['change_pp']);self.assertIsNotNone(weeks[1]['change_pp'])
    def test_partial_week(self):self.assertEqual(sum(w['days'] for w in weekly_coverage(self.rows())),10)
    def test_invalid_room_counts(self):
        rows=self.rows();rows[0]['booked_rooms']=4
        with self.assertRaises(ValueError):report_rows(rows)
    def test_invalid_extension(self):
        with self.assertRaises(ValueError):export_booking_excel(self.rows(),'wrong.csv')
    def test_excel_export(self):
        try:import openpyxl
        except ImportError:self.skipTest('openpyxl unavailable')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'booking.xlsx';export_booking_excel(self.rows(),path)
            wb=openpyxl.load_workbook(path);self.assertEqual(len(wb['Booking coverage']['A']) ,11)
            self.assertIn('Weekly comparison',wb.sheetnames)
    def test_pdf_export(self):
        try:import reportlab
        except ImportError:self.skipTest('reportlab unavailable')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'booking.pdf';export_booking_pdf(self.rows(),path)
            self.assertTrue(path.read_bytes().startswith(b'%PDF'))
