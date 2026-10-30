import sqlite3
import unittest
from first_run_security import validate_admin_credentials, needs_admin_setup, create_first_admin

class FirstRunSecurityTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, salt TEXT NOT NULL, role TEXT NOT NULL)')
 def test_requires_setup(self):
  self.assertTrue(needs_admin_setup(self.db))
 def test_create_admin(self):
  create_first_admin(self.db,'owner','Strong&Pass1234','Strong&Pass1234')
  self.assertFalse(needs_admin_setup(self.db))
  username,digest,salt,role=self.db.execute('SELECT username,password_hash,salt,role FROM users').fetchone()
  self.assertEqual((username,role),('owner','admin'))
  self.assertNotEqual(digest,'Strong&Pass1234')
  self.assertEqual(len(salt),32)
 def test_reject_second_admin(self):
  create_first_admin(self.db,'owner','Strong&Pass1234','Strong&Pass1234')
  with self.assertRaises(PermissionError):
   create_first_admin(self.db,'another','Strong&Pass1234','Strong&Pass1234')
 def test_reject_short_password(self):
  with self.assertRaises(ValueError):validate_admin_credentials('owner','Short1!','Short1!')
 def test_reject_mismatch(self):
  with self.assertRaises(ValueError):validate_admin_credentials('owner','Strong&Pass1234','Strong&Pass1235')
 def test_reject_weak_password(self):
  with self.assertRaises(ValueError):validate_admin_credentials('owner','onlylowercase12345','onlylowercase12345')
 def test_reject_username_in_password(self):
  with self.assertRaises(ValueError):validate_admin_credentials('owner','OWNER&Pass1234','OWNER&Pass1234')
 def test_reject_bad_username(self):
  with self.assertRaises(ValueError):validate_admin_credentials('a b','Strong&Pass1234','Strong&Pass1234')
 def test_invalid_does_not_create_account(self):
  with self.assertRaises(ValueError):create_first_admin(self.db,'owner','bad','bad')
  self.assertTrue(needs_admin_setup(self.db))
