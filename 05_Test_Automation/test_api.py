"""HTTP contract checks with in-process or live localhost transport."""

import argparse
from http.client import HTTPConnection, HTTPResponse
from io import BytesIO
import json
from pathlib import Path
import sys
from threading import Thread
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from api import WalletHandler, WalletHTTPServer
from wallet import Wallet


class StreamRequest:
    def __init__(self, request):
        self.incoming = BytesIO(request)
        self.outgoing = BytesIO()

    def makefile(self, _mode):
        return self.outgoing


class StreamWalletHandler(WalletHandler):
    def setup(self):
        self.rfile = self.request.incoming
        self.wfile = self.request.outgoing

    def finish(self):
        pass


class WalletAPITests(unittest.TestCase):
    live = False

    def setUp(self):
        if not self.live:
            self.server = SimpleNamespace(wallet=Wallet(), sessions={})
            return
        server = WalletHTTPServer(0)
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.shutdown)
        self.port = server.server_port

    def request(self, path, body=None, token=None, status=200):
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        data = None if body is None else json.dumps(body).encode("utf-8")
        method = "GET" if data is None else "POST"
        if self.live:
            connection = HTTPConnection("127.0.0.1", self.port, timeout=5)
            try:
                connection.request(method, path, body=data, headers=headers)
                with connection.getresponse() as response:
                    return self.check_response(response, status)
            finally:
                connection.close()
        headers.update({"Host": "127.0.0.1", "Content-Length": str(len(data or b""))})
        header_lines = "".join(f"{name}: {value}\r\n" for name, value in headers.items())
        wire = f"{method} {path} HTTP/1.0\r\n{header_lines}\r\n".encode("ascii")
        stream = StreamRequest(wire + (data or b""))
        StreamWalletHandler(stream, ("127.0.0.1", 0), self.server)
        stream.outgoing.seek(0)
        with HTTPResponse(stream, method=method) as response:
            response.begin()
            return self.check_response(response, status)

    def check_response(self, response, status):
        self.assertEqual(status, response.status)
        self.assertEqual("application/json", response.headers.get_content_type())
        return json.load(response)

    def login(self, name="alice"):
        return self.request("/login", {"username": name, "password": "demo123"})["token"]

    def balance(self, token):
        return self.request("/balance", token=token)["balance"]

    def test_api_01_login_returns_session_and_balance(self):
        token = self.login()
        self.assertTrue(token)
        self.assertEqual({"account": "alice", "balance": 500},
                         self.request("/balance", token=token))

    def test_api_02_bad_login_and_missing_token_are_rejected(self):
        self.assertIn("error", self.request("/login", {"username": "alice", "password": "wrong"},
                                           status=401))
        self.assertIn("error", self.request("/balance", status=401))

    def test_api_03_top_up_at_lower_limit_updates_balance(self):
        token = self.login()
        record = self.request("/top-ups", {"amount": 10}, token, status=201)
        self.assertEqual(("TX-0001", 10, "Successful"),
                         (record["reference"], record["amount"], record["status"]))
        self.assertEqual(510, self.balance(token))

    def test_api_04_invalid_top_ups_do_not_change_state(self):
        token = self.login()
        for amount in (9, 5001, 10.5):
            with self.subTest(amount=amount):
                self.assertIn("error", self.request("/top-ups", {"amount": amount}, token, status=400))
        self.assertEqual(500, self.balance(token))
        self.assertEqual([], self.request("/transactions", token=token)["transactions"])

    def test_api_05_transfer_updates_both_wallets_and_recipient_history(self):
        alice, bob = self.login(), self.login("bob")
        record = self.request("/transfers", {"recipient": "bob", "amount": 200}, alice, status=201)
        self.assertEqual("Successful", record["status"])
        self.assertEqual((300, 300), (self.balance(alice), self.balance(bob)))
        self.assertEqual([record], self.request("/transactions", token=bob)["transactions"])

    def test_api_06_rejected_transfers_do_not_change_state(self):
        alice, bob = self.login(), self.login("bob")
        for recipient, amount in (("bob", 501), ("unknown", 200)):
            with self.subTest(recipient=recipient):
                self.assertIn("error", self.request("/transfers", {"recipient": recipient, "amount": amount},
                                                   alice, status=400))
        self.assertEqual((500, 100), (self.balance(alice), self.balance(bob)))
        self.assertEqual([], self.request("/transactions", token=alice)["transactions"])

    def test_api_07_failed_payment_refunds_once(self):
        token = self.login()
        record = self.request("/payments", {"amount": 200}, token, status=201)
        self.assertEqual(("Pending", 300), (record["status"], self.balance(token)))
        path = f"/payments/{record['reference']}/complete"
        self.assertEqual("Failed", self.request(path, {"succeeded": False}, token)["status"])
        self.assertEqual(500, self.balance(token))
        self.assertIn("error", self.request(path, {"succeeded": False}, token, status=400))
        self.assertEqual(500, self.balance(token))

    def test_api_08_successful_payment_keeps_funds_deducted(self):
        token = self.login()
        record = self.request("/payments", {"amount": 200}, token, status=201)
        path = f"/payments/{record['reference']}/complete"
        self.assertEqual("Successful", self.request(path, {"succeeded": True}, token)["status"])
        self.assertEqual(300, self.balance(token))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Send requests over a localhost TCP socket.")
    WalletAPITests.live = parser.parse_args().live
    print("HTTP transport:", "localhost TCP" if WalletAPITests.live else "in-process HTTP streams", flush=True)
    sys.argv[1:] = []
    unittest.main(verbosity=2)
