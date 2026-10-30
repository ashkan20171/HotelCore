import sqlite3
import tempfile
import unittest
from pathlib import Path
from stay_performance import allocated_quote, estimated_branch_performance, export_estimated_performance

class PerformanceTests(unittest.TestCase):
    def test_overlap(self):
        amount,nights=allocated_quote(400,'2026-01-01','2026-01-05','2026-01-02','2026-01-04')
        self.assertEqual((amount,nights),(200,2))
    def test_no_overlap(self):
        self.assertEqual(allocated_quote(400,'2026-01-01','2026-01-05','2026-02-01','2026-02-03')[1],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):allocated_quote(-1,'2026-01-01','2026-01-02','2026-01-01','2026-01-02')
    def test_scope_and_missing(self):
        db=sqlite3.connect(':memory:')
        db.executescript("""CREATE TABLE branches(id INTEGER,name TEXT,active INTEGER);
        CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
        CREATE TABLE rooms(id INTEGER,branch_id INTEGER,status TEXT);
        CREATE TABLE reservations(id INTEGER,branch_id INTEGER,status TEXT,checkin TEXT,checkout TEXT);
        CREATE TABLE booking_rates(reservation_id INTEGER,accommodation_total INTEGER);
        INSERT INTO branches VALUES(1,'A',1),(2,'B',1);
        INSERT INTO user_branches VALUES(3,1);
        INSERT INTO rooms VALUES(1,1,'فعال'),(2,2,'فعال');
        INSERT INTO reservations VALUES(1,1,'رزرو شده','2026-01-01','2026-01-03'),(2,2,'رزرو شده','2026-01-01','2026-01-03');
        INSERT INTO booking_rates VALUES(1,400),(2,900);""")
        result=estimated_branch_performance(db,branch_id=1,start='2026-01-01',end='2026-01-03',user_id=3,role='staff')
        self.assertEqual(result['estimated_accommodation_value'],400)
        self.assertEqual(result['estimated_adr'],200)
        self.assertEqual(result['estimated_revpar'],200)
        with self.assertRaises(PermissionError):estimated_branch_performance(db,branch_id=2,start='2026-01-01',end='2026-01-03',user_id=3,role='staff')
        db.execute("DELETE FROM booking_rates WHERE reservation_id=1")
        result=estimated_branch_performance(db,branch_id=1,start='2026-01-01',end='2026-01-03',user_id=3,role='staff')
        self.assertEqual(result['missing_quotes'],1)
        self.assertIsNone(result['estimated_adr'])
        db.close()
    def test_export(self):
        try:from openpyxl import load_workbook
        except ImportError:self.skipTest('openpyxl not installed')
        with tempfile.TemporaryDirectory() as folder:
            for lang in ('fa','en'):
                path=Path(folder)/(lang+'.xlsx')
                row=dict(branch_name='=SUM(1,2)',rooms=1,occupied_room_nights=1,available_room_nights=2,estimated_accommodation_value=100,estimated_adr=100,estimated_revpar=50,missing_quotes=0)
                export_estimated_performance(path,[row],start='2026-01-01',end='2026-01-03',language=lang)
                sheet=load_workbook(path).active
                self.assertEqual(sheet['A5'].data_type,'s')
                self.assertTrue(sheet['A5'].value.startswith("'="))
                self.assertEqual(sheet.sheet_view.rightToLeft,lang=='fa')
