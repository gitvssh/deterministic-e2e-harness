from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hurl_tool import ASSETS, HURL_VERSION

ROOT = Path(__file__).resolve().parents[1]
PHASES = ("quickstart", "lint", "typecheck", "test", "audit", "sbom", "license")


def run(argv: Sequence[str], *, capture: bool = False) -> str:
    print("+", " ".join(argv))
    result = subprocess.run(
        list(argv),
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        if capture:
            print("Command failed; output was intentionally withheld.", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout if capture else ""


def quickstart() -> None:
    run(["uv", "sync", "--frozen"])
    run(["uv", "run", "python", "scripts/check_repository_policy.py"])
    run(["uv", "run", "python", "scripts/check_kit_contract.py"])
    run(["uv", "run", "python", "scripts/run_demo.py"])


def lint() -> None:
    run(["uv", "run", "ruff", "check", "."])
    run(["uv", "run", "ruff", "format", "--check", "."])
    run(["uv", "run", "python", "scripts/check_repository_policy.py"])
    run(["uv", "run", "python", "scripts/check_kit_contract.py"])


def typecheck() -> None:
    run(["uv", "run", "mypy"])


def test() -> None:
    run(["uv", "run", "pytest"])
    run(["uv", "run", "python", "scripts/run_demo.py"])


def audit() -> None:
    with tempfile.NamedTemporaryFile(prefix="e2e-harness-requirements-", suffix=".txt") as exported:
        run(
            [
                "uv",
                "export",
                "--quiet",
                "--frozen",
                "--no-emit-project",
                "--no-hashes",
                "--output-file",
                exported.name,
            ]
        )
        run(["uv", "run", "pip-audit", "--strict", "--requirement", exported.name])


def sbom() -> None:
    with tempfile.TemporaryDirectory(prefix="e2e-harness-sbom-") as temporary:
        path = Path(temporary) / "python.cdx.json"
        run(
            [
                "uv",
                "run",
                "cyclonedx-py",
                "environment",
                "--output-format",
                "JSON",
                "--output-file",
                str(path),
            ]
        )
        document = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
        if document.get("bomFormat") != "CycloneDX" or not document.get("components"):
            raise SystemExit("Python SBOM is empty or invalid")
        tool_component = {
            "type": "application",
            "name": "hurl",
            "version": HURL_VERSION,
            "licenses": [{"license": {"id": "Apache-2.0"}}],
        }
        cast(list[dict[str, Any]], document["components"]).append(tool_component)
        if not all(asset.sha256 for asset in ASSETS.values()):
            raise SystemExit("Hurl platform checksums are incomplete")
    print("CycloneDX SBOM and pinned Hurl component are valid.")


def license_review() -> None:
    raw = run(["uv", "run", "pip-licenses", "--format=json"], capture=True)
    packages = cast(list[dict[str, Any]], json.loads(raw))
    licenses = [str(item.get("License", "")) for item in packages]
    unknown = [name for name in licenses if not name or name == "UNKNOWN"]
    forbidden = []
    for name in licenses:
        normalized = name.upper()
        if (
            "AGPL" in normalized
            or "SSPL" in normalized
            or ("GPL" in normalized and "LGPL" not in normalized)
        ):
            forbidden.append(name)
    if unknown or forbidden:
        raise SystemExit(
            f"license review failed: unknown={len(unknown)}, forbidden={len(forbidden)}"
        )
    print(f"Dependency license review passed for {len(licenses)} Python packages and Hurl.")


FUNCTIONS = {
    "quickstart": quickstart,
    "lint": lint,
    "typecheck": typecheck,
    "test": test,
    "audit": audit,
    "sbom": sbom,
    "license": license_review,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=(*PHASES, "all"))
    arguments = parser.parse_args()
    selected = PHASES if arguments.phase == "all" else (arguments.phase,)
    for phase in selected:
        print(f"== {phase} ==")
        FUNCTIONS[phase]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
