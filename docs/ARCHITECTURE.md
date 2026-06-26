# VolteX -- System Architecture

## Scope

VolteX is a general-purpose multi-agent AI consensus platform. This document
describes the coordination and development infrastructure -- see [SCOPE.md](SCOPE.md)
for the platform definition and [CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md) for
the consensus process. The current implementation focuses on software and code
review.

---

## Roles

- The user (Human): final authority and approval gate.
- Claude (Operator / Implementer): proposes plans, performs local implementation,
  operates the workflow.
- Codex (Worker / Reviewer): local read-only review; returns structured verdicts.
- ChatGPT (Strategist): strategic validation, conflict review, and user-facing
  plain-English review (advisory, no repo access).
- Local execution tools (Desktop Commander, Chrome MCP): carry out actions, not
  decision-makers.

---

## Multi-Agent Coordination Model

```
The user -- sole authority
  |
  +- Claude (Operator / Implementer)
  |     Branch: agent/claude
  |     Dir:    D:\AI-Agents\VolteX\project-claude\
  |     CLI:    claude -p --max-turns 3 "<task>"
  |
  +- Codex (Worker / Reviewer)
        Branch: agent/chatgpt
        Dir:    D:\AI-Agents\VolteX\project-chatgpt\
        CLI:    codex exec --sandbox read-only "<task>"
```

ChatGPT acts as an external strategist/reviewer (advisory, no repo access); the
user relays review packets and verdicts.

Note: the `agent/chatgpt` branch and `project-chatgpt` worktree are a legacy name
now used by the Codex worker. Codex (local reviewer) and ChatGPT (external
strategist) are distinct roles despite the shared historical name.

---

## Local Directory Layout

```
D:\AI-Agents\VolteX\
  project-main\      main branch (source of truth, protected)
  project-claude\    agent/claude branch (Claude's isolated workspace)
  project-chatgpt\   agent/chatgpt branch (Codex's isolated workspace)
  orchestrator\      Python orchestration scripts (local, not a worktree)
```

`project-claude` and `project-chatgpt` are git worktrees of `project-main`.
Each agent sees the same repo history but works in an isolated branch and
directory.

---

## Workflow (current)

```
1. The user opens a GitHub Issue
2. Orchestrator assigns the task to Claude or Codex
3. Agent works in its isolated worktree and branch
4. Agent opens a PR -- never merges itself
5. Codex (and/or ChatGPT) reviews via the structured verdict bridge
6. The user approves and merges to main
```

---

## Consensus Protocol (direction)

The current workflow is the single-pass review bridge above. The full consensus
protocol -- Claude proposes; Codex and/or ChatGPT review; a bounded five-round
loop; consensus or an RFI-style decision package; then the user's plain-English
approval -- is documented in [CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md).

---

## GitHub Guardrails

- `main` branch protected: no direct pushes
- PRs reviewed before merge
- CI checks required on every pull request
- No agent approves or merges its own PR

---

## Orchestrator

A Python tool that:
- Accepts a task string and target agent name
- Selects the correct CLI command and working directory
- Runs the command with a timeout and max-turn limit
- Logs stdout/stderr to a dated file
- Sends review packets to Codex and parses structured verdicts
- Writes review transcripts

See `orchestrator/README.md` for details.

---

## Layers

| Layer              | Status    | Description                                          |
|--------------------|-----------|------------------------------------------------------|
| Agent workflow     | Active    | Claude + Codex via git worktrees                     |
| Orchestrator       | Active    | Python tool coordinating CLI agents                  |
| Review bridge      | Active    | Structured Claude-to-Codex verdicts and transcripts  |
| Discord interface  | Active    | Local operator interface (status/latest/packet/review/room-status) |
| Consensus loop     | Direction | Full multi-round Claude/Codex/ChatGPT consensus loop |

---

## Decisions Log

| Date       | Decision                                                    | Reason                                                |
|------------|-------------------------------------------------------------|-------------------------------------------------------|
| 2026-06-24 | Claude is operator, Codex is reviewer                       | Claude has local execution tools + dispatch           |
| 2026-06-24 | Worktrees over separate clones                              | Shared history, cleaner, avoids drift                 |
| 2026-06-25 | VolteX defined as a multi-agent AI consensus platform       | VolteX is the coordination layer, not the end product |
| 2026-06-26 | Docs generalized to any user; no project-specific framing   | VolteX is a general-purpose platform                  |
