import sqlite3
import unittest
from security_alerts_v113 import migrate as alerts_migrate
from security_notifications_v114 import sync_alerts,inbox,unread_count,archive,restore,mark_read

class ArchiveNotificationTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,role TEXT,active INTEGER)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?)',[(1,'admin',1),(2,'reception',1)])
  alerts_migrate(self.db)
  self.db.execute("INSERT INTO security_alert_history(actor_id,days,severity,failed_attempts,previous_attempts,threshold) VALUES(1,7,'high',8,2,5)")
  sync_alerts(self.db,1)
 def test_archive_hides_from_inbox_and_badge(self):
  nid=inbox(self.db,1)[0][0]
  archive(self.db,1,nid)
  self.assertEqual(unread_count(self.db,1),0)
  self.assertEqual(inbox(self.db,1),[])
  self.assertEqual(len(inbox(self.db,1,status='archived')),1)
 def test_restore_is_read(self):
  nid=inbox(self.db,1)[0][0];archive(self.db,1,nid);restore(self.db,1,nid)
  self.assertEqual(len(inbox(self.db,1)),1)
  self.assertEqual(unread_count(self.db,1),0)
 def test_invalid_or_repeated_actions(self):
  nid=inbox(self.db,1)[0][0];archive(self.db,1,nid)
  for fn in (archive,mark_read):
   with self.assertRaises(ValueError):fn(self.db,1,nid)
  restore(self.db,1,nid)
  with self.assertRaises(ValueError):restore(self.db,1,nid)
 def test_access_restricted(self):
  nid=inbox(self.db,1)[0][0]
  for fn in (archive,restore):
   with self.assertRaises(PermissionError):fn(self.db,2,nid)
 def test_idempotent_schema_upgrade(self):
  from security_notifications_v114 import migrate
  migrate(self.db);migrate(self.db)
  self.assertIn('archived_at',[r[1] for r in self.db.execute('PRAGMA table_info(security_notifications)')])
