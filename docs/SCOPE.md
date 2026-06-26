# VolteX -- Scope Definition

This is the canonical definition of what VolteX is and is not. The other docs
(README, CONSENSUS_PROTOCOL, PROJECT_BRIEF, ARCHITECTURE, AGENTS) summarize this
file and link here.

## What VolteX Is

VolteX is a general-purpose multi-agent AI consensus platform. Its purpose is to
coordinate AI agents through a structured, user-approved consensus process so that
work is auditable, reviewable, and confidence-checked before anything is built.
The current implementation focuses on software and code review; the same consensus
model can extend to other project types later.

VolteX is the platform for building better things -- not the end product itself.

It coordinates:

- The user: the final authority and approval gate.
- Claude: proposes plans, performs local implementation, and operates the workflow.
- Codex: performs local read-only review and returns structured verdicts.
- ChatGPT: provides strategic validation, conflict review, and user-facing
  plain-English decision review.
- Local execution tools (Desktop Commander, Chrome MCP): carry out actions (write
  code, navigate GitHub, fill forms, manage the local environment). They are
  tools, not independent decision-makers.

The consensus process itself is defined in
[CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md).

## What VolteX Is Not

- VolteX is not the end product the user builds with it.
- VolteX does not itself implement the user's applications.

VolteX is the coordination layer: it helps the user produce better projects, then
gets out of the way.

## Current Scope

In scope now:
- Defining VolteX as the general-purpose multi-agent AI consensus platform.
- The current workflow foundation: orchestrator dispatch and the Claude-to-Codex
  structured review bridge, gated by CI and the user's approval, with PR-only
  merges.
- The local Discord operator interface (status, latest, packet, review,
  room-status).

Direction (documented, not yet implemented):
- The full multi-round agent consensus loop (see CONSENSUS_PROTOCOL.md).
- Extending the consensus model to non-software project types.

## Why the Name Stays

VolteX keeps its name; it denotes the consensus platform itself. The name combines
Volt (energy, live current) and -ex (platform suffix).
