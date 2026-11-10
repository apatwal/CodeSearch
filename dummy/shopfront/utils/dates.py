"""Date helpers."""

from datetime import date, timedelta


def add_business_days(start, days):
    """Return the date that is `days` business days after `start`."""
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days -= 1
    return current


def due_date(issued: date, net_days: int = 30) -> date:
    return issued + timedelta(days=net_days)
