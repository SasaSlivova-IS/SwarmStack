import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bootstrap, rank, checks = (load(name) for name in ["bootstrap", "model_frontier", "check"])


def config():
    c = json.loads((ROOT / "templates/project.example.json").read_text())
    c.update(status="confirmed", name="Pilot", goal="Make a checkable tool", success="A user sees the intended output", github_repository="example/pilot", test_environment="Disposable temporary fixture")
    c["commands"]["test"] = "python3 -m unittest"
    for m in c["models"].values():
        m.update(provider="fixture-provider", model="fixture-model", effort="medium")
    return c


class Adoption(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.target = self.base / "project"
        self.target.mkdir()

    def invoke(self, c, *extra):
        path = self.base / "confirmed.json"
        path.write_text(json.dumps(c))
        return subprocess.run([sys.executable, str(ROOT / "scripts/bootstrap.py"), "--target", str(self.target), "--config", str(path), *extra], capture_output=True, text=True)

    def test_preview_is_read_only(self):
        result = self.invoke(config())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"mode": "preview"', result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_has_complete_local_links_and_hashed_outputs(self):
        result = self.invoke(config(), "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Working on Pilot", (self.target / "AGENTS.md").read_text())
        self.assertEqual(checks.link_errors(self.target), [])
        lock = json.loads((self.target / ".swarmstack/lock.json").read_text())
        for name, digest in lock["files"].items():
            self.assertEqual(hashlib.sha256((self.target / name).read_bytes()).hexdigest(), digest)
        self.assertFalse(any(config()["authority"].values()))
        self.assertEqual(json.loads((self.target / ".swarmstack/project.json").read_text()), config())

    def test_existing_agents_is_preserved_and_no_partial_setup(self):
        (self.target / "AGENTS.md").write_text("existing authority")
        result = self.invoke(config(), "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "existing authority")
        self.assertEqual(len(list(self.target.iterdir())), 1)

    def test_repeated_apply_refuses_without_modification(self):
        self.assertEqual(self.invoke(config(), "--apply").returncode, 0)
        files = {p: p.read_bytes() for p in self.target.rglob("*") if p.is_file()}
        self.assertNotEqual(self.invoke(config(), "--apply").returncode, 0)
        self.assertTrue(all(p.read_bytes() == data for p, data in files.items()))

    def test_draft_and_unresolved_values_refuse(self):
        for field, value in [("status", "draft"), ("name", "REPLACE_WITH_NAME")]:
            with self.subTest(field=field):
                c = config(); c[field] = value
                self.assertNotEqual(self.invoke(c, "--apply").returncode, 0)
                self.assertEqual(list(self.target.iterdir()), [])

    def test_outside_paths_and_fake_boolean_grants_refuse(self):
        for field, value in [("requirements_path", "../outside.md"), ("glossary_path", "C:\\outside.md")]:
            c = config(); c[field] = value
            with self.assertRaises(ValueError):
                bootstrap.build_plan(self.target, c)
        c = config(); c["authority"]["deploy"] = "false"
        with self.assertRaises(ValueError):
            bootstrap.build_plan(self.target, c)

    def test_symlink_target_and_parent_refuse(self):
        link = self.base / "link"
        link.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(ValueError):
            bootstrap.build_plan(link, config())
        outside = self.base / "outside"; outside.mkdir()
        (self.target / ".github").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            bootstrap.build_plan(self.target, config())
        self.assertEqual(list(outside.iterdir()), [])

    def test_toolkit_target_refuses(self):
        with self.assertRaises(ValueError):
            bootstrap.build_plan(ROOT, config())

    def test_configured_commands_are_never_executed(self):
        c = config()
        sentinel = self.base / "must-not-exist"
        c["commands"]["test"] = "touch " + str(sentinel)
        self.assertEqual(self.invoke(c, "--apply").returncode, 0)
        self.assertFalse(sentinel.exists())

    def test_partial_write_reports_created_but_not_completed_file(self):
        original_open = Path.open
        class PartialWriter:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                self.stream.__enter__()
                return self
            def write(self, data):
                self.stream.write(data[:2])
                self.stream.flush()
                raise OSError("injected disk-full write failure")
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
        def interrupted_open(path, *args, **kwargs):
            return PartialWriter(original_open(path, *args, **kwargs))
        with mock.patch.object(Path, "open", interrupted_open):
            with self.assertRaises(RuntimeError) as result:
                bootstrap.apply_plan(self.target, {"partial.txt": b"complete bytes"})
        self.assertEqual((self.target / "partial.txt").read_bytes(), b"co")
        self.assertIn('"created": ["partial.txt"]', str(result.exception))
        self.assertIn('"completed": []', str(result.exception))

    def test_existing_skill_refuses_before_writes(self):
        d = self.target / ".agents/skills/code-review"; d.mkdir(parents=True)
        (d / "SKILL.md").write_text("preserved skill")
        self.assertNotEqual(self.invoke(config(), "--apply").returncode, 0)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertEqual((d / "SKILL.md").read_text(), "preserved skill")


class Frontier(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/models.illustrative.json").read_text())

    def test_tradeoffs_survive_and_dominated_option_does_not(self):
        result = rank.frontier(self.data, True)
        self.assertEqual(set(result["frontier"]), {"cheap", "balanced", "strong"})
        self.assertEqual(result["dominated"], ["dominated"])
        self.assertEqual(result["unknown"], ["unknown"])

    def test_identical_measurements_do_not_dominate_each_other(self):
        row = copy.deepcopy(self.data["configurations"][0]); row["id"] = "equal"
        self.data["configurations"].append(row)
        self.assertIn("equal", rank.frontier(self.data, True)["frontier"])

    def test_illustrative_requires_opt_in(self):
        with self.assertRaises(ValueError):
            rank.frontier(self.data)

    def test_mixed_cohorts_and_nonfinite_cost_refuse(self):
        for key, value in [("cohort", "incomparable"), ("cost_per_task_usd", float("nan"))]:
            data = copy.deepcopy(self.data); data["configurations"][0][key] = value
            with self.assertRaises(ValueError):
                rank.frontier(data, True)


if __name__ == "__main__":
    unittest.main()
