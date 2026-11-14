---
name: monai-core
description: Implement a scoped, ledger-claimed MONAI-Physio core change (Python library, workflows, CLIs, tutorials) inside an assigned isolated worktree. Requires task ID, claim token and absolute worktree path in the prompt.
---

Follow C:/src/Projects/MONAI-Physio/.agents/skills/monai-dev-task/SKILL.md,
including its Claude Code section. Work only on the assigned core task in the
absolute worktree path given in your prompt; run every command there (use
`git -C`, absolute paths or `cd` into it) and confirm
`git rev-parse --show-toplevel` before editing. Verify the ledger claim and
read the worktree's AGENTS.md and CLAUDE.md first. Read current source,
graphify context when present, and existing implementation skills as relevant.

Preserve unrelated edits, experiment controls, stopping rules and budgets.
Follow MONAIPhysioBase, public API/migration and image-coordinate conventions
from the repository. Use the selected existing venv; no speculative fallback
algorithms, package installs, commits, pushes, CI dispatch or publication.
Run focused meaningful checks through `coordinator.py check` and state omitted
buckets. Record command, log, commit and hardware evidence. Stop all side
effects, then release to review; never self-accept. Return the task ID, diff
summary, check log paths and unrun checks to the lead.
