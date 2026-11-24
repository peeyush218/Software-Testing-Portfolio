# Test automation

This portfolio uses Python's built-in `unittest` for wallet logic and a Tkinter test runner for desktop UI flows. Run both from the repository root in a graphical desktop session.

```powershell
python 05_Test_Automation/test_wallet.py
python 05_Test_Automation/run_ui_cases.py
```

The unit script checks six rules. The UI script opens a fresh app per case, fills entry fields, invokes the app's buttons, and compares the displayed messages, balances, and history with the case expectations. The final defect drill is expected to fail on the seeded variant. The runner reports success if all baseline cases pass and the drill detects the injected fault.

Use `--record` to replace the CSV logs with a new run. The checked-in logs contain the original results. On Windows, you can add `--screenshots` to capture current evidence if Pillow is installed. The ordinary test commands require only Python and Tkinter.
