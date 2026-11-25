"""Check discoverability and local contracts without rewriting upstream skills."""

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FIELDS = (
    "when_to_use",
    "preconditions",
    "workflow",
    "validation",
    "deliverables",
)


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects ambiguous duplicate mapping keys."""


def _construct_unique_mapping(loader, node, deep=False):
    # Check keys before SafeLoader flattens YAML merge keys. Explicit values
    # may override merged defaults, but duplicate keys in the authored mapping
    # itself are almost certainly an authoring error.
    seen = set()
    for key_node, _value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            continue
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError:
            # Let SafeLoader raise its normal error for an unhashable key.
            continue
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json_object(path):
    """Load a JSON object and reject duplicate keys or unexpected top-level types."""
    try:
        value = json.loads(path.read_text(), object_pairs_hook=_unique_json_object)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def check(root=ROOT):
    errors = []
    skills = root / ".agents/skills"
    catalog_path = root / ".agents/skill-contracts.json"
    try:
        catalog = _load_json_object(catalog_path)
    except (OSError, ValueError) as error:
        errors.append(f"{catalog_path}: {error}")
        catalog = {}

    names = set()
    entries = sorted(skills.glob("*/SKILL.md"))
    if not entries:
        errors.append("No skills discovered")
    index = (root / ".agents/README.md").read_text()
    indexed = re.findall(r"\]\(skills/([^/]+)/SKILL\.md\)", index)
    for entry in entries:
        try:
            text = entry.read_text()
            match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
            if not match:
                raise ValueError("Missing frontmatter")
            metadata = yaml.load(match[1], Loader=_UniqueKeyLoader)
            if not isinstance(metadata, dict):
                raise ValueError("Frontmatter must be a mapping")
            name = metadata.get("name")
            if not isinstance(name, str) or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", name
            ):
                raise ValueError("Invalid name")
            if name != entry.parent.name or name in names:
                raise ValueError("Name must match directory and be unique")
            names.add(name)
            description = metadata.get("description")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("Missing description")
            contract = catalog.get(name)
            if not isinstance(contract, dict):
                raise ValueError("Missing local contract")
            for field in CONTRACT_FIELDS:
                if (
                    not isinstance(contract.get(field), str)
                    or not contract[field].strip()
                ):
                    raise ValueError(f"Missing contract section: {field}")
        except (ValueError, yaml.YAMLError) as error:
            errors.append(f"{entry}: {error}")
    for entry in entries:
        provenance = entry.parent / "INSTALL_SOURCE.json"
        upstreams = [
            entry.parent / "UPSTREAM.md",
            entry.parent / "references/UPSTREAM.md",
        ]
        if provenance.exists():
            try:
                data = _load_json_object(provenance)
                repository = data.get("repository")
                parsed_repository = (
                    urlsplit(repository) if isinstance(repository, str) else None
                )
                repository_parts = (
                    [part for part in parsed_repository.path.split("/") if part]
                    if parsed_repository
                    else []
                )
                if (
                    parsed_repository is None
                    or parsed_repository.scheme != "https"
                    or parsed_repository.netloc != "github.com"
                    or len(repository_parts) != 2
                ):
                    raise ValueError("Invalid provenance repository")
                source_path = data.get("path")
                normalized_path = (
                    PurePosixPath(source_path)
                    if isinstance(source_path, str)
                    else None
                )
                if (
                    normalized_path is None
                    or not source_path.strip()
                    or "\\" in source_path
                    or normalized_path.is_absolute()
                    or ".." in normalized_path.parts
                ):
                    raise ValueError("Invalid provenance path")
                requested_ref = data.get("requested_ref")
                if not isinstance(requested_ref, str) or not requested_ref.strip():
                    raise ValueError("Invalid requested_ref")
                if "resolved_commit" not in data:
                    raise ValueError("Missing resolved_commit")
                commit = data["resolved_commit"]
                if commit is not None and (
                    not isinstance(commit, str)
                    or not re.fullmatch(r"[0-9a-fA-F]{40}", commit)
                ):
                    raise ValueError("Invalid resolved_commit")
                for doc in upstreams:
                    if doc.exists() and commit:
                        stated = re.findall(r"`([0-9a-fA-F]{40})`", doc.read_text())
                        if stated and commit not in stated:
                            errors.append(
                                f"{doc}: source snapshot differs from INSTALL_SOURCE.json; review adaptation history"
                            )
            except (OSError, ValueError, TypeError) as error:
                errors.append(f"{provenance}: {error}")
    if set(catalog) != names:
        errors.append("Sidecar catalog differs from discovered skills")
    if set(indexed) != names or len(indexed) != len(set(indexed)):
        errors.append("Skill index is incomplete or duplicated")
    for doc in skills.rglob("*.md"):
        text = doc.read_text()
        # Ignore fenced examples: example paths are not resource declarations.
        text = re.sub(r"(?ms)^(`{3,}|~{3,}).*?^\1\s*$", "", text)
        targets = re.findall(r"\]\(([^)\n]+)\)", text)
        targets += re.findall(r"^\[[^]]+\]:\s+(\S+)", text, re.M)
        for target in targets:
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            resource = (doc.parent / unquote(parsed.path)).resolve()
            if parsed.path.startswith((".claude/", ".codex/")) or any(
                part in (".claude", ".codex") for part in Path(parsed.path).parts
            ):
                errors.append(
                    f"{doc}: Shared skill links to client-private resource {target}"
                )
            if not resource.is_relative_to(root.resolve()) or not resource.exists():
                errors.append(f"{doc}: Missing or escaping resource {target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        errors = check()
    except (OSError, ValueError) as error:
        parser.exit(1, f"Skill check failed: {error}\n")
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print("Skill discovery, local contracts, resources and index passed.")


if __name__ == "__main__":
    main()
