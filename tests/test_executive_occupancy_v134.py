import sqlite3,unittest
from datetime import date
from executive_occupancy_v134 import daily_occupancy,management_alerts
class OccupancyTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY);CREATE TABLE reservations(room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
  INSERT INTO rooms VALUES(1);INSERT INTO rooms VALUES(2);
  INSERT INTO reservations VALUES(1,'2026-10-01','2026-10-04','confirmed');
  INSERT INTO reservations VALUES(1,'2026-10-01','2026-10-04','confirmed');
  INSERT INTO reservations VALUES(2,'2026-10-02','2026-10-03','cancelled');""")
 def tearDown(self):self.db.close()
 def test_daily_occupancy_deduplicated(self):
  r=daily_occupancy(self.db,date(2026,10,1),date(2026,10,4))
  self.assertEqual([x['occupancy_pct'] for x in r],[50,50,50,0])
 def test_no_rooms(self):
  self.db.execute('DELETE FROM rooms')
  self.assertEqual(daily_occupancy(self.db,date(2026,10,1),date(2026,10,1))[0]['occupancy_pct'],0)
 def test_date_validation(self):
  with self.assertRaises(ValueError):daily_occupancy(self.db,date(2026,10,3),date(2026,10,1))
 def test_alerts(self):
  self.assertEqual(management_alerts({'room_count':2,'occupancy_pct':20,'income':100,'expenses':95},{'income':200}),['low_occupancy','high_expense_ratio','receipts_decline'])
 def test_alert_thresholds(self):
  with self.assertRaises(ValueError):management_alerts({}, {},low_occupancy=True)
