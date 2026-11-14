---
name: monai-slicer
description: Implement and validate a scoped, ledger-claimed MONAI-Physio Slicer module or embedded-runtime change inside an assigned isolated worktree. Requires task ID, claim token and absolute worktree path in the prompt.
---

Follow C:/src/Projects/MONAI-Physio/.agents/skills/monai-dev-task/SKILL.md,
including its Claude Code section. Own only the assigned Slicer worktree (the
absolute path in your prompt) and allowed paths; run every command there and
confirm `git rev-parse --show-toplevel` before editing. Read AGENTS.md,
README.md, docs/VALIDATION.md and the relevant module source before editing.
Preserve scene geometry and world-frame conversions using Slicer's runtime
conventions.

Slicer's embedded Python and Qt/MRML environment differs from standalone
Python. Do not claim module import, UI, sample downloads or end-to-end
validation from ordinary pytest alone. Use existing runtime tests when the
actual host is available; record the Slicer version and exact checks. A static
pass does not validate UI. No setup downloads, dependency replacement,
releases, commits or pushes without explicit authority. Run checks through
`coordinator.py check`, stop side effects, record evidence and release for
independent review.
