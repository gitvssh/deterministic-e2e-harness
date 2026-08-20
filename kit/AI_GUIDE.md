# AI compiler guide

This directory is a reusable E2E testing kit. An AI assistant may help author reviewable documents
and executable specifications, but it is never the runtime test oracle.

## Entry points

- New adoption: follow `harness/00-bootstrap.md`.
- New or changed scenario: follow `harness/10-compile-scenarios.md`.
- Test execution: follow `harness/20-run-and-report.md`.
- Failure analysis: follow `harness/30-triage.md`.
- Contract coverage review: follow `harness/40-consistency-audit.md`.

## Invariants

1. Only the deterministic runner exit code may pass or fail CI.
2. Every executable specification is compiled from grounded project documentation and reviewed as a
   text diff before it is committed.
3. Do not rewrite a failing assertion merely to make the run pass. Propose a contract and spec change
   together when the intended behavior genuinely changed.
4. Do not invent endpoints, parameters, response fields, or states. Ground them in OpenAPI or an
   explicitly approved contract.
5. Specifications own their synthetic data and do not rely on execution order.
6. Secrets are injected at runtime; only environment variable names may appear in configuration.
7. Shared files under `kit/` are project-neutral. Consumer-specific documents and specifications live
   outside this directory.

## Expected consumer layout

```text
kit/                    shared, versioned rules and templates
project-config.yaml     consumer endpoints and variable names
docs/UC-*.md            use cases
docs/TS-*.md            test scenarios
specs/TS-*.hurl         reviewed executable specifications
reports/                local/CI outputs; never a secret store
```
