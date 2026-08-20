# Contributing

Contributions should preserve the central invariant: committed deterministic specifications—not an
LLM judgment—own CI pass/fail.

1. Describe the behavior change in a use case or scenario document.
2. Update the matching Hurl specification in the same change.
3. Use synthetic data only.
4. Run `python3 scripts/quality.py all`.
5. Explain any compatibility impact to consumers of `kit/`.

Do not weaken an assertion solely to make a failing implementation pass. If the contract changed,
make the contract change explicit and review the document and specification diff together.
