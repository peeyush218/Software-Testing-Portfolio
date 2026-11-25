# Test execution summary

Demo v1.0 was tested on Windows with Python 3.13.9 and Tk 8.6. The UI driver exercised the app's sign-in, top-up, transfer, simulated payment, and history screens.

| Run | Planned | Passed | Failed | Blocked | Not run |
|---|---:|---:|---:|---:|---:|
| Baseline desktop UI | 17 | 17 | 0 | 0 | 0 |
| Python unit tests | 6 | 6 | 0 | 0 | 0 |
| White-box decision tests | 8 | 8 | 0 | 0 | 0 |
| HTTP API tests using in-process transport | 8 | 8 | 0 | 0 | 0 |
| **Baseline total** | **39** | **39** | **0** | **0** | **0** |
| Seeded defect drill | 1 | 0 | 1 | 0 | 0 |

All 39 baseline cases passed. The white-box trace observed 20 of 20 outcomes across 10 Wallet decisions. The API tests exercised the HTTP parser and request handler using in-process streams because the execution sandbox blocked localhost TCP. Use `--live` to test the same suite over TCP on a machine with loopback access.

The baseline tests confirmed no defects. DRILL-01 reproduced the injected missing refund and the corresponding baseline case verified a return to ₹500.

The app uses two demo accounts, whole-rupee inputs, and session-only storage. Test results cover simulated payments in this offline environment.

[Combined run output](All_Test_Run.txt) · [Case results](../03_Test_Execution/Execution_Log.csv) · [Defect report](../04_Defect_Reports/BUG-001.md)
