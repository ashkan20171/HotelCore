import sqlite3
import unittest
from billing import migrate, calculate_invoice, apply_adjustment

class BillingTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT,rate INTEGER);
  CREATE TABLE guests(id INTEGER PRIMARY KEY,name TEXT);
  CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
  CREATE TABLE payments(id INTEGER PRIMARY KEY,reservation_id INTEGER,amount INTEGER);
  CREATE TABLE service_orders(id INTEGER PRIMARY KEY,reservation_id INTEGER,quantity INTEGER,unit_price INTEGER);
  CREATE TABLE discounts(code TEXT PRIMARY KEY,percent INTEGER,active INTEGER);
  INSERT INTO rooms VALUES(1,'101',1000);INSERT INTO guests VALUES(1,'Ali');
  INSERT INTO reservations VALUES(1,1,1,'2026-10-01','2026-10-04','رزرو شده');
  INSERT INTO payments VALUES(1,1,1500);INSERT INTO service_orders VALUES(1,1,2,250);
  INSERT INTO discounts VALUES('WELCOME10',10,1);INSERT INTO discounts VALUES('OLD',20,0);""")
  migrate(self.db)
 def tearDown(self):self.db.close()
 def test_invoice(self):
  inv=calculate_invoice(self.db,1)
  self.assertEqual((inv['subtotal'],inv['total'],inv['balance']),(3500,3500,2000))
 def test_discount_tax(self):
  apply_adjustment(self.db,1,'welcome10',9)
  inv=calculate_invoice(self.db,1)
  self.assertEqual((inv['discount'],inv['tax'],inv['total'],inv['balance']),(350,283,3433,1933))
 def test_inactive_code_rejected(self):
  with self.assertRaises(ValueError):apply_adjustment(self.db,1,'OLD',0)
 def test_bad_tax_rejected(self):
  with self.assertRaises(ValueError):apply_adjustment(self.db,1,'',101)
 def test_migration_idempotent(self):
  migrate(self.db);apply_adjustment(self.db,1,'',0);migrate(self.db)
  self.assertEqual(calculate_invoice(self.db,1)['total'],3500)

if __name__=='__main__':unittest.main()
