import sqlite3
import tempfile
import unittest
from pathlib import Path
from branch_cashflow import migrate,record_expense,cashflow,export_cashflow

class BranchCashflowTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript('''CREATE TABLE branches(id INTEGER,name TEXT,active INTEGER);
        CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
        CREATE TABLE users(id INTEGER);
        CREATE TABLE reservations(id INTEGER,branch_id INTEGER);
        CREATE TABLE payments(id INTEGER,reservation_id INTEGER,amount INTEGER,created_at TEXT);
        INSERT INTO branches VALUES(1,'A',1),(2,'B',1);
        INSERT INTO users VALUES(3);
        INSERT INTO user_branches VALUES(3,1);
        INSERT INTO reservations VALUES(1,1),(2,2);
        INSERT INTO payments VALUES(1,1,500,'2026-01-02 10:00:00'),(2,2,900,'2026-01-02 10:00:00');''')
        migrate(self.db)
    def tearDown(self):self.db.close()
    def test_idempotent_migration(self):
        migrate(self.db)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM branch_expenses').fetchone()[0],0)
    def test_branch_scope(self):
        with self.assertRaises(PermissionError):record_expense(self.db,branch_id=2,user_id=3,role='staff',category='X',description='',amount=10,spent_on='2026-01-02')
        with self.assertRaises(PermissionError):cashflow(self.db,branch_id=2,user_id=3,role='staff',start='2026-01-01',end='2026-01-04')
    def test_cash_movement(self):
        record_expense(self.db,branch_id=1,user_id=3,role='staff',category='Supplies',description='Test',amount=120,spent_on='2026-01-02')
        result=cashflow(self.db,branch_id=1,user_id=3,role='staff',start='2026-01-01',end='2026-01-04')
        self.assertEqual((result['receipts'],result['expenses'],result['net_cash_movement']),(500,120,380))
        self.assertEqual(result['expense_count'],1)
    def test_date_boundaries(self):
        record_expense(self.db,branch_id=1,user_id=3,role='staff',category='X',description='',amount=100,spent_on='2026-01-04')
        self.assertEqual(cashflow(self.db,branch_id=1,user_id=3,role='staff',start='2026-01-01',end='2026-01-04')['expenses'],0)
    def test_invalid_amount_and_date(self):
        for amount in (0,-1,True,1.2):
            with self.assertRaises(ValueError):record_expense(self.db,branch_id=1,user_id=3,role='staff',category='X',description='',amount=amount,spent_on='2026-01-02')
        with self.assertRaises(ValueError):cashflow(self.db,branch_id=1,user_id=3,role='staff',start='2026-01-04',end='2026-01-01')
    def test_excel(self):
        try:from openpyxl import load_workbook
        except ImportError:self.skipTest('openpyxl unavailable')
        with tempfile.TemporaryDirectory() as folder:
            for lang in ('fa','en'):
                path=Path(folder)/(lang+'.xlsx')
                report=dict(receipts=100,expenses=20,net_cash_movement=80,expense_rows=[('2026-01-02','=2+2','+cmd',20)])
                export_cashflow(path,report,start='2026-01-01',end='2026-01-03',branch_name='=evil',language=lang)
                ws=load_workbook(path).active
                self.assertTrue(ws['B1'].value.startswith("'="))
                self.assertEqual(ws['B8'].data_type,'s')
                self.assertEqual(ws.sheet_view.rightToLeft,lang=='fa')
