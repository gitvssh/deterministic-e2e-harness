# TS-PAY-001 — Decline, retry, and capture

Related use case: `UC-PAY-001`

## Purpose

Prove that a retryable decline is explicit and that a reviewed retry produces an observable captured
payment without relying on another scenario's state.

## Synthetic data

- User external ID: `candidate-{{run_id}}`
- Email domain: `example.com`
- Order ID: `order-{{run_id}}`
- Amount: `12500`
- Test tokens: `synthetic-decline`, `synthetic-approve`

## Steps

| # | Request | Expected result | Grounding source |
| --- | --- | --- | --- |
| 1 | `POST /users` | 201, active user ID | OpenAPI `/users` |
| 2 | `POST /payments` | 402, retryable `PAYMENT_DECLINED` | OpenAPI `/payments` |
| 3 | `POST /payments/retry` | 200, captured payment ID | OpenAPI `/payments/retry` |
| 4 | `GET /payments/{payment_id}` | 200, captured state and amount 12500 | OpenAPI `/payments/{payment_id}` |

## Cleanup and isolation

The API process is created for one test run and destroyed afterward. Every identifier contains the
unique `run_id`; the scenario does not depend on pre-existing data.
