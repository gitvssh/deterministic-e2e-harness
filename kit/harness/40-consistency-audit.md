# 40 — Audit documentation and specification consistency

For every use case, build a small mapping:

| Acceptance criterion | Scenario step | Hurl request/assertion | Grounding source |
| --- | --- | --- | --- |

Flag an item when:

- an acceptance criterion has no executable assertion;
- a Hurl request or field has no documented grounding;
- a state transition is asserted only through a generic 2xx response;
- an authorization boundary has no negative case;
- a scenario depends on another scenario's state;
- a secret value appears in a document, configuration, specification, or report.

The audit is advisory. It may propose missing cases, but only the deterministic runner may gate CI.
