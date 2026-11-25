"""Check discoverability and local contracts without rewriting upstream skills."""

import argparse
import json
import re
from pathlib import Path
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


def check(root=ROOT):
    errors = []
    skills = root / ".agents/skills"
    catalog = json.loads((root / ".agents/skill-contracts.json").read_text())
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
            metadata = yaml.safe_load(match[1])
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
                data = json.loads(provenance.read_text())
                commit = data.get("resolved_commit")
                if commit is not None and not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
                    raise ValueError("Invalid resolved_commit")
                if not isinstance(data.get("repository"), str) or not data[
                    "repository"
                ].startswith("https://github.com/"):
                    raise ValueError("Invalid provenance repository")
                for doc in upstreams:
                    if doc.exists() and commit:
                        stated = re.findall(r"`([0-9a-fA-F]{40})`", doc.read_text())
                        if stated and commit not in stated:
                            errors.append(
                                f"{doc}: source snapshot differs from INSTALL_SOURCE.json; review adaptation history"
                            )
            except (ValueError, TypeError) as error:
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
