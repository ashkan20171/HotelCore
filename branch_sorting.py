"""Stable ordering of permission-scoped branch comparison rows."""

SORT_KEYS = ('receipts', 'expenses', 'net', 'branch')

def sort_branch_rows(rows, key='receipts', descending=True):
    if key not in SORT_KEYS:
        raise ValueError('Unsupported branch sort key')
    if not isinstance(descending, bool):
        raise ValueError('descending must be boolean')
    items = list(rows)
    if key == 'branch':
        return sorted(items, key=lambda row: str(row['branch']).casefold(), reverse=descending)
    return sorted(items, key=lambda row: (int(row[key]), str(row['branch']).casefold()), reverse=descending)
