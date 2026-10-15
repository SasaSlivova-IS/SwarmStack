"""Standalone /swarm command gate. Local SQLite only; no host API, network or scheduler."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from urllib.parse import urlsplit

MIN_COOLDOWN = 5 * 60 * 60
VERSION = 1
INFLIGHT = ("offered", "delivered", "uncertain")


def parse_command(text, repository):
    parts = text.strip().split()
    if len(parts) != 2 or parts[0] != "/swarm":
        raise ValueError("use /swarm followed by one command or a GitHub issue link")
    value = parts[1]
    if value in {"backend", "frontend", "auto"}:
        return "direction", value, "queue"
    if value in {"status", "blockers"}:
        return "report", value, "read"
    if value in {"pause", "resume"}:
        return "control", value, "steer" if value == "pause" else "wake_or_queue"
    url = urlsplit(value)
    match = re.fullmatch(r"/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)/?", url.path)
    if url.scheme != "https" or url.netloc.lower() != "github.com" or not match or match[1].lower() != repository.lower():
        raise ValueError("provide an HTTPS GitHub issue link for this configured repository")
    return "direction", "https://github.com/" + repository + "/issues/" + match[2], "queue"


def project_config(project):
    root = Path(os.path.abspath(project))
    if not root.is_dir() or any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("project must be an existing directory without symlink components")
    path = root / ".swarmstack/project.json"
    if any(p.is_symlink() for p in (path, path.parent)):
        raise ValueError("project configuration must not use symlinks")
    config = json.loads(path.read_text(encoding="utf-8"))
    repo = config.get("github_repository", "")
    options = config.get("swarm", {})
    if config.get("schema_version") != 1 or config.get("status") != "confirmed" or not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("confirmed v1 project configuration is required")
    if not isinstance(options, dict) or set(options) != {"host", "orchestrator", "direction_cooldown_seconds", "status_ttl_seconds"}:
        raise ValueError("configure the swarm host, orchestrator and cooldowns first")
    if options["host"] not in {"t3", "codex", "claude", "manual"} or not isinstance(options["orchestrator"], str) or not options["orchestrator"].strip():
        raise ValueError("verify and configure one actual orchestrator identity")
    for key, minimum, maximum in [("direction_cooldown_seconds", MIN_COOLDOWN, 31536000), ("status_ttl_seconds", 0, 3600)]:
        value = options[key]
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError("invalid " + key)
    return root, repo.lower(), options


class Gate:
    def __init__(self, project, *, now=None, immediate=False):
        self.root, self.repo, self.options = project_config(project)
        self.now = time.time() if now is None else now
        if type(self.now) not in (int, float) or not math.isfinite(self.now) or self.now < 0:
            raise ValueError("invalid wall clock")
        self.binding = json.dumps([str(self.root), self.repo.lower(), self.options["host"], self.options["orchestrator"]])
        folder = self.root / ".swarmstack/local"
        if folder.is_symlink() or (folder.exists() and not folder.is_dir()):
            raise ValueError("unsafe local state directory")
        folder.mkdir(mode=0o700, exist_ok=True)
        db = folder / "swarm.sqlite3"
        for suffix in ["", "-journal", "-wal", "-shm"]:
            file = Path(str(db) + suffix)
            if file.is_symlink() or (file.exists() and (not file.is_file() or file.stat().st_nlink != 1)):
                raise ValueError("unsafe local state file")
        self.db = sqlite3.connect(str(db), timeout=0 if immediate else 5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS commands (id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, target TEXT NOT NULL, route TEXT NOT NULL, state TEXT NOT NULL, created REAL NOT NULL, external_id TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS cache (name TEXT PRIMARY KEY, observed REAL NOT NULL, payload TEXT NOT NULL)")
            if self.get("version", VERSION) != VERSION or self.get("binding", self.binding) != self.binding:
                raise ValueError("state version or project/orchestrator binding mismatch")
            self.set("version", VERSION)
            self.set("binding", self.binding)
            previous = self.get("last_seen", self.now)
            if type(previous) not in (int, float) or not math.isfinite(previous) or previous < 0:
                raise ValueError("invalid persisted clock")
            self.clock_rollback = self.now < previous
            self.now = max(self.now, previous)
            self.set("last_seen", self.now)
        except Exception:
            self.db.rollback()
            self.db.close()
            raise

    def close(self, commit=True):
        try:
            self.db.commit() if commit else self.db.rollback()
        finally:
            self.db.close()

    def get(self, key, default=None):
        row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return default if row is None else json.loads(row[0])

    def set(self, key, value):
        self.db.execute("INSERT INTO meta VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))

    def output(self, status, row=None, **extra):
        data = {"status": status, "host": self.options["host"], "orchestrator": self.options["orchestrator"], "clock_rollback": self.clock_rollback, **extra}
        if row is not None:
            data.update(command_id=row["id"], target=row["target"], route=row["route"], state=row["state"], transport_key=row["id"], external_id=row["external_id"])
        return data

    def inflight(self):
        return self.db.execute("SELECT * FROM commands WHERE kind='direction' AND state IN ('offered','delivered','uncertain') ORDER BY created LIMIT 1").fetchone()

    def request(self, text, request_id):
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 200 or any(ord(c) < 32 for c in request_id):
            raise ValueError("use the stable original user-message ID")
        kind, target, route = parse_command(text, self.repo)
        existing = self.db.execute("SELECT * FROM commands WHERE request_id=?", (request_id,)).fetchone()
        if existing:
            if (existing["kind"], existing["target"]) != (kind, target):
                raise ValueError("request ID cannot be rebound to another command")
            return self.output("ALREADY_RECORDED", existing)
        ident = hashlib.sha256((self.binding + "\n" + request_id).encode()).hexdigest()
        if kind == "report":
            self.db.execute("INSERT INTO commands VALUES (?,?,?,?,?,?,?,NULL)", (ident, request_id, kind, target, route, "read", self.now))
            row = self.db.execute("SELECT * FROM cache WHERE name=?", (target,)).fetchone()
            if row and not self.clock_rollback and 0 <= self.now - row["observed"] < self.options["status_ttl_seconds"]:
                return self.output("CACHED", route="read", report=target, observed_at=row["observed"], payload=json.loads(row["payload"]))
            return self.output("READ", route="read", report=target, reason="refresh from actual records; queue one request only if Root must supply missing facts")
        active = self.get("active_direction")
        if kind == "direction" and active == target and not self.inflight():
            self.db.execute("UPDATE commands SET state='superseded' WHERE kind='direction' AND state='pending'")
            self.db.execute("INSERT INTO commands VALUES (?,?,?,?,?,?,?,NULL)", (ident, request_id, kind, target, route, "noop", self.now))
            return self.output("ALREADY_ACTIVE", target=target, route="none", eligible_at=self.get("eligible_at", 0))
        state = "pending" if kind == "direction" else "offered"
        self.db.execute("INSERT INTO commands VALUES (?,?,?,?,?,?,?,NULL)", (ident, request_id, kind, target, route, state, self.now))
        row = self.db.execute("SELECT * FROM commands WHERE id=?", (ident,)).fetchone()
        if kind == "control":
            self.set("latest_control", ident)
            if target == "pause":
                self.set("pause_requested", True)
        if kind != "direction":
            return self.output("ALLOW", row, instruction="same authorised goal only; verify actual host state")
        self.db.execute("UPDATE commands SET state='superseded' WHERE kind='direction' AND state='pending' AND id<>?", (ident,))
        return self.next()

    def next(self):
        pending = self.db.execute("SELECT * FROM commands WHERE kind='direction' AND state='pending' ORDER BY created DESC LIMIT 1").fetchone()
        if pending is None:
            return self.output("EMPTY")
        outstanding = self.inflight()
        if outstanding:
            return self.output("DEFER", pending, reason="reconcile outstanding host delivery first; never resend under a new key", outstanding_command=outstanding["id"], eligible_at=self.get("eligible_at", 0))
        if self.get("paused", False) or self.get("pause_requested", False):
            return self.output("DEFER", pending, reason="goal is paused; direction does not resume it", eligible_at=self.get("eligible_at", 0))
        if self.clock_rollback:
            return self.output("DEFER", pending, reason="wall clock moved backwards; retain pending direction")
        eligible = self.get("eligible_at", 0)
        if self.now < eligible:
            return self.output("DEFER", pending, reason="five-hour direction window", eligible_at=eligible)
        self.db.execute("UPDATE commands SET state='offered' WHERE id=?", (pending["id"],))
        return self.output("ALLOW", dict(pending, state="offered"), instruction="queue once using transport_key; no expanded authority")

    def receipt(self, ident, result, external_id=None):
        row = self.db.execute("SELECT * FROM commands WHERE id=?", (ident,)).fetchone()
        if row is None:
            raise ValueError("unknown command")
        if external_id is not None and row["external_id"] and row["external_id"] != external_id:
            raise ValueError("conflicting external receipt")
        if result == "delivered":
            if not isinstance(external_id, str) or not external_id.strip() or len(external_id) > 300:
                raise ValueError("actual host message receipt is required")
            if row["state"] not in INFLIGHT or (row["external_id"] and row["external_id"] != external_id):
                raise ValueError("delivery receipt conflicts with recorded state")
        elif result == "applied":
            if row["state"] == "applied":
                return self.output("ALREADY_RECORDED", row)
            if row["state"] != "delivered" or not row["external_id"]:
                raise ValueError("delivery is required before observed application")
        elif result not in {"failed", "uncertain"} or row["state"] not in INFLIGHT:
            raise ValueError("invalid receipt transition")
        self.db.execute("UPDATE commands SET state=?,external_id=COALESCE(?,external_id) WHERE id=?", (result, external_id, ident))
        if result == "applied":
            if row["kind"] == "direction":
                self.set("active_direction", row["target"])
                self.set("eligible_at", self.now + self.options["direction_cooldown_seconds"])
            elif row["target"] in {"pause", "resume"} and self.get("latest_control") == ident:
                self.set("paused", row["target"] == "pause")
                self.set("pause_requested", row["target"] == "pause")
            self.db.execute("DELETE FROM cache")
        return self.output("RECORDED", dict(row, state=result))

    def cache(self, name, payload):
        if name not in {"status", "blockers"}:
            raise ValueError("unknown report")
        raw = json.dumps(payload)
        if len(raw.encode()) > 16384:
            raise ValueError("keep reports below 16 KiB")
        self.db.execute("INSERT INTO cache VALUES (?,?,?) ON CONFLICT(name) DO UPDATE SET observed=excluded.observed,payload=excluded.payload", (name, self.now, raw))
        return self.output("RECORDED", report=name, observed_at=self.now)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    sub = parser.add_subparsers(dest="action", required=True)
    req = sub.add_parser("request"); req.add_argument("command"); req.add_argument("--request-id", required=True)
    sub.add_parser("next")
    sub.add_parser("inspect")
    rec = sub.add_parser("receipt"); rec.add_argument("command_id"); rec.add_argument("result", choices=["delivered", "applied", "failed", "uncertain"]); rec.add_argument("--external-id")
    cache = sub.add_parser("cache"); cache.add_argument("name", choices=["status", "blockers"]); cache.add_argument("--json-file", type=Path, required=True)
    sub.add_parser("invalidate")
    args = parser.parse_args()
    gate = None
    try:
        if args.action == "request" and (not 1 <= len(args.request_id) <= 200 or any(ord(c) < 32 for c in args.request_id)):
            raise ValueError("use the stable original user-message ID")
        is_pause = args.action == "request" and args.command.strip() == "/swarm pause"
        try:
            gate = Gate(args.project, immediate=is_pause)
        except (ValueError, OSError, sqlite3.Error, TypeError) as exc:
            if not is_pause:
                raise
            root, repo, options = project_config(args.project)
            ident = hashlib.sha256((json.dumps([str(root), repo.lower(), options["host"], options["orchestrator"]]) + "\n" + args.request_id).encode()).hexdigest()
            print(json.dumps({"status": "ALLOW", "target": "pause", "route": "steer", "command_id": ident, "transport_key": ident, "persisted": False, "host": options["host"], "orchestrator": options["orchestrator"], "warning": "local state unavailable; pause still routes to verified orchestrator"}))
            return 0
        if args.action == "request":
            result = gate.request(args.command, args.request_id)
        elif args.action == "next":
            result = gate.next()
        elif args.action == "inspect":
            rows = gate.db.execute("SELECT * FROM commands WHERE state IN ('offered','delivered','uncertain','pending') ORDER BY created DESC LIMIT 10").fetchall()
            result = gate.output("STATE", active_direction=gate.get("active_direction"), eligible_at=gate.get("eligible_at", 0), pause_requested=gate.get("pause_requested", False), latest_control=gate.get("latest_control"), outstanding=[dict(row) for row in rows])
        elif args.action == "receipt":
            result = gate.receipt(args.command_id, args.result, args.external_id)
        elif args.action == "cache":
            result = gate.cache(args.name, json.loads(args.json_file.read_text(encoding="utf-8")))
        else:
            gate.db.execute("DELETE FROM cache"); result = gate.output("RECORDED")
        gate.close(); gate = None
        print(json.dumps(result, separators=(",", ":")))
        return 0
    except (ValueError, OSError, sqlite3.Error, TypeError) as exc:
        if gate is not None:
            gate.close(False)
        print(json.dumps({"status": "ERROR", "route": "none", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
