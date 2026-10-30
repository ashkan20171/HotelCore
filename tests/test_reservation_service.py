import sqlite3
import unittest
from unittest.mock import patch
from reservation_service import create_reservation

class ReservationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:')
        self.c.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT,rate INTEGER);
        CREATE TABLE guests(id INTEGER PRIMARY KEY,name TEXT,phone TEXT,national_id TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,checkin TEXT,checkout TEXT,branch_id INTEGER,status TEXT DEFAULT 'رزرو شده');""")
        self.c.execute("INSERT INTO rooms VALUES(1,1,'فعال',100)")
        self.c.commit()
        self.args=dict(user_id=1,role='admin',branch_id=1,room_id=1,name='مهمان تست',phone='09123456789',national_id='',checkin='2026-11-01',checkout='2026-11-03')
    def tearDown(self): self.c.close()
    def create(self, **changes):
        args={**self.args,**changes}
        with patch('reservation_service.require_room',side_effect=lambda *a: None),patch('reservation_service.quote_reservation',return_value={}),patch('reservation_service.save_quote'):
            return create_reservation(self.c,**args)
    def test_success(self):
        self.create()
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM reservations').fetchone()[0],1)
    def test_overlap_rolls_back_guest(self):
        self.create()
        with self.assertRaises(ValueError):self.create(checkin='2026-11-02',checkout='2026-11-04')
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM guests').fetchone()[0],1)
    def test_adjacent_stays_allowed(self):
        self.create()
        self.create(checkin='2026-11-03',checkout='2026-11-04')
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM reservations').fetchone()[0],2)
    def test_unauthorized_room_no_guest(self):
        with patch('reservation_service.require_room',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):create_reservation(self.c,**self.args)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM guests').fetchone()[0],0)
    def test_quote_failure_rolls_back(self):
        with patch('reservation_service.require_room'),patch('reservation_service.quote_reservation',side_effect=RuntimeError('quote failed')):
            with self.assertRaises(RuntimeError):create_reservation(self.c,**self.args)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM guests').fetchone()[0],0)

if __name__=='__main__':unittest.main()
