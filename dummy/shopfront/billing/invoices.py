"""Invoice calculation."""

from dataclasses import dataclass, field
from datetime import date

from shopfront.utils.dates import due_date

TAX_RATE = 0.08


@dataclass
class LineItem:
    sku: str
    quantity: int
    unit_price_cents: int


@dataclass
class Invoice:
    customer_id: str
    issued: date
    items: list = field(default_factory=list)

    @property
    def due(self):
        return due_date(self.issued)


def calculate_invoice_total(invoice, discount_cents=0):
    """Return the invoice total in cents, after discount and tax."""
    subtotal = sum(i.quantity * i.unit_price_cents for i in invoice.items)
    subtotal = max(subtotal - discount_cents, 0)
    # FIXME: tax should depend on the customer's region, not a flat rate.
    return round(subtotal * (1 + TAX_RATE))
