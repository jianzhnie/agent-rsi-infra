"""Local skill contracts detect drift without normalizing upstream metadata."""

import json

import pytest

from scripts.check_skills import CONTRACT_FIELDS, check


def fixture(root):
    folder = root / ".agents/skills/example"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        '---\nname: example\ndescription: "Use: example task"\n'
        "vendor_extension: {custom: true}\n---\n# Example\n[detail](detail.md)\n"
    )
    (folder / "detail.md").write_text("Task details\n")
    (root / ".agents/README.md").write_text("[example](skills/example/SKILL.md)\n")
    (root / ".agents/skill-contracts.json").write_text(
        json.dumps({"example": dict.fromkeys(CONTRACT_FIELDS, "Local policy")})
    )
    return folder


def test_upstream_extensions_and_sidecar_are_supported(tmp_path):
    fixture(tmp_path)
    assert check(tmp_path) == []


@pytest.mark.parametrize("fault", ["resource", "section", "index", "yaml"])
def test_invalid_skill_resources_or_contracts_are_reported(tmp_path, fault):
    folder = fixture(tmp_path)
    if fault == "resource":
        (folder / "detail.md").unlink()
    elif fault == "section":
        p = tmp_path / ".agents/skill-contracts.json"
        data = json.loads(p.read_text())
        del data["example"]["validation"]
        p.write_text(json.dumps(data))
    elif fault == "index":
        (tmp_path / ".agents/README.md").write_text("")
    else:
        (folder / "SKILL.md").write_text("---\nname: [broken\n---\n")
    assert check(tmp_path)
