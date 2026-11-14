---
name: monai-simpleware
description: Implement a scoped, ledger-claimed MONAI-Physio Simpleware plugin or external Python helper change inside an assigned isolated worktree. Requires task ID, claim token and absolute worktree path in the prompt.
---

Follow C:/src/Projects/MONAI-Physio/.agents/skills/monai-dev-task/SKILL.md,
including its Claude Code section. Own only the assigned Simpleware worktree
(the absolute path in your prompt) and paths; run every command there and
confirm `git rev-parse --show-toplevel` before editing. Read AGENTS.md,
CLAUDE.md, docs/API_MAP.md and module instructions before editing. Preserve
the two-process embedded-host/helper boundary and each module's separate
existing venv. Run mypy per module.

Preserve user-selected torch/CUDA and exact wheel compatibility; do not pin or
replace dependencies as an incidental fix. Do not silently substitute a
sibling core checkout for the module's documented published package. Record
host/version, image direction/origin/spacing, mask/landmark conversions, and
actual end-to-end evidence. Host/licence absence means that check is unrun.
No license workaround, downloads, installs, commits, pushes or publication.
Run checks through `coordinator.py check`, stop side effects, and release to
independent review with reproducible commands and remaining gaps.
