# Deterministic E2E Harness

A document-driven API testing kit where AI may compile reviewed requirements into static Hurl
specifications, while a deterministic runner remains the only CI pass/fail authority.

> The included registration and payment flow is entirely synthetic. It runs locally without an
> account, API key, database, or external service.

## Problem

AI-generated tests become difficult to trust when an LLM invents requests or judges results during
every CI run. The same prompt can produce different traffic, hide a real regression by rewriting a
failing assertion, or require credentials just to reproduce a result.

## Solution

This kit separates nondeterministic authoring from deterministic execution:

1. requirements and scenarios are the source of truth;
2. an AI assistant may compile them into plain-text Hurl specifications;
3. a human reviews the specification diff before it is committed;
4. CI runs only the committed specification and trusts only Hurl's exit code;
5. failures produce evidence for triage—never an automatic assertion rewrite.

The rules are tool-neutral. Hurl is the reference adapter because its request and assertion format is
plain text, reviewable, and independent of the application language.

## Architecture

```text
requirements + scenario documents
              |
              v
   AI-assisted compilation ----> human diff review
              |                         |
              +-------------------------+
                              |
                              v
                    committed *.hurl spec
                              |
                              v
                     deterministic Hurl run
                              |
                   pass/fail exit code + report
```

`kit/AI_GUIDE.md` defines the non-negotiable boundaries. The numbered documents under
`kit/harness/` cover bootstrap, compilation, execution, triage, and consistency auditing. See
[`docs/architecture.md`](docs/architecture.md) for component responsibilities.

## Quickstart

Requirements: Linux or macOS, Python 3.14, and `uv` 0.9.26. Hurl 8.0.1 is downloaded from its
official release and verified against a pinned SHA-256 digest.

```bash
python3 scripts/quality.py quickstart
```

The command installs locked development tools, starts the synthetic API on a random loopback port,
runs the reviewed Hurl journey, and shuts the server down. It does not use Docker or credentials.

To adopt the kit in another repository, copy `kit/`, then create project-specific `docs/`, `specs/`,
and `project-config.yaml` from the templates. Never edit the shared rules to make a failing product
look green.

## Validation

Local and CI validation use the same entry point:

```bash
python3 scripts/quality.py all
```

It performs formatting and lint checks, strict type checking, unit tests, the real Hurl integration
journey, dependency vulnerability auditing, CycloneDX SBOM validation, and dependency-license
review. GitHub Actions uses the repository-scoped `homelab-deterministic-e2e-harness` ARC runner
with read-only permissions and no Actions cache or artifact storage.

## Demo

The synthetic scenario proves a complete state transition:

1. register a fictional user;
2. submit a payment using a deterministic decline token and assert HTTP 402;
3. retry with a deterministic approval token and capture the payment;
4. query the payment and verify the final `captured` state.

The human-readable contract and executable specification live together:

- [`examples/payment_flow/docs/UC-PAY-001.md`](examples/payment_flow/docs/UC-PAY-001.md)
- [`examples/payment_flow/docs/TS-PAY-001.md`](examples/payment_flow/docs/TS-PAY-001.md)
- [`examples/payment_flow/specs/TS-PAY-001.hurl`](examples/payment_flow/specs/TS-PAY-001.hurl)
- [`examples/payment_flow/openapi.yaml`](examples/payment_flow/openapi.yaml)

## Limitations

- The reference adapter validates HTTP APIs; browser journeys require a separately reviewed runner
  adapter.
- AI compilation is an authoring aid, not a CI dependency or test oracle.
- The synthetic server is deliberately in-memory and single-process; it is not production payment
  code.
- This kit does not provision test environments, seed real customer data, or manage credentials.
- Hurl downloads are pinned for Linux x86-64/ARM64 and macOS x86-64/ARM64 only.

## License

Apache-2.0. See [LICENSE](LICENSE).
