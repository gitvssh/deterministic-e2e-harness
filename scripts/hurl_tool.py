from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HURL_VERSION = "8.0.1"
RELEASE_BASE = f"https://github.com/Orange-OpenSource/hurl/releases/download/{HURL_VERSION}"


@dataclass(frozen=True)
class Asset:
    archive: str
    sha256: str


ASSETS: dict[tuple[str, str], Asset] = {
    (
        "linux",
        "x86_64",
    ): Asset(
        f"hurl-{HURL_VERSION}-x86_64-unknown-linux-gnu.tar.gz",
        "cac7c4670d69444db120edb21fe06c97ba8c80dcc52279957c8dd18f05fb0c06",
    ),
    (
        "linux",
        "aarch64",
    ): Asset(
        f"hurl-{HURL_VERSION}-aarch64-unknown-linux-gnu.tar.gz",
        "bc4732df4754748e9bf296aa3832ec019f798afb399f1279b72ed37b6e04525c",
    ),
    (
        "darwin",
        "x86_64",
    ): Asset(
        f"hurl-{HURL_VERSION}-x86_64-apple-darwin.tar.gz",
        "55e95bb7a8d61ae6919eaaf96f260f0836f5b34c1b0f7731e38be803f6984367",
    ),
    (
        "darwin",
        "aarch64",
    ): Asset(
        f"hurl-{HURL_VERSION}-aarch64-apple-darwin.tar.gz",
        "b57928e246617df73cb1b2157f31f507dcbde6ae12e828cc53dde0e40e05bbbb",
    ),
}


def normalized_platform() -> tuple[str, str]:
    system = platform.system().casefold()
    machine = platform.machine().casefold()
    machine = {"amd64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    return system, machine


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(asset: Asset, destination: Path) -> None:
    request = urllib.request.Request(
        f"{RELEASE_BASE}/{asset.archive}",
        headers={"User-Agent": "deterministic-e2e-harness/1.0.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)


def extract_hurl(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as bundle:
        matches = [
            member
            for member in bundle.getmembers()
            if member.isfile() and member.name.endswith("/bin/hurl")
        ]
        if len(matches) != 1 or matches[0].size > 100 * 1024 * 1024:
            raise RuntimeError("Hurl archive has an unexpected executable layout")
        source = bundle.extractfile(matches[0])
        if source is None:
            raise RuntimeError("Hurl executable could not be read from the archive")
        destination.write_bytes(source.read())
    destination.chmod(0o755)


def install_executable(candidate: Path, target: Path) -> None:
    """Copy into the target filesystem before the atomic replacement."""
    staging_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b",
            prefix=f".{target.name}-",
            dir=target.parent,
            delete=False,
        ) as staging:
            staging_path = Path(staging.name)
            with candidate.open("rb") as source:
                shutil.copyfileobj(source, staging)
            staging.flush()
            os.fsync(staging.fileno())
        staging_path.chmod(0o755)
        os.replace(staging_path, target)
    finally:
        if staging_path is not None:
            staging_path.unlink(missing_ok=True)


def ensure_hurl() -> Path:
    key = normalized_platform()
    asset = ASSETS.get(key)
    if asset is None:
        raise RuntimeError(f"unsupported platform: {key[0]}/{key[1]}")
    target = ROOT / ".tools" / "hurl" / HURL_VERSION / f"{key[0]}-{key[1]}" / "hurl"
    if target.is_file():
        validate_version(target)
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hurl-download-") as temporary:
        archive = Path(temporary) / asset.archive
        download(asset, archive)
        if sha256(archive) != asset.sha256:
            raise RuntimeError("Hurl archive checksum mismatch")
        candidate = Path(temporary) / "hurl"
        extract_hurl(archive, candidate)
        install_executable(candidate, target)
    validate_version(target)
    return target


def validate_version(executable: Path) -> None:
    result = subprocess.run(
        [str(executable), "--version"],
        check=False,
        text=True,
        capture_output=True,
        timeout=10,
    )
    first_line = result.stdout.splitlines()[0] if result.stdout else ""
    if result.returncode != 0 or not first_line.startswith(f"hurl {HURL_VERSION} "):
        raise RuntimeError("Hurl executable version does not match the repository pin")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-path", action="store_true")
    arguments = parser.parse_args()
    executable = ensure_hurl()
    if arguments.print_path:
        print(executable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
