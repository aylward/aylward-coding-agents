"""Local execution ledger; no network, scheduler, Git mutation, or AI dependency."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent
REPOS = {
    "core": ROOT.parent / "monai-physio",
    "slicer": ROOT.parent / "monai-physio-slicer",
    "simpleware": ROOT.parent / "monai-physio-simpleware",
}
ROLES = (
    "development-lead",
    "core",
    "slicer",
    "simpleware",
    "testing-ci",
    "scientific-validation",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(repo: Path, *args: str) -> str:
    """Trust only the explicitly selected checkout, for this process only."""
    return subprocess.check_output(
        [
            "git",
            "-c",
            f"safe.directory={repo.resolve().as_posix()}",
            "-C",
            str(repo),
            *args,
        ],
        text=True,
        encoding="utf-8",
    ).strip()


def fingerprint(repo: Path) -> str:
    """Include staged, unstaged and untracked content, excluding Git ignores."""
    state: dict[str, Any] = {
        "head": git(repo, "rev-parse", "HEAD"),
        "diff": hashlib.sha256(
            git(repo, "diff", "HEAD", "--binary").encode()
        ).hexdigest(),
        "untracked": [],
    }
    names = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    for name in sorted(filter(None, names.split("\0"))):
        state["untracked"].append(
            [name, hashlib.sha256((repo / name).read_bytes()).hexdigest()]
        )
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


class Ledger:
    """Serialize task updates and append their audit event in one transaction."""

    def __init__(self, path: Path, initialize: bool = False) -> None:
        self.path = path.resolve()
        if initialize:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        uri = self.path.as_uri() + ("?mode=rwc" if initialize else "?mode=rw")
        self.db = sqlite3.connect(uri, uri=True, timeout=10, isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=10000")
        if initialize:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, source TEXT UNIQUE NOT NULL,
                    payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL,
                    at TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL);
            """)

    def close(self) -> None:
        self.db.close()

    def get(self, task_id: str) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT payload FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Unknown task: {task_id}")
        return json.loads(row[0])

    def all(self) -> list[dict[str, Any]]:
        return [
            json.loads(row[0])
            for row in self.db.execute("SELECT payload FROM tasks ORDER BY id")
        ]

    @contextmanager
    def edit(self, task_id: str, action: str) -> Iterator[dict[str, Any]]:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            task = self.get(task_id)
            yield task
            task["revision"] += 1
            task["updated"] = utc()
            payload = json.dumps(task, sort_keys=True)
            self.db.execute("UPDATE tasks SET payload=? WHERE id=?", (payload, task_id))
            self.db.execute(
                "INSERT INTO events(task,at,action,payload) VALUES(?,?,?,?)",
                (task_id, task["updated"], action, payload),
            )
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def create(
        self,
        source: str,
        title: str,
        role: str,
        repo: Path,
        authorization: str,
        criteria: str,
        allowed: list[str],
        base: str,
        read_only: bool = False,
    ) -> dict[str, Any]:
        if role not in ROLES:
            raise ValueError("Unknown role")
        if not all(x.strip() for x in (source, title, authorization, criteria)):
            raise ValueError("Source, title, authority and criteria are required")
        if not read_only and not allowed:
            raise ValueError("An editing task needs explicit allowed paths")
        task = {
            "id": uuid.uuid4().hex[:12],
            "source": source,
            "title": title,
            "role": role,
            "repo": str(repo.resolve()),
            "authorization": authorization,
            "criteria": criteria,
            "allowed_paths": allowed,
            "read_only": read_only,
            "base": git(repo, "rev-parse", "--verify", base + "^{commit}"),
            "status": "queued",
            "revision": 1,
            "updated": utc(),
            "owner": None,
            "token": None,
            "workspace": None,
            "checks": [],
            "review": None,
            "workers": [],
        }
        payload = json.dumps(task, sort_keys=True)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                "INSERT INTO tasks VALUES(?,?,?)", (task["id"], source, payload)
            )
            self.db.execute(
                "INSERT INTO events(task,at,action,payload) VALUES(?,?,?,?)",
                (task["id"], task["updated"], "create", payload),
            )
        return task

    @staticmethod
    def owned(task: dict[str, Any], token: str) -> None:
        if task["status"] != "running" or task["token"] != token:
            raise ValueError("Task is not running under this claim token")

    def claim(self, task_id: str, owner: str) -> dict[str, Any]:
        if not owner.strip():
            raise ValueError("Supply the actual worker chat/session ID")
        with self.edit(task_id, "claim") as task:
            if task["status"] != "queued":
                raise ValueError("Task must be queued; claims never expire silently")
            workers = task.setdefault(
                "workers", [task["owner"]] if task["owner"] else []
            )
            if owner not in workers:
                workers.append(owner)
            task.update(
                status="running", owner=owner, token=uuid.uuid4().hex, review=None
            )
        return task

    def bind(self, task_id: str, token: str, workspace: Path) -> dict[str, Any]:
        workspace = workspace.resolve()
        with self.edit(task_id, "bind-worktree") as task:
            self.owned(task, token)
            repo = Path(task["repo"])
            common = Path(
                git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
            ).resolve()
            actual = Path(
                git(
                    workspace, "rev-parse", "--path-format=absolute", "--git-common-dir"
                )
            ).resolve()
            if common != actual or workspace == repo.resolve():
                raise ValueError("Use a separate worktree of the assigned repository")
            entries = git(repo, "worktree", "list", "--porcelain")
            paths = [
                Path(line[9:]).resolve()
                for line in entries.splitlines()
                if line.startswith("worktree ")
            ]
            if workspace not in paths:
                raise ValueError("Workspace is not a registered Git worktree")
            if git(workspace, "rev-parse", "HEAD") != task["base"]:
                raise ValueError("Worktree must start at the task's exact base commit")
            for other in self.all():
                if (
                    other["id"] != task_id
                    and other["workspace"] == str(workspace)
                    and other["status"] not in ("completed", "canceled")
                ):
                    raise ValueError("Worktree is already assigned to another task")
            task["workspace"] = str(workspace)
        return task

    def release(
        self, task_id: str, token: str, status: str, evidence: str
    ) -> dict[str, Any]:
        if status not in ("queued", "blocked", "review") or not evidence.strip():
            raise ValueError("Release requires queued/blocked/review and evidence")
        with self.edit(task_id, "release") as task:
            self.owned(task, token)
            if status == "review" and not task["read_only"] and not task["workspace"]:
                raise ValueError("Editing tasks need an isolated worktree")
            task.update(status=status, token=None, handoff=evidence, review=None)
        return task

    def requeue(self, task_id: str, evidence: str) -> dict[str, Any]:
        if not evidence.strip():
            raise ValueError("Record the reason and confirmation that old work stopped")
        with self.edit(task_id, "lead-requeue") as task:
            if task["status"] not in ("blocked", "review"):
                raise ValueError("Release running work before reassignment")
            task.update(status="queued", review=None, handoff=evidence)
        return task

    def check(
        self, task_id: str, token: str, command: list[str], timeout: int = 300
    ) -> dict[str, Any]:
        task = self.get(task_id)
        self.owned(task, token)
        if not command:
            raise ValueError("Supply an explicit command after --")
        if not task["read_only"] and not task["workspace"]:
            raise ValueError("Bind an isolated worktree before executing checks")
        cwd = Path(task["workspace"] or task["repo"])
        before = fingerprint(cwd)
        head_before = git(cwd, "rev-parse", "HEAD")
        started = utc()
        log_dir = self.path.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log = log_dir / f"{task_id}-{uuid.uuid4().hex}.log"
        with log.open("w", encoding="utf-8") as stream:
            try:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    timeout=timeout,
                    shell=False,
                    check=False,
                )
                code = result.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                stream.write(str(exc))
                code = -1
        record = {
            "argv": command,
            "cwd": str(cwd),
            "started": started,
            "ended": utc(),
            "exit_code": code,
            "log": str(log),
            "before": before,
            "after": fingerprint(cwd),
            "head_before": head_before,
            "head_after": git(cwd, "rev-parse", "HEAD"),
        }
        with self.edit(task_id, "check") as task:
            self.owned(task, token)
            task["checks"].append(record)
            task["review"] = None
        return record

    def review(self, task_id: str, reviewer: str, evidence: str) -> dict[str, Any]:
        if not reviewer.strip() or not evidence.strip():
            raise ValueError("Review requires reviewer identity and evidence")
        with self.edit(task_id, "independent-review") as task:
            if task["status"] != "review" or reviewer in task.get(
                "workers", [task["owner"]]
            ):
                raise ValueError("Use a different reviewer session on a review task")
            cwd = Path(task["workspace"] or task["repo"])
            task["review"] = {
                "reviewer": reviewer,
                "evidence": evidence,
                "fingerprint": fingerprint(cwd),
                "head": git(cwd, "rev-parse", "HEAD"),
                "at": utc(),
            }
        return task

    def complete(self, task_id: str, acceptance: str) -> dict[str, Any]:
        if not acceptance.strip():
            raise ValueError("Record the actual user acceptance reference")
        with self.edit(task_id, "user-acceptance") as task:
            if task["status"] != "review" or not task["review"]:
                raise ValueError("Independent review is required")
            current = fingerprint(Path(task["workspace"] or task["repo"]))
            if task["review"]["fingerprint"] != current:
                raise ValueError("Source changed after review")
            checks = task["checks"]
            if not checks or not (
                checks[-1]["exit_code"] == 0
                and checks[-1]["before"] == current
                and checks[-1]["after"] == current
            ):
                raise ValueError("Latest check must pass on unchanged current source")
            task.update(status="completed", acceptance=acceptance)
        return task

    def export(self) -> dict[str, Any]:
        """Omit claim tokens from portable reports; export is not an inbox."""
        tasks = [{k: v for k, v in t.items() if k != "token"} for t in self.all()]
        return {
            "schema_version": 1,
            "generated": utc(),
            "authority": "local execution only",
            "delivery": "not sent; no recipient acknowledgement",
            "tasks": tasks,
        }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "state" / "tasks.sqlite3")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list")
    sub.add_parser("export")
    new = sub.add_parser("new")
    for arg in ("source", "title", "authorization", "criteria", "base"):
        new.add_argument("--" + arg, required=True)
    new.add_argument("--repo", choices=REPOS, required=True)
    new.add_argument("--role", choices=ROLES, required=True)
    new.add_argument("--allow", action="append", default=[])
    new.add_argument("--read-only", action="store_true")
    for action in (
        "show",
        "history",
        "claim",
        "bind",
        "release",
        "requeue",
        "check",
        "review",
        "complete",
    ):
        child = sub.add_parser(action)
        child.add_argument("id")
        if action in ("bind", "release", "check"):
            child.add_argument("--token", required=True)
        if action == "claim":
            child.add_argument("--owner", required=True)
        if action == "bind":
            child.add_argument("--workspace", type=Path, required=True)
        if action in ("release", "requeue", "review"):
            child.add_argument("--evidence", required=True)
        if action == "release":
            child.add_argument(
                "--status", choices=("queued", "blocked", "review"), required=True
            )
        if action == "review":
            child.add_argument("--reviewer", required=True)
        if action == "complete":
            child.add_argument("--acceptance", required=True)
        if action == "check":
            child.add_argument("--timeout", type=int, default=300)
    arguments = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in arguments:
        split = arguments.index("--")
        command = arguments[split + 1 :]
        arguments = arguments[:split]
    args = parser.parse_args(arguments)
    if command and args.action != "check":
        parser.error("Only check accepts a command after --")
    ledger = None
    result: Any
    try:
        ledger = Ledger(args.db, initialize=args.action == "new")
        if args.action == "new":
            result = ledger.create(
                args.source,
                args.title,
                args.role,
                REPOS[args.repo],
                args.authorization,
                args.criteria,
                args.allow,
                args.base,
                args.read_only,
            )
        elif args.action == "list":
            result = ledger.export()["tasks"]
        elif args.action == "export":
            result = ledger.export()
        elif args.action == "show":
            result = ledger.get(args.id)
        elif args.action == "history":
            result = [
                {"seq": r[0], "at": r[1], "action": r[2]}
                for r in ledger.db.execute(
                    "SELECT seq,at,action FROM events WHERE task=? ORDER BY seq",
                    (args.id,),
                )
            ]
        elif args.action == "claim":
            result = ledger.claim(args.id, args.owner)
        elif args.action == "bind":
            result = ledger.bind(args.id, args.token, args.workspace)
        elif args.action == "release":
            result = ledger.release(args.id, args.token, args.status, args.evidence)
        elif args.action == "requeue":
            result = ledger.requeue(args.id, args.evidence)
        elif args.action == "check":
            result = ledger.check(args.id, args.token, command, args.timeout)
        elif args.action == "review":
            result = ledger.review(args.id, args.reviewer, args.evidence)
        else:
            result = ledger.complete(args.id, args.acceptance)
        print(json.dumps(result, indent=2))
        return 1 if args.action == "check" and result["exit_code"] != 0 else 0
    except (ValueError, sqlite3.Error, OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    finally:
        if ledger:
            ledger.close()


if __name__ == "__main__":
    raise SystemExit(main())
