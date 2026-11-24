# Test design techniques

Refer to [Test Cases](Test_Cases.csv) for setup, input, steps, and expected output.

- **Equivalence partitioning** groups valid and invalid credentials in TC-01 and TC-02. TC-09 and TC-13 cover positive and zero transfer amounts. The unit suite also covers negative and fractional top-up inputs.
- **Boundary value analysis** uses one-rupee increments at the ₹10 and ₹5,000 top-up limits. TC-03 to TC-08 cover ₹9, ₹10, ₹11, ₹4,999, ₹5,000, and ₹5,001.
- **Decision table testing** covers all four combinations of recipient validity and sufficient funds.
- **State transition testing** observes the Pending payment in TC-14 and exercises each supported transition in TC-15 and TC-16.
- **Functional testing** checks the order and contents of transaction history in TC-17.

## Transfer decision table

Alice starts with ₹500. Each row uses a positive integer amount.

| Case | Recipient | Amount | Other wallet exists | Funds sufficient | Action |
|---|---|---:|---|---|---|
| TC-09 | bob | ₹200 | Yes | Yes | Debit Alice, credit Bob, and show the reference in Bob's history. |
| TC-10 | bob | ₹501 | Yes | No | Show insufficient balance. Alice's balance and history stay unchanged. |
| TC-11 | unknown | ₹200 | No | Yes | Show recipient error. Alice's balance and history stay unchanged. |
| TC-12 | unknown | ₹501 | No | No | Show recipient error because that rule runs first. Alice's balance and history stay unchanged. |

## Payment transitions

| Case | Action | Observable status | Available balance |
|---|---|---|---:|
| TC-14 | Start a ₹200 payment | Pending | ₹300 |
| TC-15 | Complete the pending ₹200 payment | Successful | ₹300 |
| TC-16 | Fail the pending ₹200 payment | Failed | ₹500 |
