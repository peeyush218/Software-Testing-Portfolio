"""Run with python app/demo.py from the repository root."""

import tkinter as tk
from tkinter import ttk

from wallet import Wallet, WalletError


class WalletApp:
    def __init__(self, root):
        self.root = root
        self.wallet = Wallet()
        self.account = None
        self.status = tk.StringVar()
        self.balance = tk.StringVar()
        self.fields = {}
        self.buttons = {}
        root.title("Digital Wallet and Payment Management System")
        root.geometry("860x650")
        root.minsize(780, 610)
        root.configure(background="#edf2f8")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#edf2f8")
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", background="#edf2f8", foreground="#152944",
                        font=("Segoe UI", 24, "bold"))
        style.configure("Page.TLabel", background="#edf2f8", foreground="#304964",
                        font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="white", foreground="#203954",
                        font=("Segoe UI", 10))
        style.configure("Balance.TLabel", background="#edf2f8", foreground="#113d67",
                        font=("Segoe UI", 24, "bold"))
        style.configure("TButton", padding=(9, 6), font=("Segoe UI", 9))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        self.frame = ttk.Frame(root, padding=24, style="Page.TFrame")
        self.frame.pack(fill="both", expand=True)
        self.show_login()

    def clear(self):
        for child in self.frame.winfo_children():
            child.destroy()
        self.fields.clear()
        self.buttons.clear()
        self.status.set("")

    def field(self, parent, key, label, secret=False):
        ttk.Label(parent, text=label, style="Card.TLabel").pack(anchor="w")
        entry = ttk.Entry(parent, show="*" if secret else "", width=20)
        entry.pack(fill="x", pady=(3, 8))
        self.fields[key] = entry

    def button(self, parent, key, label, command):
        self.buttons[key] = ttk.Button(parent, text=label, command=command)
        self.buttons[key].pack(fill="x", pady=3)

    def show_login(self):
        self.clear()
        self.account = None
        ttk.Label(self.frame, text="Digital Wallet", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.frame, text="Payment management demo", style="Page.TLabel").pack(anchor="w")
        card = ttk.Frame(self.frame, padding=20, style="Card.TFrame")
        card.pack(anchor="w", pady=20)
        self.field(card, "username", "Username")
        self.field(card, "password", "Password", secret=True)
        self.button(card, "login", "Sign in", self.sign_in)
        ttk.Label(self.frame, textvariable=self.status, style="Page.TLabel").pack(anchor="w")
        self.fields["username"].focus_set()

    def sign_in(self):
        try:
            self.account = self.wallet.login(
                self.fields["username"].get(), self.fields["password"].get()
            )
        except WalletError as error:
            self.status.set(str(error))
            return
        self.show_wallet()

    def show_wallet(self):
        self.clear()
        header = ttk.Frame(self.frame, style="Page.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Digital Wallet", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Sign out", command=self.show_login).pack(side="right")
        ttk.Label(self.frame, text=f"Available balance for {self.account}", style="Page.TLabel").pack(anchor="w")
        ttk.Label(self.frame, textvariable=self.balance, style="Balance.TLabel").pack(anchor="w")
        actions = ttk.Frame(self.frame, style="Page.TFrame")
        actions.pack(fill="x", pady=(12, 8))
        cards = []
        for title in ("Top up wallet", "Send money", "Simulate payment"):
            card = ttk.Frame(actions, padding=12, style="Card.TFrame")
            card.pack(side="left", fill="both", expand=True, padx=(0, 6))
            ttk.Label(card, text=title, style="Card.TLabel",
                      font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
            cards.append(card)
        top_up, transfer, payment = cards
        self.field(top_up, "top_up", "Amount (₹)")
        self.button(top_up, "top_up", "Add funds", lambda: self.act(
            self.wallet.top_up, self.account, self.fields["top_up"].get()))
        self.field(transfer, "recipient", "Recipient username")
        self.field(transfer, "transfer", "Amount (₹)")
        self.button(transfer, "transfer", "Send transfer", lambda: self.act(
            self.wallet.transfer, self.account, self.fields["recipient"].get(),
            self.fields["transfer"].get()))
        self.field(payment, "payment", "Amount (₹)")
        self.button(payment, "payment", "Start payment", lambda: self.act(
            self.wallet.start_payment, self.account, self.fields["payment"].get()))
        self.button(payment, "success", "Complete selected payment",
                    lambda: self.resolve_selected(True))
        self.button(payment, "fail", "Fail selected payment",
                    lambda: self.resolve_selected(False))
        ttk.Label(self.frame, textvariable=self.status, style="Page.TLabel").pack(anchor="w", pady=(2, 7))
        ttk.Label(self.frame, text="Transaction history", style="Page.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(2, 5))
        columns = ("reference", "kind", "from", "to", "amount", "status")
        self.history = ttk.Treeview(self.frame, columns=columns, show="headings", height=5)
        for column in columns:
            self.history.heading(column, text=column.title())
            self.history.column(column, width=110, minwidth=60)
        self.history.pack(fill="both", expand=True)
        self.refresh()

    def resolve_selected(self, succeeded):
        selected = self.history.selection()
        if not selected:
            self.status.set("Select a payment in transaction history.")
            return
        self.act(self.wallet.complete_payment, self.account, selected[0], succeeded)

    def act(self, operation, *args):
        try:
            transaction = operation(*args)
        except WalletError as error:
            self.status.set(str(error))
            return
        self.status.set(f"{transaction.reference} • {transaction.status}")
        self.refresh()

    def refresh(self):
        self.balance.set(f"₹{self.wallet.balances[self.account]:,}")
        self.history.delete(*self.history.get_children())
        for entry in reversed(self.wallet.history(self.account)):
            self.history.insert("", "end", iid=entry.reference, values=(
                entry.reference, entry.kind, entry.account, entry.recipient,
                f"₹{entry.amount:,}", entry.status,
            ))


if __name__ == "__main__":
    root = tk.Tk()
    WalletApp(root)
    root.mainloop()
