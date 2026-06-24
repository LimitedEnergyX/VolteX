# Orchestrator

Local task dispatcher for VolteX multi-agent workflow.
Routes tasks to Claude or Codex workers via headless CLI calls.

## Purpose

The orchestrator is the single control point for assigning work to agents.
It enforces branch safety, logs every run, and handles agent unavailability cleanly.
It does not directly edit code — agents do that in their own worktrees.

## Requirements

- Python 3.9+
- `claude` CLI on PATH (Claude Code, authenticated)
- `codex` CLI on PATH (when Codex worker is enabled — not yet installed)

## Usage

```powershell
cd D:\AI-Agents\VolteX\project-main\orchestrator

# Dry run — print command, do not execute
python orchestrator.py run --agent claude --task "Summarize this repo. Do not edit files." --dry-run

# Live run
python orchestrator.py run --agent claude --task "Summarize this repo. Do not edit files."

# Help
python orchestrator.py --help
python orchestrator.py run --help
```

## Agents

| Agent  | Status    | CLI command                                          | Worktree        |
|--------|-----------|------------------------------------------------------|-----------------|
| claude | Available | `claude -p --max-turns 3 "<task>"`                   | project-claude  |
| codex  | Available | `codex exec --sandbox read-only "<task>"`            | project-chatgpt |

## Logs

Every live run writes a timestamped log to:

```
D:\AI-Agents\VolteX\orchestrator\logs\YYYY-MM-DD_HH-MM-SS_<agent>.log
```

Log contents: agent, branch, worktree, command, start time, end time,
duration, return code, stdout, stderr.

Logs are written outside the git repo and are not committed.

## Safety Rules

- **Refuses to run if the worktree is on `main`.** Hard block — no exceptions.
- **Always test with `--dry-run` first** before a live run.
- **No edit-capable mode by default.** Read-only tasks only unless the task
  prompt explicitly asks the agent to edit, and the agent's own guardrails permit it.
- **Timeout:** 300 seconds hard limit per invocation.
- **No secrets in task prompts.** Never pass tokens, keys, or credentials as task strings.
- **Codex runs read-only by default** (`--sandbox read-only`). Write-capable mode is not enabled.
- **stdin is closed** (`subprocess.DEVNULL`) for all agents — prevents interactive hangs in headless mode.

## Current Limitations

- Fixed Windows paths (`D:\AI-Agents\VolteX\`). Not portable across machines.
- Single-turn dispatch only. No multi-step task chaining yet.
- No Discord integration. Status reporting is console and log file only.
- Codex worker resolves binary via: `CODEX_CLI_PATH` env var → PATH → `C:\Users\RDPJarvis\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe`.
- Codex write-capable mode (`--sandbox workspace-write`) is not enabled.
- Claude subprocess auth requires an authenticated terminal session.
  Set `ANTHROPIC_API_KEY` as a User env var for non-interactive/scheduled use.

## Agent Commands Reference

```bash
# Claude — read-only
claude -p --max-turns 3 "<task>"

# Codex — read-only (default, always)
codex exec --sandbox read-only "<task>"

# Codex — write-capable (NOT enabled — future phase only)
# codex exec --sandbox workspace-write "<task>"
```

## Next Planned Steps

1. Prove live Claude run end-to-end from the orchestrator
2. Install Codex CLI and enable the codex worker
3. Add `--issue` flag to pull task text from a GitHub Issue number
4. Add a Discord webhook status post after each run
5. Add multi-agent handoff: Claude completes task, Codex reviews the PR
