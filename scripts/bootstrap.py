"""Preview-first project adoption. Never executes project commands or overwrites files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
from configuration import normalise_config, validate

def safe_directory(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("target has a symlink component")
    if not path.is_dir():
        raise ValueError("target must be an existing directory")
    if path == ROOT or ROOT in path.parents or path in ROOT.parents:
        raise ValueError("target must be separate from the toolkit, not its ancestor")
    return path


def snapshot():
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(ROOT), *args], text=True, stderr=subprocess.DEVNULL).strip()
    return {"revision": git("rev-parse", "HEAD"), "source_dirty": bool(git("status", "--porcelain", "--untracked-files=normal"))}


def optional_swarm(body, enabled):
    pattern = r"<!-- swarm:start -->(.*?)<!-- swarm:end -->"
    return re.sub(pattern, lambda match: match[1].strip() if enabled else "", body, flags=re.S)


def render_outputs(config, *, installation_only=False, skill_hosts=None):
    config = normalise_config(config)
    validate(config, draft=installation_only)
    skill_hosts = ["codex"] if skill_hosts is None else skill_hosts
    if not skill_hosts or len(set(skill_hosts)) != len(skill_hosts) or not set(skill_hosts) <= {"codex", "claude"}:
        raise ValueError("select codex, claude or both skill mappings")
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
    add(".swarmstack/INSTALL.md", (ROOT / "INSTALL.md").read_text().replace("](skills/", "](../.agents/skills/"))
    add(".swarmstack/templates/project.example.json", (ROOT / "templates/project.example.json").read_bytes())
    add(".swarmstack/scripts/configuration.py", (ROOT / "scripts/configuration.py").read_bytes())
    add(".swarmstack/scripts/stack.py", (ROOT / "scripts/stack.py").read_bytes())
    add(".swarmstack/scripts/model_frontier.py", (ROOT / "scripts/model_frontier.py").read_bytes())
    if "swarm" in config["skills"]:
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
            if name == "swarmstack" and src.parent.name == "references":
                body = body.replace("../../../SETUP.md", "../../../../.swarmstack/SETUP.md").replace("../../../INSTALL.md", "../../../../.swarmstack/INSTALL.md").replace("../../../scripts/stack.py", "../../../../.swarmstack/scripts/stack.py")
            if src.name == "SKILL.md":
                body = body.replace("../../SETUP.md", "../../../.swarmstack/SETUP.md").replace("../../guides/", "../../../.swarmstack/guides/").replace("../../scripts/", "../../../.swarmstack/scripts/")
            add(".agents/skills/" + name + "/" + src.relative_to(ROOT / "skills" / name).as_posix(), body)
    if "claude" in skill_hosts:
        for name, data in list(outputs.items()):
            if name.startswith(".agents/skills/"):
                outputs[name.replace(".agents/skills/", ".claude/skills/", 1)] = data
    if installation_only:
        outputs = {name: data for name, data in outputs.items() if name not in {"AGENTS.md", "docs/agents/issue-tracker.md", ".swarmstack/state.md", ".swarmstack/decisions.md"} and not name.startswith(".github/")}
    for src in sorted((ROOT / "licenses").glob("*.txt")):
        add(".swarmstack/licenses/" + src.name, src.read_bytes())
    add(".swarmstack/LICENSE", (ROOT / "LICENSE").read_bytes())
    add(".swarmstack/CREDITS.md", (ROOT / "CREDITS.md").read_text().replace("](skills/", "](../.agents/skills/"))
    add(".swarmstack/provenance.json", (ROOT / "provenance.json").read_bytes())
    add(".swarmstack/THIRD_PARTY.md", (ROOT / "THIRD_PARTY.md").read_text().replace("skills/*/", "../.agents/skills/*/"))
    lock = {"toolkit": "SwarmStack", "phase": "installed" if installation_only else "configured", "skill_hosts": skill_hosts, **snapshot(), "files": {name: hashlib.sha256(data).hexdigest() for name, data in outputs.items()}}
    add(".swarmstack/lock.json", json.dumps(lock, indent=2) + "\n")
    return outputs


def build_plan(target, config):
    target = safe_directory(target)
    outputs = render_outputs(config)
    return new_files_plan(target, outputs)


def new_files_plan(target, outputs):
    target = safe_directory(target)
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
