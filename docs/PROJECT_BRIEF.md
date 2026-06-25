# VolteX -- Project Brief

## What is VolteX?

VolteX is the coding-assistant coordination platform, not the downstream
application being built. It is Shawn's control plane for coordinating AI coding
assistants and the infrastructure around them: Claude (operator), Codex
(worker), ChatGPT (reviewer), GitHub, CI, review transcripts, handoffs, restore
tags, and approval gates.

See [SCOPE.md](SCOPE.md) for the canonical scope definition.

The name combines Volt (energy, live current) and -ex (platform suffix). It now
denotes the coordination platform itself -- not a Revit or BIM product.

## Problem

Coordinating multiple AI coding assistants by hand is error-prone: work is hard
to review, decisions are not auditable, and there is no safe, repeatable handoff
between the agents and the human. There is no single control plane that enforces
review and keeps a durable record.

## Solution

VolteX provides that control plane. It routes tasks to the right agent, runs
reviews through a structured verdict bridge, records transcripts, gates every
change behind CI and human approval, and preserves continuity through handoffs
and restore tags.

## Current Phase

Operating the multi-agent coordination workflow and keeping documentation
aligned with actual scope.

**In scope now:**
- Multi-agent coordination workflow (Claude + Codex + ChatGPT + Shawn)
- Orchestrator dispatch, review bridge, transcripts, handoffs, restore tags
- CI gate and approval gates
- Documentation that keeps scope accurate

**Deferred / not active scope:**
- The Revit tool and any Revit/BIM integration (deferred downstream work)
- Discord and voice layers
- Any agent-feature expansion beyond the proven workflow

## Downstream Projects

Separate projects VolteX may help coordinate, refine, or build:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.

## Stakeholders

- Owner: Shawn Tovey / LimitedEnergyX
- Agents: Claude (operator/implementer), Codex (worker), ChatGPT (reviewer/strategist)

## Success Criteria

- Scope is accurately documented (VolteX = coordination platform, Revit deferred)
- Multi-agent workflow remains safe, reviewable, and repeatable
- Every change is gated by CI and human approval
