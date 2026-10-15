"""Read-only local SwarmStack status and installation health. No network or host actions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys

from configuration import normalise_config, validate

PROJECT_RECORDS = {".swarmstack/project.json", ".swarmstack/state.md", ".swarmstack/decisions.md"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def project_root(value):
    root = Path(os.path.abspath(value))
    if not root.is_dir() or any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("project must be an existing directory without symlink components")
    return root


def managed_name(name):
    if not isinstance(name, str) or not name or any(c in name for c in "\\:\x00"):
        raise ValueError("invalid managed path")
    if str(PurePosixPath(name)) != name or any(p in {".", ".."} for p in name.split("/")) or name.startswith("/"):
        raise ValueError("invalid managed path")
    if any(part.endswith(".") or part.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *["COM" + str(i) for i in range(1, 10)], *["LPT" + str(i) for i in range(1, 10)]} for part in name.split("/")):
        raise ValueError("ambiguous or reserved filesystem path")
    if name.casefold() in PROJECT_RECORDS and name not in PROJECT_RECORDS:
        raise ValueError("protected project record alias")
    if name in {"AGENTS.md", "docs/agents/issue-tracker.md", ".github/pull_request_template.md", ".swarmstack/local/.gitignore"}:
        return name
    if re.fullmatch(r"\.github/ISSUE_TEMPLATE/[A-Za-z0-9_.-]+\.yml", name):
        return name
    if re.fullmatch(r"\.agents/skills/[a-z0-9-]+/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+", name):
        return name
    if re.fullmatch(r"\.swarmstack/(?:[A-Za-z0-9_.-]+|(?:guides|scripts|licenses|templates)/[A-Za-z0-9_.-]+)", name):
        if name != ".swarmstack/lock.json":
            return name
    raise ValueError("path is outside managed toolkit outputs")


def safe_path(root, name):
    path = root / name
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("symlink in managed path: " + name)
    if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
        raise ValueError("managed path must be a regular unshared file: " + name)
    if any(p.exists() and not p.is_dir() for p in path.parents):
        raise ValueError("invalid managed parent: " + name)
    return path


def load_install(root):
    config = json.loads(safe_path(root, ".swarmstack/project.json").read_text(encoding="utf-8"))
    lock = json.loads(safe_path(root, ".swarmstack/lock.json").read_text(encoding="utf-8"))
    validate(normalise_config(config))
    if not isinstance(lock, dict) or lock.get("toolkit") != "SwarmStack" or not isinstance(lock.get("files"), dict) or not lock["files"]:
        raise ValueError("invalid installation manifest")
    seen = set()
    for name, value in lock["files"].items():
        managed_name(name)
        if name.casefold() in seen:
            raise ValueError("duplicate filesystem path alias")
        seen.add(name.casefold())
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("invalid manifest digest")
    return config, lock


def unfinished_updates(root):
    folder = root / ".swarmstack/local/updates"
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise ValueError("unsafe update receipt directory")
    result = []
    if folder.exists():
        for p in folder.glob("*/receipt.json"):
            receipt = json.loads(safe_path(root, p.relative_to(root).as_posix()).read_text(encoding="utf-8"))
            if receipt.get("state") != "complete":
                result.append(p.parent.name)
    return result


def report(project, health=False):
    root = project_root(project)
    result = {"observed_at": datetime.now(timezone.utc).isoformat(), "mode": "health" if health else "status", "network_checked": False}
    if not (root / ".swarmstack").exists() and not (root / ".swarmstack").is_symlink():
        return {**result, "state": "not_installed"}
    try:
        config, lock = load_install(root)
    except (ValueError, OSError, TypeError) as exc:
        return {**result, "state": "incomplete", "errors": [str(exc)]}
    missing, modified, errors = [], [], []
    for name, expected in lock["files"].items():
        try:
            p = safe_path(root, name)
            if not p.exists():
                missing.append(name)
            elif digest(p.read_bytes()) != expected:
                modified.append(name)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    try:
        pending = unfinished_updates(root)
    except (ValueError, OSError, TypeError) as exc:
        pending = ["unreadable receipts"]
        errors.append(str(exc))
    if health:
        for skill in normalise_config(config)["skills"]:
            candidates = [".agents/skills/" + skill + "/SKILL.md"]
            if skill == "swarmstack":
                candidates += [".agents/skills/setup-project/SKILL.md", ".agents/skills/swarmstack-help/SKILL.md"]
            if not any(safe_path(root, name).is_file() for name in candidates):
                errors.append("selected skill missing: " + skill)
        for name in lock["files"]:
            if not name.endswith(".md"):
                continue
            try:
                p = safe_path(root, name)
                if not p.is_file():
                    continue
                for link in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
                    if "://" in link or link.startswith(("#", "mailto:")):
                        continue
                    candidate = Path(os.path.abspath(p.parent / link.split("#")[0].strip("<>")))
                    if root not in candidate.parents and candidate != root:
                        errors.append("external local link in " + name)
                    elif any(x.is_symlink() for x in (candidate, *candidate.parents)) or not candidate.exists():
                        errors.append("missing or symlinked local link in " + name)
            except (ValueError, OSError) as exc:
                errors.append(str(exc))
    return {**result, "state": "attention_needed" if missing or errors or pending else "installed",
            "revision": lock.get("revision"), "source_dirty": lock.get("source_dirty", False),
            "skills": config["skills"], "configured_host": config.get("swarm", {}).get("host"),
            "host_discovery": "unverified", "upstream_version": "not_checked",
            "modified": modified, "missing": missing, "unfinished_updates": pending, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("command", choices=["status", "health"])
    args = parser.parse_args()
    try:
        data = report(args.project, args.command == "health")
        print(json.dumps(data))
        return 1 if data["state"] in {"incomplete", "attention_needed"} else 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({"state": "error", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
