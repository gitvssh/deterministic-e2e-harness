from __future__ import annotations

import os
import platform
from pathlib import Path

import pytest

from scripts.hurl_tool import (
    ASSETS,
    HURL_VERSION,
    install_executable,
    normalized_platform,
    sha256,
)


def test_hurl_assets_are_sha256_pinned_for_supported_platforms() -> None:
    assert set(ASSETS) == {
        ("linux", "x86_64"),
        ("linux", "aarch64"),
        ("darwin", "x86_64"),
        ("darwin", "aarch64"),
    }
    assert HURL_VERSION == "8.0.1"
    for asset in ASSETS.values():
        assert asset.archive.startswith(f"hurl-{HURL_VERSION}-")
        assert len(asset.sha256) == 64
        int(asset.sha256, 16)


def test_platform_aliases_are_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(platform, "machine", lambda: "AMD64")
    assert normalized_platform() == ("linux", "x86_64")


def test_sha256_reads_file_content(tmp_path: Path) -> None:
    sample = tmp_path / "sample"
    sample.write_bytes(b"deterministic")
    assert sha256(sample) == "0badac3c6df445ad3aea62da1350683923aba37c685978afed96a515d12921a3"


def test_hurl_install_stages_on_target_filesystem_before_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = tmp_path / "download" / "hurl"
    target = tmp_path / "workspace" / ".tools" / "hurl"
    candidate.parent.mkdir()
    target.parent.mkdir(parents=True)
    candidate.write_bytes(b"pinned hurl executable")
    replace_sources: list[Path] = []
    real_replace = os.replace

    def same_filesystem_replace(source: str | Path, destination: str | Path) -> None:
        source_path = Path(source)
        destination_path = Path(destination)
        assert source_path.parent == destination_path.parent
        replace_sources.append(source_path)
        real_replace(source_path, destination_path)

    monkeypatch.setattr(os, "replace", same_filesystem_replace)

    install_executable(candidate, target)

    assert target.read_bytes() == b"pinned hurl executable"
    assert target.stat().st_mode & 0o111 == 0o111
    assert candidate.is_file()
    assert len(replace_sources) == 1
    assert not replace_sources[0].exists()
