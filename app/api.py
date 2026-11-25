"""Loopback-only HTTP interface for the simulated wallet."""

import argparse
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets

from wallet import Wallet, WalletError


class RequestError(ValueError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class WalletHTTPServer(HTTPServer):
    def __init__(self, port):
        self.wallet = Wallet()
        self.sessions = {}
        super().__init__(("127.0.0.1", port), WalletHandler)


class WalletHandler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8192:
                raise ValueError()
            body = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeError):
            raise RequestError(HTTPStatus.BAD_REQUEST, "Expected a JSON object.") from None
        if not isinstance(body, dict):
            raise RequestError(HTTPStatus.BAD_REQUEST, "Expected a JSON object.")
        return body

    def account(self):
        scheme, _, token = self.headers.get("Authorization", "").partition(" ")
        user = self.server.sessions.get(token) if scheme.lower() == "bearer" else None
        if user is None:
            raise RequestError(HTTPStatus.UNAUTHORIZED, "A valid bearer token is required.")
        return user

    @staticmethod
    def string_field(data, field):
        value = data.get(field)
        if not isinstance(value, str):
            raise RequestError(HTTPStatus.BAD_REQUEST, f"{field} must be a string.")
        return value

    def amount_field(self, data):
        amount = data.get("amount")
        if type(amount) is not int:
            raise RequestError(HTTPStatus.BAD_REQUEST, "amount must be a whole number.")
        return str(amount)

    def dispatch(self, method):
        wallet = self.server.wallet
        if method == "POST" and self.path == "/login":
            data = self.read_json()
            username = self.string_field(data, "username")
            password = self.string_field(data, "password")
            try:
                account = wallet.login(username, password)
            except WalletError as error:
                raise RequestError(HTTPStatus.UNAUTHORIZED, str(error)) from error
            token = secrets.token_urlsafe(24)
            self.server.sessions[token] = account
            return HTTPStatus.OK, {"account": account, "token": token}

        account = self.account()
        if method == "GET" and self.path == "/balance":
            return HTTPStatus.OK, {"account": account, "balance": wallet.balances[account]}
        if method == "GET" and self.path == "/transactions":
            return HTTPStatus.OK, {"transactions": [asdict(tx) for tx in wallet.history(account)]}

        if method == "POST":
            path = self.path.strip("/").split("/")
            if self.path == "/top-ups":
                tx = wallet.top_up(account, self.amount_field(self.read_json()))
                return HTTPStatus.CREATED, asdict(tx)
            if self.path == "/transfers":
                data = self.read_json()
                tx = wallet.transfer(account, self.string_field(data, "recipient"),
                                     self.amount_field(data))
                return HTTPStatus.CREATED, asdict(tx)
            if self.path == "/payments":
                tx = wallet.start_payment(account, self.amount_field(self.read_json()))
                return HTTPStatus.CREATED, asdict(tx)
            if len(path) == 3 and path[0] == "payments" and path[2] == "complete":
                succeeded = self.read_json().get("succeeded")
                if type(succeeded) is not bool:
                    raise RequestError(HTTPStatus.BAD_REQUEST, "succeeded must be a Boolean.")
                tx = wallet.complete_payment(account, path[1], succeeded)
                return HTTPStatus.OK, asdict(tx)
        raise RequestError(HTTPStatus.NOT_FOUND, "Endpoint not found.")

    def handle_method(self, method):
        try:
            status, data = self.dispatch(method)
        except RequestError as error:
            status, data = error.status, {"error": str(error)}
        except WalletError as error:
            status, data = HTTPStatus.BAD_REQUEST, {"error": str(error)}
        self.reply(status, data)

    def do_GET(self):
        self.handle_method("GET")

    def do_POST(self):
        self.handle_method("POST")

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the local demo wallet API.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with WalletHTTPServer(args.port) as server:
        print(f"Wallet API listening at http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
