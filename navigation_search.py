"""Bilingual sidebar search, independent of Qt and database state."""
import unicodedata


def normalize_query(value):
    if not isinstance(value, str):
        raise TypeError('Navigation search must be a string')
    value = unicodedata.normalize('NFKC', value).casefold()
    return ' '.join(value.replace('ي', 'ی').replace('ك', 'ک').split())


def matching_navigation_indices(query, persian, english):
    if len(persian) != len(english):
        raise ValueError('Navigation labels must have matching lengths')
    terms = normalize_query(query).split()
    return {i for i, (fa, en) in enumerate(zip(persian, english))
            if all(term in normalize_query(f'{fa} {en}') for term in terms)}
