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
import install


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
        for name in ["SETUP.md", "INSTALL.md", "LICENSE", "CREDITS.md", "THIRD_PARTY.md", "provenance.json", ".gitignore"]:
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

    def install_draft(self, host="both"):
        target = self.base / "new-project"; target.mkdir()
        _, payload = install.build_plan(target, host)
        bootstrap.apply_plan(target, payload)
        return target

    def test_installer_preview_then_project_local_skills_without_configuration(self):
        target = self.base / "fresh"; target.mkdir()
        _, payload = install.build_plan(target, "both")
        self.assertEqual(list(target.iterdir()), [])
        bootstrap.apply_plan(target, payload)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / ".github").exists())
        self.assertTrue((target / ".agents/skills/swarmstack/SKILL.md").is_file())
        self.assertTrue((target / ".claude/skills/swarmstack/SKILL.md").is_file())
        self.assertEqual(stack.report(target, True)["state"], "setup_required")
        import check
        self.assertEqual(check.link_errors(target), [])
        for name in ["matt-pocock.txt", "i-have-adhd.txt", "pstack.txt"]:
            self.assertTrue((target / ".swarmstack/licenses" / name).is_file())

    def test_setup_configures_installed_skills_then_generic_repeat_refuses_writes(self):
        target = self.install_draft()
        before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
        proposal, _ = update.plan(target, configure=config())
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()})
        result = update.apply(target, proposal["approval_id"], configure=config())
        self.assertEqual(result["state"], "configured")
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertEqual(stack.report(target, True)["state"], "installed")
        self.assertEqual(json.loads((target / ".swarmstack/project.json").read_text()), config())
        with self.assertRaisesRegex(ValueError, "setup already exists"):
            update.plan(target, configure=config())
        hosts = json.loads((target / ".swarmstack/lock.json").read_text())["skill_hosts"]
        self.assertEqual(hosts, ["codex", "claude"])

    def test_installer_preserves_existing_instructions_and_refuses_skill_collision(self):
        target = self.base / "existing"; target.mkdir()
        (target / "AGENTS.md").write_text("existing project rules")
        _, payload = install.build_plan(target)
        bootstrap.apply_plan(target, payload)
        self.assertEqual((target / "AGENTS.md").read_text(), "existing project rules")
        with self.assertRaises(ValueError): install.build_plan(target)
        proposal, _ = update.plan(target, configure=config())
        self.assertTrue(any(c["path"] == "AGENTS.md" for c in proposal["conflicts"]))
        with self.assertRaisesRegex(ValueError, "conflicts"):
            update.apply(target, proposal["approval_id"], configure=config())
        # An explicitly reviewed existing-file integration remains marked as customised.
        proposal, _ = update.plan(target, configure=config(), keep_existing=["AGENTS.md"])
        update.apply(target, proposal["approval_id"], configure=config(), keep_existing=["AGENTS.md"])
        self.assertIn("AGENTS.md", stack.report(target)["modified"])
        self.assertEqual((target / "AGENTS.md").read_text(), "existing project rules")

    def test_inconsistent_or_unknown_phase_is_not_setup_or_update_ready(self):
        path = self.project / ".swarmstack/lock.json"
        original = json.loads(path.read_text())
        for phase in ["installed", "unknown", None]:
            broken = copy.deepcopy(original); broken["phase"] = phase
            path.write_text(json.dumps(broken))
            with self.subTest(phase=phase):
                self.assertEqual(stack.report(self.project)["state"], "incomplete")
                with self.assertRaises(ValueError):
                    update.plan(self.project, configure=config())
                with self.assertRaises(ValueError):
                    update.plan(self.project)
        legacy = copy.deepcopy(original); legacy.pop("phase")
        path.write_text(json.dumps(legacy))
        self.assertEqual(stack.report(self.project)["state"], "installed")

    def test_malformed_draft_config_is_reported_incomplete(self):
        target = self.install_draft()
        path = target / ".swarmstack/project.json"
        draft = json.loads(path.read_text()); draft["swarm"] = None
        path.write_text(json.dumps(draft))
        self.assertEqual(stack.report(target)["state"], "incomplete")

    def test_dirty_source_cannot_install_a_package_that_cannot_be_configured(self):
        target = self.base / "dirty-source-project"; target.mkdir()
        (self.source / "guides/backend.md").write_text("uncommitted changes")
        with self.assertRaisesRegex(ValueError, "clean"):
            install.build_plan(target)
        self.assertEqual(list(target.iterdir()), [])

    def test_setup_requires_confirmed_details_and_same_pinned_source(self):
        target = self.install_draft()
        with self.assertRaises(ValueError):
            update.plan(target)
        draft = json.loads((target / ".swarmstack/project.json").read_text())
        with self.assertRaises(ValueError):
            update.plan(target, configure=draft)
        self.change_source()
        with self.assertRaisesRegex(ValueError, "installed toolkit revision"):
            update.plan(target, configure=config())

    def test_claude_mappings_survive_later_toolkit_update(self):
        target = self.install_draft("claude")
        proposal, _ = update.plan(target, configure=config())
        update.apply(target, proposal["approval_id"], configure=config())
        self.change_source()
        proposal, _ = update.plan(target)
        update.apply(target, proposal["approval_id"])
        self.assertTrue((target / ".claude/skills/swarmstack/SKILL.md").exists())
        self.assertEqual(stack.report(target, True)["state"], "installed")

    def test_install_and_setup_cli_are_distinct(self):
        target = self.base / "cli-project"; target.mkdir()
        command = [sys.executable, str(self.source / "scripts/install.py"), "--target", str(target), "--host", "both"]
        preview = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(list(target.iterdir()), [])
        applied = subprocess.run(command + ["--apply"], capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(stack.report(target)["state"], "setup_required")
        accepted = self.base / "accepted.json"; accepted.write_text(json.dumps(config()))
        setup = [sys.executable, str(self.source / "scripts/update.py"), "--project", str(target), "--configure", str(accepted)]
        preview = subprocess.run(setup, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        approval = json.loads(preview.stdout)["approval_id"]
        applied = subprocess.run(setup + ["--apply", approval], capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual(stack.report(target, True)["phase"], "configured")

    def test_not_installed_and_partial_setup_are_truthful(self):
        empty = self.base / "empty"; empty.mkdir()
        self.assertEqual(stack.report(empty)["state"], "not_installed")
        (empty / ".swarmstack").mkdir()
        self.assertEqual(stack.report(empty)["state"], "incomplete")


if __name__ == "__main__":
    unittest.main()
