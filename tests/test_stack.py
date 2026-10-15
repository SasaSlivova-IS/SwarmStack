import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap
import stack
import update


def config():
    data = json.loads((ROOT / "templates/project.example.json").read_text())
    data.update(status="confirmed", name="Fixture", goal="Check installation", success="Correct output", github_repository="example/fixture", test_environment="temporary project")
    data["commands"]["test"] = "must-not-execute"
    data["swarm"].update(host="manual", orchestrator="fixture-root")
    for m in data["models"].values():
        m.update(provider="fixture", model="fixture", effort="medium")
    return data


class Stack(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.source = self.base / "source"; self.source.mkdir()
        self.project = self.base / "project"; self.project.mkdir()
        for name in ["skills", "guides", "templates", "scripts", "licenses", ".github"]:
            shutil.copytree(ROOT / name, self.source / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ["SETUP.md", "LICENSE", "CREDITS.md", "THIRD_PARTY.md", "provenance.json", ".gitignore"]:
            shutil.copyfile(ROOT / name, self.source / name)
        self.git("init", "-q")
        self.commit()
        self.patch = mock.patch.object(bootstrap, "ROOT", self.source)
        self.patch.start(); self.addCleanup(self.patch.stop)
        _, outputs = bootstrap.build_plan(self.project, config())
        bootstrap.apply_plan(self.project, outputs)
        self.old_revision = bootstrap.snapshot()["revision"]

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.source), *args], stderr=subprocess.STDOUT)

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")

    def change_source(self):
        p = self.source / "guides/backend.md"
        p.write_text(p.read_text() + "\nAdditional fixture rule.\n")
        self.commit()

    def bytes(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob("*") if p.is_file()}

    def test_status_health_are_read_only_and_do_not_execute_configured_commands(self):
        before = self.bytes()
        self.assertEqual(stack.report(self.project)["revision"], self.old_revision)
        health = stack.report(self.project, True)
        self.assertEqual(health["state"], "installed", health)
        self.assertEqual(health["host_discovery"], "unverified")
        self.assertFalse(health["network_checked"])
        self.assertEqual(before, self.bytes())

    def test_installed_report_and_reviewed_source_update_cli(self):
        before = self.bytes()
        result = subprocess.run([sys.executable, str(self.project / ".swarmstack/scripts/stack.py"), "--project", str(self.project), "health"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "installed")
        self.assertEqual(before, self.bytes())
        self.change_source()
        command = [sys.executable, str(self.source / "scripts/update.py"), "--project", str(self.project)]
        preview = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(before, self.bytes())
        approved = json.loads(preview.stdout)["approval_id"]
        applied = subprocess.run(command + ["--apply", approved], capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual(json.loads(applied.stdout)["state"], "updated")

    def test_missing_file_and_broken_link_are_found_without_repairs(self):
        p = self.project / ".swarmstack/guides/backend.md"; p.unlink()
        result = stack.report(self.project, True)
        self.assertIn(".swarmstack/guides/backend.md", result["missing"])
        self.assertTrue(any("local link" in e for e in result["errors"]))
        self.assertFalse(p.exists())

    def test_local_customisation_is_visible_but_not_called_broken(self):
        p = self.project / ".swarmstack/guides/backend.md"; p.write_text("custom rule\n")
        result = stack.report(self.project, True)
        self.assertIn(".swarmstack/guides/backend.md", result["modified"])
        self.assertEqual(result["state"], "installed")

    def test_preview_no_writes_then_exact_approved_update_and_backups(self):
        self.change_source()
        before = self.bytes()
        proposal, _ = update.plan(self.project)
        self.assertEqual(before, self.bytes())
        self.assertIn("Additional fixture rule", str(proposal["changes"]))
        result = update.apply(self.project, proposal["approval_id"])
        self.assertEqual(result["state"], "updated")
        self.assertEqual(stack.report(self.project, True)["state"], "installed")
        saved = Path(result["receipt"]).parent / "before/.swarmstack/guides/backend.md"
        self.assertEqual(saved.read_bytes(), before[".swarmstack/guides/backend.md"])
        for name in update.PROTECTED:
            self.assertEqual((self.project / name).read_bytes(), before[name])

    def test_local_only_edits_are_preserved_and_remain_visible(self):
        p = self.project / ".swarmstack/guides/frontend.md"; p.write_text("local rule\n")
        self.change_source()
        proposal, _ = update.plan(self.project)
        self.assertIn(".swarmstack/guides/frontend.md", proposal["preserved"])
        update.apply(self.project, proposal["approval_id"])
        self.assertEqual(p.read_text(), "local rule\n")
        self.assertIn(".swarmstack/guides/frontend.md", stack.report(self.project)["modified"])

    def test_conflicting_local_and_upstream_changes_block_all_writes(self):
        p = self.project / ".swarmstack/guides/backend.md"; p.write_text("local rule\n")
        self.change_source()
        proposal, _ = update.plan(self.project)
        self.assertTrue(proposal["conflicts"])
        before = self.bytes()
        with self.assertRaisesRegex(ValueError, "conflicts"):
            update.apply(self.project, proposal["approval_id"])
        self.assertEqual(before, self.bytes())

    def test_project_edit_after_preview_invalidates_approval(self):
        self.change_source(); proposal, _ = update.plan(self.project)
        p = self.project / ".swarmstack/state.md"; p.write_text("changed state\n")
        before = self.bytes()
        with self.assertRaisesRegex(ValueError, "state changed"):
            update.apply(self.project, proposal["approval_id"])
        self.assertEqual(before, self.bytes())

    def test_changed_source_invalidates_approval_and_dirty_source_refuses(self):
        self.change_source(); proposal, _ = update.plan(self.project)
        (self.source / "guides/frontend.md").write_text("changed source\n")
        with self.assertRaisesRegex(ValueError, "clean"):
            update.plan(self.project)
        self.commit()
        with self.assertRaisesRegex(ValueError, "state changed"):
            update.apply(self.project, proposal["approval_id"])

    def test_unsafe_manifest_path_and_symlink_refuse_without_outside_reads_or_writes(self):
        lock = self.project / ".swarmstack/lock.json"
        data = json.loads(lock.read_text()); data["files"]["../outside"] = "0" * 64
        lock.write_text(json.dumps(data))
        with self.assertRaises(ValueError): update.plan(self.project)
        self.assertEqual(stack.report(self.project)["state"], "incomplete")

    def test_symlinked_managed_file_is_not_overwritten(self):
        p = self.project / ".swarmstack/guides/backend.md"; p.unlink()
        outside = self.base / "outside"; outside.write_text("preserve")
        p.symlink_to(outside)
        self.change_source()
        with self.assertRaisesRegex(ValueError, "symlink"): update.plan(self.project)
        self.assertEqual(outside.read_text(), "preserve")

    def test_add_and_remove_managed_paths_only_from_approved_plan(self):
        added = self.source / "guides/fixture.md"; added.write_text("new guide\n")
        (self.source / "guides/improvement.md").unlink(); self.commit()
        proposal, _ = update.plan(self.project)
        self.assertIn("remove", [c["action"] for c in proposal["changes"]])
        update.apply(self.project, proposal["approval_id"])
        self.assertTrue((self.project / ".swarmstack/guides/fixture.md").exists())
        self.assertFalse((self.project / ".swarmstack/guides/improvement.md").exists())
        self.assertEqual(stack.report(self.project, True)["state"], "installed")

    def test_disk_failure_retains_receipt_backup_and_blocks_blind_retry(self):
        self.change_source(); proposal, _ = update.plan(self.project)
        original = update.replace_file
        def fail(path, data):
            if path == self.project / ".swarmstack/guides/backend.md":
                raise OSError("injected disk fault")
            return original(path, data)
        with mock.patch.object(update, "replace_file", fail):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                update.apply(self.project, proposal["approval_id"])
        self.assertTrue(stack.report(self.project)["unfinished_updates"])
        with self.assertRaisesRegex(ValueError, "unfinished"):
            update.plan(self.project)

    def test_health_refuses_invalid_configuration_and_missing_selected_skill(self):
        path = self.project / ".swarmstack/project.json"
        original = json.loads(path.read_text())
        for key in ["authority", "budget", "commands", "models"]:
            data = copy.deepcopy(original); data.pop(key)
            path.write_text(json.dumps(data))
            with self.subTest(key=key):
                self.assertEqual(stack.report(self.project, True)["state"], "incomplete")
        data = copy.deepcopy(original); data["swarm"]["host"] = "unsupported"
        path.write_text(json.dumps(data))
        self.assertEqual(stack.report(self.project, True)["state"], "incomplete")
        path.write_text(json.dumps(original))

    def test_optional_host_metadata_is_validated_even_without_swarm_skill(self):
        path = self.project / ".swarmstack/project.json"
        original = json.loads(path.read_text())
        original["skills"].remove("swarm")
        for bad in [None, [], "unsupported", {"host": "unknown"}]:
            data = copy.deepcopy(original); data["swarm"] = bad
            path.write_text(json.dumps(data))
            with self.subTest(bad=bad):
                self.assertEqual(stack.report(self.project, True)["state"], "incomplete")

    def test_manifest_case_aliases_refuse_before_planning(self):
        path = self.project / ".swarmstack/lock.json"
        original = json.loads(path.read_text())
        for name in [".swarmstack/STATE.md", ".swarmstack/PROJECT.json", ".swarmstack/DECISIONS.md", ".swarmstack/guides/BACKEND.md"]:
            data = copy.deepcopy(original)
            data["files"][name] = data["files"][name.lower()]
            path.write_text(json.dumps(data))
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    update.plan(self.project)
        path.write_text(json.dumps(original))

    def test_not_installed_and_partial_setup_are_truthful(self):
        empty = self.base / "empty"; empty.mkdir()
        self.assertEqual(stack.report(empty)["state"], "not_installed")
        (empty / ".swarmstack").mkdir()
        self.assertEqual(stack.report(empty)["state"], "incomplete")


if __name__ == "__main__":
    unittest.main()
