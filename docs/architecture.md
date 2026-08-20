# Architecture

## Responsibilities

| Component | Owns | Must not own |
| --- | --- | --- |
| Requirement documents | User intent and acceptance criteria | Runtime credentials |
| AI compiler | Draft conversion from grounded documents to a static spec | CI verdicts or runtime healing |
| Human review | Approval of the document/specification diff | Hidden out-of-band expectations |
| Hurl adapter | Deterministic requests, captures, assertions, and exit code | Requirement invention |
| Triage | Evidence classification and proposed next action | Automatic assertion changes |

## Trust boundary

An AI assistant is outside the CI decision boundary. It may create a reviewable text change before a
run and summarize evidence after a run. During the run, the committed specification, injected
variables, target API, and Hurl binary are the complete execution inputs.

Runner variables may contain loopback or environment URLs and secret references. Secret values are
injected by the consumer's CI secret store and must never be rendered into specifications or reports.

## Reproducibility controls

- Hurl is version- and checksum-pinned.
- Specifications create their own synthetic data using a unique run identifier.
- Fixed sleeps are avoided; asynchronous behavior should use bounded polling.
- A failing specification is evidence of drift until the product contract is deliberately changed.
- CI has read-only repository permissions and does not upload caches or artifacts.
