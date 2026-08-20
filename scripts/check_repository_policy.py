from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CI = ROOT / ".github" / "workflows" / "ci.yml"
FORBIDDEN_PARTS = {".ai", ".claude", ".codex", ".git", "_vault"}
GENERATED_PARTS = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tools",
    ".venv",
    "__pycache__",
}
FORBIDDEN_NAMES = {"AGENTS.md", "CLAUDE.md", "kubeconfig"}
FORBIDDEN_SUFFIXES = {".db", ".key", ".log", ".p12", ".pem", ".sqlite", ".tfstate"}
FULL_SHA = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
ACTION_USE = re.compile(r"^\s*-?\s*uses:\s*([^@\s]+)@([^#\s]+)", re.MULTILINE)
UNTRUSTED_TRIGGER = re.compile(r"(?m)^\s*pull_request(?:_target)?:\s*$")
PRIVATE_MARKERS = re.compile(
    "|".join(
        (
            "damecasol" + r"\.com",
            "kv/data/" + "projects",
            "registry." + "dameca" + "sol.com",
            "En" + "FTRMS",
            "q" + "bang",
            "Road" + "Pay",
        )
    ),
    re.IGNORECASE,
)


def check_public_ci(problems: list[str]) -> None:
    if not PUBLIC_CI.is_file():
        problems.append("missing public CI workflow")
        return
    text = PUBLIC_CI.read_text(encoding="utf-8")
    if UNTRUSTED_TRIGGER.search(text):
        problems.append("public CI must not execute fork pull requests on the internal runner")
    required = {
        "github.repository == 'gitvssh/deterministic-e2e-harness'": "repository guard",
        "github.actor == 'gitvssh'": "trusted actor guard",
        "runs-on: homelab-deterministic-e2e-harness": "dedicated ARC label",
        "permissions:\n  contents: read": "read-only workflow permissions",
        "enable-cache: false": "disabled uv Actions cache",
    }
    for fragment, description in required.items():
        if fragment not in text:
            problems.append(f"public CI missing {description}")
    forbidden = {
        "runs-on: ubuntu-": "GitHub-hosted runner",
        "runs-on: windows-": "GitHub-hosted runner",
        "runs-on: macos-": "GitHub-hosted runner",
        "runs-on: self-hosted": "shared self-hosted label",
        "actions/cache@": "Actions cache storage",
        "actions/upload-artifact@": "Actions artifact storage",
        "actions/download-artifact@": "Actions artifact storage",
        "type=gha": "BuildKit Actions cache storage",
    }
    for fragment, description in forbidden.items():
        if fragment in text:
            problems.append(f"public CI uses forbidden {description}")
    for action, revision in ACTION_USE.findall(text):
        if not FULL_SHA.fullmatch(revision):
            problems.append(f"GitHub Action is not SHA-pinned: {action}")


def main() -> int:
    problems: list[str] = []
    check_public_ci(problems)
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in GENERATED_PARTS for part in relative.parts):
            continue
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            continue
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            problems.append(f"forbidden path: {relative}")
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        if PRIVATE_MARKERS.search(text):
            problems.append(f"private project or platform marker: {relative}")
    if problems:
        print("\n".join(problems))
        return 1
    print("Repository publication policy is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
