"""Drive the desktop UI and record the actual results in the portfolio."""

import argparse
import csv
import ctypes
from datetime import date
from pathlib import Path
import sys
import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from demo import WalletApp
from wallet import Wallet


def case(case_id, module, technique, steps, expected, action, screenshot=""):
    return case_id, module, technique, steps, expected, action, screenshot


class UIFixture:
    def __init__(self, root):
        self.root = root
        self.app = WalletApp(root)

    def click(self, button, **fields):
        for name, value in fields.items():
            entry = self.app.fields[name]
            entry.delete(0, "end")
            entry.insert(0, str(value))
        self.app.buttons[button].invoke()
        self.root.update()

    def login(self, username="alice", password="demo123"):
        self.click("login", username=username, password=password)
        return self.app.balance.get() if self.app.account else self.app.status.get()

    def rows(self):
        return [self.app.history.item(item, "values") for item in self.app.history.get_children()]

    def feedback(self):
        return f"{self.app.status.get()} | balance {self.app.balance.get()} | history rows {len(self.rows())}"

    def top_up(self, amount):
        self.login()
        self.click("top_up", top_up=amount)
        return self.feedback()

    def transfer(self, amount, recipient):
        self.login()
        self.click("transfer", transfer=amount, recipient=recipient)
        if not self.rows():
            return self.feedback()
        sender = self.feedback()
        self.app.show_login()
        recipient_balance = self.login("bob")
        row = self.rows()[0]
        return f"{sender} | bob {recipient_balance} | history {' / '.join(row)}"

    def payment(self, decision):
        self.login()
        self.click("payment", payment=200)
        pending = self.feedback()
        if decision == "pending":
            return pending
        self.app.history.selection_set(self.app.history.get_children()[0])
        self.click(decision)
        return f"{pending} -> {self.feedback()} | history status {self.rows()[0][-1]}"

    def history(self):
        self.login()
        self.click("top_up", top_up=100)
        self.click("transfer", transfer=200, recipient="bob")
        return " | ".join(" / ".join(row) for row in self.rows())


class MissingRefundDrill(Wallet):
    """Deliberately seeded fault for the isolated defect reporting exercise."""

    def complete_payment(self, account, reference, succeeded):
        payment = super().complete_payment(account, reference, succeeded)
        if not succeeded:
            self.balances[account] -= payment.amount
        return payment


def cases():
    definitions = [
        case("TC-01", "Login", "Equivalence partitioning",
             "Sign in as alice with demo123; read the wallet balance.",
             "₹500", lambda ui: ui.login()),
        case("TC-02", "Login", "Equivalence partitioning",
             "Sign in as alice with an incorrect password.",
             "Invalid username or password.", lambda ui: ui.login(password="wrong")),
    ]
    for number, amount, accepted in [
        (3, 9, False), (4, 10, True), (5, 11, True),
        (6, 4999, True), (7, 5000, True), (8, 5001, False),
    ]:
        message = "TX-0001 • Successful" if accepted else "Top-up must be between ₹10 and ₹5,000."
        balance = 500 + amount if accepted else 500
        definitions.append(case(
            f"TC-{number:02}", "Top-up", "Boundary value analysis",
            f"Sign in as alice; submit a ₹{amount:,} top-up; check message, balance, and history.",
            f"{message} | balance ₹{balance:,} | history rows {int(accepted)}",
            lambda ui, amount=amount: ui.top_up(amount),
        ))
    definitions.extend([
        case("TC-09", "Transfer", "Decision table / equivalence partitioning",
             "Sign in as alice and send ₹200 to bob; check both accounts and bob's history.",
             "TX-0001 • Successful | balance ₹300 | history rows 1 | bob ₹300 | history TX-0001 / Transfer / alice / bob / ₹200 / Successful",
             lambda ui: ui.transfer(200, "bob"), "TC-09-transfer.png"),
        case("TC-10", "Transfer", "Decision table",
             "Sign in as alice; try sending ₹501 to bob.",
             "Insufficient balance. | balance ₹500 | history rows 0",
             lambda ui: ui.transfer(501, "bob")),
        case("TC-11", "Transfer", "Decision table",
             "Sign in as alice; try sending ₹200 to unknown.",
             "Choose another existing wallet. | balance ₹500 | history rows 0",
             lambda ui: ui.transfer(200, "unknown")),
        case("TC-12", "Transfer", "Decision table",
             "Sign in as alice; try sending ₹501 to unknown.",
             "Choose another existing wallet. | balance ₹500 | history rows 0",
             lambda ui: ui.transfer(501, "unknown")),
        case("TC-13", "Transfer", "Equivalence partitioning",
             "Sign in as alice; try sending ₹0 to bob.",
             "Enter a positive whole-rupee amount. | balance ₹500 | history rows 0",
             lambda ui: ui.transfer(0, "bob")),
        case("TC-14", "Payment", "State transition",
             "Sign in as alice; start a ₹200 payment and observe the pending transaction.",
             "TX-0001 • Pending | balance ₹300 | history rows 1",
             lambda ui: ui.payment("pending")),
        case("TC-15", "Payment", "State transition",
             "Sign in as alice; start a ₹200 payment; select it; complete it; inspect balance and history.",
             "TX-0001 • Pending | balance ₹300 | history rows 1 -> TX-0001 • Successful | balance ₹300 | history rows 1 | history status Successful",
             lambda ui: ui.payment("success")),
        case("TC-16", "Payment", "State transition",
             "Sign in as alice; start a ₹200 payment; select it; fail it; inspect balance and history.",
             "TX-0001 • Pending | balance ₹300 | history rows 1 -> TX-0001 • Failed | balance ₹500 | history rows 1 | history status Failed",
             lambda ui: ui.payment("fail"), "TC-16-payment-refund.png"),
        case("TC-17", "History", "Functional",
             "Sign in as alice; top up ₹100 and send ₹200 to bob; read both history rows.",
             "TX-0002 / Transfer / alice / bob / ₹200 / Successful | TX-0001 / Top-up / alice /  / ₹100 / Successful",
             lambda ui: ui.history()),
    ])
    return definitions


def screenshot(root, name):
    from PIL import ImageGrab

    root.update()
    handle = ctypes.windll.user32.GetParent(root.winfo_id()) or root.winfo_id()
    ImageGrab.grab(window=handle).save(ROOT / "07_Screenshots" / name)


def write_csv(path, headings, rows):
    with (ROOT / path).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headings)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="Update the portfolio CSV files.")
    parser.add_argument("--screenshots", action="store_true",
                        help="Capture the UI on Windows using Pillow.")
    args = parser.parse_args()
    designs, results = [], []
    drill_result = None
    for case_id, module, technique, steps, expected, action, image in cases():
        root = tk.Tk()
        if not args.screenshots:
            root.withdraw()
        try:
            ui = UIFixture(root)
            actual = action(ui)
            status = "Pass" if expected == actual else "Fail"
            designs.append((case_id, module, technique, "Fresh app; alice ₹500 and bob ₹100.",
                            steps, expected))
            results.append((case_id, "Demo v1.0", date.today().isoformat(), expected, actual,
                            status, image if args.screenshots else ""))
            print(f"{case_id} {status}")
            if args.screenshots and image:
                screenshot(root, image)
            if case_id == "TC-16":
                root.destroy()
                root = tk.Tk()
                if not args.screenshots:
                    root.withdraw()
                ui = UIFixture(root)
                ui.app.wallet = MissingRefundDrill()
                observed = action(ui)
                drill_result = ("DRILL-01", "Seeded missing-refund variant", date.today().isoformat(),
                                expected, observed, "Fail" if observed != expected else "Pass",
                                "DRILL-01-missing-refund.png" if args.screenshots else "")
                if args.screenshots:
                    screenshot(root, drill_result[-1])
        finally:
            root.destroy()
    if args.record:
        write_csv("02_Test_Case_Design/Test_Cases.csv",
                  ("ID", "Module", "Technique", "Preconditions", "Steps and data", "Expected result"), designs)
        headings = ("ID", "Build", "Date", "Expected", "Actual", "Status", "Evidence filename")
        write_csv("03_Test_Execution/Execution_Log.csv", headings, results)
        write_csv("03_Test_Execution/Defect_Drill_Log.csv", headings, [drill_result])
    passed = sum(row[5] == "Pass" for row in results)
    print(f"Demo v1.0: {passed}/{len(results)} passed.")
    print(f"DRILL-01: {drill_result[5]} (see Defect_Drill_Log.csv for recorded values).")
    return 0 if passed == len(results) and drill_result[5] == "Fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
