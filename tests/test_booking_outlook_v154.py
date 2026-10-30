import sqlite3,unittest
from datetime import date
from booking_outlook_v154 import booking_outlook,outlook_summary

class OutlookTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(':memory:')
        self.conn.executescript("CREATE TABLE rooms(id INTEGER PRIMARY KEY);CREATE TABLE reservations(id INTEGER PRIMARY KEY,checkin TEXT,checkout TEXT,room_id INTEGER,status TEXT);INSERT INTO rooms VALUES(1),(2);INSERT INTO reservations VALUES(1,'2026-11-01','2026-11-03',1,'confirmed'),(2,'2026-11-01','2026-11-02',1,'confirmed'),(3,'2026-11-02','2026-11-04',2,'cancelled');")
    def tearDown(self):self.conn.close()
    def test_distinct_rooms_and_checkout_exclusion(self):
        rows=booking_outlook(self.conn,date(2026,11,1),3)
        self.assertEqual([r['booked_rooms'] for r in rows],[1,1,0])
        self.assertEqual([r['booked_pct'] for r in rows],[50,50,0])
    def test_summary(self):
        summary=outlook_summary(booking_outlook(self.conn,date(2026,11,1),3,low_threshold=40))
        self.assertEqual(summary['low_demand_days'],1)
    def test_invalid_bounds(self):
        with self.assertRaises(ValueError):booking_outlook(self.conn,date.today(),91)
        with self.assertRaises(ValueError):booking_outlook(self.conn,date.today(),2,-1)
    def test_empty_hotel(self):
        self.conn.execute('DELETE FROM rooms')
        self.assertEqual(outlook_summary(booking_outlook(self.conn,date(2026,11,1),2))['low_demand_days'],0)
