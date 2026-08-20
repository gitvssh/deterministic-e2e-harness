# UC-PAY-001 — Retry a declined payment

## Actor and goal

- Actor: a fictional checkout client.
- Goal: recover from a retryable payment decline and confirm the final captured state.
- Business value: demonstrate explicit failure handling and observable state transitions.

## Preconditions

- The synthetic API is healthy.
- No account, credential, or external payment provider is required.

## Main flow

1. Register a synthetic user with a run-specific identifier.
2. Submit a payment with the deterministic decline token.
3. Observe the stable `PAYMENT_DECLINED` code and retryable flag.
4. Retry the same order with the deterministic approval token.
5. Query the payment and confirm it remains captured for the expected amount.

## Acceptance criteria

- Given a new run identifier, registration returns an active user.
- Given the decline token, payment submission returns HTTP 402 with a retryable decline.
- Given the approval token for the same order, retry returns a captured payment.
- Given the captured payment identifier, retrieval returns the same order, amount, and status.

## Out of scope

- Real payment credentials, settlement, refunds, authentication, persistence, and concurrency.
