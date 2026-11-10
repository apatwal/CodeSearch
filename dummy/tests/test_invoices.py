import unittest
from datetime import date

from shopfront.billing.invoices import Invoice, LineItem, calculate_invoice_total


class InvoiceTotalTest(unittest.TestCase):
    def test_total_includes_tax(self):
        inv = Invoice("c1", date(2026, 1, 1), [LineItem("A", 2, 500)])
        self.assertEqual(calculate_invoice_total(inv), 1080)

    def test_discount_never_goes_negative(self):
        inv = Invoice("c1", date(2026, 1, 1), [LineItem("A", 1, 100)])
        self.assertEqual(calculate_invoice_total(inv, discount_cents=500), 0)


if __name__ == "__main__":
    unittest.main()
