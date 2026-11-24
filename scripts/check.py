"""Check repository sources, or explicitly fix Python style before verifying."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_PATHS = ["scripts", "tests", ".agents/skills"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Check only (default)")
    modes.add_argument(
        "--fix",
        action="store_true",
        help="Apply safe Ruff fixes and format, then verify",
    )
    args = parser.parse_args(argv)
    checks = []
    if args.fix:
        checks.extend(
            [
                (
                    "fix-lint",
                    ["ruff", "check", "--fix", "--no-unsafe-fixes", *PYTHON_PATHS],
                ),
                ("fix-format", ["ruff", "format", *PYTHON_PATHS]),
            ]
        )
    checks.extend(
        [
            ("lint", ["ruff", "check", "--no-fix", *PYTHON_PATHS]),
            ("format", ["ruff", "format", "--check", *PYTHON_PATHS]),
            (
                "tests",
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            ),
            ("shell", ["bash", ".agents/skills/shell-check/scripts/check.sh"]),
        ]
    )
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
