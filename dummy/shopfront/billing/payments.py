"""Card payments through the external gateway.

Restricted: only the billing team may read this module (see dummy/acl.json).
"""

import warnings

from shopfront.config import PAYMENT_GATEWAY_API_KEY
from shopfront.utils.retry import retry_with_backoff


class GatewayClient:
    def __init__(self, api_key=PAYMENT_GATEWAY_API_KEY):
        self.api_key = api_key

    def post(self, path, payload):
        # Stub: a real client would make an HTTPS request here.
        return {"status": "ok", "path": path, "amount_cents": payload["amount_cents"]}


def charge_card(customer_id, amount_cents, client=None):
    """Charge a customer's saved card, retrying transient gateway failures."""
    client = client or GatewayClient()
    return retry_with_backoff(
        lambda: client.post("/charges", {"customer": customer_id, "amount_cents": amount_cents})
    )


def refund(charge_id, client=None):
    client = client or GatewayClient()
    return client.post(f"/charges/{charge_id}/refund", {"amount_cents": 0})


def legacy_charge(customer_id, amount_cents):
    """Deprecated: use charge_card instead."""
    warnings.warn("legacy_charge is deprecated; use charge_card", DeprecationWarning)
    return charge_card(customer_id, amount_cents)
