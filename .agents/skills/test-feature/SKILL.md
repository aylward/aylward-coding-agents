---
name: test-feature
description: Plan and write verification for a MONAI-Physio core change (real-data pytest with baselines) or a Simpleware change (manual host checklist, helper CLI and static checks).
---

This skill has repository-specific instructions. Use only the section for
the repository being changed; its relative paths and commands are relative
to that repository's root (or its assigned worktree). For a repository
without a section, such as `monai-physio-slicer/`, follow its own README,
AGENTS.md and docs instead.

## Core (`monai-physio/`)

Write or update tests for the following in MONAI Physio:

$ARGUMENTS

Instructions:
1. Read the implementation file(s) to understand the public interface.
2. Read the existing test file for this module if one exists (e.g. `tests/test_<module>.py`).
3. Propose a test plan: list the behaviors to cover and the inputs each behavior
   needs.
4. **Strongly prefer real (downloaded) test data over synthetic data.** Request
   the session fixtures (`test_directories`, `download_test_data`,
   `test_images`) so the standard test datasets are pulled automatically on
   first use. Real data exercises the production code paths - preprocessing,
   resampling, dtype handling, world-frame metadata - that synthetic toy
   volumes silently bypass. Only fall back to synthetic `itk.Image` or
   `pv.PolyData` inputs when:
     - the behavior under test is a pure unit (e.g. axis arithmetic, dict
       routing) where real data adds no signal, or
     - real data would push the test into a slow / GPU / Simpleware bucket
       that doesn't fit the test's purpose.
   When using synthetic inputs anyway, keep volumes ≤64 voxels per side and
   say so in the docstring.
5. **When a test produces an image or surface as output, compare against a
   baseline** using the `process_tests.py` utilities (e.g. `ProcessTests`) rather
   than ad-hoc value assertions. Store baselines under `tests/baselines/`
   (Git LFS-tracked). Run with `--create-baselines` to materialize missing
   baselines on first use; afterward, regression compares to the stored
   baseline. This catches drift that hand-written numeric thresholds miss.
6. Do not restate ITK shape, axis order, or world frame in test docstrings -
   those are fixed conventions. State only what is specific to the test, such
   as the size of a synthetic volume.
7. Mark tests that need a GPU, a slow runtime, or a licensed Simpleware
   install with `@pytest.mark.requires_gpu`, `@pytest.mark.slow`, or
   `@pytest.mark.requires_simpleware` so they fall into the right opt-in
   bucket (`--run-gpu`, `--run-slow`, `--run-simpleware`). Tests that just
   need downloadable data need **no** marker - the fixture chain handles it.
8. Show the exact command to run the new tests, including any opt-in flags
   the markers require. Examples:
   - `py -m pytest tests/test_<module>.py -v`
   - `py -m pytest tests/test_<module>.py -v --run-slow`
   - `py -m pytest tests/test_<module>.py -v --run-gpu --run-slow`
   - `py -m pytest tests/test_<module>.py --create-baselines` (first run, to
     materialize new baselines)

## Simpleware (`monai-physio-simpleware/`)

Plan verification for the following in this repo:

$ARGUMENTS

This repo has no pytest suite and no test fixtures (see `CLAUDE.md`).
Do not invent a `tests/` tree unless the user explicitly asks for one.

Instructions:
1. Read the implementation file(s) to understand the public interface.
2. Classify the change:
   - **Simpleware plugin** (`monai_label_module`): write a manual checklist of
     ribbon actions to run in ScanIP (Configure, Launch/Verify Server,
     Fetch and Infer, Submit and Train, Download Bundle), the expected result of
     each, and what to check in `%TEMP%/monailabel_server_state.json` or logs.
   - **Venv-side helper** (`_*_helper.py`): give the exact
     `<module_dir>/venv/Scripts/python.exe _<name>_helper.py ...`
     invocation and the JSON keys expected on stdout.
   - **Long-running helper** (`respiratory_motion_module`,
     `recon_4d_module`): give the exact helper command to run on a
     small input and what output to inspect.
3. Run the static checks that do exist: `ruff check`, `ruff format --check`,
   and `mypy` on the touched sub-project.
4. If the user does want automated tests, propose a pytest layout for pure
   (non-Simpleware, non-GPU) logic first and confirm before creating files.
