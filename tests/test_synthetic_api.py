from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

import pytest

from examples.payment_flow.app.server import SyntheticServer, stable_id


@contextmanager
def running_server() -> Iterator[str]:
    server = SyntheticServer(("127.0.0.1", 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, cast(dict[str, Any], json.loads(response.read()))
    except urllib.error.HTTPError as error:
        return error.code, cast(dict[str, Any], json.loads(error.read()))


def test_stable_id_is_repeatable_without_exposing_source_value() -> None:
    first = stable_id("usr", "candidate-one")
    assert first == stable_id("usr", "candidate-one")
    assert first != stable_id("usr", "candidate-two")
    assert "candidate-one" not in first


def test_complete_decline_retry_capture_flow() -> None:
    with running_server() as base_url:
        status, health = request_json(f"{base_url}/health")
        assert (status, health) == (200, {"status": "ok"})

        status, user = request_json(
            f"{base_url}/users",
            method="POST",
            payload={"external_id": "candidate-test", "email": "candidate-test@example.com"},
        )
        assert status == 201
        assert user["status"] == "active"

        payment = {
            "user_id": user["user_id"],
            "order_id": "order-test",
            "amount": 12500,
            "payment_token": "synthetic-decline",
        }
        status, decline = request_json(f"{base_url}/payments", method="POST", payload=payment)
        assert status == 402
        assert decline == {"code": "PAYMENT_DECLINED", "retryable": True}

        payment["payment_token"] = "synthetic-approve"
        status, captured = request_json(
            f"{base_url}/payments/retry", method="POST", payload=payment
        )
        assert status == 200
        assert captured["status"] == "captured"
        assert captured["amount"] == 12500

        status, stored = request_json(f"{base_url}/payments/{captured['payment_id']}")
        assert status == 200
        assert stored == captured


def test_real_looking_email_is_rejected() -> None:
    with running_server() as base_url:
        status, body = request_json(
            f"{base_url}/users",
            method="POST",
            payload={"external_id": "candidate-test", "email": "person@example.org"},
        )
        assert status == 400
        assert body["code"] == "INVALID_REQUEST"


@pytest.mark.parametrize("amount", [0, -1, True, "12500"])
def test_invalid_amount_is_rejected(amount: object) -> None:
    with running_server() as base_url:
        _, user = request_json(
            f"{base_url}/users",
            method="POST",
            payload={"external_id": "candidate-test", "email": "candidate-test@example.com"},
        )
        status, body = request_json(
            f"{base_url}/payments",
            method="POST",
            payload={
                "user_id": user["user_id"],
                "order_id": "order-test",
                "amount": amount,
                "payment_token": "synthetic-decline",
            },
        )
        assert status == 400
        assert body["code"] == "INVALID_REQUEST"
