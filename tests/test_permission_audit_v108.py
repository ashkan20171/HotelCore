import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from permission_audit import migrate,record_change,recent_changes,export_changes_csv
from permission_policy import migrate as migrate_policy,set_override
from security_sessions import migrate as migrate_sessions

class PermissionAuditTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT,active INTEGER)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?)',[(1,'admin','admin',1),(2,'reception','reception',1)])
  self.db.execute('CREATE TABLE security_events(id INTEGER PRIMARY KEY,actor_id INTEGER,target_id INTEGER,event TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
  migrate(self.db);migrate_policy(self.db);migrate_sessions(self.db)
 def test_change_records_old_and_new(self):
  set_override(self.db,1,2,'reservations.manage',False)
  set_override(self.db,1,2,'reservations.manage',True)
  rows=recent_changes(self.db,1,target_id=2)
  self.assertEqual(rows[0][4:6],('deny','allow'))
  self.assertEqual(rows[1][4:6],('default','deny'))
 def test_default_removes_override_and_audits(self):
  set_override(self.db,1,2,'reservations.manage',False)
  set_override(self.db,1,2,'reservations.manage',None)
  self.assertEqual(recent_changes(self.db,1,target_id=2)[0][5],'default')
 def test_non_admin_denied(self):
  with self.assertRaises(PermissionError):recent_changes(self.db,2)
 def test_invalid_limit(self):
  with self.assertRaises(ValueError):recent_changes(self.db,1,limit=501)
 def test_export_formula_safe(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'audit.csv'
   export_changes_csv(path,[('now','=bad','@user','+cmd','deny','allow')])
   with path.open(encoding='utf-8-sig',newline='') as handle: row=next(csv.DictReader(handle))
   self.assertTrue(row['actor'].startswith("'="))
   self.assertTrue(row['target'].startswith("'@"))
 def test_invalid_permission_denied(self):
  with self.assertRaises(ValueError):set_override(self.db,1,2,'not.a.permission',True)

if __name__=='__main__':unittest.main()
