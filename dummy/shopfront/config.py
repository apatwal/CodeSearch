"""Application settings loaded from the environment."""

import os

DATABASE_URL = os.environ.get("SHOPFRONT_DATABASE_URL", "sqlite:///shopfront.db")

# Fake value for testing search over secret-like strings. Not a real key.
PAYMENT_GATEWAY_API_KEY = os.environ.get("PAYMENT_GATEWAY_API_KEY", "dummy-not-a-real-key")

TOKEN_TTL_SECONDS = 3600
LOW_STOCK_THRESHOLD = 5
MAX_RETRIES = 3
