import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("swarm", ROOT / "scripts/swarm.py")
swarm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(swarm)


class Swarm(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name).resolve() / "project"
        folder = self.project / ".swarmstack"; folder.mkdir(parents=True)
        self.config = {"schema_version": 1, "status": "confirmed", "github_repository": "example/project", "swarm": {"host": "manual", "orchestrator": "fixture-root", "direction_cooldown_seconds": 18000, "status_ttl_seconds": 60}}
        self.save_config()

    def save_config(self):
        (self.project / ".swarmstack/project.json").write_text(json.dumps(self.config), encoding="utf-8")

    def call(self, action, *args, now=1000):
        gate = swarm.Gate(self.project, now=now)
        try:
            result = getattr(gate, action)(*args)
            gate.close()
            return result
        except Exception:
            gate.close(False)
            raise

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/swarm.py"), "--project", str(self.project), *args], capture_output=True, text=True, timeout=10, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        return result.returncode, json.loads(result.stdout)

    def apply(self, command="/swarm backend", request="message1", now=1000):
        offered = self.call("request", command, request, now=now)
        self.call("receipt", offered["command_id"], "delivered", "host-message-" + request, now=now + 1)
        self.call("receipt", offered["command_id"], "applied", now=now + 2)
        return offered

    def test_direction_delivery_does_not_start_cooldown(self):
        offered = self.call("request", "/swarm backend", "message1")
        self.assertEqual((offered["status"], offered["route"]), ("ALLOW", "queue"))
        self.call("receipt", offered["command_id"], "delivered", "real-host-message")
        gate = swarm.Gate(self.project, now=1001)
        self.assertIsNone(gate.get("active_direction")); self.assertEqual(gate.get("eligible_at", 0), 0); gate.close()
        self.assertEqual(self.call("request", "/swarm frontend", "message2", now=1001)["status"], "DEFER")

    def test_five_hours_starts_at_application_and_latest_pending_wins(self):
        self.apply()
        self.assertEqual(self.call("request", "/swarm frontend", "message2", now=1003)["status"], "DEFER")
        self.assertEqual(self.call("request", "/swarm auto", "message3", now=1004)["status"], "DEFER")
        self.assertEqual(self.call("next", now=19001)["status"], "DEFER")
        due = self.call("next", now=19002)
        self.assertEqual((due["status"], due["target"]), ("ALLOW", "auto"))
        self.assertEqual(self.call("next", now=19003)["status"], "EMPTY")

    def test_returning_to_active_direction_cancels_unsent_other_direction(self):
        self.apply()
        self.call("request", "/swarm frontend", "message2", now=1003)
        self.assertEqual(self.call("request", "/swarm backend", "message3", now=1004)["status"], "ALREADY_ACTIVE")
        self.assertEqual(self.call("next", now=20000)["status"], "EMPTY")

    def test_repeated_inflight_direction_does_not_relay_after_first_application(self):
        first = self.call("request", "/swarm backend", "first")
        self.assertEqual(self.call("request", "/swarm backend", "repeat", now=1001)["status"], "DEFER")
        self.call("receipt", first["command_id"], "delivered", "host", now=1002)
        self.call("receipt", first["command_id"], "applied", now=1003)
        result = self.call("next", now=19004)
        self.assertEqual((result["status"], result["route"]), ("ALREADY_ACTIVE", "none"))
        self.assertEqual(self.call("next", now=19005)["status"], "EMPTY")

    def test_applied_receipt_is_idempotent_and_does_not_extend_window(self):
        offered = self.apply()
        self.assertEqual(self.call("receipt", offered["command_id"], "applied", now=2000)["status"], "ALREADY_RECORDED")
        result = self.call("request", "/swarm frontend", "message2", now=19002)
        self.assertEqual(result["status"], "ALLOW")

    def test_cannot_apply_before_delivery_or_change_receipt_identity(self):
        offered = self.call("request", "/swarm backend", "message1")
        with self.assertRaises(ValueError): self.call("receipt", offered["command_id"], "applied")
        self.call("receipt", offered["command_id"], "delivered", "real-id")
        with self.assertRaises(ValueError): self.call("receipt", offered["command_id"], "delivered", "other-id")

    def test_request_id_cannot_be_rebound(self):
        self.call("request", "/swarm backend", "message1")
        with self.assertRaises(ValueError): self.call("request", "/swarm frontend", "message1")

    def test_noop_and_report_request_ids_remain_bound_after_restart(self):
        self.apply()
        self.assertEqual(self.call("request", "/swarm backend", "noop", now=1003)["status"], "ALREADY_ACTIVE")
        with self.assertRaises(ValueError): self.call("request", "/swarm frontend", "noop", now=1004)
        self.call("request", "/swarm status", "report", now=1005)
        with self.assertRaises(ValueError): self.call("request", "/swarm auto", "report", now=1006)

    def test_uncertain_delivery_holds_next_and_verified_failure_releases(self):
        offered = self.call("request", "/swarm backend", "message1")
        self.call("receipt", offered["command_id"], "uncertain")
        self.assertEqual(self.call("request", "/swarm frontend", "message2")["status"], "DEFER")
        self.call("receipt", offered["command_id"], "failed")
        self.assertEqual(self.call("next")["target"], "frontend")

    def test_pause_bypasses_window_and_blocks_directions_until_actual_resume(self):
        self.apply()
        pause = self.call("request", "/swarm pause", "pause", now=1003)
        self.assertEqual((pause["status"], pause["route"]), ("ALLOW", "steer"))
        self.assertEqual(self.call("request", "/swarm auto", "auto", now=20000)["status"], "DEFER")
        resume = self.call("request", "/swarm resume", "resume", now=20001)
        self.assertEqual(resume["route"], "wake_or_queue")
        self.assertEqual(self.call("next", now=20002)["status"], "DEFER")
        self.call("receipt", resume["command_id"], "delivered", "resume-host", now=20003)
        self.call("receipt", resume["command_id"], "applied", now=20004)
        self.assertEqual(self.call("next", now=20005)["status"], "ALLOW")

    def test_late_old_pause_receipt_does_not_overwrite_new_resume_intent(self):
        pause = self.call("request", "/swarm pause", "pause")
        resume = self.call("request", "/swarm resume", "resume", now=1001)
        self.call("receipt", resume["command_id"], "delivered", "resume-host", now=1002)
        self.call("receipt", resume["command_id"], "applied", now=1003)
        self.call("receipt", pause["command_id"], "delivered", "pause-host", now=1004)
        self.call("receipt", pause["command_id"], "applied", now=1005)
        self.assertEqual(self.call("request", "/swarm backend", "direction", now=1006)["status"], "ALLOW")

    def test_status_is_read_only_to_host_and_cached_with_expiry(self):
        self.assertEqual(self.call("request", "/swarm status", "status")["status"], "READ")
        self.call("cache", "status", {"actual": "snapshot"})
        cached = self.call("request", "/swarm status", "status2", now=1059)
        self.assertEqual((cached["status"], cached["payload"], cached["observed_at"]), ("CACHED", {"actual": "snapshot"}, 1000))
        self.assertEqual(self.call("request", "/swarm status", "status3", now=1060)["status"], "READ")

    def test_meaningful_applied_change_invalidates_reports(self):
        self.call("cache", "blockers", {"pending": []})
        self.apply(now=1001)
        self.assertEqual(self.call("request", "/swarm blockers", "report", now=1004)["status"], "READ")

    def test_issue_links_are_normalized_and_cross_project_urls_refuse(self):
        url = "https://github.com/example/project/issues/42/?x=1#issuecomment-9"
        result = self.call("request", "/swarm " + url, "link")
        self.assertEqual(result["target"], "https://github.com/example/project/issues/42")
        for value in ["42", "#42", "https://github.com/other/project/issues/42", "https://github.com/example/project/pull/42", "https://evil.test/example/project/issues/42", "https://name@github.com/example/project/issues/42"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError): self.call("request", "/swarm " + value, "bad")

    def test_pause_still_routes_when_database_is_corrupt(self):
        local = self.project / ".swarmstack/local"; local.mkdir()
        (local / "swarm.sqlite3").write_bytes(b"corrupt SQLite fixture")
        rc, result = self.cli("request", "/swarm pause", "--request-id", "pause")
        self.assertEqual((rc, result["status"], result["route"], result["persisted"]), (0, "ALLOW", "steer", False))
        self.assertEqual(result["orchestrator"], "fixture-root")

    def test_whitespace_pause_preserves_unavailable_state_fallback(self):
        local = self.project / ".swarmstack/local"; local.mkdir()
        (local / "swarm.sqlite3").write_bytes(b"corrupt fixture")
        for command in ["/swarm   pause", "/swarm\tpause"]:
            with self.subTest(command=command):
                rc, result = self.cli("request", command, "--request-id", "pause")
                self.assertEqual((rc, result["status"], result["route"]), (0, "ALLOW", "steer"))
                self.assertFalse(result["persisted"])

    def test_pause_still_routes_while_another_process_owns_the_sqlite_lock(self):
        self.call("request", "/swarm status", "init")
        db = sqlite3.connect(str(self.project / ".swarmstack/local/swarm.sqlite3"), isolation_level=None)
        self.addCleanup(db.close); db.execute("BEGIN IMMEDIATE")
        rc, result = self.cli("request", "/swarm pause", "--request-id", "pause")
        self.assertEqual((rc, result["status"], result["persisted"]), (0, "ALLOW", False))

    def test_new_processes_retain_delivery_and_cooldown(self):
        rc, offered = self.cli("request", "/swarm backend", "--request-id", "original")
        self.assertEqual((rc, offered["status"]), (0, "ALLOW"))
        self.cli("receipt", offered["command_id"], "delivered", "--external-id", "host")
        self.cli("receipt", offered["command_id"], "applied")
        self.assertEqual(self.cli("request", "/swarm backend", "--request-id", "again")[1]["status"], "ALREADY_ACTIVE")
        self.assertEqual(self.cli("request", "/swarm frontend", "--request-id", "new")[1]["status"], "DEFER")
        self.assertEqual(self.cli("request", "/swarm backend", "--request-id", "original")[1]["status"], "ALREADY_RECORDED")

    def test_atomic_claim_prevents_duplicate_concurrent_delivery(self):
        self.call("request", "/swarm status", "init")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.cli("request", "/swarm backend", "--request-id", "same"), range(2)))
        self.assertEqual(sorted(r[1]["status"] for r in results), ["ALLOW", "ALREADY_RECORDED"])
        self.assertEqual(len({r[1]["command_id"] for r in results}), 1)

    def test_exited_sender_reuses_original_key_and_does_not_offer_again(self):
        offered = self.cli("request", "/swarm backend", "--request-id", "original")[1]
        # The first process exited without a receipt, as after a crash at relay.
        later = self.cli("request", "/swarm backend", "--request-id", "original")[1]
        self.assertEqual(later["status"], "ALREADY_RECORDED")
        self.assertEqual(later["transport_key"], offered["transport_key"])
        self.assertEqual(self.cli("request", "/swarm frontend", "--request-id", "new")[1]["status"], "DEFER")

    def test_abrupt_process_exit_preserves_committed_offer(self):
        code = "import sys,os;sys.path.insert(0,sys.argv[1]);import swarm;g=swarm.Gate(sys.argv[2]);g.request('/swarm backend','crash');g.db.commit();os._exit(77)"
        result = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts"), str(self.project)], timeout=10)
        self.assertEqual(result.returncode, 77)
        after = self.cli("request", "/swarm backend", "--request-id", "crash")[1]
        self.assertEqual((after["status"], after["state"]), ("ALREADY_RECORDED", "offered"))

    def test_abrupt_exit_before_commit_rolls_back_without_duplicate_claim(self):
        code = "import sys,os;sys.path.insert(0,sys.argv[1]);import swarm;g=swarm.Gate(sys.argv[2]);g.request('/swarm backend','crash');os._exit(78)"
        result = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts"), str(self.project)], timeout=10)
        self.assertEqual(result.returncode, 78)
        after = self.cli("request", "/swarm backend", "--request-id", "crash")[1]
        self.assertEqual(after["status"], "ALLOW")
        self.assertEqual(self.cli("request", "/swarm backend", "--request-id", "crash")[1]["status"], "ALREADY_RECORDED")

    def test_minimum_cooldown_and_binding_are_checked(self):
        self.config["swarm"]["direction_cooldown_seconds"] = 17999; self.save_config()
        with self.assertRaises(ValueError): self.call("next")
        self.config["swarm"]["direction_cooldown_seconds"] = 18000; self.save_config(); self.call("next")
        self.config["swarm"]["orchestrator"] = "another-root"; self.save_config()
        with self.assertRaises(ValueError): self.call("next")

    def test_clock_rollback_defers_and_does_not_reuse_old_cache(self):
        self.call("cache", "status", {"ok": True}, now=2000)
        self.assertEqual(self.call("request", "/swarm status", "read", now=1000)["status"], "READ")
        self.assertEqual(self.call("request", "/swarm backend", "direction", now=1000)["status"], "DEFER")

    def test_project_path_with_spaces_and_unicode_works_without_shell_interpolation(self):
        renamed = self.project.with_name("project with spaces é")
        self.project.rename(renamed); self.project = renamed
        rc, result = self.cli("request", "/swarm backend", "--request-id", "unicode")
        self.assertEqual((rc, result["status"]), (0, "ALLOW"))

    def test_symlinked_state_is_not_followed(self):
        local = self.project / ".swarmstack/local"; target = self.project / "outside"; target.mkdir()
        try: local.symlink_to(target, target_is_directory=True)
        except OSError as exc: self.skipTest("host cannot create symlink fixture: " + str(exc))
        self.assertEqual(self.cli("request", "/swarm backend", "--request-id", "bad")[1]["status"], "ERROR")
        self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
