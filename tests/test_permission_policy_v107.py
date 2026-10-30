import sqlite3
import unittest
from permission_policy import migrate,effective_permissions,set_override,require_user_permission
from user_access_management import migrate as migrate_users
from security_overview import require_permission

class PolicyTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT,password_hash TEXT,salt TEXT)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?,?)',[(1,'boss','admin','h','s'),(2,'clerk','reception','h','s')])
  migrate_users(self.db);migrate(self.db)
 def test_role_default(self):
  self.assertIn('reservations.manage',effective_permissions(self.db,2))
 def test_deny(self):
  set_override(self.db,1,2,'reservations.manage',False)
  with self.assertRaises(PermissionError):require_permission(self.db,2,'reservations.manage')
 def test_restore_default(self):
  set_override(self.db,1,2,'reservations.manage',False)
  set_override(self.db,1,2,'reservations.manage',None)
  self.assertTrue(require_user_permission(self.db,2,'reservations.manage'))
 def test_reserved_permission(self):
  with self.assertRaises(PermissionError):set_override(self.db,1,2,'users.manage',True)
 def test_admin_immutable(self):
  with self.assertRaises(PermissionError):set_override(self.db,1,1,'reservations.view',False)
 def test_nonadmin_cannot_edit(self):
  with self.assertRaises(PermissionError):set_override(self.db,2,1,'reservations.view',False)
 def test_invalid(self):
  with self.assertRaises(ValueError):set_override(self.db,1,2,'nonsense',True)
 def test_audit(self):
  set_override(self.db,1,2,'reservations.view',False)
  self.assertEqual(self.db.execute('SELECT event FROM security_events').fetchone()[0],'permission_override_changed')
