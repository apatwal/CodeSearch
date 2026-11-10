# Dummy codebase: `shopfront`

A small, fake e-commerce backend for testing CodeSearch queries. It has no dependencies. Run its tests from this folder with:

```sh
python3 -m unittest discover -s tests -t .
```

`acl.json` defines fake users and teams and which paths each team can read. Use it to test permission-aware search.

## Layout

```
shopfront/
  config.py            settings, including a fake API key   (admins only)
  auth/passwords.py    salted password storage (pbkdf2)
  auth/tokens.py       session tokens: issue_token, validate, revoke
  billing/invoices.py  calculate_invoice_total, Invoice, LineItem   (billing, admins)
  billing/payments.py  charge_card, refund, legacy_charge (deprecated)  (billing, admins)
  inventory/stock.py   validate, reserve, restock, sync_from_warehouse
  api/routes.py        handle_checkout, handle_low_stock_report
  utils/retry.py       retry_with_backoff
  utils/dates.py       add_business_days, due_date
tests/                 unittest tests for invoices and stock
```

## Sample queries and expected results

Results are listed as file and symbol, not line numbers, so they still hold after you edit the code.

| Query | Kind | Expected results |
|---|---|---|
| `calculate_invoice_total` | exact symbol | definition in `billing/invoices.py`; usage in `tests/test_invoices.py` |
| `retry_with_backoff` | find callers | `billing/payments.py` (`charge_card`), `inventory/stock.py` (`sync_from_warehouse`), plus the definition in `utils/retry.py` |
| `validate` | ambiguous name | two different functions: `auth/tokens.py` and `inventory/stock.py` |
| how are passwords hashed | semantic | `auth/passwords.py`. The word "hash" appears only in `hashlib`, so a good result depends on meaning, not the function name `derive_key`. |
| deprecated functions | semantic | `legacy_charge` in `billing/payments.py` |
| `TODO` or `FIXME` | lexical | `inventory/stock.py` (TODO), `billing/invoices.py` (FIXME) |
| where do we talk to the payment gateway | semantic | `GatewayClient` and `charge_card` in `billing/payments.py` |
| API key | secrets | `config.py` (`PAYMENT_GATEWAY_API_KEY`), `billing/payments.py` |

## Permission scenarios

Rules in `acl.json` are checked in order, and the first matching rule wins.

| User | Team | Query | Expected |
|---|---|---|---|
| alice | billing | `charge_card` | sees `billing/payments.py` and `api/routes.py` |
| bob | inventory | `charge_card` | sees only `api/routes.py`; `billing/payments.py` must not appear |
| bob | inventory | `PAYMENT_GATEWAY_API_KEY` | no results from `config.py` or `billing/payments.py` |
| carol | admins | `PAYMENT_GATEWAY_API_KEY` | sees `config.py` and `billing/payments.py` |
| alice | billing | `PAYMENT_GATEWAY_API_KEY` | sees `billing/payments.py` but not `config.py` |

## Drift scenarios

Use these to check that results stay accurate after something changes:

1. **Rename:** rename `calculate_invoice_total` to `invoice_total`. Searching the old name should return nothing.
2. **Delete:** remove `legacy_charge`. It should drop out of the "deprecated functions" results.
3. **Move:** move `utils/retry.py` to `utils/backoff.py`. Results should point to the new path.
4. **Revoke access:** remove `alice` from `billing` in `acl.json`. Her next search for `charge_card` should no longer return `billing/payments.py`.
5. **Grant access:** add `bob` to `billing`. He should now see `billing/payments.py`.
