"""Validate local Markdown links, lightweight skill metadata and source notices."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def link_errors(root, skip_templates=False):
    errors = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if ".git" in path.parts or (skip_templates and rel.startswith("templates/")):
            continue
        body = path.read_text()
        for line in body.splitlines():
            if line.rstrip() != line:
                errors.append(rel + ": trailing whitespace")
        for dest in re.findall(r"\]\(([^)]+)\)", body):
            if "://" in dest or dest.startswith(("#", "mailto:")):
                continue
            dest = dest.split("#")[0].strip("<>")
            if dest and not (path.parent / dest).exists():
                errors.append(rel + ": missing local link " + dest)
    return errors


def check(root=ROOT):
    errors = link_errors(root, skip_templates=True)
    required = ["README.md", "AGENTS.md", "INSTALL.md", "scripts/install.py", "SETUP.md", "LICENSE", "THIRD_PARTY.md", "docs/design.md", "docs/review.md", "templates/project.example.json", ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/bug.yml", ".github/ISSUE_TEMPLATE/feature.yml"]
    errors.extend("missing " + name for name in required if not (root / name).is_file())
    for p in (root / "skills").glob("*/SKILL.md"):
        body = p.read_text()
        if not body.startswith("---\n") or body.count("---\n") < 2:
            errors.append(str(p.relative_to(root)) + ": missing frontmatter")
            continue
        header = body.split("---\n", 2)[1]
        if not re.search(r"^name: .+", header, re.M) or not re.search(r"^description: .+", header, re.M):
            errors.append(str(p.relative_to(root)) + ": name/description required")
        if len(body.splitlines()) > 35:
            errors.append(str(p.relative_to(root)) + ": entrypoint exceeds 35 lines")
    provenance = json.loads((root / "provenance.json").read_text())
    for item in provenance["sources"]:
        if item.get("snapshot"):
            p = root / "skills" / item["skill"] / item["snapshot"]
            if hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]:
                errors.append("custom skill snapshot drift: " + item["skill"])
    for name in ["bug", "feature"]:
        body = (root / ".github/ISSUE_TEMPLATE" / (name + ".yml")).read_text()
        ids = re.findall(r"^    id: (.+)$", body, re.M)
        if len(ids) != len(set(ids)) or not {"problem", "done", "owner"} <= set(ids):
            errors.append("issue form IDs invalid: " + name)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = check()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: local links, required assets, short skill entrypoints, customised-skill hashes and issue form IDs.")
    print("YAML host parsing, actual skill discovery and model/provider behavior are separate checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
