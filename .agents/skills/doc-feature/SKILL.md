---
name: doc-feature
description: Inspect changed MONAI-Physio core or Simpleware code and existing docstrings, update docstrings and inline comments to match current behavior, and refresh the repository's API catalog or knowledge graph when public APIs changed.
---

This skill has repository-specific instructions. Use only the section for
the repository being changed; its relative paths and commands are relative
to that repository's root (or its assigned worktree). For a repository
without a section, such as `monai-physio-slicer/`, follow its own README,
AGENTS.md and docs instead.

## Core (`monai-physio/`)

Update documentation for the following in MONAI Physio:

$ARGUMENTS

Instructions:
1. Read the changed source file(s) in full.
2. Read existing docstrings for every public method or class that changed.
3. Update docstrings to reflect current behavior using NumPy docstring style.
   Do not restate ITK shape, axis order, or world space - those are fixed
   project conventions. Document only real deviations from them.
4. Add inline comments only for non-obvious logic (coordinate transforms, shape permutations).
5. Do not create new `.md` files unless explicitly asked.
6. After any public API change - a signature, public behavior, or a public
   attribute - refresh the knowledge graph: `graphify update .`
7. Do not paraphrase the method name as the docstring - explain what it does and why.

## Simpleware (`monai-physio-simpleware/`)

Update documentation for the following in this repo:

$ARGUMENTS

Instructions:
1. Read the changed source file(s) in full.
2. Read existing docstrings for every public function or class that changed.
3. Update docstrings to reflect current behavior using NumPy docstring style.
   Do not restate ITK shape, axis order, or world space - document only real
   deviations (e.g. a NumPy array with reversed axes, or a Simpleware
   coordinate quirk).
4. Add inline comments only for non-obvious logic (coordinate transforms,
   shape permutations, Simpleware API workarounds).
5. Do not create new `.md` files unless explicitly asked.
6. After any public API change - a signature, public behavior, or a public
   attribute - regenerate `docs/API_MAP.md` (`py utils/generate_api_map.py`).
   If that script is not present, say so and edit the affected entries by hand.
   Update `CLAUDE.md` only for architecture or workflow changes.
7. Do not paraphrase the function name as the docstring - explain what it does
   and why.
