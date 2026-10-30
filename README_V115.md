# Ashkan Hotel Pro v115 — Security notification lifecycle

- Sidebar unread alert counter and administrator-only dashboard alert shortcut.
- Persistent archive and restore actions; archived notifications do not contribute to unread badge.
- Archive preserves security history and marks item read; restoring does not re-trigger unread state.
- Admin-only actions, parameterized SQL, backward-compatible SQLite migration.
- Persian RTL / English LTR interface labels.
- Alerts still sync only on explicit security analytics/inbox refresh, not background monitoring.
- Back up hotel.db before replacing application files.
