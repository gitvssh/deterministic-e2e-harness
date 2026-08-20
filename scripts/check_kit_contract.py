from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "payment_flow"


def main() -> int:
    required = [
        ROOT / "kit" / "AI_GUIDE.md",
        ROOT / "kit" / "harness" / "00-bootstrap.md",
        ROOT / "kit" / "harness" / "10-compile-scenarios.md",
        ROOT / "kit" / "harness" / "20-run-and-report.md",
        ROOT / "kit" / "harness" / "30-triage.md",
        ROOT / "kit" / "harness" / "40-consistency-audit.md",
        EXAMPLE / "docs" / "UC-PAY-001.md",
        EXAMPLE / "docs" / "TS-PAY-001.md",
        EXAMPLE / "specs" / "TS-PAY-001.hurl",
        EXAMPLE / "openapi.yaml",
    ]
    problems = [
        f"missing required contract file: {path.relative_to(ROOT)}"
        for path in required
        if not path.is_file()
    ]
    if problems:
        print("\n".join(problems))
        return 1

    scenario = (EXAMPLE / "docs" / "TS-PAY-001.md").read_text(encoding="utf-8")
    specification = (EXAMPLE / "specs" / "TS-PAY-001.hurl").read_text(encoding="utf-8")
    openapi = (EXAMPLE / "openapi.yaml").read_text(encoding="utf-8")
    for path, status in (
        ("/users", "201"),
        ("/payments", "402"),
        ("/payments/retry", "200"),
        ("/payments/{payment_id}", "200"),
    ):
        literal_path = path.replace("{payment_id}", "{{payment_id}}")
        if path not in scenario or path not in openapi:
            problems.append(f"scenario or OpenAPI grounding missing for {path}")
        if literal_path not in specification or not re.search(rf"HTTP\s+{status}\b", specification):
            problems.append(f"executable assertion missing for {path} -> {status}")
    if "{{run_id}}" not in specification:
        problems.append("specification does not isolate synthetic data with run_id")
    if "synthetic-decline" not in specification or "synthetic-approve" not in specification:
        problems.append("specification does not use both deterministic payment tokens")
    if problems:
        print("\n".join(problems))
        return 1
    print("Kit documents, grounding, and executable specification are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
