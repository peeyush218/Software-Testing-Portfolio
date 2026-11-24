# Test execution summary

Demo v1.0 was tested on Windows with Python 3.13.9 and Tk 8.6. The UI driver exercised the app's sign-in, top-up, transfer, simulated payment, and history screens.

| Run | Planned | Passed | Failed | Blocked | Not run |
|---|---:|---:|---:|---:|---:|
| Baseline desktop UI | 17 | 17 | 0 | 0 | 0 |
| Python unit tests | 6 | 6 | 0 | 0 | 0 |
| Seeded defect drill | 1 | 0 | 1 | 0 | 0 |

All 17 executed baseline UI cases matched their expected results. The six wallet unit tests passed. No defects were confirmed in these baseline runs. DRILL-01 exercised a deliberately injected missing refund. The defect was reproduced in the variant and the corresponding baseline case verified a return to ₹500.

The app uses two demo accounts, whole-rupee inputs, and session-only storage. Test results cover simulated payments in this offline environment.

[UI run output](UI_Run.txt) · [Unit run output](Unit_Run.txt) · [Case results](../03_Test_Execution/Execution_Log.csv) · [Defect report](../04_Defect_Reports/BUG-001.md)
