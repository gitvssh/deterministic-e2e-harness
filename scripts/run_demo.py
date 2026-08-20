from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hurl_tool import ensure_hurl

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "examples" / "payment_flow" / "app" / "server.py"
SPEC = ROOT / "examples" / "payment_flow" / "specs" / "TS-PAY-001.hurl"


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def wait_until_ready(base_url: str, process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("synthetic API stopped before becoming ready")
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except urllib.error.URLError, TimeoutError:
            time.sleep(0.05)
    raise RuntimeError("synthetic API did not become ready")


def run_demo() -> None:
    port = reserve_port()
    base_url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [sys.executable, str(SERVER), "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_until_ready(base_url, process)
        result = subprocess.run(
            [
                str(ensure_hurl()),
                "--test",
                "--variable",
                f"base_url={base_url}",
                "--variable",
                f"run_id={uuid.uuid4().hex[:16]}",
                str(SPEC),
            ],
            cwd=ROOT,
            check=False,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Hurl journey failed with exit {result.returncode}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main() -> int:
    run_demo()
    print("Synthetic registration, decline, retry, and capture journey passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
