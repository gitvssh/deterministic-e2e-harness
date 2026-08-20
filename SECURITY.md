# Security policy

## Supported version

Security fixes are applied to the latest release and the current `main` branch.

## Reporting a vulnerability

Use GitHub private vulnerability reporting when it is available. Otherwise, open a minimal issue
requesting a private reporting channel without including exploit details, credentials, personal
data, or customer information.

## Test-data boundary

Only synthetic values belong in examples, specifications, reports, issues, and pull requests. Keep
credentials in the consumer repository's approved secret store and inject only environment variable
names into runner configuration. Never commit access tokens, real payment data, session cookies,
production URLs, or captured response bodies containing personal information.

Downloaded Hurl archives are accepted only when their SHA-256 digest matches the pinned platform
entry in `scripts/hurl_tool.py`.
