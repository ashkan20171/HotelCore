import sqlite3
import unittest
from room_type_comparison import compare_room_types

class CompareRoomTypesTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""
        CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER);
        CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
        CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT,kind TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
        CREATE TABLE booking_rates(reservation_id INTEGER,accommodation_total INTEGER);
        INSERT INTO branches VALUES(1,'Main',1),(2,'Other',1);
        INSERT INTO user_branches VALUES(4,1);
        INSERT INTO rooms VALUES(1,1,'فعال','Suite'),(2,2,'فعال','Suite');
        INSERT INTO reservations VALUES(1,1,1,'2026-10-01','2026-10-03','رزرو شده'),(2,1,1,'2026-10-03','2026-10-05','رزرو شده');
        INSERT INTO booking_rates VALUES(1,200),(2,400);
        """)
    def tearDown(self):self.db.close()
    def compare(self,branch=1):
        return compare_room_types(self.db,branch_id=branch,start='2026-10-03',end='2026-10-05',user_id=4,role='staff')
    def test_period_and_deltas(self):
        report=self.compare(); self.assertEqual(report['previous_start'],'2026-10-01')
        suite=report['rows'][0];self.assertEqual(suite['adr_now'],200)
        self.assertEqual(suite['adr_delta'],100)
        self.assertEqual(suite['revpar_delta'],100)
    def test_access_denied(self):
        with self.assertRaises(PermissionError):self.compare(branch=2)
    def test_missing_quote_hides_delta(self):
        self.db.execute('DELETE FROM booking_rates WHERE reservation_id=1')
        self.assertIsNone(self.compare()['rows'][0]['adr_delta'])
    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            compare_room_types(self.db,branch_id=1,start='2026-10-05',end='2026-10-03',user_id=4,role='staff')
