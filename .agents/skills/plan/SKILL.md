---
name: plan
description: Inspect MONAI-Physio core or Simpleware source files, summarize the current design, and produce a numbered implementation plan with open questions. Does not write code unless explicitly asked.
---

This skill has repository-specific instructions. Use only the section for
the repository being changed; its relative paths and commands are relative
to that repository's root (or its assigned worktree). For a repository
without a section, such as `monai-physio-slicer/`, follow its own README,
AGENTS.md and docs instead.

## Core (`monai-physio/`)

Analyze the following and produce a design plan for the MONAI Physio repository.

Task: $ARGUMENTS

Instructions:
1. Use `graphify query "<question>"` to locate relevant classes and methods, then read those source files.
2. Summarize current behavior in 3–5 bullet points.
3. Produce a numbered implementation plan with enough detail to act on.
4. List every file that will change.
5. Call out any change that breaks the fixed data conventions - an axis
   permutation, an ITK-to-NumPy handoff, or an LPS-to-USD conversion. Do not
   restate the conventions themselves.
6. List open questions that need user input before coding starts.
7. Do not modify any files unless the task explicitly asks you to.

## Simpleware (`monai-physio-simpleware/`)

Analyze the following and produce a design plan for this repo.

Task: $ARGUMENTS

Instructions:
1. Use `docs/API_MAP.md` and Grep to locate relevant code, then read those source files.
2. Summarize current behavior in 3-5 bullet points.
3. Produce a numbered implementation plan with enough detail to act on.
4. List every file that will change, and which sub-project (and venv) each belongs to.
5. Call out risks: the Simpleware-embedded-Python vs venv-subprocess boundary,
   Simpleware API constraints (see `CLAUDE.md`), axis permutations, and
   ITK-to-NumPy handoffs. Do not restate fixed conventions.
6. List open questions that need user input before coding starts.
7. Do not modify any files unless the task explicitly asks you to.
