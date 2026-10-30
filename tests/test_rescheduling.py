import sqlite3, unittest
from pricing import migrate, migrate_booking_rates, reschedule, quote_reservation
class ReschedulingTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.execute('PRAGMA foreign_keys=ON')
  self.db.executescript("CREATE TABLE rooms(id INTEGER PRIMARY KEY,kind TEXT,rate INTEGER,status TEXT);CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);INSERT INTO rooms VALUES(1,'استاندارد',1000,'فعال');INSERT INTO reservations VALUES(1,1,'2026-10-20','2026-10-22','رزرو شده');")
  migrate(self.db);migrate_booking_rates(self.db)
 def tearDown(self):self.db.close()
 def test_seasonal_quote(self):
  self.db.execute("INSERT INTO seasonal_rates(room_kind,start_date,end_date,multiplier_percent) VALUES('همه','2026-10-21','2026-10-24',150)")
  self.assertEqual(quote_reservation(self.db,1,'2026-10-20','2026-10-23'),4000)
 def test_reschedule(self):
  self.assertEqual(reschedule(self.db,1,1,'2026-10-22','2026-10-24'),2000)
  self.assertEqual(self.db.execute('SELECT accommodation_total FROM booking_rates').fetchone()[0],2000)
 def test_overlap(self):
  self.db.execute("INSERT INTO reservations VALUES(2,1,'2026-10-23','2026-10-25','رزرو شده')")
  with self.assertRaises(ValueError):reschedule(self.db,1,1,'2026-10-22','2026-10-24')
 def test_checked_in_cannot_edit(self):
  self.db.execute("UPDATE reservations SET status='پذیرش شده' WHERE id=1")
  with self.assertRaises(ValueError):reschedule(self.db,1,1,'2026-10-22','2026-10-24')
