"""Session tokens."""

import secrets
import time

from shopfront.config import TOKEN_TTL_SECONDS

_sessions = {}


def issue_token(user_id):
    token = secrets.token_urlsafe(32)
    _sessions[token] = (user_id, time.time() + TOKEN_TTL_SECONDS)
    return token


def validate(token):
    """Return the user id for a live token, or None if it is unknown or expired."""
    entry = _sessions.get(token)
    if entry is None:
        return None
    user_id, expires_at = entry
    if time.time() > expires_at:
        del _sessions[token]
        return None
    return user_id


def revoke(token):
    _sessions.pop(token, None)
