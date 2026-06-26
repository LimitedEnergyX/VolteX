# VolteX

VolteX is a general-purpose multi-agent AI consensus platform. AI agents
collaborate and cross-check each other's work in a bounded, structured loop, then
present a clear recommendation to the user for approval -- so the user produces
higher-quality work with confidence. The current implementation focuses on
software and code review; the same consensus model can extend to other project
types later.

See [docs/SCOPE.md](docs/SCOPE.md) for the canonical scope definition and
[docs/CONSENSUS_PROTOCOL.md](docs/CONSENSUS_PROTOCOL.md) for the consensus process.

## Status

The current workflow is the orchestrator review bridge: Claude proposes, Codex
reviews via a structured verdict, and the user approves, with PR-only merges. A
local Discord operator interface is live (`/voltex status`, `/voltex latest`,
`/voltex packet`, `/voltex review`, `/voltex room-status`). The full multi-round
consensus loop is documented as the target direction.

## Structure

```
+- docs/            Scope, consensus protocol, project brief, architecture
+- orchestrator/    Multi-agent orchestration layer
+- discord_bridge/  Local Discord operator interface
+- AGENTS.md        Rules for AI agent collaboration
+- README.md
```

For the local Discord operator interface, see
[discord_bridge/README.md](discord_bridge/README.md).

## Roles

- The user: final authority and approval gate.
- Claude: proposes plans, performs local implementation, operates the workflow.
- Codex: local read-only review; returns structured verdicts.
- ChatGPT: strategic validation, conflict review, user-facing plain-English decision review.
- Local execution tools (Desktop Commander, Chrome MCP): carry out actions, not decision-makers.

## Agent Workflow

The agents collaborate using isolated git worktrees and a strict PR-only handoff
model. See [AGENTS.md](AGENTS.md) for rules and invocation commands, and
[docs/CONSENSUS_PROTOCOL.md](docs/CONSENSUS_PROTOCOL.md) for the consensus loop.

## What VolteX Is (and Is Not)

VolteX is the platform for building better things -- it is not the end product
itself. It coordinates the agents and surfaces decisions to the user; the projects
the user builds with it are separate.

---

Built by Shawn C. Tovey, RCDD / LimitedEnergyX.
