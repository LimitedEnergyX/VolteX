# VolteX -- Scope Definition

This is the canonical definition of what VolteX is and is not. The other docs
(README, CONSENSUS_PROTOCOL, PROJECT_BRIEF, ARCHITECTURE, AGENTS) summarize this
file and link here.

## What VolteX Is

VolteX is a multi-agent AI consensus platform for orchestrating software
development. Its purpose is to coordinate AI coding assistants through a
structured, human-approved consensus process so that software work is auditable,
reviewable, and confidence-checked before anything is built.

VolteX is the coding-assistant coordination platform, not the downstream
application being built.

It coordinates:

- Shawn: the final authority and approval gate.
- Claude: proposes plans, performs local implementation, and operates the
  workflow.
- Codex: performs local read-only review and returns structured verdicts.
- ChatGPT: provides strategic validation, conflict review, and Shawn-facing
  plain-English decision review.
- Desktop Commander and Chrome MCP: execution tools on Jarvis (write code,
  navigate GitHub, fill forms, manage the local environment). They are tools, not
  independent decision-makers.

The consensus process itself is defined in
[CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md).

## What VolteX Is Not

- VolteX is not PLEX.
- VolteX is not Purple Rainmaker.
- VolteX is not the Revit tool.
- VolteX is not a Revit or BIM integration product.
- VolteX does not itself implement downstream applications.

VolteX is the platform Shawn uses to coordinate coding assistants and build or
refine downstream projects.

## Downstream Projects

Separate projects that VolteX may help build or refine. They are not VolteX
itself:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.
- Other software projects, later.

## Current Scope

In scope now:
- Defining VolteX as the multi-agent AI consensus platform and recording the
  agreed direction in documentation.
- The current workflow foundation: orchestrator dispatch and the Claude-to-Codex
  structured review bridge, gated by CI and Shawn's approval, with PR-only merges.

Deferred to future PRs (documented as direction, not implemented here):
- The Discord operator interface.
- Multi-round agent consensus automation.
- Any orchestrator, CI, or agent-behavior changes needed to implement the
  consensus protocol.
- The Revit tool and any Revit/BIM integration (deferred downstream work, tracked
  under GitHub Issue #4).

## Why the Name Stays

VolteX keeps its name. The name now denotes the consensus platform itself, not a
Revit or BIM product. Earlier docs framed VolteX around Revit and BIM; that
framing is superseded by this file.
