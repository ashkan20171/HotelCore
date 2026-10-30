"""Pure helpers for Unicode-aware, multi-term table filtering."""
import unicodedata

def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or ""))
    return text.casefold().translate(str.maketrans({"ي":"ی", "ك":"ک", "ـ":"", "۰":"0", "۱":"1", "۲":"2", "۳":"3", "۴":"4", "۵":"5", "۶":"6", "۷":"7", "۸":"8", "۹":"9", "٠":"0", "١":"1", "٢":"2", "٣":"3", "٤":"4", "٥":"5", "٦":"6", "٧":"7", "٨":"8", "٩":"9"}))

def row_matches(values, query):
    haystack = normalize(" ".join(map(str, values)))
    return all(token in haystack for token in normalize(query).split())
