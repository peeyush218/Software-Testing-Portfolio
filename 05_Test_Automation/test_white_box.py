"""White-box tests and decision tracing for the Wallet source."""

import ast
import inspect
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from wallet import Wallet, WalletError


class WalletWhiteBoxTests(unittest.TestCase):
    def setUp(self):
        self.wallet = Wallet()

    def test_wb_01_login_guard(self):
        self.assertEqual("alice", self.wallet.login("alice", "demo123"))
        for user, password in (("unknown", "demo123"), ("alice", "wrong")):
            with self.subTest(user=user), self.assertRaisesRegex(WalletError, "Invalid username"):
                self.wallet.login(user, password)

    def test_wb_02_amount_format_and_zero_guards(self):
        for value in ("١٠", "10.5", "1000000000", "0"):
            with self.subTest(value=value), self.assertRaisesRegex(WalletError, "positive whole-rupee"):
                self.wallet._amount(value)
        self.assertEqual(10, self.wallet._amount(" 10 "))

    def test_wb_03_top_up_range_guard(self):
        for value in ("9", "5001"):
            with self.subTest(value=value), self.assertRaisesRegex(WalletError, "Top-up must be"):
                self.wallet.top_up("alice", value)
        self.assertEqual(500, self.wallet.balances["alice"])
        self.assertEqual([], self.wallet.transactions)
        self.assertEqual("TX-0001", self.wallet.top_up("alice", "10").reference)
        self.assertEqual(510, self.wallet.balances["alice"])

    def test_wb_04_transfer_recipient_guard(self):
        for recipient in ("alice", "unknown"):
            with self.subTest(recipient=recipient), self.assertRaisesRegex(WalletError, "existing wallet"):
                self.wallet.transfer("alice", recipient, "501")
        self.assertEqual({"alice": 500, "bob": 100}, self.wallet.balances)
        self.assertEqual([], self.wallet.transactions)

    def test_wb_05_transfer_balance_guard(self):
        with self.assertRaisesRegex(WalletError, "Insufficient balance"):
            self.wallet.transfer("alice", "bob", "501")
        self.assertEqual([], self.wallet.transactions)
        self.wallet.transfer("alice", "bob", "500")
        self.assertEqual({"alice": 0, "bob": 600}, self.wallet.balances)

    def test_wb_06_payment_start_balance_guard(self):
        with self.assertRaisesRegex(WalletError, "Insufficient balance"):
            self.wallet.start_payment("alice", "501")
        self.assertEqual([], self.wallet.transactions)
        self.assertEqual("Pending", self.wallet.start_payment("alice", "500").status)
        self.assertEqual(0, self.wallet.balances["alice"])

    def test_wb_07_payment_lookup_type_and_owner_guard(self):
        top_up = self.wallet.top_up("alice", "10")
        payment = self.wallet.start_payment("alice", "200")
        for owner, reference in (("alice", "missing"), ("alice", top_up.reference),
                                 ("bob", payment.reference)):
            with self.subTest(owner=owner, reference=reference), self.assertRaisesRegex(
                    WalletError, "Payment not found"):
                self.wallet.complete_payment(owner, reference, True)
        self.assertEqual("Pending", payment.status)
        self.assertEqual(310, self.wallet.balances["alice"])

    def test_wb_08_payment_success_failure_and_finalized_guard(self):
        successful = self.wallet.start_payment("alice", "200")
        self.wallet.complete_payment("alice", successful.reference, True)
        self.assertEqual(("Successful", 300), (successful.status, self.wallet.balances["alice"]))
        failed = self.wallet.start_payment("alice", "100")
        self.wallet.complete_payment("alice", failed.reference, False)
        self.assertEqual(("Failed", 300), (failed.status, self.wallet.balances["alice"]))
        with self.assertRaisesRegex(WalletError, "already been finalized"):
            self.wallet.complete_payment("alice", failed.reference, False)
        self.assertEqual(300, self.wallet.balances["alice"])


def wallet_decisions(path):
    """Return direct if statements in Wallet methods and their two next lines."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    wallet = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Wallet")
    for method in wallet.body:
        if not isinstance(method, ast.FunctionDef):
            continue
        for i, statement in enumerate(method.body):
            if isinstance(statement, ast.If):
                otherwise = statement.orelse[0] if statement.orelse else method.body[i + 1]
                yield method.name, statement.lineno, statement.body[0].lineno, otherwise.lineno


def main():
    path = Path(inspect.getsourcefile(Wallet))
    decisions = list(wallet_decisions(path))
    edges = set()
    previous_line = {}

    def trace(frame, event, _argument):
        if frame.f_code.co_filename != str(path):
            return None
        if event == "line":
            previous = previous_line.get(frame)
            edges.add((previous, frame.f_lineno))
            previous_line[frame] = frame.f_lineno
        elif event == "return":
            previous_line.pop(frame, None)
        return trace

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WalletWhiteBoxTests)
    saved_trace = sys.gettrace()
    sys.settrace(trace)
    try:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        sys.settrace(saved_trace)

    observed = 0
    for method, line, true_line, false_line in decisions:
        yes = (line, true_line) in edges
        no = (line, false_line) in edges
        observed += yes + no
        print(f"{method}:{line} | true {'hit' if yes else 'miss'} | false {'hit' if no else 'miss'}")
    expected = 2 * len(decisions)
    print(f"Wallet source decisions: {observed}/{expected} outcomes observed ({len(decisions)} decisions).")
    return 0 if result.wasSuccessful() and observed == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
