# AGENTS.md -- VolteX Multi-Agent Workflow Rules

## Scope

VolteX is the coding-assistant coordination platform, not the downstream
application being built. Revit is deferred and is not active scope; it is
tracked as downstream work (see [docs/SCOPE.md](docs/SCOPE.md)). These rules
govern how the agents coordinate that platform.

## Agents

| Agent  | Role                                              | Branch          | Worktree                              |
|--------|---------------------------------------------------|-----------------|---------------------------------------|
| Claude | Orchestrator, implementer, repo hygiene           | `agent/claude`  | `D:\AI-Agents\VolteX\project-claude`  |
| Codex  | Strategy, review, risk checks, alternate ideas    | `agent/chatgpt` | `D:\AI-Agents\VolteX\project-chatgpt` |

## CLI Invocation

```bash
# Claude — read-only / planning
claude -p --max-turns 3 "<task>"

# Codex — read-only / planning
codex exec "<task>"

# Codex — with file edits allowed
codex exec --sandbox workspace-write "<task>"
```

## Branch Rules

- `main` is protected. No direct pushes after initial scaffold commit.
- Claude works exclusively on `agent/claude` in `project-claude/`.
- Codex works exclusively on `agent/chatgpt` in `project-chatgpt/`.
- All work handed off via Pull Request only.
- Human approval required before any PR is merged to `main`.
- No agent merges its own PR.

## Turn Limits

- Default: `--max-turns 3` per invocation.
- If a task needs more turns, a human re-invokes with a new prompt.
- No agent runs indefinitely without a human checkpoint.

## Guardrails

- No secrets, tokens, credentials, API keys, or auth files in any commit.
- No direct edits to `main`.
- No agent touches the other agent's worktree or branch.
- No Revit implementation in this repo. Revit is deferred downstream work, not active VolteX scope (see [docs/SCOPE.md](docs/SCOPE.md)).
- No Discord bot code until local CLI bridge is proven working.

## Task Protocol

1. Human opens a GitHub Issue describing the task.
2. Orchestrator (or human) assigns the issue to Claude or Codex.
3. Agent works in its own worktree and branch only.
4. Agent opens a PR when complete. States what was done and what to review.
5. Other agent (or human) reviews the PR.
6. Human approves and merges.

## Failure / Stall Handling

- If an agent exceeds max turns without completing: human re-invokes with a narrower prompt.
- If agents produce conflicting implementations: human decides, opens an issue to reconcile.
- If a PR has unresolved conflicts with `main`: the authoring agent rebases its branch.
