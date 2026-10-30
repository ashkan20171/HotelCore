import sqlite3
import unittest
from branches import migrate_branches, add_branch, assign_room

class BranchTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT)')
        self.db.execute("INSERT INTO rooms(number) VALUES('101')")
        migrate_branches(self.db)
    def tearDown(self):self.db.close()
    def test_legacy_rooms_default_to_main_branch(self):
        self.assertEqual(self.db.execute('SELECT branch_id FROM rooms').fetchone()[0],1)
    def test_migration_idempotent(self):
        migrate_branches(self.db)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM branches').fetchone()[0],1)
    def test_create_and_assign(self):
        bid=add_branch(self.db,'شعبه دوم','تهران')
        assign_room(self.db,1,bid)
        self.assertEqual(self.db.execute('SELECT branch_id FROM rooms').fetchone()[0],bid)
    def test_reject_empty_name(self):
        with self.assertRaises(ValueError):add_branch(self.db,'  ')
    def test_reject_invalid_room(self):
        with self.assertRaises(ValueError):assign_room(self.db,999,1)

if __name__=='__main__':unittest.main()
