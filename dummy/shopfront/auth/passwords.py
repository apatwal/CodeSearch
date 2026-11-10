"""Password storage.

Passwords are never stored directly. We store a salted, stretched digest and
compare in constant time on login.
"""

import hashlib
import hmac
import os

ITERATIONS = 200_000


def derive_key(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return salt, digest


def check_password(password, salt, expected):
    _, digest = derive_key(password, salt)
    return hmac.compare_digest(digest, expected)
