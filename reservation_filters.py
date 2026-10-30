"""Pure, locale-aware reservation table filtering and status presentation."""
from form_validation import normalize_digits

STATUSES = (
    ('رزرو شده', 'Booked'),
    ('پذیرش شده', 'Checked in'),
    ('خارج شده', 'Checked out'),
    ('لغو شده', 'Cancelled'),
)

def normalize_query(value):
    return normalize_digits(str(value or '')).replace('ي','ی').replace('ك','ک').casefold().strip()

def status_options(language='fa'):
    return [('همه وضعیت‌ها' if language=='fa' else 'All statuses', None)] + [
        (fa if language=='fa' else en, fa) for fa,en in STATUSES
    ]

def matches_reservation(values, query='', status=None, language='fa'):
    values=[str(v or '') for v in values]
    if status:
        known=next((en for fa,en in STATUSES if fa==status),status)
        if not any(normalize_query(v) in (normalize_query(status),normalize_query(known)) for v in values[-1:]):
            return False
    term=normalize_query(query)
    return not term or any(term in normalize_query(value) for value in values)

def status_color(status):
    mapping={
        'رزرو شده':('#1763a6','#e9f3ff'),
        'پذیرش شده':('#167249','#e6f7ee'),
        'خارج شده':('#536179','#eef1f6'),
        'لغو شده':('#a12d42','#ffecef'),
    }
    return mapping.get(status,('#334155','#f1f5f9'))
