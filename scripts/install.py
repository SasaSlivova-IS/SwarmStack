"""Install project-local SwarmStack skills. No project configuration or global changes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import bootstrap


def build_plan(target, host="codex"):
    if host not in {"codex", "claude", "both"}:
        raise ValueError("choose codex, claude or both")
    target = bootstrap.safe_directory(target)
    if (target / ".swarmstack").exists() or (target / ".swarmstack").is_symlink():
        raise ValueError("SwarmStack installation already exists; nothing was changed")
    if bootstrap.snapshot()["source_dirty"]:
        raise ValueError("installation needs a clean, reviewed toolkit checkout")
    config = json.loads((bootstrap.ROOT / "templates/project.example.json").read_text(encoding="utf-8"))
    hosts = ["codex", "claude"] if host == "both" else [host]
    outputs = bootstrap.render_outputs(config, installation_only=True, skill_hosts=hosts)
    return bootstrap.new_files_plan(target, outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--host", choices=["codex", "claude", "both"], default="codex")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        target, outputs = build_plan(args.target, args.host)
        print(json.dumps({"mode": "apply" if args.apply else "preview", "host": args.host, "files": list(outputs)}, indent=2))
        if args.apply:
            bootstrap.apply_plan(target, outputs)
            print("Skills installed locally. Refresh skill discovery, then run /swarmstack setup. Project is not configured.")
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print("Refused: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
