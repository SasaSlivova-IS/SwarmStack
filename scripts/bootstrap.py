"""Preview-first project adoption. Never executes project commands or overwrites files."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"grill-with-docs", "code-review", "setup-project", "delivery", "adhd-output", "unslop", "swarm"}
AUTHORITY = {"create_threads", "create_branches", "push_issue_branches", "open_prs", "merge_integration", "promote_production", "deploy"}


def safe_directory(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("target has a symlink component")
    if not path.is_dir():
        raise ValueError("target must be an existing directory")
    if path == ROOT or ROOT in path.parents or path in ROOT.parents:
        raise ValueError("target must be separate from the toolkit, not its ancestor")
    return path


def local_path(value):
    return isinstance(value, str) and bool(value) and not value.startswith(("/", "\\")) and not re.match(r"^[A-Za-z]:", value) and ".." not in value.replace("\\", "/").split("/")


def validate(config):
    required = {"schema_version", "status", "name", "goal", "success", "github_repository", "primary_branch", "integration_branch", "requirements_path", "glossary_path", "test_environment", "commands", "models", "budget", "authority", "human_ux_acceptance_required", "skills"}
    if not required <= set(config) or set(config) - required - {"swarm"} or config.get("schema_version") != 1 or config.get("status") != "confirmed":
        raise ValueError("use the exact v1 configuration and confirm setup first")
    for field in ["name", "goal", "success", "github_repository", "primary_branch", "integration_branch", "test_environment"]:
        value = config[field]
        if not isinstance(value, str) or not value.strip() or any(x in value for x in ["REPLACE_", "SELECT_", "\n", "\r"]):
            raise ValueError("unresolved or invalid field: " + field)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config["github_repository"]):
        raise ValueError("github_repository must be owner/repository")
    if not all(local_path(config[f]) for f in ["requirements_path", "glossary_path"]):
        raise ValueError("requirements/glossary must use project-relative paths")
    if set(config["commands"]) != {"test", "lint", "typecheck", "build"}:
        raise ValueError("commands must name test/lint/typecheck/build, nullable when inapplicable")
    for name, command in config["commands"].items():
        if command is not None and (not isinstance(command, str) or not command.strip() or "REPLACE_" in command):
            raise ValueError("unresolved command: " + name)
    if not config["commands"]["test"]:
        raise ValueError("an actual test/check command is required")
    if set(config["authority"]) != AUTHORITY or not all(type(v) is bool for v in config["authority"].values()):
        raise ValueError("authority grants must be explicit booleans")
    if type(config["human_ux_acceptance_required"]) is not bool:
        raise ValueError("human acceptance policy must be explicit")
    budget = config["budget"]
    if set(budget) != {"spend_limit_usd", "paid_overage", "allowed_data"}:
        raise ValueError("invalid budget fields")
    cost = budget["spend_limit_usd"]
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0 or type(budget["paid_overage"]) is not bool or not isinstance(budget["allowed_data"], str) or not budget["allowed_data"].strip():
        raise ValueError("invalid budget or data permission")
    if not isinstance(config["skills"], list) or not config["skills"] or len(set(config["skills"])) != len(config["skills"]) or not set(config["skills"]) <= SKILLS:
        raise ValueError("select known unique skills")
    if not {"grill-with-docs", "code-review", "setup-project", "delivery", "adhd-output", "unslop"} <= set(config["skills"]):
        raise ValueError("the six original linked skills remain required; new setups also select swarm")
    if set(config["models"]) != {"frontend", "backend", "review"}:
        raise ValueError("select frontend/backend/review models from the live host")
    for model in config["models"].values():
        if not isinstance(model, dict) or set(model) != {"provider", "model", "effort"} or any(not isinstance(v, str) or not v.strip() or "SELECT_" in v for v in model.values()):
            raise ValueError("model IDs and efforts must be resolved")


def snapshot():
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(ROOT), *args], text=True, stderr=subprocess.DEVNULL).strip()
    return {"revision": git("rev-parse", "HEAD"), "source_dirty": bool(git("status", "--porcelain", "--untracked-files=normal"))}


def optional_swarm(body, enabled):
    pattern = r"<!-- swarm:start -->(.*?)<!-- swarm:end -->"
    return re.sub(pattern, lambda match: match[1].strip() if enabled else "", body, flags=re.S)


def build_plan(target, config):
    target = safe_directory(target)
    validate(config)
    uses_swarm = "swarm" in config["skills"]
    outputs = {}
    def add(name, data):
        if name in outputs:
            raise ValueError("duplicate output: " + name)
        outputs[name] = data.encode() if isinstance(data, str) else data
    add("AGENTS.md", optional_swarm((ROOT / "templates/project/AGENTS.md").read_text().replace("{{PROJECT_NAME}}", config["name"]), uses_swarm))
    add(".swarmstack/project.json", json.dumps(config, indent=2) + "\n")
    add(".swarmstack/state.md", "# Current project state\n\nSetup adopted; project behavior is not yet qualified. Root records issue owners, pins, blockers, next actions and evidence here.\n")
    add(".swarmstack/decisions.md", "# Accepted setup\n\nThe user-confirmed project.json is the setup decision. Record future accepted changes and unresolved questions here; installation is not runtime acceptance.\n")
    add("docs/agents/issue-tracker.md", "# Issue tracker\n\nGitHub repository: " + config["github_repository"] + "\n\nRead issues with the host connector or gh issue view NUMBER --repo " + config["github_repository"] + ". Use full accepted scope and relevant comments, not only titles. Posting, closing and merging require project authority. One dedicated thread per issue.\n")
    for src in sorted((ROOT / "guides").glob("*.md")):
        body = optional_swarm(src.read_text(), uses_swarm).replace("../skills/", "../../.agents/skills/")
        add(".swarmstack/guides/" + src.name, body)
    setup = (ROOT / "SETUP.md").read_text().replace("](skills/", "](../.agents/skills/")
    add(".swarmstack/SETUP.md", setup)
    add(".swarmstack/templates/project.example.json", (ROOT / "templates/project.example.json").read_bytes())
    add(".swarmstack/scripts/model_frontier.py", (ROOT / "scripts/model_frontier.py").read_bytes())
    if "swarm" in config["skills"]:
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("swarm_gate", ROOT / "scripts/swarm.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.validate_options(config.get("swarm", {}))
        add(".swarmstack/scripts/swarm.py", (ROOT / "scripts/swarm.py").read_bytes())
        add(".swarmstack/local/.gitignore", "*\n!.gitignore\n")
    for src in sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        add(".github/ISSUE_TEMPLATE/" + src.name, src.read_bytes())
    add(".github/pull_request_template.md", (ROOT / ".github/pull_request_template.md").read_bytes())
    for name in config["skills"]:
        for src in sorted((ROOT / "skills" / name).rglob("*")):
            if not src.is_file():
                continue
            body = src.read_text()
            if src.name == "SKILL.md":
                body = body.replace("../../SETUP.md", "../../../.swarmstack/SETUP.md").replace("../../guides/", "../../../.swarmstack/guides/").replace("../../scripts/", "../../../.swarmstack/scripts/")
            add(".agents/skills/" + name + "/" + src.relative_to(ROOT / "skills" / name).as_posix(), body)
    for src in sorted((ROOT / "licenses").glob("*.txt")):
        add(".swarmstack/licenses/" + src.name, src.read_bytes())
    add(".swarmstack/LICENSE", (ROOT / "LICENSE").read_bytes())
    add(".swarmstack/CREDITS.md", (ROOT / "CREDITS.md").read_text().replace("](skills/", "](../.agents/skills/"))
    add(".swarmstack/provenance.json", (ROOT / "provenance.json").read_bytes())
    add(".swarmstack/THIRD_PARTY.md", (ROOT / "THIRD_PARTY.md").read_text().replace("skills/*/", "../.agents/skills/*/"))
    lock = {"toolkit": "SwarmStack", **snapshot(), "files": {name: hashlib.sha256(data).hexdigest() for name, data in outputs.items()}}
    add(".swarmstack/lock.json", json.dumps(lock, indent=2) + "\n")
    for name in outputs:
        dest = target / name
        if dest.exists() or dest.is_symlink():
            raise ValueError("refusing existing destination: " + name)
        if any(p.is_symlink() or (p.exists() and not p.is_dir()) for p in dest.parents if p != target and target in p.parents):
            raise ValueError("unsafe destination parent: " + name)
    return target, outputs


def apply_plan(target, outputs):
    created, completed = [], []
    try:
        for name, data in outputs.items():
            dest = target / name
            # Recheck at the write boundary. No attempt to support hostile concurrent writers.
            if any(p.is_symlink() for p in (dest, *dest.parents)):
                raise ValueError("symlink appeared during apply: " + name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as stream:
                created.append(name)
                stream.write(data)
            completed.append(name)
    except (OSError, ValueError) as exc:
        raise RuntimeError("setup stopped; preserve partial files " + json.dumps({"created": created, "completed": completed}) + ": " + str(exc)) from exc
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        target, outputs = build_plan(args.target, config)
        print(json.dumps({"mode": "apply" if args.apply else "preview", "target": str(target), "files": list(outputs)}, indent=2))
        if args.apply:
            written = apply_plan(target, outputs)
            print("Installed " + str(len(written)) + " files; no project command executed.")
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print("Refused: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
