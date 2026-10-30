import sqlite3
import unittest
from room_type_analytics import room_type_performance, room_type_alerts

class RoomTypeAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript('''
        CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER);
        CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
        CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT,kind TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
        CREATE TABLE booking_rates(reservation_id INTEGER,accommodation_total INTEGER);
        INSERT INTO branches VALUES(1,'Main',1),(2,'Other',1);
        INSERT INTO user_branches VALUES(4,1);
        INSERT INTO rooms VALUES(1,1,'فعال','Suite'),(2,1,'فعال','Suite'),(3,1,'فعال','Standard'),(4,2,'فعال','Suite');
        INSERT INTO reservations VALUES(1,1,1,'2026-10-01','2026-10-03','رزرو شده'),(2,2,4,'2026-10-01','2026-10-03','رزرو شده');
        INSERT INTO booking_rates VALUES(1,400),(2,800);
        ''')
    def tearDown(self): self.db.close()
    def report(self, **kwargs):
        return room_type_performance(self.db,branch_id=1,start='2026-10-01',end='2026-10-03',user_id=4,role='staff',**kwargs)
    def test_aggregates_and_adr(self):
        rows={r['kind']:r for r in self.report()}
        self.assertEqual(rows['Suite']['estimated_value'],400)
        self.assertEqual(rows['Suite']['estimated_adr'],200)
        self.assertEqual(rows['Suite']['estimated_revpar'],100)
        self.assertEqual(rows['Suite']['occupancy_percent'],50)
        self.assertEqual(rows['Standard']['occupancy_percent'],0)
    def test_branch_isolation(self):
        with self.assertRaises(PermissionError):
            room_type_performance(self.db,branch_id=2,start='2026-10-01',end='2026-10-03',user_id=4,role='staff')
    def test_missing_quote(self):
        self.db.execute('DELETE FROM booking_rates WHERE reservation_id=1')
        suite=next(r for r in self.report() if r['kind']=='Suite')
        self.assertIsNone(suite['estimated_adr'])
        self.assertEqual(suite['missing_quotes'],1)
        self.assertTrue(room_type_alerts([suite], 'en'))
    def test_invalid_dates(self):
        with self.assertRaises(ValueError):
            room_type_performance(self.db,branch_id=1,start='2026-10-03',end='2026-10-01',user_id=4,role='staff')
    def test_partial_allocation(self):
        rows=room_type_performance(self.db,branch_id=1,start='2026-10-02',end='2026-10-03',user_id=4,role='staff')
        suite=next(r for r in rows if r['kind']=='Suite')
        self.assertEqual(suite['estimated_value'],200)
