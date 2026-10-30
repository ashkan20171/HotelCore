"""Stable, localized navigation groups. Indices map to existing application routes."""

NAV_GROUPS = (
    ('frontdesk', (0, 1, 2, 3, 5, 11, 20, 22)),
    ('finance', (4, 6, 8, 10, 14, 16, 17, 24)),
    ('operations', (9, 12, 13, 19, 21)),
    ('administration', (7, 15, 18, 23, 25)),
)

TITLES = {
    'frontdesk': ('پذیرش و اقامت', 'FRONT DESK & STAYS'),
    'finance': ('مالی و گزارش‌ها', 'FINANCE & REPORTS'),
    'operations': ('عملیات و خدمات', 'OPERATIONS & SERVICES'),
    'administration': ('مدیریت و تنظیمات', 'ADMINISTRATION'),
}


def group_for_index(index):
    if isinstance(index, bool) or not isinstance(index, int):
        raise ValueError('Navigation index must be an integer')
    for name, indices in NAV_GROUPS:
        if index in indices:
            return name
    raise ValueError('Unknown navigation index')


def group_title(group, language):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    return TITLES[group][0 if language == 'fa' else 1]


def visible_groups(visible_indices):
    visible = set(visible_indices)
    return {name for name, indices in NAV_GROUPS if visible.intersection(indices)}
