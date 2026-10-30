"""Pure bilingual presentation helpers for the security administration page."""
from __future__ import annotations

def account_counts(records):
    return {'active':sum(bool(r[3]) for r in records),
            'disabled':sum(not bool(r[3]) for r in records),
            'admins':sum(r[2]=='admin' and bool(r[3]) for r in records)}

def account_rows(records,*,fa=True):
    return [(name,role,('فعال' if active else 'غیرفعال') if fa else
             ('Active' if active else 'Disabled'))
            for _,name,role,active in records]
