# Orchestrator

Coordinates task assignment between Claude and Codex agents.

## Status

Planned. Not yet implemented.

## Planned Capabilities

- Accept a task (GitHub Issue number or plain text prompt)
- Choose the correct agent (Claude or Codex) based on task type
- Run the correct CLI command with the correct working directory
- Log stdout/stderr to a timestamped file
- Enforce per-invocation timeout and max-turn limits
- Post status updates to a Discord webhook (future)

## Planned CLI

```bash
python orchestrator.py --task "Implement X from issue #5" --agent claude
python orchestrator.py --task "Review PR #6 for risks" --agent codex
python orchestrator.py --issue 7 --agent claude
```

## Agent Commands (Reference)

```bash
# Claude — read-only mode
claude -p --max-turns 3 "<task>"

# Codex — read-only mode
codex exec "<task>"

# Codex — with file edits allowed
codex exec --sandbox workspace-write "<task>"
```

## Worktree Paths

| Agent  | Working Directory                      | Branch          |
|--------|----------------------------------------|-----------------|
| Claude | D:\AI-Agents\VolteX\project-claude\   | agent/claude    |
| Codex  | D:\AI-Agents\VolteX\project-chatgpt\  | agent/chatgpt   |

## Implementation Notes

- Use `subprocess.run()` with `cwd` set to the correct worktree path
- Capture stdout/stderr, write to `logs/YYYY-MM-DD_HH-MM_<agent>.log`
- Hard timeout: 300 seconds per invocation
- Max turns enforced via `--max-turns` flag (Claude) and Codex sandbox settings
- Never run both agents on the same task simultaneously without a conflict check
