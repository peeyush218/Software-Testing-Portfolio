"""An in-memory wallet for an academic software-testing demonstration."""

from dataclasses import dataclass


class WalletError(ValueError):
    pass


@dataclass
class Transaction:
    reference: str
    kind: str
    account: str
    amount: int
    status: str
    recipient: str = ""


class Wallet:
    def __init__(self):
        self.balances = {"alice": 500, "bob": 100}
        self.transactions = []

    def login(self, username, password):
        if username not in self.balances or password != "demo123":
            raise WalletError("Invalid username or password.")
        return username

    def _amount(self, value):
        value = value.strip()
        if not value.isascii() or not value.isdecimal() or len(value) > 9:
            raise WalletError("Enter a positive whole-rupee amount.")
        amount = int(value)
        if amount == 0:
            raise WalletError("Enter a positive whole-rupee amount.")
        return amount

    def _record(self, kind, account, amount, status, recipient=""):
        reference = f"TX-{len(self.transactions) + 1:04d}"
        transaction = Transaction(reference, kind, account, amount, status, recipient)
        self.transactions.append(transaction)
        return transaction

    def top_up(self, account, value):
        amount = self._amount(value)
        if not 10 <= amount <= 5000:
            raise WalletError("Top-up must be between ₹10 and ₹5,000.")
        self.balances[account] += amount
        return self._record("Top-up", account, amount, "Successful")

    def transfer(self, account, recipient, value):
        amount = self._amount(value)
        if recipient == account or recipient not in self.balances:
            raise WalletError("Choose another existing wallet.")
        if amount > self.balances[account]:
            raise WalletError("Insufficient balance.")
        self.balances[account] -= amount
        self.balances[recipient] += amount
        return self._record("Transfer", account, amount, "Successful", recipient)

    def start_payment(self, account, value):
        amount = self._amount(value)
        if amount > self.balances[account]:
            raise WalletError("Insufficient balance.")
        self.balances[account] -= amount
        return self._record("Payment", account, amount, "Pending", "Demo merchant")

    def complete_payment(self, account, reference, succeeded):
        payment = next(
            (entry for entry in self.transactions if entry.reference == reference),
            None,
        )
        if payment is None or payment.kind != "Payment" or payment.account != account:
            raise WalletError("Payment not found.")
        if payment.status != "Pending":
            raise WalletError("Payment has already been finalized.")
        if succeeded:
            payment.status = "Successful"
        else:
            self.balances[account] += payment.amount
            payment.status = "Failed"
        return payment

    def history(self, account):
        return [
            entry for entry in self.transactions
            if account in (entry.account, entry.recipient)
        ]
