# GitHub submission and viva guide

## Prepare the submission

1. Extract the ZIP. Open the `Software-Testing-Portfolio` folder and make sure it contains `README.md` and `app`.
2. The README already contains both team members and roll numbers. If you have already run the wallet on your laptop, proceed to publishing.

## Publish to GitHub

1. Sign in to GitHub and create an empty repository named `Software-Testing-Portfolio`. Leave the README, license, and gitignore initialization options off. Choose the visibility required by your class. If your class allows private submission, you can give your faculty access through the repository settings.
2. On the empty repository page, click **uploading an existing file**. For each later batch, use **Add file → Upload files** from the repository's main page.
3. Open the extracted `Software-Testing-Portfolio` folder in File Explorer. Drag the listed items from inside that folder to GitHub, one batch at a time. Paste the matching message and click **Commit changes** after each batch. If prompted, commit directly to the main branch.

| Batch | Items to drag | Commit message |
|---|---|---|
| 1 | `README.md`, `app`, and `.gitignore` if visible | Add wallet demo and portfolio overview |
| 2 | `01_Test_Plan`, `02_Test_Case_Design`, `05_Test_Automation` | Add test plan cases and automation |
| 3 | `03_Test_Execution`, `04_Defect_Reports`, `06_Test_Reports`, `07_Screenshots`, `Conclusion.md`, `SUBMISSION_GUIDE.md` | Record test outcomes and defect exercise |

4. On the repository's main page, verify that the README displays both team members. Open the test summary and one screenshot to check that the folders uploaded correctly. Copy the repository URL for submission.

## Demonstrate the portfolio

1. Open the repository and explain its five modules and the simulated data.
2. Open the test cases. Explain why ₹9, ₹10, and ₹11 test the lower top-up limit.
3. Launch a fresh wallet, sign in as Alice, and send ₹200 to Bob. Show Alice's ₹300 balance, then sign in as Bob and show his ₹300 and the received transfer.
4. Relaunch the app, sign in as Alice, start a ₹200 payment, select its history row, and click **Fail selected payment**. Show the returned ₹500 and compare it with the deliberately faulty drill screenshot where the balance stayed ₹300.
5. Run the unit tests and open the summary. Describe the recorded 17 UI passes, six unit passes, and one expected failure in the seeded exercise.

If asked why the drill failed, explain that the test ran a variant intentionally configured to leave funds deducted, so the team could practice capturing, reporting, and comparing a reproducible defect. The production behavior is outside this demo's scope.
