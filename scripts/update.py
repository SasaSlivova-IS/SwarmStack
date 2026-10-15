"""Preview or apply an approved toolkit-only update from this clean, reviewed checkout."""
import argparse
import difflib
import json
import os
from pathlib import Path
import sys
import tempfile

import bootstrap
import stack

PROTECTED = stack.PROJECT_RECORDS
LOCK = ".swarmstack/lock.json"


def current_bytes(root, name):
    path = stack.safe_path(root, name)
    return path.read_bytes() if path.exists() else None


def plan(project):
    root = stack.project_root(project)
    bootstrap.safe_directory(root)
    config, old = stack.load_install(root)
    pending = stack.unfinished_updates(root)
    if pending:
        raise ValueError("reconcile unfinished update receipts before another update")
    source = bootstrap.snapshot()
    if source["source_dirty"]:
        raise ValueError("update source must be a clean, reviewed Git checkout")
    desired = bootstrap.render_outputs(config)
    desired.pop(LOCK)
    if bootstrap.snapshot() != source:
        raise ValueError("source changed while preparing update; review a fresh checkout")
    for name in desired:
        stack.managed_name(name)
    seen = {}
    for name in set(old["files"]) | set(desired):
        previous = seen.setdefault(name.casefold(), name)
        if previous != name:
            raise ValueError("source/installation filesystem path alias")
    changes, conflicts, preserved, expected = [], [], [], {}
    next_files = dict(old["files"])
    payloads = {}
    for name in sorted(set(old["files"]) | set(desired)):
        before = current_bytes(root, name)
        present = stack.digest(before) if before is not None else None
        expected[name] = present
        base = old["files"].get(name)
        after = desired.get(name)
        target = stack.digest(after) if after is not None else None
        if name in PROTECTED:
            if before is None:
                conflicts.append({"path": name, "reason": "missing project-owned record"})
            else:
                preserved.append(name)
            continue
        if present == target:
            if target is None:
                next_files.pop(name, None)
            else:
                next_files[name] = target
            continue
        if present != base:
            if target == base:
                preserved.append(name)
            else:
                conflicts.append({"path": name, "reason": "local and upstream changes require a reviewed merge"})
            continue
        action = "remove" if after is None else "add" if before is None else "replace"
        diff = "".join(difflib.unified_diff((before or b"").decode("utf-8").splitlines(True),
                                          (after or b"").decode("utf-8").splitlines(True),
                                          fromfile=name, tofile=name))
        changes.append({"path": name, "action": action, "before": present, "after": target, "diff": diff})
        payloads[name] = after
        if target is None:
            next_files.pop(name, None)
        else:
            next_files[name] = target
    old_lock = current_bytes(root, LOCK)
    expected[LOCK] = stack.digest(old_lock)
    new_lock = {"toolkit": "SwarmStack", **source, "files": next_files}
    payloads[LOCK] = (json.dumps(new_lock, indent=2) + "\n").encode()
    data = {"project": str(root), "from_revision": old.get("revision"), "to_revision": source["revision"],
            "changes": changes, "conflicts": conflicts, "preserved": preserved, "expected": expected,
            "manifest_after": stack.digest(payloads[LOCK])}
    data["approval_id"] = stack.digest(json.dumps(data, sort_keys=True).encode())
    return data, payloads


def replace_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp = tempfile.mkstemp(prefix=".swarmstack-update-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_receipt(path, data):
    replace_file(path, (json.dumps(data, indent=2) + "\n").encode())


def apply(project, approval_id):
    data, payloads = plan(project)
    if data["approval_id"] != approval_id:
        raise ValueError("proposal or project/source state changed; review a fresh preview")
    if data["conflicts"]:
        raise ValueError("resolve local/upstream conflicts before applying")
    root = stack.project_root(project)
    for name, expected in data["expected"].items():
        before = current_bytes(root, name)
        if (stack.digest(before) if before is not None else None) != expected:
            raise ValueError("project changed before update: " + name)
    folder = root / ".swarmstack/local/updates" / approval_id
    if any(p.is_symlink() or (p.exists() and not p.is_dir()) for p in (folder, *folder.parents)):
        raise ValueError("unsafe update backup directory")
    if folder.exists():
        raise ValueError("update backup already exists; reconcile it before retrying")
    folder.mkdir(parents=True)
    # Keep backup contents out of ordinary source control, even without the swarm gate.
    (folder / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
    changed = []
    receipt = {"approval_id": approval_id, "state": "preparing", "changed": changed}
    receipt_path = folder / "receipt.json"
    write_receipt(receipt_path, receipt)
    try:
        for name in [c["path"] for c in data["changes"]] + [LOCK]:
            before = current_bytes(root, name)
            if before is not None:
                saved = folder / "before" / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(before)
        (folder / "proposal.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        receipt["state"] = "applying"
        write_receipt(receipt_path, receipt)
        for name in [c["path"] for c in data["changes"]] + [LOCK]:
            before = current_bytes(root, name)
            if (stack.digest(before) if before is not None else None) != data["expected"][name]:
                raise ValueError("project changed at write boundary: " + name)
            path = stack.safe_path(root, name)
            if payloads[name] is None:
                path.unlink()
            else:
                replace_file(path, payloads[name])
            changed.append(name)
            write_receipt(receipt_path, receipt)
        receipt["state"] = "complete"
        write_receipt(receipt_path, receipt)
    except (ValueError, OSError) as exc:
        receipt.update(state="failed", error=str(exc))
        try:
            write_receipt(receipt_path, receipt)
        except OSError:
            pass
        raise RuntimeError("update interrupted; preserve backup and reconcile receipt " + str(receipt_path)) from exc
    return {"state": "updated", "revision": data["to_revision"], "changed": changed, "preserved": data["preserved"],
            "receipt": str(receipt_path), "runtime_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--apply", metavar="APPROVAL_ID", help="apply only the exact reviewed preview")
    args = parser.parse_args()
    try:
        result = apply(args.project, args.apply) if args.apply else plan(args.project)[0]
        print(json.dumps(result, indent=2))
        return 1 if result.get("conflicts") else 0
    except (ValueError, OSError, RuntimeError, TypeError) as exc:
        print(json.dumps({"state": "refused", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
