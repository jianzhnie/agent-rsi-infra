"""Run repository checks, or explicitly fix Python style before verifying."""

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
PYTHON_PATHS = ["scripts", "tests", ".agents/skills", "autotuner", "rsi_bench"]
DEFAULT_TIMEOUT = 300.0


@dataclass
class CheckResult:
    name: str
    status: Literal["passed", "failed", "blocked", "skipped"]
    return_code: int | None = None
    duration_seconds: float | None = None
    message: str | None = None


def _commands(fix: bool) -> list[tuple[str, list[str]]]:
    checks = []
    if fix:
        checks += [
            (
                "fix-lint",
                ["ruff", "check", "--fix", "--no-unsafe-fixes", *PYTHON_PATHS],
            ),
            ("fix-format", ["ruff", "format", *PYTHON_PATHS]),
        ]
    return checks + [
        ("lint", ["ruff", "check", "--no-fix", *PYTHON_PATHS]),
        ("format", ["ruff", "format", "--check", *PYTHON_PATHS]),
        ("skills", [sys.executable, "scripts/check_skills.py"]),
        (
            "tests",
            [
                sys.executable,
                "-m",
                "pytest",
                "tests",
                "-q",
            ],
        ),
        ("shell", ["bash", ".agents/skills/shell-check/scripts/check.sh"]),
    ]


def run_check(name: str, command: list[str], timeout_seconds: float) -> CheckResult:
    executable = command[0]
    missing = (
        [executable]
        if executable != sys.executable and shutil.which(executable) is None
        else []
    )
    modules = {"tests": "pytest", "skills": "yaml"}
    module = modules.get(name)
    if module and importlib.util.find_spec(module) is None:
        missing.append(f"Python module {module}")
    if name == "shell" and shutil.which("shellcheck") is None:
        missing.append("shellcheck")
    if missing:
        return CheckResult(
            name, "blocked", message=f"Missing command: {', '.join(missing)}"
        )
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, check=False, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return CheckResult(
            name,
            "failed",
            None,
            time.monotonic() - started,
            f"Timed out after {timeout_seconds:g}s",
        )
    except OSError as error:
        return CheckResult(
            name, "blocked", None, time.monotonic() - started, str(error)
        )
    return CheckResult(
        name,
        "passed" if result.returncode == 0 else "failed",
        result.returncode,
        time.monotonic() - started,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Check only (default)")
    modes.add_argument(
        "--fix", action="store_true", help="Apply safe Ruff fixes, then verify"
    )
    parser.add_argument("--only", help="Comma-separated checks to run")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Per-check timeout in seconds",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="Write structured results to this path",
    )
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be positive")
    checks = _commands(args.fix)
    if args.only is not None:
        selected = {item.strip() for item in args.only.split(",") if item.strip()}
        if not selected:
            parser.error("--only must select at least one check")
        if args.fix:
            parser.error("--fix requires full verification; cannot combine with --only")
        known = {name for name, _ in checks}
        unknown = selected - known
        if unknown:
            parser.error(f"Unknown checks: {', '.join(sorted(unknown))}")
        checks = [(name, command) for name, command in checks if name in selected]
    context = {
        "cwd": str(ROOT),
        "python": sys.executable,
        "timeout_seconds": args.timeout,
        "commands": [{"name": name, "command": command} for name, command in checks],
    }
    context["python_version"] = sys.version
    context["tools"] = {}
    for tool in ("ruff", "bash", "shellcheck"):
        executable = shutil.which(tool)
        info = {"path": executable, "version": None}
        if executable:
            try:
                probe = subprocess.run(
                    [executable, "--version"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=min(args.timeout, 5),
                    check=False,
                )
                info["version"] = (
                    (probe.stdout or probe.stderr).splitlines()[0]
                    if (probe.stdout or probe.stderr)
                    else None
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
        context["tools"][tool] = info
    print(f"Repository: {ROOT}\nPython: {sys.executable}", flush=True)
    results = []
    for name, command in checks:
        print(f"\n[{name}] {' '.join(command)}", flush=True)
        result = run_check(name, command, args.timeout)
        results.append(result)
        if result.status in ("failed", "blocked"):
            print(
                f"{result.status.upper()} {name}: {result.message or 'command failed'}",
                file=sys.stderr,
            )
    payload = {
        "version": 1,
        "context": context,
        "results": [asdict(item) for item in results],
    }
    if args.json_path:
        try:
            args.json_path.write_text(json.dumps(payload, indent=2) + "\n")
        except OSError as error:
            print(f"Cannot write report: {error}", file=sys.stderr)
            return 1
    failures = [item.name for item in results if item.status in ("failed", "blocked")]
    if failures:
        print(f"\nFailed checks: {', '.join(failures)}", file=sys.stderr)
        return 1
    print(
        "\n"
        + (
            "Selected checks passed."
            if args.only is not None
            else "All repository checks passed."
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
