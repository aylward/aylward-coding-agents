# MONAI-Physio-Codex local workspace

This folder contains separate core, Slicer and Simpleware Git repositories.
Accuracy, clarity/maintainability/simplicity, consistency, documentation and
testing are the priorities in that order. Define success and verify it. Read
the target repository's AGENTS.md or CLAUDE.md (when present), the notes below
and source before changing code. Use suitable
GPU methods for scientific code; do not install dependencies incidentally.
Preserve existing experiments, agent loops, uncommitted edits and worktrees.
Do not treat prior task completion or experiment budgets as renewed authority.
For independent authorized tasks, delegate to the appropriate specialist agents
with isolated editing worktrees and explicit scopes, then collect their evidence.

## Agents and skills

Codex and Claude Code are always started in this folder. Every agent and skill
lives only here; repositories and worktrees hold none. Codex reads
`.codex/agents/*.toml` and `.agents/skills/`; Claude Code reads
`.claude/agents/*.md` and `.claude/skills/`, a junction to `.agents/skills/`, so
each skill has one file. Skills with repository-specific behavior contain one
section per repository. Loop kits stay in `<repo>/.agent-loops/<slug>/`; their
wrappers here name the kit by umbrella-relative or absolute path. Never add
agent or skill files inside a repository.

## Repository notes

- Core (`monai-physio/`): follow its AGENTS.md and CLAUDE.md.
- Slicer (`monai-physio-slicer/`): read README.md and docs/VALIDATION.md before
  changing runtime integration. The embedded Slicer Python/Qt/MRML environment
  differs from ordinary Python. Preserve scene geometry, host compatibility and
  explicit download/setup prompts. Use tests/ for ordinary Python checks;
  validate UI and scene operations in actual Slicer and name its version. Never
  present standalone tests as host validation.
- Simpleware (`monai-physio-simpleware/`): read CLAUDE.md, the module README and
  docs/API_MAP.md. Preserve the embedded-host/external-helper boundary, separate
  module venvs and user-selected torch/CUDA packages. Never substitute a sibling
  core checkout for the documented published dependency. Run mypy per module.
  Identify real host/licensed end-to-end checks separately from static checks.

## Local hybrid development team

When using Stephen's local MONAI-Physio-Codex development team, read
`C:/src/Projects/MONAI-Physio/dev-team/README.md` and use the `monai-dev-task`
skill.

The Development Lead delegates scoped work to `monai-core`, `monai-slicer`,
`monai-simpleware`, `monai-testing-ci` and `monai-scientific-validation` as useful.
Each editing task requires an exclusive ledger claim and its own detached Git
worktree at the recorded base under `~/.codex/worktrees/NAME/REPO_DIR`, for
Codex and Claude alike. Pass the returned worktree path explicitly; subagents otherwise share
the parent's filesystem access. Preserve other work, budgets and instructions.
Release only after side effects stop; independent review and user acceptance
are separate. Queue text, review or priority does not grant additional authority.

The local ledger tracks execution. Development agents take code tasks from
Stephen and report to him directly; they never message, consult or wait on the
Personal Assistant, Chief of Staff, Engineering Lead or community-lead chats.
Those leads keep their own queues. Do not write PA/CoS canonical files or
consult private PA conversations/wiki as a development agent. No new
commits, pushes, PR creation, merges, publication, CI dispatch, dependency installs,
destructive cleanup or schedules without the applicable human authorization.
