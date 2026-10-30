import hashlib
import sqlite3
import unittest
from password_security import change_password, validate_new_password, verify_password

class PasswordTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE users(username TEXT PRIMARY KEY,password_hash TEXT,salt TEXT)')
        salt='a'*32
        digest=hashlib.pbkdf2_hmac('sha256',b'OldPassword123!',bytes.fromhex(salt),240000).hex()
        self.db.execute('INSERT INTO users VALUES(?,?,?)',('alice',digest,salt))
    def tearDown(self):self.db.close()
    def test_rotate(self):
        self.assertTrue(change_password(self.db,'alice','OldPassword123!','NewPassword456!','NewPassword456!'))
        row=self.db.execute('SELECT salt,password_hash FROM users').fetchone()
        self.assertTrue(verify_password('NewPassword456!',*row))
        self.assertFalse(verify_password('OldPassword123!',*row))
    def test_wrong_old_preserves(self):
        before=self.db.execute('SELECT password_hash FROM users').fetchone()
        with self.assertRaises(ValueError):change_password(self.db,'alice','wrong','NewPassword456!','NewPassword456!')
        self.assertEqual(before,self.db.execute('SELECT password_hash FROM users').fetchone())
    def test_confirmation(self):
        with self.assertRaises(ValueError):change_password(self.db,'alice','OldPassword123!','NewPassword456!','Mismatch123!')
    def test_short(self):
        with self.assertRaises(ValueError):validate_new_password('short1')
    def test_username(self):
        with self.assertRaises(ValueError):validate_new_password('alicePassword123','alice')
    def test_same_password(self):
        with self.assertRaises(ValueError):change_password(self.db,'alice','OldPassword123!','OldPassword123!','OldPassword123!')
    def test_malformed_hash(self):self.assertFalse(verify_password('test','xyz','bad'))
    def test_only_letters(self):
        with self.assertRaises(ValueError):validate_new_password('abcdefghijklmnop')
