"""Static localization audit for interface strings (not database values)."""
from localization import STRINGS

def untranslated(labels):
    """Return distinct non-empty labels missing an English translation."""
    return sorted({label for label in labels if label and (label not in STRINGS or not STRINGS[label].strip())})

def translation_coverage(labels):
    """Return (translated, total) over distinct non-empty UI labels."""
    unique = {label for label in labels if label}
    missing = set(untranslated(unique))
    return len(unique) - len(missing), len(unique)
