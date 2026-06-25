# VolteX

VolteX is a multi-agent AI consensus platform for orchestrating software
development. It is the coding-assistant coordination platform, not the downstream
application being built. Shawn uses VolteX to coordinate AI coding assistants
(Claude, Codex, ChatGPT) through a structured, human-approved consensus process,
so software work is auditable, reviewable, and confidence-checked before anything
is built.

See [docs/SCOPE.md](docs/SCOPE.md) for the canonical scope definition and
[docs/CONSENSUS_PROTOCOL.md](docs/CONSENSUS_PROTOCOL.md) for the consensus process
direction.

## Status

Active workflow foundation. The current workflow is the orchestrator review
bridge: Claude proposes, Codex reviews via a structured verdict, Shawn approves,
PR-only merges. The broader consensus protocol and the Discord operator interface
are documented as direction and deferred to future PRs.

Revit is deferred. VolteX is not the Revit tool -- see Downstream Projects.

## Structure

```
+- docs/            Scope, consensus protocol, project brief, architecture
+- orchestrator/    Multi-agent orchestration layer
+- AGENTS.md        Rules for AI agent collaboration
+- README.md
```

## Roles

- Shawn: final authority and approval gate.
- Claude: proposes plans, performs local implementation, operates the workflow.
- Codex: local read-only review; returns structured verdicts.
- ChatGPT: strategic validation, conflict review, Shawn-facing plain-English decision review.
- Desktop Commander and Chrome MCP: execution tools on Jarvis, not decision-makers.

## Agent Workflow

Claude and Codex collaborate using isolated git worktrees and a strict PR-only
handoff model. See [AGENTS.md](AGENTS.md) for rules and invocation commands, and
[docs/CONSENSUS_PROTOCOL.md](docs/CONSENSUS_PROTOCOL.md) for the planned consensus
loop.

## Downstream Projects

Separate projects VolteX may help build or refine -- not VolteX itself:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.
- Other software projects, later.
