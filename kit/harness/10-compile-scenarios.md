# 10 — Compile scenarios into Hurl

## Compilation contract

For every scenario step, identify the exact grounding source for:

- HTTP method and route;
- request fields, types, and required values;
- expected status code;
- response fields used by later steps;
- state transition or externally visible side effect.

If any item lacks a source, stop and request a contract decision. Do not guess.

## Hurl adapter

1. Use `{{base_url}}` and explicit runtime variables instead of hard-coded environment URLs.
2. Generate unique synthetic identifiers from `{{run_id}}`.
3. Capture only identifiers required by later requests.
4. Assert status, stable error codes, and contract fields; avoid prose error messages that may be
   localized.
5. Keep one scenario per file so failure ownership is obvious.
6. For asynchronous behavior, use bounded Hurl retry/polling rather than fixed sleeps.
7. Never write tokens, cookies, card data, or response bodies containing personal information to a
   report.

## Review output

Present the scenario document and generated Hurl diff together. Note each OpenAPI or contract section
used as grounding. The executable file becomes authoritative only after human review and commit.
