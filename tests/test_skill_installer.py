"""Exercise complete skill imports using local fixtures, never GitHub services."""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/install-skill-from-github/scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    spec = importlib.util.spec_from_file_location(
        "repository_skill_installer", SCRIPTS / "install-skill-from-github.py"
    )
    installer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = installer
    spec.loader.exec_module(installer)
finally:
    sys.path.pop(0)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "source"
        self.repo.mkdir()
        self.dest = self.base / "destination with spaces"
        (self.repo / "LICENSE").write_text("Fixture license\n")
        (self.repo / "NOTICE").write_text("Fixture attribution\n")
        self.source_skill("one")
        self.source_skill("two")

    def source_skill(self, name):
        folder = self.repo / "skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test fixture.\n---\nUse references/detail.txt.\n"
        )
        (folder / "references").mkdir()
        (folder / "references/detail.txt").write_text("Resource\n")
        return folder

    def install(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with (
            patch.object(
                installer, "_prepare_repo", return_value=str(self.repo)
            ) as prepare,
            patch.object(installer, "_tmp_root", return_value=str(self.base)),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(error),
        ):
            status = installer.main([*args, "--dest", str(self.dest)])
        return status, output.getvalue(), error.getvalue(), prepare

    def test_default_destination_is_repository_collection(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "global")}):
            self.assertEqual(Path(installer._default_dest()), ROOT / ".agents/skills")

    def test_blob_link_preserves_resources_and_notices(self):
        status, output, error, _ = self.install(
            "--url", "https://github.com/example/repo/blob/main/skills/one/SKILL.md"
        )
        self.assertEqual(status, 0, error)
        target = self.dest / "one"
        self.assertEqual(
            (target / "SKILL.md").read_bytes(),
            (self.repo / "skills/one/SKILL.md").read_bytes(),
        )
        self.assertEqual((target / "references/detail.txt").read_text(), "Resource\n")
        self.assertEqual((target / "LICENSE").read_text(), "Fixture license\n")
        self.assertEqual((target / "NOTICE").read_text(), "Fixture attribution\n")
        source = json.loads((target / "INSTALL_SOURCE.json").read_text())
        self.assertEqual(source["path"], "skills/one")
        self.assertEqual(source["requested_ref"], "main")
        self.assertIsNone(source["resolved_commit"])
        self.assertIn("Installed one", output)

    def test_zip_install_handles_branch_names_without_network(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("snapshot/skills/one/SKILL.md", "Skill content\n")
            archive.writestr("snapshot/skills/one/references/detail.txt", "Resource\n")
            archive.writestr("snapshot/LICENSE", "Archive license\n")
        with (
            patch.object(
                installer, "_request", return_value=data.getvalue()
            ) as request,
            patch.object(installer, "_tmp_root", return_value=str(self.base)),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            status = installer.main(
                [
                    "--repo",
                    "example/repo",
                    "--path",
                    "skills/one",
                    "--ref",
                    "feature/typing",
                    "--dest",
                    str(self.dest),
                    "--method",
                    "download",
                ]
            )
        self.assertEqual(status, 0)
        self.assertIn("feature%2Ftyping", request.call_args.args[0])
        self.assertEqual((self.dest / "one/LICENSE").read_text(), "Archive license\n")
        metadata = json.loads((self.dest / "one/INSTALL_SOURCE.json").read_text())
        self.assertIsNone(metadata["resolved_commit"])

    def test_file_paths_and_commit_provenance(self):
        revision = "a" * 40
        status, _, error, _ = self.install(
            "--repo", "example/repo", "--path", "skills/one/SKILL.md", "--ref", revision
        )
        self.assertEqual(status, 0, error)
        source = json.loads((self.dest / "one/INSTALL_SOURCE.json").read_text())
        self.assertEqual(source["resolved_commit"], revision)

    def test_existing_destination_is_not_changed_or_downloaded(self):
        (self.dest / "one").mkdir(parents=True)
        sentinel = self.dest / "one/user-content"
        sentinel.write_text("keep")
        status, _, _, prepare = self.install(
            "--repo", "example/repo", "--path", "skills/one"
        )
        self.assertEqual(status, 1)
        prepare.assert_not_called()
        self.assertEqual(sentinel.read_text(), "keep")

    def test_broken_destination_symlink_is_not_replaced(self):
        self.dest.mkdir()
        target = self.dest / "one"
        target.symlink_to(self.base / "missing")
        status, _, _, prepare = self.install(
            "--repo", "example/repo", "--path", "skills/one"
        )
        self.assertEqual(status, 1)
        self.assertTrue(target.is_symlink())
        prepare.assert_not_called()

    def test_invalid_paths_and_duplicate_targets_fail_before_download(self):
        for paths in (
            ["../one"],
            ["skills/../one"],
            ["/absolute"],
            ["skills/one", "skills/one"],
        ):
            with self.subTest(paths=paths):
                status, _, _, prepare = self.install(
                    "--repo", "example/repo", "--path", *paths
                )
                self.assertEqual(status, 1)
                prepare.assert_not_called()

    def test_name_cannot_silently_rename_a_batch(self):
        status, _, _, prepare = self.install(
            "--repo",
            "example/repo",
            "--path",
            "skills/one",
            "skills/two",
            "--name",
            "alias",
        )
        self.assertEqual(status, 1)
        prepare.assert_not_called()

    def test_invalid_second_source_leaves_no_partial_install(self):
        (self.repo / "skills/two/SKILL.md").unlink()
        status, _, _, _ = self.install(
            "--repo", "example/repo", "--path", "skills/one", "skills/two"
        )
        self.assertEqual(status, 1)
        self.assertFalse((self.dest / "one").exists())

    def test_copy_failure_rolls_back_only_this_invocation(self):
        self.dest.mkdir()
        sentinel = self.dest / "existing"
        sentinel.write_text("keep")
        copytree = shutil.copytree

        def failing_copy(src, dest, *args, **kwargs):
            if Path(dest) == self.dest / "two":
                raise OSError("Simulated disk failure")
            return copytree(src, dest, *args, **kwargs)

        with patch.object(installer.shutil, "copytree", side_effect=failing_copy):
            status, _, error, _ = self.install(
                "--repo", "example/repo", "--path", "skills/one", "skills/two"
            )
        self.assertEqual(status, 1)
        self.assertIn("Simulated disk failure", error)
        self.assertFalse((self.dest / "one").exists())
        self.assertFalse((self.dest / "two").exists())
        self.assertEqual(sentinel.read_text(), "keep")

    def test_escaping_source_link_is_rejected(self):
        (self.repo / "skills/one/outside").symlink_to(self.base / "outside")
        status, _, _, _ = self.install("--repo", "example/repo", "--path", "skills/one")
        self.assertEqual(status, 1)
        self.assertFalse((self.dest / "one").exists())

    def test_zip_traversal_is_rejected_before_extraction(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("../escape", "untrusted")
        data.seek(0)
        with (
            zipfile.ZipFile(data) as archive,
            self.assertRaises(installer.InstallError),
        ):
            installer._safe_extract_zip(archive, str(self.base / "extract"))
        self.assertFalse((self.base / "escape").exists())

    def test_root_skill_does_not_copy_git_state(self):
        (self.repo / "SKILL.md").write_text("Root skill\n")
        (self.repo / ".git").mkdir()
        (self.repo / ".git/keep").write_text("private Git state")
        # This fixture is not a real Git checkout; its source revision stays unknown.
        with patch.object(installer.subprocess, "run") as run:
            run.return_value.returncode = 1
            status, _, error, _ = self.install(
                "--repo", "example/repo", "--path", "SKILL.md", "--name", "root-skill"
            )
        self.assertEqual(status, 0, error)
        self.assertFalse((self.dest / "root-skill/.git").exists())

    def test_git_can_fetch_an_older_commit(self):
        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(self.repo), *args], text=True
            ).strip()

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("add", ".")
        git("-c", "commit.gpgsign=false", "commit", "-qm", "first")
        old = git("rev-parse", "HEAD")
        (self.repo / "skills/one/SKILL.md").write_text("Changed\n")
        git("add", ".")
        git("-c", "commit.gpgsign=false", "commit", "-qm", "second")
        checkout = self.base / "checkout"
        checkout.mkdir()
        result = installer._git_sparse_checkout(
            self.repo.as_uri(), old, ["skills/one"], str(checkout)
        )
        content = Path(result, "skills/one/SKILL.md").read_text()
        self.assertIn("name: one", content)


if __name__ == "__main__":
    unittest.main()
