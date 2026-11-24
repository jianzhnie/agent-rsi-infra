"""Run the same non-mutating repository checks locally and in CI."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks = [
        ("lint", ["ruff", "check", "scripts", "tests"]),
        ("format", ["ruff", "format", "--check", "scripts", "tests"]),
        ("tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        (
            "shell",
            ["bash", ".agents/skills/shell-check/scripts/check.sh"],
        ),
    ]
    failures = []
    for name, command in checks:
        print(f"\n[{name}] {' '.join(command)}", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, check=False)
        except OSError as error:
            print(f"FAIL {name}: {error}", file=sys.stderr)
            failures.append(name)
            continue
        if result.returncode:
            failures.append(name)
    if failures:
        print(f"\nFailed checks: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("\nAll repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
