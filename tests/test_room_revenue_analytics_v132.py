import sqlite3,unittest
from datetime import date
from room_revenue_analytics_v132 import room_value_by_type
class RoomAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,kind TEXT,rate INTEGER);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
        INSERT INTO rooms VALUES(1,'Suite',200),(2,'Suite',100),(3,'Standard',80);
        INSERT INTO reservations VALUES(1,1,'2026-10-21','2026-10-24','confirmed'),(2,2,'2026-10-22','2026-10-24','cancelled');""")
    def tearDown(self):self.db.close()
    def test_estimates(self):
        rows=room_value_by_type(self.db,date(2026,10,22),date(2026,10,23))
        suite=next(r for r in rows if r['type']=='Suite')
        self.assertEqual(suite['booked_nights'],2)
        self.assertEqual(suite['booked_value'],400)
        self.assertEqual(suite['estimated_adr'],200)
        self.assertEqual(suite['estimated_revpar'],100)
    def test_empty_room_type(self):
        standard=next(r for r in room_value_by_type(self.db,date(2026,10,22),date(2026,10,23)) if r['type']=='Standard')
        self.assertEqual(standard['estimated_adr'],0)
    def test_invalid_dates(self):
        with self.assertRaises(ValueError):room_value_by_type(self.db,date(2026,10,24),date(2026,10,22))
    def test_partial_overlap(self):
        rows=room_value_by_type(self.db,date(2026,10,23),date(2026,10,25))
        self.assertEqual(next(r for r in rows if r['type']=='Suite')['booked_nights'],1)
