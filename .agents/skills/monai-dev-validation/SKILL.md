---
name: monai-dev-validation
description: Independently review MONAI-Physio implementation, test or scientific evidence at an exact revision before a local execution task can be accepted.
---

Read `C:/src/Projects/MONAI-Physio/dev-team/README.md` and the ledger task. Use a
different session from the implementation worker. Review current source and raw
logs independently. Do not treat the worker's narrative as independent evidence.

For CI, inspect existing run/job/artifact evidence at the source SHA. Separate
setup failure from test failure, and skipped from passed buckets. Do not rerun or
dispatch jobs. For local checks use the real repository/host Python, focused
commands, and the task's authorized test buckets. Preserve actual command, cwd,
exit code, log, input data, hardware/version and tolerance provenance.

For scientific work inspect the relevant numerical/physical invariants, reference
baseline, units and transforms, convergence and validation coverage. Passing
unit tests, solver convergence and visual plausibility support different claims.
State unrun GPU, licensed-host, tutorial or end-to-end checks explicitly.

Return findings tied to paths and evidence, with acceptance criteria satisfied
or unmet. If acceptable, record `review --reviewer ACTUAL_SESSION_ID --evidence
REFERENCE`. If deficient, keep it in review or let the lead requeue after the
worker stops. Any subsequent source change invalidates the recorded review.
`complete` requires a real user acceptance reference and a passing current check;
it never grants permission to commit, merge, push or publish.

In Claude Code, run as a fresh `monai-testing-ci` or
`monai-scientific-validation` subagent whose prompt holds only the task ID,
worktree path, criteria and raw evidence paths, never the worker's summary.
Use the reviewer owner label the lead assigned; it must differ from every
worker label on the task.
