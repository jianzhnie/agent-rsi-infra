"""Verify the discovery names of the remaining local skills."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"


class SkillResourcesTests(unittest.TestCase):
    def test_skill_names_match_discovery_directories(self):
        names = []
        entries = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertTrue(entries, "No shared skills were discovered")
        for entry in entries:
            header = entry.read_text().split("---", 2)[1]
            name = re.search(r"^name: (.+)$", header, re.M).group(1).strip()
            self.assertEqual(name, entry.parent.name)
            names.append(name)
        self.assertEqual(len(names), len(set(names)))

    def test_related_skills_exist(self):
        available = {entry.parent.name for entry in SKILLS.glob("*/SKILL.md")}
        entries = [
            *SKILLS.glob("*/SKILL.md"),
            *(ROOT / ".claude/agents").glob("*.md"),
        ]
        for entry in entries:
            match = re.search(r"^  related_skills: \[(.*?)\]$", entry.read_text(), re.M)
            if match:
                for name in filter(None, map(str.strip, match[1].split(","))):
                    self.assertIn(name, available, (entry, name))


if __name__ == "__main__":
    unittest.main()
