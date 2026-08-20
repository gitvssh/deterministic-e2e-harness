# 20 — Run deterministic specifications

## Preconditions

- the specification is committed and reviewed;
- the target environment is explicitly selected;
- required runtime variables are present;
- the runner version matches the repository pin.

## Run

```bash
hurl --test \
  --variable base_url="$E2E_BASE_URL" \
  --variable run_id="$(date -u +%Y%m%dT%H%M%SZ)" \
  specs/*.hurl
```

Use a stronger unique run identifier in concurrent CI. A nonzero Hurl exit code fails the gate. Do
not reinterpret a failure as success based on an AI summary.

Store reports only when the consumer's repository policy explicitly permits it. Redact or omit
response bodies that may contain secrets or personal data.
