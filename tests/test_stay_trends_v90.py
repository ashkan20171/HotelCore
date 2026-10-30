import sqlite3
import unittest
from stay_trends import previous_window, daily_occupancy, compare_periods

class StayTrendsTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript('''
        CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER);
        CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
        CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
        CREATE TABLE booking_rates(reservation_id INTEGER,accommodation_total INTEGER);
        INSERT INTO branches VALUES(1,'Main',1),(2,'Other',1);
        INSERT INTO user_branches VALUES(4,1);
        INSERT INTO rooms VALUES(1,1,'فعال'),(2,1,'فعال'),(3,2,'فعال');
        INSERT INTO reservations VALUES(1,1,'2026-10-02','2026-10-04','رزرو شده'),(2,2,'2026-10-02','2026-10-05','رزرو شده');
        INSERT INTO booking_rates VALUES(1,200),(2,600);
        ''')
    def tearDown(self): self.db.close()
    def test_previous_window(self): self.assertEqual(previous_window('2026-10-03','2026-10-06'),('2026-09-30','2026-10-03'))
    def test_daily_occupancy(self):
        data=daily_occupancy(self.db,branch_id=1,start='2026-10-01',end='2026-10-05',user_id=4,role='staff')
        self.assertEqual([x['occupied'] for x in data],[0,1,1,0]);self.assertEqual(data[1]['occupancy_percent'],50.0)
    def test_cross_branch_forbidden(self):
        with self.assertRaises(PermissionError):daily_occupancy(self.db,branch_id=2,start='2026-10-01',end='2026-10-05',user_id=4,role='staff')
    def test_compare(self):
        data=compare_periods(self.db,branch_id=1,start='2026-10-02',end='2026-10-04',user_id=4,role='staff')
        self.assertEqual(data['current']['occupancy_percent'],50.0)
        self.assertEqual(data['previous']['occupancy_percent'],0.0)
        self.assertEqual(data['changes']['occupancy_percent'],50.0)
    def test_invalid_window(self):
        with self.assertRaises(ValueError):previous_window('2026-10-05','2026-10-01')
