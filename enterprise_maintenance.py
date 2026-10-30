"""Offline SQLite integrity and consistent backup helpers for Hotel Pro Enterprise."""
from __future__ import annotations
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone

REQUIRED_TABLES = frozenset({'rooms', 'guests', 'reservations', 'payments', 'users'})

def database_health(db_path):
    """Read-only health snapshot; never returns guests or payment details."""
    db_path = Path(db_path)
    if not db_path.is_file():
        return {'ok': False, 'reason': 'database_missing', 'tables_missing': sorted(REQUIRED_TABLES)}
    connection = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)
    try:
        integrity = connection.execute('PRAGMA integrity_check').fetchone()[0]
        foreign_keys = connection.execute('PRAGMA foreign_key_check').fetchall()
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        missing = sorted(REQUIRED_TABLES - tables)
        return {'ok': integrity == 'ok' and not foreign_keys and not missing,
                'integrity': integrity,
                'foreign_key_violations': len(foreign_keys),
                'tables_missing': missing,
                'table_count': len(tables)}
    finally:
        connection.close()

def create_consistent_backup(db_path, output_dir, *, now=None):
    """Use SQLite online backup API; refuse overwrite and backup into source path."""
    source = Path(db_path).resolve()
    target_dir = Path(output_dir).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not target_dir.is_dir():
        raise NotADirectoryError(target_dir)
    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError('Backup timestamp must be timezone-aware')
    target = target_dir / f'hotel_backup_{timestamp.strftime("%Y%m%d_%H%M%S_%f")}.db'
    if target == source or target.exists():
        raise FileExistsError(target)
    # Exclusive reservation avoids silently overwriting existing backups.
    with target.open('xb'):
        pass
    try:
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as original:
            with closing(sqlite3.connect(target)) as backup:
                original.backup(backup)
        result = database_health(target)
        if not result['ok']:
            raise RuntimeError(f'Backup validation failed: {result}')
        return target
    except BaseException:
        target.unlink(missing_ok=True)
        raise
