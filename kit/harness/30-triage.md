# 30 — Triage a failed run

Classify the first causal failure using request/response evidence and the grounded contract:

- product regression;
- intended contract change not reflected in docs/spec;
- environment unavailable or missing capability;
- test-data collision or isolation defect;
- flaky asynchronous dependency;
- harness defect.

Record the failing step, expected contract, observed status/field, and smallest safe next action.
Never edit the specification automatically. An intended contract change requires a reviewed document
and specification change in the same proposal.
