---
name: impl
description: Read relevant MONAI-Physio core or Simpleware source files, summarize current behavior, propose a brief plan, then implement the requested feature or refactor in small diffs.
---

This skill has repository-specific instructions. Use only the section for
the repository being changed; its relative paths and commands are relative
to that repository's root (or its assigned worktree). For a repository
without a section, such as `monai-physio-slicer/`, follow its own README,
AGENTS.md and docs instead.

## Core (`monai-physio/`)

Implement the following in the MONAI Physio repository:

$ARGUMENTS

Instructions:
1. Use `graphify query "<question>"` to locate relevant files, then read them in full.
2. Summarize current behavior in 2–4 sentences.
3. State the implementation plan in numbered steps. For non-trivial changes, pause and confirm before proceeding.
4. Implement in the smallest reviewable diff possible.
5. Update docstrings and type hints for every changed public method.
6. Run `ruff check . --fix && ruff format .` after editing Python files.
7. Prefer compatibility. Break a public API only when the change is generally
   beneficial to future users, and never via a deprecation shim, removed-symbol
   re-export, or removed-symbol stub - provide a conversion script when the
   change is substantial.
8. Explicitly note any breaking changes introduced, and append an entry for
   each to `docs/developer/migration_next.md` using the template at the bottom
   of that file.
9. Do not add features beyond what was requested.
10. When fixing a bug, fix it. Do not add a comment recording what was wrong,
    what changed, or how it was diagnosed - that belongs in the commit
    message, not the code. Only truly exceptional motivations earn a comment.

## Simpleware (`monai-physio-simpleware/`)

Implement the following in this repo:

$ARGUMENTS

Instructions:
1. Locate relevant files with `docs/API_MAP.md` and Grep, then read them in full.
   Identify which sub-project is touched (`monai_label_module`,
   `export_usd_module`, `restore_labelmap_spatial_information`,
   `recon_4d_module`, `respiratory_motion_module`); each
   has its own venv and dependencies.
2. Summarize current behavior in 2-4 sentences.
3. State the implementation plan in numbered steps. For non-trivial changes, pause and confirm before proceeding.
4. Implement in the smallest reviewable diff possible.
5. Update docstrings and type hints for every changed public function.
6. Run `ruff check <files> --fix && ruff format <files>` on the touched files only.
7. For `monai_label_module` plugins, respect the two-process design: no PyTorch,
   ITK, or network libraries in plugin code; delegate to the module's
   `_*_helper.py`.
   Follow the Simpleware API constraints in `CLAUDE.md`.
8. Prefer compatibility; call out any breaking change (renamed settings keys,
   CLI flags, output layouts) in the summary.
9. Do not add features beyond what was requested.
10. When fixing a bug, fix it. Do not add a comment recording what was wrong or
    how it was diagnosed - that belongs in the commit message.
