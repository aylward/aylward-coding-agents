"""Exercise ownership races, Git isolation, provenance and acceptance gates."""

import json
import sqlite3
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coordinator import Ledger, fingerprint, git


class CoordinatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory(prefix="monai-dev-team-test-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "--quiet")
        (self.repo / "sample.txt").write_text("original\n", encoding="utf-8")
        git(self.repo, "add", "sample.txt")
        git(
            self.repo,
            "-c",
            "user.name=Local Test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Local temporary fixture",
        )
        self.db = self.root / "state" / "tasks.sqlite3"
        self.ledger = Ledger(self.db, initialize=True)

    def tearDown(self) -> None:
        self.ledger.close()
        self.temp.cleanup()

    def new(self, source: str = "test-1", read_only: bool = True) -> dict:
        return self.ledger.create(
            source,
            "Test scope",
            "core",
            self.repo,
            "Local fixture authorization",
            "Sample is intact",
            ["sample.txt"],
            "HEAD",
            read_only,
        )

    def test_atomic_claim_across_connections(self) -> None:
        task = self.new()

        def claim(owner: str) -> str:
            ledger = Ledger(self.db)
            try:
                ledger.claim(task["id"], owner)
                return "claimed"
            except ValueError:
                return "busy"
            finally:
                ledger.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, ["worker-a", "worker-b"]))
        self.assertCountEqual(results, ["claimed", "busy"])
        self.assertEqual(self.ledger.get(task["id"])["revision"], 2)

    def test_deduplication_and_transaction_rollback(self) -> None:
        task = self.new()
        with self.assertRaises(sqlite3.IntegrityError):
            self.new()
        claim = self.ledger.claim(task["id"], "worker")
        with self.assertRaises(ValueError):
            self.ledger.release(task["id"], "wrong", "review", "attempt")
        self.assertEqual(self.ledger.get(task["id"]), claim)
        self.assertEqual(
            self.ledger.db.execute("SELECT count(*) FROM events").fetchone()[0], 2
        )
        with self.assertRaises(ValueError):
            self.ledger.requeue(task["id"], "Cannot steal live work")

    def test_git_worktree_identity_base_and_double_booking(self) -> None:
        task = self.new(read_only=False)
        claim = self.ledger.claim(task["id"], "worker")
        with self.assertRaises(ValueError):
            self.ledger.bind(task["id"], claim["token"], self.repo)
        tree = self.root / "worktree"
        git(self.repo, "worktree", "add", "--quiet", "--detach", str(tree), "HEAD")
        self.ledger.bind(task["id"], claim["token"], tree)
        other = self.new("test-2", read_only=False)
        other_claim = self.ledger.claim(other["id"], "worker-b")
        with self.assertRaises(ValueError):
            self.ledger.bind(other["id"], other_claim["token"], tree)
        (tree / "sample.txt").write_text("isolated\n", encoding="utf-8")
        self.assertEqual((self.repo / "sample.txt").read_text(), "original\n")

    def test_review_requires_tests_independent_identity_and_current_source(
        self,
    ) -> None:
        task = self.new()
        task_id = task["id"]
        claim = self.ledger.claim(task_id, "worker")
        self.ledger.release(task_id, claim["token"], "review", "Ready for review")
        with self.assertRaises(ValueError):
            self.ledger.review(task_id, "worker", "Self review")
        self.ledger.review(task_id, "reviewer", "Independent evidence")
        with self.assertRaises(ValueError):
            self.ledger.complete(task_id, "No passing check exists")
        self.ledger.requeue(task_id, "Review needs execution evidence; worker stopped")
        claim = self.ledger.claim(task_id, "worker")
        passed = self.ledger.check(
            task_id, claim["token"], [sys.executable, "-c", "print('verified')"]
        )
        self.assertEqual(passed["exit_code"], 0)
        self.ledger.release(task_id, claim["token"], "review", "Check log attached")
        self.ledger.review(task_id, "reviewer", "Reviewed source and exact check log")
        (self.repo / "sample.txt").write_text("changed\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.ledger.complete(task_id, "Must reject source drift")
        (self.repo / "sample.txt").write_text("original\n", encoding="utf-8")
        result = self.ledger.complete(task_id, "Explicit fixture acceptance")
        self.assertEqual(result["status"], "completed")

    def test_failure_timeout_and_source_changing_check_remain_ineligible(self) -> None:
        task = self.new()
        claim = self.ledger.claim(task["id"], "worker")
        failed = self.ledger.check(
            task["id"], claim["token"], [sys.executable, "-c", "raise SystemExit(7)"]
        )
        self.assertEqual(failed["exit_code"], 7)
        timed_out = self.ledger.check(
            task["id"],
            claim["token"],
            [sys.executable, "-c", "import time; time.sleep(2)"],
            timeout=1,
        )
        self.assertEqual(timed_out["exit_code"], -1)
        drifted = self.ledger.check(
            task["id"],
            claim["token"],
            [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('sample.txt').write_text('new')",
            ],
        )
        self.assertNotEqual(drifted["before"], drifted["after"])
        self.ledger.release(task["id"], claim["token"], "review", "Drift recorded")
        self.ledger.review(task["id"], "reviewer", "Review cannot override test drift")
        with self.assertRaises(ValueError):
            self.ledger.complete(task["id"], "Must not accept a source-changing test")

    def test_untracked_content_and_snapshot_token_redaction(self) -> None:
        before = fingerprint(self.repo)
        (self.repo / "extra.txt").write_text("extra", encoding="utf-8")
        self.assertNotEqual(before, fingerprint(self.repo))
        task = self.new()
        self.ledger.claim(task["id"], "worker")
        snapshot = self.ledger.export()
        self.assertNotIn("token", snapshot["tasks"][0])
        self.assertIn("not sent", snapshot["delivery"])

    def test_untracked_filename_and_content_are_unambiguous(self) -> None:
        (self.repo / "a").write_bytes(b"bc")
        first = fingerprint(self.repo)
        (self.repo / "a").unlink()
        (self.repo / "ab").write_bytes(b"c")
        self.assertNotEqual(first, fingerprint(self.repo))

    def test_previous_worker_cannot_review_after_cross_client_handoff(self) -> None:
        task = self.new()
        desktop = self.ledger.claim(task["id"], "desktop-worker")
        self.ledger.release(task["id"], desktop["token"], "queued", "Stopped; handoff")
        cursor = self.ledger.claim(task["id"], "cursor-worker")
        self.ledger.release(task["id"], cursor["token"], "review", "Ready")
        for worker in ("desktop-worker", "cursor-worker"):
            with self.assertRaises(ValueError):
                self.ledger.review(task["id"], worker, "Cannot review own task")
        self.ledger.review(
            task["id"], "independent-reviewer", "Source and logs checked"
        )

    def test_cli_persistence_and_explicit_check_command(self) -> None:
        task = self.new()
        claim = self.ledger.claim(task["id"], "worker")
        script = str(Path(__file__).resolve().parents[1] / "coordinator.py")
        result = subprocess.run(
            [
                sys.executable,
                script,
                "--db",
                str(self.db),
                "check",
                task["id"],
                "--token",
                claim["token"],
                "--",
                sys.executable,
                "-c",
                "print('CLI round trip')",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["exit_code"], 0)
        reopened = Ledger(self.db)
        try:
            self.assertEqual(len(reopened.get(task["id"])["checks"]), 1)
        finally:
            reopened.close()


if __name__ == "__main__":
    unittest.main()
