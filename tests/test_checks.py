"""Exercise check/fix behavior with local tools and a temporary source tree."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CheckFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        scripts = self.project / "scripts"
        scripts.mkdir()
        shutil.copyfile(ROOT / "scripts/check.py", scripts / "check.py")
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

    def test_default_and_explicit_checks_never_fix_source(self):
        for args in ((), ("--check",)):
            with self.subTest(args=args):
                result = self.run_checks(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(self.source.read_text(), "value=1\n")
                self.assertIn("Shell verification completed", result.stdout)
                self.assertNotIn("--fix", (self.project / "tool-log").read_text())

    def test_fix_writes_source_then_verifies_behavior(self):
        result = self.run_checks("--fix")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.source.read_text(), "value = 1\n")
        self.assertIn("1 passed", result.stdout)
        self.assertIn("Shell verification completed", result.stdout)
        commands = (self.project / "tool-log").read_text().splitlines()
        self.assertIn("--no-unsafe-fixes", commands[0])
        self.assertTrue(any("--no-fix" in command for command in commands[1:]))

    def test_unfixed_error_still_runs_verification_and_fails(self):
        self.env["UNFIXABLE"] = "1"
        result = self.run_checks("--fix")
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 passed", result.stdout)
        self.assertIn("Shell verification completed", result.stdout)
        self.assertIn("Failed checks:", result.stderr)

    def test_missing_tool_does_not_report_success_or_stop_other_checks(self):
        self.ruff.unlink()
        result = self.run_checks()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL lint:", result.stderr)
        self.assertIn("Shell verification completed", result.stdout)

    def test_conflicting_modes_do_not_run_tools(self):
        result = self.run_checks("--check", "--fix")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.project / "tool-log").exists())
        self.assertEqual(self.source.read_text(), "value=1\n")


if __name__ == "__main__":
    unittest.main()
