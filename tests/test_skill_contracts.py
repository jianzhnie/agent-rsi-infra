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


def test_upstream_extensions_and_sidecar_are_supported(tmp_path) -> None:
    fixture(tmp_path)
    assert check(tmp_path) == []


@pytest.mark.parametrize("fault", ["resource", "section", "index", "yaml"])
def test_invalid_skill_resources_or_contracts_are_reported(tmp_path, fault) -> None:
    folder = fixture(tmp_path)
    if fault == "resource":
        (folder / "detail.md").unlink()
    elif fault == "section":
        p = tmp_path / ".agents/skill-contracts.json"
        data = json.loads(p.read_text())
        data["example"].pop("validation")
        p.write_text(json.dumps(data))
    elif fault == "index":
        (tmp_path / ".agents/README.md").write_text("")
    else:
        (folder / "SKILL.md").write_text("---\nname: [broken\n---\n")
    assert check(tmp_path)


def test_duplicate_frontmatter_keys_are_rejected(tmp_path) -> None:
    folder = fixture(tmp_path)
    (folder / "SKILL.md").write_text(
        "---\nname: example\nname: shadow\ndescription: Example skill.\n---\n"
    )

    errors = check(tmp_path)

    assert any("duplicate key 'name'" in error for error in errors)


def test_duplicate_nested_frontmatter_keys_are_rejected(tmp_path) -> None:
    folder = fixture(tmp_path)
    (folder / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example skill.\n"
        "vendor_extension:\n  nested:\n    enabled: true\n    enabled: false\n"
        "---\n"
    )

    errors = check(tmp_path)

    assert any("duplicate key 'enabled'" in error for error in errors)


def test_yaml_merge_key_can_be_overridden_explicitly(tmp_path) -> None:
    folder = fixture(tmp_path)
    (folder / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example skill.\n"
        "defaults: &defaults\n  nested: {enabled: true}\n"
        "vendor_extension:\n  <<: *defaults\n  nested: {enabled: false}\n"
        "---\n"
    )

    assert check(tmp_path) == []


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("[]", "Expected a JSON object"),
        ('{"example": {}, "example": {}}', "Duplicate JSON key"),
    ],
)
def test_sidecar_catalog_rejects_invalid_json_objects(
    tmp_path, content, expected
) -> None:
    fixture(tmp_path)
    (tmp_path / ".agents/skill-contracts.json").write_text(content)

    errors = check(tmp_path)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ("[]", "Expected a JSON object"),
        (
            '{"repository": "https://github.com/example/repo"}',
            "Invalid provenance path",
        ),
        (
            json.dumps(
                {
                    "repository": "https://github.com/example/repo",
                    "path": "../outside",
                    "requested_ref": "main",
                    "resolved_commit": None,
                }
            ),
            "Invalid provenance path",
        ),
        (
            json.dumps(
                {
                    "repository": "https://github.com/example/repo",
                    "path": "skills/example",
                    "requested_ref": "main",
                }
            ),
            "Missing resolved_commit",
        ),
        (
            '{"repository": "https://github.com/example/repo", '
            '"path": "skills/example", "requested_ref": "main", '
            '"requested_ref": "shadow", "resolved_commit": null}',
            "Duplicate JSON key",
        ),
    ],
)
def test_install_source_requires_valid_snapshot_shape(
    tmp_path, metadata, expected
) -> None:
    folder = fixture(tmp_path)
    (folder / "INSTALL_SOURCE.json").write_text(metadata)

    errors = check(tmp_path)

    assert any(expected in error for error in errors)
