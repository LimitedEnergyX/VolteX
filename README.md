# VolteX

A live Revit integration platform — think Plex, but for BIM workflows.

## Status

Early scaffold. No Revit plugin yet.
Current phase: architecture definition and multi-agent workflow foundation.

## Structure

```
├── docs/               Project brief and architecture
├── orchestrator/       Multi-agent orchestration layer (planned)
├── AGENTS.md           Rules for AI agent collaboration
└── README.md
```

## Agent Workflow

Claude and Codex collaborate on this repo using isolated git worktrees and a strict PR-only handoff model.
See [AGENTS.md](AGENTS.md) for rules and invocation commands.

## Future Vision

- Live connection to open Revit models
- Real-time model data streaming
- Browser-based viewer and dashboards
- Multi-user collaboration layer
- Revit plugin (later phase)
- Discord command/status layer (later phase)
