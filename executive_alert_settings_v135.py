# Per-admin management alert preferences; isolated and validated.
import sqlite3

DEFAULTS = {'low_occupancy': 30, 'high_expense_ratio': 90, 'receipts_decline': 20}

def validate(settings):
    if not isinstance(settings, dict) or set(settings) != set(DEFAULTS):
        raise ValueError('Invalid settings fields')
    if any(type(value) is not int or not 0 <= value <= 100 for value in settings.values()):
        raise ValueError('Thresholds must be integers from 0 to 100')
    return dict(settings)

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS executive_alert_preferences (
        actor_id INTEGER PRIMARY KEY,
        low_occupancy INTEGER NOT NULL CHECK(low_occupancy BETWEEN 0 AND 100),
        high_expense_ratio INTEGER NOT NULL CHECK(high_expense_ratio BETWEEN 0 AND 100),
        receipts_decline INTEGER NOT NULL CHECK(receipts_decline BETWEEN 0 AND 100)
    )''')

def load(conn, actor_id):
    if type(actor_id) is not int or actor_id <= 0:
        raise ValueError('Invalid actor')
    # Legacy databases may not have this optional preferences table.
    try:
        row = conn.execute('''SELECT low_occupancy, high_expense_ratio, receipts_decline
            FROM executive_alert_preferences WHERE actor_id=?''', (actor_id,)).fetchone()
    except sqlite3.OperationalError as exc:
        if 'no such table' not in str(exc).lower():
            raise
        return dict(DEFAULTS)
    return validate(dict(zip(DEFAULTS, row))) if row else dict(DEFAULTS)

def save(conn, actor_id, settings):
    if type(actor_id) is not int or actor_id <= 0:
        raise ValueError('Invalid actor')
    settings = validate(settings)
    migrate(conn)
    conn.execute('''INSERT INTO executive_alert_preferences
        (actor_id,low_occupancy,high_expense_ratio,receipts_decline) VALUES (?,?,?,?)
        ON CONFLICT(actor_id) DO UPDATE SET
        low_occupancy=excluded.low_occupancy,
        high_expense_ratio=excluded.high_expense_ratio,
        receipts_decline=excluded.receipts_decline''',
        (actor_id, *(settings[k] for k in DEFAULTS)))
    return settings
