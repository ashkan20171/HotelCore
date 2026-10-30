import unittest
import sqlite3
from datetime import datetime,timezone
from unittest.mock import patch
from operational_reports_v130 import REPORTS,fetch,validate

class OperationalReportsTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript('''CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT,kind TEXT,rate INTEGER,status TEXT);
        CREATE TABLE guests(id INTEGER PRIMARY KEY,name TEXT,phone TEXT,national_id TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,checkin TEXT,checkout TEXT,status TEXT,created_at TEXT);
        CREATE TABLE payments(id INTEGER PRIMARY KEY,reservation_id INTEGER,amount INTEGER,method TEXT,created_at TEXT);
        CREATE TABLE expenses(id INTEGER PRIMARY KEY,category TEXT,description TEXT,amount INTEGER,created_at TEXT);
        INSERT INTO rooms VALUES(1,'101','Suite',500,'active');
        INSERT INTO guests VALUES(1,'Guest','SECRET_PHONE','SECRET_NATIONAL_ID');
        INSERT INTO reservations VALUES(1,1,1,'2026-10-22','2026-10-24','confirmed','2026-10-23 12:00:00');
        INSERT INTO payments VALUES(1,1,100,'card','2026-10-23 12:00:00');
        INSERT INTO expenses VALUES(1,'Maintenance','Air conditioner',25,'2026-10-23 12:00:00');''')
        self.now=datetime(2026,10,23,18,tzinfo=timezone.utc)
    def tearDown(self):self.db.close()
    def test_all_report_types(self):
        with patch('operational_reports_v130._actor'):
            for kind,spec in REPORTS.items():
                rows=fetch(self.db,1,report=kind,columns=spec['default'],now=self.now)
                self.assertEqual(len(rows),1,kind)
    def test_no_sensitive_guest_columns(self):
        self.assertNotIn('phone',REPORTS['guests']['columns'])
        self.assertNotIn('national_id',REPORTS['guests']['columns'])
    def test_reject_sql_injection(self):
        for bad in (('id;DROP TABLE guests',),(),('room','room')):
            with self.assertRaises(ValueError):validate('rooms',bad)
    def test_reject_unknown_report(self):
        with self.assertRaises(ValueError):validate('users',('id',))
    def test_limit_and_day_validation(self):
        for days,limit in ((0,20),(366,20),(1,1001),(True,20)):
            with self.assertRaises(ValueError):validate('rooms',('room',),days,limit)
    def test_date_range(self):
        with patch('operational_reports_v130._actor'):
            rows=fetch(self.db,1,report='payments',columns=('amount',),days=1,now=datetime(2026,11,1,tzinfo=timezone.utc))
            self.assertEqual(rows,[])
    def test_fail_closed_actor(self):
        with patch('operational_reports_v130._actor',side_effect=PermissionError('Denied')):
            with self.assertRaises(PermissionError):fetch(self.db,1,report='rooms',columns=('room',))
    def test_naive_datetime(self):
        with patch('operational_reports_v130._actor'):
            with self.assertRaises(ValueError):fetch(self.db,1,report='rooms',columns=('room',),now=datetime(2026,10,23))
if __name__=='__main__':unittest.main()
