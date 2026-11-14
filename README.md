# aylward-coding-agents

Revision-controlled copy of the AI coding-agent infrastructure used at the
top level of the MONAI-Physio workspace (`C:/src/Projects/MONAI-Physio`), where
Codex and Claude Code are always started.

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Workspace instructions loaded by both clients |
| `.agents/skills/` | Skills shared by Codex and Claude Code (one file each) |
| `.agents/settings.json` | Agent permissions for `.agents/` |
| `.claude/agents/` | Claude Code subagents |
| `.codex/agents/` | Codex custom agents |
| `dev-team/` | Local development-team ledger (`coordinator.py`), helper, tests and guide |
| `MONAI-Physio-Codex.code-workspace` | Multi-root editor workspace |

Not included: task-specific loop wrappers (`*-loop` skills and their agents),
loop kits and verifiers, `dev-team/evidence/`, `dev-team/state/`, caches and
plugin data. Those are project state. Decisions that agents must follow are
copied into files (for example `dev-team/ACTION-ONLY-POLICY.txt`) rather than
cited by chat. Development agents take code tasks from Stephen and report to
him; they never message other lead-agent chats, so no chat identifiers are
needed.

## Deploying to the workspace

Copy the paths above into the workspace root. Claude Code reads skills from
`.claude/skills`, which must be a directory junction to `.agents/skills`
(git cannot store the junction):

```powershell
New-Item -ItemType Junction -Path .claude\skills -Target (Resolve-Path .agents\skills)
```

Check the ledger tools with the workspace venv:

```powershell
& .\venv\Scripts\python.exe -m unittest discover -s .\dev-team\tests -v
```
