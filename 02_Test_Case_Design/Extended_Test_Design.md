# White box and HTTP API test design

The desktop cases continue to use [black-box functional test design](Test_Design.md). The cases below test source decisions and the HTTP interface. Each starts with fresh test data.

## White-box cases

| Case | Source decision or path | Expected result |
|---|---|---|
| WB-01 | Valid login, unknown account, wrong password | Only valid credentials return Alice. |
| WB-02 | ASCII, decimal, length and zero amount guards | Invalid input is rejected. A padded positive integer is accepted. |
| WB-03 | Top-up range guard using ₹9, ₹5,001 and ₹10 | Only ₹10 is accepted and recorded. |
| WB-04 | Self and unknown recipients | Error occurs before the funds check. State stays unchanged. |
| WB-05 | Transfer ₹501 and exactly ₹500 | ₹501 is rejected. The ₹500 transfer leaves Alice at ₹0 and Bob at ₹600. |
| WB-06 | Start payment for ₹501 and exactly ₹500 | ₹501 is rejected. The ₹500 payment starts Pending with ₹0 available. |
| WB-07 | Missing payment, wrong type and wrong owner | Each lookup fails. The valid pending payment stays unchanged. |
| WB-08 | Complete, fail and repeat finalization | Success retains the deduction. Failure refunds it. Repeat finalization is rejected. |

The trace checks the true and false successors of the ten direct `if` decisions in the Wallet methods. The metric excludes compound-condition combinations, comprehensions and other modules.

## HTTP API cases

Authenticated calls use the bearer token from `POST /login`. The tests assert HTTP status, JSON and wallet state.

| Case | Request scenario | Expected result |
|---|---|---|
| API-01 | Sign in and query balance | HTTP 200, usable token and ₹500 for Alice. |
| API-02 | Bad password or missing token | HTTP 401 and JSON error. |
| API-03 | Top up ₹10 | HTTP 201, successful transaction and ₹510. |
| API-04 | Top up ₹9, ₹5,001 or a fraction | HTTP 400. Balance and history stay unchanged. |
| API-05 | Transfer ₹200 to Bob | HTTP 201. Both balances are ₹300 and Bob sees the transfer. |
| API-06 | Insufficient funds or unknown recipient | HTTP 400. Balances and sender history stay unchanged. |
| API-07 | Start and fail ₹200 payment, then repeat | HTTP 201 Pending at ₹300, HTTP 200 Failed at ₹500, then HTTP 400 with ₹500 still available. |
| API-08 | Start and complete ₹200 payment | HTTP 201 then 200, Successful and ₹300 available. |

[Recorded run](../06_Test_Reports/All_Test_Run.txt) · [Commands](../05_Test_Automation/README.md)
