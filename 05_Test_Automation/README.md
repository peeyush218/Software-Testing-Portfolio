# Test automation

## Run all four suites

```powershell
python 05_Test_Automation/run_all.py
```

| Suite | Individual command |
|---|---|
| Black-box UI | `python 05_Test_Automation/run_ui_cases.py` |
| Wallet unit | `python 05_Test_Automation/test_wallet.py` |
| White-box decisions | `python 05_Test_Automation/test_white_box.py` |
| HTTP API | `python 05_Test_Automation/test_api.py` |

Use `python 05_Test_Automation/test_api.py --live` to run the same API cases over localhost TCP. The command starts its own temporary servers. The recorded baseline used in-process HTTP streams because the execution sandbox blocked localhost connections.

For an interactive demo, start `python app/api.py` in one terminal and run these commands in a separate PowerShell terminal:

```powershell
$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/login -ContentType 'application/json' -Body '{"username":"alice","password":"demo123"}'
Invoke-RestMethod -Uri http://127.0.0.1:8765/balance -Headers @{ Authorization = "Bearer $($session.token)" }
```

The response should show Alice with ₹500. Use **Ctrl+C** to stop the server.

## Original UI and unit runs

This portfolio uses Python's built-in `unittest` for wallet logic and a Tkinter test runner for desktop UI flows. Run both from the repository root in a graphical desktop session.

```powershell
python 05_Test_Automation/test_wallet.py
python 05_Test_Automation/run_ui_cases.py
```

The unit script checks six rules. The UI script opens a fresh app per case, fills entry fields, invokes the app's buttons, and compares the displayed messages, balances, and history with the case expectations. The final defect drill is expected to fail on the seeded variant. The runner reports success if all baseline cases pass and the drill detects the injected fault.

Use `--record` to replace the CSV logs with a new run. The checked-in logs contain the original results. On Windows, you can add `--screenshots` to capture current evidence if Pillow is installed. The ordinary test commands require only Python and Tkinter.
