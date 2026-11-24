# Digital Wallet and Payment Management System

**Subject:** Software Testing

| Team member | Roll number |
|---|---|
| Peeyush Punj | 1MS23IS088 |
| Prakhar Srivastava | 1MS23IS091 |

This portfolio tests a local desktop wallet that supports sign-in, demo top-ups, transfers between two wallets, simulated merchant payments, and transaction history. The objective is to verify transaction outcomes, balance changes, input validation, and the activity shown for each account.

## Run the wallet

1. Install Python 3 with Tkinter if it is absent. On Windows, verify it with `python --version` and `python -m tkinter`. The second command should open a small test window. Close the test window.
2. Open PowerShell in this folder and run `python app/demo.py`. On Windows, use `py` in place of `python` if your installation exposes that command.
3. Sign in as `alice` or `bob` with the demo password `demo123`. Alice starts with ₹500 and Bob starts with ₹100.
4. Enter a whole-rupee amount to top up, send a transfer, or start a simulated payment. To finalize a payment, click its row in Transaction history and select **Complete selected payment** or **Fail selected payment**.
5. Sign out to switch accounts within the same running app. Closing and reopening the app resets balances and history. Funds and payment outcomes are simulated.

## Portfolio

| Deliverable | File |
|---|---|
| Test plan, scope, rules, and payment diagram | [Test plan](01_Test_Plan/Test_Plan.md) |
| Seventeen test cases | [Test cases](02_Test_Case_Design/Test_Cases.csv) |
| Technique notes and transfer decision table | [Test design](02_Test_Case_Design/Test_Design.md) |
| Recorded expected and actual UI results | [Execution log](03_Test_Execution/Execution_Log.csv) |
| Defect reporting exercise and retest | [BUG-001](04_Defect_Reports/BUG-001.md) |
| Scripts and rerun instructions | [Automation](05_Test_Automation/README.md) |
| Results, counts, and run logs | [Test execution summary](06_Test_Reports/Test_Summary.md) |
| Images from the run | [Screenshots](07_Screenshots/README.md) |
| Findings and coverage limits | [Conclusion](Conclusion.md) |

For GitHub publishing steps and a short viva walkthrough, see [Submission guide](SUBMISSION_GUIDE.md).
