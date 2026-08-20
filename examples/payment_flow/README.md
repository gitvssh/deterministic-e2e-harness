# Synthetic payment flow

This fixture contains no real user, merchant, card, or payment-provider data. The in-memory API uses
two explicit test tokens:

- `synthetic-decline` always returns a retryable decline;
- `synthetic-approve` captures the payment on retry.

Run it through the repository quickstart rather than using it as production application code.
