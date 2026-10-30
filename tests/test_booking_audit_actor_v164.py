import sqlite3
import unittest
from booking_audit_v161 import install, set_current_actor, reservation_timeline

class BookingAuditActorV164Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE reservations(id INTEGER PRIMARY KEY, room_id INTEGER, guest_id INTEGER, checkin TEXT, checkout TEXT, status TEXT, created_at TEXT)')
        install(self.db)
        set_current_actor('database-trigger')

    def tearDown(self):
        self.db.close()
        set_current_actor('database-trigger')

    def test_authenticated_actor_is_recorded_on_insert(self):
        set_current_actor('ashkan.admin')
        self.db.execute("INSERT INTO reservations VALUES(1,10,20,'2026-11-01','2026-11-02','confirmed','2026-10-24')")
        self.assertEqual(reservation_timeline(self.db, 1)[0]['actor'], 'ashkan.admin')

    def test_actor_is_recorded_on_update(self):
        self.db.execute("INSERT INTO reservations VALUES(1,10,20,'2026-11-01','2026-11-02','confirmed','2026-10-24')")
        set_current_actor('frontdesk.user')
        self.db.execute("UPDATE reservations SET status='checked-in' WHERE id=1")
        self.assertEqual(reservation_timeline(self.db, 1)[0]['actor'], 'frontdesk.user')

    def test_invalid_actor_falls_back_to_safe_default(self):
        set_current_actor('  ')
        self.db.execute("INSERT INTO reservations VALUES(1,10,20,'2026-11-01','2026-11-02','confirmed','2026-10-24')")
        self.assertEqual(reservation_timeline(self.db, 1)[0]['actor'], 'database-trigger')

    def test_install_remains_idempotent_and_refreshes_trigger(self):
        install(self.db)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'booking_audit_%'").fetchone()[0], 3)

if __name__ == '__main__':
    unittest.main()
