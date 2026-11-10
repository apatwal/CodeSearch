"""Stock levels per SKU."""

from shopfront.config import LOW_STOCK_THRESHOLD
from shopfront.utils.retry import retry_with_backoff

_stock = {}


def validate(sku, quantity):
    """Raise ValueError if the request can't be filled from current stock."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if _stock.get(sku, 0) < quantity:
        raise ValueError(f"insufficient stock for {sku}")


def reserve(sku, quantity):
    validate(sku, quantity)
    _stock[sku] -= quantity


def restock(sku, quantity):
    _stock[sku] = _stock.get(sku, 0) + quantity


def low_stock_skus():
    return [sku for sku, qty in _stock.items() if qty < LOW_STOCK_THRESHOLD]


def sync_from_warehouse(fetch):
    """Replace local stock with the warehouse's counts."""
    # TODO: diff against local counts instead of overwriting them.
    counts = retry_with_backoff(fetch)
    _stock.clear()
    _stock.update(counts)
