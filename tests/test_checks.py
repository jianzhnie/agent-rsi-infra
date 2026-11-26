"""Exercise check/fix behavior with local tools and a temporary source tree."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CheckFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        scripts = self.project / "scripts"
        scripts.mkdir()
        shutil.copyfile(ROOT / "scripts/check.py", scripts / "check.py")
        (scripts / "check_skills.py").write_text(
            "print('Skill verification completed')\n"
        )
        self.source = scripts / "example.py"
        self.source.write_text("value=1\n")
        tests = self.project / "tests"
        tests.mkdir()
        (tests / "test_behavior.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class Behavior(unittest.TestCase):\n"
            "    def test_source_is_formatted(self):\n"
            "        self.assertEqual(Path('scripts/example.py').read_text(), 'value = 1\\n')\n"
        )
        shell = self.project / ".agents/skills/shell-check/scripts/check.sh"
        shell.parent.mkdir(parents=True)
        shell.write_text("echo 'Shell verification completed'\n")
        self.bin = self.project / "bin"
        self.bin.mkdir()
        (self.bin / "bash").symlink_to(shutil.which("bash"))
        (self.bin / "shellcheck").write_text("#!/bin/sh\nexit 0\n")
        (self.bin / "shellcheck").chmod(0o755)
        self.ruff = self.bin / "ruff"
        self.ruff.write_text(
            f"#!{sys.executable}\n"
            "import os, sys\nfrom pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "with open('tool-log', 'a') as log: log.write(' '.join(args) + '\\n')\n"
            "source = Path('scripts/example.py')\n"
            "if '--fix' in args or (args[0] == 'format' and '--check' not in args):\n"
            "    source.write_text('value = 1\\n')\n"
            "if args[0] == 'check' and os.environ.get('UNFIXABLE'):\n"
            "    sys.exit(1)\n"
            "sys.exit(0 if source.read_text() == 'value = 1\\n' else 1)\n"
        )
        self.ruff.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.bin)}

    def run_checks(self, *args):
        return subprocess.run(
            [sys.executable, str(self.project / "scripts/check.py"), *args],
            cwd=self.project,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_default_and_explicit_checks_never_fix_source(self) -> None:
        for args in ((), ("--check",)):
            with self.subTest(args=args):
                result = self.run_checks(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(self.source.read_text(), "value=1\n")
                self.assertIn("Shell verification completed", result.stdout)
                self.assertNotIn("--fix", (self.project / "tool-log").read_text())

    def test_fix_writes_source_then_verifies_behavior(self) -> None:
        result = self.run_checks("--fix")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.source.read_text(), "value = 1\n")
        self.assertIn("1 passed", result.stdout)
        self.assertIn("Shell verification completed", result.stdout)
        commands = [
            line
            for line in (self.project / "tool-log").read_text().splitlines()
            if line != "--version"
        ]
        self.assertIn("--no-unsafe-fixes", commands[0])
        self.assertTrue(any("--no-fix" in command for command in commands[1:]))

    def test_unfixed_error_still_runs_verification_and_fails(self) -> None:
        self.env["UNFIXABLE"] = "1"
        result = self.run_checks("--fix")
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 passed", result.stdout)
        self.assertIn("Shell verification completed", result.stdout)
        self.assertIn("Failed checks:", result.stderr)

    def test_missing_tool_does_not_report_success_or_stop_other_checks(self) -> None:
        self.ruff.unlink()
        result = self.run_checks()
        self.assertEqual(result.returncode, 1)
        self.assertIn("BLOCKED lint:", result.stderr)
        self.assertIn("Shell verification completed", result.stdout)

    def test_failed_shell_check_returns_failure_after_python_checks(self) -> None:
        self.source.write_text("value = 1\n")
        shell = self.project / ".agents/skills/shell-check/scripts/check.sh"
        shell.write_text("exit 7\n")
        result = self.run_checks("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 passed", result.stdout)
        self.assertIn("Failed checks: shell", result.stderr)

    def test_conflicting_modes_do_not_run_tools(self) -> None:
        result = self.run_checks("--check", "--fix")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.project / "tool-log").exists())
        self.assertEqual(self.source.read_text(), "value=1\n")

    def test_only_runs_selected_check_and_writes_json(self) -> None:
        result = self.run_checks("--only", "shell", "--json", "result.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Shell verification completed", result.stdout)
        self.assertNotIn("[lint]", result.stdout)
        payload = json.loads((self.project / "result.json").read_text())
        self.assertEqual([item["name"] for item in payload["results"]], ["shell"])
        self.assertEqual(payload["results"][0]["status"], "passed")

    def test_timeout_is_reported_as_failure(self) -> None:
        self.ruff.write_text("#!" + sys.executable + "\nimport time; time.sleep(1)\n")
        self.ruff.chmod(0o755)
        result = self.run_checks("--only", "lint", "--timeout", "0.01")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Timed out", result.stderr)

    def test_non_root_call_and_multiple_failures(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.project / "scripts/check.py"),
                "--only",
                "lint,format",
            ],
            cwd=self.project.parent,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Failed checks: lint, format", result.stderr)
        self.assertTrue((self.project / "tool-log").exists())

    def test_empty_selection_and_partial_fix_are_rejected(self) -> None:
        for args in (
            ("--only", ","),
            ("--fix", "--only", "lint"),
            ("--timeout", "nan"),
        ):
            self.assertEqual(self.run_checks(*args).returncode, 2)

    def test_formatter_versions_match_across_local_and_commit_checks(self) -> None:
        """A formatter upgrade must update every entrypoint to avoid conflicting rewrites."""
        project_configuration = (ROOT / "pyproject.toml").read_text()
        dependency_version = re.search(
            r'"ruff==([^"\n]+)"', project_configuration
        ).group(1)
        required_version = re.search(
            r'required-version = "==([^"\n]+)"', project_configuration
        ).group(1)
        hooks = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
        hook_revision = next(
            repository["rev"]
            for repository in hooks["repos"]
            if repository["repo"].endswith("/ruff-pre-commit")
        )
        self.assertEqual(dependency_version, required_version)
        self.assertEqual(hook_revision, f"v{dependency_version}")

    def test_missing_shellcheck_is_blocked(self) -> None:
        (self.bin / "shellcheck").unlink()
        result = self.run_checks("--only", "shell", "--json", "report.json")
        self.assertEqual(result.returncode, 1)
        payload = json.loads((self.project / "report.json").read_text())
        self.assertEqual(payload["results"][0]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
