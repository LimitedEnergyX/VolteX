# VolteX -- Project Brief

## What is VolteX?

VolteX is a multi-agent AI consensus platform for orchestrating software
development. It is the coding-assistant coordination platform, not the downstream
application being built. Shawn uses VolteX to coordinate AI coding assistants
(Claude, Codex, ChatGPT) through a structured, human-approved consensus process,
so software work is auditable, reviewable, and confidence-checked before anything
is built.

See [SCOPE.md](SCOPE.md) for the canonical scope definition and
[CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md) for the consensus process.

The name combines Volt (energy, live current) and -ex (platform suffix). It now
denotes the consensus platform itself -- not a Revit or BIM product.

## Problem

Coordinating multiple AI coding assistants by hand is error-prone: work is hard
to review, decisions are not auditable, and there is no safe, repeatable handoff
between the agents and the human. There is no single control plane that enforces
review, builds consensus, and keeps a durable record.

## Solution

VolteX provides that control plane. Claude proposes, Codex and ChatGPT review,
and the agents iterate in a bounded consensus loop. A recommended solution -- or,
if the agents cannot agree, a structured decision package -- is presented to Shawn
in plain English. Nothing proceeds without his approval. Approved work follows a
proper Git workflow (branch, commit, review, CI, merge, tag/handoff).

## Current Phase

Operating the workflow foundation and recording the consensus-platform direction
in documentation.

**In scope now:**
- VolteX defined as the multi-agent AI consensus platform
- Orchestrator dispatch and the Claude-to-Codex structured review bridge
- CI gate, approval gates, transcripts, handoffs, restore tags
- Documentation that keeps scope accurate

**Deferred to future PRs (direction, not implemented here):**
- Discord operator interface
- Multi-round agent consensus automation
- Orchestrator, CI, or agent-behavior changes to implement the protocol
- The Revit tool and any Revit/BIM integration (deferred downstream work)

## Downstream Projects

Separate projects VolteX may help build or refine:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.
- Other software projects, later.

## Stakeholders

- Owner: Shawn Tovey / LimitedEnergyX
- Agents: Claude (operator/implementer), Codex (worker/reviewer), ChatGPT (strategic reviewer)

## Success Criteria

- Scope is accurately documented (VolteX = consensus platform, Revit deferred)
- The multi-agent workflow remains safe, reviewable, and repeatable
- Every change is gated by consensus review and Shawn's explicit approval
