# VolteX -- System Architecture

## Scope

VolteX is the coding-assistant coordination platform, not the downstream
application being built. This document describes the coordination and
development infrastructure. Downstream application architecture (including the
deferred Revit tool) is out of scope here -- see [SCOPE.md](SCOPE.md).

---

## Multi-Agent Coordination Model

```
Human (Shawn) -- sole authority
  |
  +- Claude (Operator / Implementer)
  |     Role:   Implementation, repo hygiene, orchestration
  |     Branch: agent/claude
  |     Dir:    D:\AI-Agents\VolteX\project-claude\
  |     CLI:    claude -p --max-turns 3 "<task>"
  |
  +- Codex (Worker / Reviewer)
        Role:   Review, risk checks, alternate implementations
        Branch: agent/chatgpt
        Dir:    D:\AI-Agents\VolteX\project-chatgpt\
        CLI:    codex exec --sandbox read-only "<task>"
```

ChatGPT acts as an external reviewer/strategist (advisory, no repo access);
Shawn relays review packets and verdicts.

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

## Workflow

```
1. Human opens a GitHub Issue
2. Orchestrator assigns the task to Claude or Codex
3. Agent works in its isolated worktree and branch
4. Agent opens a PR -- never merges itself
5. Codex (and/or ChatGPT) reviews via the structured verdict bridge
6. Human approves and merges to main
```

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

| Layer           | Status              | Description                                          |
|-----------------|---------------------|------------------------------------------------------|
| Agent workflow  | Active              | Claude + Codex via git worktrees                     |
| Orchestrator    | Active              | Python tool coordinating CLI agents                  |
| Review bridge   | Active              | Structured Claude-to-Codex verdicts and transcripts  |
| Discord         | Deferred            | Command/status layer only -- not the source of truth |
| Downstream apps | Deferred/downstream | Separate products VolteX may later help build        |
| Revit tool      | Deferred/downstream | Future downstream project; not active VolteX scope   |

---

## Decisions Log

| Date       | Decision                                                  | Reason                                              |
|------------|-----------------------------------------------------------|-----------------------------------------------------|
| 2026-06-24 | Claude is operator, Codex is reviewer                     | Claude has Desktop Commander + dispatch             |
| 2026-06-24 | Worktrees over separate clones                            | Shared history, cleaner, avoids drift               |
| 2026-06-24 | Discord deferred                                          | Prove CLI bridge first, avoid wasted effort         |
| 2026-06-25 | VolteX defined as the coordination platform; Revit deferred | VolteX is the control plane, not the downstream app |
