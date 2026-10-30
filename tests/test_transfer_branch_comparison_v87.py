import csv
import os
import sqlite3
import tempfile
import unittest
from transfer_branch_comparison import compare_transfers, export_comparison_csv


class BranchComparisonTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript('''
            CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER);
            CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
            CREATE TABLE room_transfer_history(id INTEGER PRIMARY KEY,branch_id INTEGER,reservation_id INTEGER,
                source_room_id INTEGER,destination_room_id INTEGER,actor TEXT,created_at TEXT);
            INSERT INTO branches VALUES(1,'Berlin',1),(2,'Hamburg',1),(3,'Closed',0);
            INSERT INTO user_branches VALUES(7,1);
            INSERT INTO room_transfer_history VALUES
                (1,1,10,101,102,'Alice','2026-10-01'),
                (2,1,10,102,103,'Alice','2026-10-02'),
                (3,2,20,201,202,'Bob','2026-10-03'),
                (4,3,30,301,302,'Hidden','2026-10-03');
        ''')

    def tearDown(self): self.db.close()

    def test_admin_all_active_branches(self):
        rows=compare_transfers(self.db,user_id=1,role='admin')
        self.assertEqual([r['branch_id'] for r in rows],[1,2])
        self.assertEqual((rows[0]['transfers'],rows[0]['reservations'],rows[0]['active_staff']),(2,1,1))

    def test_non_admin_only_assigned_branch(self):
        rows=compare_transfers(self.db,user_id=7,role='staff')
        self.assertEqual([r['branch_id'] for r in rows],[1])
        with self.assertRaises(PermissionError):
            compare_transfers(self.db,user_id=7,role='staff',branch_ids=[1,2])

    def test_date_range(self):
        rows=compare_transfers(self.db,user_id=1,role='admin',date_from='2026-10-02',date_to='2026-10-02')
        self.assertEqual(sum(r['transfers'] for r in rows),1)

    def test_reject_invalid_date(self):
        with self.assertRaises(ValueError):compare_transfers(self.db,user_id=1,role='admin',date_from='2026-02-31')

    def test_export(self):
        rows=compare_transfers(self.db,user_id=1,role='admin')
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,'report.csv')
            export_comparison_csv(path,rows)
            with open(path,encoding='utf-8-sig',newline='') as file:
                result=list(csv.reader(file))
            self.assertEqual(len(result),3)
            self.assertEqual(result[1][1],'Berlin')

    def test_no_transfer_table(self):
        self.db.execute('DROP TABLE room_transfer_history')
        rows=compare_transfers(self.db,user_id=1,role='admin')
        self.assertEqual([r['transfers'] for r in rows],[0,0])


if __name__=='__main__':unittest.main()
