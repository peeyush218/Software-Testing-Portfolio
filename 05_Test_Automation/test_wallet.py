"""Independent unit checks for wallet operations."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from wallet import Wallet, WalletError


class WalletTests(unittest.TestCase):
    def setUp(self):
        self.wallet = Wallet()

    def test_top_up_stores_reference_and_amount(self):
        record = self.wallet.top_up("alice", "10")
        self.assertEqual(("TX-0001", 10, "Successful"),
                         (record.reference, record.amount, record.status))
        self.assertEqual(510, self.wallet.balances["alice"])

    def test_negative_and_fractional_amounts_do_not_change_state(self):
        for amount in ("-10", "10.50"):
            with self.subTest(amount=amount), self.assertRaises(WalletError):
                self.wallet.top_up("alice", amount)
        self.assertEqual(500, self.wallet.balances["alice"])
        self.assertEqual([], self.wallet.history("alice"))

    def test_exact_balance_transfer_updates_both_accounts(self):
        entry = self.wallet.transfer("alice", "bob", "500")
        self.assertEqual({"alice": 0, "bob": 600}, self.wallet.balances)
        self.assertEqual([entry], self.wallet.history("bob"))

    def test_failed_payment_returns_reserved_funds_once(self):
        entry = self.wallet.start_payment("alice", "200")
        self.wallet.complete_payment("alice", entry.reference, False)
        with self.assertRaises(WalletError):
            self.wallet.complete_payment("alice", entry.reference, False)
        self.assertEqual(500, self.wallet.balances["alice"])
        self.assertEqual("Failed", entry.status)

    def test_successful_payment_keeps_reserved_funds_deducted(self):
        entry = self.wallet.start_payment("alice", "200")
        self.wallet.complete_payment("alice", entry.reference, True)
        self.assertEqual(300, self.wallet.balances["alice"])
        self.assertEqual("Successful", entry.status)

    def test_history_shows_only_the_accounts_own_activity(self):
        self.wallet.top_up("alice", "100")
        self.assertEqual([], self.wallet.history("bob"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
