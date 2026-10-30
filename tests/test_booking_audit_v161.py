import json
import sqlite3
import unittest
from booking_audit_v161 import install, reservation_timeline, recent_events

class BookingAuditV161Tests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript('''CREATE TABLE reservations(
            id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,
            checkin TEXT,checkout TEXT,status TEXT,created_at TEXT);
        INSERT INTO reservations VALUES(1,10,20,'2026-11-01','2026-11-03','confirmed','2026-10-24');''')
        install(self.db)

    def tearDown(self): self.db.close()

    def test_install_is_idempotent(self):
        install(self.db)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'booking_audit_%'").fetchone()[0],3)

    def test_create_event_captures_non_sensitive_booking_fields(self):
        self.db.execute("INSERT INTO reservations VALUES(2,11,21,'2026-11-05','2026-11-06','confirmed','2026-10-24')")
        event=reservation_timeline(self.db,2)[0]
        self.assertEqual(event['event_type'],'created')
        self.assertEqual(event['new_values']['room_id'],11)
        self.assertNotIn('guest_name',event['new_values'])

    def test_update_records_old_and_new_state(self):
        self.db.execute("UPDATE reservations SET status='cancelled' WHERE id=1")
        event=reservation_timeline(self.db,1)[0]
        self.assertEqual(event['event_type'],'updated')
        self.assertEqual(event['old_values']['status'],'confirmed')
        self.assertEqual(event['new_values']['status'],'cancelled')

    def test_noop_update_does_not_create_noise(self):
        self.db.execute("UPDATE reservations SET status=status WHERE id=1")
        self.assertEqual(reservation_timeline(self.db,1),[])

    def test_delete_records_last_state(self):
        self.db.execute('DELETE FROM reservations WHERE id=1')
        event=reservation_timeline(self.db,1)[0]
        self.assertEqual(event['event_type'],'deleted')
        self.assertEqual(event['old_values']['checkin'],'2026-11-01')

    def test_parameter_validation(self):
        for rid in (0,-1,'1',True):
            with self.assertRaises(ValueError): reservation_timeline(self.db,rid)
        for limit in (0,501,True):
            with self.assertRaises(ValueError): recent_events(self.db,limit)

    def test_recent_events_newest_first(self):
        self.db.execute("UPDATE reservations SET status='checked-in' WHERE id=1")
        self.db.execute("UPDATE reservations SET status='checked-out' WHERE id=1")
        rows=recent_events(self.db)
        self.assertEqual(len(rows),2)
        self.assertGreaterEqual(rows[0]['id'],rows[1]['id'])

if __name__=='__main__': unittest.main()
