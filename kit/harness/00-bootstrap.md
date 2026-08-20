# 00 — Bootstrap a consumer repository

## Inputs

- the target API's reviewed OpenAPI document or equivalent contract;
- one to three critical user journeys;
- an environment URL variable name;
- authentication variable names, if required;
- known environment capabilities and constraints.

Do not request or record raw credentials.

## Procedure

1. Copy `kit/` into the consumer repository at a versioned path.
2. Create `project-config.yaml` from `kit/templates/project-config.yaml`.
3. Record only public endpoints or environment variable names in configuration.
4. Create one `docs/UC-<DOMAIN>-<NNN>.md` per user goal.
5. Create one matching `docs/TS-<DOMAIN>-<NNN>.md` per deterministic scenario.
6. Compile each scenario using `10-compile-scenarios.md`.
7. Review the document and Hurl diffs together before committing.
8. Run the specification twice with distinct run identifiers to prove state isolation.

Bootstrap is incomplete if a specification depends on manually prepared state, a previous scenario,
or a secret committed to the repository.
