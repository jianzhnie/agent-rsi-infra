"""Check deployment paths and index coverage without starting external services."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".claude"


class LayoutTests(unittest.TestCase):
    def test_registered_runtime_paths_exist(self):
        settings = json.loads((AGENT / "settings.example.json").read_text())
        commands = [
            hook["command"]
            for groups in settings["hooks"].values()
            for group in groups
            for hook in group["hooks"]
        ] + [settings["statusLine"]["command"]]
        registered = set()
        for command in commands:
            self.assertTrue(command.startswith('"${CLAUDE_PROJECT_DIR}/.claude/'))
            self.assertTrue(command.endswith('"'))
            path = command.removeprefix('"${CLAUDE_PROJECT_DIR}/.claude/').removesuffix(
                '"'
            )
            self.assertTrue((AGENT / path).is_file(), path)
            registered.add(path)
        expected = {
            str(path.relative_to(AGENT))
            for path in (AGENT / "hooks").rglob("*.sh")
            if path.name != "common.sh"
        } | {"scripts/status-line.sh"}
        self.assertEqual(registered, expected)

    def test_index_covers_all_configuration_entries(self):
        text = (ROOT / ".agents/README.md").read_text()
        # Index tables contain one local file link per configuration entry.
        links = [
            target
            for line in text.splitlines()
            if line.startswith("| ")
            for target in re.findall(r"\]\(([^)]+)\)", line)
            if not target.startswith("https://")
        ]
        self.assertEqual(len(links), len(set(links)))
        expected = {
            "../.claude/settings.example.json",
            "../.claude/scripts/status-line.sh",
        }
        for folder in ("agents",):
            expected.update(
                str(p.relative_to(ROOT / ".agents"))
                for p in (ROOT / ".agents" / folder).glob("*.md")
            )
        expected.update(
            "skills/" + str(p.relative_to(ROOT / ".agents/skills"))
            for p in (ROOT / ".agents/skills").glob("*/SKILL.md")
        )
        expected.update(
            "../.claude/" + str(p.relative_to(AGENT))
            for p in (AGENT / "hooks").rglob("*.sh")
            if p.name != "common.sh"
        )
        self.assertEqual(set(links), expected)

    def test_agent_adapters_match_shared_definitions(self):
        from scripts.sync_agents import render

        outputs = render()
        self.assertTrue(outputs)
        self.assertFalse((AGENT / "agents").is_symlink())
        for path, content in outputs.items():
            self.assertEqual(path.read_text(), content, str(path))
        sources = {p.stem for p in (ROOT / ".agents/agents").glob("*.md")}
        self.assertEqual(sources, {p.stem for p in (AGENT / "agents").glob("*.md")})
        self.assertEqual(
            sources, {p.stem for p in (ROOT / ".codex/agents").glob("*.toml")}
        )

    def test_role_description_with_colon_remains_yaml_string(self):
        import tempfile

        from scripts.sync_agents import render

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".agents/agents/debugger.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                '---\nname: debugger\ndescription: Inspect: "failure"\n---\n\nDebug.\n'
            )
            outputs = render(root)
            adapter = outputs[root / ".claude/agents/debugger.md"]
            value = re.search(r"^description: (.+)$", adapter, re.M).group(1)
            self.assertEqual(json.loads(value), 'Inspect: "failure"')
            source.write_text("---\nname: debugger\n---\nDebug.\n")
            with self.assertRaisesRegex(ValueError, "Missing role"):
                render(root)

    def test_shared_skills_resolve_to_single_source(self):
        self.assertEqual((AGENT / "skills").resolve(), ROOT / ".agents/skills")
        for skill in (ROOT / ".agents/skills").rglob("*"):
            if not skill.is_file():
                continue
            self.assertTrue(
                (
                    AGENT / "skills" / skill.relative_to(ROOT / ".agents/skills")
                ).samefile(skill)
            )

    def test_client_instruction_imports_resolve(self):
        for name in ("CLAUDE.md", "GEMINI.md"):
            entry = ROOT / name
            imports = re.findall(r"^@(.+)$", entry.read_text(), re.M)
            self.assertTrue(imports, name)
            for target in imports:
                self.assertTrue((entry.parent / target).is_file(), (name, target))

    def test_local_document_links_resolve(self):
        for doc in [
            ROOT / "README.md",
            ROOT / ".agents/README.md",
            *sorted((ROOT / ".agents/agents").glob("*.md")),
            ROOT / "AGENTS.md",
            ROOT / "CONTRIBUTING.md",
            *sorted((ROOT / ".agents/skills").rglob("*.md")),
            *sorted((ROOT / "docs").glob("*.md")),
        ]:
            for target in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
                if target.startswith(("https://", "http://", "#")):
                    continue
                self.assertTrue(
                    (doc.parent / target.split("#")[0]).is_file(), (doc, target)
                )


if __name__ == "__main__":
    unittest.main()
