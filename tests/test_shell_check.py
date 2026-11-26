"""Exercise Shell selection and failure aggregation without real static analysis."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/shell-check/scripts/check.sh"


class ShellCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project with spaces"
        self.project.mkdir()
        self.bin = Path(self.temp.name) / "bin"
        self.bin.mkdir()
        for name in ("bash", "git", "find", "mktemp", "rm"):
            executable = shutil.which(name)
            self.assertIsNotNone(executable, name)
            (self.bin / name).symlink_to(executable)
        self.capture = Path(self.temp.name) / "arguments"
        self.env = {**os.environ, "PATH": str(self.bin), "CAPTURE": str(self.capture)}
        self.mock = self.bin / "shellcheck"
        self.mock.write_text(
            '#!/bin/bash\nprintf "%s\\0" "$@" >> "$CAPTURE"\n'
            '[[ "$*" != *bad-static.sh* ]]\n'
        )
        self.mock.chmod(0o755)

    def run_check(self, *args, cwd=None):
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), *map(str, args)],
            cwd=cwd or self.project,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_repository_selection_from_subdirectory(self) -> None:
        subprocess.run(
            [str(self.bin / "git"), "init", "-q"], cwd=self.project, check=True
        )
        for name in ("tracked.sh", "new file.sh", "line\nbreak.sh", "ignored.sh"):
            (self.project / name).write_text("echo ok\n")
        (self.project / ".gitignore").write_text("ignored.sh\n")
        subprocess.run(
            [str(self.bin / "git"), "add", "tracked.sh"], cwd=self.project, check=True
        )
        nested = self.project / "nested"
        nested.mkdir()
        result = self.run_check(cwd=nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Files: 3;", result.stdout)
        arguments = self.capture.read_bytes().split(b"\0")
        self.assertIn(b"new file.sh", arguments)
        self.assertIn(b"line\nbreak.sh", arguments)
        self.assertNotIn(b"ignored.sh", arguments)

    def test_failures_do_not_stop_later_files(self) -> None:
        (self.project / "bad-static.sh").write_text("echo ok\n")
        (self.project / "bad-syntax.sh").write_text("if\n")
        (self.project / "valid.sh").write_text("echo ok\n")
        result = self.run_check(self.project)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(
            "Files: 3; syntax failures: 1; shellcheck failures: 1;", result.stdout
        )
        self.assertIn(b"valid.sh", self.capture.read_bytes())

    def test_missing_shellcheck_is_not_success(self) -> None:
        self.mock.unlink()
        (self.project / "valid.sh").write_text("echo ok\n")
        result = self.run_check(self.project / "valid.sh")
        self.assertEqual(result.returncode, 1)
        self.assertIn("PASS syntax", result.stdout)
        self.assertIn("shellcheck skipped: 1", result.stdout)
        self.assertIn("SKIPPED shellcheck", result.stderr)

    @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck is not installed")
    def test_follows_local_sourced_library(self) -> None:
        executable = shutil.which("shellcheck")
        self.mock.unlink()
        self.mock.symlink_to(executable)
        (self.project / "helper.bash").write_text(
            '#!/bin/bash\nhello() { printf "%s\\n" "hello"; }\n'
        )
        target = self.project / "main.sh"
        target.write_text("#!/bin/bash\nsource ./helper.bash\nhello\n")
        result = self.run_check(target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS shellcheck", result.stdout)

    def test_invalid_or_empty_target_is_not_success(self) -> None:
        for target in (self.project / "missing", self.project):
            with self.subTest(target=target):
                result = self.run_check(target)
                self.assertEqual(result.returncode, 2)

    def test_default_requires_repository(self) -> None:
        result = self.run_check()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Not in a Git repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
