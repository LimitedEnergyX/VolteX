# VolteX — System Architecture

## Current Phase: Agent Workflow Foundation

This document describes the development infrastructure architecture.
Application architecture (Revit bridge, streaming layer, etc.) will be defined in a later phase.

---

## Multi-Agent Development Model

```
Human
  │
  ├── Claude (Orchestrator)
  │     Role:    Architecture control, implementation, repo hygiene
  │     Branch:  agent/claude
  │     Dir:     D:\AI-Agents\VolteX\project-claude\
  │     CLI:     claude -p --max-turns 3 "<task>"
  │
  └── Codex (Reviewer / Strategist)
        Role:    Strategy, review, risk checks, alternate implementations
        Branch:  agent/chatgpt
        Dir:     D:\AI-Agents\VolteX\project-chatgpt\
        CLI:     codex exec "<task>"
                 codex exec --sandbox workspace-write "<task>"  ← for edits
```

---

## Local Directory Layout

```
D:\AI-Agents\VolteX\
  project-main\       ← main branch (source of truth, protected)
  project-claude\     ← agent/claude branch (Claude's isolated workspace)
  project-chatgpt\    ← agent/chatgpt branch (Codex's isolated workspace)
  orchestrator\       ← Python orchestration scripts (local, not a worktree)
```

`project-claude` and `project-chatgpt` are git worktrees of `project-main`.
Each agent sees the same repo history but works in an isolated branch and directory.

---

## Workflow

```
1. Human opens GitHub Issue
         │
2. Orchestrator assigns issue to Claude or Codex
         │
3. Agent works in its isolated worktree and branch
         │
4. Agent opens a PR — never merges itself
         │
5. Other agent reviews (or human reviews)
         │
6. Human approves and merges to main
```

---

## GitHub Guardrails

- `main` branch protected: no direct pushes
- PRs require at least one review before merge
- CI checks required before merge (when CI is added)
- No agent can approve or merge its own PR

---

## Orchestrator (Planned)

A minimal Python script that:
- Accepts a task string and target agent name
- Selects the correct CLI command and working directory
- Runs the command with a timeout and max-turn limit
- Logs stdout/stderr to a dated file
- Posts status to Discord webhook (future)

See `orchestrator/README.md` for implementation plan.

---

## Future Layers

| Layer           | Status  | Description                                         |
|-----------------|---------|-----------------------------------------------------|
| Agent workflow  | Active  | Claude + Codex via git worktrees (this document)    |
| Orchestrator    | Planned | Python script coordinating CLI agents               |
| Discord         | Planned | Command/status layer only — not the source of truth |
| VolteX Core     | Future  | Revit bridge, streaming, viewer, API               |
| Revit Plugin    | Future  | In-Revit component that exposes live model data     |

---

## Decisions Log

| Date       | Decision                                                  | Reason                                      |
|------------|-----------------------------------------------------------|---------------------------------------------|
| 2026-06-24 | Claude is orchestrator, Codex is reviewer                 | Claude has Desktop Commander + dispatch     |
| 2026-06-24 | Worktrees over separate clones                            | Shared history, cleaner, avoids drift       |
| 2026-06-24 | Discord deferred                                          | Prove CLI bridge first, avoid wasted effort |
| 2026-06-24 | No Revit plugin until architecture phase complete         | Avoid building on an undefined foundation   |
