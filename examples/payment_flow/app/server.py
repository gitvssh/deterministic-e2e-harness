from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, cast
from urllib.parse import urlparse


@dataclass
class SyntheticState:
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    payments: dict[str, dict[str, Any]] = field(default_factory=dict)


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def parse_payload(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("invalid content length") from exc
    if length <= 0 or length > 16_384:
        raise ValueError("invalid payload size")
    try:
        payload = json.loads(handler.rfile.read(length))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    return cast(dict[str, Any], payload)


def require_string(payload: dict[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def require_amount(payload: dict[str, Any]) -> int:
    value = payload.get("amount")
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("amount must be a positive integer")
    return value


class SyntheticHandler(BaseHTTPRequestHandler):
    server: SyntheticServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def respond(self, status: HTTPStatus, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.respond(HTTPStatus.OK, {"status": "ok"})
            return
        prefix = "/payments/"
        if path.startswith(prefix):
            payment_id = path.removeprefix(prefix)
            payment = self.server.state.payments.get(payment_id)
            if payment is None:
                self.respond(HTTPStatus.NOT_FOUND, {"code": "PAYMENT_NOT_FOUND"})
                return
            self.respond(HTTPStatus.OK, payment)
            return
        self.respond(HTTPStatus.NOT_FOUND, {"code": "NOT_FOUND"})

    def do_POST(self) -> None:
        try:
            payload = parse_payload(self)
            path = urlparse(self.path).path
            if path == "/users":
                self.register_user(payload)
                return
            if path == "/payments":
                self.submit_payment(payload)
                return
            if path == "/payments/retry":
                self.retry_payment(payload)
                return
            self.respond(HTTPStatus.NOT_FOUND, {"code": "NOT_FOUND"})
        except ValueError as exc:
            self.respond(HTTPStatus.BAD_REQUEST, {"code": "INVALID_REQUEST", "detail": str(exc)})

    def register_user(self, payload: dict[str, Any]) -> None:
        external_id = require_string(payload, "external_id")
        email = require_string(payload, "email")
        if not email.endswith("@example.com"):
            raise ValueError("only synthetic example.com addresses are accepted")
        user_id = stable_id("usr", external_id)
        user = {"user_id": user_id, "status": "active"}
        self.server.state.users[user_id] = user
        self.respond(HTTPStatus.CREATED, user)

    def payment_fields(self, payload: dict[str, Any]) -> tuple[str, str, int, str]:
        user_id = require_string(payload, "user_id")
        order_id = require_string(payload, "order_id")
        amount = require_amount(payload)
        token = require_string(payload, "payment_token")
        if user_id not in self.server.state.users:
            raise ValueError("unknown user")
        return user_id, order_id, amount, token

    def submit_payment(self, payload: dict[str, Any]) -> None:
        _, _, _, token = self.payment_fields(payload)
        if token != "synthetic-decline":
            raise ValueError("initial request must use the synthetic decline token")
        self.respond(
            HTTPStatus.PAYMENT_REQUIRED,
            {"code": "PAYMENT_DECLINED", "retryable": True},
        )

    def retry_payment(self, payload: dict[str, Any]) -> None:
        user_id, order_id, amount, token = self.payment_fields(payload)
        if token != "synthetic-approve":
            raise ValueError("retry must use the synthetic approval token")
        payment_id = stable_id("pay", f"{user_id}:{order_id}:{amount}")
        payment = {
            "payment_id": payment_id,
            "user_id": user_id,
            "order_id": order_id,
            "amount": amount,
            "status": "captured",
        }
        self.server.state.payments[payment_id] = payment
        self.respond(HTTPStatus.OK, payment)


class SyntheticServer(ThreadingHTTPServer):
    state: SyntheticState

    def __init__(self, address: tuple[str, int]) -> None:
        super().__init__(address, SyntheticHandler)
        self.state = SyntheticState()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    arguments = parser.parse_args()
    server = SyntheticServer((arguments.host, arguments.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
