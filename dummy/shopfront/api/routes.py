"""HTTP-style handlers. Framework-free so the fixture has no dependencies."""

from shopfront.auth import tokens
from shopfront.billing.payments import charge_card
from shopfront.inventory import stock


def handle_checkout(token, sku, quantity, unit_price_cents):
    user_id = tokens.validate(token)
    if user_id is None:
        return 401, {"error": "unauthorized"}
    try:
        stock.reserve(sku, quantity)
    except ValueError as exc:
        return 409, {"error": str(exc)}
    result = charge_card(user_id, quantity * unit_price_cents)
    return 200, result


def handle_low_stock_report(token):
    if tokens.validate(token) is None:
        return 401, {"error": "unauthorized"}
    return 200, {"skus": stock.low_stock_skus()}
