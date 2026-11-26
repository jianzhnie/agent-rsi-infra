"""Exercise recipe guide extraction with valid Markdown code fences."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/model-recipes/scripts/read_recipe.sh"
)


class RecipeTests(unittest.TestCase):
    def test_nested_fences_preserve_section_and_exclude_following_section(self) -> None:
        for fence in ("````", "~~~~"):
            with self.subTest(fence=fence), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "recipe.json"
                section = (
                    "## Prerequisites\nBefore.\n"
                    f"{fence}markdown\n```python\n## Not a section\n```\n"
                    f"{fence}\nAfter.\n"
                )
                path.write_text(
                    json.dumps({"guide": section + "## Troubleshooting\nOther.\n"})
                )
                result = subprocess.run(
                    ["bash", str(SCRIPT), str(path), "prerequisites"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(result.stdout, section)
