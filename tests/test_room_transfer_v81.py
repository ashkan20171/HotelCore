import sqlite3
import unittest
from room_transfer import transfer_booking

class TransferTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT,number TEXT,kind TEXT,rate INTEGER);
   CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
   CREATE TABLE booking_rates(reservation_id INTEGER PRIMARY KEY,accommodation_total INTEGER,calculated_at TEXT);
   CREATE TABLE seasonal_rates(id INTEGER PRIMARY KEY,room_kind TEXT,start_date TEXT,end_date TEXT,multiplier_percent INTEGER);
   CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER); CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
   INSERT INTO branches VALUES(1,'Main',1); INSERT INTO user_branches VALUES(1,1);
   INSERT INTO rooms VALUES(1,1,'فعال','101','Standard',100); INSERT INTO rooms VALUES(2,1,'فعال','102','Standard',100);
   INSERT INTO reservations VALUES(1,1,1,'2026-11-01','2026-11-03','رزرو شده');""")
  self.db.commit()
 def tearDown(self):self.db.close()
 def test_success(self):
  total=transfer_booking(self.db,user_id=1,role='admin',branch_id=1,reservation_id=1,destination_room_id=2)
  self.assertEqual(self.db.execute('SELECT room_id FROM reservations WHERE id=1').fetchone()[0],2)
  self.assertEqual(self.db.execute('SELECT source_room_id,destination_room_id FROM room_transfer_history').fetchone(),(1,2))
 def test_same_room_rollback(self):
  with self.assertRaises(ValueError):transfer_booking(self.db,user_id=1,role='admin',branch_id=1,reservation_id=1,destination_room_id=1)
  self.assertEqual(self.db.execute('SELECT room_id FROM reservations WHERE id=1').fetchone()[0],1)
 def test_overlap_rollback(self):
  self.db.execute("INSERT INTO reservations VALUES(2,1,2,'2026-11-02','2026-11-04','رزرو شده')");self.db.commit()
  with self.assertRaises(ValueError):transfer_booking(self.db,user_id=1,role='admin',branch_id=1,reservation_id=1,destination_room_id=2)
  self.assertEqual(self.db.execute('SELECT room_id FROM reservations WHERE id=1').fetchone()[0],1)
