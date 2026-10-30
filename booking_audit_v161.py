"""Append-only SQLite audit trail for reservation lifecycle changes.

The triggers capture every insert/update/delete, including changes made outside
UI helpers. The actor is recorded as 'database-trigger' because SQLite triggers
cannot reliably infer the authenticated application user without an explicit
actor context from every connection.
"""
from __future__ import annotations
import json
from contextvars import ContextVar

# Per-execution-context actor; the UI sets this after successful authentication.
_actor = ContextVar("booking_audit_actor", default="database-trigger")

def set_current_actor(actor):
    """Set the authenticated username used by audit triggers in this context."""
    value = str(actor or "").strip()
    if not value or len(value) > 128 or any(ord(ch) < 32 for ch in value):
        value = "database-trigger"
    _actor.set(value)
    return value

def register_actor_function(conn):
    """Register the connection-local SQLite function required by audit triggers."""
    conn.create_function("booking_audit_actor", 0, lambda: _actor.get(), deterministic=False)
    return conn

TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS booking_audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('created','updated','deleted')),
    event_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    actor TEXT NOT NULL DEFAULT 'database-trigger',
    old_values TEXT,
    new_values TEXT
);
CREATE INDEX IF NOT EXISTS idx_booking_audit_reservation_time
    ON booking_audit_events(reservation_id, event_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_booking_audit_event_time
    ON booking_audit_events(event_at DESC, id DESC);
'''

TRIGGER_SQL = '''
CREATE TRIGGER IF NOT EXISTS booking_audit_after_insert
AFTER INSERT ON reservations
BEGIN
  INSERT INTO booking_audit_events(reservation_id,event_type,actor,new_values)
  VALUES(NEW.id,'created',booking_audit_actor(),json_object(
    'room_id',NEW.room_id,'guest_id',NEW.guest_id,'checkin',NEW.checkin,
    'checkout',NEW.checkout,'status',NEW.status,'created_at',NEW.created_at));
END;
CREATE TRIGGER IF NOT EXISTS booking_audit_after_update
AFTER UPDATE ON reservations
WHEN OLD.room_id IS NOT NEW.room_id OR OLD.guest_id IS NOT NEW.guest_id
 OR OLD.checkin IS NOT NEW.checkin OR OLD.checkout IS NOT NEW.checkout
 OR OLD.status IS NOT NEW.status OR OLD.created_at IS NOT NEW.created_at
BEGIN
  INSERT INTO booking_audit_events(reservation_id,event_type,actor,old_values,new_values)
  VALUES(NEW.id,'updated',booking_audit_actor(),
    json_object('room_id',OLD.room_id,'guest_id',OLD.guest_id,'checkin',OLD.checkin,
      'checkout',OLD.checkout,'status',OLD.status,'created_at',OLD.created_at),
    json_object('room_id',NEW.room_id,'guest_id',NEW.guest_id,'checkin',NEW.checkin,
      'checkout',NEW.checkout,'status',NEW.status,'created_at',NEW.created_at));
END;
CREATE TRIGGER IF NOT EXISTS booking_audit_after_delete
AFTER DELETE ON reservations
BEGIN
  INSERT INTO booking_audit_events(reservation_id,event_type,actor,old_values)
  VALUES(OLD.id,'deleted',booking_audit_actor(),json_object(
    'room_id',OLD.room_id,'guest_id',OLD.guest_id,'checkin',OLD.checkin,
    'checkout',OLD.checkout,'status',OLD.status,'created_at',OLD.created_at));
END;
'''

def install(conn):
    """Install idempotent audit schema and triggers on an existing connection."""
    register_actor_function(conn)
    conn.executescript(TABLE_SQL)
    # Recreate triggers so upgrades replace the earlier hard-coded actor value.
    conn.executescript("""DROP TRIGGER IF EXISTS booking_audit_after_insert;
        DROP TRIGGER IF EXISTS booking_audit_after_update;
        DROP TRIGGER IF EXISTS booking_audit_after_delete;""")
    conn.executescript(TRIGGER_SQL)


def reservation_timeline(conn, reservation_id, limit=100):
    """Return validated, newest-first audit events for one reservation."""
    if type(reservation_id) is not int or reservation_id < 1:
        raise ValueError('reservation_id must be a positive integer')
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('limit must be between 1 and 500')
    rows = conn.execute('''SELECT id,reservation_id,event_type,event_at,actor,old_values,new_values
        FROM booking_audit_events WHERE reservation_id=?
        ORDER BY event_at DESC,id DESC LIMIT ?''',(reservation_id,limit)).fetchall()
    result=[]
    for row in rows:
        item=dict(zip(('id','reservation_id','event_type','event_at','actor','old_values','new_values'),row))
        for key in ('old_values','new_values'):
            if item[key] is not None:
                try: item[key]=json.loads(item[key])
                except (TypeError,ValueError): item[key]={}
        result.append(item)
    return result


def recent_events(conn, limit=100):
    """Return recent audit events across all reservations, newest first."""
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('limit must be between 1 and 500')
    rows=conn.execute('''SELECT id,reservation_id,event_type,event_at,actor,old_values,new_values
        FROM booking_audit_events ORDER BY event_at DESC,id DESC LIMIT ?''',(limit,)).fetchall()
    return [dict(zip(('id','reservation_id','event_type','event_at','actor','old_values','new_values'),r)) for r in rows]
