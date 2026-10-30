"""Pure, Unicode-safe guest filtering helpers."""
import unicodedata

_DIGITS=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')

def normalize_query(value):
    text=unicodedata.normalize('NFKC',str(value or '')).translate(_DIGITS)
    return ' '.join(text.replace('ي','ی').replace('ك','ک').casefold().split())

def matches_guest(fields, query):
    words=normalize_query(query).split()
    content=normalize_query(' '.join(str(x or '') for x in fields))
    return all(word in content for word in words)
