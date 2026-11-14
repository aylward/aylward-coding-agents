---
name: check-conventions
description: Audit changed files (or a given path) against the hard project rules of the MONAI-Physio core or Simpleware repository. Reports violations without auto-fixing.
---

This skill has repository-specific instructions. Use only the section for
the repository being changed; its relative paths and commands are relative
to that repository's root (or its assigned worktree). For a repository
without a section, such as `monai-physio-slicer/`, follow its own README,
AGENTS.md and docs instead.

## Core (`monai-physio/`)

Audit MONAI Physio source for hard-rule violations.

$ARGUMENTS

By default, audit every Python file modified since `HEAD`. If $ARGUMENTS names
specific files or directories, audit those instead.

### Determine the file set

```powershell
# Default: changed, non-deleted .py files since HEAD
git diff --diff-filter=d --name-only HEAD -- '*.py'
```

If a path was passed in $ARGUMENTS, expand it to all `.py` files under that
path (recursively). Skip files that no longer exist on disk.

### Rules to check

For each file, read the **entire file** (rules below depend on surrounding
context such as class inheritance), then flag every occurrence of:

#### Base class and logging
- [ ] A class that orchestrates workflow / segmentation / registration / USD
      conversion but does **not** inherit from `MONAIPhysioBase`.
- [ ] A `print(` call inside the body of a class that inherits from
      `MONAIPhysioBase` (it must use `self.log_info()` / `self.log_debug()`).
      Standalone scripts and helper / data-container classes may use `print()`.

#### USD / coordinate conventions
- [ ] An `import` of `monai_physio.vtk_to_usd` (or `from ... vtk_to_usd ...`)
      from a file that is **not** `src/monai_physio/convert_vtk_to_usd.py`
      and is **not** itself inside `src/monai_physio/vtk_to_usd/`.
      Experiments, CLIs, tests, and tutorials must use `ConvertVTKToUSD`.
- [ ] A docstring or comment claiming PyVista surfaces are in **RAS** - they
      are in **LPS** internally; convert to USD Y-up only at export.

#### Windows multiprocessing
- [ ] A module-level instantiation of `SegmentChestTotalSegmentator` (or a
      module-level call into it) that is not guarded by
      `if __name__ == "__main__":`. Required on Windows because
      `torch.multiprocessing` re-imports the module in child workers.

#### Code style
- [ ] `X | None` in a type hint (use `Optional[X]`; ruff `UP007` is suppressed).
- [ ] `Any` in a public signature without a comment explaining why.
- [ ] A docstring delimited with `'''` (use `"""`).
- [ ] A string literal using `'...'` (use `"..."`; ruff `flake8-quotes` sets
      `inline-quotes = "double"`).
- [ ] A line longer than 88 characters.
- [ ] An emoji or other non-ASCII glyph inside a `.py` file (Windows cp1252
      encoding has broken builds; keep emojis out of source).

#### Public API hygiene
- [ ] A public method (no leading underscore) without a NumPy-style docstring.
- [ ] A docstring or comment that restates the fixed ITK shape, axis order, or
      LPS world space - flag it even when it also documents what the parameter
      or return value means. Only genuine deviations from the conventions in
      `CLAUDE.md` may be documented.
- [ ] A comment that narrates a bug fix's history instead of the code itself -
      what was wrong, what changed, or how it was diagnosed. That belongs in
      the commit message. Flag it unless the motivation is truly exceptional
      (a non-obvious constraint a future editor would otherwise reintroduce).

#### Migration guide
- [ ] A deprecation shim, removed-symbol re-export, or removed-symbol stub
      kept solely for backward compatibility. Break the API instead, and ship
      a conversion script when the break is substantial.
- [ ] A public class, method, CLI flag, or signature that the diff renames,
      removes, or changes, with no matching entry in
      `docs/developer/migration_next.md`. The entry may record `None needed`
      for the conversion script when the break is not substantial. Report the
      missing entry against the changed line.

### Output

Group findings by file. For each finding, print:

```text
<path>:<line>  <rule short name>  <one-line excerpt>
```

End with a one-line summary: total findings per rule category.

Do **not** auto-fix. The point is to surface violations the user can decide
how to address. If `$ARGUMENTS` includes `--fix`, ask before mutating anything
and limit fixes to the trivially mechanical rules (line length is not one of
them - `ruff format` covers that).

## Simpleware (`monai-physio-simpleware/`)

Audit source for hard-rule violations.

$ARGUMENTS

By default, audit every Python file modified since `HEAD`. If $ARGUMENTS names
specific files or directories, audit those instead.

### Determine the file set

```powershell
git diff --diff-filter=d --name-only HEAD -- '*.py'
```

If a path was passed in $ARGUMENTS, expand it to all `.py` files under that
path (recursively). Skip files that no longer exist on disk.

### Rules to check

Read the **entire file** for each, then flag every occurrence of:

#### Simpleware plugins (every module, excluding the `_*_helper.py` files)
- [ ] An import of `torch`, `itk`, `monai`, `monailabel`, `requests`, or other
      heavy/network libs in plugin code. Plugins run in Simpleware's embedded
      Python; this work belongs in the module's `_*_helper.py` via `subprocess`.
- [ ] `app.ImportNiftiImage()` without first closing an open document
      (`existing.Close()`) - only one document may be open.
- [ ] `doc.RemoveBackground(bg)` or `mask.SetName(name)` with a single argument
      (both need a second arg), `app.LogMessage`, or an `Image` class use.
- [ ] A masks-from-labelmap path using Threshold instead of
      `doc.CreateMasksFromPresegmentedData`.
- [ ] A hard-coded venv path other than `<module_dir>/venv/Scripts/python.exe`,
      or a settings key not in `_settings.py` (`module_dir`, `studies_dir`,
      `model`, `server_address`, `server_port`).
- [ ] A helper subcommand result not emitted as a single JSON object on stdout.

#### Code style
- [ ] A missing type hint (mypy is strict with `disallow_untyped_defs`).
- [ ] `Any` in a public signature without a comment explaining why.
- [ ] A line longer than 88 characters.
- [ ] An emoji or other non-ASCII glyph in a `.py` file (Windows cp1252 issues).
- [ ] `os.system` or `subprocess` without `check=True`/explicit return-code handling.
- [ ] A hard-coded absolute data path (e.g. `D:/data/...`) outside a
      CLI default or documented constant.

#### Public API hygiene
- [ ] A public function/class without a NumPy-style docstring.
- [ ] A docstring or comment that restates fixed ITK shape / axis order / world
      space conventions. Only real deviations may be documented.
- [ ] A comment narrating a bug fix's history rather than the code itself.
- [ ] A reference to the old `physiomotion4d` package or PhysioMotion4D name
      (now `monai_physio` / MONAI-Physio), or a git/sibling-path source for
      `monai-physio` or `unigradicon` in a pyproject.toml (use PyPI releases).
- [ ] A plugin module name that is not unique across modules (e.g. a new
      `_settings.py`; only monai_label_module keeps that name).
- [ ] A public API change with `docs/API_MAP.md` not refreshed.

### Output

Group findings by file. For each finding print:

```text
<path>:<line>  <rule short name>  <one-line excerpt>
```

End with a one-line summary: total findings per rule category.

Do **not** auto-fix. If `$ARGUMENTS` includes `--fix`, ask before mutating
anything and limit fixes to trivially mechanical rules.
