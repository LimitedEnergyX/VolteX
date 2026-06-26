# AGENTS.md -- VolteX Multi-Agent Workflow Rules

## Scope

VolteX is a general-purpose multi-agent AI consensus platform. These rules govern
how the agents collaborate. The current implementation focuses on software and
code review; the full multi-round consensus protocol (Claude proposes; Codex
and/or ChatGPT review; bounded five-round loop; the user approves in plain
English) is documented in [docs/CONSENSUS_PROTOCOL.md](docs/CONSENSUS_PROTOCOL.md).

## Agents

| Agent  | Role                                                    | Branch          | Worktree                              |
|--------|---------------------------------------------------------|-----------------|---------------------------------------|
| Claude | Operator: proposes plans, implements, operates workflow | `agent/claude`  | `D:\AI-Agents\VolteX\project-claude`  |
| Codex  | Reviewer: local read-only review, structured verdicts   | `agent/chatgpt` | `D:\AI-Agents\VolteX\project-chatgpt` |

Note: `agent/chatgpt` / `project-chatgpt` is a legacy name now used by the Codex
worker. Codex (reviewer) and ChatGPT (external strategist) are distinct roles.

## CLI Invocation

```bash
# Claude -- read-only / planning
claude -p --max-turns 3 "<task>"

# Codex -- read-only / planning
codex exec "<task>"

# Codex -- with file edits allowed
codex exec --sandbox workspace-write "<task>"
```

## Branch Rules

- `main` is protected. No direct pushes after the initial scaffold commit.
- Claude works exclusively on `agent/claude` in `project-claude/`.
- Codex works exclusively on `agent/chatgpt` in `project-chatgpt/`.
- All work handed off via Pull Request only.
- The user's approval is required before any PR is merged to `main`.
- No agent merges its own PR.

## Turn Limits

- Default: `--max-turns 3` per invocation.
- If a task needs more turns, the user re-invokes with a new prompt.
- No agent runs indefinitely without a checkpoint from the user.

## Guardrails

- No secrets, tokens, credentials, API keys, or auth files in any commit.
- No direct edits to `main`.
- No agent touches the other agent's worktree or branch.
- VolteX is the coordination platform, not the end product -- agents do not build
  the user's own end products inside this repo.

## Task Protocol

1. The user opens a GitHub Issue describing the task.
2. The orchestrator (or the user) assigns the issue to Claude or Codex.
3. The agent works in its own worktree and branch only.
4. The agent opens a PR when complete, stating what was done and what to review.
5. The other agent (or the user) reviews the PR.
6. The user approves and merges.

## Failure / Stall Handling

- If an agent exceeds max turns without completing: the user re-invokes with a
  narrower prompt.
- If agents produce conflicting implementations: the user decides and opens an
  issue to reconcile.
- If a PR has unresolved conflicts with `main`: the authoring agent rebases its
  branch.
