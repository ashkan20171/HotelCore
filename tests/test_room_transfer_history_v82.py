import sqlite3
import tempfile
import unittest
from pathlib import Path
from room_transfer_history import query_transfers, export_transfers_csv

class TransferHistoryTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT);
  CREATE TABLE room_transfer_history(id INTEGER PRIMARY KEY,reservation_id INTEGER,source_room_id INTEGER,destination_room_id INTEGER,branch_id INTEGER,actor TEXT,created_at TEXT);
  INSERT INTO rooms VALUES(1,'101'),(2,'102');
  INSERT INTO room_transfer_history VALUES(1,5,1,2,1,'admin','2026-10-20 10:00:00'),(2,6,2,1,2,'other','2026-10-21 10:00:00');""")
 def tearDown(self):self.db.close()
 def test_branch_scope(self):self.assertEqual([r[2] for r in query_transfers(self.db,branch_id=1)],[5])
 def test_reservation_filter(self):self.assertEqual(query_transfers(self.db,branch_id=1,reservation_id=6),[])
 def test_actor_filter(self):self.assertEqual(len(query_transfers(self.db,branch_id=1,actor='adm')),1)
 def test_date_filter(self):self.assertEqual(query_transfers(self.db,branch_id=1,date_from='2026-10-21'),[])
 def test_invalid_branch(self):
  with self.assertRaises(ValueError):query_transfers(self.db,branch_id=0)
 def test_invalid_limit(self):
  with self.assertRaises(ValueError):query_transfers(self.db,branch_id=1,limit=5000)
 def test_missing_table(self):
  db=sqlite3.connect(':memory:')
  try:self.assertEqual(query_transfers(db,branch_id=1),[])
  finally:db.close()
 def test_csv(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'history.csv';export_transfers_csv(path,query_transfers(self.db,branch_id=1))
   self.assertIn('admin',path.read_text(encoding='utf-8-sig'))
