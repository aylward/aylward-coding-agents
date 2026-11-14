# MONAI-Physio-Codex development team

This is the local execution layer for Stephen Aylward's hybrid development team.
The Desktop project `MONAI-Physio-Codex` uses `C:\src\Projects\MONAI-Physio`.
The separately listed ChatGPT project with that name is a different project.
Role identities and tasks persist as files and a local SQLite database. Codex
starts execution sessions on demand; nothing here installs a background service.

## Start from the desktop

In the local **MONAI-Physio-Codex** project, ask:

> Act as Development Lead. Use monai-dev-task. [Describe the requested change.]
> Record measurable success criteria and authorized paths. Delegate useful
> independent work to the specialist agents in isolated worktrees, run checks,
> obtain independent review, and report for my acceptance. Do not commit or push.

Before preparing a MONAI-Physio commit, read `COMMIT-MESSAGE-FORMAT.txt` in this
directory. Stephen requires its prefixed title and complete body/checklist format;
mark checks complete only with actual evidence and name unrun checks explicitly.

## Action-only tasks and reports

Stephen's November 11, 2026 action-only policy, copied in full to
`ACTION-ONLY-POLICY.txt` in this folder, applies to the Development Lead and every specialist through this shared guide.
It supersedes conflicting older task presentation and completion-evidence rules.

- Record only concrete requested actions with short titles. Preserve existing
  ownership, source IDs, priority, urgency and history. Do not create blocker,
  stale-information, verification-demand or duplicate task rows.
- When Stephen marks an action Done, record **Completed** immediately. Do not
  request proof, reopen it, or leave an unverified open projection. His decision
  does not claim that an unrun technical or scientific check passed.
- Keep task rows concise. Put technical context, diagnostics, acceptance criteria,
  evidence and proposed fixes in a linked simple editable Word document. Use
  standard Word styles, native lists, single spacing and no body/list spacing.
  Internal raw logs and execution history remain preserved separately.
- Investigate and resolve problems agents can handle within existing authority,
  coordinating with their current owners. If Stephen must intervene, prepare a
  concrete solution first, then state his exact action, expected result and why
  it requires him. Do not merely report a pending decision or old information.
- Chief of Staff retains canonical project intake. Do not reopen its four
  reconciled Done projections or change another owner's queue. This policy
  authorizes no new engineering/CI runs, spending, sending, permissions,
  monitors, chats, schedules or expansion of work. Development agents report
  actions to Stephen; they do not edit any lead's to-do list. Stopped experiments stay
  stopped until Stephen gives a new instruction.

The coordinator's source fingerprints, checks and review states describe
internal execution. They must never prevent recording Stephen's Done decision
as Completed in the user-facing action summary. If a technical gate remains
unmet, retain that detail in the linked Word document and raw history; do not
create an open acceptance/verification task merely to satisfy the gate.

The current local action presentation is `state/development-actions.txt`, with
technical context in `evidence/development-actions-context.docx`. It is a local
view of existing work, not a new canonical queue or an instruction to execute.

The current chat can act as the lead. Codex and Claude Code are always started
at the umbrella, and every agent and skill lives only there (see the umbrella
AGENTS.md). The six roles are `.codex/agents/monai-*.toml` for Codex and
`.claude/agents/monai-*.md` for Claude Code:

| Agent | Responsibility |
| --- | --- |
| monai-development-lead | Scope, delegation, task ownership, integration and reporting |
| monai-core | Core library, workflows, CLIs and tutorials |
| monai-slicer | Slicer modules and actual embedded-runtime integration |
| monai-simpleware | Simpleware plugins and their per-module helpers |
| monai-testing-ci | Focused tests and existing CI job/artifact evidence |
| monai-scientific-validation | Independent numerical and scientific assessment |

Two skills in the umbrella `.agents/skills/` (also visible to Claude through the
`.claude/skills` junction), `monai-dev-task` and `monai-dev-validation`, describe
the shared execution and independent review workflows. Roles inherit the configured model and actual parent permissions. A role
file is instructions, not a separate sandbox, service, login or new sidebar chat.

## Local commands and ownership

Use the existing Python 3.11 venv; no packages are required for the coordinator.
In PowerShell at the umbrella folder:

```powershell
$teamPython = 'C:\src\Projects\MONAI-Physio\venv\Scripts\python.exe'
$coordinator = 'C:\src\Projects\MONAI-Physio\dev-team\coordinator.py'
& $teamPython $coordinator --help
& $teamPython $coordinator list
# Optional forwarding helper: .\dev-team\team.ps1 list
```

In the managed sandbox this venv launcher failed; the same venv reported Python
3.11.9 and ran successfully through approved execution outside the sandbox.
That failure did not establish that Python was missing. Do not rebuild the venv
or substitute the system's advertised Python 3.10 for scientific-library checks.

Create one execution record per source scope/revision. Use a direct-user request
reference, or an ID Stephen supplies with the task. `--base` must name the
chosen local commit/ref; no fetch or checkout runs automatically. For dependencies,
record their task IDs and blocking criteria in `--criteria`, and leave dependent
work queued until they are satisfied. Paths are explicit brief constraints.

```powershell
& $teamPython $coordinator new --source 'USER:request-id:scope-v1' `
  --title 'Describe a bounded change' --repo core --role core `
  --authorization 'Reference the actual human-authorized scope' `
  --criteria 'State expected behavior, checks and dependencies' `
  --allow 'src/monai_physio/target.py' --allow 'tests/test_target.py' --base HEAD
& $teamPython $coordinator claim TASK_ID --owner ACTUAL_WORKER_SESSION_ID
& $teamPython $coordinator show TASK_ID
```

`claim` returns a token; use it for bind/check/release. Use `--read-only` when
creating investigations that need no editing worktree. Duplicate source IDs are
rejected. SQLite transactions serialize claims across clients. Claims do not
expire automatically. The same Windows account can read the database; tokens
prevent accidental concurrent updates and are not an authentication boundary.

## Worktrees

The umbrella folder is not a Git repository. Select the actual source root:

| Key | Repository | Observed source branch during setup |
| --- | --- | --- |
| core | `monai-physio` | `simulate_aorta_flow_warp` |
| slicer | `monai-physio-slicer` | `main` |
| simpleware | `monai-physio-simpleware` | `monai_physio_extensions` |

The source roots are under `C:\src\Projects\MONAI-Physio`. Core and Slicer have
preexisting uncommitted work. Existing `loop-worktrees` are not this team's
resources and must not be reset, pruned or repurposed. `monai-physio-newton` was
not a Git checkout and is not registered as an implementation target.

For each editing task, call the desktop `create_worktree` tool with the actual
repository as `sourceRoot` and the recorded task base as `ref`. Use the returned
absolute directory for every worker command. Managed worktrees begin detached
under `~/.codex/worktrees/NAME/REPO_DIR`; uncommitted source changes are not
copied. Choose a base deliberately: current experiment HEAD is not automatically
the correct base for unrelated work. Preserve modified source checkouts.

From CLI clients without that tool, `codex exec --worktree -C REPOSITORY` is the
documented CLI entry point; inspect its selected base/path before using it. This
CLI path was help-checked but not used for the setup smoke test. Codex does not
use raw `git worktree add` to bypass the desktop's managed-worktree lifecycle.
Claude Code has no equivalent tool, so it mirrors that policy with a detached
`git worktree add` in the same root; see **Claude Code integration**.

```powershell
& $teamPython $coordinator bind TASK_ID --token CLAIM_TOKEN --workspace RETURNED_PATH
```

Binding checks the Git common directory, registered worktree path, exact initial
HEAD, and exclusive task assignment. It rejects the original source checkout.
Nothing is installed into worktrees; agents and skills come from the umbrella
session. Do not bind a worktree after committing changes; bind at the selected base first.
Use one worktree per editing task. Parallel read-only reviews may inspect it only
after the worker stops. Archive managed worktrees using `archive_worktree` when
their work is no longer needed; inspect and preserve results first. Never prune
or remove a user's existing worktree as incidental cleanup.

## Checks, review and handoff

```powershell
& $teamPython $coordinator check TASK_ID --token CLAIM_TOKEN --timeout 300 -- `
  $teamPython -m pytest tests/test_target.py -q
& $teamPython $coordinator release TASK_ID --token CLAIM_TOKEN `
  --status review --evidence 'Exact log, diff, criteria assessment and unrun checks'
& $teamPython $coordinator review TASK_ID --reviewer ACTUAL_REVIEWER_SESSION_ID `
  --evidence 'Independent source/log assessment and reference'
# Stephen marking Done is an actual user completion decision (see policy above):
& $teamPython $coordinator complete TASK_ID --acceptance 'Actual user decision reference'
& $teamPython $coordinator history TASK_ID
```

Check commands run as explicit argv with no shell in the assigned workspace,
recording a unique log and before/after source fingerprint. A failure returns a
nonzero CLI status. Fingerprints include HEAD, staged/unstaged diff, and untracked
nonignored file content. Review and completion reject source drift; completion
also requires a current passing, source-preserving latest check. Read the log:
the coordinator cannot judge whether a command actually tests the criteria.
Ignored datasets, dependencies, hardware and external CI state are not included
in the fingerprint: record their versions/provenance in the technical evidence.
These internal command gates do not override Stephen's Completed task status.

Reviews reject every worker session recorded on the task, including prior clients
that handed it off. This is a role guardrail,
not authenticated approval enforcement. Never invent reviewer identities or user
acceptance strings. A passing script cannot certify scientific or clinical validity.
The coordinator records decisions; humans and agents must establish their truth.

Before another client takes over, stop all worker/check side effects, then release
with `--status queued` and an evidence/handoff reference. The next client claims
the same task with its actual session ID. Use `--status blocked` for a real blocker;
the lead can `requeue TASK_ID --evidence 'Resolution; old worker stopped'` from
blocked/review. A lost running claim is recovered with `show` and a deliberate
release only after confirming the old process/session has stopped. Timeout stops
the direct test process; confirm child processes have stopped before handoff.

## Working with Stephen, not other lead agents

Code tasks come from Stephen and are reported to Stephen, in the session where
he asked. Development agents in every client (Codex, Claude Code, Cursor) never
message, consult, wait on or take instructions from the Personal Assistant,
Chief of Staff, Engineering Lead, community-lead or other lead-agent chats, and
do not read their automations or conversations for work. Those leads keep their
own queues, checkpoints and standing approvals; the development team does not
take them over or feed them. They follow development work on their own by
pulling from GitHub (branches, PRs, issues, CI), which is expected; make that
record accurate through the normal authorized commit/PR process rather than by
messaging them.

- **Intake:** record each task with a direct-user source (`USER:...`). If
  Stephen hands over work that another lead tracks, he supplies that ID and it is
  recorded as the source; agents do not look it up. Decisions agents must follow
  are copied into files here (for example `ACTION-ONLY-POLICY.txt` and
  `COMMIT-MESSAGE-FORMAT.txt`), not cited by chat.
- **Reporting:** report to Stephen in the session. When he wants a status file
  to share elsewhere himself, write the ledger export:

```powershell
& $teamPython $coordinator export |
  Set-Content -LiteralPath .\dev-team\state\development-status.json -Encoding utf8
```

The export is a private internal execution report with source IDs, state, scope,
worktree and evidence references, omitting claim tokens. Do not use the raw
export as user-facing task rows; use short actions linked to the Word context.
Export never dispatches messages or imports instructions. Do not copy private PA
context into repositories or use private wiki communications as an engineering
task queue.

No PA/CoS canonical files, locks, sync processes, schedules or source permissions
are changed by this setup. The local ledger does not grant the Chief of Staff's
role-specific GitHub issue authority. Pushes, public PRs and reviews, merges,
releases, remote CI dispatch, installs and destructive operations retain their
specific approval requirements. Existing experiment stopping rules still apply.

## ChatGPT Desktop, Cursor and CLI integration

Verified here: local project discovery, command execution, repository identities,
Codex CLI help/version, Cursor's installed `openai.chatgpt` extension, ledger tests,
and the managed-worktree smoke test described in `evidence/verification.json`.
No Cursor UI was launched and no cross-client transcript round trip was observed.

[Official desktop settings](https://learn.chatgpt.com/docs/developer-settings#ide-extension-sync)
describe sharing active chats/editor context when the desktop app and Codex IDE
extension use the same project. [The IDE guide](https://learn.chatgpt.com/docs/ide)
lists Cursor. A separate ChatGPT cloud project/chat does not establish local
process access. This setup does not expose a network listener or create a cloud
bridge. Continue into this local project or use an explicitly supported connected
local environment; verify command access there before promising execution.

To use Cursor, open `MONAI-Physio-Codex.code-workspace`, select the Codex sidebar,
sign in if required, and look for the desktop project's chat. For editing a task,
open its exact managed worktree and pass the shared ledger task ID; check `pwd`,
`git rev-parse --show-toplevel`, owner and allowed scope before editing. The
multi-root workspace is convenient navigation, not proof of the same project
identity/session. Verify that a harmless message appears in the same chat in both
clients before relying on live chat sharing. If it does not, use the persistent
task handoff above; do not run two writers. Cursor's native AI chat is a separate
client and does not inherit Codex conversation state automatically.

The desktop-bundled CLI reported `0.167.0-alpha.3.2`; the ordinary user PATH selected
a separate standalone `0.142.5` binary during approved outside-sandbox diagnostics.
Use an explicit executable if CLI behavior differs between contexts. The inspected
desktop binary was under `%LOCALAPPDATA%/OpenAI/Codex/bin/<build-id>/codex.exe`;
that versioned location can change with updates. No global PATH/config changes
were made. The older CLI's redacted `doctor` report confirmed auth/config and
provider/WebSocket reachability, with overall failure due to `TERM=dumb` and
warnings about an optional MCP endpoint and rollout/database inventory parity.
Those diagnostics did not run a model task or verify custom-role discovery in the
older client. Do not claim an autonomous CLI job passed. Desktop delegation and
command execution are independently usable without that older CLI.

## Claude Code integration

Claude Code reads `.claude/agents/` and `.claude/skills/`, not the Codex TOMLs.
The umbrella `.claude/skills` is a directory junction to `.agents/skills`, so
both clients load the same skill files. In Claude Code, start in the umbrella
folder and ask, for example:

> Act as monai-development-lead. Use monai-dev-task. [Describe the change.]

The lead delegates with the Agent tool (`subagent_type` = role name); review
roles `monai-testing-ci` and `monai-scientific-validation` have no edit tools.
Claude's built-in worktree features branch from the default/HEAD ref, so Claude
follows the Codex policy instead: a detached worktree at the recorded base under
the same root, `$HOME/.codex/worktrees/NAME/REPO_DIR` (command in the
`monai-dev-task` skill), without Codex's internal `.codex-worktree-name` marker.
Both clients can then list, read and, through the ledger handoff, take over each
other's tasks. Owner labels are `claude:SESSION_ID:ROLE:N`. The single
`loop-kit` skill contains a "local dev team" section that links generated loop
kits to this ledger, its worktrees, specialist roles and checks. Not yet
exercised: a full Claude-led ledger task with worktree, check, release and review.

## Layout, verification and rollback

Every agent and skill exists once, at the umbrella; edit them there. The former
`install.py`, which copied role/skill templates into each repository, was retired
on 2026-11-13 when the files moved to the umbrella. Same-named core and
Simpleware skills/agents were merged into one file with a section per
repository, and loop-kit wrappers were moved with their kit paths rewritten to
`monai-physio/.agent-loops/<slug>/`. Loop kits whose contracts or kit checks pin
the old repository wrapper paths or hashes (`tutorial-19-aorta-warp`,
`aorta-1d-rigid`) need an approved contract amendment before they are resumed.
The `fireants` loop was removed at Stephen's request on 2026-11-13; its kit,
external verifier and wrappers are archived in
`state/removed-fireants-loop-20261113/`. The complete pre-move tree, the installer, its tests and manifest
are kept in `state/agent-relocation-20261113/`, `state/installation.json` and
`state/originals/`; restore from there only under a separately authorized
rollback.

```powershell
& $teamPython -m unittest discover -s .\dev-team\tests -v
```

Do not edit Codex's backing databases or global security/trust configuration.

Documentation references checked for this installation:
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[skills](https://learn.chatgpt.com/docs/build-skills), and
[configuration](https://learn.chatgpt.com/docs/config-file/config-reference).
