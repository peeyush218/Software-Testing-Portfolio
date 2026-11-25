"""Run all baseline suites and the isolated defect exercise."""

from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    location = Path(__file__).resolve().parent
    suites = (
        ("Black-box desktop UI and seeded defect exercise", "run_ui_cases.py"),
        ("Existing wallet unit tests", "test_wallet.py"),
        ("White-box wallet decision tests", "test_white_box.py"),
        ("HTTP API tests", "test_api.py"),
    )
    failures = []
    for label, script in suites:
        print(f"\n{label}", flush=True)
        if subprocess.run([sys.executable, str(location / script)], check=False).returncode:
            failures.append(script)
    print(f"\nFailed suites: {', '.join(failures)}" if failures else "\nAll four suites completed successfully.")
    raise SystemExit(bool(failures))
