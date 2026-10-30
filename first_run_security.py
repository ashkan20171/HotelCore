"""Explicit, secure first-run administrator provisioning (no hard-coded password)."""
import hashlib
import re
import secrets

def validate_admin_credentials(username, password, confirmation):
    username=username.strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,32}',username):
        raise ValueError('Username must be 3–32 Latin letters, digits, _, . or -')
    if password != confirmation:
        raise ValueError('Passwords do not match')
    if len(password)<12 or len(password)>128:
        raise ValueError('Password must be 12–128 characters')
    if not (any(c.islower() for c in password) and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password) and any(not c.isalnum() for c in password)):
        raise ValueError('Use upper/lowercase letters, a digit and a symbol')
    if username.casefold() in password.casefold():
        raise ValueError('Password must not contain username')
    return username

def needs_admin_setup(conn):
    return not bool(conn.execute("SELECT 1 FROM users LIMIT 1").fetchone())

def create_first_admin(conn, username, password, confirmation):
    username=validate_admin_credentials(username,password,confirmation)
    if not needs_admin_setup(conn):
        raise PermissionError('Initial administrator already exists')
    salt=secrets.token_hex(16)
    hashed=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),bytes.fromhex(salt),240000).hex()
    conn.execute('INSERT INTO users(username,password_hash,salt,role) VALUES(?,?,?,?)',
                 (username,hashed,salt,'admin'))
    return username
