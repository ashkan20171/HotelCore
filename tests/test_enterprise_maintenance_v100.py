import sqlite3
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from enterprise_maintenance import database_health,create_consistent_backup
from enterprise_cli import main

TABLES=('rooms','guests','reservations','payments','users')

class EnterpriseMaintenanceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.base=Path(self.tmp.name)
  self.db=self.base/'hotel.db'
  with sqlite3.connect(self.db) as conn:
   for table in TABLES:conn.execute(f'CREATE TABLE {table}(id INTEGER PRIMARY KEY)')
   conn.execute('INSERT INTO rooms(id) VALUES(1)')
 def test_health(self):
  result=database_health(self.db)
  self.assertTrue(result['ok'])
  self.assertEqual(result['foreign_key_violations'],0)
 def test_missing_database(self):
  self.assertFalse(database_health(self.base/'missing.db')['ok'])
 def test_missing_tables(self):
  with sqlite3.connect(self.db) as conn:conn.execute('DROP TABLE payments')
  self.assertIn('payments',database_health(self.db)['tables_missing'])
 def test_consistent_backup(self):
  backup=create_consistent_backup(self.db,self.base,now=datetime(2026,10,23,tzinfo=timezone.utc))
  self.assertTrue(database_health(backup)['ok'])
  with sqlite3.connect(backup) as conn:
   self.assertEqual(conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0],1)
 def test_no_overwrite(self):
  stamp=datetime(2026,10,23,tzinfo=timezone.utc)
  create_consistent_backup(self.db,self.base,now=stamp)
  with self.assertRaises(FileExistsError):create_consistent_backup(self.db,self.base,now=stamp)
 def test_bad_timestamp(self):
  with self.assertRaises(ValueError):create_consistent_backup(self.db,self.base,now=datetime(2026,10,23))
 def test_missing_directory(self):
  with self.assertRaises(NotADirectoryError):create_consistent_backup(self.db,self.base/'missing')
 def test_cli_health(self):
  self.assertEqual(main(['--database',str(self.db),'health']),0)
