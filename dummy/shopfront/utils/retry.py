"""Retry helper shared by modules that call flaky external services."""

import time

from shopfront.config import MAX_RETRIES


def retry_with_backoff(fn, attempts=MAX_RETRIES, base_delay=0.1):
    """Call fn, retrying on exception with exponential backoff."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
