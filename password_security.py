"""Credential rotation service: no UI dependencies, atomic SQLite updates."""
import hashlib
import hmac
import secrets

ITERATIONS = 240000

def validate_new_password(password, username=''):
    if len(password) < 12:
        raise ValueError('Password must contain at least 12 characters.')
    if len(password) > 1024:
        raise ValueError('Password is too long.')
    if password.strip() != password:
        raise ValueError('Password must not start or end with spaces.')
    if username and username.casefold() in password.casefold():
        raise ValueError('Password must not contain your username.')
    if password.isdigit() or password.isalpha():
        raise ValueError('Use a combination of letters, digits or symbols.')
    return True

def verify_password(password, salt_hex, digest_hex):
    try:
        candidate = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), ITERATIONS)
        return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False

def change_password(conn, username, current_password, new_password, confirmation):
    if new_password != confirmation:
        raise ValueError('New passwords do not match.')
    validate_new_password(new_password, username)
    row = conn.execute('SELECT password_hash, salt FROM users WHERE username=?', (username,)).fetchone()
    if not row or not verify_password(current_password, row[1], row[0]):
        raise ValueError('Current password is incorrect.')
    if verify_password(new_password, row[1], row[0]):
        raise ValueError('New password must be different from the current password.')
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), bytes.fromhex(salt), ITERATIONS).hex()
    conn.execute('UPDATE users SET password_hash=?,salt=? WHERE username=?', (digest,salt,username))
    return True
